// Parameter presets for the procedural reconstruction.
// Tweak these values (and re-save) to edit the artwork.
//
// Notes:
// - `tMax` is in radians. Setting it to `2*Math.PI*cycles` is convenient.
// - Each layer draws `strokes * pointsPerStroke` point sprites.
// - The curve is computed in the vertex shader; no textures or image assets are used.

const CONFIG = {
  canvas: {
    // Render resolution multiplier (1 = devicePixelRatio). Increase for crisper lines.
    resolutionScale: 1.0,
  },

  background: {
    // Warm paper base (sampled from the reference image corner).
    paperBase: [0.9806, 0.9556, 0.9303],
    // Very subtle cool tint towards the center.
    paperCool: [0.9700, 0.9750, 0.9850],
    vignetteStrength: 0.22,
    vignettePower: 1.85,

    grainStrength: 0.045,
    grainScale: 1.6,

    // Adds faint “paper fibers” (anisotropic noise).
    fiberStrength: 0.020,
    fiberScale: 2.6,
    fiberAniso: [1.8, 0.65],
  },

  layers: [
    {
      name: "Blue pencil",
      type: "flower",
      color: [0.780, 0.718, 0.866], // ~ #c7b7dd
      alpha: 1.0,

      // Geometry / sampling
      strokes: 2,
      pointsPerStroke: 140000,
      tMax: Math.PI * 2.0 * 420.0,

      // Stroke-to-stroke offsets
      phase: 0.00,
      phaseStep: 0.16,

      // Global transforms
      globalScale: 0.60,
      offset: [0.0, -0.02],

      // Petal envelope (8 petals via petalN=4)
      petalN: 4.0,
      petalPower: 0.65,
      diagScale: 0.92,
      diagPower: 0.75,

      // Internal looping
      innerFreq: 7.23,
      innerFreqStep: 0.09,
      modAmp: 0.35,
      modWobble: 0.50,

      // Radial “breathing” that returns strokes back towards the center (controls the fan-like texture)
      oscMin: 0.42,

      // Scalloped edges
      loopFreq: 75.5,
      loopFreqStep: 0.55,
      loopAmp: 0.040,

      // Vertical shaping
      yScale: 1.05,
      yWarp: -0.18,

      // Stroke appearance
      pointSize: 1.75,
      softness: 10.0,
      grain: 0.28,
    },

    {
      name: "Pink pencil",
      type: "flower",
      color: [0.927, 0.823, 0.858], // ~ #ecd2db
      alpha: 0.045,

      strokes: 2,
      pointsPerStroke: 140000,
      tMax: Math.PI * 2.0 * 420.0,

      // Stroke-to-stroke offsets
      phase: 0.23,
      phaseStep: 0.14,

      globalScale: 0.612,
      offset: [0.0, -0.02],

      petalN: 4.0,
      petalPower: 0.66,
      diagScale: 0.91,
      diagPower: 0.74,

      innerFreq: 7.11,
      innerFreqStep: 0.08,
      modAmp: 0.33,
      modWobble: 0.45,

      // Radial “breathing” (slightly different from the blue layer)
      oscMin: 0.44,

      loopFreq: 76.7,
      loopFreqStep: 0.60,
      loopAmp: 0.038,

      yScale: 1.05,
      yWarp: -0.18,

      pointSize: 1.65,
      softness: 10.5,
      grain: 0.30,
    },

    // Subtle central axis (helps match the faint centerline in the reference).
    {
      name: "Axis",
      type: "axis",
      color: [0.717, 0.634, 0.793], // slightly deeper lavender ~ #b7a2ca
      alpha: 0.028,

      strokes: 1,
      pointsPerStroke: 9000,
      tMax: 1.0, // ignored by axis mode

      globalScale: 0.62,
      offset: [0.0, -0.02],

      axisWidth: 0.0024,
      axisYMin: -1.55,
      axisYMax: 1.22,

      pointSize: 1.45,
      softness: 12.0,
      grain: 0.18,
    },
  ],
};
