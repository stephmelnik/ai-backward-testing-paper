from __future__ import annotations

import torch
import torch.nn.functional as F


def sample_dt(dt: torch.Tensor, pts: torch.Tensor) -> torch.Tensor:
    """Sample a distance transform image at curve points.

    Args:
        dt: Tensor [1,1,H,W] or [B,1,H,W] (float32 preferred)
        pts: Tensor [B,N,2] in normalized coords [-1,1] (x,y)

    Returns:
        samples: [B,N]
    """
    assert pts.ndim == 3 and pts.shape[-1] == 2
    B, N, _ = pts.shape

    if dt.ndim != 4:
        raise ValueError("dt must be [B,1,H,W] or [1,1,H,W]")

    if dt.shape[0] == 1 and B > 1:
        dt_b = dt.expand(B, -1, -1, -1)
    elif dt.shape[0] == B:
        dt_b = dt
    else:
        raise ValueError(f"dt batch mismatch: dt has {dt.shape[0]} but pts has {B}")

    # grid_sample expects grid [B, H_out, W_out, 2]
    grid = pts.view(B, N, 1, 2)
    out = F.grid_sample(dt_b, grid, mode="bilinear", padding_mode="border", align_corners=True)
    return out[:, 0, :, 0]  # [B,N]


def oob_penalty(pts: torch.Tensor) -> torch.Tensor:
    """Out-of-bounds penalty for points leaving [-1,1]^2.

    Returns per-candidate vector [B].
    """
    excess = F.relu(torch.abs(pts) - 1.0)  # [B,N,2]
    return (excess * excess).mean(dim=(1, 2))


def coverage_loss_target_to_curve(
    curve_pts: torch.Tensor,
    target_edge_pts: torch.Tensor,
    *,
    max_points: int = 2048,
    chunk: int = 512,
    squared: bool = True,
    rng: torch.Generator | None = None,
) -> torch.Tensor:
    """Coverage loss: average distance from target edge points to nearest curve point.

    This prevents the curve from matching only a small subset of edges.

    Args:
        curve_pts: [B,N,2]
        target_edge_pts: [M,2]
        max_points: number of target points to sample per iteration
        chunk: chunk size for cdist to reduce peak memory
        squared: if True, uses squared distance
        rng: optional torch Generator

    Returns:
        per-candidate loss [B]
    """
    B, N, _ = curve_pts.shape
    M = target_edge_pts.shape[0]
    if M == 0:
        raise ValueError("target_edge_pts is empty")

    if max_points is not None and M > max_points:
        idx = torch.randint(0, M, (max_points,), device=curve_pts.device, generator=rng)
        pts = target_edge_pts[idx]
    else:
        pts = target_edge_pts

    # Accumulate mean of min distances in chunks over target points.
    total = torch.zeros(B, device=curve_pts.device, dtype=curve_pts.dtype)
    count = 0
    for start in range(0, pts.shape[0], chunk):
        q = pts[start : start + chunk]  # [c,2]
        # d: [B,N,c]
        d = torch.cdist(curve_pts, q[None, :, :].expand(B, -1, -1))
        # min over curve points => nearest curve point for each target point
        m = d.min(dim=1).values  # [B,c]
        if squared:
            m = m * m
        total += m.mean(dim=1)
        count += 1

    return total / max(count, 1)
