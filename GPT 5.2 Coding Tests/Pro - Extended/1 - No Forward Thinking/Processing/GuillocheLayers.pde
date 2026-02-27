/**
 * GuillocheLayers.pde
 * 
 * Flower layers: each layer is a bundle of guilloché curves.
 */

abstract class GuillocheLayer {
  // Appearance
  int baseColor;
  float baseAlpha;
  float strokeW;
  float rotation;

  // Geometry
  float globalScale;
  float yScale;
  int petalsN;
  int curveCount;
  float phaseRange;
  float phaseOffset;
  float wPhaseStep;
  float wPhaseOffset;

  // Base curve params
  float baseR;
  float baseA;
  float baseB;
  float baseM;

  Warp warp = new Warp();

  GuillocheLayer() {}

  abstract float calcR(int i, float u);
  abstract float calcA(int i, float u);
  abstract float calcB(int i, float u);
  abstract float calcM(int i, float u);
  abstract float curveAlpha(int i, float u);

  void render(PGraphics pg, AngleTable tab, PVector center) {
    pg.pushStyle();
    pg.noFill();
    pg.strokeWeight(strokeW);
    pg.strokeCap(ROUND);
    pg.strokeJoin(ROUND);

    float cr = cos(rotation);
    float sr = sin(rotation);

    for (int i = 0; i < curveCount; i++) {
      float u = (curveCount == 1) ? 0.5 : i / (float)(curveCount - 1);

      float phase = (u - 0.5) * 2.0 * phaseRange + phaseOffset;
      float wphase = i * wPhaseStep + wPhaseOffset;

      float R = calcR(i, u);
      float A = calcA(i, u);
      float B = calcB(i, u);
      float M = calcM(i, u);

      float a = curveAlpha(i, u);

      pg.stroke(red(baseColor), green(baseColor), blue(baseColor), a);

      pg.beginShape();
      for (int j = 0; j < tab.steps; j++) {
        float t = tab.t[j];

        float r = R + A * cos(petalsN * t + phase);
        float w = B * cos(M * t + wphase);

        float x = r * tab.cosT[j] - w * tab.sinT[j];
        float y = (r * tab.sinT[j] + w * tab.cosT[j]) * yScale;

        // Apply gentle polar warp to emphasize the top petal.
        float wf = warp.factor(x, y);
        x *= wf;
        y *= wf;

        // Global scale + rotation + translate
        float xs = x * globalScale;
        float ys = y * globalScale;

        float xr = xs * cr - ys * sr;
        float yr = xs * sr + ys * cr;

        pg.vertex(center.x + xr, center.y + yr);
      }
      pg.endShape();
    }

    pg.popStyle();
  }
}

class BlueLayer extends GuillocheLayer {
  BlueLayer() {
    baseColor = Config.BLUE_BASE;
    baseAlpha = Config.BLUE_ALPHA;
    strokeW = Config.STROKE_WEIGHT;

    globalScale = Config.FLOWER_SCALE;
    yScale = 1.22;
    petalsN = 8;

    curveCount = 110;
    phaseRange = 1.20;
    phaseOffset = 0.0;
    wPhaseStep = 0.17;
    wPhaseOffset = 0.0;

    baseR = 3.80;
    baseA = 4.20;
    baseB = 0.65;
    baseM = 28.0;

    rotation = Config.FLOWER_ROTATION - 0.012;
    warp.topLift = 0.055;
    warp.shoulder = 0.018;
  }

  float calcR(int i, float u) {
    return baseR + 0.08 * sin(i * 0.15);
  }

  float calcA(int i, float u) {
    return baseA + 0.12 * cos(i * 0.11);
  }

  float calcB(int i, float u) {
    // Slight breathing in wobble amplitude (creates the pencil-like layering).
    float mult = 0.75 + 0.40 * sin(i * 0.23 + 1.20);
    return baseB * mult;
  }

  float calcM(int i, float u) {
    // Wobble frequency drift for scalloped edges.
    return baseM + 1.20 * sin(i * 0.07);
  }

  float curveAlpha(int i, float u) {
    // Fade outer curves slightly to avoid a dark rim.
    float centerBias = 1.0 - abs(u - 0.5) * 1.2;
    centerBias = constrain(centerBias, 0.25, 1.0);
    return baseAlpha * centerBias;
  }
}

class PinkLayer extends GuillocheLayer {
  PinkLayer() {
    baseColor = Config.PINK_BASE;
    baseAlpha = Config.PINK_ALPHA;
    strokeW = Config.STROKE_WEIGHT;

    globalScale = Config.FLOWER_SCALE;
    yScale = 1.22;
    petalsN = 7;

    curveCount = 100;
    phaseRange = 1.00;
    phaseOffset = 0.35;
    wPhaseStep = 0.21;
    wPhaseOffset = 0.50;

    baseR = 3.75;
    baseA = 4.05;
    baseB = 0.55;
    baseM = 26.0;

    rotation = Config.FLOWER_ROTATION + 0.010;
    warp.topLift = 0.045;
    warp.shoulder = 0.014;
  }

  float calcR(int i, float u) {
    return baseR + 0.10 * cos(i * 0.18);
  }

  float calcA(int i, float u) {
    return baseA + 0.10 * sin(i * 0.13);
  }

  float calcB(int i, float u) {
    float mult = 0.75 + 0.35 * cos(i * 0.27);
    return baseB * mult;
  }

  float calcM(int i, float u) {
    return baseM + 1.60 * cos(i * 0.09);
  }

  float curveAlpha(int i, float u) {
    float centerBias = 1.0 - abs(u - 0.5) * 1.0;
    centerBias = constrain(centerBias, 0.35, 1.0);
    return baseAlpha * centerBias;
  }
}
