import numpy as np
from numba import jit

class GumowskiMiraSystem:
    """
    Implements the Gumowski-Mira strange attractor.
    
    The system is defined by the iterative equations:
    x_{n+1} = y_n + a(1 - b*y_n^2)y_n + g(x_n)
    y_{n+1} = -x_n + g(x_{n+1})
    
    where g(x) = mu*x + (2(1-mu)x^2) / (1+x^2)
    """
    
    def __init__(self, a, b, mu):
        self.a = a
        self.b = b
        self.mu = mu

    def generate(self, n_points, x0, y0, discard=0):
        """
        Generates the trajectory of the attractor.
        Returns tuple (x_array, y_array).
        """
        print(f"Generating {n_points} points (Accurate Mode)...")
        
        # We use a static helper function for performance (JIT compilation recommended if available)
        # Here we use standard numpy which is fast enough for ~3M points.
        x, y = self._simulation_loop(n_points + discard, x0, y0, self.a, self.b, self.mu)
        
        # Discard warmup points
        return x[discard:], y[discard:]

    @staticmethod
    def _simulation_loop(total_steps, x0, y0, a, b, mu):
        """
        Core integration loop.
        """
        x = np.zeros(total_steps)
        y = np.zeros(total_steps)
        
        x[0], y[0] = x0, y0
        
        curr_x = x0
        curr_y = y0
        
        for i in range(total_steps - 1):
            # Calculate g(x_n)
            gx = mu * curr_x + (2 * (1 - mu) * curr_x**2) / (1 + curr_x**2)
            
            # Calculate x_{n+1}
            next_x = curr_y + a * curr_y * (1 - b * curr_y**2) + gx
            
            # Calculate g(x_{n+1})
            gx_next = mu * next_x + (2 * (1 - mu) * next_x**2) / (1 + next_x**2)
            
            # Calculate y_{n+1}
            next_y = -curr_x + gx_next
            
            x[i+1] = next_x
            y[i+1] = next_y
            
            curr_x = next_x
            curr_y = next_y
            
        return x, y

    def transform_for_flower_shape(self, x, y):
        """
        Post-processes the raw chaotic data to match the flower orientation.
        1. Rotates the shape (the raw math generates it diagonally).
        2. Mirrors it to ensure perfect bilateral symmetry matching the reference.
        """
        # 1. Rotation (-45 degrees aligns the "wings" upright)
        theta = np.radians(-45)
        c, s = np.cos(theta), np.sin(theta)
        x_rot = x * c - y * s
        y_rot = x * s + y * c
        
        # 2. Symmetrization (Mirroring)
        # The reference image is perfectly symmetric. We take the right half
        # and mirror it to the left to guarantee this look.
        
        # Filter for right side (assuming centered on 0)
        # We allow a small overlap to prevent a gap in the center spine
        mask = x_rot >= -0.1 
        x_right = x_rot[mask]
        y_right = y_rot[mask]
        
        # Create mirrored copy
        x_final = np.concatenate([x_right, -x_right])
        y_final = np.concatenate([y_right, y_right])
        
        return x_final, y_final