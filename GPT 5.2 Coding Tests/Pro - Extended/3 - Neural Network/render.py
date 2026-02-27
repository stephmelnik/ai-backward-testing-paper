from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import torch

from models.inr import INR, INRConfig
from utils.coords import make_coord_grid
from utils.image_io import save_image_rgb


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Render a reconstruction from a trained INR checkpoint")
    p.add_argument("--ckpt", type=str, required=True, help="Path to model checkpoint (.pt)")
    p.add_argument("--out", type=str, required=True, help="Output image path (PNG recommended)")
    p.add_argument("--H", type=int, default=0, help="Height (defaults to checkpoint H)")
    p.add_argument("--W", type=int, default=0, help="Width (defaults to checkpoint W)")
    p.add_argument("--chunk", type=int, default=1_000_000, help="#pixels per inference chunk")
    return p.parse_args()


@torch.no_grad()
def render(model: torch.nn.Module, H: int, W: int, device: torch.device, chunk: int) -> torch.Tensor:
    grid = make_coord_grid(H, W, device=device, dtype=torch.float32)
    coords = grid.coords
    out_chunks = []
    for i in range(0, coords.shape[0], chunk):
        out_chunks.append(model(coords[i : i + chunk]).detach())
    out = torch.cat(out_chunks, dim=0)
    return out.reshape(H, W, 3)


def main() -> None:
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    ckpt = torch.load(args.ckpt, map_location=device, weights_only=False)
    cfg = INRConfig(**ckpt["cfg"]) if isinstance(ckpt.get("cfg"), dict) else INRConfig()
    model = INR(cfg).to(device)
    model.load_state_dict(ckpt["model"], strict=True)
    model.eval()

    H = int(args.H) if args.H > 0 else int(ckpt.get("H"))
    W = int(args.W) if args.W > 0 else int(ckpt.get("W"))
    if H <= 0 or W <= 0:
        raise ValueError("H/W must be provided either via args or checkpoint")

    recon = render(model, H, W, device=device, chunk=args.chunk)
    save_image_rgb(args.out, recon.detach().cpu().numpy())
    print(f"Saved: {args.out}")


if __name__ == "__main__":
    main()
