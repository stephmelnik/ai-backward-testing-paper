# Procedural Flower Line Art

This project generates a lotus-like **guilloché / pencil-line** flower *procedurally* using
Python + NumPy + Matplotlib. No external images or textures are used.

The look is built from:
- **Open teardrop-side arcs** (petal “veins”)
- **Nested closed teardrop loops** (leaflet/heart structures)
- **Scalloped outlines** (small loop offsets along the border)
- Two lightly rotated color layers (pink + blue)

## Files

- `generate_flower.py` — CLI to render the artwork.
- `procedural_flower/`
  - `geometry.py` — rotation helper
  - `curves.py` — curve primitives (teardrop loop, teardrop side arc, scallops)
  - `petal.py` — petal builders (veins, nested loops, scalloped outline)
  - `flower.py` — assembles the 8-petal flower + inner petals
  - `render.py` — renderer + background vignette
  - `defaults.py` — default params and stroke styles

## Run

From this folder:

```bash
python generate_flower.py --out generated_flower.png
```

Optional tweaks:

```bash
python generate_flower.py --out generated_flower.png --size 2048 --dpi 256 --vlim 1.7 --vignette 0.10
```

## Editing tips

- Adjust overall proportions in `procedural_flower/flower.py` (`FlowerParams`).
- Adjust line weight / transparency in `procedural_flower/defaults.py`.
- Adjust petal fill complexity in `procedural_flower/petal.py`:
  - `petal_veins_teardrop()` for the main open arc families
  - `petal_loops()` for nested closed loops
  - `petal_outline()` for scalloped edging
