from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection


@dataclass(frozen=True)
class StrokeStyle:
    color: Tuple[float, float, float]
    linewidth: float
    alpha: float = 0.08

    # Optional per-curve alpha ramp (helps mimic pencil density)
    alpha_min: float | None = None
    alpha_max: float | None = None
    alpha_gamma: float = 1.8


@dataclass(frozen=True)
class RenderConfig:
    size_px: int = 2048
    dpi: int = 256
    view_lim: float = 1.7
    background: Tuple[float, float, float] = (0.98, 0.95, 0.92)  # warm paper
    vignette_strength: float = 0.10  # 0..1
    vignette_power: float = 2.2


def _add_vignette(ax: plt.Axes, cfg: RenderConfig) -> None:
    """Subtle radial edge darkening to mimic paper/vignette."""
    if cfg.vignette_strength <= 0:
        return
    n = 600
    x = np.linspace(-1.0, 1.0, n)
    xx, yy = np.meshgrid(x, x)
    rr = np.sqrt(xx * xx + yy * yy)
    rr = np.clip(rr, 0.0, 1.0)
    alpha = (rr ** cfg.vignette_power) * cfg.vignette_strength
    rgba = np.zeros((n, n, 4), dtype=float)
    rgba[..., 3] = alpha  # black with varying alpha
    ax.imshow(
        rgba,
        extent=(-cfg.view_lim, cfg.view_lim, -cfg.view_lim, cfg.view_lim),
        interpolation="bilinear",
        zorder=0,
    )


def _curve_radii(curves: List[np.ndarray]) -> np.ndarray:
    """A cheap per-curve scale heuristic: max distance to origin."""
    radii = np.zeros(len(curves), dtype=float)
    for i, c in enumerate(curves):
        radii[i] = float(np.max(np.linalg.norm(c, axis=1)))
    return radii


def _build_colors(curves: List[np.ndarray], style: StrokeStyle) -> List[Tuple[float, float, float, float]]:
    if style.alpha_min is None or style.alpha_max is None or len(curves) == 0:
        return [(*style.color, float(style.alpha))] * len(curves)

    r = _curve_radii(curves)
    rmin, rmax = float(r.min()), float(r.max())
    denom = (rmax - rmin) if rmax != rmin else 1.0
    rn = (r - rmin) / denom
    a = float(style.alpha_min) + (float(style.alpha_max) - float(style.alpha_min)) * (rn ** float(style.alpha_gamma))
    a = np.clip(a, 0.0, 1.0)
    return [(*style.color, float(ai)) for ai in a]


def render(
    out_path: str | Path,
    layers_by_color: Dict[str, Dict[str, List[np.ndarray]]],
    styles: Dict[str, Dict[str, StrokeStyle]],
    cfg: RenderConfig = RenderConfig(),
) -> Path:
    """Render the flower to a PNG/SVG/PDF via Matplotlib."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    figsize = (cfg.size_px / cfg.dpi, cfg.size_px / cfg.dpi)
    fig, ax = plt.subplots(figsize=figsize, dpi=cfg.dpi)
    fig.patch.set_facecolor(cfg.background)
    ax.set_facecolor(cfg.background)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-cfg.view_lim, cfg.view_lim)
    ax.set_ylim(-cfg.view_lim, cfg.view_lim)

    # Remove default matplotlib padding so the output is exactly size_px × size_px
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

    _add_vignette(ax, cfg)

    # Draw order: fill -> loops -> outline (for each color layer)
    for color_key in ("pink", "blue"):
        if color_key not in layers_by_color:
            continue
        layer_groups = layers_by_color[color_key]
        style_groups = styles.get(color_key, {})

        for group_name, z in (("fill", 2), ("loops", 3), ("outline", 4)):
            curves = layer_groups.get(group_name, [])
            if not curves:
                continue
            st = style_groups.get(group_name)
            if st is None:
                continue

            colors = _build_colors(curves, st)
            lc = LineCollection(
                curves,
                colors=colors,
                linewidths=st.linewidth,
                capstyle="round",
                joinstyle="round",
                zorder=z,
            )
            ax.add_collection(lc)

    fig.savefig(out_path, facecolor=cfg.background, pad_inches=0.0)
    plt.close(fig)
    return out_path
