Fractal Reverse Engineering via Symmetry-Aware SIREN

This project is a high-precision reverse engineering tool designed to reconstruct the mathematical function underlying a raster fractal image.

Unlike traditional vectorization (which traces contours) or auto-encoders (which compress pixels), this system treats the image as a continuous signal. It trains a Symmetry-Aware Sinusoidal Representation Network (SIREN) to learn the implicit equation f(x,y)→(r,g,b) that defines the fractal.
Key Features

    Symmetry-Aware Manifold Folding: The system analyzes the input image using Computer Vision to detect reflectional symmetries (D2​ Dihedral group). If symmetries are found, the coordinate space is mathematically folded (x→∣x∣) before entering the neural network. This guarantees the output is perfectly symmetric and increases effective resolution by 4x.

    Implicit Neural Representation (INR): Uses Sine-activation layers (SIREN) capable of modeling high-frequency details and derivatives, unlike standard ReLU networks which result in blurry reconstructions.

    Edge-Weighted Optimization: Pre-calculates an image gradient map (Sobel) to weigh the loss function. The network focuses 10x more capacity on sharp fractal boundaries than on flat textures.

    Hardware Accelerated: Optimized for RTX 4080 and Ryzen 9 architectures, utilizing TF32 tensor cores, mixed-precision (AMP) training, and massive batch sizes (~262k rays/step).

🛠 Prerequisites

This project is tailored for the following high-performance environment:

    GPU: NVIDIA RTX 4080 (Laptop) - Ampere/Ada Architecture optimized

    CPU: AMD Ryzen 9 7945HX3D

    OS: Windows 11

    Python: 3.14

    CUDA: 13.0

📦 Installation

    Create a Virtual Environment:
    Bash

    python -m venv venv
    .\venv\Scripts\activate

    Install Dependencies: Install PyTorch with CUDA 13.0 support and the required computer vision libraries.
    Bash

    # Install PyTorch for CUDA 13.0
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu130

    # Install Data Processing tools
    pip install numpy opencv-python tqdm

    Prepare Input: Place the target image in the root directory and ensure it is named: To Test For AI.jpg

🚀 Usage

To start the reverse engineering process:
Bash

python run.py

Execution Pipeline

    CV Analysis: The system reads the image and calculates Mean Squared Error (MSE) across axes to determine if the fractal is mirrored.

    JIT Compilation: The model is compiled using torch.compile to optimize kernel fusion for the specific GPU architecture.

    Training: The model trains for 5,000 epochs.

        Note: You will see the Loss value decrease. A loss below 0.005 usually indicates an extremely high-fidelity reconstruction.

    Rendering: The code generates a new image, reverse_engineered_fractal.png, by querying the learned mathematical function at every pixel coordinate.

📂 Project Structure

    config.py: Central configuration for hardware triggers (TF32, CuDNN), hyperparameters (Learning Rate, Omega_0), and file paths.

    symmetry.py: Computer Vision module. Detects structural rules (Left/Right or Top/Bottom reflections) to constrain the search space.

    model.py: Defines the FractalINR class. This is the "equation" being learned. It implements the coordinate folding and Sine-activated dense layers.

    dataset.py: Manages VRAM-resident tensors. Computes the gradient importance map so the AI knows which pixels are "difficult" (edges) vs "easy" (background).

    run.py: The main entry point. Orchestrates the training loop, gradient scaling, and final rendering.

🧠 Methodology Details
Coordinate Folding

If the image is detected as symmetric, the network does not learn the whole image. Instead, it learns the Fundamental Domain.
f(x,y)=NeuralNet(∣x∣,∣y∣)

This effectively "hard codes" the symmetry, ensuring that even if the network makes a small error, that error is perfectly mirrored, preserving the fractal aesthetic.
Loss Function

We use a weighted L1 loss to prioritize high-frequency details:
L=mean(∣I^−I∣⋅(1+λ⋅∣∣∇I∣∣))

Where ∣∣∇I∣∣ is the magnitude of the image gradient (edge detection). This forces the AI to "care" more about the intricate fractal boundaries than the dark background.
⚠️ Troubleshooting

    Out of Memory (OOM): If you run out of VRAM, open config.py and reduce BATCH_SIZE from 2**18 to 2**16.

    Blurry Output: Increase EPOCHS in config.py or increase the EDGE_WEIGHT_MULTIPLIER.

    JIT Errors: If torch.compile fails (due to Windows/Compiler compatibility), the code will print a warning and continue with standard eager execution.