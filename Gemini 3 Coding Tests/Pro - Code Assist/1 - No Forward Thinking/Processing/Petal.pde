/**
 * Petal.pde
 * Represents a single petal or lobe of the flower.
 * Generates a dense set of curves oscillating around a central Bezier spine.
 */

class Petal {
  PVector p0, p1, p2, p3; // Bezier control points for the spine
  float maxWidth;         // Maximum width of the petal envelope
  int lineCount;          // Number of lines to draw to create texture
  
  // Color Palette Definition
  color colorCenter = color(20, 20, 140);   // Deep Blue/Purple
  color colorMid    = color(100, 60, 180);  // Violet
  color colorTip    = color(255, 150, 160); // Pink/Salmon

  Petal(PVector start, PVector c1, PVector c2, PVector end, float w, int count) {
    this.p0 = start.copy();
    this.p1 = c1.copy();
    this.p2 = c2.copy();
    this.p3 = end.copy();
    this.maxWidth = w;
    this.lineCount = count;
  }

  void draw() {
    noFill();
    strokeWeight(0.6); // Very thin lines for delicate texture
    
    // Draw multiple variations of the spine
    for (int i = 0; i < lineCount; i++) {
      // Normalized progress through the batch of lines (0.0 to 1.0)
      float progress = map(i, 0, lineCount, 0, 1);
      
      // Each line has a unique phase and slightly different frequency
      // This creates the interference/moire pattern look
      float phase = progress * TWO_PI * 15; 
      float freq = 10.0 + (progress * 2.0); 
      
      drawParametricCurve(progress, phase, freq);
    }
  }

  // Draws a single curve that follows the spine but oscillates
  void drawParametricCurve(float lineIndexNorm, float phase, float freq) {
    beginShape();
    
    // Resolution of the curve
    int steps = 300;
    
    for (int tStep = 0; tStep <= steps; tStep++) {
      float t = tStep / (float)steps;
      
      // 1. Calculate position on the main spine (Bezier)
      float bx = bezierPoint(p0.x, p1.x, p2.x, p3.x, t);
      float by = bezierPoint(p0.y, p1.y, p2.y, p3.y, t);
      
      // 2. Calculate the tangent vector to find the normal
      float tx = bezierTangent(p0.x, p1.x, p2.x, p3.x, t);
      float ty = bezierTangent(p0.y, p1.y, p2.y, p3.y, t);
      
      // Normalize tangent
      float len = sqrt(tx*tx + ty*ty);
      if (len > 0) { tx /= len; ty /= len; }
      
      // Calculate Normal vector (perpendicular to tangent)
      float nx = -ty;
      float ny = tx;
      
      // 3. Determine Envelope Width at this point t
      // Shape profile: starts thin, gets wide, tapers at end.
      // sin(t * PI) gives a nice leaf shape (0 -> 1 -> 0)
      float envelope = sin(t * PI);
      // Flatten the tip slightly for a rounder look
      envelope = pow(envelope, 0.8); 
      
      float currentWidth = maxWidth * envelope;
      
      // 4. Oscillate!
      // We add sine waves to the position to create the loops.
      // We oscillate in both Normal and Tangent directions to create loops/curls.
      
      // Primary oscillation (Transverse wave - width)
      // Varies based on which line we are drawing (lineIndexNorm) to fill the space
      float waveAmp = currentWidth * (sin(phase + t * freq * TWO_PI) * 0.5 + 0.5);
      
      // To make it look like the reference, we need the lines to span the full width
      // but loop back.
      // Let's use a "Spirograph" logic:
      // Center of oscillation is the spine.
      // Radius is currentWidth.
      
      // Modulate amplitude based on the specific line index to fill the petal volume
      // Some lines stay near center, some go to edge.
      float spread = (lineIndexNorm - 0.5) * 2.0; // -1 to 1
      
      // Complex oscillation pattern
      float oscN = sin(t * freq * PI + phase) * currentWidth * 0.8;
      float oscT = cos(t * freq * PI + phase) * currentWidth * 0.3; // Smaller longitudinal wave creates loops
      
      // Apply offsets
      float px = bx + (nx * oscN) + (tx * oscT);
      float py = by + (ny * oscN) + (ty * oscT);
      
      // 5. Coloring
      // Calculate distance from the "heart" of the flower (approx 0,0)
      float distFromCenter = dist(0, 0, px, py);
      
      // Map distance to color gradient
      color c = getGradientColor(distFromCenter);
      
      // Set alpha low for blending
      stroke(c, 60); 
      
      vertex(px, py);
    }
    endShape();
  }
  
  // Helper to interpolate colors based on distance
  color getGradientColor(float d) {
    // Define zones
    float coreRadius = 100;
    float midRadius = 350;
    float edgeRadius = 600;
    
    if (d < coreRadius) {
      return colorCenter;
    } else if (d < midRadius) {
      float amt = map(d, coreRadius, midRadius, 0, 1);
      return lerpColor(colorCenter, colorMid, amt);
    } else {
      float amt = map(d, midRadius, edgeRadius, 0, 1);
      // Clamp amount
      if (amt > 1) amt = 1;
      return lerpColor(colorMid, colorTip, amt);
    }
  }
}