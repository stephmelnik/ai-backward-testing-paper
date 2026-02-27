from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np
import torch


@dataclass
class CoordGrid:
    """Pixel-center coordinate grid.

    Coordinates are in [-1,1] with origin at image center.
    x increases to the right, y increases downward (image coordinates).
    """

    coords: torch.Tensor  # (H*W, 2) float32
    H: int
    W: int


def make_coord_grid(H: int, W: int, device: torch.device, dtype: torch.dtype = torch.float32) -> CoordGrid:
    # Pixel centers in [0,1]
    ys = (torch.arange(H, device=device, dtype=dtype) + 0.5) / float(H)
    xs = (torch.arange(W, device=device, dtype=dtype) + 0.5) / float(W)

    # Meshgrid -> H,W
    yy, xx = torch.meshgrid(ys, xs, indexing="ij")

    # Normalize to [-1,1], keep aspect ratio by scaling x to match y units.
    # This makes the coordinate system isotropic (important for representing circles).
    x = (xx * 2.0 - 1.0) * (float(W) / float(H))
    y = (yy * 2.0 - 1.0)

    coords = torch.stack([x, y], dim=-1).reshape(-1, 2)
    return CoordGrid(coords=coords, H=H, W=W)


def sample_pixels(
    coords: torch.Tensor,
    rgb: torch.Tensor,
    batch_size: int,
    rng: torch.Generator,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Randomly sample pixels.

    Args:
        coords: (N,2)
        rgb: (N,3)
    Returns:
        c: (B,2)
        t: (B,3)
    """
    N = coords.shape[0]
    idx = torch.randint(0, N, (batch_size,), generator=rng, device=coords.device)
    return coords[idx], rgb[idx]
