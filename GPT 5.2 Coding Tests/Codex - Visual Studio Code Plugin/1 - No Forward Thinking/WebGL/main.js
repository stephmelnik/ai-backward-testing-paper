"use strict";

const canvas = document.getElementById("scene");
const fallback = document.getElementById("fallback");
const gl = canvas.getContext("webgl", {
  antialias: true,
  premultipliedAlpha: false,
});

if (!gl) {
  fallback.hidden = false;
  throw new Error("WebGL not available.");
}

const vertexShaderSource = `
  attribute vec2 aPosition;
  attribute vec4 aColor;
  uniform vec2 uScale;
  varying vec4 vColor;

  void main() {
    vec2 pos = aPosition * uScale;
    gl_Position = vec4(pos, 0.0, 1.0);
    vColor = aColor;
  }
`;

const fragmentShaderSource = `
  precision mediump float;
  varying vec4 vColor;

  void main() {
    gl_FragColor = vColor;
  }
`;

function createShader(type, source) {
  const shader = gl.createShader(type);
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    const info = gl.getShaderInfoLog(shader);
    gl.deleteShader(shader);
    throw new Error(info);
  }
  return shader;
}

function createProgram(vsSource, fsSource) {
  const program = gl.createProgram();
  const vs = createShader(gl.VERTEX_SHADER, vsSource);
  const fs = createShader(gl.FRAGMENT_SHADER, fsSource);
  gl.attachShader(program, vs);
  gl.attachShader(program, fs);
  gl.linkProgram(program);
  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
    const info = gl.getProgramInfoLog(program);
    gl.deleteProgram(program);
    throw new Error(info);
  }
  return program;
}

const program = createProgram(vertexShaderSource, fragmentShaderSource);
gl.useProgram(program);

const positionLocation = gl.getAttribLocation(program, "aPosition");
const colorLocation = gl.getAttribLocation(program, "aColor");
const scaleLocation = gl.getUniformLocation(program, "uScale");

const background = [0.973, 0.949, 0.933];

const BASE = {
  R: 1.0,
  r: 1.0 / 7.0,
  steps: 1100,
};

const LAYERS = [
  {
    name: "blue-core",
    color: [0.47, 0.50, 0.82],
    alpha: 0.08,
    count: 90,
    dMin: 0.12,
    dMax: 0.92,
    dBias: 1.35,
    phase: -0.2,
    phaseStep: 0.065,
    phaseJitter: 1.6,
    wobble: 0.02,
    wobbleVar: 0.05,
    wobbleFreq: 12,
    wobbleFreqVar: 6,
    rotation: 0.0,
    scale: 0.52,
    stretchX: 1.0,
    stretchY: 1.16,
    shiftY: -0.08,
    pinch: 0.38,
    pinchStart: 0.05,
    pinchEnd: 0.9,
    twist: 0.22,
    alphaByRadius: true,
    fadeRadius: 0.86,
    seed: 11.0,
  },
  {
    name: "pink-overlay",
    color: [0.92, 0.70, 0.78],
    alpha: 0.07,
    count: 80,
    dMin: 0.1,
    dMax: 0.88,
    dBias: 1.22,
    phase: 0.22,
    phaseStep: 0.072,
    phaseJitter: 1.4,
    wobble: 0.025,
    wobbleVar: 0.045,
    wobbleFreq: 14,
    wobbleFreqVar: 6,
    rotation: 0.05,
    scale: 0.51,
    stretchX: 1.0,
    stretchY: 1.12,
    shiftY: -0.06,
    pinch: 0.34,
    pinchStart: 0.08,
    pinchEnd: 0.88,
    twist: 0.18,
    alphaByRadius: true,
    fadeRadius: 0.84,
    seed: 37.0,
  },
  {
    name: "rim-echo",
    color: [0.86, 0.75, 0.82],
    alpha: 0.045,
    count: 46,
    dMin: 0.76,
    dMax: 1.02,
    dBias: 1.0,
    phase: -0.08,
    phaseStep: 0.11,
    phaseJitter: 1.9,
    wobble: 0.05,
    wobbleVar: 0.04,
    wobbleFreq: 18,
    wobbleFreqVar: 8,
    rotation: 0.0,
    scale: 0.53,
    stretchX: 1.0,
    stretchY: 1.18,
    shiftY: -0.08,
    pinch: 0.3,
    pinchStart: 0.1,
    pinchEnd: 0.92,
    twist: 0.1,
    alphaByRadius: true,
    fadeRadius: 0.9,
    seed: 83.0,
  },
];

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function lerp(a, b, t) {
  return a + (b - a) * t;
}

function smoothstep(a, b, x) {
  const t = clamp((x - a) / (b - a), 0, 1);
  return t * t * (3 - 2 * t);
}

function rand(seed) {
  const s = Math.sin(seed * 12.9898 + 78.233) * 43758.5453;
  return s - Math.floor(s);
}

function spiroPoint(t, R, r, d, phase, wobble, wobbleFreq, wobblePhase) {
  const k = (R - r) / r;
  let x = (R - r) * Math.cos(t) + d * Math.cos(k * t + phase);
  let y = (R - r) * Math.sin(t) - d * Math.sin(k * t + phase);
  if (wobble !== 0) {
    x += wobble * Math.cos(wobbleFreq * t + wobblePhase);
    y += wobble * Math.sin(wobbleFreq * t + wobblePhase);
  }
  return [x, y];
}

function transformPoint(x, y, layer) {
  x *= layer.scale;
  y *= layer.scale;

  if (layer.rotation !== 0) {
    const c = Math.cos(layer.rotation);
    const s = Math.sin(layer.rotation);
    const xr = x * c - y * s;
    const yr = x * s + y * c;
    x = xr;
    y = yr;
  }

  if (layer.twist !== 0) {
    const r = Math.hypot(x, y);
    const angle = Math.atan2(y, x) + layer.twist * (1.0 - r);
    x = Math.cos(angle) * r;
    y = Math.sin(angle) * r;
  }

  x *= layer.stretchX;
  y *= layer.stretchY;

  const pinchT = smoothstep(layer.pinchStart, layer.pinchEnd, -y);
  x *= 1.0 - layer.pinch * pinchT;

  y += layer.shiftY;
  return [x, y];
}

function radialFade(point, layer) {
  const r = Math.hypot(point[0], point[1]);
  const t = clamp(1.0 - r / layer.fadeRadius, 0.0, 1.0);
  return 0.55 + 0.45 * t;
}

function addPolyline(points, layer, positions, colors) {
  const c = layer.color;
  for (let i = 0; i < points.length - 1; i++) {
    const p0 = points[i];
    const p1 = points[i + 1];
    const a0 = layer.alphaByRadius ? layer.alpha * radialFade(p0, layer) : layer.alpha;
    const a1 = layer.alphaByRadius ? layer.alpha * radialFade(p1, layer) : layer.alpha;
    positions.push(p0[0], p0[1], p1[0], p1[1]);
    colors.push(c[0], c[1], c[2], a0, c[0], c[1], c[2], a1);
  }
}

function addSpiroLayer(base, layer, positions, colors) {
  for (let i = 0; i < layer.count; i++) {
    const t = layer.count === 1 ? 0.5 : i / (layer.count - 1);
    const biasT = Math.pow(t, layer.dBias);
    const d = lerp(layer.dMin, layer.dMax, biasT);
    const phase =
      layer.phase +
      i * layer.phaseStep +
      rand(i + layer.seed) * layer.phaseJitter;
    const wobble =
      layer.wobble + rand(i + layer.seed + 3.1) * layer.wobbleVar;
    const wobblePhase = rand(i + layer.seed + 5.4) * Math.PI * 2.0;
    const wobbleFreq =
      layer.wobbleFreq +
      Math.floor(rand(i + layer.seed + 9.7) * layer.wobbleFreqVar);

    const points = [];
    for (let s = 0; s <= base.steps; s++) {
      const angle = (s / base.steps) * Math.PI * 2.0;
      const basePoint = spiroPoint(
        angle,
        base.R,
        base.r,
        d,
        phase,
        wobble,
        wobbleFreq,
        wobblePhase
      );
      points.push(transformPoint(basePoint[0], basePoint[1], layer));
    }

    addPolyline(points, layer, positions, colors);
  }
}

function addStemLine(positions, colors) {
  const color = [0.62, 0.63, 0.8];
  const alpha = 0.05;
  positions.push(0.0, -0.9, 0.0, 0.9);
  colors.push(color[0], color[1], color[2], alpha);
  colors.push(color[0], color[1], color[2], alpha);
}

function buildGeometry() {
  const positions = [];
  const colors = [];

  for (const layer of LAYERS) {
    addSpiroLayer(BASE, layer, positions, colors);
  }

  addStemLine(positions, colors);

  return {
    positions: new Float32Array(positions),
    colors: new Float32Array(colors),
    vertexCount: positions.length / 2,
  };
}

const geometry = buildGeometry();

const positionBuffer = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
gl.bufferData(gl.ARRAY_BUFFER, geometry.positions, gl.STATIC_DRAW);
gl.enableVertexAttribArray(positionLocation);
gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);

const colorBuffer = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER, colorBuffer);
gl.bufferData(gl.ARRAY_BUFFER, geometry.colors, gl.STATIC_DRAW);
gl.enableVertexAttribArray(colorLocation);
gl.vertexAttribPointer(colorLocation, 4, gl.FLOAT, false, 0, 0);

gl.enable(gl.BLEND);
gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

function resize() {
  const dpr = window.devicePixelRatio || 1;
  const width = Math.round(canvas.clientWidth * dpr);
  const height = Math.round(canvas.clientHeight * dpr);
  if (canvas.width !== width || canvas.height !== height) {
    canvas.width = width;
    canvas.height = height;
  }

  gl.viewport(0, 0, canvas.width, canvas.height);
  const aspect = canvas.width / canvas.height;
  let scaleX = 1.0;
  let scaleY = 1.0;
  if (aspect > 1) {
    scaleX = 1.0 / aspect;
  } else {
    scaleY = aspect;
  }
  gl.uniform2f(scaleLocation, scaleX, scaleY);
}

function draw() {
  resize();
  gl.clearColor(background[0], background[1], background[2], 1.0);
  gl.clear(gl.COLOR_BUFFER_BIT);
  gl.drawArrays(gl.LINES, 0, geometry.vertexCount);
}

window.addEventListener("resize", draw);
draw();
