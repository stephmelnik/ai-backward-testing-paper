function estimateMaxD(layerCfg) {
  let maxD = 0;
  for (const s of layerCfg.underlay) {
    maxD = Math.max(maxD, s.d0 + Math.abs(s.d1) + Math.abs(s.d2));
  }
  for (const d of layerCfg.accents.dValues) {
    maxD = Math.max(maxD, d);
  }
  return maxD;
}

function computeScale(flowerCfg) {
  const { R, r, layers } = flowerCfg.guilloche;
  const base = (R - r);
  const maxD = Math.max(estimateMaxD(layers.blue), estimateMaxD(layers.pink));
  const radiusUnits = base + maxD;
  return flowerCfg.radius / radiusUnits;
}

function strokeCubic(ctx, p0, p1, p2, p3) {
  ctx.beginPath();
  ctx.moveTo(p0.x, p0.y);
  ctx.bezierCurveTo(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y);
  ctx.stroke();
}

function drawPetalVeins(ctx, rng, opts) {
  const {
    petals,
    curvesPerPetal,
    length,
    width,
    rot,
    cx,
    cy,
    scale,
    scaleY,
    stroke,
    alpha,
    lineWidth,
  } = opts;

  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.strokeStyle = rgba(stroke, 1);
  ctx.lineWidth = lineWidth;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';

  const TWO_PI = Math.PI * 2;

  for (let p = 0; p < petals; p++) {
    const baseAng = (p / petals) * TWO_PI + rot;

    // A gentle fan: more curvature for outer veins.
    for (let i = 0; i < curvesPerPetal; i++) {
      const u = curvesPerPetal <= 1 ? 1 : i / (curvesPerPetal - 1);
      const uE = Math.pow(u, 1.10);

      const L = length * (0.34 + 0.66 * uE);
      const W = width * (0.12 + 0.88 * uE);

      const localTip = { x: 0, y: L };

      // Two symmetric strokes per vein (left and right), like a penciled leaf.
      for (const sign of [-1, 1]) {
        const phaseA = 0.9 + p * 0.6;
        const phaseB = 1.7 + p * 0.55;

        const bend1 = (0.35 + 0.65 * Math.sin(uE * Math.PI * 1.25 + phaseA));
        const bend2 = (0.35 + 0.65 * Math.sin(uE * Math.PI * 1.10 + phaseB));

        const cp1 = {
          x: sign * W * 0.26 * bend1,
          y: L * 0.24,
        };
        const cp2 = {
          x: sign * W * 0.62 * bend2,
          y: L * 0.78,
        };

        // Subtle pencil wobble
        const wobble = 0.016 + 0.012 * uE;
        const ang = baseAng + jitter(rng, wobble);

        const P0 = rotatePoint(0, 0, ang);
        const P1 = rotatePoint(cp1.x + jitter(rng, 0.05), cp1.y + jitter(rng, 0.07), ang);
        const P2 = rotatePoint(cp2.x + jitter(rng, 0.07), cp2.y + jitter(rng, 0.09), ang);
        const P3 = rotatePoint(localTip.x, localTip.y, ang);

        const p0 = { x: cx + P0.x * scale, y: cy + P0.y * scale * scaleY };
        const p1 = { x: cx + P1.x * scale, y: cy + P1.y * scale * scaleY };
        const p2 = { x: cx + P2.x * scale, y: cy + P2.y * scale * scaleY };
        const p3 = { x: cx + P3.x * scale, y: cy + P3.y * scale * scaleY };

        strokeCubic(ctx, p0, p1, p2, p3);
      }
    }
  }

  ctx.restore();
}

function drawAxis(ctx, { cx, cy, scale, scaleY, stroke, alpha, lineWidth }) {
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.strokeStyle = rgba(stroke, 1);
  ctx.lineWidth = lineWidth;
  ctx.lineCap = 'round';

  const len = scale * 12.8;
  ctx.beginPath();
  ctx.moveTo(cx, cy - len * scaleY);
  ctx.lineTo(cx, cy + len * scaleY);
  ctx.stroke();
  ctx.restore();
}

function drawFlower(ctx, w, h, rng, flowerCfg) {
  const scale = computeScale(flowerCfg);
  const { aspectY } = flowerCfg;

  const cx = w * flowerCfg.center.x;
  const cy = h * flowerCfg.center.y;

  const gcfg = flowerCfg.guilloche;
  const { R, r } = gcfg;

  // Light axis spine (drawn once, under everything)
  drawAxis(ctx, {
    cx,
    cy,
    scale,
    scaleY: aspectY,
    stroke: gcfg.layers.blue.stroke,
    alpha: flowerCfg.axis.alpha,
    lineWidth: flowerCfg.axis.lineWidth,
  });

  // Draw each color layer as its own named "component".
  for (const [name, layer] of Object.entries(gcfg.layers)) {
    ctx.save();
    ctx.globalCompositeOperation = layer.composite;

    // Underlay: long sweeping spirograph passes (gives the scalloped pencil look)
    for (const sweep of layer.underlay) {
      const baseOpts = {
        R,
        r,
        ...sweep,
        cx,
        cy,
        scale,
        scaleY: aspectY,
        stroke: layer.stroke,
        // gentle per-point wiggle to avoid perfect computer symmetry
        dJitter: 0.018,
      };

      // Two or three light re-traces to mimic pencil pressure variation
      const passes = name === 'blue' ? 3 : 2;
      drawScribbledSweeps(ctx, rng, baseOpts, passes, 0.012);
    }

    // Veins: fan-like interior curves per petal
    drawPetalVeins(ctx, rng, {
      ...layer.veins,
      cx,
      cy,
      scale,
      scaleY: aspectY,
      stroke: layer.stroke,
    });

    // Accents: a few fixed rosettes with slightly higher pressure
    const a = layer.accents;
    for (const d of a.dValues) {
      drawRosette(ctx, {
        R,
        r,
        D: d,
        cx,
        cy,
        scale,
        scaleY: aspectY,
        rot: (layer.veins.rot || 0) + jitter(rng, a.rotJitter),
        stroke: layer.stroke,
        alpha: a.alpha * randRange(rng, 0.85, 1.05),
        lineWidth: a.lineWidth,
        steps: 7200,
      });
    }

    ctx.restore();
  }

  // Final softening pass: a whisper of extra underlay to tie colors together.
  ctx.save();
  ctx.globalCompositeOperation = 'multiply';
  drawSweepingHypotrochoid(ctx, rng, {
    R,
    r,
    d0: 3.35,
    d1: 3.25,
    d2: 0.25,
    m1: 0.09,
    m2: 0.35,
    phase1: 0.8,
    phase2: 2.2,
    cycles: 72,
    pointsPerCycle: 620,
    rot: 0.03,
    cx,
    cy,
    scale,
    scaleY: aspectY,
    stroke: { r: 165, g: 152, b: 210 },
    alpha: 0.028,
    lineWidth: 0.45,
    dJitter: 0.016,
  });
  ctx.restore();
}
