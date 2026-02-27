import torch
import cv2
import numpy as np

class FractalData:
    def __init__(self, image_path, device, edge_weight_mult):
        print(f"[Data] Loading {image_path}...")
        
        # Load Image
        img_bgr = cv2.imread(image_path)
        self.h, self.w, _ = img_bgr.shape
        
        # 1. Calculate Importance Map (Edge Detection)
        # We calculate gradients to tell the network where accuracy matters most.
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_mag = np.sqrt(sobelx**2 + sobely**2)
        
        # Normalize gradients [0, 1]
        gradient_mag = (gradient_mag - gradient_mag.min()) / (gradient_mag.max() - gradient_mag.min() + 1e-8)
        
        # Create weight map: 1.0 for flat areas, high value for edges
        weights = 1.0 + (gradient_mag * edge_weight_mult)
        
        # 2. Prepare Tensors
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        pixels = torch.tensor(img_rgb, dtype=torch.float32, device=device) / 255.0
        weights = torch.tensor(weights, dtype=torch.float32, device=device).unsqueeze(-1) # (H,W,1)
        
        # 3. Generate Coordinates [-1, 1]
        # indexing='ij' -> y varies dim 0, x varies dim 1
        y_coords = torch.linspace(-1, 1, self.h, device=device)
        x_coords = torch.linspace(-1, 1, self.w, device=device)
        grid_y, grid_x = torch.meshgrid(y_coords, x_coords, indexing='ij')
        coords = torch.stack([grid_x, grid_y], dim=-1)
        
        # Flatten for training
        self.coords = coords.reshape(-1, 2)       # [N, 2]
        self.pixels = pixels.reshape(-1, 3)       # [N, 3]
        self.weights = weights.reshape(-1, 1)     # [N, 1]
        
        print(f"[Data] Prepared {self.coords.shape[0]} pixels. VRAM Loaded.")

    def get_training_tensors(self):
        return self.coords, self.pixels, self.weights

    def get_resolution(self):
        return self.h, self.w