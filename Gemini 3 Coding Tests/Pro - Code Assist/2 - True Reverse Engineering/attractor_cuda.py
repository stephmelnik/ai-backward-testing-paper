"""
Core rendering logic for Strange Attractors using PyTorch and CUDA.
"""
import torch
import torch.nn as nn
import numpy as np
from settings import DEVICE

class StrangeAttractorRenderer(nn.Module):
    def __init__(self, width, height, params):
        super().__init__()
        self.width = width
        self.height = height
        self.params = params
        
        # Register parameters as buffers
        self.a = params['a']
        self.b = params['b']
        self.c = params['c']
        self.d = params['d']

    def forward(self, batch_size, iterations):
        """
        Generates the attractor points and aggregates them into a density map.
        """
        # Initialize random points in range [-2, 2]
        x = (torch.rand(batch_size, device=DEVICE) * 4.0) - 2.0
        y = (torch.rand(batch_size, device=DEVICE) * 4.0) - 2.0
        
        # The density map (histogram)
        density = torch.zeros(self.height * self.width, device=DEVICE, dtype=torch.float32)
        
        # Coordinate scaling to fit image
        scale_factor = self.width / 5.0 
        center_x = self.width / 2.0
        center_y = self.height / 2.0

        # Warmup iterations to settle particles onto the attractor
        with torch.no_grad():
            for _ in range(20):
                xn = torch.sin(self.a * y) - torch.cos(self.b * x)
                yn = torch.sin(self.c * x) - torch.cos(self.d * y)
                x, y = xn, yn

            # Recording iterations
            for _ in range(iterations):
                xn = torch.sin(self.a * y) - torch.cos(self.b * x)
                yn = torch.sin(self.c * x) - torch.cos(self.d * y)
                x, y = xn, yn
                
                # Map to screen coordinates
                ix = (x * scale_factor + center_x).long()
                iy = (y * scale_factor + center_y).long()
                
                # Filter points strictly inside bounds
                mask = (ix >= 0) & (ix < self.width) & (iy >= 0) & (iy < self.height)
                
                if mask.any():
                    valid_indices = (iy[mask] * self.width + ix[mask])
                    counts = torch.bincount(valid_indices, minlength=self.width * self.height).float()
                    density += counts

        return density.reshape(self.height, self.width)

    def render_image(self, density, color_cfg):
        """
        Converts the raw density map into a colored image using log-density mapping.
        """
        density_log = torch.log1p(density * color_cfg['exposure'])
        d_max = density_log.max()
        density_norm = density_log / d_max if d_max > 0 else density_log
        density_norm = torch.pow(density_norm, 1.0 / color_cfg['gamma'])
        
        output = torch.zeros((self.height, self.width, 3), device=DEVICE)
        bg = torch.tensor(color_cfg['bg'], device=DEVICE)
        core = torch.tensor(color_cfg['core'], device=DEVICE)
        edge = torch.tensor(color_cfg['edge'], device=DEVICE)
        
        d_expanded = density_norm.unsqueeze(-1)
        structure_alpha = torch.clamp(d_expanded * 2.5, 0, 1)
        structure_color = edge + (core - edge) * d_expanded
        
        final_image = structure_color * structure_alpha + bg * (1 - structure_alpha)
        return torch.clamp(final_image, 0, 1)