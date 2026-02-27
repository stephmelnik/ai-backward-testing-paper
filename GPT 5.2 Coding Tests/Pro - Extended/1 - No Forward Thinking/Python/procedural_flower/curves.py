from __future__ import annotations

import numpy as np


def smoothstep(x: np.ndarray) -> np.ndarray:
    """Classic smoothstep on [0,1] with clamping."""
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def teardrop_points(width: float, height: float, p: float = 1.5, n: int = 900) -> tuple[np.ndarray, np.ndarray]:
    """Closed teardrop-like loop (cusp at base).

    Parametrization:
        x = w * sin(t) * (sin(t/2)^p)
        y = h * (1 - cos(t)) / 2

    This yields a smooth, symmetric loop that starts/ends at (0,0)
    and reaches its tip at (0, height).

    Returns:
        (points, t) where points is (n,2) and t is (n,)
    """
    t = np.linspace(0.0, 2.0 * np.pi, int(n), endpoint=True)
    s = np.sin(t / 2.0)
    x = float(width) * np.sin(t) * (s ** float(p))
    y = float(height) * (1.0 - np.cos(t)) / 2.0
    pts = np.column_stack([x, y]).astype(float)
    return pts, t


def teardrop_side_points(width: float, height: float, p: float = 1.5, n: int = 500, side: int = 1) -> tuple[np.ndarray, np.ndarray]:
    """One side of the teardrop curve from base to tip (open arc).

    The parameter t runs from 0..pi so y increases monotonically.

    Args:
        width, height: shape controls
        p: cusp exponent
        n: samples
        side: +1 (right) or -1 (left)

    Returns:
        (points, t) where points is (n,2).
    """
    t = np.linspace(0.0, np.pi, int(n), endpoint=True)
    s = np.sin(t / 2.0)
    x = float(width) * np.sin(t) * (s ** float(p))
    x *= int(side)
    y = float(height) * (1.0 - np.cos(t)) / 2.0
    pts = np.column_stack([x, y]).astype(float)
    return pts, t


def leaf_arc_segment(
    width: float,
    y0: float,
    y1: float,
    alpha: float = 0.55,
    beta: float = 0.75,
    n: int = 360,
    side: int = 1,
) -> tuple[np.ndarray, np.ndarray]:
    """Open 'leaf' arc from (0,y0) to (0,y1) on one side.

    Uses a Beta-function-like profile:
        x(u) = side * w * (u^alpha) * ((1-u)^beta)
        y(u) = y0 + (y1 - y0) * u
        u in [0,1]

    Args:
        width: Maximum x scale.
        y0: Start y.
        y1: End y.
        alpha, beta: Shape exponents (>0).
        n: Samples.
        side: +1 for right, -1 for left.

    Returns:
        (points, u)
    """
    u = np.linspace(0.0, 1.0, int(n), endpoint=True)
    y = float(y0) + (float(y1) - float(y0)) * u
    x = int(side) * float(width) * (u ** float(alpha)) * ((1.0 - u) ** float(beta))
    pts = np.column_stack([x, y]).astype(float)
    return pts, u


def _envelope(u: np.ndarray, a: float = 1.2, b: float = 0.25) -> np.ndarray:
    """Envelope that is 0 at u=0 and u=1."""
    u = np.clip(u, 0.0, 1.0)
    return (u ** float(a)) * ((1.0 - u) ** float(b))


def add_bend_local(points: np.ndarray, y0: float, y1: float, amount: float, a: float = 1.1, b: float = 0.25) -> np.ndarray:
    """Add a sideways bend along local +y axis, vanishing at endpoints."""
    y = points[:, 1]
    denom = (float(y1) - float(y0)) if float(y1) != float(y0) else 1.0
    u = (y - float(y0)) / denom
    x = points[:, 0] + float(amount) * _envelope(u, a=a, b=b)
    return np.column_stack([x, y]).astype(float)


def bend_x(points: np.ndarray, amount: float = 0.0, a: float = 1.4, b: float = 0.7) -> np.ndarray:
    """General-purpose bend using a normalized y envelope (closed curves)."""
    y = points[:, 1]
    y_min = float(y.min())
    y_ptp = float(np.ptp(y)) if float(np.ptp(y)) != 0.0 else 1.0
    u = (y - y_min) / y_ptp
    x = points[:, 0] + float(amount) * _envelope(u, a=a, b=b)
    return np.column_stack([x, y]).astype(float)


def scallop_offset_local(
    points: np.ndarray,
    t: np.ndarray,
    freq: int = 26,
    radius: float = 0.012,
    start: float = 0.55,
    power: float = 1.6,
    phase: float = 0.0,
) -> np.ndarray:
    """Add small loop-like scallops by offsetting along local tangent/normal.

    This creates a guilloché-like 'looping' edge when applied to an outline curve.
    Amplitude is ramped up only for the upper portion of the curve (by y).

    Args:
        points: (N,2) curve.
        t: (N,) parameter samples (same length).
        freq: Oscillation frequency along curve.
        radius: Max loop radius.
        start: y-normalized threshold where loops begin (0..1).
        power: Envelope exponent.
        phase: Phase offset.

    Returns:
        Offset points.
    """
    pts = np.asarray(points, dtype=float)
    tt = np.asarray(t, dtype=float)

    # Local frames
    dp = np.gradient(pts, axis=0)
    tang = dp / (np.linalg.norm(dp, axis=1, keepdims=True) + 1e-9)
    normal = np.column_stack([-tang[:, 1], tang[:, 0]])

    y = pts[:, 1]
    y_norm = (y - float(y.min())) / (float(np.ptp(y)) + 1e-9)
    env = smoothstep((y_norm - float(start)) / (1.0 - float(start)))
    env = env ** float(power)

    ph = float(freq) * tt + float(phase)
    amp = float(radius) * env
    offset = (np.cos(ph)[:, None] * normal + np.sin(ph)[:, None] * tang) * amp[:, None]
    return (pts + offset).astype(float)
