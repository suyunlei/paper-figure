# Four Visual Archetypes & Complete Design System

Every figure must select **one** primary archetype (or the flagship [**Architectural Studio Editorial**](./editorial_studio_style.md) two-stage preset in [`scripts/editorial_studio.py`](../scripts/editorial_studio.py)) and enforce its exact color, typography, container, and connector grammar across the entire canvas.

---

## 1. Archetype Design Tokens

### Archetype A — Studio Grey Exploded Spatial Pipeline (*VoxCity* Style)
Best for: software packages, automated data-to-simulation pipelines, multi-layer 3D raster/voxel builders, interoperability & file-export tools.

| Token | Value | Usage |
| :--- | :--- | :--- |
| `canvas_bg` | `#D9DBDE` | Matte architectural studio grey canvas (no gradient, no texture) |
| `frame_border` | `#FFFFFF` (`1.6 pt`, 90° sharp corners) | Outer numbered module frames; break top border behind title using `#D9DBDE` notch |
| `flow_line` | `#FFFFFF` (`1.8 pt`, dash `(1.3, 2.0)`) | Intra- and inter-module orthogonal connectors |
| `chevron_accent` | `#FFFFFF` (`2.0 pt`) | Triple polyline chevrons `>>>` centered on key flow segments |
| `iso_layer_rim` | `#FFFFFF` (`1.1 pt`) | Perimeter edges of each 30° isometric raster/voxel slice |
| `iso_rail` | `#FFFFFF` (`0.95 pt`, dotted) | Vertical corner alignment rails connecting exploded layers |
| `icon_stroke` | `#FFFFFF` (`1.6–1.9 pt`) | Minimal uniform-stroke wireframe icons (`cloud_download`, `iso_cube`, `y_merge`, `line_chart`, `export_arrow`) |
| `title_ink` | `#111111` | Main title, module titles, primary bottom captions |
| `sub_ink` | `#3E454E` | Subtitle, technical metadata, compact colorbar ticks |
| `halo_stroke` | `#FFFFFF` (`2.5 pt`) | Outer text stroke behind `-30°` rotated layer edge labels |
| `clay_neutral` | `#E2E4E7` / `#C7CCD4` / `#AEB5C0` | Un-highlighted 3D building massing and neutral terrain |
| `badge_stroke` | `#2D333B` | Dark-slate folded-corner file badges (`.INX`, `.OBJ`, `.VOX`, `.GPKG`) |
| `science_cmaps` | `inferno`, `viridis`, `terrain`, custom `#0E2F56 → #38A39D → #E6C15A` | Reserved strictly for scientific heatmaps, canopy/elevation, and simulation slices |

---

### Archetype B — Editorial White Clay-3D + Loupes & Method Column (*Binyu Lei Signature* Style)
Best for: human-centric urban analytics, GeoAI / GNN urban prediction, street-view + 3D city model integration, urban comfort & microclimate frameworks.

| Token | Value | Usage |
| :--- | :--- | :--- |
| `canvas_bg` | `#FFFFFF` | Pure crisp journal editorial background |
| `header_band_bg` | `#D2D5DA` | Flat neutral-grey header strips inside Step 1–4 panels |
| `dashed_zone_bg` | `#F4F5F7` | Subtle cool-grey fill for dashed GNN / methodology compartments |
| `panel_border` | `#B8BEC7` (`0.9 pt` solid) or `#7C828D` (`0.9 pt` dashed `(4, 2.5)`) | Step container outlines |
| `clay_faces` | Top `#F4F5F7`, Left `#DDE1E7`, Right `#C2C8D2`, Edge `#B0B7C3` (`0.35 pt`) | Matte white-clay 3D city massing model |
| `focal_gold` | `#F0C419` (left `#D9AE12`, right `#BD940A`) | Single highlighted focal building or target asset (`2024 ISPRS`) |
| `stem_cobalt` | `#3B5BDB` / `stem_magenta` `#D6336C` | Semantic 3D point stems & matching rounded pill callouts (`2026 Cities`) |
| `gnn_focal` | `#D95F02` (orange) + `#4E9A8E` (sage-teal) | Target node & message-passing highlight inside tilted GNN planes |
| `loupe_rim` | `#FFFFFF` (`2.0 pt`) or `#4B525E` (`1.1 pt`) | Circular photo / context zoom loupes |
| `leader_line` | `#4B525E` (`0.95 pt`, dotted `(1.2, 1.8)`) | Radial curved or straight callouts with `0.035 in` start dot |
| `bracket_ink` | `#8C929C` (`0.9 pt`) | Delicate `[ ... ]` feature-group brackets (`2025 SCS`) |
| `title_ink` | `#181C20` | Bold module/step headings and table headers |
| `sub_ink` | `#4A525E` | Dimension sub-labels, metrics (`MAE, RMSE, R2`), split notes |

---

### Archetype C — Isometric Conceptual Interplay & Digital Twin Mirror
Best for: review papers, bidirectional digital-twin conceptualizations, multidimensional index diagrams, lifecycle challenge taxonomies.

| Token | Value | Usage |
| :--- | :--- | :--- |
| `canvas_bg` | `#FFFFFF` | Pure editorial white |
| `physical_blue` | `#7E93DF` / `#9FAFE8` / `#C4CEF5` | Periwinkle isometric city blocks & physical-world icon badges |
| `virtual_slate` | `#B5BDC9` / `#D0D6DF` / `#E7EBF0` | Cool silver-slate mirrored virtual twin blocks |
| `exchange_arc` | `#DCE1EA` (soft thick translucent arc) + `#6C737F` arrowhead | Bidirectional information exchange loops between twins or City⇄Humans |
| `callout_border` | `#B8BEC7` (`0.85 pt`, rounded `r=0.10 in`) | Minimalist perimeter callout cards with hairline icon boxes |
| `elbow_leader` | `#7C828D` (`0.9 pt`, dotted) | Orthogonal L-shaped connectors with dot anchor on the diorama |
| `category_heading` | Bold-italic underlined sans-serif (`#181C20`) | Dimension titles (*3D urban morphology*, *Human visual perception*) |
| `lifecycle_ring` | `#0A7B34`, `#8FD175`, `#D8DCE2`, `#6A2C91`, `#B89EC9`, `#D8DCE2` | 6-phase diverging botanical-green to plum-purple ring (`2023 AutCon`) |

---

### Archetype D — Multi-Stage Spine / S-Flow Matrix
Best for: multi-modal sensing experiments, empirical urban informatics studies combining CV segmentation + depth + GNN + SHAP/statistical interpretation.

| Token | Value | Usage |
| :--- | :--- | :--- |
| `canvas_bg` | `#FFFFFF` | Pure white |
| `spine_accent` | `#555C68` (slate) or `#181C20` (ink) | Left vertical stage-icon spine (`0.08 in` vertical dashed flow) OR `1. Data → 5. Analysis` S-grid |
| `sub_header_band` | `#7A7F85` (white text `#FFFFFF`) or `#E8EAED` (dark text `#181C20`) | Compact inner module headers |
| `flow_triangle` | `#343A40` (solid `▶` / `▼` / `▲` glyphs) | Crisp inter-module progression markers (`2026 CEUS Cycling`) |
| `section_rule` | `#9CA3AF` (`0.9 pt`) | Horizontal divider lines separating output mini-plots & interpretations |
| `plot_palette` | `#5B8E7D` (sage), `#4A7C9B` (steel blue), `#D97757` (muted coral), `#8C6BB1` (muted violet) | Restrained scientific bars/curves inside embedded mini-charts |

---

## 2. Typography Scale (Calibrated for `16.0 × 10.0 in` Canvas at 300 DPI)

Font stack: `['Arial', 'Helvetica', 'DejaVu Sans']` (plus `'Microsoft YaHei'` fallback when Chinese characters appear). Always preserve editable SVG text (`svg.fonttype = 'none'`) alongside 300 DPI PNG exports.

| Role | Size (pt) | Weight / Style | Color | Notes |
| :--- | :---: | :--- | :--- | :--- |
| **Figure Main Title** | `17–20` | Bold | `#111111` / `#181C20` | Short framework/system name; top-left aligned |
| **One-Line Subtitle** | `10.5–11.5` | Regular | `#3E454E` / `#4A525E` | ≤12 words summarizing input → mechanism → output |
| **Numbered Module / Step Title** | `11–12.5` | Bold | `#111111` / `#181C20` | Centered in header band or embedded in top-left frame notch |
| **Isometric `-30°` Layer Label** | `9–10` | Regular or Medium | `#111111` | Aligned parallel to front-left isometric edge with `2.5 pt` `#FFFFFF` halo |
| **Sub-element / Stage Caption** | `9–10.5` | Bold or Regular | `#111111` / `#181C20` | 1 line beneath 3D asset or icon |
| **Technical Micro-Label / Table Cell** | `7.5–8.5` | Regular / Italic | `#3E454E` / `#4A525E` | Metrics (`MAE, RMSE, R2`), split notes, file names |
| **Underlined Dimension Header** | `10` | Bold Italic + Underline | `#181C20` | Signature Archetype C callout label style |

> **Scaling Rule**: If exporting a narrow Elsevier Graphical Abstract (`16 × 6.4 in`) or vertical single-column frame (`10 × 12 in`), keep all body text `≥ 7.5 pt` at final print size so nothing becomes illegible at 50% scale.

---

## 3. Container & Connector Grammar

1. **Notched Hollow Frame (Archetype A)**: `1.6 pt` solid `#FFFFFF` rectangle with sharp `0°` corners; place a solid `#D9DBDE` rectangle behind the top-left title (`pad = 0.12 in`) so the white frame cleanly breaks on both sides of the title.
2. **Gray-Header Modular Box (Archetype B/D)**: `0.9 pt` `#B8BEC7` outer rectangle + full-width `#D2D5DA` or `#7A7F85` header strip (`height = 0.34–0.42 in`) with centered bold title.
3. **Dashed Methodology Zone (Archetype B)**: `#F4F5F7` fill + `0.9 pt` `#7C828D` dashed `(4, 2.5)` outline.
4. **Dotted Orthogonal Flow + Triple Chevron (Archetype A)**: `#FFFFFF` `1.8 pt` dotted path `(1.3, 2.0)` with strict 90° horizontal/vertical elbows; overlay three crisp open `>>>` chevrons (`2.0 pt`, `0.11 in` leg) pointing along the flow segment.
5. **Radial / Curved Context Leader (Archetype B/C)**: `0.95 pt` dotted `(1.2, 1.8)` dark-slate line starting from a `0.035 in` anchor dot on a 3D building/route point and terminating cleanly on a circular loupe rim or pill tag.

---

## 4. The 10 Anti-AI-Slop Iron Laws

| Forbidden "AI-Diagram" Telltale | UAL / Binyu Lei Replacement |
| :--- | :--- |
| 1. Rounded white pill-cards on colored gradients | Sharp 90° hollow white frames (Archetype A) or hairline `#FFFFFF`/`#F4F5F7` zones (Archetype B–D) |
| 2. Soft drop shadows under every box | Zero drop shadows anywhere; create separation via whitespace and hairline stroke contrast |
| 3. Rainbow-colored headers per step (blue/green/orange/purple) | Unified neutral slate/grey headers across all steps; color only inside data/target geometry |
| 4. Diagonal or curved messy spaghetti arrows crossing labels | Strictly orthogonal H/V elbows (`A`) or radial non-crossing dotted leaders (`B`/`C`) |
| 5. Multi-sentence prose explanations inside diagram boxes | 2–5 word phrases, parameter tags, or compact `Index | Feature | Value` micro-tables |
| 6. Decorative miniature gauges, fake bar icons, or sparkles | Real embedded mini-plots (SHAP, EMM, histogram) or minimal 1.7 pt wireframe glyphs |
| 7. Mixed camera angles (top-down map next to tilted 45° perspective box) | Single locked 30° parallel orthographic projection across all 3D stacks and GNN planes |
| 8. Low-contrast text over noisy raster textures | `2.5 pt` `#FFFFFF` text halo (`path_effects.withStroke`) on all over-layer `-30°` labels |
| 9. Random unaligned box widths and ragged margins | Strict grid columns with equal outer margins (`≥0.25 in`) and aligned baselines |
| 10. Clipart cartoons of people/buildings | Architectural white-clay 3D massing (`#F4F5F7`/`#DDE1E7`/`#C2C8D2`) or clean minimalist vector line-art |
