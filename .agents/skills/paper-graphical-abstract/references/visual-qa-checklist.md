# Visual QA Checklist & Journal Export Standards

Inspect every rendered PNG (via `read_file` / image viewer) **and** every exported vector file (`.svg` and/or `.pdf`) before considering a Graphical Abstract complete.

## 1. 12-Point Visual Self-Critique Rubric

1. **5-Second Narrative Glance**: Without reading small labels, can a reviewer trace the left-to-right or top-to-bottom story (`Input → Core Method → Output/Impact`) in under 5 seconds?
2. **90/10 Color Restraint**: Does the neutral canvas (`#D9DBDE` or `#FFFFFF`) plus matte greys dominate the image, leaving vivid color strictly on scientific data/focal targets (`audit_figure.py` high-saturation fraction `< 28%`)?
3. **50% Zoom Legibility**: View the image scaled down to ~50% width (manuscript column / ScienceDirect Graphical Abstract card). Is every module header, layer label, micro-colorbar endpoint, and table value crisp and readable?
4. **Zero Collisions or Occlusion**: Confirm zero text crosses frame lines, arrow shafts, neighboring labels, or circular loupes. In `editorial_studio.py`, verify all callouts sit on top-most `ann_ax` (`zorder=30`) so placed `sub_ax` images never clip or bury annotations.
5. **Edge Clearance & Margin Discipline**: No frame, badge, or label touches the outer `1.5%–2%` edge of the canvas (`audit_figure.py` edge-clipping check passes).
6. **Isometric Parallel Consistency & Alpha-Union Alignment**: Do all 3D layers, voxel/cut-cell blocks, and tilted GNN planes share an identical 30° parallel projection? Verify multi-layer 3D stacks were cropped with `crop_stack_alpha_union` so corners align vertically.
7. **Depth Sorting Integrity**: Verify front buildings/trees/voxels cleanly occlude back geometry with zero Z-fighting or reversed faces.
8. **White-Halo & Backing Contrast**: Over-layer `-30°` labels carry a `2.5 pt` `#FFFFFF` halo (`withStroke`), and 3D callout text carries a `CANVAS_BG` translucent pill backing (`alpha=0.82–0.85`).
9. **Physical-Aspect-Corrected Connectors**: Verify horizontal and vertical `>>>` chevrons have identical angles and proportions (`draw_dotted_chevrons`), and cross-module links follow orthogonal rails without crossing panels.
10. **3D→2D Sub-Pixel Anchor Precision**: Confirm every 3D callout arrow lands cleanly on its intended landmark (`sightline`, `viewpoint`, `landmark`, `envelope`, `park`) via projected `[u, v]` coordinates from `anchors.json`.
11. **Zero AI-Slop Artifacts**: Verify zero drop shadows, zero glossy rounded cards, zero bloated prose, and zero generative AI textures substituting for real renders.
12. **Vector Integrity (`--svg` and/or `--pdf`)**: Run `audit_figure.py` with `--svg` and/or `--pdf` to confirm valid SVG `<text>` nodes (`svg.fonttype = 'none'`) and selectable Type-42 PDF fonts (`pdf.fonttype = 42`).

---

## 2. Journal Export Targets

| Target Venue / Use Case | Recommended Aspect / Dimensions | Required Formats | Minimum Resolution |
| :--- | :--- | :--- | :--- |
| **Architectural Studio Editorial** (*CEUS* / *Cities* / *SCS* / *ISPRS*) | `16.0 × 9.6 in` wide landscape | 240–300 DPI PNG + vector PDF &/or SVG | `3840 × 2304 px` (240 DPI) to `4800 × 2880 px` (300 DPI) |
| **Elsevier Graphical Abstract** | Landscape `5:2` to `16:9` (e.g., `16.0 × 6.4 in` or `16.0 × 9.0 in`) | 300 DPI PNG + vector PDF / SVG master | `≥ 1328 × 531 px` |
| **Manuscript Figure 1 (Double-Column Width)** | `16.0 × 10.0 in` or `16.0 × 9.6 in`, printed at `180–190 mm` wide | Vector **SVG / PDF** + 300 DPI PNG | 300 DPI minimum |
| **Vertical Analytical Spine (2-Column Tall / Full-Page)** | `11.0 × 13.5 in` or `12.0 × 14.0 in` | Vector **SVG / PDF** + 300 DPI PNG | 300 DPI |
| **GitHub README / Project Page Hero Banner** | `16.0 × 9.6 in` or `16.0 × 10.0 in` | PNG (sRGB) + SVG | `2400 × 1500 px` (150–300 DPI) |
