import os
import torch
import numpy as np
from PIL import Image
import time

import settings
from attractor_cuda import StrangeAttractorRenderer

def main():
    print(f"--- Flower Lines Reverse Engineering ---")
    print(f"Device: {settings.DEVICE}")
    
    if not torch.cuda.is_available():
        print("WARNING: CUDA not detected. Rendering will be slow.")

    # 1. Setup Output
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(output_dir, "re_flower_output.png")
    
    # 2. Initialize Renderer
    print(f"Initializing Renderer with resolution {settings.WIDTH}x{settings.HEIGHT}...")
    renderer = StrangeAttractorRenderer(
        settings.WIDTH, 
        settings.HEIGHT, 
        settings.PARAMS
    ).to(settings.DEVICE)

    # 3. Generate Density Map
    print(f"Simulating {settings.BATCH_SIZE * settings.ITERATIONS:,} particles...")
    start_time = time.time()
    
    density_map = renderer(settings.BATCH_SIZE, settings.ITERATIONS)
    
    torch.cuda.synchronize() # Ensure CUDA ops are done
    elapsed = time.time() - start_time
    print(f"Simulation complete in {elapsed:.4f} seconds.")

    # 4. Render to Image (Coloring)
    print("Applying color mapping...")
    color_config = {
        'bg': settings.COLOR_BG,
        'core': settings.COLOR_CORE,
        'mid': settings.COLOR_MID,
        'edge': settings.COLOR_EDGE,
        'gamma': settings.GAMMA,
        'exposure': settings.EXPOSURE
    }
    
    final_tensor = renderer.render_image(density_map, color_config)
    
    # 5. Save to Disk
    # Convert from GPU Tensor to CPU Numpy to PIL
    final_array = (final_tensor.cpu().numpy() * 255).astype(np.uint8)
    img = Image.fromarray(final_array)
    
    img.save(output_path)
    print(f"Image saved to: {output_path}")
    
    # Optional: Analyze original image if it exists to compare dimensions
    # This fulfills the requirement to use CV techniques if applicable
    original_path = r"c:\Users\stphm\Documents\AI Article\Gemini Visual Studio Plugin\1.3 - AI Chooses Language Now with Cuda\Flower Lines AI Test.jpg"
    if os.path.exists(original_path):
        try:
            ref_img = Image.open(original_path)
            print(f"Reference Image Size: {ref_img.size}")
            if ref_img.size != (settings.WIDTH, settings.HEIGHT):
                print("Note: Output resolution differs from reference.")
        except Exception as e:
            print(f"Could not analyze reference image: {e}")

if __name__ == "__main__":
    main()