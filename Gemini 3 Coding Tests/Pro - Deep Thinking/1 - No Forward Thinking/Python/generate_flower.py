# generate_flower.py
import time
import config
import chaos
import renderer

def main():
    print("--- Gumowski-Mira Flower Generator ---")
    start_time = time.time()
    
    # 1. Generate Trajectory
    x, y = chaos.generate_points(config)
    
    # 2. Render Image
    img = renderer.render_density_map(x, y, config)
    
    # 3. Save
    img.save(config.OUTPUT_FILENAME, dpi=(config.DPI, config.DPI))
    
    elapsed = time.time() - start_time
    print(f"Done! Saved to '{config.OUTPUT_FILENAME}'")
    print(f"Total time: {elapsed:.2f} seconds")

if __name__ == "__main__":
    main()