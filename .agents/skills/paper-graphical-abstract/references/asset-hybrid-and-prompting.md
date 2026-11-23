# Hybrid Real-Asset Preparation & Multi-Archetype Prompting Guide

## 1. Hybrid Real-Data + Vector Compositing Workflow

Binyu Lei and UAL figures achieve exceptional credibility because they blend **real domain renders** (3D city models, street-view imagery, GIS maps, real SHAP/EMM plots) with **crisp Matplotlib/vector annotations**—never letting a single tool try to fake everything.

### A. Exporting Transparent-Background 3D Assets (PyVista / Blender / QGIS)
When rendering a real 3D city model, voxel stack, or clay massing scene externally before compositing via `editorial_studio.py` or `ual_ga_kit.py`:

1. **Camera & Projection**:
   - Enable **parallel orthographic projection** (`plotter.enable_parallel_projection()` in PyVista; Orthographic camera in Blender).
   - Lock to a **30° isometric angle** (e.g., symmetric SW isometric `focus + [-D, -D, +D]`, identical `parallel_scale`) across every 3D asset in the figure so left/right edges align across panels.
2. **Lighting & Antialiasing**:
   - Use soft three-point studio lighting (`lighting="three lights"` + MSAA anti-aliasing in PyVista) with zero harsh specular glare.
   - Render off-screen at high resolution (`≥ 1100–2000 px`) and cache trimmed transparent PNGs in a dedicated asset directory so Stage-B layout tuning runs in seconds.
3. **Alpha-Union Cropping & 3D→2D Sub-Pixel Anchor Projection**:
   - For multi-layer 3D exploded stacks, crop all layers using their **joint alpha bounding box (`crop_stack_alpha_union`)** so corners stay pixel-aligned across layers.
   - For single assets receiving leader callouts, crop with `tight_crop_with_bbox` and simultaneously project key 3D landmarks through the active VTK/orthographic camera into cropped normalized `[u, v]` coordinates saved to `anchors.json` (`project_pyvista_3d_to_crop_uv` / `project_ortho_3d_to_crop_uv`), then render arrows on top-most `ann_ax` via `add_anchored_callout`.
4. **Transparent Background & Clay Shading**:
   - Export RGBA PNG with **alpha transparency** (`plotter.screenshot(..., transparent_background=True)`).
   - For **Studio Editorial** (`editorial_studio.py`): main walls `#E2E4E7`, oblique faces `#D5DFE6`, terracotta roofs/cuts `#CC6542`, terrain skirt `#8C8782`; darken ground to `#353B44` behind `inferno` facade maps; desaturate context behind `opacity=0.55–0.60` envelopes.
   - For **Archetype B white-clay models**: set base city mesh to matte off-white (`#E6E8EC`) and paint ONLY the focal building (`#F0C419`), walking route (`#D6336C`), or sensor stems (`#3B5BDB` / `#D6336C`).
5. **Compositing**:
   - In `editorial_studio.py`, place assets with `rect = place_asset(ax, "asset.png", x0, y0, x1, y1)` (`Lanczos` proportional scaling, returning exact placement rectangle).
   - In `ual_ga_kit.py`, use `place_image_box(ax, "asset.png", x, y, w, h)` or circular zoom `place_image_loupe(...)`.

### B. Real Mini-Charts vs. Schematic Vector Diagrams
- **Embed real Matplotlib mini-charts** (exported as transparent PNG/SVG or drawn on inset `fig.add_axes(...)`) whenever showing empirical findings inside Stage 3/4/5:
  - Feature contribution (`SHAP` horizontal bars, sorted by magnitude, muted sage/steel/coral colors).
  - Route/group response (`Estimated Marginal Means` multi-line comparison).
  - Multi-city data distributions (pastel histograms with circular geographic map insets, `2024 CEUS Fig. 5`).
  - Choropleth spatial maps (always include a crisp mini north arrow and scalebar).
- **Use schematic vector primitives** (`ual_ga_kit.py`) for conceptual GNN planes (`draw_gnn_planes`), isometric feature disc stacks (`draw_iso_exploded_stack`), bracketed indicator lists (`draw_bracket_list`), and file-export ecosystems (`draw_file_badge`).

---

## 2. Upgraded Multi-Archetype Prompt & Visual Blueprint Template

Use this template when the user requests a figure design prompt, structured visual specification, or blueprint before coding (Blueprint / Prompt Mode). Fill every bracketed slot before handing off.

```markdown
## Visual Architecture Blueprint — [Project / Paper Short Name]

- **Selected Archetype**: [A: Studio Grey Exploded Spatial Pipeline | B: Editorial White Clay-3D + Loupes & Method Column | C: Isometric Conceptual Interplay & Twin Mirror | D: Multi-Stage Spine / S-Flow Matrix]
- **Canvas & Output**: `[16.0 × 10.0 in]` (or `[16.0 × 6.4 in]` for Elsevier GA), `300 DPI PNG` + `editable vector SVG`
- **Background & Palette**:
  - Ground: `[#D9DBDE for A | #FFFFFF for B/C/D]`
  - Structural Ink & Borders: `[#FFFFFF 1.6 pt notched frames for A | #D2D5DA header bands + #B8BEC7 0.9 pt lines for B/D]`
  - Scientific Signal Accent (≤10% area): `[e.g., #F0C419 focal building, #3B5BDB/#D6336C stems, inferno/viridis field]`

### Top Header (Word Budget ≤ 15 words)
- **Bold Title**: `[Framework / Tool Name]`
- **1-Line Subtitle**: `[One concise clause: raw inputs -> core mechanism -> target urban/scientific outcome]`

### Spatial Anchor (Centerpiece Visual)
- **Geometry**: `[30° isometric exploded stack | white-clay 3D campus + circular SVI loupes | mirrored Physical↔Virtual twin diorama]`
- **Asset Source**: `[User-provided transparent RGBA PNG / real GeoTIFF | procedural isometric geometry via ual_ga_kit.py]`

### Numbered Module Plan (3–5 Stages, ≤ 5 words per node)
1. **[Module 1 Title — Input / Configuration]**:
   - Visual elements: `[e.g., Settings panel + 4 exploded 30° layers with -30° halo labels]`
   - Labels: `[Short phrase 1]`, `[Short phrase 2]`, `[...]`
2. **[Module 2 Title — Core Model / Generation / Fusion]**:
   - Visual elements: `[e.g., Voxelized stack -> Y-merge -> unified 3D voxel model | Tilted 2-plane GraphSAGE diagram]`
   - Flow connector: `[White dotted (1.3, 2.0) + >>> chevrons | Dotted radial leader + dark stage arrow]`
3. **[Module 3 Title — Simulation / Prediction / Evaluation]**:
   - Visual elements: `[e.g., Diagonal-split comparison + 2.0 pt circular zoom loupe + compact colorbar | Mini SHAP bar chart + 3-class comfort strip]`
4. **[Module 4 Title — Applications / Output / Ecosystem]** *(optional if 3 stages suffice)*:
   - Visual elements: `[e.g., Horizontal white dotted bus -> dark-slate folded file badges (.INX, .OBJ, .VOX, .GPKG)]`

### Non-Negotiable Restraint Rules
- Zero drop shadows, zero glossy pill cards, zero rainbow headers, zero multi-sentence prose blocks.
- Keep ≥ 25%–30% unobstructed neutral ground; keep all 3D projections locked at 30° isometric; verify via `audit_figure.py` and visual inspection.
```
