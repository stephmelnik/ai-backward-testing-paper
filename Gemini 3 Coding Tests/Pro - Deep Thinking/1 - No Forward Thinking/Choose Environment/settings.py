"""
Configuration settings for the Gumowski-Mira Flower Generator.
Adjust these values to change the shape, color, and resolution of the output.
"""

# --- Output Settings ---
OUTPUT_FILENAME = "procedural_flower.png"
DPI = 300
FIGURE_SIZE = (12, 12)  # Square canvas (inches)

# --- Mathematical Parameters ---
# The Gumowski-Mira attractor is defined by these constants.
# The specific values below represent the "Sweet Spot" for the floral shape.
# MU controls the "openness" of the petals. Try -0.45 to -0.55 for variations.
A = 0.008
B = 0.05
MU = -0.48

# --- Simulation Settings ---
# The image is formed by a single continuous trajectory.
# 2-5 million points are required to achieve the smooth "smoke" texture.
NUM_POINTS = 3_000_000
INITIAL_X = 0.0
INITIAL_Y = 0.5
DISCARD_STEPS = 5000  # Warmup steps to allow the attractor to settle

# --- Visual Settings ---
BACKGROUND_COLOR = "#FAF9F6"  # Off-White / Cream
LINE_WIDTH = 0.1              # Extremely thin lines are crucial for the texture
LINE_ALPHA = 0.15             # Low opacity allows overlapping lines to glow

# --- Color Gradient ---
# The color transitions from the center of the flower to the tips.
# Format: Hex Strings
COLOR_CENTER = "#483D8B"  # Dark Slate Blue (Spine/Center)
COLOR_MID    = "#9370DB"  # Medium Purple
COLOR_EDGE   = "#FFB6C1"  # Light Pink (Petal Tips)