class Palette {
  Configuration config;
  
  // Colors sampled from the reference image style
  int cInner = 0xFF3F51B5; // Deep Indigo / Blue for the spine/center
  int cMid   = 0xFF9C27B0; // Violet transition
  int cOuter = 0xFFFF80AB; // Soft Pink for the outer petal tips
  
  Palette(Configuration c) {
    this.config = c;
  }
  
  int getColor(float radius) {
    // Map the mathematical radius (approx 0 to 20) to a 0.0-1.0 progress value.
    // The value '15.0' defines the radius where the outer color is fully dominant.
    float t = constrain(radius / 15.0, 0, 1);
    
    // Create a 2-stage gradient: Inner -> Mid -> Outer
    if (t < 0.5) {
      // First half: Blue to Purple
      return lerpColor(cInner, cMid, t * 2.0);
    } else {
      // Second half: Purple to Pink
      return lerpColor(cMid, cOuter, (t - 0.5) * 2.0);
    }
  }
}
