class Attractor {
  float x, y;
  Configuration config;
  
  Attractor(Configuration c) {
    this.config = c;
    reset();
  }
  
  void reset() {
    x = config.startX;
    y = config.startY;
    
    // Skip the first few iterations to let the orbit settle onto the attractor
    for(int i=0; i<100; i++) update();
  }
  
  // The helper function G(v) specific to this attractor
  float g(float v) {
    float mu = config.mu;
    return mu * v + (2 * (1 - mu) * v * v) / (1 + v * v);
  }
  
  void update() {
    // Calculate G(x_n)
    float gx = g(x);
    
    // Calculate x_n+1
    float nextX = y + config.a * y * (1 - config.b * y * y) + gx;
    
    // Calculate y_n+1
    // Note: The equation uses the NEW x (nextX) for the G calculation
    float gyNext = g(nextX);
    float nextY = -x + gyNext;
    
    // Update state
    x = nextX;
    y = nextY;
  }
  
  PVector getCurrent() {
    return new PVector(x, y);
  }
}
