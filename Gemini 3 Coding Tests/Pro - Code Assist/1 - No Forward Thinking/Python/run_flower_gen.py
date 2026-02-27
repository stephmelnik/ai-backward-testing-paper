"""
Entry point to generate the flower image.
"""
import os
import sys

# Ensure the script directory is in the python path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

import flower_logic

def main():
    # Define output path
    output_file = os.path.join(script_dir, "flower_output.svg")
    
    print(f"Generating procedural flower to {output_file}...")
    flower_logic.generate_flower(output_file)
    print("Done.")

if __name__ == "__main__":
    main()