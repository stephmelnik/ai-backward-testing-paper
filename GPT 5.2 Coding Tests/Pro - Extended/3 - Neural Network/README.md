# Fractal Image Reverse Engineering (INR)

This project "reverse engineers" the provided image by fitting a **continuous**, **differentiable** function
`f(x, y) -> RGB` that reproduces the target as closely as possible.

It uses a GPU-accelerated **implicit neural representation (INR)** (SIREN or Fourier-feature MLP) and
a training loop that samples pixels (vectorized; no per-pixel loops) and optimizes the model with PyTorch.

The output is:
- a trained checkpoint (`.pt`) containing the learned function parameters
- a rendered reconstruction image (PNG)
- metrics (PSNR / SSIM)

## Why this counts as reverse engineering
Instead of copying pixels into the output, the code learns an explicit *function* that generates the image
from coordinates. This is an equation-like representation (a program) and can be rendered at any resolution.

## Setup
Install dependencies (examples):

```bash
pip install torch torchvision pillow numpy tqdm opencv-python scikit-image
```

## Usage

### 1) Train

```bash
python train.py --image "../To Test For AI.jpg" --outdir outputs/run1 --model siren --hidden 512 --layers 8 --steps 200000 --batch 65536 --lr 1e-4 --lr_end 1e-5 --schedule cosine --grad-loss 0.1 --ssim-loss 0.05 --amp
```

Notes:
- Increase `--steps` for higher accuracy.
- Increase `--hidden`, `--layers`, and/or `--batch` if you have VRAM headroom.

### 2) Render full resolution

```bash
python render.py --ckpt outputs/run1/model_best.pt --out outputs/run1/recon_full.png
```

### 3) Evaluate

```bash
python evaluate.py --image "To Test For AI.jpg" --recon outputs/run1/recon_full.png
```

## Tips for maximum accuracy
- Use `--model siren` with a wider/deeper network.
- Train longer (`--steps 300000+`).
- Keep `--lr` small in later stages (`--lr 5e-5` or `1e-5`).
- Render in float32 (default) and save as PNG.

