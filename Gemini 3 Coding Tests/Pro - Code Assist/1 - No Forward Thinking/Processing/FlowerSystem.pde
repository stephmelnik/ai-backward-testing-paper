/**
 * FlowerSystem.pde
 * Manages the collection of petals that make up the flower.
 * Defines the shape and layout of the flower using Bezier control points.
 */

class FlowerSystem {
  ArrayList<Petal> petals;

  FlowerSystem() {
    petals = new ArrayList<Petal>();
    initStructure();
  }

  void initStructure() {
    // Define the flower structure using layers of petals.
    // Coordinates are relative to the center (0,0).
    // Y is negative going up.
    
    // 1. Center Top Lobe (The main vertical petal)
    // Spine goes straight up.
    addSymmetricPetal(
      new PVector(0, 0),       // Start
      new PVector(0, -200),    // Control 1
      new PVector(0, -350),    // Control 2
      new PVector(0, -550),    // End
      140,                     // Max Width
      200                      // Density (Line count)
    );

    // 2. Upper Side Wings (Large, extending outwards and up)
    addSymmetricPetal(
      new PVector(0, 0),
      new PVector(80, -150),
      new PVector(250, -300),
      new PVector(350, -400),
      120,
      180
    );

    // 3. Mid Side Wings (Extending horizontally)
    addSymmetricPetal(
      new PVector(0, 0),
      new PVector(100, -50),
      new PVector(300, -100),
      new PVector(420, -150),
      110,
      180
    );

    // 4. Lower Side Lobes (Drooping slightly)
    addSymmetricPetal(
      new PVector(0, 0),
      new PVector(80, 50),
      new PVector(250, 50),
      new PVector(380, 100),
      100,
      160
    );
    
    // 5. Bottom Lobes (Small, round base)
    addSymmetricPetal(
      new PVector(0, 0),
      new PVector(50, 80),
      new PVector(100, 150),
      new PVector(0, 250),
      90,
      150
    );
  }

  // Helper to add a petal and its mirrored counterpart
  void addSymmetricPetal(PVector start, PVector c1, PVector c2, PVector end, float w, int density) {
    // Right side
    petals.add(new Petal(start, c1, c2, end, w, density));
    
    // Left side (Mirror X)
    PVector mC1 = new PVector(-c1.x, c1.y);
    PVector mC2 = new PVector(-c2.x, c2.y);
    PVector mEnd = new PVector(-end.x, end.y);
    petals.add(new Petal(start, mC1, mC2, mEnd, w, density));
  }

  void render() {
    for (Petal p : petals) {
      p.draw();
    }
  }
}