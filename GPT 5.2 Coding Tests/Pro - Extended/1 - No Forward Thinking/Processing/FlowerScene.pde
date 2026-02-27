/**
 * FlowerScene.pde
 * 
 * Scene orchestrator: background + flower layers.
 */
class FlowerScene {
  PaperBackground paper;
  GuillocheFlower flower;

  FlowerScene() {
    paper = new PaperBackground(Config.PAPER_BASE);
    flower = new GuillocheFlower();
  }

  void render(PGraphics pg) {
    paper.render(pg);
    flower.render(pg);
  }
}
