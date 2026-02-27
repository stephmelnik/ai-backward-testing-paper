/**
 * PaperBackground.pde
 * 
 * Warm paper background with subtle vignette + grain/fibers.
 * No pixel-array work; everything is primitives.
 */
class PaperBackground {
  int baseCol;

  PaperBackground(int baseCol) {
    this.baseCol = baseCol;
  }

  void render(PGraphics pg) {
    pg.pushStyle();
    pg.background(baseCol);

    drawVignette(pg);
    drawPaperGrain(pg);

    pg.popStyle();
  }

  void drawVignette(PGraphics pg) {
    // Soft center lift and edge darkening via concentric ellipses.
    pg.noStroke();

    float cx = pg.width * 0.5;
    float cy = pg.height * 0.5;

    // Center glow (slight)
    int steps = 120;
    for (int i = 0; i < steps; i++) {
      float t = i / (float)(steps - 1);
      float a = lerp(18, 0, t) * Config.VIGNETTE_STRENGTH;
      float r = lerp(pg.width * 1.25, pg.width * 0.15, t);
      pg.fill(255, 255, 255, a);
      pg.ellipse(cx, cy, r, r);
    }

    // Edge shade (very subtle)
    int steps2 = 140;
    for (int i = 0; i < steps2; i++) {
      float t = i / (float)(steps2 - 1);
      float a = lerp(0, 26, t) * Config.VIGNETTE_STRENGTH;
      float r = lerp(pg.width * 0.75, pg.width * 1.45, t);
      // Warm shadow tint
      pg.fill(235, 226, 214, a);
      pg.ellipse(cx, cy, r, r);
    }
  }

  void drawPaperGrain(PGraphics pg) {
    // Grain dots
    pg.strokeWeight(1);
    for (int i = 0; i < Config.GRAIN_DOTS; i++) {
      float x = random(pg.width);
      float y = random(pg.height);

      // Slightly warmer/cooler specks
      float n = noise(x * 0.005, y * 0.005);
      int col = (n < 0.5) ? color(255, 252, 248) : color(240, 232, 222);

      float a = 6 + 10 * pow(1 - abs(n - 0.5) * 2, 2);
      pg.stroke(red(col), green(col), blue(col), a);
      pg.point(x, y);
    }

    // Paper fibers: faint short lines
    pg.strokeWeight(1);
    for (int i = 0; i < Config.FIBER_LINES; i++) {
      float x = random(pg.width);
      float y = random(pg.height);
      float ang = random(TWO_PI);
      float len = random(10, 60);

      float x2 = x + cos(ang) * len;
      float y2 = y + sin(ang) * len;

      float a = random(4, 10);
      pg.stroke(238, 230, 220, a);
      pg.line(x, y, x2, y2);
    }
  }
}
