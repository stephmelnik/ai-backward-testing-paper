import torch
import torch.nn as nn
import torch.optim as optim
import cv2
import numpy as np
import os
import sys
from tqdm import tqdm

from config import cfg
from symmetry import SymmetryAnalyzer
from model import FractalINR
from dataset import FractalData

def main():
    print("=== Fractal Reverse Engineering System ===")
    
    if not os.path.exists(cfg.INPUT_IMAGE):
        print(f"Error: {cfg.INPUT_IMAGE} not found.")
        return

    # 1. Analyze Symmetry
    analyzer = SymmetryAnalyzer(cfg.INPUT_IMAGE)
    sym_x, sym_y = analyzer.analyze()

    # 2. Load Data (VRAM Resident)
    data = FractalData(cfg.INPUT_IMAGE, cfg.DEVICE, cfg.EDGE_WEIGHT_MULTIPLIER)
    coords, pixels, weights = data.get_training_tensors()
    h, w = data.get_resolution()

    # 3. Initialize Model
    model = FractalINR(cfg, sym_x, sym_y).to(cfg.DEVICE)
    
    # Compile model for RTX 4080 optimization
    if sys.platform != "win32":
        try:
            model = torch.compile(model)
            print("[System] PyTorch JIT Compiler enabled.")
        except Exception as e:
            print(f"[Warning] JIT Compilation failed: {e}")
    else:
        print("[System] Windows detected: Skipping torch.compile (Triton not supported).")

    # 4. Optimizer Setup
    optimizer = optim.Adam(model.parameters(), lr=cfg.LEARNING_RATE)
    # Cosine Annealing ensures we settle into the sharpest possible minimum
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=cfg.EPOCHS, eta_min=1e-6)
    scaler = torch.amp.GradScaler('cuda') # Mixed Precision

    # 5. Training Loop
    print(f"[Training] Starting {cfg.EPOCHS} epochs...")
    model.train()
    
    # We use random sampling from the VRAM tensors
    num_pixels = coords.shape[0]
    pbar = tqdm(range(cfg.EPOCHS), unit="epoch")
    
    for epoch in pbar:
        # Random batch indices
        idx = torch.randint(0, num_pixels, (cfg.BATCH_SIZE,), device=cfg.DEVICE)
        
        batch_coords = coords[idx]
        batch_pixels = pixels[idx]
        batch_weights = weights[idx]
        
        optimizer.zero_grad(set_to_none=True)
        
        with torch.amp.autocast('cuda'):
            pred = model(batch_coords)
            
            # Weighted L1 Loss
            # L1 preserves edges better than MSE. Weights prioritize the fractal boundary.
            diff = torch.abs(pred - batch_pixels)
            loss = torch.mean(diff * batch_weights)
        
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
        scheduler.step()
        
        if epoch % 100 == 0:
            pbar.set_description(f"Loss: {loss.item():.6f}")

    # 6. Save "Equation"
    torch.save(model.state_dict(), cfg.MODEL_WEIGHTS)
    print(f"[Output] Model weights saved to {cfg.MODEL_WEIGHTS}")

    # 7. Render (Reverse Engineered Image)
    print("[Render] Generating high-fidelity output...")
    model.eval()
    
    output_buffer = []
    chunk_size = 500000
    
    # Inference on the full grid
    # (Since data.coords contains the exact grid of the original image)
    with torch.no_grad():
        for i in tqdm(range(0, num_pixels, chunk_size)):
            chunk_coords = coords[i:i+chunk_size]
            with torch.amp.autocast('cuda'):
                chunk_pred = model(chunk_coords)
            chunk_pred = torch.clamp(chunk_pred, 0, 1)
            output_buffer.append(chunk_pred.float()) # Keep as float32
            
    # Reassemble
    full_img = torch.cat(output_buffer, dim=0).view(h, w, 3)
    img_np = (full_img.cpu().numpy() * 255).astype(np.uint8)
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    
    cv2.imwrite(cfg.OUTPUT_IMAGE, img_bgr)
    print(f"[Output] Saved to {cfg.OUTPUT_IMAGE}")

if __name__ == "__main__":
    main()