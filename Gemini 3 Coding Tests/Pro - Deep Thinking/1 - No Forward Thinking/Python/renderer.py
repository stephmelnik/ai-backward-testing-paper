# renderer.py
import numpy as np
import math
from PIL import Image

def render_density_map(x, y, config):
    width = config.WIDTH
    height = config.HEIGHT
    
    print("Transforming coordinates...")
    
    # 1. Rotation
    theta = math.radians(config.ROTATION)
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    
    # Apply rotation matrix
    x_rot = x * cos_t - y * sin_t
    y_rot = x * sin_t + y * cos_t
    
    # 2. Scaling and Mapping to Pixels
    # Center the coordinates
    cx = width / 2
    cy = height / 2
    
    # Scale factor (adjusted for aspect ratio)
    scale_factor = config.SCALE * (min(width, height) / 100.0)
    
    # Map to screen space
    u = cx + x_rot * scale_factor
    v = cy - (y_rot + config.OFFSET_Y) * scale_factor
    
    # 3. Accumulate Density (Histogram)
    print("Accumulating density grid...")
    
    # Convert to integer indices
    u_idx = u.astype(np.int32)
    v_idx = v.astype(np.int32)
    
    # Filter valid points
    mask = (u_idx >= 0) & (u_idx < width) & (v_idx >= 0) & (v_idx < height)
    valid_u = u_idx[mask]
    valid_v = v_idx[mask]
    
    # Create buffers
    # density: how many points hit this pixel?
    # distance: sum of distances from center (for coloring)
    density = np.zeros((height, width), dtype=np.float32)
    distance_accum = np.zeros((height, width), dtype=np.float32)
    
    # Calculate distance from center for gradient coloring
    # We use the original (rotated) coordinates to determine 'radius'
    dists = np.sqrt(x_rot**2 + y_rot**2)
    valid_dists = dists[mask]
    
    # Fast accumulation
    np.add.at(density, (valid_v, valid_u), 1.0)
    np.add.at(distance_accum, (valid_v, valid_u), valid_dists)
    
    # 4. Coloring and Post-Processing
    print("Rendering final image...")
    
    # Logarithmic Tone Mapping
    # Creates the "glow" by compressing dynamic range
    log_density = np.log1p(density * config.EXPOSURE)
    max_val = np.max(log_density)
    norm_density = log_density / max_val if max_val > 0 else log_density
    
    # Gamma Correction (makes faint lines visible)
    norm_density = np.power(norm_density, config.GAMMA)
    
    # Average distance map (for gradient)
    with np.errstate(divide='ignore', invalid='ignore'):
        avg_dist = distance_accum / density
        avg_dist[~np.isfinite(avg_dist)] = 0
    
    # Create Color Gradient Map
    # Normalize distance. 
    # 15.0 is an empirical max radius for these parameters/scale
    t_map = np.clip(avg_dist / 15.0, 0.0, 1.0)
    
    # Prepare colors
    c_bg = np.array(config.COLOR_BG)
    c_in = np.array(config.COLOR_INNER)
    c_out = np.array(config.COLOR_OUTER)
    
    # Expand dims for broadcasting
    t_map = t_map[:, :, np.newaxis]       # (H, W, 1)
    alpha = norm_density[:, :, np.newaxis] # (H, W, 1)
    
    # Interpolate Line Color: Inner -> Outer
    line_rgb = (1.0 - t_map) * c_in + t_map * c_out
    
    # Composite: Background -> Line
    final_rgb = (1.0 - alpha) * c_bg + alpha * line_rgb
    
    # Cast to bytes
    final_img = np.clip(final_rgb, 0, 255).astype(np.uint8)
    
    return Image.fromarray(final_img)