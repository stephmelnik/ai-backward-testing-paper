# config.py

# --- Output Settings ---
OUTPUT_FILENAME = "flower_recreation.png"
WIDTH = 2000
HEIGHT = 2000
DPI = 300

# --- Mathematical Parameters ---
# The Gumowski-Mira attractor equations depend on mu, a (alpha), and b (sigma).
# These specific values generate the "folded wing" flower shape.
# Try varying MU between -0.2 and -0.9 for different petal folds.
MU = -0.45
ALPHA = 0.008
SIGMA = 0.05

# Initial conditions (starting point of the simulation)
START_X = 0.1
START_Y = 0.1

# Point Count: 
# 10 Million (10_000_000) creates the smooth, high-quality "gossamer" look.
# Lower to 1_000_000 for faster previews.
ITERATIONS = 10_000_000

# --- Rendering / Visuals ---
# How much to zoom in on the attractor
SCALE = 22.0
# Offset to center the flower vertically
OFFSET_Y = 2.0
# Rotation in degrees (90 makes it stand upright)
ROTATION = 90.0

# --- Color Palette ---
# Background: Floral White / Cream
COLOR_BG = (253, 251, 245)  

# Gradient: Deep Indigo (Center) -> Soft Pink (Edges)
COLOR_INNER = (75, 0, 130)    # Indigo/Purple
COLOR_OUTER = (255, 182, 193) # Light Pink

# --- Exposure ---
# GAMMA < 1.0 brightens the faint, thin lines.
GAMMA = 0.6
# EXPOSURE controls the overall "glow" intensity.
EXPOSURE = 1.5