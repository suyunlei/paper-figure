"""
demo_studio_grey_voxcity.py — Archetype A Showcase
Studio Grey Exploded Spatial Pipeline (VoxCity / NUS UAL Style).

Generates high-resolution PNG + editable Type-42 vector PDF at:
  .agents/skills/paper-graphical-abstract/examples/output/demo_archetype_a_studio_grey.{png,pdf}
"""

from __future__ import annotations

from pathlib import Path
import sys

from matplotlib.colors import ListedColormap
from matplotlib.patches import Circle, Polygon, Rectangle
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ual_ga_kit import (
    PALETTES,
    create_canvas,
    draw_compact_colorbar,
    draw_diagonal_split,
    draw_file_badge,
    draw_icon,
    draw_iso_exploded_stack,
    draw_iso_layer_grid,
    draw_iso_voxel_city,
    draw_notched_frame,
    draw_ortho_flow,
    place_image_loupe,
    save_publication_figure,
)


def _make_synthetic_layers(n: int = 40) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Generate clean deterministic geospatial layers (TE, LC, BH, CH)."""
    yy, xx = np.meshgrid(np.linspace(0.0, 1.0, n), np.linspace(0.0, 1.0, n))

    # 1. Smooth terrain elevation
    terrain = (
        12.0 * np.exp(-((xx - 0.25) ** 2 + (yy - 0.72) ** 2) / 0.12)
        + 8.5 * np.exp(-((xx - 0.80) ** 2 + (yy - 0.25) ** 2) / 0.16)
        + 3.0 * np.sin(xx * 4.2) * np.cos(yy * 3.5)
    )

    # 2. Semantic land cover (0=urban ground, 1=road, 2=park grass, 3=building pad, 4=water)
    lc = np.zeros((n, n), dtype=int)
    lc[:, n // 2 - 1 : n // 2 + 2] = 1
    lc[n // 2 - 1 : n // 2 + 2, :] = 1
    lc[:11, n - 11 :] = 4
    lc[4:16, 4:15] = 2
    lc[n - 16 : n - 3, 4:14] = 2
    lc[22:32, 22:32] = 3
    lc[5:13, 24:31] = 3
    lc[24:35, 6:13] = 3

    # 3. Building heights
    bh = np.zeros((n, n), dtype=float)
    bh[22:31, 22:31] = 48.0
    bh[25:30, 25:30] = 74.0
    bh[5:12, 24:30] = 28.0
    bh[25:34, 6:12] = 36.0
    bh[6:12, 6:10] = 18.0

    # 4. Tree canopy height
    ch = np.zeros((n, n), dtype=float)
    rng = np.random.default_rng(19)
    for cx_c, cy_c, rad, h_m in [(0.24, 0.24, 0.12, 16.0), (0.20, 0.78, 0.11, 14.0), (0.65, 0.18, 0.08, 11.0)]:
        mask = ((xx - cx_c) ** 2 + (yy - cy_c) ** 2) < rad ** 2
        ch[mask] = h_m * (0.65 + 0.35 * rng.random(mask.sum()))
    ch[bh > 0] = 0.0

    return terrain, lc, bh, ch


def _make_simulation_fields(n: int = 48) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Generate clean urban environmental simulation fields (Solar, SVF, GVI, Greening)."""
    yy, xx = np.meshgrid(np.linspace(0.0, 1.0, n), np.linspace(0.0, 1.0, n))
    bmask = (
        ((xx > 0.56) & (xx < 0.78) & (yy > 0.56) & (yy < 0.78))
        | ((xx > 0.14) & (xx < 0.32) & (yy > 0.58) & (yy < 0.76))
        | ((xx > 0.58) & (xx < 0.76) & (yy > 0.14) & (yy < 0.30))
    )

    solar = 0.85 - 0.45 * np.exp(-((xx - 0.66) ** 2 + (yy - 0.66) ** 2) / 0.05) + 0.12 * np.sin(xx * 6.0)
    solar[bmask] = 0.96

    svf = 0.88 - 0.55 * np.exp(-((xx - 0.62) ** 2 + (yy - 0.62) ** 2) / 0.06) - 0.30 * np.exp(-((xx - 0.25) ** 2 + (yy - 0.66) ** 2) / 0.04)
    svf = np.clip(svf, 0.12, 0.98)
    svf[bmask] = 0.08

    gvi = 0.18 + 0.72 * np.exp(-((xx - 0.24) ** 2 + (yy - 0.25) ** 2) / 0.07) + 0.55 * np.exp(-((xx - 0.22) ** 2 + (yy - 0.82) ** 2) / 0.05)
    gvi = np.clip(gvi, 0.05, 0.95)
    gvi[bmask] = 0.04

    # Greening scenario improves cooling / shade comfort
    greening = np.clip(0.32 + 0.58 * np.exp(-((xx - 0.45) ** 2 + (yy - 0.48) ** 2) / 0.14) - 0.15 * bmask, 0.1, 0.96)
    return solar, svf, gvi, greening


def _draw_settings_column(ax, x: float, y: float, w: float, h: float) -> None:
    """Draw minimal white-outlined configuration panel inside Module 1."""
    ax.add_patch(
        Rectangle((x, y), w, h, facecolor="none", edgecolor="#FFFFFF", linewidth=1.35, zorder=3)
    )
    ax.text(x + w * 0.42, y + h + 0.16, "Settings", fontsize=10.5, fontweight="bold", color="#111111", ha="center", va="bottom", zorder=5)
    draw_icon(ax, "gear", x + w * 0.80, y + h + 0.25, size=0.28, color="#FFFFFF", lw=1.55, zorder=5)

    # Slot 1: Target area miniature map outline
    s1_x, s1_y, s1_s = x + (w - 0.94) * 0.5, y + h - 1.25, 0.94
    ax.add_patch(Rectangle((s1_x, s1_y), s1_s, s1_s, facecolor="#C7CBD1", edgecolor="#FFFFFF", lw=1.0, zorder=4))
    for rx in (0.28, 0.66):
        ax.plot([s1_x + rx * s1_s, s1_x + rx * s1_s], [s1_y, s1_y + s1_s], color="#FFFFFF", lw=0.7, zorder=4.1)
    for ry in (0.34, 0.72):
        ax.plot([s1_x, s1_x + s1_s], [s1_y + ry * s1_s, s1_y + ry * s1_s], color="#FFFFFF", lw=0.7, zorder=4.1)
    ax.add_patch(Rectangle((s1_x + 0.20, s1_y + 0.20), 0.54, 0.54, facecolor="none", edgecolor="#FFFFFF", lw=1.4, zorder=4.4))
    ax.text(x + w * 0.5, s1_y - 0.12, "Target area", fontsize=8.8, color="#111111", ha="center", va="top", zorder=5)

    # Slot 2: Data sources selector card
    s2_x, s2_y, s2_w, s2_h = x + 0.13, y + 2.38, w - 0.26, 1.08
    ax.add_patch(Rectangle((s2_x, s2_y), s2_w, s2_h, facecolor="#ECEEF1", edgecolor="#FFFFFF", lw=1.0, zorder=4))
    ax.add_patch(Rectangle((s2_x, s2_y + s2_h - 0.26), s2_w, 0.26, facecolor="#D9DBDE", edgecolor="#FFFFFF", lw=0.9, zorder=4.2))
    for i, src in enumerate(["OpenStreetMap", "EUBUCCO v0.1", "META Canopy"]):
        ax.text(s2_x + 0.08, s2_y + s2_h - 0.42 - i * 0.24, src, fontsize=7.6, color="#2B3139", ha="left", va="center", zorder=4.5)
    ax.text(x + w * 0.5, s2_y - 0.12, "Data sources", fontsize=8.8, color="#111111", ha="center", va="top", zorder=5)

    # Slot 3: Mesh size wireframe cube
    cube_cy = y + 0.92
    draw_icon(ax, "iso_cube", x + w * 0.5, cube_cy, size=0.72, color="#FFFFFF", lw=1.65, zorder=5)
    ax.plot([x + 0.22, x + w - 0.22], [cube_cy - 0.44, cube_cy - 0.44], color="#FFFFFF", lw=1.1, zorder=5)
    ax.text(x + w * 0.5, cube_cy - 0.54, "Mesh size (2 m)", fontsize=8.8, color="#111111", ha="center", va="top", zorder=5)


def build_demo(out_stem: Path) -> None:
    pal = PALETTES["studio_grey"]
    fig, ax = create_canvas(
        figsize=(16.0, 10.0),
        theme="studio_grey",
        dpi=300,
        title="VoxCity: Automated 3D Semantic Voxel Modeling & Urban Simulation",
        subtitle="Open geospatial integration  ->  grid-based semantic voxel generation  ->  microclimate simulation  ->  interoperable export",
        title_x=0.35,
        title_y=9.68,
    )

    terrain, lc, bh, ch = _make_synthetic_layers()
    solar, svf, gvi, greening = _make_simulation_fields()
    lc_cmap = ListedColormap(["#AEB5BF", "#47505C", "#5E9E4C", "#C84B37", "#2F6FA3"])

    # -----------------------------------------------------------------------
    # Module 1: Open Data & Configuration (left)
    # -----------------------------------------------------------------------
    draw_notched_frame(ax, 0.34, 0.40, 5.20, 8.28, "1. Open Data & Configuration", bg_color=pal["bg"])
    _draw_settings_column(ax, 0.56, 1.32, 1.44, 6.20)

    # Download icon & flow to exploded layers
    draw_icon(ax, "cloud_download", 2.38, 7.62, size=0.44, color="#FFFFFF", lw=1.7)
    ax.text(2.38, 7.22, "Download", fontsize=9.2, color="#111111", ha="center", va="top", zorder=6)
    draw_ortho_flow(ax, [(2.00, 6.72), (2.78, 6.72)], color="#FFFFFF", lw=1.8, chevrons=3, chevron_size=0.09)

    m1_layers = [
        {"data": terrain, "cmap": "terrain", "label": "Terrain elevation"},
        {"data": lc, "cmap": lc_cmap, "vmin": 0, "vmax": 4, "label": "Land cover"},
        {"data": bh, "cmap": "viridis", "label": "Building height"},
        {"data": ch, "cmap": ListedColormap(["#EAECEF", "#B6DB9C", "#6FB857", "#3A8732"]), "vmin": 0, "vmax": 16, "label": "Canopy height"},
    ]
    draw_iso_exploded_stack(ax, m1_layers, cx=3.95, cy=4.48, size=1.80, dz=0.98)
    ax.text(3.95, 0.86, "Multi-source 2D geospatial layers", fontsize=9.6, fontweight="bold", color="#111111", ha="center", va="top", zorder=6)

    # -----------------------------------------------------------------------
    # Inter-module Flow 1 -> 2
    # -----------------------------------------------------------------------
    draw_ortho_flow(ax, [(5.44, 6.32), (6.48, 6.32)], color="#FFFFFF", lw=1.85, chevrons=3, chevron_pos=0.38, chevron_size=0.10, zorder=7)
    draw_icon(ax, "iso_cube", 5.82, 7.18, size=0.40, color="#FFFFFF", lw=1.65, zorder=8)
    ax.text(5.82, 6.80, "Voxelization", fontsize=9.0, color="#111111", ha="center", va="top", zorder=8)

    # -----------------------------------------------------------------------
    # Module 2: 3D Semantic Voxel Generation (center)
    # -----------------------------------------------------------------------
    draw_notched_frame(ax, 6.10, 0.40, 3.85, 8.28, "2. 3D Semantic Voxel Generation", bg_color=pal["bg"])

    m2_layers = [
        {"data": terrain, "cmap": "copper", "label": "Terrain"},
        {"data": lc, "cmap": lc_cmap, "vmin": 0, "vmax": 4, "label": "Land cover"},
        {"data": bh, "cmap": "cividis", "label": "Building"},
        {"data": ch, "cmap": ListedColormap(["#EAECEF", "#A8D58E", "#5CA84A", "#2F7D2C"]), "vmin": 0, "vmax": 16, "label": "Tree"},
    ]
    draw_iso_exploded_stack(ax, m2_layers, cx=8.04, cy=6.32, size=1.62, dz=0.60)

    # Vertical Y-merge integration flow
    draw_ortho_flow(ax, [(8.04, 4.72), (8.04, 3.68)], color="#FFFFFF", lw=1.85, chevrons=3, chevron_pos=0.52, chevron_size=0.095, zorder=7)
    draw_icon(ax, "y_merge", 7.30, 4.30, size=0.38, color="#FFFFFF", lw=1.7, zorder=8)
    ax.text(7.30, 3.94, "Integration", fontsize=9.0, color="#111111", ha="center", va="top", zorder=8)

    draw_iso_voxel_city(ax, cx=8.04, cy=2.04, size=1.84, grid_n=14, seed=7, show_prism=True, prism_color="#FFFFFF")
    ax.text(8.04, 0.86, "Semantic Voxel City Model", fontsize=9.8, fontweight="bold", color="#111111", ha="center", va="top", zorder=6)

    # -----------------------------------------------------------------------
    # Inter-module Flow 2 -> 3 & 2 -> 4
    # -----------------------------------------------------------------------
    draw_ortho_flow(
        ax,
        [(9.62, 2.32), (10.23, 2.32), (10.23, 6.24), (10.82, 6.24)],
        color="#FFFFFF", lw=1.85, chevrons=3, chevron_seg=1, chevron_pos=0.50, chevron_size=0.10, zorder=7,
    )

    # -----------------------------------------------------------------------
    # Module 3: Urban Environment Simulation (upper right)
    # -----------------------------------------------------------------------
    draw_notched_frame(ax, 10.52, 3.36, 5.14, 5.32, "3. Urban Environment Simulation", bg_color=pal["bg"])

    draw_icon(ax, "line_chart", 11.12, 4.92, size=0.38, color="#FFFFFF", lw=1.65, zorder=8)
    ax.text(11.12, 4.56, "Simulation", fontsize=8.8, color="#111111", ha="center", va="top", zorder=8)

    m3_layers = [
        {"data": gvi, "cmap": "viridis", "label": "Green View Index"},
        {"data": svf, "cmap": "ual_ocean_gold", "label": "Sky View Factor"},
        {"data": solar, "cmap": "inferno", "label": "Solar Irradiance"},
    ]
    draw_iso_exploded_stack(ax, m3_layers, cx=12.24, cy=6.32, size=1.64, dz=0.70)

    # Zoom Loupe zooming into top solar heatmap
    solar_zoom = solar[12:38, 12:38]
    loupe_cx, loupe_cy, loupe_r = 14.62, 7.20, 0.80
    import matplotlib as mpl
    solar_rgba = mpl.colormaps["inferno"](solar_zoom)
    place_image_loupe(
        ax,
        solar_rgba,
        cx=loupe_cx,
        cy=loupe_cy,
        radius=loupe_r,
        rim_color="#FFFFFF",
        rim_lw=2.0,
        label="Street-level zoom",
        label_pos="bottom",
        label_color="#111111",
        label_size=8.6,
        zorder=10,
    )
    # Tangent dotted zoom lines from top simulation layer to loupe rim
    ax.plot([12.50, loupe_cx - loupe_r * 0.45], [7.30, loupe_cy + loupe_r * 0.85], color="#FFFFFF", lw=1.35, ls=(0, (1.4, 1.8)), zorder=9.5)
    ax.plot([12.82, loupe_cx - loupe_r * 0.30], [6.90, loupe_cy - loupe_r * 0.90], color="#FFFFFF", lw=1.35, ls=(0, (1.4, 1.8)), zorder=9.5)

    # Diagonal Split Comparison (Baseline vs Greening)
    draw_diagonal_split(
        ax,
        solar,
        greening,
        x=13.84,
        y=3.92,
        w=1.56,
        h=1.56,
        cmap_left="inferno",
        cmap_right="ual_ocean_gold",
        split_color="#FFFFFF",
        split_lw=2.0,
        label_left="Baseline",
        label_right="Greening",
        zorder=7,
    )
    ax.text(14.62, 3.74, "Scenario contrast", fontsize=8.6, fontweight="bold", color="#111111", ha="center", va="top", zorder=8)

    # Compact horizontal colorbar beneath simulation stack
    draw_compact_colorbar(
        ax,
        x=11.16,
        y=3.84,
        w=2.16,
        h=0.16,
        cmap="inferno",
        vmin_label="Low (0.1)",
        vmax_label="High (0.95)",
        title="Irradiance / Index",
        text_color="#111111",
        fontsize=7.8,
        zorder=8,
    )

    # -----------------------------------------------------------------------
    # Module 4: Output Format & Export Ecosystem (lower right)
    # -----------------------------------------------------------------------
    draw_notched_frame(ax, 10.52, 0.40, 5.14, 2.60, "4. Output Format & Export Ecosystem", bg_color=pal["bg"])

    # Flow from Voxel city (Module 2) into Module 4 horizontal bus
    draw_ortho_flow(ax, [(9.56, 1.94), (14.90, 1.94)], color="#FFFFFF", lw=1.8, chevrons=3, chevron_pos=0.125, chevron_size=0.09, zorder=7)
    draw_icon(ax, "export_arrow", 12.66, 2.46, size=0.36, color="#FFFFFF", lw=1.65, zorder=8)
    ax.text(12.96, 2.46, "File export", fontsize=9.0, fontweight="bold", color="#111111", ha="left", va="center", zorder=8)

    badges = [
        ("INX", "ENVI-met", "Microclimate", 11.24),
        ("OBJ", "Blender / Rhino", "3D Render", 12.46),
        ("VOX", "MagicaVoxel", "Voxel Mesh", 13.68),
        ("GPKG", "GeoPackage", "GIS / QGIS", 14.90),
    ]
    for ext, name, sub, bx in badges:
        draw_ortho_flow(ax, [(bx, 1.94), (bx, 1.54)], color="#FFFFFF", lw=1.55, chevrons=0, zorder=6)
        draw_file_badge(
            ax,
            ext=ext,
            cx=bx,
            cy=1.28,
            size=0.40,
            name=name,
            sublabel=sub,
            stroke=pal["badge_stroke"],
            text_color="#111111",
            sub_color="#3E454E",
            bg_fill="#FFFFFF",
            zorder=8,
        )

    save_publication_figure(fig, out_stem, formats=("png", "svg"), dpi=300)


if __name__ == "__main__":
    out = ROOT / "examples" / "output" / "demo_archetype_a_studio_grey"
    build_demo(out)
    print(f"[OK] Saved {out}.png and {out}.svg")
