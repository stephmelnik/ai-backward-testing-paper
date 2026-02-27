from __future__ import annotations

import argparse
from pathlib import Path

from procedural_flower.defaults import default_flower_params, default_render_config, default_styles
from procedural_flower.flower import build_flower_layers
from procedural_flower.render import render


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Procedurally generate a lotus-like line-art flower.")
    p.add_argument("--out", type=str, default="generated_flower.png", help="Output image path (png/svg/pdf).")
    p.add_argument("--size", type=int, default=2048, help="Canvas size in pixels (square). Default: 2048")
    p.add_argument("--dpi", type=int, default=256, help="Matplotlib DPI. Default: 256")
    p.add_argument("--vlim", type=float, default=1.7, help="View limit for x/y (controls zoom). Default: 1.7")
    p.add_argument("--vignette", type=float, default=0.10, help="Vignette strength 0..1. Default: 0.10")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    out_path = Path(args.out)

    pink_params, blue_params = default_flower_params()
    cfg = default_render_config()
    styles = default_styles()

    # Override a few render settings from CLI
    cfg = cfg.__class__(
        size_px=int(args.size),
        dpi=int(args.dpi),
        view_lim=float(args.vlim),
        background=cfg.background,
        vignette_strength=float(args.vignette),
        vignette_power=cfg.vignette_power,
    )

    layers_by_color = {
        "pink": build_flower_layers(pink_params),
        "blue": build_flower_layers(blue_params),
    }

    out_file = render(out_path, layers_by_color=layers_by_color, styles=styles, cfg=cfg)
    print(f"Wrote: {out_file.resolve()}")  # noqa: T201


if __name__ == "__main__":
    main()
