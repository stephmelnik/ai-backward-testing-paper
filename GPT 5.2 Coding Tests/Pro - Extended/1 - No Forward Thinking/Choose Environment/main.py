import argparse
import matplotlib.pyplot as plt
from flower import draw_flower, FlowerStyle, FlowerPalette


def render(output_path: str, size: int = 2048):
    """
    Render the procedural flower to a PNG.
    """
    palette = FlowerPalette()
    style = FlowerStyle(palette=palette)

    # Choose dpi so that figsize * dpi = size
    dpi = 256
    inches = size / dpi

    fig, ax = plt.subplots(figsize=(inches, inches), dpi=dpi, facecolor=palette.background)
    ax.set_facecolor(palette.background)

    draw_flower(ax, origin=(0.0, -0.30), style=style)

    # Frame similar to reference composition
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-2.2, 2.2)
    ax.set_ylim(-2.4, 2.1)

    fig.savefig(output_path, facecolor=palette.background, bbox_inches="tight", pad_inches=0)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", default="output.png", help="Output PNG filename")
    parser.add_argument("-s", "--size", type=int, default=2048, help="Output size in pixels (square)")
    args = parser.parse_args()

    render(args.output, args.size)
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
