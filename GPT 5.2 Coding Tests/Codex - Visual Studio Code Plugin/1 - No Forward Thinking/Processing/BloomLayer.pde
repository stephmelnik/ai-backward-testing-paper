class BloomLayer {
  ArrayList<PetalCluster> clusters;
  color strokeColor;
  float alpha;
  float weight;

  BloomLayer(ArrayList<PetalCluster> clusters, color strokeColor, float alpha, float weight) {
    this.clusters = clusters;
    this.strokeColor = strokeColor;
    this.alpha = alpha;
    this.weight = weight;
  }

  void render(float drift) {
    for (PetalCluster cluster : clusters) {
      cluster.drawLoops(strokeColor, alpha, weight, drift);
    }
    for (PetalCluster cluster : clusters) {
      cluster.drawSpines(strokeColor, alpha * 0.6f, weight * 0.8f, -drift * 0.6f);
    }
  }
}

class PetalCluster {
  float angle;
  float length;
  float width;
  int loops;
  float jitter;
  float roundness;
  float phase;

  PetalCluster(float angle, float length, float width, int loops, float jitter, float roundness, float phase) {
    this.angle = angle;
    this.length = length;
    this.width = width;
    this.loops = loops;
    this.jitter = jitter;
    this.roundness = roundness;
    this.phase = phase;
  }

  void drawLoops(color strokeColor, float alpha, float weight, float drift) {
    for (int i = 0; i < loops; i++) {
      float denom = max(1.0f, loops - 1.0f);
      float t = i / denom;
      float s = lerp(0.18f, 1.0f, t);
      float wobble = sin(t * TWO_PI * 1.6f + phase) * jitter;
      float localAngle = angle + wobble + drift;

      float localLength = length * s;
      float localWidth = width * s * (0.9f + 0.1f * sin(t * TWO_PI * 2.0f + phase));
      float localRoundness = lerp(0.7f, roundness, s);

      float a = alpha * (0.15f + 0.85f * s);
      float w = weight * (0.25f + 0.75f * s);

      stroke(strokeColor, a);
      strokeWeight(w);
      drawLeaf(localLength, localWidth, localAngle, localRoundness);
    }
  }

  void drawSpines(color strokeColor, float alpha, float weight, float drift) {
    for (int i = -2; i <= 2; i++) {
      float offset = width * 0.08f * i;
      float localAngle = angle + drift + sin(phase + i) * jitter * 0.4f;

      stroke(strokeColor, alpha * (0.35f + 0.12f * abs(i)));
      strokeWeight(weight * 0.35f);
      drawSpine(length * 0.95f, localAngle, offset);
    }
  }
}

void drawLeaf(float length, float width, float angle, float roundness) {
  pushMatrix();
  rotate(angle);

  beginShape();
  vertex(0, 0);
  float cp1x = width * 0.35f;
  float cp1y = -length * 0.15f;
  float cp2x = width * 0.95f;
  float cp2y = -length * roundness;
  float tipY = -length;
  bezierVertex(cp1x, cp1y, cp2x, cp2y, 0, tipY);

  float cp3x = -width * 0.95f;
  float cp3y = -length * roundness;
  float cp4x = -width * 0.35f;
  float cp4y = -length * 0.15f;
  bezierVertex(cp3x, cp3y, cp4x, cp4y, 0, 0);
  endShape();

  popMatrix();
}

void drawSpine(float length, float angle, float offset) {
  pushMatrix();
  rotate(angle);

  beginShape();
  vertex(0, 0);
  bezierVertex(offset * 0.3f, -length * 0.3f, offset * 0.6f, -length * 0.7f, offset * 0.1f, -length);
  endShape();

  popMatrix();
}
