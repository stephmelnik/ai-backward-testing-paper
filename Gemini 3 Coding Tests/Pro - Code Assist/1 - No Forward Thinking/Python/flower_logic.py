"""
Core procedural generation logic for the flower pattern.
"""
import math
import random
import vector_math as vm
from svg_writer import SVGWriter

def get_color_gradient(dist_from_center, max_dist):
    """
    Generates a color based on distance from the flower center.
    Center = Blue/Purple, Edges = Pink/Salmon.
    """
    # Normalize distance
    ratio = min(1.0, max(0.0, dist_from_center / max_dist))
    
    # Color Palette (RGB 0-255)
    # Deep Blue/Purple (Center)
    c1 = (80, 80, 200) 
    # Soft Pink/Salmon (Tips)
    c2 = (255, 180, 180)
    
    # Interpolate
    r = int(c1[0] + (c2[0] - c1[0]) * ratio)
    g = int(c1[1] + (c2[1] - c1[1]) * ratio)
    b = int(c1[2] + (c2[2] - c1[2]) * ratio)
    
    return f"rgb({r},{g},{b})"

def generate_petal_veins(svg, p0, p1, p2, width_max, num_lines=40, chirality=1):
    """
    Generates a set of spiraling veins for a single petal defined by a Bezier spine (p0, p1, p2).
    """
    center_ref = p0 # The base of the flower
    max_flower_radius = 450.0 
    
    for i in range(num_lines):
        points = []
        
        # Randomized parameters for each line to create organic variation
        phase = random.uniform(0, 2 * math.pi)
        
        # Frequency of the spiral (loops per petal length)
        freq = 15.0 + random.uniform(-2.0, 2.0)
        
        # Amplitude jitter
        amp_scale = random.uniform(0.9, 1.1)
        
        # Steps along the curve
        steps = 100
        for s in range(steps + 1):
            t = s / steps
            
            # 1. Get position on the central spine
            pos = vm.quadratic_bezier(p0, p1, p2, t)
            
            # 2. Get local coordinate frame (Tangent and Normal)
            tangent = vm.normalize(vm.quadratic_bezier_derivative(p0, p1, p2, t))
            normal = vm.rotate_90(tangent)
            
            # 3. Calculate Envelope (Width profile)
            # Shape: Starts thin, gets wide, tapers at tip.
            envelope = width_max * math.sin(t * math.pi) * amp_scale
            
            # Taper the base more aggressively
            if t < 0.2:
                envelope *= (t / 0.2)
            
            # 4. Calculate Spiral Offset
            angle = (freq * t * 2 * math.pi) + phase
            
            # Normal component (Side to side)
            offset_n = math.cos(angle) 
            
            # Tangent component (Forward/Backward loop effect)
            offset_t = math.sin(angle) * 0.4 * chirality
            
            # Combine
            displacement = vm.add(
                vm.mul(normal, offset_n * envelope),
                vm.mul(tangent, offset_t * envelope)
            )
            
            final_pos = vm.add(pos, displacement)
            points.append(final_pos)
        
        # Determine color based on the midpoint of the line
        mid_idx = len(points) // 2
        dist = vm.distance(points[mid_idx], center_ref)
        color = get_color_gradient(dist, max_flower_radius)
        
        # Draw the line
        svg.add_polyline(points, stroke=color, stroke_width=0.6, opacity=0.6)

def generate_flower(filepath):
    """Main function to compose the flower."""
    width, height = 1000, 1000
    center_x, center_y = width / 2, height * 0.85
    
    # Cream/Off-white background
    svg = SVGWriter(width, height, background_color="#FDFBF7")
    
    base_pt = (center_x, center_y)
    
    # Configuration for petals: [Control_Offset, End_Offset, Width]
    # Offsets are relative to base_pt
    petals = [
        # Layer 1: Large Lower Side Lobes
        { "control": (-200, -100), "end": (-350, -150), "width": 140, "mirror": True },
        # Layer 2: Large Upper Side Lobes
        { "control": (-150, -400), "end": (-280, -550), "width": 160, "mirror": True },
        # Layer 3: Central Top Lobe
        { "control": (0, -400), "end": (0, -750), "width": 180, "mirror": False },
        # Layer 4: Inner/Middle Lobes (Filling the gaps)
        { "control": (-80, -300), "end": (-120, -500), "width": 100, "mirror": True },
        # Layer 5: Bottom Center (Inverted/Small)
        { "control": (0, 50), "end": (0, 120), "width": 80, "mirror": False }
    ]
    
    for p_config in petals:
        c_off = p_config["control"]
        e_off = p_config["end"]
        w = p_config["width"]
        
        # Construct points
        p0 = base_pt
        p1 = (base_pt[0] + c_off[0], base_pt[1] + c_off[1])
        p2 = (base_pt[0] + e_off[0], base_pt[1] + e_off[1])
        
        # Draw Mesh (Two passes with opposite chirality)
        # This creates the lattice/interference pattern look
        generate_petal_veins(svg, p0, p1, p2, w, num_lines=35, chirality=1)
        generate_petal_veins(svg, p0, p1, p2, w, num_lines=35, chirality=-1)
        
        # Draw Mirror Petal if requested
        if p_config["mirror"]:
            # Mirror X coordinates around center
            p1_m = (base_pt[0] - c_off[0], base_pt[1] + c_off[1])
            p2_m = (base_pt[0] - e_off[0], base_pt[1] + e_off[1])
            
            generate_petal_veins(svg, p0, p1_m, p2_m, w, num_lines=35, chirality=1)
            generate_petal_veins(svg, p0, p1_m, p2_m, w, num_lines=35, chirality=-1)

    svg.save(filepath)