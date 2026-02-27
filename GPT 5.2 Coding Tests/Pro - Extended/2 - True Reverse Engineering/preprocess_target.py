import argparse
import json
from pathlib import Path

import cv2
import numpy as np


def _center_crop_square(img: np.ndarray) -> np.ndarray:
    h, w = img.shape[:2]
    side = min(h, w)
    y0 = (h - side) // 2
    x0 = (w - side) // 2
    return img[y0 : y0 + side, x0 : x0 + side]


def _ink_channel(bgr: np.ndarray, mode: str) -> np.ndarray:
    """Return a single-channel uint8 image where "ink" is high."""
    if mode == "chroma":
        # Chroma magnitude in Lab. Works well for colored ink on a neutral paper background.
        lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
        a = lab[:, :, 1].astype(np.float32) - 128.0
        b = lab[:, :, 2].astype(np.float32) - 128.0
        chroma = np.sqrt(a * a + b * b)

        # Robust normalization to [0, 255]
        scale = np.percentile(chroma, 99.9)
        scale = max(scale, 1e-6)
        chroma_u8 = np.clip(chroma / scale * 255.0, 0.0, 255.0).astype(np.uint8)
        return chroma_u8

    if mode == "gray":
        return cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    raise ValueError(f"Unknown ink mode: {mode}")


def _auto_canny_thresholds(img_u8: np.ndarray, low_p: float, high_p: float) -> tuple[int, int]:
    vals = img_u8.reshape(-1)
    lo = float(np.percentile(vals, low_p))
    hi = float(np.percentile(vals, high_p))
    # Ensure valid ordering.
    if hi <= lo:
        hi = lo + 1.0
    lo_i = int(np.clip(lo, 0, 254))
    hi_i = int(np.clip(hi, lo_i + 1, 255))
    return lo_i, hi_i


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True, help="Path to target image")
    ap.add_argument("--cache", required=True, help="Output cache .npz")
    ap.add_argument("--res", type=int, default=512, help="Square resolution for preprocessing")
    ap.add_argument(
        "--ink-mode",
        choices=["chroma", "gray"],
        default="chroma",
        help="How to extract ink signal before edge detection",
    )
    ap.add_argument("--blur", type=float, default=1.0, help="Gaussian blur sigma")
    ap.add_argument("--canny-low-p", type=float, default=70.0, help="Low threshold percentile")
    ap.add_argument("--canny-high-p", type=float, default=95.0, help="High threshold percentile")
    ap.add_argument("--dilate", type=int, default=0, help="Dilate edges by N pixels (0 disables)")
    ap.add_argument("--edge-samples", type=int, default=20000, help="How many edge points to store")
    ap.add_argument("--seed", type=int, default=123, help="Sampling seed")
    args = ap.parse_args()

    target_path = Path(args.target)
    if not target_path.exists():
        raise FileNotFoundError(str(target_path))

    bgr = cv2.imread(str(target_path), cv2.IMREAD_COLOR)
    if bgr is None:
        raise RuntimeError(f"cv2.imread failed: {target_path}")

    # Crop and resize to square.
    bgr_sq = _center_crop_square(bgr)
    bgr_sq = cv2.resize(bgr_sq, (args.res, args.res), interpolation=cv2.INTER_AREA)

    ink = _ink_channel(bgr_sq, args.ink_mode)
    if args.blur > 0:
        k = int(max(3, (args.blur * 6) // 2 * 2 + 1))
        ink = cv2.GaussianBlur(ink, (k, k), sigmaX=args.blur, sigmaY=args.blur)

    lo, hi = _auto_canny_thresholds(ink, args.canny_low_p, args.canny_high_p)
    edges = cv2.Canny(ink, lo, hi, L2gradient=True)

    if args.dilate > 0:
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (args.dilate * 2 + 1, args.dilate * 2 + 1))
        edges = cv2.dilate(edges, kernel, iterations=1)

    # Distance transform: distance to nearest edge pixel.
    # distanceTransform treats 0 pixels as "obstacles" (distance 0). So we want edges to be 0.
    inv = 255 - edges
    inv = (inv > 0).astype(np.uint8) * 255
    dt = cv2.distanceTransform(inv, distanceType=cv2.DIST_L2, maskSize=3).astype(np.float32)

    # Edge mask 0/1
    edge_mask = (edges > 0).astype(np.uint8)

    # Sample edge points in normalized [-1, 1] coords for PyTorch grid_sample.
    ys, xs = np.nonzero(edge_mask)
    if len(xs) == 0:
        raise RuntimeError("No edges found. Try changing --ink-mode or Canny percentiles.")

    pts = np.stack(
        [
            (xs.astype(np.float32) / (args.res - 1)) * 2.0 - 1.0,
            (ys.astype(np.float32) / (args.res - 1)) * 2.0 - 1.0,
        ],
        axis=1,
    )

    rng = np.random.default_rng(args.seed)
    n_keep = min(args.edge_samples, pts.shape[0])
    keep_idx = rng.choice(pts.shape[0], size=n_keep, replace=False)
    edge_points = pts[keep_idx].astype(np.float32)

    meta = {
        "target": str(target_path.name),
        "res": int(args.res),
        "ink_mode": args.ink_mode,
        "blur": float(args.blur),
        "canny_low_p": float(args.canny_low_p),
        "canny_high_p": float(args.canny_high_p),
        "dilate": int(args.dilate),
        "edge_points_total": int(pts.shape[0]),
        "edge_points_kept": int(edge_points.shape[0]),
    }

    out_path = Path(args.cache)
    np.savez_compressed(
        str(out_path),
        dt=dt,
        edge_mask=edge_mask,
        edge_points=edge_points,
        meta=json.dumps(meta),
    )

    print(f"Saved cache: {out_path}")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
