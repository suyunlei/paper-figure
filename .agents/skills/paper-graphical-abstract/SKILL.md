---
name: paper-graphical-abstract
description: >-
  Designs, structures, prompts, and programmatically renders publication-ready Graphical Abstracts,
  Figure 1 methodological frameworks, and system architecture workflow maps for research papers—distilled
  from Dr. Binyu Lei and the NUS Urban Analytics Lab (VoxCity, Urban Comfort Index, Human-Centric
  Digital Twins, GeoAI). Use when asked to create a paper overview diagram, graphical abstract,
  multi-stage pipeline, or architecture blueprint—especially for urban analytics, GIS/3D city modeling,
  GeoAI, environmental simulation, digital twins, and interdisciplinary engineering papers. Do NOT use for
  ordinary single-variable statistical charts, box/scatter plots, or standalone data-exploration plots.
---

# Paper Graphical Abstract Skill (Binyu Lei / NUS UAL Style)

Create restrained, architectural, high-information-density Graphical Abstracts and Figure 1 workflow maps using Matplotlib vector typography and transparent-background 2D/3D spatial assets.

## Core Design Philosophy (The 7 UAL / Binyu Lei Invariants)

1. **90/10 Neutral-to-Signal Ratio**: Reserve ~90% of the canvas for neutral architecture (matte studio grey `#D9DBDE` or crisp editorial white `#FFFFFF`, soft clay grays `#E6E8EC`/`#D2D5DA`, hairline borders) and concentrate ~10% vivid saturation strictly on scientific variables (heatmaps, focal buildings, simulation gradients, target nodes).
2. **Architectural Restraint over Decoration**: Zero drop shadows, zero glossy pill cards, zero rainbow module headers, zero decorative mini-gauges. Every mark carries technical meaning.
3. **Spatial Anchor First**: Ground abstract pipelines in a concrete spatial or physical object—an exploded 3D voxel stack, white-clay 3D city massing, street-view loupe, or geospatial map inset.
4. **Parallel Isometric Discipline**: Keep all 3D models, exploded layers, and multi-plane GNN diagrams locked to a single orthographic parallel projection (30° isometric azimuth, uniform scale).
5. **Extreme Word Economy**: Use bold short titles plus 2–5 word sub-labels and technical tags. Never write prose sentences inside boxes.
6. **Hybrid Real-Data + Vector Composition**: Composite real simulation rasters, street-view imagery, and genuine mini-plots (SHAP bars, histograms, maps) cleanly inside vector frames and circular zoom loupes rather than fabricating decorative cartoons.
7. **Mandatory Visual QA Loop**: Audit pixel balance, edge margins, color saturation, and font embedding, then inspect the rendered PNG directly before delivery.

## Mode Routing

- **Code-First Render Mode (Default)**: Build the full layout in Python using [`scripts/ual_ga_kit.py`](./scripts/ual_ga_kit.py), export 300 DPI PNG plus editable vector SVG, run [`scripts/audit_figure.py`](./scripts/audit_figure.py), and visually inspect the PNG.
- **Blueprint / Prompt Mode**: When the user asks for a figure design brief, layout plan, or external generation prompt (or supplies only raw paper notes without a render request), read [`references/asset-hybrid-and-prompting.md`](./references/asset-hybrid-and-prompting.md) and output the Multi-Archetype Visual Blueprint.

## 4-Archetype Selector

Choose one archetype matching the paper's narrative structure, then read [`references/archetypes-and-design-system.md`](./references/archetypes-and-design-system.md) for exact hex tokens, typography sizes, and stroke grammar.

| Paper Contribution Type | Archetype | Canvas & Visual Signature | Reference Anchor |
| :--- | :--- | :--- | :--- |
| **Software toolchain, simulation pipeline, open-data → 3D model → export** | **A — Studio Grey Exploded Spatial Pipeline** | `#D9DBDE` matte grey; 90° `#FFFFFF` notched frames; 30° isometric exploded raster/voxel stacks + `-30°` halo labels; dotted `(1.3, 2.0)` flows with `>>>`; dark folded file badges | `2026-ceus-voxcity` (see [`examples/demo_studio_grey_voxcity.py`](./examples/demo_studio_grey_voxcity.py)) |
| **Urban sensing, GeoAI/GNN prediction, 3D city model + method steps** | **B — Editorial White Clay-3D + Loupes & Method Column** | `#FFFFFF` canvas; white-clay 3D massing with 1–2 focal accents (`#F0C419` / `#3B5BDB` / `#D6336C`); circular photo loupes; right-hand Step 1–4 gray-band or dashed zones; `[ ... ]` feature brackets | `2023-scs-human-dt`, `2024-ceus-gnn-building`, `2025-scs-urban-comfort`, `2026-cities-jitai` (see [`examples/demo_editorial_clay_geoai.py`](./examples/demo_editorial_clay_geoai.py)) |
| **Conceptual framework, bidirectional digital twin, survey/lifecycle taxonomy** | **C — Isometric Conceptual Interplay & Twin Mirror** | `#FFFFFF` canvas; central vector diorama (periwinkle `#7E93DF` Physical vs. slate `#C8CED8` Virtual mirror) + curved translucent exchange arcs; L-shaped dotted leaders + underlined italic callouts | `2025-scs-urban-comfort` GA, `2026-cities-jitai` Fig. 1, `2023-autcon-dt-challenges` (see [`examples/demo_interplay_twin.py`](./examples/demo_interplay_twin.py)) |
| **Empirical workflow, multi-modal sensing + XAI/GNN + spatial evaluation** | **D — Multi-Stage Spine / S-Flow Matrix** | `#FFFFFF` canvas; left vertical icon-spine OR 5-cell numbered S-flow grid embedding real SVI segmentation/depth/irradiance chips, tilted GNN encoder-decoder planes, and real SHAP/EMM mini-plots | `2026-bae-walking`, `2026-ceus-cyclingsafety`, `2026-epb-waterway` (see [`examples/demo_geoai_matrix.py`](./examples/demo_geoai_matrix.py)) |

## 6-Stage Production Workflow

### Stage 1: Paper Distillation & Strict Word Budget
Extract only what fits in a 5-second glance:
- **Top Header**: 1 bold project/framework name + ≤1-line positioning subtitle (12 words max).
- **Primary Modules**: 3–5 numbered stages (`1. Data`, `2. Model`, `3. Simulation/Analysis`, `4. Applications/Export`).
- **Node Budget**: ≤5 words per node label; convert multi-line explanations into compact key-value pairs, micro-tables, or `Name + (metric/tool)` tags.

### Stage 2: Aspect Ratio & Target Format
- **Manuscript Fig. 1 / Architecture Overview**: `16.0 × 10.0 in` (16:10 default) or `16.0 × 9.0 in` (widescreen); use `12.0 × 9.0 in` or `11.0 × 13.5 in` for vertical Spine/Matrix layouts.
- **Elsevier Graphical Abstract (CEUS, Cities, SCS, B&E, AutCon)**: Wide landscape (`5:2` to `16:9`, e.g., `16.0 × 6.4 in` or `16.0 × 9.0 in`; export ≥ `1328 × 531 px` at 300 DPI).

### Stage 3: Grid Zoning & Asset Audit
1. Map all containers onto clean columns/rows with ≥ `0.25 in` outer margin and ≥ `0.22 in` inter-module gutters.
2. Inventory user-supplied real assets (PyVista transparent PNGs, QGIS maps, street-view photos, SHAP plots). Where real renders are absent, prepare transparent-background assets per [`references/asset-hybrid-and-prompting.md`](./references/asset-hybrid-and-prompting.md) or generate crisp schematic geometry via `ual_ga_kit.py`.

### Stage 4: Author Script Using `scripts/ual_ga_kit.py`
Use the full-bleed physical-inch canvas (`create_canvas`) with `aspect='equal'` so isometric angles stay exact 30° and circles stay true:
- **Archetype A frames**: `draw_notched_frame` (1.6 pt `#FFFFFF`, `#D9DBDE` title notch) + `draw_ortho_flow` (`dash=(1.3, 2.0)`, `chevrons=3`) + `draw_iso_exploded_stack` + `draw_iso_voxel_city` + `draw_file_badge`.
- **Archetype B/D containers**: `draw_header_panel`, `draw_dashed_zone`, `draw_iso_clay_city`, `place_image_loupe`, `draw_leader_line`, `draw_bracket_list`, `draw_gnn_planes`, `draw_micro_table`, `draw_pill_tag`.
- Export via `save_publication_figure(fig, out_stem, formats=('png', 'svg'), dpi=300)` so SVG retains editable `<text>` nodes (`svg.fonttype = 'none'`).

### Stage 5: Automated Quantitative Audit
Run the QA script after every render:
```bash
python .agents/skills/paper-graphical-abstract/scripts/audit_figure.py <out.png> --svg <out.svg> --theme <studio_grey|editorial_white|interplay_twin|geoai_matrix>
```
Resolve any `[FAIL]` or `[WARN]` on edge clipping, neutral-ground ratio, over-saturation (`>28%` vivid pixels), or missing editable `<text>` elements in SVG.

### Stage 6: Visual Self-Critique Loop (Mandatory)
Open the rendered PNG visually and review every item in [`references/visual-qa-checklist.md`](./references/visual-qa-checklist.md). Fix overlapping labels, clipped badges, inconsistent isometric slopes, or weak visual hierarchy, re-run the script, and re-audit before finishing.

## Resource Map

- [`references/lei-binyu-visual-analysis.md`](./references/lei-binyu-visual-analysis.md) — Read when choosing framing motifs or justifying design choices against Binyu Lei's 2023–2026 UAL corpus (including anti-patterns to avoid).
- [`references/archetypes-and-design-system.md`](./references/archetypes-and-design-system.md) — Read before writing drawing code to lock in exact hex codes, typography scale, line weights, and anti-AI-slop rules.
- [`references/asset-hybrid-and-prompting.md`](./references/asset-hybrid-and-prompting.md) — Read when preparing external PyVista/Blender/QGIS transparent assets or operating in Blueprint/Prompt mode.
- [`references/visual-qa-checklist.md`](./references/visual-qa-checklist.md) — Read during Stage 6 visual self-critique and before final journal export.
- [`scripts/ual_ga_kit.py`](./scripts/ual_ga_kit.py) — Reusable Matplotlib/NumPy/PIL drawing kit implementing all 4 archetypes' geometric primitives.
- [`scripts/audit_figure.py`](./scripts/audit_figure.py) — Post-render PNG + SVG automated quality validator.
- [`examples/demo_studio_grey_voxcity.py`](./examples/demo_studio_grey_voxcity.py), [`examples/demo_editorial_clay_geoai.py`](./examples/demo_editorial_clay_geoai.py), [`examples/demo_interplay_twin.py`](./examples/demo_interplay_twin.py), & [`examples/demo_geoai_matrix.py`](./examples/demo_geoai_matrix.py) — Reference implementations for Archetypes A, B, C, and D.
