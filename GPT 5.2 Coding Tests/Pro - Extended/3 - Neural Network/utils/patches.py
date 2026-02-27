from __future__ import annotations

from typing import Tuple

import torch


def sample_patches(
    coords_flat: torch.Tensor,
    rgb_flat: torch.Tensor,
    H: int,
    W: int,
    patch_size: int,
    num_patches: int,
    rng: torch.Generator,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Sample square patches as flattened coordinate and rgb tensors.

    Returns:
        coords: (P, S*S, 2)
        rgb: (P, S*S, 3)
    """
    device = coords_flat.device
    if patch_size > H or patch_size > W:
        raise ValueError(f"Patch size {patch_size} bigger than image {H}x{W}")

    # top-left corners
    y0 = torch.randint(0, H - patch_size + 1, (num_patches,), generator=rng, device=device)
    x0 = torch.randint(0, W - patch_size + 1, (num_patches,), generator=rng, device=device)

    dy = torch.arange(patch_size, device=device)
    dx = torch.arange(patch_size, device=device)

    yy = y0[:, None, None] + dy[None, :, None]
    xx = x0[:, None, None] + dx[None, None, :]

    idx = (yy * W + xx).reshape(num_patches, -1)
    c = coords_flat[idx]
    t = rgb_flat[idx]
    return c, t
