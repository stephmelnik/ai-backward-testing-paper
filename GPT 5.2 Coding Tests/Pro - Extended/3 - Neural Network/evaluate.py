from __future__ import annotations

import argparse

import torch

from metrics import psnr, ssim
from utils.image_io import load_image_rgb


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate PSNR/SSIM between target and reconstruction")
    p.add_argument("--image", type=str, required=True, help="Path to target image")
    p.add_argument("--recon", type=str, required=True, help="Path to reconstructed image")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    tgt = load_image_rgb(args.image)
    rec = load_image_rgb(args.recon)

    if tgt.shape != rec.shape:
        raise ValueError(f"Shape mismatch: target={tgt.shape} recon={rec.shape}")

    t = torch.from_numpy(tgt.data).float()
    r = torch.from_numpy(rec.data).float()

    p = psnr(r, t)
    s = ssim(r, t)

    print(f"PSNR: {p:.2f} dB")
    print(f"SSIM: {s:.4f}")


if __name__ == "__main__":
    main()
