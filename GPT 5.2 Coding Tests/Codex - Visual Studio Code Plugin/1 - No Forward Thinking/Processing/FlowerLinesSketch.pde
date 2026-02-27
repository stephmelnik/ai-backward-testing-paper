int CANVAS_SIZE = 1200;
float BASE_OFFSET_Y = 0.66f;

BloomLayer pinkLayer;
BloomLayer blueLayer;
color BG = color(247, 239, 232);
color PINK = color(220, 162, 186);
color BLUE = color(118, 128, 205);
color STEM = color(150, 140, 190);

void settings() {
  size(900, 900);
  smooth(8);
}

void setup() {
  noFill();
  strokeCap(ROUND);
  strokeJoin(ROUND);

  ArrayList<PetalCluster> clusters = new ArrayList<PetalCluster>();
  clusters.add(new PetalCluster(radians(-90), 430, 240, 90, 0.08f, 0.92f, 0.3f));
  clusters.add(new PetalCluster(radians(-120), 360, 240, 80, 0.09f, 0.88f, 0.6f));
  clusters.add(new PetalCluster(radians(-60), 360, 240, 80, 0.09f, 0.88f, 1.2f));
  clusters.add(new PetalCluster(radians(-150), 300, 250, 70, 0.10f, 0.86f, 0.9f));
  clusters.add(new PetalCluster(radians(-30), 300, 250, 70, 0.10f, 0.86f, 1.5f));
  clusters.add(new PetalCluster(radians(-170), 250, 260, 60, 0.11f, 0.84f, 1.1f));
  clusters.add(new PetalCluster(radians(-10), 250, 260, 60, 0.11f, 0.84f, 1.7f));

  pinkLayer = new BloomLayer(clusters, PINK, 55, 0.9f);
  blueLayer = new BloomLayer(clusters, BLUE, 65, 1.1f);

  noLoop();
}

void draw() {
  background(BG);

  pushMatrix();
  translate(width / 2.0f, height * BASE_OFFSET_Y);

  drawStem();
  pinkLayer.render(0.02f);
  blueLayer.render(-0.02f);

  popMatrix();
  
  boolean screenshot = true;
  if(screenshot) {
      save("test.jpg");
      screenshot = false;
  }
}

void drawStem() {
  stroke(STEM, 60);
  strokeWeight(1);
  line(0, 0, 0, -480);
}
