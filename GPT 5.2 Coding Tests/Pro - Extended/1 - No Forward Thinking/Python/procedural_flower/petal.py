from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from .curves import (
    add_bend_local,
    bend_x,
    scallop_offset_local,
    teardrop_points,
    teardrop_side_points,
)
from .geometry import rotate_points


@dataclass(frozen=True)
class TeardropVeinLayerSpec:
    """Specification for one family of open teardrop-side arcs inside a petal."""
    height_scale: float   # multiplies the petal height
    width_scale: float    # multiplies the petal width
    count: int            # number of arc pairs (left+right)
    spread: float         # internal fan spread in radians
    p_base: float         # base exponent for the teardrop cusp


def petal_veins_teardrop(
    angle_rad: float,
    width: float,
    height: float,
    size: float = 1.0,
    seed: int = 0,
    layers: Iterable[TeardropVeinLayerSpec] | None = None,
) -> list[np.ndarray]:
    """Generate symmetric open arcs for a petal, using teardrop-side curves.

    Compared to drawing full closed loops, open arcs read more like
    "veins" and help avoid overly circular banding.

    Args:
        angle_rad: Petal orientation, where 0 points upward.
        width, height: Petal base shape controls (local coordinates).
        size: Overall scale multiplier.
        seed: Random seed for subtle variation.
        layers: Optional specs. Defaults create 3 nested families.

    Returns:
        List of polylines (each polyline is (N,2)).
    """
    rng = np.random.default_rng(int(seed))
    curves: list[np.ndarray] = []

    if layers is None:
        layers = [
            TeardropVeinLayerSpec(height_scale=1.00, width_scale=1.00, count=60, spread=0.06, p_base=1.4),
            TeardropVeinLayerSpec(height_scale=0.85, width_scale=0.78, count=44, spread=0.04, p_base=1.5),
            TeardropVeinLayerSpec(height_scale=0.70, width_scale=0.62, count=34, spread=0.03, p_base=1.6),
        ]

    for li, layer in enumerate(layers):
        cnt = max(1, int(layer.count))
        for i in range(cnt):
            s = i / (cnt - 1) if cnt > 1 else 0.0

            wi = float(width) * float(size) * float(layer.width_scale) * (0.15 + 0.85 * (s ** 0.88))
            hi = float(height) * float(size) * float(layer.height_scale) * (0.30 + 0.70 * (s ** 1.05))

            # Cusp exponent (slightly varied)
            p = float(layer.p_base) + 1.2 * (1.0 - s)
            p += 0.05 * np.sin(2.0 * np.pi * (s * 0.8 + li * 0.2)) + 0.02 * float(rng.standard_normal())

            # Internal fan rotation
            da = (s - 0.5) * float(layer.spread)

            # Outward bend magnitude
            bend_mag = 0.10 * float(width) * float(size) * (0.2 + 0.8 * s)
            bend_mag *= 0.9 + 0.15 * np.sin(2.0 * np.pi * (s * 0.7 + li * 0.4))

            for side in (1, -1):
                pts, _t = teardrop_side_points(wi, hi, p=p, n=480, side=side)
                # Bend is applied in local coordinates (y in [0, hi])
                pts = add_bend_local(pts, y0=0.0, y1=hi, amount=bend_mag * side, a=1.2, b=0.25)
                pts = rotate_points(pts, da)
                pts = rotate_points(pts, float(angle_rad))
                curves.append(pts)

    return curves


def _segment_teardrop_loop(width: float, y0: float, y1: float, p: float = 1.6, n: int = 760) -> tuple[np.ndarray, np.ndarray]:
    """Closed teardrop loop that spans from y0 (base) to y1 (tip) in local coords."""
    h = float(y1) - float(y0)
    pts, t = teardrop_points(width=float(width), height=h, p=float(p), n=int(n))
    pts[:, 1] += float(y0)
    return pts, t


def petal_loops(
    angle_rad: float,
    width: float,
    height: float,
    size: float = 1.0,
    seed: int = 0,
) -> list[np.ndarray]:
    """Nested closed loops inside a petal (leaflet/heart structures)."""
    rng = np.random.default_rng(int(seed))
    curves: list[np.ndarray] = []

    segments = [
        # (y0_frac, y1_frac, width_weight, count)
        (0.00, 1.00, 1.00, 22),
        (0.08, 0.88, 0.75, 18),
        (0.18, 0.74, 0.58, 14),
        (0.30, 0.62, 0.45, 10),
    ]

    for (y0f, y1f, wt, count) in segments:
        y0 = float(height) * float(size) * float(y0f)
        y1 = float(height) * float(size) * float(y1f)
        count = max(1, int(count))

        for i in range(count):
            s = i / (count - 1) if count > 1 else 0.0
            wi = float(width) * float(size) * float(wt) * (0.12 + 0.88 * (s ** 0.9))
            wi *= 1.0 + 0.02 * np.sin(2.0 * np.pi * (s * 1.3 + float(y0f)))

            p = 1.2 + 1.4 * (1.0 - s)
            pts, _t = _segment_teardrop_loop(wi, y0, y1, p=p, n=760)

            # A tiny alternating bend for subtle variation
            bend_amt = 0.10 * float(width) * float(size) * (0.2 + 0.8 * s)
            bend_amt *= 0.5 + 0.5 * np.sin(2.0 * np.pi * (s * 0.8 + float(y1f)))
            sign = 1.0 if (i % 2 == 0) else -1.0
            pts = bend_x(pts, amount=bend_amt * sign * 0.15, a=1.4, b=0.7)

            da = (s - 0.5) * 0.04 + sign * 0.005
            pts = rotate_points(pts, da)
            pts = rotate_points(pts, float(angle_rad))
            curves.append(pts)

    return curves


def petal_outline(
    angle_rad: float,
    width: float,
    height: float,
    size: float = 1.0,
    seed: int = 0,
    loops: int = 3,
) -> list[np.ndarray]:
    """Scalloped outline curves for a petal."""
    rng = np.random.default_rng(int(seed))
    curves: list[np.ndarray] = []
    loops = max(1, int(loops))

    for k in range(loops):
        s = 0.90 + 0.10 * (k / (loops - 1)) if loops > 1 else 0.95
        pts, t = teardrop_points(
            width=float(width) * float(size) * s,
            height=float(height) * float(size) * s,
            p=1.18,
            n=1100,
        )

        pts = scallop_offset_local(
            pts,
            t=t,
            freq=int(30 + rng.integers(-2, 3)),
            radius=0.011 * (0.75 + 0.5 * (k / (loops - 1) if loops > 1 else 0.5)),
            start=0.40,
            power=1.6,
            phase=float(rng.random() * 2.0 * np.pi),
        )

        pts = rotate_points(pts, float(angle_rad))
        curves.append(pts)

    return curves
