"""
demo_editorial_studio.py — Architectural Studio Editorial Flagship Demo (Two-Stage Engine)

Demonstrates the complete Stage-A (cached transparent RGBA PNGs + alpha-union stack crop +
3D->2D [u, v] sub-pixel anchor JSON) -> Stage-B (16.0 x 9.6 in #D9DBDE canvas + top-most ann_ax +
physical-aspect-corrected chevrons + micro-colorbars + doc cards) pipeline without requiring PyVista.

Outputs:
  .agents/skills/paper-graphical-abstract/examples/output/demo_editorial_studio.{png,pdf,svg}
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from matplotlib.colors import ListedColormap, to_rgb
from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from editorial_studio import (
    ATTENUATION_DELTA_CMAP,
    CANVAS_BG,
    CHM_STUDIO_CMAP,
    DEM_STUDIO_CMAP,
    ENVELOPE_GLASS_CMAP,
    HIERARCHY_BLUES,
    INK,
    LINE_WHITE,
    MUTED_INK,
    STUDIO_MATERIALS,
    add_anchored_callout,
    add_micro_colorbar,
    apply_delta_noise_floor,
    create_studio_canvas,
    crop_stack_alpha_union,
    draw_doc_card,
    draw_dotted_chevrons,
    draw_line_icon,
    draw_orthogonal_rail,
    draw_section_frame,
    iso_project_3d,
    load_anchors_json,
    place_asset,
    project_ortho_3d_to_crop_uv,
    render_exploded_3d_layers,
    render_iso_raster_stack,
    save_anchors_json,
    save_editorial_figure,
    tight_crop_with_bbox,
)

OUT_DIR = ROOT / "examples" / "output"
CACHE_DIR = OUT_DIR / "editorial_studio_cache"

# Unified orthographic projection bounds for all 3D city bays (exact 14:13 ratio -> 1400x1300 px)
WORLD_XLIM = (-28.0, 28.0)
WORLD_YLIM = (-4.0, 48.0)
CITY_FIG_IN = (7.0, 6.5)
CITY_DPI = 200
CITY_FULL_WH = (int(CITY_FIG_IN[0] * CITY_DPI), int(CITY_FIG_IN[1] * CITY_DPI))


# ---------------------------------------------------------------------------
# Deterministic 3D SW-Top Orthographic Polyhedral Primitives
# ---------------------------------------------------------------------------

def _shade_rgb(hex_or_rgb, factor: float) -> tuple[float, float, float]:
    rgb = np.array(to_rgb(hex_or_rgb) if isinstance(hex_or_rgb, str) else hex_or_rgb[:3], dtype=float)
    return tuple(np.clip(rgb * factor, 0.0, 1.0))


def _draw_ortho_prism(
    ax: plt.Axes,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    z0: float,
    z1: float,
    top_col,
    left_col,
    right_col,
    edge_col: str = "none",
    lw: float = 0.0,
    alpha: float = 1.0,
    zorder: float = 4.0,
    slant_roof_dx: float = 0.0,
) -> None:
    """Draw 3D prism in SW-top isometric projection with optional pitched roof slope."""
    p = lambda x, y, z: iso_project_3d(x, y, z)
    zt_w = z1
    zt_e = z1 + slant_roof_dx

    # Left-facing vertical wall (x = x0)
    left_poly = [p(x0, y0, z0), p(x0, y1, z0), p(x0, y1, zt_w), p(x0, y0, zt_w)]
    # Front-right vertical wall (y = y0)
    right_poly = [p(x0, y0, z0), p(x1, y0, z0), p(x1, y0, zt_e), p(x0, y0, zt_w)]
    # Top face
    top_poly = [p(x0, y0, zt_w), p(x1, y0, zt_e), p(x1, y1, zt_e), p(x0, y1, zt_w)]

    for verts, fc in ((left_poly, left_col), (right_poly, right_col), (top_poly, top_col)):
        ax.add_patch(
            Polygon(
                verts,
                closed=True,
                facecolor=fc,
                edgecolor=edge_col if lw > 0 else "none",
                linewidth=lw,
                joinstyle="miter",
                alpha=alpha,
                zorder=zorder,
            )
        )


def _new_fullbleed_ortho_fig(
    figsize: tuple[float, float] = CITY_FIG_IN,
    dpi: int = CITY_DPI,
    xlim: tuple[float, float] = WORLD_XLIM,
    ylim: tuple[float, float] = WORLD_YLIM,
) -> tuple[plt.Figure, plt.Axes]:
    fig = plt.figure(figsize=figsize, dpi=dpi)
    fig.patch.set_alpha(0.0)
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    ax.set_facecolor("none")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    return fig, ax


def _fig_to_rgba(fig: plt.Figure) -> np.ndarray:
    fig.canvas.draw()
    rgba = np.asarray(fig.canvas.buffer_rgba(), dtype=np.uint8).copy()
    plt.close(fig)
    return rgba


def _site_geometry() -> dict:
    """Curated architectural district (twin towers, pitched-roof blocks, park, parcel)."""
    # Buildings: (id, x0, y0, x1, y1, h, slant_dx, is_landmark, has_delta)
    buildings = [
        ("tw_n", 18.0, 21.0, 25.0, 27.5, 16.5, 0.0, True, 0.01),
        ("tw_s", 18.0, 13.5, 25.0, 20.0, 13.5, 0.0, True, 0.02),
        ("b1", 3.0, 22.0, 9.5, 27.5, 4.8, 1.1, False, 0.09),
        ("b2", 11.0, 22.0, 16.5, 27.0, 5.8, -0.9, False, 0.14),
        ("b3", 3.0, 15.0, 8.8, 20.5, 6.4, 0.0, False, 0.16),
        ("b4", 10.5, 15.0, 16.2, 20.2, 5.2, 0.8, False, 0.12),   # central parcel building
        ("b5", 3.5, 8.0, 9.5, 13.5, 4.4, 1.0, False, 0.04),
        ("b6", 11.0, 8.2, 16.5, 13.2, 6.2, -1.0, False, 0.11),
        ("b7", 18.2, 6.8, 25.2, 11.8, 4.6, 0.8, False, 0.02),
        ("b8", 2.5, 2.5, 7.8, 6.8, 3.8, 0.0, False, 0.01),
        ("b9", 9.8, 2.5, 15.5, 6.6, 4.5, 0.9, False, 0.06),
        ("b10", 17.5, 2.2, 24.8, 5.6, 3.6, 0.0, False, 0.01),
    ]
    # Canopy tree blobs (x, y, z_base, size)
    trees = [
        (21.5, 12.6, 0.0, 1.1), (24.5, 12.8, 0.0, 1.2), (16.9, 17.5, 0.0, 1.0),
        (9.6, 18.0, 0.0, 0.95), (9.6, 23.0, 0.0, 1.0), (14.2, 7.4, 0.0, 0.95),
        (23.5, 20.6, 0.0, 1.05), (6.4, 14.2, 0.0, 0.9),
    ]
    return {"buildings": buildings, "trees": trees}


# ---------------------------------------------------------------------------
# Stage-A Renderers (Cached Transparent PNGs + Anchors JSON)
# ---------------------------------------------------------------------------

def _render_inputs_4layer(cache_dir: Path, force: bool) -> Path:
    out_p = cache_dir / "01_inputs_4layer.png"
    if out_p.exists() and not force:
        return out_p

    n = 44
    yy, xx = np.meshgrid(np.linspace(0.0, 1.0, n), np.linspace(0.0, 1.0, n))
    dem = (
        0.55 * np.exp(-((xx - 0.25) ** 2 + (yy - 0.72) ** 2) / 0.14)
        + 0.40 * np.exp(-((xx - 0.78) ** 2 + (yy - 0.28) ** 2) / 0.16)
    )
    dem_rgba = DEM_STUDIO_CMAP(np.clip(dem / max(dem.max(), 1e-6), 0.0, 1.0))

    # Desaturated studio landcover
    lc = np.zeros((n, n, 4), dtype=np.float32)
    lc[:, :] = [0.95, 0.96, 0.97, 1.0]
    lc[18:22, :] = [0.92, 0.93, 0.95, 1.0]
    lc[:, 20:24] = [0.92, 0.93, 0.95, 1.0]
    lc[6:16, 4:14] = [0.53, 0.80, 0.46, 1.0]
    lc[26:38, 28:40] = [0.82, 0.35, 0.29, 1.0]
    lc[8:20, 26:38] = [0.82, 0.35, 0.29, 1.0]
    lc[26:36, 8:20] = [0.82, 0.35, 0.29, 1.0]
    lc[:10, n - 10 :] = [0.17, 0.49, 0.80, 1.0]

    bh = np.zeros((n, n), dtype=float)
    bh[26:37, 29:39] = 0.92
    bh[8:20, 27:37] = 0.56
    bh[26:36, 8:19] = 0.65
    bh[6:15, 16:23] = 0.42
    bh_rgba = plt.get_cmap("viridis")(bh)
    bh_rgba[bh < 0.05, :3] = [0.17, 0.09, 0.28]

    ch = np.zeros((n, n), dtype=float)
    for cx_c, cy_c, rad in ((0.22, 0.25, 0.11), (0.38, 0.56, 0.09), (0.72, 0.44, 0.08)):
        m = ((xx - cx_c) ** 2 + (yy - cy_c) ** 2) < rad ** 2
        ch[m] = 0.78
    ch_rgba = CHM_STUDIO_CMAP(ch)

    layers = [
        ("Terrain elevation", dem_rgba),
        ("Land cover", lc),
        ("LoD2 buildings", bh_rgba),
        ("Canopy height", ch_rgba),
    ]
    return render_iso_raster_stack(layers, out_p, gap=0.72, figsize=(4.4, 6.2), dpi=300, label_fontsize=10.2, force=force)


def _render_city_mode(
    mode: str,
    site: dict,
    show_terrain: bool = True,
    show_buildings: bool = True,
    show_trees: bool = True,
    landcover_only: bool = False,
    clear_parcel: bool = False,
) -> tuple[np.ndarray, plt.Axes | None]:
    """Render one orthographic 3D layer or full city scene into an RGBA buffer."""
    fig, ax = _new_fullbleed_ortho_fig()
    p = lambda x, y, z: iso_project_3d(x, y, z)
    bnds = (0.0, 28.0, 0.0, 30.0)

    # White reference rim so alpha-union aligns cleanly across exploded layers
    if not show_terrain or landcover_only:
        rx = [bnds[0], bnds[1], bnds[1], bnds[0], bnds[0]]
        ry = [bnds[2], bnds[2], bnds[3], bnds[3], bnds[2]]
        pts_r = [p(x, y, 0.0) for x, y in zip(rx, ry)]
        ax.plot([q[0] for q in pts_r], [q[1] for q in pts_r], color=LINE_WHITE, lw=1.6, zorder=2)

    if show_terrain:
        skirt_col = (
            STUDIO_MATERIALS["dark_context_skirt"]
            if mode == "facade"
            else ("#6E757E" if mode == "delta" else STUDIO_MATERIALS["skirt_warm"])
        )
        ground_col = (
            STUDIO_MATERIALS["dark_context_terrain"]
            if mode == "facade"
            else ("#CED4DA" if mode == "delta" else ("#B9A696" if mode == "terrain_only" else "#E9ECEF"))
        )
        _draw_ortho_prism(
            ax, bnds[0], bnds[2], bnds[1], bnds[3], -1.8, 0.0,
            top_col=ground_col,
            left_col=_shade_rgb(skirt_col, 0.94),
            right_col=_shade_rgb(skirt_col, 0.80),
            zorder=2.0,
        )
        # Road corridors & park green patch
        if mode != "terrain_only":
            road_col = "#2A2F36" if mode == "facade" else "#F4F6F8"
            for rx0, ry0, rx1, ry1 in ((0.0, 12.2, 28.0, 13.6), (16.4, 0.0, 17.8, 30.0), (0.0, 6.8, 28.0, 7.9)):
                rp = [p(rx0, ry0, 0.02), p(rx1, ry0, 0.02), p(rx1, ry1, 0.02), p(rx0, ry1, 0.02)]
                ax.add_patch(Polygon(rp, closed=True, facecolor=road_col, edgecolor="none", zorder=2.2))

            park_col = "#2E4A36" if mode == "facade" else ("#7FD49B" if mode == "delta" else "#80BA8A")
            pk = [p(18.5, 11.8, 0.03), p(27.0, 11.8, 0.03), p(27.0, 13.4, 0.03), p(18.5, 13.4, 0.03)]
            ax.add_patch(Polygon(pk, closed=True, facecolor=park_col, edgecolor="none", zorder=2.3))

            if landcover_only:
                for _, bx0, by0, bx1, by1, *_ in site["buildings"]:
                    bp = [p(bx0, by0, 0.04), p(bx1, by0, 0.04), p(bx1, by1, 0.04), p(bx0, by1, 0.04)]
                    ax.add_patch(Polygon(bp, closed=True, facecolor="#D15A4A", edgecolor="none", zorder=2.4))

    # Build sorted list of 3D objects
    items = []
    if show_buildings and not landcover_only:
        for b in site["buildings"]:
            bid, x0, y0, x1, y1, bh, sdx, is_lm, dval = b
            if clear_parcel and bid == "b4":
                continue
            key = (-(0.5 * (x0 + x1) + 0.5 * (y0 + y1)), 0.5 * bh)
            items.append((key, "bldg", b))

    if show_trees and not landcover_only:
        for tx, ty, tz, tsz in site["trees"]:
            key = (-(tx + ty), tz + tsz)
            items.append((key, "tree", (tx, ty, tz, tsz)))

    if mode == "envelope":
        # Central parcel crimson ring + translucent Zmax cap
        px0, py0, px1, py1 = 10.3, 14.8, 16.4, 20.4
        ring_pts = [p(px0, py0, 0.15), p(px1, py0, 0.15), p(px1, py1, 0.15), p(px0, py1, 0.15), p(px0, py0, 0.15)]
        ax.plot([q[0] for q in ring_pts], [q[1] for q in ring_pts], color=STUDIO_MATERIALS["parcel_crimson"], lw=2.6, zorder=18)
        items.append(((-(0.5 * (px0 + px1) + 0.5 * (py0 + py1)), 5.0), "env", (px0, py0, px1, py1)))

    items.sort(key=lambda row: row[0])
    inf_cmap = plt.get_cmap("inferno")

    for step_i, (_k, kind, payload) in enumerate(items):
        zord = 4.0 + step_i * 0.25
        if kind == "bldg":
            bid, x0, y0, x1, y1, bh, sdx, is_lm, dval = payload
            if mode == "facade":
                val = min(1.0, 0.28 + bh / 20.0 + (0.20 if is_lm else 0.0))
                fc_base = inf_cmap(val)[:3]
                tc = [0.42, 0.45, 0.49]  # muted roof on heatmap
                lc = _shade_rgb(fc_base, 0.92)
                rc = _shade_rgb(fc_base, 0.78)
            elif mode == "delta":
                d_rgb = apply_delta_noise_floor(np.array([dval]), vmax=0.18, threshold=0.025)[0] / 255.0
                tc = to_rgb(STUDIO_MATERIALS["delta_neutral_roof"])
                lc = tuple(d_rgb)
                rc = _shade_rgb(d_rgb, 0.88)
            elif mode == "envelope":
                if is_lm:
                    tc = to_rgb(STUDIO_MATERIALS["highlight_roof"])
                    lc = to_rgb(STUDIO_MATERIALS["highlight_wall"])
                    rc = _shade_rgb(STUDIO_MATERIALS["highlight_wall"], 0.88)
                else:
                    tc = to_rgb(STUDIO_MATERIALS["desat_roof"])
                    lc = to_rgb(STUDIO_MATERIALS["desat_wall"])
                    rc = to_rgb(STUDIO_MATERIALS["desat_oblique"])
            else:
                tc = to_rgb(STUDIO_MATERIALS["roof_terracotta"])
                lc = to_rgb(STUDIO_MATERIALS["wall_main"])
                rc = to_rgb(STUDIO_MATERIALS["wall_oblique"]) if abs(sdx) > 0.1 else _shade_rgb(STUDIO_MATERIALS["wall_main"], 0.90)

            _draw_ortho_prism(
                ax, x0, y0, x1, y1, 0.0, bh,
                top_col=tc, left_col=lc, right_col=rc,
                edge_col="#9EA6B0" if mode == "studio" else "none",
                lw=0.25 if mode == "studio" else 0.0,
                zorder=zord, slant_roof_dx=sdx,
            )

        elif kind == "tree":
            tx, ty, tz, tsz = payload
            t_col = "#557058" if mode == "facade" else ("#3D8E52" if mode == "delta" else "#448B52")
            t_alpha = 0.68 if mode == "facade" else (0.36 if mode == "delta" else 0.90)
            _draw_ortho_prism(
                ax, tx - tsz, ty - tsz, tx + tsz, ty + tsz, tz + 0.5, tz + 2.4,
                top_col=t_col, left_col=_shade_rgb(t_col, 0.88), right_col=_shade_rgb(t_col, 0.76),
                alpha=t_alpha, zorder=zord,
            )

        elif kind == "env":
            px0, py0, px1, py1 = payload
            # Translucent multi-step Z_max sightline envelope
            for step_e, (ez0, ez1, frac) in enumerate([(0.2, 4.2, 0.18), (4.2, 8.2, 0.52), (8.2, 11.4, 0.92)]):
                col_e = ENVELOPE_GLASS_CMAP(frac)[:3]
                _draw_ortho_prism(
                    ax, px0 + step_e * 0.35, py0 + step_e * 0.2, px1 - step_e * 0.2, py1 - step_e * 0.3,
                    ez0, ez1,
                    top_col=col_e, left_col=_shade_rgb(col_e, 0.92), right_col=_shade_rgb(col_e, 0.82),
                    edge_col="#FFFFFF", lw=0.45, alpha=0.58, zorder=zord + step_e * 0.05,
                )

    if mode == "facade":
        # Translucent 60-deg cyan view cone emerging from tower window
        w_pt = p(18.0, 17.5, 10.5)
        c1 = p(10.0, 14.5, 7.0)
        c2 = p(10.0, 20.5, 13.5)
        cone_poly = [w_pt, c1, c2]
        ax.add_patch(
            Polygon(
                cone_poly,
                closed=True,
                facecolor=STUDIO_MATERIALS["view_cone_cyan"],
                edgecolor=STUDIO_MATERIALS["view_cone_edge"],
                linewidth=1.6,
                alpha=0.42,
                zorder=40,
            )
        )

    if mode == "envelope":
        # Plaza viewpoint pins + orange protected sightline rays
        pins = [(4.2, 16.5, 1.4), (5.0, 18.2, 1.4), (5.6, 19.6, 1.4)]
        targets = [(18.0, 15.8, 11.8), (18.0, 17.8, 13.4), (18.0, 22.8, 15.5)]
        for (ox, oy, oz), (tx, ty, tz) in zip(pins, targets):
            op = p(ox, oy, oz)
            og = p(ox, oy, 0.0)
            tp = p(tx, ty, tz)
            ax.plot([og[0], op[0]], [og[1], op[1]], color=STUDIO_MATERIALS["viewpoint_dark"], lw=1.8, zorder=35)
            ax.scatter([op[0]], [op[1]], s=28, facecolor="#FF5A26", edgecolor="#FFFFFF", lw=0.7, zorder=36)
            ax.add_patch(
                FancyArrowPatch(
                    op, tp,
                    arrowstyle="-|>,head_length=5.5,head_width=3.2",
                    color=STUDIO_MATERIALS["sightline_orange"],
                    linewidth=1.55,
                    zorder=37,
                )
            )

    rgba = _fig_to_rgba(fig)
    return rgba, None


def _render_core_stages(cache_dir: Path, force: bool) -> dict[str, Path]:
    paths = {
        "core1": cache_dir / "04_core_staircase.png",
        "core2": cache_dir / "05_core_octree.png",
        "core3": cache_dir / "06_core_cutcell.png",
        "core4a": cache_dir / "07_core_hybrid_intact.png",
        "core4b": cache_dir / "07_core_hybrid_cutaway.png",
    }
    if all(p.exists() for p in paths.values()) and not force:
        return paths

    # Shared helper for 500x420 crisp core widgets
    def _save_core(rgba: np.ndarray, dest: Path) -> None:
        pil, _ = tight_crop_with_bbox(rgba, pad=4)
        pil.save(dest)

    # 1. Staircase
    if force or not paths["core1"].exists():
        fig, ax = _new_fullbleed_ortho_fig((4.5, 3.8), 200, (-8.5, 8.5), (-2.0, 12.5))
        steps = []
        for ix in range(5):
            for iy in range(4):
                z_h = 2.0 + ix * 0.75 + iy * 0.45
                steps.append(((-(ix + iy), z_h), (ix, iy, z_h)))
        steps.sort(key=lambda r: r[0])
        for i, (_, (ix, iy, zh)) in enumerate(steps):
            _draw_ortho_prism(
                ax, -4.0 + ix * 1.5, -3.0 + iy * 1.5, -2.5 + ix * 1.5, -1.5 + iy * 1.5, 0.0, zh,
                top_col="#C27C62", left_col="#C4CAD1", right_col="#AEB6BF",
                edge_col="#4E5863", lw=0.65, zorder=4 + i * 0.1,
            )
        _save_core(_fig_to_rgba(fig), paths["core1"])

    # 2. Octree coalescing (8h, 4h, 2h blocks + ghost shell)
    if force or not paths["core2"].exists():
        fig, ax = _new_fullbleed_ortho_fig((4.5, 3.8), 200, (-8.5, 8.5), (-2.0, 12.5))
        oct_blocks = [
            (-3.2, -2.2, 0.0, 0.8, 0.0, 3.2, HIERARCHY_BLUES["8h"]),
            (0.0, -2.2, 2.8, 0.8, 0.0, 3.2, HIERARCHY_BLUES["8h"]),
            (-3.2, 0.8, -1.2, 2.8, 0.0, 2.2, HIERARCHY_BLUES["4h"]),
            (-1.2, 0.8, 0.8, 2.8, 0.0, 2.2, HIERARCHY_BLUES["4h"]),
            (0.8, 0.8, 2.8, 2.8, 0.0, 4.4, HIERARCHY_BLUES["4h"]),
            (-3.2, -2.2, -1.8, -0.6, 3.2, 4.4, HIERARCHY_BLUES["2h"]),
            (-1.6, -2.2, 0.0, -0.6, 3.2, 4.8, HIERARCHY_BLUES["2h"]),
            (0.2, -0.4, 2.4, 1.2, 3.2, 5.2, HIERARCHY_BLUES["2h"]),
        ]
        oct_blocks.sort(key=lambda b: (-(0.5 * (b[0] + b[2]) + 0.5 * (b[1] + b[3])), 0.5 * (b[4] + b[5])))
        for i, (x0, y0, x1, y1, z0, z1, col) in enumerate(oct_blocks):
            _draw_ortho_prism(
                ax, x0, y0, x1, y1, z0, z1,
                top_col=_shade_rgb(col, 1.12), left_col=col, right_col=_shade_rgb(col, 0.82),
                edge_col="#1D2E3F", lw=0.85, zorder=5 + i * 0.2,
            )
        _draw_ortho_prism(
            ax, -3.5, -2.5, 3.1, 3.1, 0.0, 6.2,
            top_col="#E8ECF0", left_col="#E8ECF0", right_col="#DCE2E8",
            edge_col="#9EA6B2", lw=0.45, alpha=0.18, zorder=25, slant_roof_dx=1.4,
        )
        _save_core(_fig_to_rgba(fig), paths["core2"])

    # 3. Single-voxel QEF cut-cell
    if force or not paths["core3"].exists():
        fig, ax = _new_fullbleed_ortho_fig((4.5, 3.8), 200, (-1.6, 1.6), (-0.4, 2.3))
        p = lambda x, y, z: iso_project_3d(x, y, z)
        # Solid lower half-space prism clipped cleanly
        _draw_ortho_prism(
            ax, 0.0, 0.0, 1.0, 1.0, 0.0, 0.88,
            top_col=STUDIO_MATERIALS["roof_terracotta"],
            left_col="#3B6E9C", right_col="#2D577E",
            edge_col="#FFFFFF", lw=1.0, alpha=0.88, zorder=8, slant_roof_dx=-0.38,
        )
        # Full unit cube wireframe edges
        corners = [(x, y, z) for x in (0, 1) for y in (0, 1) for z in (0, 1)]
        edges = [
            ((0,0,0),(1,0,0)), ((1,0,0),(1,1,0)), ((1,1,0),(0,1,0)), ((0,1,0),(0,0,0)),
            ((0,0,1),(1,0,1)), ((1,0,1),(1,1,1)), ((1,1,1),(0,1,1)), ((0,1,1),(0,0,1)),
            ((0,0,0),(0,0,1)), ((1,0,0),(1,0,1)), ((1,1,0),(1,1,1)), ((0,1,0),(0,1,1)),
        ]
        for a, b in edges:
            pa, pb = p(*a), p(*b)
            ax.plot([pa[0], pb[0]], [pa[1], pb[1]], color="#3E4752", lw=2.0, zorder=15)
        # Normal vector arrow
        p0 = p(0.50, 0.50, 0.72)
        p1 = p(0.92, 0.18, 1.38)
        ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>,head_length=6.0,head_width=3.6", color="#153D64", lw=2.4, zorder=20))
        _save_core(_fig_to_rgba(fig), paths["core3"])

    # 4a & 4b. Smooth intact cut-cell shell vs cutaway octree core
    if force or not paths["core4a"].exists():
        fig, ax = _new_fullbleed_ortho_fig((4.5, 3.8), 200, (-8.5, 8.5), (-2.0, 12.5))
        _draw_ortho_prism(
            ax, -3.5, -2.5, 3.1, 3.1, 0.0, 4.8,
            top_col=STUDIO_MATERIALS["roof_terracotta"],
            left_col=STUDIO_MATERIALS["wall_alt"],
            right_col=STUDIO_MATERIALS["wall_oblique"],
            edge_col="#9EA6B2", lw=0.4, zorder=10, slant_roof_dx=1.6,
        )
        _save_core(_fig_to_rgba(fig), paths["core4a"])

    if force or not paths["core4b"].exists():
        fig, ax = _new_fullbleed_ortho_fig((4.5, 3.8), 200, (-8.5, 8.5), (-2.0, 12.5))
        # Back shell half
        _draw_ortho_prism(
            ax, -3.5, 0.3, 3.1, 3.1, 0.0, 5.2,
            top_col=STUDIO_MATERIALS["roof_terracotta"],
            left_col=STUDIO_MATERIALS["wall_alt"],
            right_col=STUDIO_MATERIALS["wall_oblique"],
            zorder=8, slant_roof_dx=1.2,
        )
        _draw_ortho_prism(
            ax, 0.3, -2.5, 3.1, 0.3, 0.0, 5.6,
            top_col=STUDIO_MATERIALS["roof_terracotta"],
            left_col=STUDIO_MATERIALS["wall_alt"],
            right_col=STUDIO_MATERIALS["wall_oblique"],
            zorder=9, slant_roof_dx=0.6,
        )
        # Exposed front SW octree core blocks
        sub_blocks = [
            (-3.4, -2.4, -1.2, 0.2, 0.0, 2.4, HIERARCHY_BLUES["8h"]),
            (-1.2, -2.4, 0.2, 0.2, 0.0, 2.4, HIERARCHY_BLUES["4h"]),
            (-3.4, -2.4, -2.0, -1.0, 2.4, 3.6, HIERARCHY_BLUES["2h"]),
            (-2.0, -2.4, -0.6, -1.0, 2.4, 3.6, HIERARCHY_BLUES["2h"]),
        ]
        for idx, (x0, y0, x1, y1, z0, z1, col) in enumerate(sub_blocks):
            _draw_ortho_prism(
                ax, x0, y0, x1, y1, z0, z1,
                top_col=_shade_rgb(col, 1.12), left_col=col, right_col=_shade_rgb(col, 0.82),
                edge_col="#1D2E3F", lw=0.75, zorder=12 + idx * 0.2,
            )
        _save_core(_fig_to_rgba(fig), paths["core4b"])

    return paths


def prepare_stage_a_assets(force: bool = False) -> dict[str, Path]:
    """Generate and cache all transparent RGBA assets + 3D->2D anchors JSON."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    site = _site_geometry()
    assets: dict[str, Path] = {}

    assets["inputs4"] = _render_inputs_4layer(CACHE_DIR, force)
    assets.update(_render_core_stages(CACHE_DIR, force))

    # Exploded 3D layers aligned via joint alpha union
    p_exp = CACHE_DIR / "02_exploded_3d_layers.png"
    if force or not p_exp.exists():
        r_terr, _ = _render_city_mode("terrain_only", site, show_terrain=True, show_buildings=False, show_trees=False)
        r_lc, _ = _render_city_mode("studio", site, show_terrain=True, show_buildings=False, show_trees=False, landcover_only=True)
        r_bldg, _ = _render_city_mode("studio", site, show_terrain=False, show_buildings=True, show_trees=False)
        r_tree, _ = _render_city_mode("studio", site, show_terrain=False, show_buildings=False, show_trees=True)
        render_exploded_3d_layers(
            [r_terr, r_lc, r_bldg, r_tree],
            ["Terrain", "Land cover", "Buildings", "Trees"],
            p_exp,
            y_step_frac=0.56,
            figsize=(4.4, 6.2),
            dpi=300,
            label_fontsize=10.2,
            force=force,
        )
    assets["layers3d"] = p_exp

    # Integrated city + Facade WSVI + Delta + Envelope (with sub-pixel anchors)
    for key, fname, mode, clear_p in (
        ("city3d", "03_integrated_city.png", "studio", False),
        ("facade3d", "08_vis_facade.png", "facade", False),
        ("phen3d", "09_vis_delta.png", "delta", False),
        ("env3d", "10_vis_envelope.png", "envelope", True),
    ):
        dest = CACHE_DIR / fname
        anc_p = CACHE_DIR / "10_anchors.json"
        if force or not dest.exists() or (key == "env3d" and not anc_p.exists()):
            rgba, _ = _render_city_mode(mode, site, clear_parcel=clear_p)
            cropped, cbox = tight_crop_with_bbox(rgba, pad=4)
            cropped.save(dest)
            if key == "env3d":
                pts_3d = {
                    "viewpoint": (4.8, 17.6, 1.4),
                    "sightline": (11.5, 19.6, 8.2),
                    "landmark": (20.5, 24.0, 16.5),
                    "envelope": (13.2, 17.5, 11.4),
                    "park": (22.8, 12.6, 0.2),
                }
                anchors = {
                    k: project_ortho_3d_to_crop_uv(pt, WORLD_XLIM, WORLD_YLIM, CITY_FULL_WH, cbox)
                    for k, pt in pts_3d.items()
                }
                save_anchors_json(anchors, anc_p)
        assets[key] = dest

    assets["anchors_json"] = CACHE_DIR / "10_anchors.json"
    return assets


# ---------------------------------------------------------------------------
# Stage-B Normalized Composition (16.0 x 9.6 in Studio Editorial Canvas)
# ---------------------------------------------------------------------------

def build_editorial_studio_demo(force_assets: bool = False) -> list[Path]:
    assets = prepare_stage_a_assets(force=force_assets)

    fig, ax, ann_ax = create_studio_canvas(
        figsize=(16.0, 9.6),
        dpi=300,
        title="VoxVista",
        subtitle="Boundary-preserving hybrid voxel twins for 3D urban modeling, window views, and sightline planning",
        title_x=0.022,
        subtitle_x=0.132,
        header_y=0.956,
    )

    # ── 4 Square-Corner White Hairline Modules ────────────────────────────────
    draw_section_frame(ax, 0.022, 0.492, 0.520, 0.416, "1. Hybrid 3D city model generation", mask_w=0.232)
    draw_section_frame(ax, 0.564, 0.492, 0.414, 0.416, "2. Core representation: cut-cell & octree", mask_w=0.278)
    draw_section_frame(ax, 0.022, 0.024, 0.728, 0.436, "3. 3D visibility, phenology & sightline planning", mask_w=0.312)
    draw_section_frame(ax, 0.774, 0.024, 0.204, 0.436, "4. Open export & bridge", mask_w=0.156)

    # ── MODULE 1 ──────────────────────────────────────────────────────────────
    draw_line_icon(ax, "cloud", 0.095, 0.874, s=0.014)
    ax.text(0.095, 0.835, "Multi-source inputs", fontsize=9.6, fontweight="bold", color=INK, ha="center", va="center")
    place_asset(ax, assets["inputs4"], 0.028, 0.506, 0.162, 0.812, zorder=11)

    draw_line_icon(ax, "cube", 0.185, 0.874, s=0.0135)
    ax.text(0.185, 0.832, "Hybrid\nvoxelization", fontsize=9.2, fontweight="bold", color=INK, ha="center", va="center")
    for yy_arr in (0.764, 0.696, 0.628, 0.560):
        draw_dotted_chevrons(ax, [(0.158, yy_arr), (0.214, yy_arr)], chev_seg_idx=0, chev_pos=0.52)

    place_asset(ax, assets["layers3d"], 0.204, 0.502, 0.352, 0.892, zorder=11)

    draw_line_icon(ax, "merge", 0.364, 0.762, s=0.0115)
    ax.text(0.364, 0.728, "Integration", fontsize=8.8, fontweight="bold", color=INK, ha="center", va="center")
    draw_dotted_chevrons(ax, [(0.346, 0.694), (0.382, 0.694)], chev_seg_idx=0, chev_pos=0.52)

    place_asset(ax, assets["city3d"], 0.376, 0.556, 0.540, 0.884, zorder=11)
    ax.text(0.460, 0.535, "Hybrid city model", fontsize=10.4, fontweight="bold", color=INK, ha="center", va="center")
    ax.text(0.460, 0.512, "0.5 m cut-cells · Kanda-Surugadai", fontsize=7.9, color=MUTED_INK, ha="center", va="center")

    # ── MODULE 2 (2 x 2 Core Algorithm Flow) ──────────────────────────────────
    place_asset(ax, assets["core1"], 0.572, 0.734, 0.730, 0.892, zorder=12)
    ax.text(0.651, 0.720, "Uniform staircase (1h)", fontsize=8.8, fontweight="bold", color=INK, ha="center", va="center")
    ax.text(0.651, 0.703, "Jagged walls & roofs", fontsize=7.4, color=MUTED_INK, ha="center", va="center")

    place_asset(ax, assets["core2"], 0.782, 0.734, 0.962, 0.892, zorder=12)
    ax.text(0.872, 0.720, "Interior octree coalescing", fontsize=8.8, fontweight="bold", color=INK, ha="center", va="center")
    for si, lbl_s in enumerate(("8h", "4h", "2h")):
        bx = 0.822 + si * 0.036
        ax.add_patch(Rectangle((bx, 0.697), 0.009, 0.012, facecolor=HIERARCHY_BLUES[lbl_s], edgecolor="#222", lw=0.5, zorder=13))
        ax.text(bx + 0.012, 0.703, lbl_s, fontsize=7.3, fontweight="bold", color=MUTED_INK, va="center", ha="left", zorder=13)

    r_core3 = place_asset(ax, assets["core3"], 0.578, 0.532, 0.722, 0.668, zorder=12)
    ann_ax.text(r_core3[0] + 0.90 * r_core3[2], r_core3[1] + 0.91 * r_core3[3], r"$\hat{\mathbf{n}}$", fontsize=9.6, fontweight="bold", color="#153D64", ha="center", va="center")
    ax.text(0.651, 0.517, "Single-voxel cut-cell", fontsize=8.8, fontweight="bold", color=INK, ha="center", va="center")
    ax.text(0.651, 0.501, r"QEF $\mathbf{n}\cdot(\mathbf{x}-\mathbf{c})\leq d$", fontsize=7.6, color="#153D64", ha="center", va="center")

    place_asset(ax, assets["core4a"], 0.766, 0.546, 0.866, 0.668, zorder=12)
    place_asset(ax, assets["core4b"], 0.874, 0.546, 0.972, 0.668, zorder=12)
    ann_ax.plot([0.869, 0.869], [0.550, 0.660], linestyle=(0, (2.0, 2.0)), linewidth=1.0, color=LINE_WHITE, alpha=0.82)
    ann_ax.text(0.816, 0.535, "Outer shell", fontsize=7.2, color=MUTED_INK, ha="center", va="center")
    ann_ax.text(0.922, 0.535, "Cutaway core", fontsize=7.2, color=MUTED_INK, ha="center", va="center")
    ax.text(0.869, 0.517, "Boundary-preserving hybrid", fontsize=8.8, fontweight="bold", color=INK, ha="center", va="center")
    ax.text(0.869, 0.501, "Smooth cut-cells + octree core", fontsize=7.4, color=MUTED_INK, ha="center", va="center")

    draw_dotted_chevrons(ax, [(0.730, 0.813), (0.784, 0.813)], chev_seg_idx=0, chev_pos=0.50)
    draw_dotted_chevrons(ax, [(0.651, 0.696), (0.651, 0.669)], chev_seg_idx=0, chev_pos=0.50)
    draw_dotted_chevrons(ax, [(0.872, 0.696), (0.872, 0.669)], chev_seg_idx=0, chev_pos=0.50)
    draw_dotted_chevrons(ax, [(0.724, 0.602), (0.764, 0.602)], chev_seg_idx=0, chev_pos=0.50)

    # ── MODULE 3 (3D Visibility, Phenology & Sightline Showcase) ──────────────
    ann_ax.text(
        0.740, 0.442,
        "60° cut-cell frustum · single-pass 5-season canopy · reverse sightline solver",
        fontsize=8.1, color=MUTED_INK, ha="right", va="center",
    )

    place_asset(ax, assets["facade3d"], 0.026, 0.082, 0.264, 0.428, zorder=11)
    ann_ax.add_patch(Rectangle((0.036, 0.402), 0.0085, 0.0115, facecolor=STUDIO_MATERIALS["view_cone_cyan"], edgecolor=STUDIO_MATERIALS["view_cone_edge"], lw=0.85))
    ann_ax.text(0.048, 0.408, "60° view cone", fontsize=7.6, fontweight="bold", color="#107A94", ha="left", va="center")
    ann_ax.text(0.145, 0.062, "Window-view potential (facade)", fontsize=10.2, fontweight="bold", color=INK, ha="center", va="center")
    add_micro_colorbar(fig, ann_ax, 0.084, 0.036, 0.118, cmap="inferno", vmin_label="0", vmax_label="1 WSVI")

    place_asset(ax, assets["phen3d"], 0.268, 0.082, 0.506, 0.428, zorder=11)
    ann_ax.text(0.274, 0.415, "Winter → Summer Δ\n(facades + ground)", fontsize=7.4, color=MUTED_INK, ha="left", va="top", linespacing=1.28)
    ann_ax.text(0.387, 0.062, "Seasonal foliage attenuation", fontsize=10.2, fontweight="bold", color=INK, ha="center", va="center")
    add_micro_colorbar(fig, ann_ax, 0.322, 0.036, 0.118, cmap=ATTENUATION_DELTA_CMAP, vmin_label="0", vmax_label="≥0.18 Δ")

    r3c = place_asset(ax, assets["env3d"], 0.510, 0.082, 0.746, 0.428, zorder=11)
    ann_ax.text(0.628, 0.062, "3D sightline height envelope", fontsize=10.2, fontweight="bold", color=INK, ha="center", va="center")
    add_micro_colorbar(fig, ann_ax, 0.558, 0.036, 0.118, cmap=ENVELOPE_GLASS_CMAP, vmin_label="23", vmax_label="75m Z_max")

    anc = load_anchors_json(assets["anchors_json"])
    add_anchored_callout(ann_ax, r3c, anc["sightline"], "Protected\nsightlines", (0.512, 0.402), color=STUDIO_MATERIALS["sightline_orange"], ha="left")
    add_anchored_callout(ann_ax, r3c, anc["viewpoint"], "Viewpoints\n(plaza)", (0.512, 0.334), color=STUDIO_MATERIALS["viewpoint_dark"], ha="left")
    add_anchored_callout(ann_ax, r3c, anc["landmark"], "Landmark\ntower", (0.742, 0.402), color="#9A3F20", ha="right")
    add_anchored_callout(ann_ax, r3c, anc["envelope"], "Allowed Z_max\nenvelope", (0.742, 0.340), color="#0F3A5D", ha="right")
    add_anchored_callout(ann_ax, r3c, anc["park"], "Green park", (0.742, 0.282), color="#2B6B3B", ha="right")

    # ── MODULE 4 (Open Export & Bridge) ───────────────────────────────────────
    draw_line_icon(ax, "export", 0.798, 0.426, s=0.013)
    ax.plot([0.954, 0.954], [0.460, 0.398], linestyle=(0, (1.3, 2.0)), lw=1.7, color=LINE_WHITE, zorder=17)
    ax.plot([0.830, 0.954], [0.398, 0.398], linestyle=(0, (1.3, 2.0)), lw=1.7, color=LINE_WHITE, zorder=17)
    ax.plot([0.876, 0.876], [0.398, 0.260], linestyle=(0, (1.3, 2.0)), lw=1.7, color=LINE_WHITE, zorder=17)
    ax.plot([0.830, 0.830], [0.398, 0.377], linestyle=(0, (1.3, 2.0)), lw=1.7, color=LINE_WHITE, zorder=17)
    ax.plot([0.922, 0.922], [0.398, 0.377], linestyle=(0, (1.3, 2.0)), lw=1.7, color=LINE_WHITE, zorder=17)
    ax.plot([0.830, 0.922], [0.260, 0.260], linestyle=(0, (1.3, 2.0)), lw=1.7, color=LINE_WHITE, zorder=17)
    ax.plot([0.830, 0.830], [0.260, 0.241], linestyle=(0, (1.3, 2.0)), lw=1.7, color=LINE_WHITE, zorder=17)
    ax.plot([0.922, 0.922], [0.260, 0.241], linestyle=(0, (1.3, 2.0)), lw=1.7, color=LINE_WHITE, zorder=17)

    for cx_d, cy_d, ext, lbl, sub, col in [
        (0.830, 0.354, "H5", "HDF5", "CompactCity", "#153D64"),
        (0.922, 0.354, "NC", "NetCDF4", "CF sub-voxel", "#2B6CA3"),
        (0.830, 0.218, "OBJ", "Blender", "3D meshes", "#D96A29"),
        (0.922, 0.218, "GLB", "WebGL", "Three.js · Cesium", "#1F8A70"),
    ]:
        draw_doc_card(ax, cx_d, cy_d, ext, lbl, sub, accent=col)

    ax.plot([0.790, 0.962], [0.128, 0.128], color=LINE_WHITE, lw=1.1, alpha=0.85, zorder=12)
    ax.text(0.876, 0.095, "Bidirectional array &\nGeoDataFrame bridge", fontsize=8.3, color=MUTED_INK, ha="center", va="center", linespacing=1.35)
    ax.text(0.818, 0.048, "Python", fontsize=11.0, fontweight="bold", color="#2B6CA3", ha="center", va="center")
    ax.text(0.934, 0.048, "VoxCity", fontsize=11.0, fontweight="bold", color=INK, ha="center", va="center")
    ax.add_patch(FancyArrowPatch((0.854, 0.048), (0.896, 0.048), arrowstyle="<|-|>,head_length=4.5,head_width=2.8", color=INK, lw=1.55, zorder=15))

    # ── Inter-Module Orthogonal Rails & Chevrons ──────────────────────────────
    draw_dotted_chevrons(ax, [(0.542, 0.700), (0.564, 0.700)], chev_seg_idx=0, chev_pos=0.50)
    draw_orthogonal_rail(
        ax,
        sources=[(0.460, 0.492), (0.869, 0.492)],
        targets=[(0.386, 0.460), (0.954, 0.460)],
        rail_y=0.476,
    )
    draw_dotted_chevrons(ax, [(0.750, 0.242), (0.774, 0.242)], chev_seg_idx=0, chev_pos=0.50)

    out_stem = OUT_DIR / "demo_editorial_studio"
    written = save_editorial_figure(fig, out_stem, formats=("png", "pdf", "svg"), dpi=300)
    plt.close(fig)
    return written


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--force-assets", action="store_true")
    args = ap.parse_args()
    paths = build_editorial_studio_demo(force_assets=args.force_assets)
    print("[OK] Exported:", ", ".join(str(p) for p in paths))
