class Configuration {
  // --- Mathematical Parameters (Gumowski-Mira Map) ---
  
  // 'mu': Controls the main lobe structure. 
  // Values around -0.48 produce this specific "Orchid" / "Fleur-de-lis" shape.
  // Values near -0.9 produce wings; values near -0.2 produce needles.
  float mu = -0.48; 
  
  // 'a': Controls the tightness of the envelope.
  // This is very sensitive. 0.008 is the standard for this biological form.
  float a = 0.008;
  
  // 'b': Usually fixed at 0.05 for these types of patterns.
  float b = 0.05;
  
  // Initial conditions. 
  float startX = 1.0;
  float startY = 1.0;

  // --- Rendering Parameters ---
  
  // Zoom level. The mathematical values are small (~ -15 to 15), so we scale up.
  float scale = 32.0;
  
  // Speed: How many points to calculate per frame.
  int iterationsPerFrame = 8000;
  
  // Rotation: PI/4 (45 degrees) aligns the attractor's natural diagonal to vertical.
  float rotation = PI / 4.0;
  
  // Offset: Adjust the position on screen.
  float offsetX = 0;
  float offsetY = 0;
  
  // Symmetry: Enforce perfect bilateral symmetry to match the reference.
  boolean mirrorX = true;
  
  // Appearance
  float alpha = 20;        // Opacity (0-255). Low values create smoother gradients.
  float pointSize = 0.65;  // Very fine points for the delicate "hairline" look.
  int bgColor = 0xFFFFFCF5; // Warm Floral White / Cream background
}
