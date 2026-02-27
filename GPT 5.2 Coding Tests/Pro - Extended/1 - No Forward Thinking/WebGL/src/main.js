const canvas = /** @type {HTMLCanvasElement} */ (document.getElementById('c'));

const gl = canvas.getContext('webgl2', {
  antialias: true,
  alpha: false,
  premultipliedAlpha: false,
  preserveDrawingBuffer: true, // allows easy PNG export
});

if (!gl) {
  throw new Error('WebGL2 not supported in this browser.');
}

// Programs
const bgProgram = createProgram(gl, bgVert, bgFrag);
const strokesProgram = createProgram(gl, strokesVert, strokesFrag);

// VAOs (no vertex buffers needed; we use gl_VertexID)
const bgVao = gl.createVertexArray();
const strokesVao = gl.createVertexArray();

// Uniform locations
const bgUniforms = getUniformLocations(gl, bgProgram, [
  'uResolution',
  'uPaperBase',
  'uPaperCool',
  'uVignetteStrength',
  'uVignettePower',
  'uGrainStrength',
  'uGrainScale',
  'uFiberStrength',
  'uFiberScale',
  'uFiberAniso',
]);

const strokeUniforms = getUniformLocations(gl, strokesProgram, [
  'uResolution',
  'uAspect',

  'uShapeType',

  'uColor',
  'uAlpha',
  'uPointSize',

  'uPointsPerStroke',
  'uTMax',

  'uGlobalScale',
  'uOffset',

  'uPhase',
  'uPhaseStep',

  'uPetalN',
  'uPetalPower',
  'uDiagScale',
  'uDiagPower',

  'uInnerFreq',
  'uInnerFreqStep',
  'uModAmp',
  'uModWobble',
  'uOscMin',

  'uLoopFreq',
  'uLoopFreqStep',
  'uLoopAmp',

  'uYScale',
  'uYWarp',

  'uAxisWidth',
  'uAxisYMin',
  'uAxisYMax',

  'uSoftness',
  'uGrain',
]);

function draw() {
  const dpr = Math.max(1, window.devicePixelRatio) * (CONFIG.canvas?.resolutionScale ?? 1);
  const resized = resizeCanvasToDisplaySize(canvas, dpr);
  if (resized) {
    gl.viewport(0, 0, canvas.width, canvas.height);
  } else {
    gl.viewport(0, 0, canvas.width, canvas.height);
  }

  const aspect = canvas.width / Math.max(1, canvas.height);

  gl.disable(gl.DEPTH_TEST);
  gl.disable(gl.CULL_FACE);

  // --- Background pass ---
  gl.useProgram(bgProgram);
  gl.bindVertexArray(bgVao);

  setUniform(gl, bgUniforms.uResolution, [canvas.width, canvas.height]);
  setUniform(gl, bgUniforms.uPaperBase, CONFIG.background.paperBase);
  setUniform(gl, bgUniforms.uPaperCool, CONFIG.background.paperCool);
  setUniform(gl, bgUniforms.uVignetteStrength, CONFIG.background.vignetteStrength);
  setUniform(gl, bgUniforms.uVignettePower, CONFIG.background.vignettePower);
  setUniform(gl, bgUniforms.uGrainStrength, CONFIG.background.grainStrength);
  setUniform(gl, bgUniforms.uGrainScale, CONFIG.background.grainScale);
  setUniform(gl, bgUniforms.uFiberStrength, CONFIG.background.fiberStrength);
  setUniform(gl, bgUniforms.uFiberScale, CONFIG.background.fiberScale);
  setUniform(gl, bgUniforms.uFiberAniso, CONFIG.background.fiberAniso);

  gl.disable(gl.BLEND);
  gl.drawArrays(gl.TRIANGLES, 0, 3);

  // --- Strokes pass ---
  gl.useProgram(strokesProgram);
  gl.bindVertexArray(strokesVao);

  setUniform(gl, strokeUniforms.uResolution, [canvas.width, canvas.height]);
  setUniform(gl, strokeUniforms.uAspect, aspect);

  // Premultiplied alpha blending (we premultiply in the fragment shader)
  gl.enable(gl.BLEND);
  gl.blendEquation(gl.FUNC_ADD);
  gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);

  for (const layer of CONFIG.layers) {
    const strokes = Math.max(1, layer.strokes | 0);
    const pointsPerStroke = Math.max(2, layer.pointsPerStroke | 0);
    const count = strokes * pointsPerStroke;

    // Common
    setUniform(gl, strokeUniforms.uColor, layer.color);
    setUniform(gl, strokeUniforms.uAlpha, layer.alpha);

    // Point size: configured in CSS pixels; convert to physical pixels.
    setUniform(gl, strokeUniforms.uPointSize, layer.pointSize * dpr);

    setUniformInt(gl, strokeUniforms.uPointsPerStroke, pointsPerStroke);
    setUniform(gl, strokeUniforms.uTMax, layer.tMax ?? 1.0);

    setUniform(gl, strokeUniforms.uGlobalScale, layer.globalScale ?? 1.0);
    setUniform(gl, strokeUniforms.uOffset, layer.offset ?? [0, 0]);

    setUniform(gl, strokeUniforms.uSoftness, layer.softness ?? 10.0);
    setUniform(gl, strokeUniforms.uGrain, layer.grain ?? 0.25);

    if (layer.type === 'axis') {
      setUniformInt(gl, strokeUniforms.uShapeType, 1);
      setUniform(gl, strokeUniforms.uAxisWidth, layer.axisWidth ?? 0.002);
      setUniform(gl, strokeUniforms.uAxisYMin, layer.axisYMin ?? -1.2);
      setUniform(gl, strokeUniforms.uAxisYMax, layer.axisYMax ?? 1.2);
    } else {
      setUniformInt(gl, strokeUniforms.uShapeType, 0);

      setUniform(gl, strokeUniforms.uPhase, layer.phase ?? 0.0);
      setUniform(gl, strokeUniforms.uPhaseStep, layer.phaseStep ?? 0.12);

      setUniform(gl, strokeUniforms.uPetalN, layer.petalN ?? 4.0);
      setUniform(gl, strokeUniforms.uPetalPower, layer.petalPower ?? 0.65);
      setUniform(gl, strokeUniforms.uDiagScale, layer.diagScale ?? 0.92);
      setUniform(gl, strokeUniforms.uDiagPower, layer.diagPower ?? 0.75);

      setUniform(gl, strokeUniforms.uInnerFreq, layer.innerFreq ?? 7.0);
      setUniform(gl, strokeUniforms.uInnerFreqStep, layer.innerFreqStep ?? 0.08);
      setUniform(gl, strokeUniforms.uModAmp, layer.modAmp ?? 0.33);
      setUniform(gl, strokeUniforms.uModWobble, layer.modWobble ?? 0.45);
      setUniform(gl, strokeUniforms.uOscMin, layer.oscMin ?? 0.42);

      setUniform(gl, strokeUniforms.uLoopFreq, layer.loopFreq ?? 75.0);
      setUniform(gl, strokeUniforms.uLoopFreqStep, layer.loopFreqStep ?? 0.6);
      setUniform(gl, strokeUniforms.uLoopAmp, layer.loopAmp ?? 0.04);

      setUniform(gl, strokeUniforms.uYScale, layer.yScale ?? 1.0);
      setUniform(gl, strokeUniforms.uYWarp, layer.yWarp ?? -0.18);
    }

    gl.drawArrays(gl.POINTS, 0, count);
  }

  gl.bindVertexArray(null);
}

function downloadPng() {
  const a = document.createElement('a');
  a.download = 'procedural-flower.png';
  a.href = canvas.toDataURL('image/png');
  a.click();
}

window.addEventListener('resize', () => draw(), { passive: true });
window.addEventListener('keydown', (e) => {
  if ((e.key === 's' || e.key === 'S') && (e.ctrlKey || e.metaKey)) {
    e.preventDefault();
    downloadPng();
  }
});

draw();
