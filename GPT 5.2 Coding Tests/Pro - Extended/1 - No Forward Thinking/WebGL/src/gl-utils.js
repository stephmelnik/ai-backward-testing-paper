// Small WebGL2 helpers (no external deps).

function createShader(gl, type, source) {
  const shader = gl.createShader(type);
  if (!shader) throw new Error("createShader returned null");
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    const log = gl.getShaderInfoLog(shader) || "";
    gl.deleteShader(shader);
    throw new Error(`Shader compile failed: ${log}`);
  }
  return shader;
}

function createProgram(gl, vsSource, fsSource) {
  const vs = createShader(gl, gl.VERTEX_SHADER, vsSource);
  const fs = createShader(gl, gl.FRAGMENT_SHADER, fsSource);

  const program = gl.createProgram();
  if (!program) throw new Error("createProgram returned null");

  gl.attachShader(program, vs);
  gl.attachShader(program, fs);
  gl.linkProgram(program);

  gl.deleteShader(vs);
  gl.deleteShader(fs);

  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
    const log = gl.getProgramInfoLog(program) || "";
    gl.deleteProgram(program);
    throw new Error(`Program link failed: ${log}`);
  }
  return program;
}

function resizeCanvasToDisplaySize(canvas, pixelRatio = 1) {
  const dpr = Math.max(1, pixelRatio);
  const displayWidth = Math.floor(canvas.clientWidth * dpr);
  const displayHeight = Math.floor(canvas.clientHeight * dpr);
  if (canvas.width !== displayWidth || canvas.height !== displayHeight) {
    canvas.width = displayWidth;
    canvas.height = displayHeight;
    return true;
  }
  return false;
}

function getUniformLocations(gl, program, names) {
  /** @type {Record<string, WebGLUniformLocation>} */
  const out = {};
  for (const name of names) {
    const loc = gl.getUniformLocation(program, name);
    if (loc === null) {
      // Not fatal: GLSL optimizer may remove unused uniforms.
      continue;
    }
    out[name] = loc;
  }
  return out;
}

function setUniform(gl, loc, value) {
  if (!loc) return;
  if (typeof value === "boolean") {
    gl.uniform1i(loc, value ? 1 : 0);
    return;
  }
  if (typeof value === "number") {
    gl.uniform1f(loc, value);
    return;
  }
  if (Array.isArray(value)) {
    if (value.length === 2) gl.uniform2f(loc, value[0], value[1]);
    else if (value.length === 3) gl.uniform3f(loc, value[0], value[1], value[2]);
    else if (value.length === 4) gl.uniform4f(loc, value[0], value[1], value[2], value[3]);
    else throw new Error(`Unsupported uniform array length: ${value.length}`);
    return;
  }
  throw new Error(`Unsupported uniform type: ${typeof value}`);
}

function setUniformInt(gl, loc, value) {
  if (!loc) return;
  gl.uniform1i(loc, value);
}
