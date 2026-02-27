/**
 * GuillocheMath.pde
 * 
 * Shared helpers for sampling and warping.
 */

class AngleTable {
  final int steps;
  final float[] t;
  final float[] cosT;
  final float[] sinT;

  AngleTable(int steps) {
    this.steps = steps;
    t = new float[steps];
    cosT = new float[steps];
    sinT = new float[steps];

    // Sample t in [0, TWO_PI) (exclude endpoint to avoid forced closing seams).
    for (int i = 0; i < steps; i++) {
      float tt = TWO_PI * i / (float)steps;
      t[i] = tt;
      cosT[i] = cos(tt);
      sinT[i] = sin(tt);
    }
  }
}

class Warp {
  // Gentle top/bottom bias (adds a lily-like emphasis).
  float topLift = 0.05f;

  // Optional second harmonic for subtle shoulder shaping.
  float shoulder = 0.02f;

  float factor(float x, float y) {
    float ang = atan2(y, x);  // Processing coords: y down; fine.
    // Up direction is ang = -HALF_PI.
    float up = -sin(ang);     // +1 at top, -1 at bottom.
    float w = 1.0 + topLift * up;

    // Add a tiny 2nd harmonic to soften side petals.
    float s = cos(2.0 * (ang + HALF_PI)); // aligned with vertical axis
    w += shoulder * s;

    return w;
  }
}
