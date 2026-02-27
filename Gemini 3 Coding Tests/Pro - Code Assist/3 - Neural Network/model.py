import torch
import torch.nn as nn
import numpy as np

class SineLayer(nn.Module):
    """
    Linear layer with Sine activation (SIREN).
    Capable of modeling complex signals and their derivatives.
    """
    def __init__(self, in_features, out_features, bias=True, is_first=False, omega_0=30):
        super().__init__()
        self.omega_0 = omega_0
        self.is_first = is_first
        self.in_features = in_features
        self.linear = nn.Linear(in_features, out_features, bias=bias)
        self.init_weights()

    def init_weights(self):
        with torch.no_grad():
            if self.is_first:
                self.linear.weight.uniform_(-1 / self.in_features, 
                                             1 / self.in_features)
            else:
                # Initialization scheme from Sitzmann et al.
                limit = np.sqrt(6 / self.in_features) / self.omega_0
                self.linear.weight.uniform_(-limit, limit)

    def forward(self, input):
        return torch.sin(self.omega_0 * self.linear(input))

class FractalINR(nn.Module):
    """
    Implicit Neural Representation of the image.
    Maps coordinates (x, y) -> Color (r, g, b).
    """
    def __init__(self, cfg, sym_x, sym_y):
        super().__init__()
        self.sym_x = sym_x
        self.sym_y = sym_y
        
        layers = []
        # Input Layer
        layers.append(SineLayer(2, cfg.HIDDEN_FEATURES, is_first=True, omega_0=cfg.OMEGA_0))
        
        # Hidden Layers
        for _ in range(cfg.HIDDEN_LAYERS):
            layers.append(SineLayer(cfg.HIDDEN_FEATURES, cfg.HIDDEN_FEATURES, 
                                    is_first=False, omega_0=cfg.OMEGA_0))
        
        self.net = nn.Sequential(*layers)
        
        # Output Layer (Linear)
        self.final_linear = nn.Linear(cfg.HIDDEN_FEATURES, 3)
        
        # Initialize output close to 0
        with torch.no_grad():
            limit = np.sqrt(6 / cfg.HIDDEN_FEATURES) / 30
            self.final_linear.weight.uniform_(-limit, limit)

    def forward(self, coords):
        # --- Symmetry Enforcement ---
        # If the image was detected to be symmetric, we fold the coordinates.
        # This constrains the solution space to valid symmetric fractals only.
        x = coords[:, 0:1]
        y = coords[:, 1:2]
        
        if self.sym_x:
            x = torch.abs(x) # Fold Left-Right
        if self.sym_y:
            y = torch.abs(y) # Fold Top-Bottom
            
        folded_coords = torch.cat([x, y], dim=1)
        
        feat = self.net(folded_coords)
        return self.final_linear(feat)