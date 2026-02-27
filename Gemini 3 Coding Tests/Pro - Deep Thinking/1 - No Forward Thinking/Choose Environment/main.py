import settings
from attractor import GumowskiMiraSystem
from visualizer import FlowerRenderer

def main():
    print("--- Procedural Flower Generator ---")
    
    # 1. Initialize Math Engine
    system = GumowskiMiraSystem(settings.A, settings.B, settings.MU)
    
    # 2. Generate Chaotic Trajectory
    raw_x, raw_y = system.generate(
        settings.NUM_POINTS, 
        settings.INITIAL_X, 
        settings.INITIAL_Y, 
        settings.DISCARD_STEPS
    )
    
    # 3. Transform Geometry (Rotate & Mirror)
    # This step aligns the math output with the visual orientation of the reference
    final_x, final_y = system.transform_for_flower_shape(raw_x, raw_y)
    
    # 4. Render and Save
    renderer = FlowerRenderer(settings)
    renderer.render(final_x, final_y)

if __name__ == "__main__":
    main()