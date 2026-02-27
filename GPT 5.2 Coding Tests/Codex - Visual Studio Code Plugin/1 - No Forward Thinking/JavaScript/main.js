const canvas = document.getElementById("art");
const ctx = canvas.getContext("2d");

const palette = {
  warm: [235, 170, 186],
  warmLight: [245, 204, 215],
  cool: [103, 113, 190],
  coolLight: [150, 157, 208],
};

function rgba(rgb, alpha) {
  return `rgba(${rgb[0]},${rgb[1]},${rgb[2]},${alpha})`;
}

function lerp(a, b, t) {
  return a + (b - a) * t;
}

function createRng(seed) {
  let t = seed >>> 0;
  return function () {
    t += 0x6d2b79f5;
    let r = Math.imul(t ^ (t >>> 15), t | 1);
    r ^= r + Math.imul(r ^ (r >>> 7), r | 61);
    return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
  };
}

function drawBackground(size, cx, cy) {
  const gradient = ctx.createRadialGradient(cx, cy, size * 0.1, cx, cy, size * 0.7);
  gradient.addColorStop(0, "#f9f1ee");
  gradient.addColorStop(1, "#f6efec");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, size, size);
}

function drawPetalPass(cx, cy, baseLen, petal, options) {
  const rng = createRng(options.seed);
  const count = options.count || 24;
  const steps = options.steps || 220;
  const strokeWidth = options.strokeWidth || 0.7;
  const lengthScale = options.lengthScale || 1;
  const widthScale = options.widthScale || 1;

  const powerRange = options.powerRange || [0.9, 1.5];
  const rippleRange = options.rippleRange || [0.04, 0.14];
  const rippleFreqRange = options.rippleFreqRange || [4, 10];
  const twistRange = options.twistRange || [0.04, 0.16];
  const wobbleRange = options.wobbleRange || [0.0, 0.12];
  const driftRange = options.driftRange || [-0.12, 0.12];

  for (let i = 0; i < count; i += 1) {
    const power = lerp(powerRange[0], powerRange[1], rng());
    const ripple = lerp(rippleRange[0], rippleRange[1], rng());
    const rippleFreq = Math.round(lerp(rippleFreqRange[0], rippleFreqRange[1], rng()));
    const twist = lerp(twistRange[0], twistRange[1], rng());
    const wobble = lerp(wobbleRange[0], wobbleRange[1], rng());
    const drift = lerp(driftRange[0], driftRange[1], rng());
    const phase = rng() * Math.PI * 2;
    const scale = lerp(0.68, 1.05, rng());
    const widthJitter = lerp(0.82, 1.1, rng());

    const length = baseLen * petal.len * lengthScale * scale;
    const width = petal.width * widthScale * widthJitter;
    const angle = petal.angle + petal.bias * lerp(0.2, 1, rng());

    ctx.strokeStyle = rgba(options.color, options.alpha * lerp(0.75, 1.1, rng()));
    ctx.lineWidth = strokeWidth * lerp(0.7, 1.2, rng());
    ctx.beginPath();

    for (let s = 0; s <= steps; s += 1) {
      const t = (s / steps) * Math.PI * 2;
      const base = Math.pow(Math.sin(t / 2), power);
      const r = length * base * (1 + ripple * Math.sin(rippleFreq * t + phase));
      const theta =
        angle +
        width * Math.sin(t) +
        twist * Math.sin(2 * t + phase) +
        wobble * Math.sin(3 * t + phase * 0.7);
      const driftAmt = drift * r * Math.sin(2 * t + phase);
      const x = cx + r * Math.cos(theta) + driftAmt * Math.cos(theta + Math.PI / 2);
      const y = cy + r * Math.sin(theta) + driftAmt * Math.sin(theta + Math.PI / 2);
      if (s === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    }
    ctx.stroke();
  }
}

function drawPetalComposite(cx, cy, baseLen, petal, index) {
  const seedBase = 9000 + index * 97;
  const warmAlpha = 0.08 + 0.1 * petal.warm;
  const coolAlpha = 0.08 + 0.08 * (1 - petal.warm);
  const stroke = Math.max(0.35, baseLen * 0.0017);

  drawPetalPass(cx, cy, baseLen, petal, {
    seed: seedBase + 1,
    count: 26,
    color: palette.warmLight,
    alpha: warmAlpha * 0.7,
    strokeWidth: stroke * 0.85,
    lengthScale: 1.07,
    widthScale: 1.15,
    rippleRange: [0.06, 0.2],
    rippleFreqRange: [8, 14],
    twistRange: [0.06, 0.2],
    powerRange: [0.9, 1.4],
    driftRange: [-0.16, 0.16],
    wobbleRange: [0.02, 0.14],
  });

  drawPetalPass(cx, cy, baseLen, petal, {
    seed: seedBase + 13,
    count: 38,
    color: palette.cool,
    alpha: coolAlpha,
    strokeWidth: stroke,
    lengthScale: 0.98,
    widthScale: 1,
    rippleRange: [0.04, 0.16],
    rippleFreqRange: [4, 10],
    twistRange: [0.04, 0.16],
    powerRange: [0.85, 1.5],
    driftRange: [-0.14, 0.14],
    wobbleRange: [0.0, 0.12],
  });

  drawPetalPass(cx, cy, baseLen, petal, {
    seed: seedBase + 31,
    count: 30,
    color: palette.warm,
    alpha: warmAlpha,
    strokeWidth: stroke * 0.9,
    lengthScale: 0.92,
    widthScale: 0.95,
    rippleRange: [0.03, 0.14],
    rippleFreqRange: [4, 9],
    twistRange: [0.03, 0.16],
    powerRange: [0.9, 1.4],
    driftRange: [-0.12, 0.12],
    wobbleRange: [0.0, 0.1],
  });

  drawPetalPass(cx, cy, baseLen, petal, {
    seed: seedBase + 49,
    count: 16,
    color: palette.coolLight,
    alpha: coolAlpha * 0.7,
    strokeWidth: stroke * 0.8,
    lengthScale: 1,
    widthScale: 1.05,
    rippleRange: [0.05, 0.16],
    rippleFreqRange: [6, 12],
    twistRange: [0.04, 0.14],
    powerRange: [1.0, 1.5],
    driftRange: [-0.1, 0.1],
    wobbleRange: [0.0, 0.1],
  });
}

function drawCore(cx, cy, baseLen, petals) {
  petals.forEach((petal, idx) => {
    const innerPetal = {
      ...petal,
      len: petal.len * 0.58,
      width: petal.width * 0.62,
    };
    drawPetalPass(cx, cy, baseLen, innerPetal, {
      seed: 4000 + idx * 37,
      count: 18,
      color: palette.cool,
      alpha: 0.12,
      strokeWidth: Math.max(0.28, baseLen * 0.0013),
      lengthScale: 0.9,
      widthScale: 1,
      rippleRange: [0.04, 0.12],
      rippleFreqRange: [5, 9],
      twistRange: [0.04, 0.12],
      powerRange: [0.9, 1.4],
      driftRange: [-0.08, 0.08],
      wobbleRange: [0.0, 0.08],
    });
  });
}

function drawAxis(cx, cy, size) {
  ctx.lineWidth = Math.max(0.3, size * 0.0007);
  ctx.strokeStyle = rgba(palette.coolLight, 0.16);
  ctx.beginPath();
  ctx.moveTo(cx, cy - size * 0.46);
  ctx.lineTo(cx, cy + size * 0.48);
  ctx.stroke();

  ctx.strokeStyle = rgba(palette.warmLight, 0.12);
  ctx.beginPath();
  ctx.moveTo(cx, cy - size * 0.42);
  ctx.lineTo(cx, cy + size * 0.46);
  ctx.stroke();
}

function drawScene(size) {
  const cx = size * 0.5;
  const cy = size * 0.53;
  const baseLen = size * 0.43;

  drawBackground(size, cx, cy);

  ctx.lineJoin = "round";
  ctx.lineCap = "round";

  const petals = [
    { name: "top", angle: -Math.PI / 2, len: 1.02, width: 0.55, bias: 0, warm: 0.85 },
    { name: "upperLeft", angle: -Math.PI / 2 - 0.7, len: 0.95, width: 0.72, bias: -0.03, warm: 0.55 },
    { name: "upperRight", angle: -Math.PI / 2 + 0.7, len: 0.95, width: 0.72, bias: 0.03, warm: 0.55 },
    { name: "midLeft", angle: -Math.PI / 2 - 1.35, len: 0.88, width: 0.84, bias: -0.05, warm: 0.45 },
    { name: "midRight", angle: -Math.PI / 2 + 1.35, len: 0.88, width: 0.84, bias: 0.05, warm: 0.45 },
    { name: "lowerLeft", angle: -Math.PI / 2 - 2.05, len: 0.82, width: 0.88, bias: -0.04, warm: 0.6 },
    { name: "lowerRight", angle: -Math.PI / 2 + 2.05, len: 0.82, width: 0.88, bias: 0.04, warm: 0.6 },
    { name: "bottom", angle: Math.PI / 2, len: 0.92, width: 0.62, bias: 0, warm: 0.75 },
  ];

  petals.forEach((petal, index) => {
    drawPetalComposite(cx, cy, baseLen, petal, index);
  });

  drawCore(cx, cy, baseLen, petals);
  drawAxis(cx, cy, size);
}

function resize() {
  const padding = 24;
  const maxSize = 1200;
  const size = Math.max(
    320,
    Math.min(maxSize, window.innerWidth - padding * 2, window.innerHeight - padding * 2)
  );
  const dpr = window.devicePixelRatio || 1;
  canvas.width = size * dpr;
  canvas.height = size * dpr;
  canvas.style.width = `${size}px`;
  canvas.style.height = `${size}px`;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  drawScene(size);
}

window.addEventListener("resize", resize);
resize();
