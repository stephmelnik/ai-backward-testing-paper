from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

from .petal import TeardropVeinLayerSpec, petal_loops, petal_outline, petal_veins_teardrop


@dataclass(frozen=True)
class FlowerParams:
    """High-level parameters controlling the flower geometry."""
    seed: int = 1
    rotation_deg: float = 0.0  # small layer rotation offset (degrees)

    base_width: float = 0.58
    base_height: float = 1.02
    big_petal_scale: float = 1.12
    small_petal_scale: float = 1.00

    # Inner (vertical) petals
    inner1_width: float = 0.28
    inner1_height: float = 0.90
    inner1_scale: float = 0.78

    inner2_width: float = 0.20
    inner2_height: float = 0.72
    inner2_scale: float = 0.60

    inner_bottom_width: float = 0.30
    inner_bottom_height: float = 0.80
    inner_bottom_scale: float = 0.70


def _petal_size_and_shape(angle_rad: float, params: FlowerParams, idx: int) -> Tuple[float, float, float]:
    """Compute (size, width, height) for a petal at a given angle."""
    size = params.big_petal_scale if (idx % 2 == 0) else params.small_petal_scale
    w = params.base_width
    h = params.base_height

    # Direction of the petal axis (local +y rotated by angle)
    dirx, diry = float(np.sin(angle_rad)), float(np.cos(angle_rad))

    # Horizontal petals: wider & slightly shorter
    if abs(dirx) > abs(diry):
        w *= 1.22
        h *= 0.92

    # Top petal: taller, a touch narrower
    if diry > 0.7:
        h *= 1.18
        w *= 0.92

    # Bottom petal: a bit taller
    if diry < -0.7:
        h *= 1.10

    return size, w, h


def build_flower_layers(params: FlowerParams) -> Dict[str, List[np.ndarray]]:
    """Build curve lists for a whole flower: fill arcs, inner loops, and scalloped outlines."""
    rot = float(np.deg2rad(params.rotation_deg))

    curves_fill: List[np.ndarray] = []
    curves_loops: List[np.ndarray] = []
    curves_outline: List[np.ndarray] = []

    # 8 petals (0 points upward; negative angles go clockwise)
    angles = [float(np.deg2rad(-k * 45.0) + rot) for k in range(8)]

    for idx, ang in enumerate(angles):
        size, w, h = _petal_size_and_shape(ang, params, idx)

        curves_fill.extend(
            petal_veins_teardrop(
                angle_rad=ang,
                width=w,
                height=h,
                size=size,
                seed=params.seed + idx * 91,
            )
        )

        curves_loops.extend(
            petal_loops(
                angle_rad=ang,
                width=w * 0.88,
                height=h,
                size=size,
                seed=params.seed + idx * 133,
            )
        )

        curves_outline.extend(
            petal_outline(
                angle_rad=ang,
                width=w,
                height=h,
                size=size,
                seed=params.seed + idx * 203,
                loops=3,
            )
        )

    # Inner vertical petals (top)
    inner_layers_1 = [
        TeardropVeinLayerSpec(height_scale=1.00, width_scale=1.00, count=70, spread=0.03, p_base=1.5),
        TeardropVeinLayerSpec(height_scale=0.85, width_scale=0.75, count=45, spread=0.02, p_base=1.6),
    ]
    curves_fill.extend(
        petal_veins_teardrop(
            angle_rad=0.0 + rot,
            width=params.inner1_width,
            height=params.inner1_height,
            size=params.inner1_scale,
            seed=params.seed + 999,
            layers=inner_layers_1,
        )
    )
    curves_loops.extend(
        petal_loops(
            angle_rad=0.0 + rot,
            width=params.inner1_width * 0.88,
            height=params.inner1_height,
            size=params.inner1_scale,
            seed=params.seed + 888,
        )
    )

    inner_layers_2 = [
        TeardropVeinLayerSpec(height_scale=1.00, width_scale=1.00, count=55, spread=0.02, p_base=1.6),
    ]
    curves_fill.extend(
        petal_veins_teardrop(
            angle_rad=0.0 + rot,
            width=params.inner2_width,
            height=params.inner2_height,
            size=params.inner2_scale,
            seed=params.seed + 1999,
            layers=inner_layers_2,
        )
    )
    curves_loops.extend(
        petal_loops(
            angle_rad=0.0 + rot,
            width=params.inner2_width * 0.88,
            height=params.inner2_height,
            size=params.inner2_scale,
            seed=params.seed + 1888,
        )
    )

    # Inner bottom petal
    inner_layers_bottom = [
        TeardropVeinLayerSpec(height_scale=1.00, width_scale=1.00, count=55, spread=0.02, p_base=1.6),
    ]
    curves_fill.extend(
        petal_veins_teardrop(
            angle_rad=float(np.pi) + rot,
            width=params.inner_bottom_width,
            height=params.inner_bottom_height,
            size=params.inner_bottom_scale,
            seed=params.seed + 2999,
            layers=inner_layers_bottom,
        )
    )
    curves_loops.extend(
        petal_loops(
            angle_rad=float(np.pi) + rot,
            width=params.inner_bottom_width * 0.88,
            height=params.inner_bottom_height,
            size=params.inner_bottom_scale,
            seed=params.seed + 2888,
        )
    )

    return {
        "fill": curves_fill,
        "loops": curves_loops,
        "outline": curves_outline,
    }
