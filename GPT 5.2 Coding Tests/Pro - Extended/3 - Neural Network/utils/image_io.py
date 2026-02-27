from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Tuple

import numpy as np
from PIL import Image


@dataclass
class ImageTensor:
    """Holds an image as float32 in [0,1] with shape (H,W,3)."""

    data: np.ndarray  # float32, HWC, RGB, [0,1]

    @property
    def shape(self) -> Tuple[int, int, int]:
        return self.data.shape

    @property
    def h(self) -> int:
        return int(self.data.shape[0])

    @property
    def w(self) -> int:
        return int(self.data.shape[1])


def load_image_rgb(path: str) -> ImageTensor:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Image not found: {path}")

    img = Image.open(path).convert("RGB")
    arr = np.asarray(img).astype(np.float32) / 255.0
    return ImageTensor(arr)


def save_image_rgb(path: str, rgb01_hwc: np.ndarray) -> None:
    """Save float image in [0,1] HWC RGB."""
    rgb01_hwc = np.clip(rgb01_hwc, 0.0, 1.0)
    img = Image.fromarray((rgb01_hwc * 255.0 + 0.5).astype(np.uint8), mode="RGB")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    img.save(path)

