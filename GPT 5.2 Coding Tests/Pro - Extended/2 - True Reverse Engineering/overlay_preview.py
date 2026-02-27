import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image

from render_fourier import eval_curve


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True, help="target_cache.npz")
    ap.add_argument("--params", required=True, help="best_params.json")
    ap.add_argument("--out", required=True, help="Output PNG")
    ap.add_argument("--size", type=int, default=1024, help="Output size")
    ap.add_argument("--curve-points", type=int, default=20000, help="Curve samples")
    args = ap.parse_args()

    data = np.load(args.cache, allow_pickle=True)
    edge = data["edge_mask"].astype(np.uint8)

    params = json.loads(Path(args.params).read_text(encoding="utf-8"))
    pts = eval_curve(params, n_points=int(args.curve_points))

    # Resize edge mask to output size
    import cv2

    edge_r = cv2.resize(edge, (args.size, args.size), interpolation=cv2.INTER_NEAREST)

    # Base RGB image: edges in red
    img = np.zeros((args.size, args.size, 3), dtype=np.uint8)
    img[..., 0] = (edge_r > 0) * 220

    # Draw curve in cyan by splatting points
    x = ((pts[:, 0] + 1.0) * 0.5 * (args.size - 1)).astype(np.int32)
    y = ((pts[:, 1] + 1.0) * 0.5 * (args.size - 1)).astype(np.int32)
    valid = (x >= 0) & (x < args.size) & (y >= 0) & (y < args.size)
    x = x[valid]
    y = y[valid]
    img[y, x, 1] = 220
    img[y, x, 2] = 220

    Image.fromarray(img).save(args.out)
    print(f"Saved: {args.out}")


if __name__ == "__main__":
    main()
