import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap

class FlowerRenderer:
    def __init__(self, config):
        self.cfg = config

    def render(self, x, y):
        print("Rendering image...")
        
        # Setup Plot
        fig, ax = plt.subplots(figsize=self.cfg.FIGURE_SIZE, dpi=self.cfg.DPI)
        fig.patch.set_facecolor(self.cfg.BACKGROUND_COLOR)
        ax.set_facecolor(self.cfg.BACKGROUND_COLOR)
        
        # --- Prepare Geometry ---
        # Convert points to segments: (x0,y0)->(x1,y1)
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        
        # --- Prepare Colors ---
        # Calculate radius for every point to map to color gradient
        # The flower is centered at (0,0) after transformation
        radii = np.sqrt(x**2 + y**2)
        
        # Normalize radii to 0.0 - 1.0 range
        # We clip outliers to ensure the gradient spans the flower body nicely
        max_r = np.percentile(radii, 98) # Use 98th percentile to ignore stray points
        norm = plt.Normalize(0, max_r)
        
        # Create Gradient Map
        cmap = LinearSegmentedColormap.from_list("flower_gradient", [
            (0.0, self.cfg.COLOR_CENTER),
            (0.5, self.cfg.COLOR_MID),
            (1.0, self.cfg.COLOR_EDGE)
        ])
        
        # Color each segment based on the radius of its starting point
        # (Using midpoint would be slightly more accurate but negligible for this density)
        colors_array = radii[:-1]
        
        # --- Draw Collection ---
        lc = LineCollection(
            segments,
            cmap=cmap,
            norm=norm,
            linewidths=self.cfg.LINE_WIDTH,
            alpha=self.cfg.LINE_ALPHA,
            rasterized=True # Important for saving complex vector files, optional for PNG
        )
        lc.set_array(colors_array)
        ax.add_collection(lc)
        
        # --- Final Polish ---
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Zoom limits
        margin = 1.0
        ax.set_xlim(x.min() - margin, x.max() + margin)
        ax.set_ylim(y.min() - margin, y.max() + margin)
        
        plt.tight_layout(pad=0)
        plt.savefig(self.cfg.OUTPUT_FILENAME, facecolor=self.cfg.BACKGROUND_COLOR)
        print(f"Success! Image saved to {self.cfg.OUTPUT_FILENAME}")
        plt.close()