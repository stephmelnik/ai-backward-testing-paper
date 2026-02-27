// GLSL shader sources (WebGL2 / GLSL ES 3.00)

const bgVert = `#version 300 es
precision highp float;

out vec2 vUv;

void main() {
  // Full-screen triangle (no vertex buffers needed).
  vec2 p;
  if (gl_VertexID == 0) p = vec2(-1.0, -1.0);
  else if (gl_VertexID == 1) p = vec2( 3.0, -1.0);
  else p = vec2(-1.0,  3.0);

  vUv = 0.5 * (p + 1.0);
  gl_Position = vec4(p, 0.0, 1.0);
}
`;

const bgFrag = `#version 300 es
precision highp float;

in vec2 vUv;
out vec4 outColor;

uniform vec2 uResolution;

uniform vec3 uPaperBase;
uniform vec3 uPaperCool;

uniform float uVignetteStrength;
uniform float uVignettePower;

uniform float uGrainStrength;
uniform float uGrainScale;

uniform float uFiberStrength;
uniform float uFiberScale;
uniform vec2 uFiberAniso;

// Hash / noise helpers (simple and fast)
float hash11(float p) {
  p = fract(p * 0.1031);
  p *= p + 33.33;
  p *= p + p;
  return fract(p);
}

float hash12(vec2 p) {
  vec3 p3 = fract(vec3(p.xyx) * 0.1031);
  p3 += dot(p3, p3.yzx + 33.33);
  return fract((p3.x + p3.y) * p3.z);
}

float valueNoise(vec2 p) {
  vec2 i = floor(p);
  vec2 f = fract(p);
  float a = hash12(i);
  float b = hash12(i + vec2(1.0, 0.0));
  float c = hash12(i + vec2(0.0, 1.0));
  float d = hash12(i + vec2(1.0, 1.0));
  vec2 u = f * f * (3.0 - 2.0 * f);
  return mix(a, b, u.x) + (c - a) * u.y * (1.0 - u.x) + (d - b) * u.x * u.y;
}

void main() {
  // Normalized centered coords (-1..1) with aspect compensation
  vec2 p = vUv * 2.0 - 1.0;
  float aspect = uResolution.x / max(1.0, uResolution.y);
  p.x *= aspect;

  // Paper base + subtle center coolness
  float center = exp(-dot(p, p) * 0.8);
  vec3 col = mix(uPaperBase, uPaperCool, 0.12 * center);

  // Vignette
  float r = length(p);
  float v = pow(clamp(1.0 - r, 0.0, 1.0), uVignettePower);
  col *= 1.0 - uVignetteStrength * (1.0 - v);

  // Grain (fine)
  vec2 gUv = gl_FragCoord.xy / max(uResolution.y, 1.0);
  float g = hash12(gUv * (650.0 * uGrainScale) + 13.7);
  col += (g - 0.5) * uGrainStrength;

  // Fibers (low-frequency, anisotropic)
  vec2 fUv = gl_FragCoord.xy / max(uResolution.y, 1.0);
  fUv *= uFiberAniso;
  float f1 = valueNoise(fUv * (18.0 * uFiberScale));
  float f2 = valueNoise(fUv * (42.0 * uFiberScale) + 9.3);
  float fibers = (f1 * 0.6 + f2 * 0.4);
  col += (fibers - 0.5) * uFiberStrength;

  outColor = vec4(col, 1.0);
}
`;

const strokesVert = `#version 300 es
precision highp float;

out vec3 vColor;
out float vAlpha;
out float vSoftness;
out float vGrain;
out float vSeed;

uniform vec2 uResolution;
uniform float uAspect;

uniform int uShapeType; // 0 = flower, 1 = axis

uniform vec3 uColor;
uniform float uAlpha;
uniform float uPointSize; // in physical pixels (already DPR scaled)

uniform int uPointsPerStroke;
uniform float uTMax;

uniform float uGlobalScale;
uniform vec2 uOffset;

// Flower params
uniform float uPhase;
uniform float uPhaseStep;

uniform float uPetalN;
uniform float uPetalPower;
uniform float uDiagScale;
uniform float uDiagPower;

uniform float uInnerFreq;
uniform float uInnerFreqStep;
uniform float uModAmp;
uniform float uModWobble;
uniform float uOscMin;

uniform float uLoopFreq;
uniform float uLoopFreqStep;
uniform float uLoopAmp;

uniform float uYScale;
uniform float uYWarp;

// Axis params
uniform float uAxisWidth;
uniform float uAxisYMin;
uniform float uAxisYMax;

uniform float uSoftness;
uniform float uGrain;

float hash11(float p) {
  p = fract(p * 0.1031);
  p *= p + 33.33;
  p *= p + p;
  return fract(p);
}

vec2 flowerPos(float t, float strokeIdx) {
  float s = strokeIdx;

  float theta = t;
  float phase = uPhase + uPhaseStep * s;
  theta += phase;

  // 8-petal rose envelope: abs(cos(4*theta)) -> 8 petals
  float base = abs(cos(uPetalN * theta));
  base = pow(base, uPetalPower);

  // Shape the diagonal petals slightly differently
  float diag = abs(cos(2.0 * theta));
  float diagW = pow(diag, uDiagPower);
  float diagScale = mix(uDiagScale, 1.0, diagW);

  float r = base * (0.25 + 0.75 * diagScale);

  // Radial “breathing”: returns the stroke back towards the center often,
  // creating the fan-like texture seen in the reference image.
  float f = uInnerFreq + uInnerFreqStep * s;
  float wob = uModWobble * sin(2.0 * theta);

  // Oscillates in [uOscMin, 1]. Using abs(sin(...)) keeps everything positive
  // while still collapsing back towards the center.
  float osc = mix(uOscMin, 1.0, abs(sin(f * t + wob)));
  r *= osc;

  // A small additional modulation avoids perfectly even banding.
  r *= 1.0 + (0.12 * uModAmp) * cos((f + 2.0) * theta + 0.6 * sin(3.0 * theta));

  // Polar -> Cartesian (angle measured from +Y axis for the upright look)
  vec2 p = vec2(r * sin(theta), r * cos(theta));

  // Scalloped edge micro-loops
  float lf = uLoopFreq + uLoopFreqStep * s;
  float lp = 1.2 * cos(theta + 0.7 * s);
  p += uLoopAmp * vec2(
    sin(lf * t + lp),
    cos(lf * t + 0.8 * sin(theta))
  );

  // Vertical shaping / skew (makes the lower petals feel heavier like the reference)
  p.y *= uYScale;
  p.y *= 1.0 + uYWarp * p.y;

  return p;
}

vec2 axisPos(float t01, float strokeIdx) {
  float s = strokeIdx;

  float y = mix(uAxisYMin, uAxisYMax, t01);

  // Tiny deterministic x wobble so the axis isn't perfectly “computer straight”
  float wob = (hash11(91.7 + s * 13.1) - 0.5) * 2.0;
  float x = wob * uAxisWidth;

  return vec2(x, y);
}

void main() {
  int stroke = gl_VertexID / uPointsPerStroke;
  int idx = gl_VertexID - stroke * uPointsPerStroke;

  float t01 = float(idx) / float(max(uPointsPerStroke - 1, 1));
  float t = t01 * uTMax;

  vec2 p;
  if (uShapeType == 1) {
    p = axisPos(t01, float(stroke));
  } else {
    p = flowerPos(t, float(stroke));
  }

  // Scale and offset in “art space”, then aspect-correct for clip space.
  p = p * uGlobalScale + uOffset;
  p.x /= uAspect;

  gl_Position = vec4(p, 0.0, 1.0);

  // Slight size variation gives a pencil-like texture without breaking symmetry.
  float sizeJit = 0.90 + 0.22 * hash11(float(gl_VertexID) * 0.017 + float(stroke) * 3.1);
  gl_PointSize = uPointSize * sizeJit;

  vColor = uColor;

  // Modulate alpha very slightly per point (grain).
  float aJit = 0.78 + 0.32 * hash11(float(gl_VertexID) * 0.031 + 7.7);
  vAlpha = uAlpha * aJit;

  vSoftness = uSoftness;
  vGrain = uGrain;
  vSeed = hash11(float(gl_VertexID) * 0.113 + float(stroke) * 19.7);
}
`;

const strokesFrag = `#version 300 es
precision highp float;

in vec3 vColor;
in float vAlpha;
in float vSoftness;
in float vGrain;
in float vSeed;

out vec4 outColor;

float hash12(vec2 p) {
  vec3 p3 = fract(vec3(p.xyx) * 0.1031);
  p3 += dot(p3, p3.yzx + 33.33);
  return fract((p3.x + p3.y) * p3.z);
}

void main() {
  // Soft round point sprite (Gaussian-like falloff).
  vec2 pc = gl_PointCoord - 0.5;
  float d2 = dot(pc, pc);

  // Fade faster near the edge of the sprite.
  float a = exp(-d2 * vSoftness);

  // Extra edge clamp so points don't look like fuzzy dots.
  a *= smoothstep(0.26, 0.0, sqrt(d2));

  // Screen-space grain (paper + pencil).
  float g = hash12(gl_FragCoord.xy * 0.65 + vSeed * 91.7);
  float grain = mix(1.0 - vGrain, 1.0 + 0.22 * vGrain, g);
  a *= grain;

  a *= vAlpha;

  // Premultiply for nicer blending.
  outColor = vec4(vColor * a, a);
}
`;
