function clamp(v, a, b) {
  return Math.max(a, Math.min(b, v));
}

function lerp(a, b, t) {
  return a + (b - a) * t;
}

function rgba({ r, g, b }, a = 1) {
  const aa = clamp(a, 0, 1);
  return `rgba(${r},${g},${b},${aa})`;
}

function rgb({ r, g, b }) {
  return `rgb(${r},${g},${b})`;
}

function rotatePoint(x, y, angleRad) {
  const c = Math.cos(angleRad);
  const s = Math.sin(angleRad);
  return { x: x * c - y * s, y: x * s + y * c };
}

function withTransform(ctx, fn, { tx = 0, ty = 0, rot = 0, sx = 1, sy = 1 } = {}) {
  ctx.save();
  ctx.translate(tx, ty);
  if (rot) ctx.rotate(rot);
  if (sx !== 1 || sy !== 1) ctx.scale(sx, sy);
  fn();
  ctx.restore();
}
