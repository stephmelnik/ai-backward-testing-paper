(() => {
  const CONFIG = {
    seed: "flower-lines",
    spiro: {
      R: 6,
      r: 1,
      rotation: -Math.PI / 2,
      yScale: 1.04
    },
    background: {
      light: "#faf4ef",
      mid: "#f6eee8",
      deep: "#f3e6de",
      fiber: "rgba(200, 180, 175, 0.08)"
    },
    stem: {
      color: "rgba(110, 120, 200, 0.08)",
      lineWidth: 0.8
    },
    layers: [
      {
        name: "pink-haze",
        color: "rgba(218, 166, 181, 0.18)",
        count: 80,
        d: 3.9,
        scale: 1.0,
        lineWidth: 0.6,
        steps: 1400,
        jitter: 0.14,
        rotationJitter: 0.06,
        wobble: 0.05,
        wobbleFreq: 8,
        centerJitter: 0.03
      },
      {
        name: "blue-sweep",
        color: "rgba(112, 124, 203, 0.22)",
        count: 80,
        d: 3.4,
        scale: 0.98,
        lineWidth: 0.6,
        steps: 1400,
        jitter: 0.12,
        rotationJitter: 0.06,
        wobble: 0.06,
        wobbleFreq: 9,
        centerJitter: 0.025
      },
      {
        name: "petal-veil",
        color: "rgba(220, 178, 193, 0.12)",
        count: 40,
        d: 3.1,
        scale: 0.9,
        lineWidth: 0.5,
        steps: 1200,
        jitter: 0.16,
        rotationJitter: 0.08,
        wobble: 0.09,
        wobbleFreq: 7,
        centerJitter: 0.03
      },
      {
        name: "pink-inner",
        color: "rgba(218, 166, 181, 0.16)",
        count: 60,
        d: 2.8,
        scale: 0.78,
        lineWidth: 0.55,
        steps: 1300,
        jitter: 0.12,
        rotationJitter: 0.05,
        wobble: 0.07,
        wobbleFreq: 11,
        centerJitter: 0.02
      },
      {
        name: "blue-core",
        color: "rgba(106, 118, 198, 0.24)",
        count: 60,
        d: 2.4,
        scale: 0.72,
        lineWidth: 0.55,
        steps: 1300,
        jitter: 0.1,
        rotationJitter: 0.05,
        wobble: 0.08,
        wobbleFreq: 12,
        centerJitter: 0.02
      }
    ]
  };

  const canvas = document.getElementById("flower");
  const ctx = canvas.getContext("2d");

  const rng = mulberry32(seedFromString(CONFIG.seed));

  function resize() {
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    draw(rect.width, rect.height);
  }

  function draw(width, height) {
    ctx.clearRect(0, 0, width, height);
    drawBackground(ctx, width, height, rng);
    drawFlower(ctx, width, height, rng);
  }

  function drawBackground(ctx, width, height, rng) {
    const grad = ctx.createRadialGradient(
      width * 0.35,
      height * 0.2,
      width * 0.1,
      width * 0.5,
      height * 0.5,
      width * 0.85
    );
    grad.addColorStop(0, CONFIG.background.light);
    grad.addColorStop(0.6, CONFIG.background.mid);
    grad.addColorStop(1, CONFIG.background.deep);
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, width, height);

    ctx.save();
    ctx.strokeStyle = CONFIG.background.fiber;
    ctx.lineWidth = 0.5;
    const fibers = Math.floor((width * height) / 8000);
    for (let i = 0; i < fibers; i += 1) {
      const x = rng() * width;
      const y = rng() * height;
      const len = 8 + rng() * 18;
      const angle = rng() * Math.PI * 2;
      ctx.beginPath();
      ctx.moveTo(x, y);
      ctx.lineTo(x + Math.cos(angle) * len, y + Math.sin(angle) * len);
      ctx.stroke();
    }
    ctx.restore();
  }

  function drawFlower(ctx, width, height, rng) {
    const cx = width * 0.5;
    const cy = height * 0.52;
    const radius = Math.min(width, height) * 0.39;

    const maxD = CONFIG.layers.reduce((acc, layer) => Math.max(acc, layer.d), 0);
    const baseScale = radius / ((CONFIG.spiro.R - CONFIG.spiro.r) + maxD);

    const base = {
      cx,
      cy,
      radius,
      scale: baseScale,
      rotation: CONFIG.spiro.rotation,
      yScale: CONFIG.spiro.yScale,
      R: CONFIG.spiro.R,
      r: CONFIG.spiro.r
    };

    CONFIG.layers.forEach((layer) => drawLayer(ctx, rng, layer, base));
    drawCenterStem(ctx, base);
  }

  function drawLayer(ctx, rng, layer, base) {
    ctx.save();
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.strokeStyle = layer.color;
    ctx.lineWidth = layer.lineWidth;

    for (let i = 0; i < layer.count; i += 1) {
      const jitter = (rng() - 0.5) * layer.jitter;
      const d = layer.d * (1 + jitter);
      const scale = base.scale * layer.scale * (1 + jitter * 0.35);
      const rotation = base.rotation + (rng() - 0.5) * layer.rotationJitter;
      const phase = rng() * Math.PI * 2;
      const wobblePhase = rng() * Math.PI * 2;
      const centerShift = (rng() - 0.5) * base.radius * layer.centerJitter;
      const centerShiftY = (rng() - 0.5) * base.radius * layer.centerJitter;

      drawSpiroCurve(ctx, {
        R: base.R,
        r: base.r,
        d,
        scale,
        rotation,
        phase,
        wobble: layer.wobble,
        wobbleFreq: layer.wobbleFreq,
        wobblePhase,
        centerX: base.cx + centerShift,
        centerY: base.cy + centerShiftY,
        steps: layer.steps,
        yScale: base.yScale
      });
    }

    ctx.restore();
  }

  function drawSpiroCurve(ctx, opts) {
    const {
      R,
      r,
      d,
      scale,
      rotation,
      phase,
      wobble,
      wobbleFreq,
      wobblePhase,
      centerX,
      centerY,
      steps,
      yScale
    } = opts;

    const cosRot = Math.cos(rotation);
    const sinRot = Math.sin(rotation);

    ctx.beginPath();
    for (let i = 0; i <= steps; i += 1) {
      const t = (i / steps) * Math.PI * 2 + phase;
      const point = hypotrochoid(t, R, r, d, wobble, wobbleFreq, wobblePhase);
      const xr = point.x * cosRot - point.y * sinRot;
      const yr = point.x * sinRot + point.y * cosRot;
      const x = centerX + xr * scale;
      const y = centerY + yr * scale * yScale;
      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    }
    ctx.stroke();
  }

  function drawCenterStem(ctx, base) {
    ctx.save();
    ctx.strokeStyle = CONFIG.stem.color;
    ctx.lineWidth = CONFIG.stem.lineWidth;
    ctx.beginPath();
    ctx.moveTo(base.cx, base.cy - base.radius * 1.05);
    ctx.lineTo(base.cx, base.cy + base.radius * 1.05);
    ctx.stroke();
    ctx.restore();
  }

  function hypotrochoid(t, R, r, d, wobble, wobbleFreq, wobblePhase) {
    const k = (R - r) / r;
    let x = (R - r) * Math.cos(t) + d * Math.cos(k * t);
    let y = (R - r) * Math.sin(t) - d * Math.sin(k * t);
    if (wobble > 0) {
      const mod = 1 + wobble * Math.sin(t * wobbleFreq + wobblePhase);
      x *= mod;
      y *= mod;
    }
    return { x, y };
  }

  function seedFromString(value) {
    let hash = 1779033703;
    for (let i = 0; i < value.length; i += 1) {
      hash = Math.imul(hash ^ value.charCodeAt(i), 3432918353);
      hash = (hash << 13) | (hash >>> 19);
    }
    return () => {
      hash = Math.imul(hash ^ (hash >>> 16), 2246822507);
      hash = Math.imul(hash ^ (hash >>> 13), 3266489909);
      return (hash ^= hash >>> 16) >>> 0;
    };
  }

  function mulberry32(seedFn) {
    let seed = seedFn();
    return () => {
      seed |= 0;
      seed = (seed + 0x6d2b79f5) | 0;
      let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  window.addEventListener("resize", resize);
  resize();
})();
