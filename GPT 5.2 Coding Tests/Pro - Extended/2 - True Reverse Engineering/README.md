# Minimal GPU Fourier Reverse Engineering

This is a **minimal**, **generic** reverse-engineering codebase for thin-line drawings.

It fits a **closed parametric curve** represented as a **Fourier series** (generic representation; *no named curve families like hypotrochoids, epitrochoids, harmonographs, etc.*).

The fitter uses:
- a **precomputed distance transform** (DT) of target edges (fast curve→target scoring)
- a **coverage term** based on distances from target edge points → nearest curve point (prevents partial matches)
- multi-start + multi-stage optimization on **GPU (CUDA)** via PyTorch

## 0) Install

Create a venv, install dependencies:

```bat
py -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

Install a CUDA-enabled PyTorch build (example for CUDA 12.4):

```bat
pip install torch --index-url https://download.pytorch.org/whl/cu124
```

Verify CUDA:

```bat
python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
```

## 1) Preprocess target

This creates an edge mask and a distance transform cache.

```bat
python preprocess_target.py --target "Flower Lines AI Test.jpg" --cache target_cache.npz --res 768
```

Options:
- `--ink-mode chroma` (default): good for colored ink on neutral paper
- `--ink-mode gray`: use grayscale edges

## 2) Fit Fourier curve (GPU)

```bat
python fit_fourier.py --cache target_cache.npz --out best_params.json --device cuda --starts 16 --stages 2
```

If you run out of VRAM, reduce starts or the coverage point count:

```bat
python fit_fourier.py --cache target_cache.npz --out best_params.json --device cuda \
  --starts 8 --cov 768
```

## 3) Render

```bat
python render_fourier.py --params best_params.json --out recon.png --size 2048
```

## Performance tips (Windows 11)

- Use **Task Manager → GPU → change graph** to **CUDA / Compute_0** (not just 3D).
- Plug in power, set Windows **Power mode: Best performance**.
- Settings → System → Display → Graphics → add your `python.exe` → **High performance (NVIDIA)**.

## Notes

- This solver is **generic** but assumes the target is primarily a **thin line drawing**. It is not intended for natural photos.
- It is designed to be **minimal**: 3 scripts + small modules.
- You can increase accuracy by increasing:
  - `--K` (Fourier harmonics)
  - `--curve-points`
  - `--steps`
  - `--starts`

