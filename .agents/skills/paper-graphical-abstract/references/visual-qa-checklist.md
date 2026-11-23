# Visual QA Checklist & Journal Export Standards

Inspect every rendered PNG (via `read_file` / image viewer) **and** every editable SVG export before considering a Graphical Abstract complete.

## 1. 12-Point Visual Self-Critique Rubric

1. **5-Second Narrative Glance**: Without reading small labels, can a reviewer trace the left-to-right or top-to-bottom story (`Input → Core Method → Output/Impact`) in under 5 seconds?
2. **90/10 Color Restraint**: Does the neutral canvas (`#D9DBDE` or `#FFFFFF`) plus matte greys dominate the image, leaving vivid color strictly on scientific data/focal targets (`audit_figure.py` high-saturation fraction `< 28%`)?
3. **50% Zoom Legibility**: View the image scaled down to ~50% width (manuscript column / ScienceDirect Graphical Abstract card). Is every module header, layer label, table value, and colorbar tick crisp and readable?
4. **Zero Collisions or Overlap**: Confirm zero text crosses frame lines, arrow shafts, neighboring labels, circular loupes, or colorbar ticks. Pay special attention to `-30°` rotated layer labels and compact micro-tables.
5. **Edge Clearance & Margin Discipline**: No frame, badge, or label touches the outer `1.5%–2%` edge of the canvas (`audit_figure.py` edge-clipping check passes).
6. **Isometric Parallel Consistency**: Do all exploded layers, voxel blocks, white-clay buildings, and tilted GNN planes share an identical 30° parallel orientation with straight vertical alignment rails?
7. **Depth Sorting Integrity (3D Clay / Voxel Models)**: Verify front buildings/trees cleanly occlude back buildings/trees with zero Z-fighting or reversed faces.
8. **White-Halo Contrast on Overlays**: Any text overlaid on dark or colored raster slices (`Canopy height`, `Building height`, `Land cover`, `Terrain elevation`) carries a clean `2.5 pt` `#FFFFFF` halo stroke (`path_effects.withStroke`) and sits flush along the front-left `-30°` edge.
9. **Connector Discipline**:
   - Archetype A: strictly horizontal/vertical 90° orthogonal elbows with uniform `(1.3, 2.0)` white dots and aligned `>>>` chevrons.
   - Archetype B/C: fine dotted leaders originate from an explicit anchor dot on the 3D model/map and meet the loupe rim cleanly without crossing unrelated labels.
10. **True Circular Geometry**: Verify `ax.set_aspect('equal')` was active so every circular loupe, sensor badge, and node circle is mathematically round (never squashed into an ellipse).
11. **Zero AI-Slop Artifacts**: Verify zero drop shadows, zero glossy gradients, zero bloated text paragraphs, zero unrequested decorative badges.
12. **Editable SVG Vector Integrity**: Run `audit_figure.py --svg ...` and confirm valid XML with editable `<text>` nodes (`svg.fonttype = 'none'`), ensuring labels remain crisp and editable in Illustrator, Figma, or Inkscape.

---

## 2. Journal Export Targets

| Target Venue / Use Case | Recommended Aspect / Dimensions | Required Formats | Minimum Resolution |
| :--- | :--- | :--- | :--- |
| **Elsevier Graphical Abstract** (*CEUS*, *Cities*, *SCS*, *B&E*, *AutCon*) | Landscape `5:2` to `16:9` (e.g., `16.0 × 6.4 in` or `16.0 × 9.0 in`) | 300 DPI PNG + editable SVG master | `≥ 1328 × 531 px` (aim for `≥ 3000 px` wide at 300 DPI) |
| **Manuscript Figure 1 (Double-Column Width)** | `16.0 × 10.0 in` (16:10) or `16.0 × 9.0 in` (16:9), printed at `180–190 mm` wide | Editable **SVG** + 300–600 DPI PNG | 300 DPI minimum; 600 DPI if fine line art |
| **Vertical Analytical Spine (2-Column Tall / Full-Page)** | `11.0 × 13.5 in` or `12.0 × 14.0 in` | Editable **SVG** + 300 DPI PNG | 300 DPI |
| **ISPRS Annals / Copernicus Two-Column** | `16.0 × 9.0 in` (16:9) or `16.0 × 10.0 in` | Editable **SVG** + 300 DPI PNG | 300 DPI |
| **GitHub README / Project Page Hero Banner** | `16.0 × 9.0 in` or `16.0 × 10.0 in` | PNG (sRGB) + SVG | `2400 × 1500 px` (150–300 DPI) |
