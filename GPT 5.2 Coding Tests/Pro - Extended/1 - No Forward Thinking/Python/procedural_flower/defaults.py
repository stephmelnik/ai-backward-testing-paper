from __future__ import annotations

from .flower import FlowerParams
from .render import RenderConfig, StrokeStyle


def default_flower_params() -> tuple[FlowerParams, FlowerParams]:
    """Two-layer setup (pink + blue) with a tiny rotation offset."""
    pink = FlowerParams(seed=2, rotation_deg=1.0)
    blue = FlowerParams(seed=1, rotation_deg=0.0)
    return pink, blue


def default_styles() -> dict[str, dict[str, StrokeStyle]]:
    """Stroke styles tuned for a soft pencil/ink look."""
    blue = (0.45, 0.45, 0.75)
    pink = (0.92, 0.60, 0.70)

    return {
        "pink": {
            "fill": StrokeStyle(color=pink, linewidth=0.22, alpha_min=0.025, alpha_max=0.065, alpha_gamma=1.7),
            "loops": StrokeStyle(color=pink, linewidth=0.24, alpha_min=0.030, alpha_max=0.085, alpha_gamma=1.6),
            "outline": StrokeStyle(color=pink, linewidth=0.30, alpha_min=0.050, alpha_max=0.110, alpha_gamma=1.4),
        },
        "blue": {
            "fill": StrokeStyle(color=blue, linewidth=0.22, alpha_min=0.025, alpha_max=0.065, alpha_gamma=1.7),
            "loops": StrokeStyle(color=blue, linewidth=0.24, alpha_min=0.030, alpha_max=0.085, alpha_gamma=1.6),
            "outline": StrokeStyle(color=blue, linewidth=0.30, alpha_min=0.050, alpha_max=0.110, alpha_gamma=1.4),
        },
    }


def default_render_config() -> RenderConfig:
    return RenderConfig(size_px=2048, dpi=256, view_lim=1.7, vignette_strength=0.10)
