---
name: paper-graphical-abstract
description: >-
  Designs, structures, prompts, and programmatically renders publication-ready Graphical Abstracts,
  Figure 1 methodological frameworks, and system architecture workflow maps for research papers—distilled
  from Dr. Binyu Lei and the NUS Urban Analytics Lab (VoxCity, VoxVista, Urban Comfort Index, Human-Centric
  Digital Twins, GeoAI). Supports the flagship Architectural Studio Editorial two-stage preset alongside
  4 UAL visual archetypes. Use when asked to create a paper overview diagram, graphical abstract,
  multi-stage pipeline, or architecture blueprint—especially for urban analytics, GIS/3D city modeling,
  GeoAI, environmental simulation, digital twins, and interdisciplinary engineering papers. Do NOT use for
  ordinary single-variable statistical charts, box/scatter plots, or standalone data-exploration plots.
---

# Paper Graphical Abstract Skill (Binyu Lei / NUS UAL Style)

Create restrained, architectural, high-information-density Graphical Abstracts and Figure 1 workflow maps using deterministic Matplotlib vector typography and transparent-background 2D/3D spatial assets.

## Core Design Philosophy (The 7 UAL / Binyu Lei Invariants)

1. **90/10 Neutral-to-Signal Ratio**: Reserve ~90% of the canvas for neutral architecture (matte studio grey `#D9DBDE` or crisp editorial white `#FFFFFF`, soft clay grays `#E2E4E7`/`#D2D5DA`, hairline borders) and concentrate ~10% vivid saturation strictly on scientific variables (heatmaps, focal landmarks, Delta thresholds, target nodes).
2. **Architectural Restraint over Decoration**: Zero drop shadows, zero glossy pill cards, zero rainbow module headers, zero decorative mini-gauges. Every mark carries technical meaning.
3. **Spatial Anchor First**: Ground abstract pipelines in a concrete spatial or physical object—an exploded 3D voxel/cut-cell stack, white-clay 3D city massing, street-view loupe, or geospatial map inset.
4. **Locked Parallel Isometric Discipline**: Keep all 3D models, exploded layers, and multi-plane GNN diagrams locked to a single orthographic parallel projection (`30°` isometric azimuth, identical camera and scale across sibling panels).
5. **Extreme Word Economy**: Use bold short noun phrases joined by `·`, compact formulas, and 2–5 word labels. Never write prose sentences inside boxes.
6. **Two-Stage Deterministic Hybrid Composition**: Decouple Stage-A transparent RGBA rendering & caching (PyVista/VTK/Blender or deterministic orthographic renders + 3D→2D `[u, v]` anchor JSON) from Stage-B normalized canvas composition with top-most `ann_ax` (`zorder=30`).
7. **Mandatory Visual QA Loop**: Audit pixel balance, edge margins, color restraint, and vector text integrity, then visually inspect the rendered PNG before delivery.

## Strict Visual Anti-Patterns (Never Violate)

- Never place white/light-grey rounded cards with drop shadows (PPT/Visio look).
- Never use thick black solid arrows, colorful thick borders, or messy diagonal crossing connectors.
- Never use unrestrained `jet` or saturated rainbow colormaps on studio figures.
- Never mix camera angles/scales across 3D panels or use distorted default perspective projection.
- Never draw annotations on bottom `ax` where placed `sub_ax` images occlude them, and never eyeball-guess 3D callout endpoints (use projected `[u, v]` JSON anchors).
- Never replace deterministic scientific data renders with generative AI textures.

## Mode & Engine Selection

- **Architectural Studio Editorial (`scripts/editorial_studio.py` — Flagship High-Precision Preset)**:
  Use for multi-module software/3D urban modeling/simulation Graphical Abstracts requiring `#D9DBDE` studio ground, `16.0 × 9.6 in` inline editorial header, Stage-A transparent asset caching (`crop_stack_alpha_union`, `tight_crop_with_bbox`), top-most `ann_ax` (`zorder=30`), physical-aspect-corrected `>>>` chevrons, slim micro-colorbars, and sub-pixel 3D→2D `[u, v]` callout anchors. Read [`references/editorial_studio_style.md`](./references/editorial_studio_style.md) first.
- **4-Archetype Procedural Engine (`scripts/ual_ga_kit.py`)**:
  Use when generating standalone vector+isometric schematics on an inch canvas across Archetypes A–D (including Editorial White Clay-3D, Physical↔Virtual Twin Mirror, or Multi-Stage Spine Matrix). Read [`references/archetypes-and-design-system.md`](./references/archetypes-and-design-system.md).
- **Blueprint / Prompt Mode**:
  When the user asks for a figure design brief or external generation prompt without rendering code, read [`references/asset-hybrid-and-prompting.md`](./references/asset-hybrid-and-prompting.md).

## Preset & Archetype Selector

| Paper Contribution Type | Preset / Archetype | Canvas & Visual Signature | Reference Anchor |
| :--- | :--- | :--- | :--- |
| **Multi-module 3D city modeling, cut-cell/voxel engines, Stage-A/B hybrid renders** | **Architectural Studio Editorial** *(Flagship)* | `#D9DBDE` studio grey; inline `23.5 pt` header; 90° notched `#FFFFFF` frames; `ann_ax` top annotation layer; `crop_stack_alpha_union`; `[u, v]` 3D→2D anchors; micro-colorbars; `#2D333B` doc cards | *VoxVista* (*CEUS* v6) · [`examples/demo_editorial_studio.py`](./examples/demo_editorial_studio.py) |
| **Lightweight toolchain pipeline (open-data → voxel → export)** | **Archetype A — Studio Grey Exploded Spatial Pipeline** | `#D9DBDE` matte grey; 90° `#FFFFFF` notched frames; 30° isometric exploded raster/voxel stacks + `-30°` halo labels; dotted `(1.3, 2.0)` flows + `>>>`; dark folded file badges | *VoxCity* (*CEUS* 2026) · [`examples/demo_studio_grey_voxcity.py`](./examples/demo_studio_grey_voxcity.py) |
| **Urban sensing, GeoAI/GNN prediction, 3D city model + method steps** | **Archetype B — Editorial White Clay-3D + Loupes & Method Column** | `#FFFFFF` canvas; white-clay 3D massing with 1–2 focal accents (`#F0C419` / `#3B5BDB` / `#D6336C`); circular photo loupes; right-hand Step 1–4 gray-band or dashed zones; `[ ... ]` feature brackets | `2023-scs-human-dt`, `2024-ceus-gnn-building`, `2025-scs-urban-comfort`, `2026-cities-jitai` · [`examples/demo_editorial_clay_geoai.py`](./examples/demo_editorial_clay_geoai.py) |
| **Conceptual framework, bidirectional digital twin, survey/lifecycle taxonomy** | **Archetype C — Isometric Conceptual Interplay & Twin Mirror** | `#FFFFFF` canvas; symmetric Physical↔Virtual twin dioramas + curved translucent exchange arcs; L-shaped dotted leaders + underlined italic callouts | `2025-scs-urban-comfort` GA, `2026-cities-jitai` Fig. 1, `2023-autcon-dt-challenges` · [`examples/demo_interplay_twin.py`](./examples/demo_interplay_twin.py) |
| **Empirical workflow, multi-modal sensing + XAI/GNN + spatial evaluation** | **Archetype D — Multi-Stage Spine / S-Flow Matrix** | `#FFFFFF` canvas; left vertical icon-spine OR numbered S-flow grid embedding SVI CV slices, tilted GNN planes, and real SHAP/EMM mini-plots | `2026-bae-walking`, `2026-ceus-cyclingsafety`, `2026-epb-waterway` · [`examples/demo_geoai_matrix.py`](./examples/demo_geoai_matrix.py) |

## 6-Stage Production Workflow

### Stage 1: Paper Distillation & Strict Word Budget
Extract only what fits in a 5-second glance:
- **Top Header**: 1 bold project/framework name + same-line or ≤1-line positioning subtitle (12 words max).
- **Primary Modules**: 3–5 numbered stages (`1. Generation`, `2. Core Representation`, `3. Simulation & Planning`, `4. Export & Bridge`).
- **Node Budget**: ≤5 words per node label; express parameters with middle dots (`0.5 m cut-cells · Kanda-Surugadai`) and compact formulas.

### Stage 2: Aspect Ratio & Output Formats
- **Architectural Studio Editorial**: `16.0 × 9.6 in` widescreen default (`240–300 DPI PNG` + vector `PDF` and/or editable `SVG`).
- **Archetypes A–D (`ual_ga_kit.py`)**: `16.0 × 10.0 in` (16:10) or `16.0 × 6.4 in` (Elsevier GA); default `PNG + SVG` (`svg.fonttype = 'none'`) or `PNG + SVG + PDF` when journal submission requires PDF.

### Stage 3: Stage-A Deterministic Asset Generation & Caching
1. Render 3D scenes off-screen with transparent RGBA, `three lights`, MSAA, and locked `parallel_projection` isometric camera.
2. Crop exploded 3D stacks via `crop_stack_alpha_union` so all layers align pixel-for-pixel; crop single assets via `tight_crop_with_bbox` and save 3D→2D `[u, v]` callout landmarks to `anchors.json`.
3. Cache assets on disk so Stage-B composition runs in seconds without re-running 3D extraction.

### Stage 4: Stage-B Normalized Composition
- **Architectural Studio Editorial (`scripts/editorial_studio.py`)**: `create_studio_canvas` → `draw_section_frame` → `place_asset` → `draw_dotted_chevrons` / `draw_orthogonal_rail` → `draw_line_icon` / `draw_doc_card` → `add_micro_colorbar` → `add_anchored_callout` on top-most `ann_ax` (`zorder=30`) → `save_editorial_figure`.
- **Archetypes A–D (`scripts/ual_ga_kit.py`)**: `create_canvas` + archetype-specific helpers + `save_publication_figure`.

### Stage 5: Automated Quantitative Audit
Run the QA script after every render (passing `--svg` and/or `--pdf`):
```bash
python .agents/skills/paper-graphical-abstract/scripts/audit_figure.py <out.png> --svg <out.svg> --pdf <out.pdf> --theme <editorial_studio|studio_grey|editorial_white|interplay_twin|geoai_matrix>
```
Resolve any `[FAIL]` or `[WARN]` on edge clipping, neutral-ground ratio, over-saturation (`>28%`), or missing vector text.

### Stage 6: Visual Self-Critique Loop (Mandatory)
Open the rendered PNG visually and check every item in [`references/visual-qa-checklist.md`](./references/visual-qa-checklist.md) (header balance, chevron symmetry, 3D occlusion, callout arrow landing precision, colorbar legibility). Fix any defects, re-run, and re-audit before delivery.

## Resource Map

- [`references/editorial_studio_style.md`](./references/editorial_studio_style.md) — **Read first** for the Architectural Studio Editorial design tokens, Stage-A/B pipeline rules, and strict anti-patterns.
- [`references/lei-binyu-visual-analysis.md`](./references/lei-binyu-visual-analysis.md) — Empirical visual catalog of 15 Binyu Lei & NUS UAL papers (2023–2026).
- [`references/archetypes-and-design-system.md`](./references/archetypes-and-design-system.md) — Exact hex codes, typography scale, and container/connector grammar for Archetypes A–D.
- [`references/asset-hybrid-and-prompting.md`](./references/asset-hybrid-and-prompting.md) — PyVista/Blender/QGIS transparent asset prep, alpha-union cropping, `[u, v]` anchor projection, and Prompt Blueprint template.
- [`references/visual-qa-checklist.md`](./references/visual-qa-checklist.md) — 12-point visual inspection checklist & journal export targets.
- [`scripts/editorial_studio.py`](./scripts/editorial_studio.py) — Architectural Studio Editorial reusable library (Stage-A caching, alpha-union, `[u, v]` projection, normalized Stage-B composition).
- [`scripts/ual_ga_kit.py`](./scripts/ual_ga_kit.py) — Inch-canvas isometric & vector drawing kit for Archetypes A–D.
- [`scripts/audit_figure.py`](./scripts/audit_figure.py) — Post-render PNG + SVG + PDF automated validator.
- [`examples/demo_editorial_studio.py`](./examples/demo_editorial_studio.py) — Flagship 4-module two-stage Architectural Studio Editorial showcase.
- [`examples/demo_studio_grey_voxcity.py`](./examples/demo_studio_grey_voxcity.py), [`examples/demo_editorial_clay_geoai.py`](./examples/demo_editorial_clay_geoai.py), [`examples/demo_interplay_twin.py`](./examples/demo_interplay_twin.py), [`examples/demo_geoai_matrix.py`](./examples/demo_geoai_matrix.py) — Archetypes A–D reference scripts.
