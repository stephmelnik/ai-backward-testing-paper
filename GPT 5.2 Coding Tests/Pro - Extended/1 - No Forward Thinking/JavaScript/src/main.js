function setupCanvas(canvas, size) {
  const dpr = window.devicePixelRatio || 1;
  // Keep an internal fixed resolution so the artwork matches the reference proportions.
  canvas.width = size * dpr;
  canvas.height = size * dpr;
  canvas.style.width = `${size}px`;
  canvas.style.height = `${size}px`;

  const ctx = canvas.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  return ctx;
}

function fitCanvasToWindow(canvas, size) {
  const pad = 20;
  const avail = Math.max(200, Math.min(window.innerWidth, window.innerHeight) - pad);
  const s = Math.min(size, avail);
  canvas.style.width = `${s}px`;
  canvas.style.height = `${s}px`;
}

function render() {
  const canvas = document.getElementById('c');
  const size = CONFIG.CANVAS_SIZE;
  const ctx = setupCanvas(canvas, size);
  fitCanvasToWindow(canvas, size);

  const rng = mulberry32(CONFIG.SEED);

  // Clear
  ctx.clearRect(0, 0, size, size);

  // Layers
  drawPaperBackground(ctx, size, size, rng, CONFIG.PAPER);
  drawFlower(ctx, size, size, rng, CONFIG.FLOWER);
}

function downloadPNG() {
  const canvas = document.getElementById('c');
  const link = document.createElement('a');
  link.download = `procedural-flower-seed-${CONFIG.SEED}.png`;
  link.href = canvas.toDataURL('image/png');
  link.click();
}

window.addEventListener('load', () => {
  render();

  window.addEventListener('resize', () => {
    const canvas = document.getElementById('c');
    fitCanvasToWindow(canvas, CONFIG.CANVAS_SIZE);
  });

  // Press "S" to save a PNG.
  window.addEventListener('keydown', (e) => {
    if (e.key.toLowerCase() === 's') {
      downloadPNG();
    }
    if (e.key.toLowerCase() === 'r') {
      render();
    }
  });
});
