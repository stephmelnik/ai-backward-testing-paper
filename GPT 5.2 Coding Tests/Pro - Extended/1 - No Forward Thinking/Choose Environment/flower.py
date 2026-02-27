from dataclasses import dataclass, field
from guilloche import draw_petal


@dataclass
class FlowerPalette:
    background: str = "#f7f1e8"
    pink: tuple = (0.88, 0.52, 0.68)
    blue: tuple = (0.38, 0.44, 0.85)


@dataclass
class FlowerStyle:
    palette: FlowerPalette = field(default_factory=FlowerPalette)
    line_width: float = 0.32
    # opacity tuned for “colored pencil” feel
    alpha_pink: float = 0.040
    alpha_blue: float = 0.050


def draw_flower(ax, origin=(0.0, -0.30), style: FlowerStyle = FlowerStyle()):
    """
    Structured composition:
    - Outer pink petals (wider)
    - Inner blue petals (narrower)
    - Light center spine lines
    """
    p = style.palette
    lw = style.line_width
    ap = style.alpha_pink
    ab = style.alpha_blue

    # ---------------------------
    # Outer layer (pink)
    # ---------------------------
    draw_petal(ax, origin, 90, 1.70, 0.55, p.pink,
              n_strands=35, lw=lw, alpha=ap, seed=1,
              freq=13.0, ecc=0.95, bend=0.00,
              env_a=4.0, env_b=1.2,
              angle_jitter=1.0)

    for ang, sgn, seed in [(60, 1, 2), (120, -1, 3)]:
        draw_petal(ax, origin, ang, 1.35, 0.48, p.pink,
                  n_strands=30, lw=lw, alpha=ap, seed=seed,
                  freq=12.5, ecc=0.92, bend=0.18*sgn,
                  env_a=3.5, env_b=1.4,
                  angle_jitter=1.2)

    for ang, sgn, seed in [(15, 1, 4), (165, -1, 5)]:
        draw_petal(ax, origin, ang, 1.55, 0.58, p.pink,
                  n_strands=35, lw=lw, alpha=ap*0.90, seed=seed,
                  freq=12.0, ecc=0.90, bend=0.22*sgn,
                  env_a=3.0, env_b=1.8,
                  angle_jitter=1.4)

    for ang, sgn, seed in [(0, 1, 6), (180, -1, 7)]:
        draw_petal(ax, origin, ang, 1.60, 0.60, p.pink,
                  n_strands=35, lw=lw, alpha=ap*0.90, seed=seed,
                  freq=12.0, ecc=0.90, bend=0.25*sgn,
                  env_a=3.0, env_b=1.9,
                  angle_jitter=1.4)

    for ang, sgn, seed in [(-25, 1, 8), (-155, -1, 9)]:
        draw_petal(ax, origin, ang, 1.35, 0.55, p.pink,
                  n_strands=30, lw=lw, alpha=ap*0.90, seed=seed,
                  freq=12.5, ecc=0.90, bend=0.20*sgn,
                  env_a=2.6, env_b=2.2,
                  angle_jitter=1.4)

    for ang, sgn, seed in [(-45, 1, 10), (-135, -1, 11)]:
        draw_petal(ax, origin, ang, 1.25, 0.52, p.pink,
                  n_strands=30, lw=lw, alpha=ap*0.90, seed=seed,
                  freq=12.5, ecc=0.90, bend=0.18*sgn,
                  env_a=2.4, env_b=2.4,
                  angle_jitter=1.4)

    for ang, sgn, seed in [(-70, 1, 12), (-110, -1, 13)]:
        draw_petal(ax, origin, ang, 1.15, 0.72, p.pink,
                  n_strands=40, lw=lw, alpha=ap*0.90, seed=seed,
                  freq=13.0, ecc=0.95, bend=0.05*sgn,
                  env_a=2.0, env_b=2.8,
                  angle_jitter=1.0)

    # ---------------------------
    # Inner layer (blue)
    # ---------------------------
    draw_petal(ax, origin, 90, 1.55, 0.35, p.blue,
              n_strands=45, lw=lw, alpha=ab, seed=21,
              freq=13.5, ecc=0.98, bend=0.00,
              env_a=4.2, env_b=1.3,
              angle_jitter=0.8)

    for ang, sgn, seed in [(80, 1, 22), (100, -1, 23)]:
        draw_petal(ax, origin, ang, 1.40, 0.26, p.blue,
                  n_strands=35, lw=lw, alpha=ab*0.95, seed=seed,
                  freq=13.0, ecc=0.95, bend=0.08*sgn,
                  env_a=3.8, env_b=1.5,
                  angle_jitter=0.8)

    for ang, sgn, seed in [(65, 1, 24), (115, -1, 25)]:
        draw_petal(ax, origin, ang, 1.30, 0.25, p.blue,
                  n_strands=35, lw=lw, alpha=ab*0.90, seed=seed,
                  freq=12.5, ecc=0.92, bend=0.12*sgn,
                  env_a=3.4, env_b=1.6,
                  angle_jitter=1.0)

    for ang, sgn, seed in [(10, 1, 26), (170, -1, 27)]:
        draw_petal(ax, origin, ang, 1.45, 0.45, p.blue,
                  n_strands=40, lw=lw, alpha=ab*0.85, seed=seed,
                  freq=12.5, ecc=0.90, bend=0.18*sgn,
                  env_a=3.0, env_b=2.0,
                  angle_jitter=1.2)

    for ang, sgn, seed in [(0, 1, 28), (180, -1, 29)]:
        draw_petal(ax, origin, ang, 1.45, 0.42, p.blue,
                  n_strands=40, lw=lw, alpha=ab*0.85, seed=seed,
                  freq=12.5, ecc=0.90, bend=0.20*sgn,
                  env_a=3.0, env_b=2.1,
                  angle_jitter=1.2)

    for ang, sgn, seed in [(-30, 1, 30), (-150, -1, 31)]:
        draw_petal(ax, origin, ang, 1.20, 0.40, p.blue,
                  n_strands=35, lw=lw, alpha=ab*0.85, seed=seed,
                  freq=12.8, ecc=0.90, bend=0.16*sgn,
                  env_a=2.6, env_b=2.4,
                  angle_jitter=1.2)

    for ang, sgn, seed in [(-50, 1, 32), (-130, -1, 33)]:
        draw_petal(ax, origin, ang, 1.10, 0.38, p.blue,
                  n_strands=35, lw=lw, alpha=ab*0.85, seed=seed,
                  freq=12.8, ecc=0.90, bend=0.14*sgn,
                  env_a=2.5, env_b=2.5,
                  angle_jitter=1.2)

    for ang, sgn, seed in [(-75, 1, 34), (-105, -1, 35)]:
        draw_petal(ax, origin, ang, 1.05, 0.50, p.blue,
                  n_strands=45, lw=lw, alpha=ab*0.90, seed=seed,
                  freq=13.2, ecc=0.95, bend=0.03*sgn,
                  env_a=2.1, env_b=3.0,
                  angle_jitter=0.8)

    # ---------------------------
    # Center spine accents
    # ---------------------------
    ax.plot([origin[0], origin[0]], [origin[1], origin[1] + 1.8],
            color=p.blue, lw=lw, alpha=0.25)
    ax.plot([origin[0], origin[0]], [origin[1], origin[1] - 1.5],
            color=p.pink, lw=lw, alpha=0.18)
