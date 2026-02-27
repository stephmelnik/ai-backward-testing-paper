"""
A simple class to write SVG files using standard string operations.
"""

class SVGWriter:
    def __init__(self, width, height, background_color=None):
        self.width = width
        self.height = height
        self.elements = []
        self.background_color = background_color

    def add_polyline(self, points, stroke="black", stroke_width=1, opacity=1.0, fill="none"):
        """Adds a polyline to the SVG."""
        if not points:
            return
        
        points_str = " ".join([f"{p[0]:.2f},{p[1]:.2f}" for p in points])
        style = f"fill:{fill};stroke:{stroke};stroke-width:{stroke_width};stroke-opacity:{opacity};stroke-linecap:round;stroke-linejoin:round"
        self.elements.append(f'<polyline points="{points_str}" style="{style}" />')

    def save(self, filepath):
        """Writes the SVG content to a file."""
        with open(filepath, 'w') as f:
            f.write(f'<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
            f.write(f'<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">\n')
            
            if self.background_color:
                f.write(f'<rect width="100%" height="100%" fill="{self.background_color}" />\n')
            
            for el in self.elements:
                f.write(el + "\n")
            
            f.write('</svg>')
        print(f"SVG saved to {filepath}")