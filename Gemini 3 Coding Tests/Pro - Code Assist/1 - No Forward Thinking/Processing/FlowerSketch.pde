/**
 * FlowerSketch.pde
 * Main entry point for the procedural flower generation.
 * Sets up the canvas and triggers the flower system renderer.
 */

FlowerSystem flower;

void setup() {
  // Set a high resolution canvas
  size(1200, 1200, P2D);
  smooth(8);
  
  // Initialize the flower system
  flower = new FlowerSystem();
  
  // Render once
  noLoop();
}

void draw() {
  // Background color: Off-white / Cream (Seashell)
  background(255, 250, 245);
  
  // Center the drawing coordinates
  translate(width/2, height * 0.65);
  
  // Draw the flower
  flower.render();
  
  //Optional: Save output
  save("procedural_flower.png");
}

void keyPressed() {
  // Press 'r' to regenerate with new noise seeds (if noise is used)
  if (key == 'r') redraw();
}
