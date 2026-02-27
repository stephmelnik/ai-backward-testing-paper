function mix(a, b, t) {
  return {
    r: Math.round(a.r + (b.r - a.r) * t),
    g: Math.round(a.g + (b.g - a.g) * t),
    b: Math.round(a.b + (b.b - a.b) * t),
  };
}

function drawPaperBackground(ctx, w, h, rng, paperCfg) {
  const base = paperCfg.base;

  // Base fill
  ctx.save();
  ctx.globalCompositeOperation = 'source-over';
  ctx.fillStyle = rgb(base);
  ctx.fillRect(0, 0, w, h);

  // Subtle vignette
  const cx = w * 0.5;
  const cy = h * 0.5;
  const r0 = 0;
  const r1 = Math.max(w, h) * paperCfg.vignetteRadius;
  const g = ctx.createRadialGradient(cx, cy, r0, cx, cy, r1);

  const edge = mix(base, { r: base.r - 18, g: base.g - 18, b: base.b - 20 }, 1);
  g.addColorStop(0, rgba(base, 0));
  g.addColorStop(0.55, rgba(base, 0.0));
  g.addColorStop(1, rgba(edge, clamp(paperCfg.vignetteStrength, 0, 0.25)));

  ctx.fillStyle = g;
  ctx.fillRect(0, 0, w, h);

  // Paper grain: tiny translucent dots
  const { dots, dotRadius, dotAlpha } = paperCfg.grain;
  for (let i = 0; i < dots; i++) {
    const x = rng() * w;
    const y = rng() * h;
    const rr = randRange(rng, dotRadius[0], dotRadius[1]);

    // Tiny warm/cool variation
    const c = {
      r: base.r + jitter(rng, 6),
      g: base.g + jitter(rng, 6),
      b: base.b + jitter(rng, 6),
    };

    ctx.fillStyle = rgba(c, randRange(rng, dotAlpha[0], dotAlpha[1]));
    ctx.beginPath();
    ctx.arc(x, y, rr, 0, Math.PI * 2);
    ctx.fill();
  }

  // Paper fibers: faint short strokes
  const { fibers, fiberLen, fiberAlpha } = paperCfg.grain;
  ctx.lineWidth = 0.6;
  ctx.lineCap = 'round';
  for (let i = 0; i < fibers; i++) {
    const x = rng() * w;
    const y = rng() * h;
    const len = randRange(rng, fiberLen[0], fiberLen[1]);
    const ang = randRange(rng, 0, Math.PI * 2);

    const x2 = x + Math.cos(ang) * len;
    const y2 = y + Math.sin(ang) * len;

    const c = {
      r: base.r + jitter(rng, 10),
      g: base.g + jitter(rng, 10),
      b: base.b + jitter(rng, 10),
    };

    ctx.strokeStyle = rgba(c, randRange(rng, fiberAlpha[0], fiberAlpha[1]));
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x2, y2);
    ctx.stroke();
  }

  ctx.restore();
}
