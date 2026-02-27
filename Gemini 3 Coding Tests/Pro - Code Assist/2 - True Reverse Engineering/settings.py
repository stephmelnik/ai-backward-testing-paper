"""
Configuration settings for the Flower Lines Reverse Engineering project.
"""
import torch

# --- Hardware Settings ---
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# --- Rendering Settings ---
# High resolution to match the detail of the input image
WIDTH = 2048
HEIGHT = 2048
# Number of particles to simulate in parallel
BATCH_SIZE = 10_000_000
# Number of iterations per particle (Total points = BATCH_SIZE * ITERATIONS)
ITERATIONS = 50
# Exposure/Gamma for the log-density mapping
GAMMA = 2.2
EXPOSURE = 0.002

# --- Mathematical Model Parameters (Peter de Jong Attractor) ---
# These parameters are tuned to produce a symmetric, folded "flower" shape.
PARAMS = {
    "a": 0.970,
    "b": -1.899,
    "c": 1.381,
    "d": -1.506
}

# --- Color Palette ---
# Colors extracted visually from "Flower Lines AI Test.jpg"
# Format: (R, G, B) in 0-1 range
COLOR_BG = (0.98, 0.97, 0.95)      # Off-white/Cream background
COLOR_CORE = (0.29, 0.24, 0.56)    # Deep Blue/Purple (Center/Dense)
COLOR_MID = (0.5, 0.4, 0.7)        # Lighter Purple
COLOR_EDGE = (0.9, 0.6, 0.6)       # Pink/Salmon (Outer edges)