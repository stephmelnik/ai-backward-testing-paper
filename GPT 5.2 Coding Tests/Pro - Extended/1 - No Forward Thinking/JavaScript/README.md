# Procedural Flower Lines (Canvas 2D)

This folder contains a fully procedural (no image assets) JavaScript recreation of the provided flower-line artwork.

## Run

Open `index.html` directly in your browser.

Optional: if you want to serve it over HTTP:

```bash
cd procedural-flower
python3 -m http.server 8000
```

Then open:

- `http://localhost:8000`

## Controls

- **S** — save a PNG
- **R** — re-render

## Edit

All important knobs are in:

- `src/config.js`

Notable parameters:

- `SEED` — deterministic texture variation
- `FLOWER.radius` and `FLOWER.aspectY` — overall size / vertical stretch
- `FLOWER.guilloche.layers.*.underlay` — the long sweeping spirograph passes
- `FLOWER.guilloche.layers.*.veins` — the leaf-vein fan curves
- `PAPER.grain` — paper texture density

## File structure

- `index.html` — minimal page with a canvas
- `src/main.js` — render entry point
- `src/draw/background.js` — paper texture + vignette
- `src/draw/guilloche.js` — hypotrochoid (spirograph) primitives
- `src/draw/flower.js` — named layers/components composing the final flower
