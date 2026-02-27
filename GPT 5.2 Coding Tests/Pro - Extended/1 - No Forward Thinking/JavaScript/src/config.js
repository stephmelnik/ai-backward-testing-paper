// Editable configuration for the procedural flower.
//
// Tip: change `SEED` to get a different, but still deterministic, pencil-like texture.

const CONFIG = {
  // Canvas
  CANVAS_SIZE: 2048,
  SEED: 1337,

  // Background paper
  PAPER: {
    base: { r: 253, g: 247, b: 240 },
    vignetteStrength: 0.085,
    vignetteRadius: 0.86,
    grain: {
      dots: 26000,
      dotRadius: [0.25, 1.4],
      dotAlpha: [0.010, 0.035],
      fibers: 1800,
      fiberLen: [8, 80],
      fiberAlpha: [0.004, 0.016],
    },
  },

  // Flower placement and overall scaling
  FLOWER: {
    // Slightly below center like the reference
    center: { x: 0.5, y: 0.515 },
    // Vertical stretch (reference flower is subtly taller than wide)
    aspectY: 1.075,
    // Desired radius in pixels (auto-converted into curve scale)
    radius: 760,

    // Core guilloche / spirograph settings
    guilloche: {
      // 6-petal base (hypotrochoid with R=7, r=1 gives k=(R-r)/r = 6)
      R: 7,
      r: 1,

      // Sweeping (d(t)) parameters for the two color layers
      layers: {
        blue: {
          composite: 'multiply',
          stroke: { r: 140, g: 132, b: 210 },
          underlay: [
            {
              d0: 3.55,
              d1: 3.10,
              // High-frequency, low-amplitude ripple to create the scalloped rim
              // seen around the outer petals.
              d2: 0.07,
              m1: 0.105,
              m2: 72.0,
              phase1: 0.20,
              phase2: 1.40,
              cycles: 104,
              pointsPerCycle: 720,
              rot: 0.0,
              alpha: 0.060,
              lineWidth: 0.55,
            },
            {
              d0: 3.25,
              d1: 3.25,
              d2: 0.35,
              m1: 0.098,
              m2: 0.315,
              phase1: 1.15,
              phase2: 0.35,
              cycles: 96,
              pointsPerCycle: 720,
              rot: 0.012,
              alpha: 0.045,
              lineWidth: 0.50,
            },
          ],
          accents: {
            // Fixed-d rosettes (more defined strokes)
            dValues: [5.4, 5.9, 6.25],
            alpha: 0.12,
            lineWidth: 0.85,
            rotJitter: 0.02,
          },
          veins: {
            petals: 6,
            curvesPerPetal: 34,
            length: 12.1,
            width: 4.6,
            alpha: 0.055,
            lineWidth: 0.26,
            rot: 0.0,
          },
        },

        pink: {
          composite: 'multiply',
          stroke: { r: 226, g: 170, b: 190 },
          underlay: [
            {
              d0: 3.45,
              d1: 3.25,
              // High-frequency, low-amplitude ripple to echo the soft scallops
              // on the outer rim.
              d2: 0.08,
              m1: 0.102,
              m2: 72.0,
              phase1: 0.95,
              phase2: 2.05,
              cycles: 104,
              pointsPerCycle: 700,
              rot: 0.060,
              alpha: 0.050,
              lineWidth: 0.52,
            },
            {
              d0: 3.20,
              d1: 3.35,
              d2: 0.30,
              m1: 0.094,
              m2: 0.345,
              phase1: 2.35,
              phase2: 0.15,
              cycles: 92,
              pointsPerCycle: 700,
              rot: 0.072,
              alpha: 0.038,
              lineWidth: 0.48,
            },
          ],
          accents: {
            dValues: [5.2, 5.7, 6.1],
            alpha: 0.10,
            lineWidth: 0.78,
            rotJitter: 0.03,
          },
          veins: {
            petals: 6,
            curvesPerPetal: 30,
            length: 11.6,
            width: 4.1,
            alpha: 0.045,
            lineWidth: 0.24,
            rot: 0.060,
          },
        },
      },
    },

    // Subtle central axis line (helps match the reference's vertical spine)
    axis: {
      alpha: 0.05,
      lineWidth: 0.7,
    },
  },
};
