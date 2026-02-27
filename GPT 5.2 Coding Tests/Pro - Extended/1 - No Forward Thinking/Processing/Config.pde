/**
 * Config.pde
 * 
 * Centralized parameters for easy editing.
 */
class Config {
  static final int CANVAS_SIZE = 2048;

  // Change SEED for a different (but similar) rendering.
  static final int SEED = 1337;

  // Background
  static final int PAPER_BASE = 0xFFFAF4EE; // warm off-white
  static final float VIGNETTE_STRENGTH = 0.12f;

  // Flower placement
  static final float FLOWER_SCALE = 94.0f;
  static final float FLOWER_ROTATION = 0.0f;  // radians
  static final float CENTER_X = 0.5f;         // relative (0..1)
  static final float CENTER_Y = 0.505f;       // relative (0..1)

  // Stroke styling
  static final float STROKE_WEIGHT = 0.65f;
  static final boolean USE_MULTIPLY_BLEND = true;

  // Palette (RGB matches sampled averages from the reference)
  static final int BLUE_BASE = 0xFFAC9AD4;
  static final int PINK_BASE = 0xFFE5BBD1;

  // Layer alpha (0..255). These are intentionally low; density comes from many curves.
  static final float BLUE_ALPHA = 14.0f;
  static final float PINK_ALPHA = 11.0f;

  // Paper grain
  static final int GRAIN_DOTS = 52000;
  static final int FIBER_LINES = 2200;
}
