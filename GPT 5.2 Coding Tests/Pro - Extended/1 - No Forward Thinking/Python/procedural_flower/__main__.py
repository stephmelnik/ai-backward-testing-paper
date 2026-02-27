from .defaults import default_flower_params, default_render_config, default_styles
from .flower import build_flower_layers
from .render import render


def main() -> None:
    pink_params, blue_params = default_flower_params()
    cfg = default_render_config()
    styles = default_styles()

    layers_by_color = {
        "pink": build_flower_layers(pink_params),
        "blue": build_flower_layers(blue_params),
    }

    render("generated_flower.png", layers_by_color=layers_by_color, styles=styles, cfg=cfg)


if __name__ == "__main__":
    main()
