// Setup
const engine = new AttractorEngine();
const renderer = new Renderer('canvas');

// UI Elements
const ui = {
    muSlider: document.getElementById('mu-slider'),
    muDisplay: document.getElementById('mu-display'),
    detailSlider: document.getElementById('detail-slider'),
    btn: document.getElementById('btn-render')
};

function renderFrame() {
    // 1. Get Settings
    const layerCount = parseInt(ui.detailSlider.value);
    
    // Points per layer: 
    // Higher values create smoother, longer continuous lines.
    // 2000 is usually enough for a full loop in this regime.
    const pointsPerLayer = 2500; 

    // 2. Compute
    const layers = engine.generateLayers(layerCount, pointsPerLayer);
    
    // 3. Draw
    renderer.draw(layers);
}

// Event Listeners
ui.muSlider.addEventListener('input', (e) => {
    const val = parseFloat(e.target.value);
    engine.setMu(val);
    ui.muDisplay.textContent = val.toFixed(3);
    
    // Use requestAnimationFrame for smooth interaction
    requestAnimationFrame(renderFrame);
});

ui.detailSlider.addEventListener('input', () => {
    requestAnimationFrame(renderFrame);
});

ui.btn.addEventListener('click', renderFrame);

// Handle Window Resize
let resizeTimeout;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(renderFrame, 200);
});

// Initial Render
renderFrame();