/**
 * FlowerLines.pde
 * 
 * Procedural recreation of a pastel guilloché "flower lines" drawing.
 * 
 * Controls:
 *   - Press 'r' to re-render (same seed).
 *   - Press 's' to save a PNG to the sketch folder.
 */

FlowerScene scene;

void setup() {
  size(2500,1350,P2D);
  pixelDensity(1);
  smooth(8);

  randomSeed(Config.SEED);
  noiseSeed(Config.SEED);

  scene = new FlowerScene();
  renderOnce();
}

void draw() {
  // Rendered once in setup(); keep draw() empty.
}

void renderOnce() {
  scene.render(g);
  noLoop();
}

void keyPressed() {
  if (key == 'r' || key == 'R') {
    loop();
    renderOnce();
  }
  if (key == 's' || key == 'S') {
    String filename = "flower-lines-" + nf(year(), 4) + nf(month(), 2) + nf(day(), 2)
      + "-" + nf(hour(), 2) + nf(minute(), 2) + nf(second(), 2) + ".png";
    saveFrame(filename);
    println("Saved: " + filename);
  }
}
