"""
editorial_studio.py — Architectural Studio Editorial Graphical Abstract Engine.

Distilled from VoxVista v6/v5 (NUS Urban Analytics Lab / CEUS studio editorial benchmark).
Provides:
  1. Design Tokens & Context-Desaturation Colormaps (studio grey #D9DBDE, clay/terracotta,
     blue-teal hierarchy, noise-suppressed Delta cmap, translucent glass envelope cmap).
  2. Decoupled Stage-A Deterministic Asset Helpers (alpha-union stack cropping, tight crop +
     3D->2D [u, v] sub-pixel anchor projection, exact 30-deg isometric raster stacks,
     cached off-screen transparent RGBA rendering, optional PyVista studio helpers).
  3. Stage-B Normalized Composition Primitives on [0, 1] x [0, 1] with a dedicated top-most
     transparent annotation layer (`ann_ax`, zorder=30) and physical-aspect-corrected chevrons
     & wireframe icons.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Iterable, Sequence

import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap, to_rgb
import matplotlib.patheffects as pe
from matplotlib.patches import FancyArrowPatch, Rectangle
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

# Ensure editable vector fonts in both SVG and PDF exports
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = [
    "Arial",
    "DejaVu Sans",
    "Liberation Sans",
    "Microsoft YaHei",
]

# ---------------------------------------------------------------------------
# 1. Design Tokens & Scientific Colormaps
# ---------------------------------------------------------------------------

CANVAS_BG = "#D9DBDE"
INK = "#111111"
SUBTITLE_INK = "#23282E"
MUTED_INK = "#3E454E"
LINE_WHITE = "#FFFFFF"
DOC_DARK = "#2D333B"

STUDIO_MATERIALS: dict[str, str] = {
    "wall_main": "#E2E4E7",
    "wall_alt": "#E4E6E8",
    "wall_oblique": "#D5DFE6",
    "roof_terracotta": "#CC6542",
    "skirt_warm": "#8C8782",
    "skirt_cool": "#8C9199",
    "dark_context_terrain": "#353B44",
    "dark_context_skirt": "#2A2F36",
    "desat_wall": "#E2E5E9",
    "desat_roof": "#CFD4DC",
    "desat_oblique": "#DAE0E6",
    "highlight_wall": "#C7D6E4",
    "highlight_roof": "#CC6542",
    "delta_neutral_wall": "#DDE1E6",
    "delta_neutral_roof": "#C4CBD3",
    "parcel_crimson": "#D93829",
    "sightline_orange": "#E05A2B",
    "viewpoint_dark": "#B83B1A",
    "view_cone_cyan": "#3EC6E0",
    "view_cone_edge": "#189AB4",
}

HIERARCHY_BLUES: dict[str, str] = {
    "8h": "#153D64",
    "4h": "#2E74A6",
    "2h": "#58B0A8",
}

FONT_STACK = ["Arial", "DejaVu Sans", "Liberation Sans", "Microsoft YaHei"]

TYPOGRAPHY_SCALE: dict[str, float] = {
    "main_title": 23.5,
    "subtitle": 12.2,
    "section_title": 11.0,
    "sub_title": 9.8,
    "step_title": 8.8,
    "annotation": 7.5,
}

ATTENUATION_DELTA_CMAP = LinearSegmentedColormap.from_list(
    "editorial_attenuation_delta",
    [
        (0.00, "#D5DBE1"),
        (0.10, "#8DE0AF"),
        (0.36, "#1FA172"),
        (0.70, "#F2B705"),
        (1.00, "#DC4C28"),
    ],
    N=256,
)

ENVELOPE_GLASS_CMAP = LinearSegmentedColormap.from_list(
    "editorial_envelope_glass",
    ["#1E6EA8", "#2FA8A8", "#8AD18A", "#F2C94C"],
    N=256,
)

DEM_STUDIO_CMAP = LinearSegmentedColormap.from_list(
    "editorial_dem_studio",
    ["#DCE3DC", "#B6C6B3", "#7F997A", "#686B56"],
    N=256,
)

CHM_STUDIO_CMAP = LinearSegmentedColormap.from_list(
    "editorial_chm_studio",
    ["#F7F9F7", "#88C988", "#1B6B33"],
    N=256,
)


def apply_delta_noise_floor(
    values: np.ndarray,
    vmax: float,
    threshold: float = 0.025,
    neutral_hex: str = "#DDE1E6",
) -> np.ndarray:
    """Color Delta values with noise-floor suppression so tiny deltas stay neutral clay."""
    vals = np.asarray(values, dtype=np.float64)
    norm = np.clip(vals / max(vmax, 1e-9), 0.0, 1.0)
    rgb = (ATTENUATION_DELTA_CMAP(norm)[..., :3] * 255.0).astype(np.uint8)
    neutral_rgb = (np.array(to_rgb(neutral_hex)) * 255.0).astype(np.uint8)
    rgb[vals < threshold] = neutral_rgb
    return rgb


# ---------------------------------------------------------------------------
# 2. Stage-B Normalized Dual-Layer Canvas & Composition Primitives
# ---------------------------------------------------------------------------

def create_studio_canvas(
    figsize: tuple[float, float] = (16.0, 9.6),
    dpi: int = 300,
    title: str | None = None,
    subtitle: str | None = None,
    title_x: float = 0.022,
    subtitle_x: float | None = None,
    header_y: float = 0.956,
    canvas_bg: str = CANVAS_BG,
) -> tuple[plt.Figure, plt.Axes, plt.Axes]:
    """Create normalized [0,1]x[0,1] studio canvas with top-most transparent `ann_ax`.

    Returns `(fig, ax, ann_ax)` where `ann_ax` sits at `zorder=30` with `facecolor="none"`
    so leader arrows, formulas, and callouts never clip behind `sub_ax` asset renders.
    """
    plt.rcParams["font.sans-serif"] = FONT_STACK
    fig = plt.figure(figsize=figsize, dpi=dpi, facecolor=canvas_bg)

    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0], zorder=0)
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.set_facecolor(canvas_bg)
    ax.set_autoscale_on(False)
    ax.axis("off")

    ann_ax = fig.add_axes([0.0, 0.0, 1.0, 1.0], zorder=30)
    ann_ax.set_xlim(0.0, 1.0)
    ann_ax.set_ylim(0.0, 1.0)
    ann_ax.set_facecolor("none")
    ann_ax.set_autoscale_on(False)
    ann_ax.axis("off")

    if title:
        ax.text(
            title_x,
            header_y,
            title,
            fontsize=TYPOGRAPHY_SCALE["main_title"],
            fontweight="bold",
            color=INK,
            ha="left",
            va="center",
            zorder=8,
        )
        if subtitle:
            sx = (
                subtitle_x
                if subtitle_x is not None
                else min(0.55, title_x + max(0.088, len(title) * 0.0112 + 0.022))
            )
            ax.text(
                sx,
                header_y - 0.001,
                subtitle,
                fontsize=TYPOGRAPHY_SCALE["subtitle"],
                fontweight="normal",
                color=SUBTITLE_INK,
                ha="left",
                va="center",
                zorder=8,
            )

    return fig, ax, ann_ax


def draw_section_frame(
    ax: plt.Axes,
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    mask_w: float | None = None,
    bg_color: str = CANVAS_BG,
    border_color: str = LINE_WHITE,
    lw: float = 1.6,
    title_size: float = 11.0,
    zorder: float = 4.0,
) -> None:
    """Draw sharp 90-deg pure-white hollow frame broken cleanly behind top-left title."""
    ax.add_patch(
        Rectangle(
            (x, y),
            w,
            h,
            facecolor="none",
            edgecolor=border_color,
            linewidth=lw,
            joinstyle="miter",
            zorder=zorder,
        )
    )
    if not title:
        return
    tx = x + 0.014
    ty = y + h
    mw = (
        mask_w
        if mask_w is not None
        else min(w - 0.024, max(0.075, len(title) * title_size * 0.00056 + 0.016))
    )
    ax.add_patch(
        Rectangle(
            (tx - 0.006, ty - 0.011),
            mw,
            0.022,
            facecolor=bg_color,
            edgecolor="none",
            zorder=zorder + 1.0,
        )
    )
    ax.text(
        tx,
        ty,
        title,
        fontsize=title_size,
        fontweight="bold",
        color=INK,
        va="center",
        ha="left",
        zorder=zorder + 2.0,
    )


def draw_dotted_chevrons(
    ax: plt.Axes,
    pts: Sequence[tuple[float, float]],
    chev_seg_idx: int | None = 0,
    chev_pos: float = 0.5,
    lw: float = 1.85,
    color: str = LINE_WHITE,
    chev_count: int = 3,
    chev_scale: float = 1.0,
    zorder: float = 18.0,
) -> None:
    """Draw white dotted flow line + physical-aspect-corrected `>>>` chevrons."""
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax.plot(
        xs,
        ys,
        linestyle=(0, (1.3, 2.0)),
        linewidth=lw,
        color=color,
        solid_capstyle="butt",
        zorder=zorder,
    )
    if chev_seg_idx is None or chev_seg_idx >= len(pts) - 1 or chev_count <= 0:
        return

    p0 = np.array(pts[chev_seg_idx], dtype=float)
    p1 = np.array(pts[chev_seg_idx + 1], dtype=float)
    dv = p1 - p0
    if np.linalg.norm(dv) < 1e-6:
        return

    fw, fh = ax.figure.get_size_inches()
    # Normalize direction in physical inches so horizontal & vertical chevrons match identically
    dv_in = np.array([dv[0] * fw, dv[1] * fh])
    u_in = dv_in / max(np.linalg.norm(dv_in), 1e-9)
    n_in = np.array([-u_in[1], u_in[0]])

    u_step = np.array([u_in[0] / fw, u_in[1] / fh]) * chev_scale
    n_step = np.array([n_in[0] / fw, n_in[1] / fh]) * chev_scale

    mid = p0 + dv * chev_pos
    offsets = np.linspace(-0.5 * (chev_count - 1), 0.5 * (chev_count - 1), chev_count)
    for k in offsets:
        tip = mid + k * 0.075 * u_step
        a = tip - 0.068 * u_step + 0.072 * n_step
        b = tip - 0.068 * u_step - 0.072 * n_step
        ax.plot(
            [a[0], tip[0], b[0]],
            [a[1], tip[1], b[1]],
            color=color,
            linewidth=max(lw, 1.95),
            solid_capstyle="round",
            solid_joinstyle="round",
            zorder=zorder + 2.0,
        )


def draw_orthogonal_rail(
    ax: plt.Axes,
    sources: Sequence[tuple[float, float]],
    targets: Sequence[tuple[float, float]],
    rail_y: float,
    lw: float = 1.8,
    color: str = LINE_WHITE,
    add_target_chevrons: bool = True,
    chev_pos: float = 0.50,
    zorder: float = 17.0,
) -> None:
    """Connect multiple module bottoms to downstream module tops via a single orthogonal rail."""
    all_x = [p[0] for p in sources] + [p[0] for p in targets]
    if not all_x:
        return
    ax.plot(
        [min(all_x), max(all_x)],
        [rail_y, rail_y],
        linestyle=(0, (1.3, 2.0)),
        linewidth=lw,
        color=color,
        solid_capstyle="butt",
        zorder=zorder,
    )
    for sx, sy in sources:
        ax.plot(
            [sx, sx],
            [sy, rail_y],
            linestyle=(0, (1.3, 2.0)),
            linewidth=lw,
            color=color,
            solid_capstyle="butt",
            zorder=zorder,
        )
    for tx, ty in targets:
        draw_dotted_chevrons(
            ax,
            [(tx, rail_y), (tx, ty)],
            chev_seg_idx=0 if add_target_chevrons else None,
            chev_pos=chev_pos,
            lw=lw,
            color=color,
            zorder=zorder,
        )


def draw_line_icon(
    ax: plt.Axes,
    kind: str,
    cx: float,
    cy: float,
    s: float = 0.0135,
    color: str = LINE_WHITE,
    lw: float = 1.65,
    zorder: float = 10.0,
) -> None:
    """Draw physical-aspect-corrected uniform-stroke wireframe icon in normalized coords."""
    fw, fh = ax.figure.get_size_inches()
    sx = s
    sy = s * (fw / fh)

    if kind == "cloud":
        th = np.linspace(0.0, math.pi, 30)
        xs_c = np.concatenate([
            [cx - 0.85 * sx],
            cx - 0.45 * sx + 0.40 * sx * np.cos(th[::-1]),
            cx + 0.12 * sx + 0.56 * sx * np.cos(th[::-1]),
            cx + 0.68 * sx + 0.34 * sx * np.cos(th[::-1]),
            [cx + 0.92 * sx, cx + 0.28 * sx],
        ])
        ys_c = np.concatenate([
            [cy - 0.25 * sy],
            cy - 0.10 * sy + 0.36 * sy * np.sin(th[::-1]),
            cy + 0.15 * sy + 0.56 * sy * np.sin(th[::-1]),
            cy - 0.08 * sy + 0.34 * sy * np.sin(th[::-1]),
            [cy - 0.25 * sy, cy - 0.25 * sy],
        ])
        ax.plot(xs_c, ys_c, color=color, linewidth=lw, solid_capstyle="round", zorder=zorder)
        ax.plot([cx - 0.85 * sx, cx - 0.28 * sx], [cy - 0.25 * sy, cy - 0.25 * sy], color=color, linewidth=lw, zorder=zorder)
        ax.plot([cx, cx], [cy + 0.12 * sy, cy - 0.62 * sy], color=color, linewidth=lw + 0.1, zorder=zorder + 1)
        ax.plot(
            [cx - 0.28 * sx, cx, cx + 0.28 * sx],
            [cy - 0.35 * sy, cy - 0.64 * sy, cy - 0.35 * sy],
            color=color, linewidth=lw + 0.1, solid_capstyle="round", zorder=zorder + 1,
        )

    elif kind == "cube":
        dx, dy = sx * 0.866, sy * 0.500
        top = [(cx, cy + sy), (cx + dx, cy + dy), (cx, cy), (cx - dx, cy + dy), (cx, cy + sy)]
        tx, ty = zip(*top)
        ax.plot(tx, ty, color=color, linewidth=lw, zorder=zorder)
        ax.plot(
            [cx - dx, cx - dx, cx, cx + dx, cx + dx],
            [cy + dy, cy - dy, cy - sy, cy - dy, cy + dy],
            color=color, linewidth=lw, zorder=zorder,
        )
        ax.plot([cx, cx], [cy, cy - sy], color=color, linewidth=lw, zorder=zorder)

    elif kind == "merge":
        ax.plot([cx - sx, cx, cx - sx], [cy + 0.7 * sy, cy, cy - 0.7 * sy], color=color, linewidth=lw, solid_capstyle="round", zorder=zorder)
        ax.plot([cx, cx + sx], [cy, cy], color=color, linewidth=lw, solid_capstyle="round", zorder=zorder)
        ax.plot([cx + 0.65 * sx, cx + sx, cx + 0.65 * sx], [cy + 0.35 * sy, cy, cy - 0.35 * sy], color=color, linewidth=lw, solid_capstyle="round", zorder=zorder)

    elif kind == "chart":
        ax.plot([cx - sx, cx - sx, cx + sx], [cy + sy, cy - sy, cy - sy], color=color, linewidth=lw, zorder=zorder)
        ax.plot(
            [cx - 0.65 * sx, cx - 0.1 * sx, cx + 0.3 * sx, cx + 0.85 * sx],
            [cy - 0.4 * sy, cy + 0.35 * sy, cy - 0.15 * sy, cy + 0.65 * sy],
            color=color, linewidth=lw, marker="o", markersize=2.6, zorder=zorder + 1,
        )

    elif kind == "export":
        ax.plot(
            [cx + 0.2 * sx, cx - sx, cx - sx, cx + sx, cx + sx],
            [cy + sy, cy + sy, cy - sy, cy - sy, cy + 0.1 * sy],
            color=color, linewidth=lw, zorder=zorder,
        )
        ax.plot([cx, cx + sx], [cy, cy + sy], color=color, linewidth=lw + 0.1, zorder=zorder + 1)
        ax.plot([cx + 0.35 * sx, cx + sx, cx + sx], [cy + sy, cy + sy, cy + 0.35 * sy], color=color, linewidth=lw + 0.1, zorder=zorder + 1)

    elif kind == "layers":
        for d in (-0.42 * sy, 0.0, 0.42 * sy):
            pts = [(cx - 0.88 * sx, cy + d), (cx, cy + d + 0.32 * sy), (cx + 0.88 * sx, cy + d), (cx, cy + d - 0.32 * sy), (cx - 0.88 * sx, cy + d)]
            px, py = zip(*pts)
            ax.plot(px, py, color=color, linewidth=lw * 0.92, zorder=zorder)

    elif kind == "target":
        th = np.linspace(0.0, 2.0 * math.pi, 48)
        ax.plot(cx + 0.72 * sx * np.cos(th), cy + 0.72 * sy * np.sin(th), color=color, linewidth=lw, zorder=zorder)
        ax.plot(cx + 0.30 * sx * np.cos(th), cy + 0.30 * sy * np.sin(th), color=color, linewidth=lw, zorder=zorder)
        ax.plot([cx - sx, cx + sx], [cy, cy], color=color, linewidth=lw * 0.8, zorder=zorder)
        ax.plot([cx, cx], [cy - sy, cy + sy], color=color, linewidth=lw * 0.8, zorder=zorder)


def draw_doc_card(
    ax: plt.Axes,
    cx: float,
    cy: float,
    ext: str,
    label: str,
    sub: str = "",
    accent: str = "#153D64",
    w: float = 0.023,
    h: float = 0.046,
    stroke: str = DOC_DARK,
    zorder: float = 12.0,
) -> None:
    """Draw a minimal dark-slate folded-corner wireframe document card with 2-line caption."""
    fold = min(w * 0.37, h * 0.22)
    x0, y0 = cx - w * 0.5, cy - h * 0.5
    poly = [
        (x0, y0),
        (x0 + w, y0),
        (x0 + w, y0 + h - fold),
        (x0 + w - fold, y0 + h),
        (x0, y0 + h),
        (x0, y0),
    ]
    px, py = zip(*poly)
    ax.plot(px, py, color=stroke, linewidth=1.75, zorder=zorder)
    ax.plot(
        [x0 + w - fold, x0 + w - fold, x0 + w],
        [y0 + h, y0 + h - fold, y0 + h - fold],
        color=stroke, linewidth=1.4, zorder=zorder,
    )
    ax.text(cx, cy - 0.002, ext, fontsize=7.6, fontweight="bold", color=stroke, ha="center", va="center", zorder=zorder + 1.0)
    if label:
        ax.text(cx, y0 - 0.017, label, fontsize=9.4, fontweight="bold", color=accent, ha="center", va="center", zorder=zorder + 1.0)
    if sub:
        ax.text(cx, y0 - 0.036, sub, fontsize=7.3, color=MUTED_INK, ha="center", va="center", zorder=zorder + 1.0)


def add_micro_colorbar(
    fig: plt.Figure,
    ann_ax: plt.Axes,
    x: float,
    y: float,
    w: float,
    h: float = 0.0095,
    cmap: str | mpl.colors.Colormap = "inferno",
    vmin_label: str = "",
    vmax_label: str = "",
    border_color: str = LINE_WHITE,
    border_lw: float = 0.85,
    label_size: float = 7.5,
    zorder: float = 14.0,
) -> plt.Axes:
    """Add an ultra-slim micro-colorbar (~0.95% canvas height) flanked by min/max labels."""
    cbar_ax = fig.add_axes([x, y, w, h], zorder=zorder)
    cm = plt.get_cmap(cmap) if isinstance(cmap, str) else cmap
    grad = cm(np.linspace(0.0, 1.0, 256))[np.newaxis, :, :3]
    cbar_ax.imshow(grad, aspect="auto")
    cbar_ax.set_xticks([])
    cbar_ax.set_yticks([])
    for sp in cbar_ax.spines.values():
        sp.set_edgecolor(border_color)
        sp.set_linewidth(border_lw)

    cy = y + h * 0.5
    if vmin_label:
        ann_ax.text(x - 0.005, cy, vmin_label, fontsize=label_size, color=MUTED_INK, ha="right", va="center")
    if vmax_label:
        ann_ax.text(x + w + 0.005, cy, vmax_label, fontsize=label_size, color=MUTED_INK, ha="left", va="center")
    return cbar_ax


def place_asset(
    ax: plt.Axes,
    img_source: str | Path | np.ndarray | Image.Image,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    zorder: float = 11.0,
) -> tuple[float, float, float, float]:
    """Scale and center a transparent RGBA asset proportionally (`Lanczos`) inside a box.

    Returns exact normalized figure rectangle `(rx, ry, rw, rh)` for zero-drift callout math.
    """
    if isinstance(img_source, (str, Path)):
        with Image.open(img_source) as raw:
            im = raw.convert("RGBA")
    elif isinstance(img_source, Image.Image):
        im = img_source.convert("RGBA")
    else:
        im = Image.fromarray(np.asarray(img_source)).convert("RGBA")

    fig_w, fig_h = ax.figure.get_size_inches()
    box_w_in = (x1 - x0) * fig_w
    box_h_in = (y1 - y0) * fig_h
    iw, ih = im.size
    scale = min(box_w_in / max(iw, 1), box_h_in / max(ih, 1))
    dw = (iw * scale) / fig_w
    dh = (ih * scale) / fig_h
    cx = 0.5 * (x0 + x1)
    cy = 0.5 * (y0 + y1)
    rect = (cx - 0.5 * dw, cy - 0.5 * dh, dw, dh)

    sub_ax = ax.figure.add_axes(rect, zorder=zorder)
    sub_ax.set_facecolor("none")
    sub_ax.imshow(im, interpolation="lanczos")
    sub_ax.axis("off")
    return rect


def uv_to_canvas(rect: Sequence[float], uv: Sequence[float]) -> tuple[float, float]:
    """Map normalized [u, v] in cropped asset ([0,1], bottom-up) to canvas [0,1] coords."""
    return float(rect[0] + uv[0] * rect[2]), float(rect[1] + uv[1] * rect[3])


def add_anchored_callout(
    ann_ax: plt.Axes,
    rect: Sequence[float],
    uv: Sequence[float],
    text: str,
    xytext: tuple[float, float],
    color: str = INK,
    ha: str = "left",
    va: str = "center",
    fontsize: float = 7.4,
    bg_color: str = CANVAS_BG,
    bg_alpha: float = 0.84,
    rad: float = 0.0,
    zorder: float = 32.0,
) -> None:
    """Place a crisp sub-pixel 3D-anchored callout on top-most `ann_ax`."""
    xy = uv_to_canvas(rect, uv)
    conn = f"arc3,rad={rad}" if abs(rad) > 1e-4 else "arc3,rad=0.0"
    ann_ax.annotate(
        text,
        xy=xy,
        xytext=xytext,
        fontsize=fontsize,
        fontweight="bold",
        color=color,
        ha=ha,
        va=va,
        bbox={
            "boxstyle": "round,pad=0.14",
            "facecolor": bg_color,
            "edgecolor": "none",
            "alpha": bg_alpha,
        },
        arrowprops={
            "arrowstyle": "-|>,head_length=0.34,head_width=0.20",
            "lw": 1.0,
            "color": color,
            "shrinkA": 2,
            "shrinkB": 1,
            "connectionstyle": conn,
        },
        zorder=zorder,
    )


def save_editorial_figure(
    fig: plt.Figure,
    out_stem: str | Path,
    formats: Iterable[str] = ("png", "pdf", "svg"),
    dpi: int = 300,
) -> list[Path]:
    """Save studio figure to PNG / PDF / SVG with matching background and Type-42 / SVG text."""
    stem = Path(out_stem)
    stem.parent.mkdir(parents=True, exist_ok=True)
    bg = fig.get_facecolor()
    written: list[Path] = []
    for fmt in formats:
        ext = fmt.lower().lstrip(".")
        target = stem.with_suffix(f".{ext}")
        kwargs: dict[str, Any] = {
            "facecolor": bg,
            "edgecolor": "none",
            "pad_inches": 0.0,
        }
        if ext in ("png", "tif", "tiff", "jpg", "jpeg"):
            kwargs["dpi"] = dpi
        fig.savefig(target, format=ext, **kwargs)
        written.append(target)
    return written


# ---------------------------------------------------------------------------
# 3. Stage-A Asset Cropping, Caching, 30-deg Stacks & 3D->2D Projection
# ---------------------------------------------------------------------------

def tight_crop_rgba(arr_rgba: np.ndarray, pad: int = 2) -> Image.Image:
    """Tightly crop transparent RGBA buffer around non-zero alpha pixels."""
    pil, _ = tight_crop_with_bbox(arr_rgba, pad=pad)
    return pil


def tight_crop_with_bbox(
    arr_rgba: np.ndarray,
    pad: int = 2,
) -> tuple[Image.Image, tuple[int, int, int, int]]:
    """Crop RGBA buffer around non-zero alpha and return `(cropped_pil, (x0, y0, x1, y1))`."""
    pil = Image.fromarray(np.asarray(arr_rgba, dtype=np.uint8), mode="RGBA")
    bbox = pil.getbbox()
    if bbox is None:
        return pil, (0, 0, pil.width, pil.height)
    x0 = max(0, bbox[0] - pad)
    y0 = max(0, bbox[1] - pad)
    x1 = min(pil.width, bbox[2] + pad)
    y1 = min(pil.height, bbox[3] + pad)
    crop_box = (x0, y0, x1, y1)
    return pil.crop(crop_box), crop_box


def crop_stack_alpha_union(
    rgba_list: Sequence[np.ndarray],
    alpha_thresh: int = 8,
    pad: int = 6,
) -> list[np.ndarray]:
    """Crop all layers in an exploded stack using their joint alpha union bounding box."""
    if not rgba_list:
        return []
    h, w = rgba_list[0].shape[:2]
    alpha_union = np.zeros((h, w), dtype=bool)
    for img in rgba_list:
        alpha_union |= np.asarray(img)[:, :, 3] > alpha_thresh
    ys, xs = np.where(alpha_union)
    if len(ys) == 0:
        return [np.asarray(img) for img in rgba_list]
    y_lo = max(0, int(ys.min()) - pad)
    y_hi = min(h, int(ys.max()) + pad + 1)
    x_lo = max(0, int(xs.min()) - pad)
    x_hi = min(w, int(xs.max()) + pad + 1)
    return [np.asarray(img)[y_lo:y_hi, x_lo:x_hi] for img in rgba_list]


def iso_project_3d(
    x: float | np.ndarray,
    y: float | np.ndarray,
    z: float | np.ndarray = 0.0,
    angle_deg: float = 30.0,
) -> tuple[float | np.ndarray, float | np.ndarray]:
    """Exact 30-degree SW-top orthographic isometric projection."""
    ca = math.cos(math.radians(angle_deg))
    sa = math.sin(math.radians(angle_deg))
    return (x - y) * ca, (x + y) * sa + z


def project_ortho_3d_to_crop_uv(
    pt_3d: Sequence[float],
    xlim: tuple[float, float],
    ylim: tuple[float, float],
    full_wh: tuple[int, int],
    crop_box: tuple[int, int, int, int],
    angle_deg: float = 30.0,
) -> list[float]:
    """Project a 3D world point from full-bleed orthographic render into cropped [u, v]."""
    sx, sy = iso_project_3d(float(pt_3d[0]), float(pt_3d[1]), float(pt_3d[2]), angle_deg=angle_deg)
    w_full, h_full = full_wh
    x_px = ((sx - xlim[0]) / max(xlim[1] - xlim[0], 1e-9)) * w_full
    y_px_bot = ((sy - ylim[0]) / max(ylim[1] - ylim[0], 1e-9)) * h_full
    y_px_top = h_full - y_px_bot
    cx0, cy0, cx1, cy1 = crop_box
    u = (x_px - cx0) / max(cx1 - cx0, 1)
    v_top = (y_px_top - cy0) / max(cy1 - cy0, 1)
    return [float(u), float(1.0 - v_top)]


def save_anchors_json(anchors: dict[str, list[float]], path: str | Path) -> Path:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(anchors, indent=2), encoding="utf-8")
    return out


def load_anchors_json(path: str | Path) -> dict[str, list[float]]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def render_iso_raster_stack(
    layers: Sequence[tuple[str, np.ndarray]],
    out_path: str | Path,
    gap: float = 0.72,
    figsize: tuple[float, float] = (4.4, 6.2),
    dpi: int = 300,
    label_fontsize: float = 10.4,
    angle_deg: float = 30.0,
    force: bool = False,
) -> Path:
    """Render cached transparent 30-deg isometric 2D raster stack with vertical white rails.

    `layers`: bottom-to-top list of `(label, rgba_array[nx, ny, 4])`.
    """
    out = Path(out_path)
    if out.exists() and not force:
        return out
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.rcParams["font.sans-serif"] = FONT_STACK

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    fig.patch.set_alpha(0.0)
    ax.set_facecolor("none")

    nx, ny = layers[0][1].shape[:2]
    x = np.linspace(0.0, 1.0, nx + 1)
    y = np.linspace(0.0, 1.0, ny + 1)
    xx, yy = np.meshgrid(x, y, indexing="ij")
    uu, vv_base = iso_project_3d(xx, yy, np.zeros_like(xx), angle_deg=angle_deg)

    # 4 vertical alignment dotted rails at corners
    for cx_r, cy_r in ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)):
        u0, v0 = iso_project_3d(np.array([cx_r]), np.array([cy_r]), np.array([0.0]), angle_deg=angle_deg)
        u1, v1 = iso_project_3d(np.array([cx_r]), np.array([cy_r]), np.array([(len(layers) - 1) * gap]), angle_deg=angle_deg)
        zod = 1 if (cx_r, cy_r) == (1.0, 1.0) else (2 if (cx_r, cy_r) != (0.0, 0.0) else 25)
        ax.plot([u0[0], u1[0]], [v0[0], v1[0]], linestyle="--", linewidth=0.95, color=LINE_WHITE, alpha=0.82, zorder=zod)

    for idx, (label, rgba) in enumerate(layers):
        zb = idx * gap
        vv = vv_base + zb
        mesh = ax.pcolormesh(
            uu, vv, np.zeros((nx, ny)),
            shading="flat", edgecolors="none", antialiased=False, zorder=4 + idx * 3,
        )
        mesh.set_array(None)
        mesh.set_facecolors(np.asarray(rgba, dtype=np.float32).reshape(-1, 4))

        rim_x = np.array([0.0, 1.0, 1.0, 0.0, 0.0])
        rim_y = np.array([0.0, 0.0, 1.0, 1.0, 0.0])
        ru, rv = iso_project_3d(rim_x, rim_y, np.full_like(rim_x, zb), angle_deg=angle_deg)
        ax.plot(ru, rv, color=LINE_WHITE, linewidth=1.1, zorder=5 + idx * 3)

        lu, lv = iso_project_3d(np.array([0.09]), np.array([0.55]), np.array([zb]), angle_deg=angle_deg)
        ax.text(
            lu[0], lv[0], label,
            rotation=-angle_deg, rotation_mode="anchor",
            ha="center", va="center",
            fontsize=label_fontsize, fontweight="bold", color=INK,
            path_effects=[pe.withStroke(linewidth=2.5, foreground=LINE_WHITE)],
            zorder=30,
        )

    ax.set_xlim(uu.min() - 0.08, uu.max() + 0.08)
    ax.set_ylim(vv_base.min() - 0.08, vv_base.max() + (len(layers) - 1) * gap + 0.08)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.savefig(out, transparent=True, bbox_inches="tight", pad_inches=0.02, dpi=dpi)
    plt.close(fig)
    return out


def render_exploded_3d_layers(
    layer_rgbas: Sequence[np.ndarray],
    labels: Sequence[str],
    out_path: str | Path,
    y_step_frac: float = 0.56,
    figsize: tuple[float, float] = (4.4, 6.2),
    dpi: int = 300,
    label_fontsize: float = 10.2,
    force: bool = False,
) -> Path:
    """Crop multi-layer 3D RGBA renders by alpha-union and stack vertically with -30-deg halo labels."""
    out = Path(out_path)
    if out.exists() and not force:
        return out
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.rcParams["font.sans-serif"] = FONT_STACK

    cropped = crop_stack_alpha_union(layer_rgbas)
    h_im, w_im = cropped[0].shape[:2]
    y_step = h_im * y_step_frac

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    fig.patch.set_alpha(0.0)
    ax.set_facecolor("none")

    for idx, (lbl, im) in enumerate(zip(labels, cropped)):
        y0_im = idx * y_step
        ax.imshow(im, extent=[0.0, w_im, y0_im, y0_im + h_im], zorder=4 + idx * 2, interpolation="lanczos")
        ax.text(
            w_im * 0.25,
            y0_im + h_im * 0.18,
            lbl,
            rotation=-29.5,
            rotation_mode="anchor",
            ha="center",
            va="center",
            fontsize=label_fontsize,
            fontweight="bold",
            color=INK,
            path_effects=[pe.withStroke(linewidth=2.5, foreground=LINE_WHITE)],
            zorder=30,
        )

    ax.set_xlim(-w_im * 0.04, w_im * 1.04)
    ax.set_ylim(-h_im * 0.04, (len(cropped) - 1) * y_step + h_im * 1.04)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.savefig(out, transparent=True, bbox_inches="tight", pad_inches=0.02, dpi=dpi)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# 4. Optional PyVista Studio Helpers (Lazy Imported When Available)
# ---------------------------------------------------------------------------

def create_pyvista_studio_plotter(window_size: tuple[int, int] = (1250, 980)) -> Any:
    """Create off-screen MSAA three-lights PyVista plotter for Stage-A asset rendering."""
    import pyvista as pv  # optional runtime dependency

    pl = pv.Plotter(off_screen=True, window_size=window_size, lighting="three lights")
    pl.enable_anti_aliasing("msaa")
    return pl


def setup_pyvista_iso_camera(
    pl: Any,
    focus: Sequence[float],
    extent: float,
    parallel_scale: float,
) -> None:
    """Lock PyVista camera to strict parallel-projection SW isometric view."""
    f = np.asarray(focus, dtype=float)
    pl.camera_position = [f + np.array([-extent * 1.4, -extent * 1.4, extent * 1.4]), f, (0.0, 0.0, 1.0)]
    pl.enable_parallel_projection()
    pl.camera.parallel_scale = parallel_scale


def project_pyvista_3d_to_crop_uv(
    pl: Any,
    pt_3d: Sequence[float],
    crop_box: tuple[int, int, int, int],
) -> list[float]:
    """Project 3D world point via VTK camera into cropped asset normalized [u, v]."""
    import pyvista as pv

    ren = pl.renderer
    _, h_full = pl.window_size
    coord = pv._vtk.vtkCoordinate()
    coord.SetCoordinateSystemToWorld()
    coord.SetValue(float(pt_3d[0]), float(pt_3d[1]), float(pt_3d[2]))
    dx, dy = coord.GetComputedDoubleDisplayValue(ren)
    x_px, y_px_top = dx, h_full - dy
    cx0, cy0, cx1, cy1 = crop_box
    u = (x_px - cx0) / max(cx1 - cx0, 1)
    v_top = (y_px_top - cy0) / max(cy1 - cy0, 1)
    return [float(u), float(1.0 - v_top)]
