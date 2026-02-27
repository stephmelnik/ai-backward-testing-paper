from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple

import torch
import torch.nn.functional as F


@dataclass
class PatchLossConfig:
    patch_size: int = 64
    num_patches: int = 8
    grad_weight: float = 0.0
    ssim_weight: float = 0.0
    ssim_window: int = 11
    ssim_sigma: float = 1.5


def _gaussian_window(window_size: int, sigma: float, device: torch.device, dtype: torch.dtype) -> torch.Tensor:
    coords = torch.arange(window_size, device=device, dtype=dtype) - (window_size - 1) / 2.0
    g = torch.exp(-(coords ** 2) / (2 * sigma * sigma))
    g = g / g.sum()
    w2d = torch.outer(g, g)
    return w2d


def ssim(img1: torch.Tensor, img2: torch.Tensor, window_size: int = 11, sigma: float = 1.5) -> torch.Tensor:
    """Differentiable SSIM.

    Args:
        img1, img2: (N,C,H,W) in [0,1]
    Returns:
        scalar tensor (mean SSIM)
    """
    if img1.shape != img2.shape:
        raise ValueError("SSIM inputs must have same shape")

    N, C, H, W = img1.shape
    device = img1.device
    dtype = img1.dtype

    window = _gaussian_window(window_size, sigma, device, dtype)
    window = window.view(1, 1, window_size, window_size)
    window = window.repeat(C, 1, 1, 1)

    # use grouped conv so each channel is processed independently
    mu1 = F.conv2d(img1, window, padding=window_size // 2, groups=C)
    mu2 = F.conv2d(img2, window, padding=window_size // 2, groups=C)

    mu1_sq = mu1 * mu1
    mu2_sq = mu2 * mu2
    mu1_mu2 = mu1 * mu2

    sigma1_sq = F.conv2d(img1 * img1, window, padding=window_size // 2, groups=C) - mu1_sq
    sigma2_sq = F.conv2d(img2 * img2, window, padding=window_size // 2, groups=C) - mu2_sq
    sigma12 = F.conv2d(img1 * img2, window, padding=window_size // 2, groups=C) - mu1_mu2

    C1 = (0.01 ** 2)
    C2 = (0.03 ** 2)

    ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2) + 1e-12)
    return ssim_map.mean()


def sobel_grads(img: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
    """Compute Sobel gradients.

    Args:
        img: (N,C,H,W)
    Returns:
        gx, gy: gradients with same shape
    """
    N, C, H, W = img.shape
    device = img.device
    dtype = img.dtype

    kx = torch.tensor(
        [[-1.0, 0.0, 1.0], [-2.0, 0.0, 2.0], [-1.0, 0.0, 1.0]],
        device=device,
        dtype=dtype,
    ) / 8.0
    ky = torch.tensor(
        [[-1.0, -2.0, -1.0], [0.0, 0.0, 0.0], [1.0, 2.0, 1.0]],
        device=device,
        dtype=dtype,
    ) / 8.0

    kx = kx.view(1, 1, 3, 3).repeat(C, 1, 1, 1)
    ky = ky.view(1, 1, 3, 3).repeat(C, 1, 1, 1)

    gx = F.conv2d(img, kx, padding=1, groups=C)
    gy = F.conv2d(img, ky, padding=1, groups=C)
    return gx, gy


def patch_losses(pred: torch.Tensor, target: torch.Tensor, cfg: PatchLossConfig) -> Tuple[torch.Tensor, dict]:
    """Compute optional patch-based losses.

    Args:
        pred, target: (P,C,H,W)
    Returns:
        loss scalar, stats dict
    """
    stats = {}
    loss = pred.new_tensor(0.0)

    if cfg.grad_weight > 0.0:
        gx_p, gy_p = sobel_grads(pred)
        gx_t, gy_t = sobel_grads(target)
        grad_l = F.mse_loss(gx_p, gx_t) + F.mse_loss(gy_p, gy_t)
        loss = loss + cfg.grad_weight * grad_l
        stats["grad"] = float(grad_l.detach().cpu())

    if cfg.ssim_weight > 0.0:
        s = ssim(pred, target, window_size=cfg.ssim_window, sigma=cfg.ssim_sigma)
        # maximize ssim -> minimize (1-ssim)
        ssim_l = (1.0 - s)
        loss = loss + cfg.ssim_weight * ssim_l
        stats["ssim"] = float(s.detach().cpu())

    return loss, stats
