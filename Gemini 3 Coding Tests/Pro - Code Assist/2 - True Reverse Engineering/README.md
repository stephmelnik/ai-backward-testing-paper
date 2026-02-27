# Flower Lines Reverse Engineering (CUDA)

This project reverse engineers the visual style of "Flower Lines AI Test.jpg" by implementing a high-performance **Strange Attractor** renderer. It uses **PyTorch** and **CUDA** to simulate hundreds of millions of particles in seconds, generating high-resolution density maps that mimic the organic, folded fabric look of the reference image.

## Overview

The core algorithm is based on the **Peter de Jong map**, a system of iterative equations that produces fractal-like structures.

$$
x_{n+1} = \sin(a y_n) - \cos(b x_n)
y_{n+1} = \sin(c x_n) - \cos(d y_n)
$$

The renderer uses a "Log-Density" mapping technique to color the output, preserving details in both the extremely dense core and the faint outer edges.

## Requirements

*   **Python 3.8+**
*   **PyTorch** (with CUDA support)
*   **NumPy**
*   **Pillow (PIL)**

### Hardware
*   **GPU:** NVIDIA RTX series recommended (Code is optimized for CUDA).
*   **RAM:** 16GB+ recommended for high-resolution rendering.

## Installation

1.  Install PyTorch with CUDA support. Visit [pytorch.org](https://pytorch.org/get-started/locally/) for the specific command for your system.
    ```bash
    pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130
    ```
2.  Install dependencies:
    ```bash
    pip install numpy pillow
    ```

## Usage

Run the main script to generate the image:

```bash
python main.py
```

The output will be saved as `re_flower_output.png` in the same directory.

## Configuration (`settings.py`)

*   **`PARAMS`**: Adjust `a`, `b`, `c`, `d` to change the shape of the attractor.
*   **`BATCH_SIZE` / `ITERATIONS`**: Control the quality. Higher numbers reduce noise but increase render time.
*   **`COLOR_*`**: Modify the RGB values to change the color palette.