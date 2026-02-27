from __future__ import annotations

import numpy as np


def rotate_points(points: np.ndarray, angle_rad: float) -> np.ndarray:
    """Rotate 2D points by angle (radians) around the origin.

    Args:
        points: Array of shape (N, 2).
        angle_rad: Rotation angle in radians.

    Returns:
        Rotated points (N, 2).
    """
    c, s = float(np.cos(angle_rad)), float(np.sin(angle_rad))
    rot = np.array([[c, -s], [s, c]], dtype=float)
    return points @ rot.T
