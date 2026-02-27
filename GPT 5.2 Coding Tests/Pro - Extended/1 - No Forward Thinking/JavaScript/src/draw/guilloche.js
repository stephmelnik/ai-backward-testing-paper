function hypotrochoidPoint({ R, r, D, t }) {
  // Hypotrochoid (spirograph) with fixed rolling circles.
  // x = (R - r) cos t + D cos((R-r)/r * t)
  // y = (R - r) sin t - D sin((R-r)/r * t)
  const k = (R - r) / r;
  const ct = Math.cos(t);
  const st = Math.sin(t);
  const ckt = Math.cos(k * t);
  const skt = Math.sin(k * t);
  const x = (R - r) * ct + D * ckt;
  const y = (R - r) * st - D * skt;
  return { x, y };
}

function drawSweepingHypotrochoid(ctx, rng, opts) {
  const {
    R,
    r,
    // D(t) = d0 + d1*sin(m1*t + p1) + d2*sin(m2*t + p2)
    d0,
    d1,
    d2,
    m1,
    m2,
    phase1,
    phase2,
    cycles,
    pointsPerCycle,
    rot,
    cx,
    cy,
    scale,
    scaleY,
    stroke,
    alpha,
    lineWidth,
    // adds gentle pencil irregularity without breaking the symmetry
    dJitter = 0.0,
  } = opts;

  const steps = Math.max(800, Math.floor(pointsPerCycle * cycles));
  const T = Math.PI * 2 * cycles;

  ctx.save();
  ctx.strokeStyle = rgba(stroke, 1);
  ctx.globalAlpha = alpha;
  ctx.lineWidth = lineWidth;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';

  ctx.beginPath();
  for (let i = 0; i <= steps; i++) {
    const tt = (i / steps) * T;
    const D =
      d0 +
      d1 * Math.sin(m1 * tt + phase1) +
      d2 * Math.sin(m2 * tt + phase2) +
      (dJitter ? jitter(rng, dJitter) : 0);

    const p = hypotrochoidPoint({ R, r, D, t: tt });
    const pr = rot ? rotatePoint(p.x, p.y, rot) : p;

    const x = cx + pr.x * scale;
    const y = cy + pr.y * scale * scaleY;

    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.stroke();
  ctx.restore();
}

function drawRosette(ctx, opts) {
  const {
    R,
    r,
    D,
    cx,
    cy,
    scale,
    scaleY,
    rot,
    stroke,
    alpha,
    lineWidth,
    steps = 6000,
  } = opts;

  ctx.save();
  ctx.strokeStyle = rgba(stroke, 1);
  ctx.globalAlpha = alpha;
  ctx.lineWidth = lineWidth;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';

  ctx.beginPath();
  for (let i = 0; i <= steps; i++) {
    const t = (i / steps) * Math.PI * 2;
    const p = hypotrochoidPoint({ R, r, D, t });
    const pr = rot ? rotatePoint(p.x, p.y, rot) : p;
    const x = cx + pr.x * scale;
    const y = cy + pr.y * scale * scaleY;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.stroke();
  ctx.restore();
}

// A lightweight helper to stroke the same curve multiple times with tiny changes.
// This mimics pencil re-tracing without resorting to raster effects.
function drawScribbledSweeps(ctx, rng, baseOpts, passes = 2, spread = 0.015) {
  for (let i = 0; i < passes; i++) {
    drawSweepingHypotrochoid(ctx, rng, {
      ...baseOpts,
      rot: (baseOpts.rot || 0) + jitter(rng, spread),
      d0: baseOpts.d0 + jitter(rng, 0.04),
      d1: baseOpts.d1 + jitter(rng, 0.05),
      d2: baseOpts.d2 + jitter(rng, 0.03),
      alpha: baseOpts.alpha * randRange(rng, 0.9, 1.08),
    });
  }
}
