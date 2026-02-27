from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import torch
import torch.nn.functional as F
from tqdm import tqdm

from losses import PatchLossConfig, patch_losses
from metrics import psnr as psnr_metric
from models.inr import INR, INRConfig
from utils.coords import make_coord_grid, sample_pixels
from utils.image_io import load_image_rgb, save_image_rgb
from utils.patches import sample_patches


def set_torch_backend_defaults() -> None:
    torch.backends.cudnn.benchmark = True
    torch.set_float32_matmul_precision("high")


def _set_lr(opt: torch.optim.Optimizer, lr: float) -> None:
    for pg in opt.param_groups:
        pg["lr"] = lr


def cosine_lr(step: int, total_steps: int, lr_start: float, lr_end: float) -> float:
    """Cosine schedule from lr_start -> lr_end over total_steps."""
    if total_steps <= 1:
        return float(lr_end)
    t = float(step) / float(total_steps - 1)
    # standard cosine anneal
    return float(lr_end + 0.5 * (lr_start - lr_end) * (1.0 + np.cos(np.pi * t)))


@torch.no_grad()
def render_full(
    model: torch.nn.Module,
    H: int,
    W: int,
    device: torch.device,
    chunk: int = 1_000_000,
) -> torch.Tensor:
    """Render full image (H,W,3) on device.

    Uses chunked evaluation to limit memory. Chunks are blocks of pixels.
    """
    grid = make_coord_grid(H, W, device=device, dtype=torch.float32)
    coords = grid.coords
    out_chunks = []
    for i in range(0, coords.shape[0], chunk):
        c = coords[i : i + chunk]
        out_chunks.append(model(c).detach())
    out = torch.cat(out_chunks, dim=0)
    return out.reshape(H, W, 3)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Reverse engineer an image via an implicit neural representation (INR).")
    p.add_argument("--image", type=str, required=True, help="Path to the target image")
    p.add_argument("--outdir", type=str, required=True, help="Output directory")

    p.add_argument("--model", type=str, default="siren", choices=["siren", "fourier_mlp"])

    # siren
    p.add_argument("--hidden", type=int, default=512)
    p.add_argument("--layers", type=int, default=8)
    p.add_argument("--w0", type=float, default=30.0)
    p.add_argument("--w0_hidden", type=float, default=1.0)

    # fourier+mlp
    p.add_argument("--ff", type=int, default=12, help="# Fourier frequencies (fourier_mlp)")
    p.add_argument("--mlp_layers", type=int, default=6)
    p.add_argument("--mlp_hidden", type=int, default=512)
    p.add_argument("--mlp_activation", type=str, default="gelu", choices=["relu", "gelu"])

    # training
    p.add_argument("--steps", type=int, default=200000)
    # Default batch is chosen to be safe on ~12GB GPUs; increase if you have more VRAM.
    p.add_argument("--batch", type=int, default=65536, help="Random pixel batch size")
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument(
        "--lr_end",
        type=float,
        default=1e-5,
        help="Final learning rate for cosine schedule (ignored if --schedule none)",
    )
    p.add_argument(
        "--schedule",
        type=str,
        default="cosine",
        choices=["none", "cosine"],
        help="Learning rate schedule",
    )
    p.add_argument("--seed", type=int, default=123)
    p.add_argument("--amp", action="store_true", help="Use mixed precision")

    # optional patch losses for sharpness/structure
    p.add_argument("--patch", type=int, default=64, help="Patch size for optional patch losses")
    p.add_argument("--patches", type=int, default=8, help="#patches per step for optional losses")
    p.add_argument("--grad-loss", type=float, default=0.0, help="Weight for Sobel gradient loss")
    p.add_argument("--ssim-loss", type=float, default=0.0, help="Weight for (1-SSIM) loss")

    # logging/checkpointing
    p.add_argument("--val_every", type=int, default=2000)
    p.add_argument("--val_samples", type=int, default=200000)
    p.add_argument("--save_every", type=int, default=5000)
    p.add_argument("--preview_every", type=int, default=5000)
    p.add_argument("--preview_scale", type=float, default=0.25, help="Preview render scale factor")

    p.add_argument("--resume", type=str, default="", help="Path to checkpoint to resume")

    return p.parse_args()


def main() -> None:
    args = parse_args()
    set_torch_backend_defaults()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Save args for reproducibility
    with open(outdir / "config.json", "w", encoding="utf-8") as f:
        json.dump(vars(args), f, indent=2)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Load image
    img = load_image_rgb(args.image)
    H, W = img.h, img.w
    print(f"Target image: {W}x{H}")

    # Prepare tensors on GPU
    target = torch.from_numpy(img.data).to(device=device, dtype=torch.float32)
    target_flat = target.reshape(-1, 3)

    grid = make_coord_grid(H, W, device=device, dtype=torch.float32)
    coords_flat = grid.coords

    # Model
    cfg = INRConfig(model=args.model)
    if args.model == "siren":
        cfg.siren_hidden = args.hidden
        cfg.siren_layers = args.layers
        cfg.siren_w0 = args.w0
        cfg.siren_w0_hidden = args.w0_hidden
    else:
        cfg.ff_num_frequencies = args.ff
        cfg.mlp_layers = args.mlp_layers
        cfg.mlp_hidden = args.mlp_hidden
        cfg.mlp_activation = args.mlp_activation

    model = INR(cfg).to(device)

    # Optimizer
    opt = torch.optim.Adam(model.parameters(), lr=args.lr, betas=(0.9, 0.99), eps=1e-15)

    # Mixed precision (optional). For SIREN, bf16 tends to be numerically safer than fp16.
    use_amp = bool(args.amp) and device.type == "cuda"
    amp_dtype = torch.bfloat16
    scaler = torch.amp.GradScaler(device=("cuda" if device.type == "cuda" else "cpu"), enabled=use_amp)

    start_step = 0
    best_psnr = -1.0

    if args.resume:
        ckpt = torch.load(args.resume, map_location=device)
        model.load_state_dict(ckpt["model"], strict=True)
        opt.load_state_dict(ckpt["opt"])
        start_step = int(ckpt.get("step", 0))
        best_psnr = float(ckpt.get("best_psnr", -1.0))
        print(f"Resumed from {args.resume} at step {start_step} (best_psnr={best_psnr:.2f})")

    # RNG
    rng = torch.Generator(device=device)
    rng.manual_seed(args.seed)

    # Fixed validation indices for consistent tracking
    val_rng = torch.Generator(device=device)
    val_rng.manual_seed(args.seed + 999)
    val_idx = torch.randint(0, coords_flat.shape[0], (args.val_samples,), generator=val_rng, device=device)
    val_coords = coords_flat[val_idx]
    val_target = target_flat[val_idx]

    patch_cfg = PatchLossConfig(
        patch_size=args.patch,
        num_patches=args.patches,
        grad_weight=args.grad_loss,
        ssim_weight=args.ssim_loss,
    )

    pbar = tqdm(range(start_step, args.steps), dynamic_ncols=True)
    for step in pbar:
        # Learning rate schedule
        if args.schedule == "cosine":
            lr_now = cosine_lr(step, args.steps, args.lr, args.lr_end)
            _set_lr(opt, lr_now)

        model.train()
        opt.zero_grad(set_to_none=True)

        # Pixel MSE batch
        c, t = sample_pixels(coords_flat, target_flat, args.batch, rng=rng)

        with torch.amp.autocast(device_type=device.type, dtype=amp_dtype, enabled=use_amp):
            pred = model(c)
            loss = F.mse_loss(pred, t)

            # Optional patch-based losses (operate on small grids so gradients/SSIM are meaningful)
            extra_stats: Dict[str, float] = {}
            if patch_cfg.grad_weight > 0.0 or patch_cfg.ssim_weight > 0.0:
                pc, pt = sample_patches(coords_flat, target_flat, H, W, patch_cfg.patch_size, patch_cfg.num_patches, rng=rng)
                # Evaluate model on all patch pixels
                P = pc.shape[0]
                S = patch_cfg.patch_size
                pred_p = model(pc.reshape(-1, 2)).reshape(P, S, S, 3).permute(0, 3, 1, 2)
                tgt_p = pt.reshape(P, S, S, 3).permute(0, 3, 1, 2)
                patch_l, stats = patch_losses(pred_p, tgt_p, patch_cfg)
                loss = loss + patch_l
                extra_stats.update(stats)

        scaler.scale(loss).backward()
        scaler.step(opt)
        scaler.update()

        # Logging
        if step % 50 == 0:
            msg = f"loss={float(loss.detach().cpu()):.6f}"
            if extra_stats:
                for k, v in extra_stats.items():
                    if k == "ssim":
                        msg += f"  ssim={v:.4f}"
                    else:
                        msg += f"  {k}={v:.6f}"
            pbar.set_description(msg)

        # Validation (PSNR on fixed subset)
        if (step + 1) % args.val_every == 0:
            model.eval()
            with torch.no_grad(), torch.amp.autocast(device_type=device.type, dtype=amp_dtype, enabled=use_amp):
                val_pred = model(val_coords)
                val_mse = F.mse_loss(val_pred, val_target).item()
                val_psnr = 10.0 * np.log10(1.0 / max(val_mse, 1e-12))

            is_best = val_psnr > best_psnr
            if is_best:
                best_psnr = val_psnr

            pbar.write(f"[val] step={step+1} mse={val_mse:.6e} psnr={val_psnr:.2f} best={best_psnr:.2f}")

            # Save best
            if is_best:
                ckpt_path = outdir / "model_best.pt"
                torch.save(
                    {
                        "model": model.state_dict(),
                        "opt": opt.state_dict(),
                        "step": step + 1,
                        "best_psnr": best_psnr,
                        "cfg": asdict(cfg),
                        "H": H,
                        "W": W,
                    },
                    ckpt_path,
                )

        # Periodic checkpoint
        if (step + 1) % args.save_every == 0:
            ckpt_path = outdir / f"model_step_{step+1}.pt"
            torch.save(
                {
                    "model": model.state_dict(),
                    "opt": opt.state_dict(),
                    "step": step + 1,
                    "best_psnr": best_psnr,
                    "cfg": asdict(cfg),
                    "H": H,
                    "W": W,
                },
                ckpt_path,
            )

        # Preview render
        if (step + 1) % args.preview_every == 0:
            model.eval()
            ph = max(16, int(H * args.preview_scale))
            pw = max(16, int(W * args.preview_scale))
            with torch.no_grad():
                recon = render_full(model, ph, pw, device=device, chunk=500_000)
                # Metrics on preview (approx)
                tgt_small = torch.nn.functional.interpolate(
                    target.permute(2, 0, 1).unsqueeze(0),
                    size=(ph, pw),
                    mode="area",
                ).squeeze(0).permute(1, 2, 0)
                preview_psnr = psnr_metric(recon, tgt_small)
                pbar.write(f"[preview] step={step+1} preview_psnr={preview_psnr:.2f}")

                recon_np = recon.detach().cpu().numpy()
                save_image_rgb(str(outdir / f"preview_step_{step+1}.png"), recon_np)

    # Save final
    ckpt_last = outdir / "model_last.pt"
    torch.save(
        {
            "model": model.state_dict(),
            "opt": opt.state_dict(),
            "step": args.steps,
            "best_psnr": best_psnr,
            "cfg": asdict(cfg),
            "H": H,
            "W": W,
        },
        ckpt_last,
    )

    # Final full-resolution render (may take a bit but yields the reconstruction)
    model.eval()
    with torch.no_grad():
        recon = render_full(model, H, W, device=device, chunk=750_000)
        recon_np = recon.detach().cpu().numpy()
        save_image_rgb(str(outdir / "recon_full.png"), recon_np)
        final_psnr = psnr_metric(recon, target)
        print(f"Final PSNR: {final_psnr:.2f} dB")


if __name__ == "__main__":
    main()
