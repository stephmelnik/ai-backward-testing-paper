import argparse
import json
import math
from pathlib import Path

import numpy as np
import torch
from tqdm import trange

from fourier_model import FourierCurveBatch, ModelConfig
from losses import sample_dt, coverage_loss_target_to_curve, oob_penalty


def _load_cache(cache_path: Path):
    data = np.load(str(cache_path), allow_pickle=True)
    dt = data["dt"].astype(np.float32)
    edge_pts = data["edge_points"].astype(np.float32)
    meta_raw = data["meta"].item()
    meta = json.loads(meta_raw) if isinstance(meta_raw, str) else {}
    res = int(dt.shape[0])
    return dt, edge_pts, meta, res


def spectral_reg(model: FourierCurveBatch, k_active: int) -> torch.Tensor:
    """Per-candidate spectral regularizer [B]. Penalizes high frequencies."""
    k = torch.arange(1, k_active + 1, device=model.ax_cos.device, dtype=model.ax_cos.dtype)[None, :]
    w = (k * k)  # [1,K]
    ax = model.ax_cos[:, :k_active]
    bx = model.ax_sin[:, :k_active]
    ay = model.ay_cos[:, :k_active]
    by = model.ay_sin[:, :k_active]
    reg = (w * (ax * ax + bx * bx + ay * ay + by * by)).mean(dim=1)

    # Small penalty on time-warp magnitude (keeps it "generic" but not too wild)
    scale, rot, trans, tw_sin, tw_cos = model._map_params()
    tw = (tw_sin * tw_sin + tw_cos * tw_cos).mean(dim=1)
    return reg + 0.15 * tw


def make_stages(k_max: int, curve_points: int, steps: int, stages: int):
    """Minimal 1-3 stage schedule."""
    stages_out = []

    if stages <= 1:
        stages_out.append(
            dict(
                name="stage1",
                k_active=k_max,
                n_points=curve_points,
                steps=steps,
                lr=0.015,
                w_cov=0.60,
                w_reg=0.010,
            )
        )
        return stages_out

    if stages == 2:
        stages_out.append(
            dict(
                name="stage1",
                k_active=min(10, k_max),
                n_points=min(2048, curve_points),
                steps=max(1, steps // 2),
                lr=0.030,
                w_cov=0.25,
                w_reg=0.030,
            )
        )
        stages_out.append(
            dict(
                name="stage2",
                k_active=k_max,
                n_points=curve_points,
                steps=steps,
                lr=0.012,
                w_cov=0.60,
                w_reg=0.012,
            )
        )
        return stages_out

    # 3 stages
    stages_out.append(
        dict(
            name="stage1",
            k_active=min(8, k_max),
            n_points=min(1536, curve_points),
            steps=max(1, steps // 3),
            lr=0.040,
            w_cov=0.15,
            w_reg=0.045,
        )
    )
    stages_out.append(
        dict(
            name="stage2",
            k_active=min(16, k_max),
            n_points=min(3072, curve_points),
            steps=max(1, steps // 2),
            lr=0.020,
            w_cov=0.40,
            w_reg=0.020,
        )
    )
    stages_out.append(
        dict(
            name="stage3",
            k_active=k_max,
            n_points=curve_points,
            steps=steps,
            lr=0.010,
            w_cov=0.70,
            w_reg=0.010,
        )
    )
    return stages_out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True, help="target_cache.npz from preprocess_target.py")
    ap.add_argument("--out", required=True, help="Output JSON with best parameters")
    ap.add_argument("--device", default="cuda", help="cuda or cpu")
    ap.add_argument("--starts", type=int, default=16, help="Parallel multi-start batch size")
    ap.add_argument("--K", type=int, default=24, help="Max Fourier harmonics")
    ap.add_argument("--timewarp", type=int, default=3, help="Time-warp harmonics J")
    ap.add_argument("--curve-points", type=int, default=4096, help="Curve samples N per iteration")
    ap.add_argument("--cov", type=int, default=2048, help="Coverage target edge points sampled per iter")
    ap.add_argument("--steps", type=int, default=4500, help="Steps per main stage")
    ap.add_argument("--stages", type=int, default=2, choices=[1, 2, 3], help="Optimization stages")
    ap.add_argument("--seed", type=int, default=123, help="Random seed")
    ap.add_argument("--log-every", type=int, default=100, help="Logging interval")
    ap.add_argument("--tf32", action="store_true", help="Enable TF32 for speed (slightly lower numeric precision)")
    args = ap.parse_args()

    device = torch.device(args.device)

    # Performance knobs
    torch.backends.cudnn.benchmark = True
    torch.backends.cuda.matmul.allow_tf32 = bool(args.tf32)
    torch.backends.cudnn.allow_tf32 = bool(args.tf32)

    cache_path = Path(args.cache)
    dt_np, edge_pts_np, meta, res = _load_cache(cache_path)

    dt = torch.from_numpy(dt_np)[None, None, ...].to(device=device, dtype=torch.float32)
    edge_pts = torch.from_numpy(edge_pts_np).to(device=device, dtype=torch.float32)

    cfg = ModelConfig(k_max=args.K, timewarp_j=args.timewarp)
    model = FourierCurveBatch(batch=args.starts, cfg=cfg, device=device)
    model.randomize_(seed=args.seed)

    # Generator for stochastic sampling of target edge points
    rng = torch.Generator(device=device)
    rng.manual_seed(args.seed + 999)

    stages = make_stages(args.K, args.curve_points, args.steps, args.stages)

    best_global = {
        "loss": float("inf"),
        "idx": 0,
        "stage": None,
        "state_dict": None,
        "k_active": args.K,
    }

    for si, st in enumerate(stages, start=1):
        k_active = int(st["k_active"])
        n_points = int(st["n_points"])
        steps = int(st["steps"])
        lr = float(st["lr"])
        w_cov = float(st["w_cov"])
        w_reg = float(st["w_reg"])

        # Precompute t grid for this stage
        t = torch.linspace(0.0, 2.0 * math.pi, n_points, device=device, dtype=torch.float32)

        opt = torch.optim.Adam(model.parameters(), lr=lr, betas=(0.9, 0.99))
        sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(1, steps))

        pbar = trange(steps, desc=f"{st['name']} (K={k_active}, N={n_points})")
        for step in pbar:
            opt.zero_grad(set_to_none=True)

            pts = model(t, k_active=k_active)  # [B,N,2]

            # Curve->target using DT
            dt_s = sample_dt(dt, pts)
            dt_loss = dt_s.mean(dim=1) / float(res)

            # Target->curve coverage (sample a subset per iter)
            cov_loss = coverage_loss_target_to_curve(
                pts,
                edge_pts,
                max_points=args.cov,
                chunk=512,
                squared=True,
                rng=rng,
            )

            oob = oob_penalty(pts)
            reg = spectral_reg(model, k_active)

            # Loss weights
            w_dt = 1.0
            w_oob = 1.2

            loss_vec = w_dt * dt_loss + w_cov * cov_loss + w_oob * oob + w_reg * reg
            loss = loss_vec.mean()

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            opt.step()
            sched.step()

            if (step + 1) % args.log_every == 0 or step == 0 or step == steps - 1:
                with torch.no_grad():
                    best_idx = int(loss_vec.argmin().item())
                    best_val = float(loss_vec[best_idx].item())
                    pbar.set_postfix(
                        {
                            "best": f"{best_val:.5f}",
                            "dt": f"{float(dt_loss[best_idx]):.5f}",
                            "cov": f"{float(cov_loss[best_idx]):.5f}",
                            "oob": f"{float(oob[best_idx]):.5f}",
                            "lr": f"{sched.get_last_lr()[0]:.4g}",
                        }
                    )

        # Stage end: update global best
        with torch.no_grad():
            pts = model(t, k_active=k_active)
            dt_s = sample_dt(dt, pts)
            dt_loss = dt_s.mean(dim=1) / float(res)
            cov_loss = coverage_loss_target_to_curve(pts, edge_pts, max_points=min(4096, edge_pts.shape[0]), chunk=512)
            oob = oob_penalty(pts)
            reg = spectral_reg(model, k_active)
            loss_vec = 1.0 * dt_loss + w_cov * cov_loss + 1.2 * oob + w_reg * reg

            best_idx = int(loss_vec.argmin().item())
            best_val = float(loss_vec[best_idx].item())

            if best_val < best_global["loss"]:
                best_global.update(
                    {
                        "loss": best_val,
                        "idx": best_idx,
                        "stage": st["name"],
                        "k_active": k_active,
                        "state_dict": {k: v.detach().clone() for k, v in model.state_dict().items()},
                    }
                )

            print(
                f"Stage {st['name']} done. Best in stage: idx={best_idx} loss={best_val:.6f} "
                f"(global best={best_global['loss']:.6f} from {best_global['stage']})"
            )

    # Restore best state and export JSON
    if best_global["state_dict"] is not None:
        model.load_state_dict(best_global["state_dict"], strict=True)

    best_idx = int(best_global["idx"])
    k_active = int(best_global["k_active"])

    params = model.export_one(best_idx, k_active=k_active)
    params["best_loss"] = float(best_global["loss"])
    params["cache_meta"] = meta

    out_path = Path(args.out)
    out_path.write_text(json.dumps(params, indent=2), encoding="utf-8")

    print(f"Saved best params to: {out_path}")
    print(f"Best loss: {best_global['loss']:.6f} (idx={best_idx}, stage={best_global['stage']})")


if __name__ == "__main__":
    main()
