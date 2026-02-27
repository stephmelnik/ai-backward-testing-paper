# chaos.py
import numpy as np
try:
    from numba import jit
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False
    print("Warning: 'numba' not found. Generation will be significantly slower.")

def get_gumowski_mira_functions():
    """
    Returns the compiled generation function.
    """
    
    # We define the core logic inside a closure or simply return the JIT-compiled version
    # depending on availability.
    
    if HAS_NUMBA:
        @jit(nopython=True)
        def run_simulation(n, mu, alpha, sigma, x0, y0):
            x = np.zeros(n, dtype=np.float64)
            y = np.zeros(n, dtype=np.float64)
            
            curr_x = x0
            curr_y = y0
            
            # Pre-calculate constant term for G(x)
            # G(x) = mu*x + 2*(1-mu)*x^2 / (1+x^2)
            c1 = 2.0 * (1.0 - mu)
            
            for i in range(n):
                # Calculate G(x_n)
                x2 = curr_x * curr_x
                gx = mu * curr_x + (c1 * x2) / (1.0 + x2)
                
                # Calculate x_{n+1}
                # Formula: x_{n+1} = y_n + alpha * y_n * (1 - sigma * y_n^2) + G(x_n)
                y2 = curr_y * curr_y
                next_x = curr_y + alpha * curr_y * (1.0 - sigma * y2) + gx
                
                # Calculate G(x_{n+1})
                nx2 = next_x * next_x
                gx_next = mu * next_x + (c1 * nx2) / (1.0 + nx2)
                
                # Calculate y_{n+1}
                # Formula: y_{n+1} = -x_n + G(x_{n+1})
                next_y = -curr_x + gx_next
                
                # Store
                x[i] = next_x
                y[i] = next_y
                
                # Update
                curr_x = next_x
                curr_y = next_y
                
            return x, y
        return run_simulation
    
    else:
        # Pure Python fallback (slow)
        def run_simulation(n, mu, alpha, sigma, x0, y0):
            x = np.zeros(n, dtype=np.float64)
            y = np.zeros(n, dtype=np.float64)
            curr_x, curr_y = x0, y0
            c1 = 2.0 * (1.0 - mu)
            
            print("  (Using pure Python fallback - this may take a while...)")
            for i in range(n):
                x2 = curr_x * curr_x
                gx = mu * curr_x + (c1 * x2) / (1.0 + x2)
                
                y2 = curr_y * curr_y
                next_x = curr_y + alpha * curr_y * (1.0 - sigma * y2) + gx
                
                nx2 = next_x * next_x
                gx_next = mu * next_x + (c1 * nx2) / (1.0 + nx2)
                
                next_y = -curr_x + gx_next
                
                x[i] = next_x
                y[i] = next_y
                curr_x, curr_y = next_x, next_y
            return x, y
        return run_simulation

def generate_points(config):
    """
    Orchestrates the simulation and ensures symmetry.
    """
    sim_func = get_gumowski_mira_functions()
    
    print(f"Generating {config.ITERATIONS} points...")
    x, y = sim_func(config.ITERATIONS, config.MU, config.ALPHA, config.SIGMA, config.START_X, config.START_Y)
    
    # The reference image is perfectly symmetrical.
    # While the attractor is naturally symmetric, mirroring ensures perfection
    # and fills in both sides equally.
    x_full = np.concatenate([x, -x])
    y_full = np.concatenate([y, y])
    
    return x_full, y_full