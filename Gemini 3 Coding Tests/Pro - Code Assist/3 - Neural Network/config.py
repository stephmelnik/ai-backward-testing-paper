import torch

class Config:
    # --- Hardware Optimization ---
    # Optimized for RTX 4080 (Ampere/Ada) and CUDA 13.0 context
    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Enable TF32 for high-performance matrix multiplications on RTX 40-series
    # This trades negligible precision for significant speedups
    MATMUL_PRECISION = 'high' 
    
    # --- Input/Output ---
    INPUT_IMAGE = "To Test For AI.jpg"
    OUTPUT_IMAGE = "reverse_engineered_fractal.png"
    MODEL_WEIGHTS = "fractal_function.pth"
    
    # --- Training Configuration ---
    # We use a massive batch size to saturate the RTX 4080's VRAM/Cores
    BATCH_SIZE = 2**18      # ~262k rays per batch
    EPOCHS = 5000           # High epoch count for convergence
    LEARNING_RATE = 5e-5    # Low learning rate for fine detail
    
    # --- Model Architecture (SIREN) ---
    # Deep and wide network to capture infinite resolution details
    HIDDEN_LAYERS = 5
    HIDDEN_FEATURES = 1024
    OMEGA_0 = 30.0          # Base frequency for sine activation
    
    # --- Advanced Accuracy Features ---
    # Weight edges this much higher than flat areas during training
    EDGE_WEIGHT_MULTIPLIER = 10.0 

cfg = Config()

# Apply hardware settings
if torch.cuda.is_available():
    torch.set_float32_matmul_precision(cfg.MATMUL_PRECISION)
    torch.backends.cudnn.benchmark = True