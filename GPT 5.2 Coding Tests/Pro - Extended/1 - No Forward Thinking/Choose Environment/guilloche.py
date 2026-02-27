import numpy as np
import random


# -----------------------------
# Core math helpers
# -----------------------------
def unit(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v, axis=1, keepdims=True)
    n = np.where(n == 0, 1.0, n)
    return v / n


def cubic_bezier(p0, p1, p2, p3, t):
    t = t[:, None]
    return (
        (1 - t) ** 3 * p0
        + 3 * (1 - t) ** 2 * t * p1
        + 3 * (1 - t) * t ** 2 * p2
        + t ** 3 * p3
    )


def cubic_bezier_tangent(p0, p1, p2, p3, t):
    t = t[:, None]
    return (
        3 * (1 - t) ** 2 * (p1 - p0)
        + 6 * (1 - t) * t * (p2 - p1)
        + 3 * t ** 2 * (p3 - p2)
    )


def bezier_points(origin, angle_deg, length, bend=0.0, bend_taper=0.6):
    """
    Build a cubic Bézier centerline:
      p0=origin -> p3=tip along angle
      bend offsets control points sideways to curve the petal.
    """
    ang = np.deg2rad(angle_deg)
    d = np.array([np.cos(ang), np.sin(ang)])
    n = np.array([-d[1], d[0]])

    p0 = np.array(origin, dtype=float)
    p3 = p0 + length * d
    p1 = p0 + length * 0.28 * d + bend * length * n
    p2 = p0 + length * 0.72 * d + bend * length * bend_taper * n
    return p0, p1, p2, p3


def beta_envelope(t, width, a=3.0, b=1.2, power=1.0):
    """
    Skewed 0..1 envelope:
      env(t)=width * normalized( t^a (1-t)^b )^power
    Gives large oscillation near the chosen peak without
    forcing a constant orbit at the endpoint.
    """
    t = np.asarray(t)
    eps = 1e-9
    tt = np.clip(t, eps, 1 - eps)
    base = (tt ** a) * ((1 - tt) ** b)
    t_peak = a / (a + b)
    peak = (t_peak**a) * ((1 - t_peak) ** b)
    env = width * (base / peak) ** power
    return env


def helix_along_bezier(p0, p1, p2, p3, t, env, freq, phase, ecc=0.85):
    """
    Oscillate around a Bézier centerline using its Frenet frame.

    offset = env * (cos(...) * N + ecc * sin(...) * T)
    """
    P = cubic_bezier(p0, p1, p2, p3, t)
    dP = cubic_bezier_tangent(p0, p1, p2, p3, t)
    T = unit(dP)
    N = np.stack([-T[:, 1], T[:, 0]], axis=1)

    ang = 2 * np.pi * freq * t + phase
    offset = (np.cos(ang)[:, None] * N + ecc * np.sin(ang)[:, None] * T) * env[:, None]
    return P + offset


# -----------------------------
# Petal primitive
# -----------------------------
def draw_petal(
    ax,
    origin,
    angle_deg,
    length,
    width,
    color,
    *,
    n_strands=35,
    lw=0.32,
    alpha=0.04,
    seed=0,
    freq=12.5,
    ecc=0.9,
    bend=0.0,
    env_a=3.0,
    env_b=1.3,
    env_power=1.0,
    angle_jitter=1.2,
    length_jitter=0.04,
    width_jitter=0.06,
    phase_jitter=0.05,
    freq_jitter=0.2,
    bend_jitter=0.04,
    n_points=2600,
):
    """
    A petal is rendered as many thin oscillating curves ("strands")
    around a Bézier centerline. Strands are phase-distributed and lightly
    jittered to create the pencil/guilloché look.
    """
    rng = random.Random(seed)
    t = np.linspace(0, 1, n_points)

    for i in range(n_strands):
        ph = 2 * np.pi * (i / n_strands) + rng.uniform(-phase_jitter, phase_jitter)
        ang = angle_deg + rng.uniform(-angle_jitter, angle_jitter)
        L = length * (1 + rng.uniform(-length_jitter, length_jitter))
        W = width * (1 + rng.uniform(-width_jitter, width_jitter))
        f = freq + rng.uniform(-freq_jitter, freq_jitter)
        b = bend + rng.uniform(-bend_jitter, bend_jitter)

        p0, p1, p2, p3 = bezier_points(origin, ang, L, bend=b)
        env = beta_envelope(t, W, a=env_a, b=env_b, power=env_power)
        Q = helix_along_bezier(p0, p1, p2, p3, t, env, f, ph, ecc=ecc)

        ax.plot(
            Q[:, 0],
            Q[:, 1],
            color=color,
            lw=lw,
            alpha=alpha,
            solid_capstyle="round",
            solid_joinstyle="round",
        )
