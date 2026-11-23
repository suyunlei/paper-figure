# Architectural Studio Editorial Design System (中灰白线建筑编辑风)

Reference standard distilled from *VoxVista* (*CEUS* v6/v5, NUS Urban Analytics Lab) for high-precision scientific graphical abstracts and multi-module system architectures. Implemented programmatically in [`scripts/editorial_studio.py`](../scripts/editorial_studio.py).

---

## 1. Design Tokens

### Canvas, Ink, and Structural Lines
| Token | Hex / Value | Role |
| :--- | :--- | :--- |
| `CANVAS_BG` | `#D9DBDE` | Matte architectural studio grey canvas (zero gradients, zero textures, zero drop shadows) |
| `INK` | `#111111` | Primary title, module headings, sub-figure headings, crisp dark arrows |
| `SUBTITLE_INK` | `#23282E` | Inline positioning subtitle on header row |
| `MUTED_INK` | `#3E454E` | Secondary metadata, parameters joined by `·`, colorbar ticks, file sub-labels |
| `LINE_WHITE` | `#FFFFFF` | 90° section frame borders (`1.6 pt`), `(1.3, 2.0)` dotted flows, `>>>` chevrons, wireframe icons, colorbar borders (`0.85 pt`) |
| `DOC_DARK` | `#2D333B` | Folded-corner export document wireframe cards |

### Material & Data Color Discipline (Context Desaturation / 焦景分离)
- **Architectural Clay Massing**: Main facades `#E2E4E7` / `#E4E6E8`; oblique walls `#D5DFE6`; pitched roofs or cut-planes `#CC6542`; terrain skirts `#8C8782` / `#8C9199`.
- **Discrete Structural Hierarchy**: Restrained monochrome-blue-teal progression (`#153D64` → `#2E74A6` → `#58B0A8` for `8h / 4h / 2h` octree coalescing). Never use saturated RGB rainbow palettes.
- **Continuous Scientific Fields**:
  - **Global Facade / Irradiance**: Perceptually uniform `inferno`; darken surrounding ground context to `#353B44` (`#2A2F36` skirt) so peak hotspots pop cleanly.
  - **Delta / Change Fields (`ATTENUATION_DELTA_CMAP`)**: Anchor near-zero values at neutral studio clay `#D5DBE1` and snap sub-threshold noise (`< 0.025`) to `#DDE1E6`, coloring only significant changes (`#8DE0AF → #1FA172 → #F2B705 → #DC4C28`).
  - **Translucent Volumetric Envelopes (`ENVELOPE_GLASS_CMAP`)**: Soft ice-blue → teal → sage → warm yellow (`#1E6EA8 → #2FA8A8 → #8AD18A → #F2C94C`) at `opacity = 0.55–0.60`, while desaturating non-focal context buildings (`#E2E5E9` / `#CFD4DC`) except 1 focal landmark (`#C7D6E4` / `#CC6542`) and crimson parcel boundary (`#D93829`).

### Strict 4-Tier Typography Scale (Baseline `16.0 × 9.6 in` Canvas)
Font stack: `['Arial', 'DejaVu Sans', 'Liberation Sans']` (plus `'Microsoft YaHei'` fallback for CJK).
1. **Tier 1 — Inline Header (`22–24 pt Bold` + `12 pt Regular`)**: Bold short tool/paper name at top-left (`y ≈ 0.956`), paired on the **same line** with a concise 1-line `#23282E` subtitle (`12.2 pt`). No header banner box.
2. **Tier 2 — Module Frame Heading (`11.0 pt Bold`)**: Embedded into the top-left border via an exact `CANVAS_BG` break-mask rectangle.
3. **Tier 3 — Sub-figure / Step Title (`8.8–10.4 pt Bold`)**: Crisp noun phrase beneath or above each asset bay.
4. **Tier 4 — Technical Micro-Labels (`7.2–8.3 pt`)**: Parameter tags joined by `·`, compact formulas (`QEF n·(x - c) <= d`), micro-colorbar endpoints, and callouts. Zero prose sentences.

---

## 2. Reusable Primitives (`scripts/editorial_studio.py`)

All Stage-B layout coordinates use normalized canvas units `[0, 1] × [0, 1]` with physical-inch aspect correction:

1. **`create_studio_canvas(...)` → `(fig, ax, ann_ax)`**: Initializes the `#D9DBDE` base axes (`zorder=0`) and a **top-most transparent annotation axes** (`ann_ax`, `zorder=30`, `facecolor="none"`) so callout arrows and labels never clip behind placed sub-axes PNGs.
2. **`draw_section_frame(ax, x, y, w, h, title, mask_w=...)`**: Sharp 90° `1.6 pt` pure white hollow frame broken cleanly behind the title by a `CANVAS_BG` mask rectangle.
3. **`draw_dotted_chevrons(ax, pts, ...)` & `draw_orthogonal_rail(ax, sources, targets, rail_y)`**: `1.7–1.9 pt` white `(1.3, 2.0)` dotted connectors with **physical-aspect-corrected** `>>>` chevrons (horizontal and vertical arrows maintain identical pixel angles on `16.0 × 9.6 in` canvases). Cross-module links follow orthogonal rails only.
4. **`draw_line_icon(...)` & `draw_doc_card(...)`**: Physical-aspect-corrected `1.5–1.8 pt` wireframe icons (`cloud`, `cube`, `merge`, `chart`, `export`) and `#2D333B` folded-corner format badges.
5. **`add_micro_colorbar(fig, ann_ax, x, y, w, h=0.0095, ...)`**: Slim `0.95%` height bar, `0.85 pt` `#FFFFFF` border, zero ticks, min/max endpoint labels flanked cleanly on left/right.
6. **`place_asset(ax, img_source, x0, y0, x1, y1)`**: Places transparent PNG into an independent `sub_ax` using exact physical-inch aspect preservation and `Lanczos` interpolation, returning `rect = (rx, ry, rw, rh)`.
7. **`add_anchored_callout(ann_ax, rect, uv, text, xytext, ...)`**: Projects normalized asset `[u, v]` coordinates into canvas coordinates on `ann_ax`, backed by translucent `CANVAS_BG` pills (`alpha=0.84`).

---

## 3. Decoupled Two-Stage Deterministic Pipeline

### Stage A — Independent Transparent Asset Generation & Caching
- Render all 3D bays (`PyVista`, `VTK`, `Blender`, or deterministic Matplotlib orthographic polyhedra) **off-screen** (`off_screen=True`, transparent RGBA, `three_lights`, MSAA) with **strictly locked `parallel_projection` isometric camera** (`[-D, -D, +D]`) and identical `parallel_scale` across sibling panels.
- **2D Exploded Stacks (`render_iso_raster_stack`)**: Exact 30° isometric `pcolormesh` (`(x - y) cos30, (x + y) sin30 + z`), 4 corner white vertical dotted rails, and `-30°` rotated labels with `2.5 pt` `#FFFFFF` halo (`path_effects.withStroke`).
- **3D Exploded Stacks (`crop_stack_alpha_union` + `render_exploded_3d_layers`)**: Crop every layer by their **union alpha bounding box** before vertical stacking so corners align pixel-for-pixel.
- **Tight Crop + 3D→2D Anchor JSON**: Crop single assets with `tight_crop_with_bbox` and write normalized `[u, v]` coordinates of key 3D landmarks (`sightline`, `viewpoint`, `landmark`, `envelope`, `park`) via `project_ortho_3d_to_crop_uv` / `project_pyvista_3d_to_crop_uv` into `anchors.json`. Cache all PNGs so Stage-B layout tweaks run in seconds.

### Stage B — Normalized Composition & Multi-Format Export
- Assemble all cached assets on `[0, 1] × [0, 1]` using `editorial_studio.py`, draw callouts on `ann_ax` using `anchors.json`, visually inspect the rendered PNG, and export high-resolution **PNG (240–300 DPI) + vector PDF / editable SVG** (`save_editorial_figure`).

---

## 4. Strict Anti-Patterns (Hard Guardrails)

- **NO** white/light-grey rounded cards or drop shadows (avoids PPT/Visio bloat).
- **NO** thick black solid arrows, rainbow borders, or diagonal crossing wires.
- **NO** unrestrained `jet` or saturated rainbow colormaps on architectural surfaces.
- **NO** mismatched camera angles, non-parallel perspective distortion, or inconsistent zoom scales across 3D panels.
- **NO** drawing annotations on the bottom `ax` where `sub_ax` images cover them, and **NO** manual eyeball-guessing of 3D leader endpoints.
- **NO** generative AI images substituting for deterministic data/geometry rendering.
