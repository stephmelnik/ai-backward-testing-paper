import cv2
import numpy as np

class SymmetryAnalyzer:
    """
    Analyzes an image to detect reflectional symmetries (D2 Group).
    Returns structural priors to constrain the neural network.
    """
    def __init__(self, image_path):
        self.img = cv2.imread(image_path)
        if self.img is None:
            raise FileNotFoundError(f"Image {image_path} not found.")
        self.gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        self.h, self.w = self.gray.shape

    def analyze(self):
        print("[Analysis] Reverse engineering image structure...")
        
        # 1. Analyze Vertical Axis (Left-Right Symmetry)
        cx = self.w // 2
        left = self.gray[:, :cx]
        right = self.gray[:, self.w-cx:]
        right_flipped = cv2.flip(right, 1)
        
        # Crop to intersection
        w_min = min(left.shape[1], right_flipped.shape[1])
        mse_x = np.mean((left[:, :w_min] - right_flipped[:, :w_min]) ** 2)
        
        # 2. Analyze Horizontal Axis (Top-Bottom Symmetry)
        cy = self.h // 2
        top = self.gray[:cy, :]
        bottom = self.gray[self.h-cy:, :]
        bottom_flipped = cv2.flip(bottom, 0)
        
        h_min = min(top.shape[0], bottom_flipped.shape[0])
        mse_y = np.mean((top[:h_min, :] - bottom_flipped[:h_min, :]) ** 2)
        
        # Threshold: Fractals are perfect, but raster images have compression noise.
        # MSE < 150 (on 0-255 scale) usually indicates strong structural symmetry.
        is_sym_x = mse_x < 150.0
        is_sym_y = mse_y < 150.0
        
        print(f"  > Vertical Axis MSE: {mse_x:.2f} -> Symmetric: {is_sym_x}")
        print(f"  > Horizontal Axis MSE: {mse_y:.2f} -> Symmetric: {is_sym_y}")
        
        return is_sym_x, is_sym_y