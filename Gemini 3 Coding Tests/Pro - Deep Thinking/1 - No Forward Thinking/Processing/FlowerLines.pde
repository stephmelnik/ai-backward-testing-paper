/**
 * FlowerLines.pde
 * 
 * Recreates the procedural "Flower Lines" image using the Gumowski-Mira strange attractor.
 * The system calculates millions of iterations of the chaotic map to reveal the 
 * invariant curves that form the petal structures.
 *
 * Controls:
 * - 'R': Reset the simulation.
 * - 'S': Save a high-resolution screenshot.
 */

Configuration config;
Attractor attractor;
Palette palette;

void setup() {
  size(1000, 1000, P2D); // P2D renderer for efficient point drawing
  smooth(8);             // High-quality anti-aliasing
  
  config = new Configuration();
  attractor = new Attractor(config);
  palette = new Palette(config);
  
  reset();
}

void reset() {
  // Creamy off-white background similar to paper
  background(config.bgColor);
  
  attractor.reset();
  
  // Use MULTIPLY blending to create smooth density accumulation.
  // This helps replicate the "ink on paper" aesthetic where overlapping lines get darker.
  blendMode(MULTIPLY); 
}

void draw() {
  // Center the drawing space
  translate(width/2 + config.offsetX, height/2 + config.offsetY);
  
  // Draw a batch of points each frame to animate the buildup
  for (int i = 0; i < config.iterationsPerFrame; i++) {
    attractor.update();
    PVector p = attractor.getCurrent();
    
    // 1. Calculate Radius for Coloring
    // We use the distance from the origin in simulation space
    float r = p.mag();
    
    // 2. Apply Coloring
    int c = palette.getColor(r);
    stroke(c, config.alpha);
    strokeWeight(config.pointSize);
    
    // 3. Transform Coordinates
    // The raw attractor is usually diagonal. We rotate it to stand vertically.
    float rotX = p.x * cos(config.rotation) - p.y * sin(config.rotation);
    float rotY = p.x * sin(config.rotation) + p.y * cos(config.rotation);
    
    // Scale up for the screen
    float sx = rotX * config.scale;
    float sy = rotY * config.scale;
    
    // 4. Draw with Symmetry
    // The reference image is perfectly bilaterally symmetric. 
    // We enforce this by drawing the point and its horizontal mirror.
    point(sx, sy);
    
    if (config.mirrorX) {
      point(-sx, sy);
    }
  }
}

void keyPressed() {
  if (key == 'r' || key == 'R') {
    reset();
  }
  if (key == 's' || key == 'S') {
    saveFrame("flower_output_####.png");
    println("Saved frame.");
  }
}
