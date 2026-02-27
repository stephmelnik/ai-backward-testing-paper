from __future__ import annotations

import math

import numpy as np
import torch

from losses import ssim as ssim_torch


def psnr(pred: torch.Tensor, target: torch.Tensor) -> float:
    """Compute PSNR for images in [0,1].

    Args:
        pred, target: (H,W,3) float tensors
    """
    mse = torch.mean((pred - target) ** 2).item()
    if mse <= 1e-12:
        return float("inf")
    return 10.0 * math.log10(1.0 / mse)


def ssim(pred: torch.Tensor, target: torch.Tensor, window_size: int = 11, sigma: float = 1.5) -> float:
    # to NCHW
    p = pred.permute(2, 0, 1).unsqueeze(0)
    t = target.permute(2, 0, 1).unsqueeze(0)
    return float(ssim_torch(p, t, window_size=window_size, sigma=sigma).item())
