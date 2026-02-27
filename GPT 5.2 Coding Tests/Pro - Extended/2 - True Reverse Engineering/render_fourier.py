import argparse
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def eval_curve(params: dict, n_points: int) -> np.ndarray:
    K = int(params.get("k_active", params.get("k_max", 24)))
    axc = np.asarray(params["ax_cos"], dtype=np.float32)[:K]
    axs = np.asarray(params["ax_sin"], dtype=np.float32)[:K]
    ayc = np.asarray(params["ay_cos"], dtype=np.float32)[:K]
    ays = np.asarray(params["ay_sin"], dtype=np.float32)[:K]

    scale = float(params["scale"])
    rot = float(params["rot_rad"])
    trans = np.asarray(params["trans"], dtype=np.float32)

    J = int(params.get("timewarp_j", 0))
    tw_sin = np.asarray(params.get("timewarp_sin", []), dtype=np.float32)
    tw_cos = np.asarray(params.get("timewarp_cos", []), dtype=np.float32)

    t = np.linspace(0.0, 2.0 * math.pi, n_points, endpoint=False, dtype=np.float32)

    # time warp
    if J > 0 and tw_sin.size >= J and tw_cos.size >= J:
        tp = t.copy()
        for j in range(1, J + 1):
            tp = tp + float(tw_sin[j - 1]) * np.sin(j * t) + float(tw_cos[j - 1]) * np.cos(j * t)
    else:
        tp = t

    x_raw = np.zeros_like(tp)
    y_raw = np.zeros_like(tp)
    for k in range(1, K + 1):
        ck = np.cos(k * tp)
        sk = np.sin(k * tp)
        x_raw += axc[k - 1] * ck + axs[k - 1] * sk
        y_raw += ayc[k - 1] * ck + ays[k - 1] * sk

    cr = math.cos(rot)
    sr = math.sin(rot)

    x = scale * (x_raw * cr - y_raw * sr) + trans[0]
    y = scale * (x_raw * sr + y_raw * cr) + trans[1]

    return np.stack([x, y], axis=1)  # normalized [-1,1]


def parse_color(s: str):
    s = s.strip()
    if s.startswith("#") and len(s) == 7:
        r = int(s[1:3], 16)
        g = int(s[3:5], 16)
        b = int(s[5:7], 16)
        return (r, g, b)
    parts = s.split(",")
    if len(parts) == 3:
        return tuple(int(p) for p in parts)
    raise ValueError("Color must be #RRGGBB or 'r,g,b'")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--params", required=True, help="best_params.json from fit_fourier.py")
    ap.add_argument("--out", required=True, help="Output PNG")
    ap.add_argument("--size", type=int, default=2048, help="Output size (square)")
    ap.add_argument("--points", type=int, default=25000, help="Curve points for rendering")
    ap.add_argument("--supersample", type=int, default=4, help="Render at N× size then downsample")
    ap.add_argument("--width", type=int, default=2, help="Line width (at final resolution)")
    ap.add_argument("--bg", default="#f7f1e8", help="Background color")
    ap.add_argument("--color", default="#3a43c8", help="Line color")
    args = ap.parse_args()

    params = json.loads(Path(args.params).read_text(encoding="utf-8"))

    ss = max(1, int(args.supersample))
    S = int(args.size) * ss

    bg = parse_color(args.bg)
    fg = parse_color(args.color)

    pts = eval_curve(params, n_points=int(args.points))

    # Map [-1,1] -> pixel
    x = (pts[:, 0] + 1.0) * 0.5 * (S - 1)
    y = (pts[:, 1] + 1.0) * 0.5 * (S - 1)

    poly = [(float(xi), float(yi)) for xi, yi in zip(x, y)]

    img = Image.new("RGB", (S, S), bg)
    dr = ImageDraw.Draw(img)
    dr.line(poly, fill=fg, width=max(1, int(args.width) * ss), joint="curve")

    if ss != 1:
        img = img.resize((int(args.size), int(args.size)), resample=Image.Resampling.LANCZOS)

    out_path = Path(args.out)
    img.save(str(out_path))
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
