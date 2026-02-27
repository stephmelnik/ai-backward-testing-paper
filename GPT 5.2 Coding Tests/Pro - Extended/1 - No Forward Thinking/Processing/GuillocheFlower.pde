/**
 * GuillocheFlower.pde
 * 
 * Composes multiple guilloché layers into the final flower drawing.
 */
class GuillocheFlower {
  AngleTable tab;
  GuillocheLayer[] layers;

  GuillocheFlower() {
    tab = new AngleTable(7800);

    layers = new GuillocheLayer[] {
      new PinkLayer(),
      new BlueLayer()
    };
  }

  void render(PGraphics pg) {
    pg.pushStyle();

    if (Config.USE_MULTIPLY_BLEND) {
      pg.blendMode(MULTIPLY);
    } else {
      pg.blendMode(BLEND);
    }

    PVector center = new PVector(pg.width * Config.CENTER_X, pg.height * Config.CENTER_Y);

    // Soft underlay to mimic pencil "ghost" lines
    drawGhostUnderlay(pg, center);

    for (GuillocheLayer layer : layers) {
      layer.render(pg, tab, center);
    }

    pg.blendMode(BLEND);
    pg.popStyle();
  }

  void drawGhostUnderlay(PGraphics pg, PVector center) {
    // Very faint, slightly larger underlay to soften edges.
    pg.pushStyle();
    pg.noFill();
    pg.strokeWeight(Config.STROKE_WEIGHT * 1.1);
    pg.stroke(255, 255, 255, 18);
    pg.strokeCap(ROUND);
    pg.strokeJoin(ROUND);

    float scale = Config.FLOWER_SCALE * 1.006;
    float yScale = 1.22;
    int steps = tab.steps;

    pg.beginShape();
    for (int j = 0; j < steps; j++) {
      float t = tab.t[j];

      float r = 3.6 + 3.9 * cos(6.0 * t);
      float w = 0.35 * cos(24.0 * t);

      float x = r * tab.cosT[j] - w * tab.sinT[j];
      float y = (r * tab.sinT[j] + w * tab.cosT[j]) * yScale;

      float xs = x * scale;
      float ys = y * scale;

      pg.vertex(center.x + xs, center.y + ys);
    }
    pg.endShape();

    pg.popStyle();
  }
}
