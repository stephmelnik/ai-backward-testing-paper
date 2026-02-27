# Procedural Flower Lines (WebGL2)

This project recreates the provided “flower lines” image using **fully procedural** drawing code:
- No raster images, textures, or pixel copying.
- Strokes are rendered as large sets of **point sprites** (GL_POINTS) with soft falloff + grain.
- The flower geometry is generated mathematically in the **vertex shader**.

## Run

Open `index.html` directly in a WebGL2-capable browser, or use a local server:

```bash
python -m http.server 8000
```

Then open `http://localhost:8000`.

## Edit

Most artistic controls are in:

- `src/params.js`

You can tweak:
- layer colors/alpha
- curve frequencies (`innerFreq`, `loopFreq`)
- number of strokes & points
- paper grain/vignette

Resize the browser window to re-render.

## Export PNG

Press **Ctrl+S** (or **⌘S** on macOS) to download a PNG of the current canvas.
