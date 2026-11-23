"""
ual_ga_kit.py — Programmatic Graphical Abstract & Workflow Engine
Distilled from Dr. Binyu Lei & NUS Urban Analytics Lab visual standards.

Pure Matplotlib + NumPy + PIL engine on an exact physical-inch coordinate canvas.
Supports all four UAL visual archetypes (Studio Grey Exploded Spatial Pipeline,
Editorial White Clay-3D + Loupes, Conceptual Twin Mirror, and Multi-Stage Matrix).
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Iterable, Sequence

import matplotlib as mpl
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import (
    Circle,
    FancyArrowPatch,
    FancyBboxPatch,
    Polygon,
    Rectangle,
)
from matplotlib.transforms import Affine2D
import numpy as np
from PIL import Image

# Ensure editable vector fonts in PDF / PS / SVG exports
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = [
    "Arial",
    "Helvetica",
    "DejaVu Sans",
    "Microsoft YaHei",
]


# ---------------------------------------------------------------------------
# Color Systems (Archetypes A–D)
# ---------------------------------------------------------------------------

PALETTES: dict[str, dict[str, str]] = {
    "studio_grey": {
        "bg": "#D9DBDE",
        "frame_border": "#FFFFFF",
        "flow_line": "#FFFFFF",
        "title": "#111111",
        "subtitle": "#3E454E",
        "halo": "#FFFFFF",
        "clay_top": "#EAECEF",
        "clay_left": "#D2D6DC",
        "clay_right": "#B5BCC6",
        "clay_edge": "#9AA2AE",
        "badge_stroke": "#2D333B",
        "accent_coral": "#CC6542",
        "accent_ray": "#E05A2B",
        "accent_teal": "#38A39D",
        "accent_navy": "#0E2F56",
        "accent_gold": "#E6C15A",
    },
    "editorial_white": {
        "bg": "#FFFFFF",
        "header_band": "#D2D5DA",
        "dashed_bg": "#F4F5F7",
        "border": "#B8BEC7",
        "dashed_border": "#7C828D",
        "title": "#181C20",
        "subtitle": "#4A525E",
        "clay_top": "#F4F5F7",
        "clay_left": "#DDE1E7",
        "clay_right": "#C2C8D2",
        "clay_edge": "#AEB6C2",
        "focal_gold": "#F0C419",
        "stem_cobalt": "#3B5BDB",
        "stem_magenta": "#D6336C",
        "gnn_orange": "#D95F02",
        "gnn_teal": "#4E9A8E",
        "leader": "#4B525E",
        "bracket": "#8C929C",
    },
    "interplay_twin": {
        "bg": "#FFFFFF",
        "physical_top": "#9FAFE8",
        "physical_left": "#7E93DF",
        "physical_right": "#6278CA",
        "virtual_top": "#E7EBF0",
        "virtual_left": "#D0D6DF",
        "virtual_right": "#B5BDC9",
        "arc_fill": "#DCE1EA",
        "border": "#B8BEC7",
        "title": "#181C20",
        "subtitle": "#4A525E",
        "leader": "#7C828D",
    },
    "geoai_matrix": {
        "bg": "#FFFFFF",
        "header_dark": "#7A7F85",
        "header_light": "#E8EAED",
        "border": "#9CA3AF",
        "title": "#181C20",
        "subtitle": "#4A525E",
        "sage": "#5B8E7D",
        "steel": "#4A7C9B",
        "coral": "#D97757",
        "violet": "#8C6BB1",
    },
}


def get_ocean_gold_cmap() -> LinearSegmentedColormap:
    """Return UAL deep-ocean-blue -> teal -> warm-gold scientific colormap."""
    return LinearSegmentedColormap.from_list(
        "ual_ocean_gold",
        ["#0E2F56", "#1D5E7A", "#38A39D", "#94C87B", "#E6C15A"],
        N=256,
    )


def _resolve_cmap(cmap: str | mpl.colors.Colormap) -> mpl.colors.Colormap:
    if isinstance(cmap, str):
        if cmap == "ual_ocean_gold":
            return get_ocean_gold_cmap()
        return mpl.colormaps[cmap]
    return cmap


def _shade_hex(hex_color: str, factor: float) -> tuple[float, float, float]:
    rgb = np.array(mpl.colors.to_rgb(hex_color), dtype=float)
    return tuple(np.clip(rgb * factor, 0.0, 1.0))


# ---------------------------------------------------------------------------
# Canvas Creation & Export
# ---------------------------------------------------------------------------

def create_canvas(
    figsize: tuple[float, float] = (16.0, 10.0),
    theme: str = "studio_grey",
    dpi: int = 300,
    title: str | None = None,
    subtitle: str | None = None,
    title_x: float = 0.40,
    title_y: float | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Create a full-bleed physical-inch canvas with equal aspect ratio."""
    pal = PALETTES.get(theme, PALETTES["editorial_white"])
    bg = pal["bg"]
    w, h = float(figsize[0]), float(figsize[1])

    fig = plt.figure(figsize=(w, h), dpi=dpi, facecolor=bg)
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0], facecolor=bg)
    ax.set_xlim(0.0, w)
    ax.set_ylim(0.0, h)
    ax.set_aspect("equal", adjustable="box")
    ax.set_autoscale_on(False)
    ax.axis("off")

    if title:
        ty = (h - 0.34) if title_y is None else title_y
        ax.text(
            title_x,
            ty,
            title,
            fontsize=18.0,
            fontweight="bold",
            color=pal["title"],
            ha="left",
            va="top",
            zorder=20,
        )
        if subtitle:
            ax.text(
                title_x,
                ty - 0.33,
                subtitle,
                fontsize=10.8,
                fontweight="normal",
                color=pal["subtitle"],
                ha="left",
                va="top",
                zorder=20,
            )

    return fig, ax


def save_publication_figure(
    fig: plt.Figure,
    out_stem: str | Path,
    formats: Iterable[str] = ("png", "svg"),
    dpi: int = 300,
) -> list[Path]:
    """Export figure cleanly in raster and editable vector formats."""
    stem = Path(out_stem)
    stem.parent.mkdir(parents=True, exist_ok=True)
    bg = fig.get_facecolor()
    written: list[Path] = []
    for fmt in formats:
        ext = fmt.lower().lstrip(".")
        target = stem.with_suffix(f".{ext}")
        save_kwargs: dict[str, Any] = {
            "facecolor": bg,
            "edgecolor": "none",
            "pad_inches": 0.0,
        }
        if ext in ("png", "tif", "tiff", "jpg", "jpeg"):
            save_kwargs["dpi"] = dpi
        fig.savefig(target, format=ext, **save_kwargs)
        written.append(target)
    return written


# ---------------------------------------------------------------------------
# Containers, Headers, Badges, and Micro-Tables
# ---------------------------------------------------------------------------

def draw_notched_frame(
    ax: plt.Axes,
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    bg_color: str = "#D9DBDE",
    border_color: str = "#FFFFFF",
    lw: float = 1.6,
    title_color: str = "#111111",
    title_size: float = 12.0,
    notch_pad: float = 0.25,
    zorder: float = 2.0,
) -> None:
    """Draw a 90-deg sharp hollow frame whose top border breaks cleanly behind the title."""
    rect = Rectangle(
        (x, y),
        w,
        h,
        facecolor="none",
        edgecolor=border_color,
        linewidth=lw,
        joinstyle="miter",
        zorder=zorder,
    )
    ax.add_patch(rect)

    if title:
        ax.text(
            x + 0.24,
            y + h,
            title,
            fontsize=title_size,
            fontweight="bold",
            color=title_color,
            ha="left",
            va="center",
            bbox={
                "facecolor": bg_color,
                "edgecolor": "none",
                "boxstyle": f"square,pad={notch_pad}",
            },
            zorder=zorder + 2.0,
        )


def draw_header_panel(
    ax: plt.Axes,
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    header_h: float = 0.36,
    header_bg: str = "#D2D5DA",
    body_bg: str = "#FFFFFF",
    border_color: str = "#B8BEC7",
    lw: float = 0.9,
    title_color: str = "#181C20",
    title_size: float = 10.5,
    align: str = "center",
    zorder: float = 2.0,
) -> tuple[float, float, float, float]:
    """Draw a flat editorial container with a clean solid gray header strip.

    Returns inner body bounds (x, y, w, h - header_h).
    """
    body = Rectangle(
        (x, y),
        w,
        h,
        facecolor=body_bg,
        edgecolor=border_color,
        linewidth=lw,
        joinstyle="miter",
        zorder=zorder,
    )
    ax.add_patch(body)

    hbar = Rectangle(
        (x, y + h - header_h),
        w,
        header_h,
        facecolor=header_bg,
        edgecolor=border_color,
        linewidth=lw,
        joinstyle="miter",
        zorder=zorder + 0.5,
    )
    ax.add_patch(hbar)

    if title:
        tx = x + w * 0.5 if align == "center" else x + 0.14
        ax.text(
            tx,
            y + h - header_h * 0.5,
            title,
            fontsize=title_size,
            fontweight="bold",
            color=title_color,
            ha=align,
            va="center",
            zorder=zorder + 1.0,
        )
    return (x, y, w, h - header_h)


def draw_dashed_zone(
    ax: plt.Axes,
    x: float,
    y: float,
    w: float,
    h: float,
    title: str | None = None,
    fill: str = "#F4F5F7",
    border_color: str = "#7C828D",
    lw: float = 0.9,
    dash: tuple[float, float] = (4.0, 2.5),
    title_size: float = 10.5,
    title_color: str = "#181C20",
    zorder: float = 2.0,
) -> None:
    """Draw a subtle cool-grey dashed methodology compartment (Lei SCS 2023 style)."""
    rect = Rectangle(
        (x, y),
        w,
        h,
        facecolor=fill,
        edgecolor=border_color,
        linewidth=lw,
        linestyle=(0, dash),
        zorder=zorder,
    )
    ax.add_patch(rect)
    if title:
        ax.text(
            x + 0.16,
            y + h - 0.14,
            title,
            fontsize=title_size,
            fontweight="bold",
            color=title_color,
            ha="left",
            va="top",
            zorder=zorder + 1.0,
        )


def draw_bracket_list(
    ax: plt.Axes,
    x: float,
    y: float,
    w: float,
    h: float,
    items: Sequence[str],
    color: str = "#8C929C",
    text_color: str = "#22262B",
    fontsize: float = 8.4,
    lw: float = 0.9,
    zorder: float = 4.0,
) -> None:
    """Draw delicate left/right square brackets enclosing compact bullet items."""
    arm = min(0.08, w * 0.08)
    # Left bracket
    ax.plot(
        [x + arm, x, x, x + arm],
        [y, y, y + h, y + h],
        color=color,
        lw=lw,
        solid_capstyle="butt",
        zorder=zorder,
    )
    # Right bracket
    ax.plot(
        [x + w - arm, x + w, x + w, x + w - arm],
        [y, y, y + h, y + h],
        color=color,
        lw=lw,
        solid_capstyle="butt",
        zorder=zorder,
    )

    n = max(1, len(items))
    top_pad = h * 0.14
    span = max(0.05, h - 2.0 * top_pad)
    for idx, item in enumerate(items):
        iy = y + h - top_pad - (0.5 * span if n == 1 else idx * span / (n - 1))
        ax.text(
            x + 0.11,
            iy,
            f"•  {item}",
            fontsize=fontsize,
            color=text_color,
            ha="left",
            va="center",
            zorder=zorder + 0.5,
        )


def draw_pill_tag(
    ax: plt.Axes,
    cx: float,
    cy: float,
    text: str,
    bg: str = "#3B5BDB",
    fg: str = "#FFFFFF",
    border: str | None = None,
    fontsize: float = 8.8,
    pad_x: float = 0.14,
    pad_y: float = 0.07,
    zorder: float = 10.0,
) -> None:
    """Draw a compact semantic pill tag (Lei Cities 2026 style)."""
    # Estimate width conservatively from character count and font size
    est_w = max(0.65, len(text) * fontsize * 0.0086 + 2.0 * pad_x)
    est_h = fontsize * 0.014 + 2.0 * pad_y
    box = FancyBboxPatch(
        (cx - est_w * 0.5, cy - est_h * 0.5),
        est_w,
        est_h,
        boxstyle=f"round,pad=0.0,rounding_size={est_h * 0.36}",
        facecolor=bg,
        edgecolor=border if border else "none",
        linewidth=0.8 if border else 0.0,
        zorder=zorder,
    )
    ax.add_patch(box)
    ax.text(
        cx,
        cy,
        text,
        fontsize=fontsize,
        fontweight="bold" if border is None else "normal",
        color=fg,
        ha="center",
        va="center",
        zorder=zorder + 0.5,
    )


def draw_micro_table(
    ax: plt.Axes,
    x: float,
    y: float,
    w: float,
    h: float,
    headers: Sequence[str],
    rows: Sequence[Sequence[str]],
    header_bg: str = "#ECEEF2",
    highlight_row: int | None = None,
    highlight_bg: str = "#FFF3CD",
    fontsize: float = 7.6,
    zorder: float = 6.0,
) -> None:
    """Draw a clean hairline attribute micro-table (Lei CEUS 2024 / Cities 2026)."""
    n_rows = len(rows) + 1
    n_cols = len(headers)
    row_h = h / n_rows
    col_w = w / n_cols

    # Header row
    hy = y + h - row_h
    ax.add_patch(
        Rectangle(
            (x, hy),
            w,
            row_h,
            facecolor=header_bg,
            edgecolor="#B8BEC7",
            linewidth=0.75,
            zorder=zorder,
        )
    )
    for c_idx, head in enumerate(headers):
        ax.text(
            x + (c_idx + 0.5) * col_w,
            hy + row_h * 0.5,
            head,
            fontsize=fontsize,
            fontweight="bold",
            color="#181C20",
            ha="center",
            va="center",
            zorder=zorder + 0.5,
        )

    # Data rows
    for r_idx, row in enumerate(rows):
        ry = y + h - (r_idx + 2) * row_h
        bg = highlight_bg if (highlight_row is not None and r_idx == highlight_row) else "#FFFFFF"
        ax.add_patch(
            Rectangle(
                (x, ry),
                w,
                row_h,
                facecolor=bg,
                edgecolor="#D2D6DC",
                linewidth=0.6,
                zorder=zorder,
            )
        )
        for c_idx, val in enumerate(row):
            ax.text(
                x + (c_idx + 0.5) * col_w,
                ry + row_h * 0.5,
                str(val),
                fontsize=fontsize,
                color="#2B3139",
                ha="center",
                va="center",
                zorder=zorder + 0.5,
            )


# ---------------------------------------------------------------------------
# Orthogonal Flows, Chevrons, Leaders & Stage Arrows
# ---------------------------------------------------------------------------

def _draw_chevrons_on_segment(
    ax: plt.Axes,
    p_a: tuple[float, float],
    p_b: tuple[float, float],
    count: int = 3,
    pos: float = 0.5,
    size: float = 0.11,
    color: str = "#FFFFFF",
    lw: float = 2.0,
    zorder: float = 6.0,
) -> None:
    dx = p_b[0] - p_a[0]
    dy = p_b[1] - p_a[1]
    seg_len = math.hypot(dx, dy)
    if seg_len < 1e-6 or count <= 0:
        return
    ux, uy = dx / seg_len, dy / seg_len
    px, py = -uy, ux  # perpendicular unit vector

    spacing = size * 1.15
    cx = p_a[0] + dx * pos
    cy = p_a[1] + dy * pos
    start_offset = -0.5 * (count - 1) * spacing

    for i in range(count):
        off = start_offset + i * spacing
        tip_x = cx + ux * off + ux * (size * 0.45)
        tip_y = cy + uy * off + uy * (size * 0.45)
        back_x = tip_x - ux * size
        back_y = tip_y - uy * size
        arm_y_off = size * 0.85
        ax.plot(
            [back_x + px * arm_y_off, tip_x, back_x - px * arm_y_off],
            [back_y + py * arm_y_off, tip_y, back_y - py * arm_y_off],
            color=color,
            linewidth=lw,
            solid_capstyle="round",
            solid_joinstyle="round",
            zorder=zorder,
        )


def draw_ortho_flow(
    ax: plt.Axes,
    points: Sequence[tuple[float, float]],
    color: str = "#FFFFFF",
    lw: float = 1.8,
    dash: tuple[float, float] = (1.3, 2.0),
    chevrons: int = 3,
    chevron_seg: int = 0,
    chevron_pos: float = 0.5,
    chevron_size: float = 0.10,
    arrow_end: bool = False,
    zorder: float = 5.0,
) -> None:
    """Draw pure orthogonal dotted polyline with optional >>> chevron cluster."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    ax.plot(
        xs,
        ys,
        color=color,
        linewidth=lw,
        linestyle=(0, dash),
        solid_capstyle="round",
        zorder=zorder,
    )
    if chevrons > 0 and len(points) >= 2:
        idx = min(max(0, chevron_seg), len(points) - 2)
        _draw_chevrons_on_segment(
            ax,
            points[idx],
            points[idx + 1],
            count=chevrons,
            pos=chevron_pos,
            size=chevron_size,
            color=color,
            lw=max(lw, 1.9),
            zorder=zorder + 0.5,
        )
    if arrow_end and len(points) >= 2:
        _draw_chevrons_on_segment(
            ax,
            points[-2],
            points[-1],
            count=1,
            pos=0.98,
            size=chevron_size * 0.9,
            color=color,
            lw=lw,
            zorder=zorder + 0.5,
        )


def draw_leader_line(
    ax: plt.Axes,
    p0: tuple[float, float],
    p1: tuple[float, float],
    style: str = "dotted",
    color: str = "#4B525E",
    lw: float = 0.95,
    curved: float = 0.0,
    start_dot: bool = True,
    end_arrow: bool = False,
    dot_r: float = 0.035,
    zorder: float = 9.0,
) -> None:
    """Draw radial straight or gently curved dotted callout leader with anchor dot."""
    ls = (0, (1.2, 1.8)) if style == "dotted" else ("-" if style == "solid" else (0, (4.0, 2.2)))
    arrow_style = "->" if end_arrow else "-"
    patch = FancyArrowPatch(
        p0,
        p1,
        connectionstyle=f"arc3,rad={curved}",
        arrowstyle=arrow_style,
        mutation_scale=9 if end_arrow else 1,
        color=color,
        linewidth=lw,
        linestyle=ls,
        zorder=zorder,
    )
    ax.add_patch(patch)
    if start_dot:
        ax.add_patch(
            Circle(
                p0,
                radius=dot_r,
                facecolor=color,
                edgecolor="#FFFFFF",
                linewidth=0.5,
                zorder=zorder + 0.5,
            )
        )


def draw_ortho_leader(
    ax: plt.Axes,
    p0: tuple[float, float],
    p1: tuple[float, float],
    elbow: str = "hv",
    color: str = "#6C737F",
    lw: float = 0.9,
    dash: tuple[float, float] = (1.4, 1.8),
    start_dot: bool = True,
    dot_r: float = 0.032,
    zorder: float = 9.0,
) -> None:
    """Draw 90-degree L-shaped dotted callout leader (Lei SCS 2025 GA style)."""
    mid = (p1[0], p0[1]) if elbow == "hv" else (p0[0], p1[1])
    ax.plot(
        [p0[0], mid[0], p1[0]],
        [p0[1], mid[1], p1[1]],
        color=color,
        linewidth=lw,
        linestyle=(0, dash),
        zorder=zorder,
    )
    if start_dot:
        ax.add_patch(
            Circle(p0, radius=dot_r, facecolor=color, edgecolor="none", zorder=zorder + 0.4)
        )


def draw_stage_arrow(
    ax: plt.Axes,
    p0: tuple[float, float],
    p1: tuple[float, float],
    color: str = "#555C68",
    lw: float = 2.0,
    head_scale: float = 13.0,
    zorder: float = 6.0,
) -> None:
    """Draw clean crisp architectural arrow between workflow stages."""
    arr = FancyArrowPatch(
        p0,
        p1,
        arrowstyle="-|>",
        mutation_scale=head_scale,
        color=color,
        linewidth=lw,
        zorder=zorder,
    )
    ax.add_patch(arr)


# ---------------------------------------------------------------------------
# Exact Parallel 30-Degree Isometric Geometry Engine
# ---------------------------------------------------------------------------

def iso_project(
    u: float | np.ndarray,
    v: float | np.ndarray,
    z: float | np.ndarray = 0.0,
    cx: float = 0.0,
    cy: float = 0.0,
    size: float = 1.0,
    angle_deg: float = 30.0,
) -> tuple[float | np.ndarray, float | np.ndarray]:
    """Map normalized 3D coordinates (u, v in [0,1], z>=0) to 2D isometric coordinates.

    Corners of [0,1]x[0,1] at z=0:
      (0, 0) = LEFT, (1, 0) = BOTTOM (front-most), (1, 1) = RIGHT, (0, 1) = TOP (back-most).
    Front-left edge (0,0)->(1,0) slopes exactly at -angle_deg (default -30 deg).
    Painter's back-to-front depth sort key is (u - v) ascending.
    """
    c = math.cos(math.radians(angle_deg))
    s = math.sin(math.radians(angle_deg))
    du = u - 0.5
    dv = v - 0.5
    x = cx + size * c * (du + dv)
    y = cy + size * s * (-du + dv) + size * z
    return x, y


def draw_iso_layer_grid(
    ax: plt.Axes,
    data_2d: np.ndarray,
    cx: float,
    cy: float,
    size: float = 2.3,
    z_offset: float = 0.0,
    cmap: str | mpl.colors.Colormap = "viridis",
    vmin: float | None = None,
    vmax: float | None = None,
    border_color: str = "#FFFFFF",
    border_lw: float = 1.1,
    alpha: float = 0.98,
    label: str | None = None,
    label_color: str = "#111111",
    halo_color: str = "#FFFFFF",
    halo_lw: float = 2.6,
    label_size: float = 9.5,
    angle_deg: float = 30.0,
    circular: bool = False,
    zorder: float = 4.0,
) -> tuple[tuple[float, float], ...]:
    """Render a 2D array (or RGB/RGBA image) in exact 30-deg parallel isometric projection.

    Returns the 4 projected diamond corner coordinates: (LEFT, BOTTOM, RIGHT, TOP).
    """
    c = math.cos(math.radians(angle_deg))
    s = math.sin(math.radians(angle_deg))
    cy_z = cy + size * z_offset

    # Corner vertices in data coordinates
    corners = (
        (cx - size * c, cy_z),               # (0, 0) LEFT
        (cx, cy_z - size * s),               # (1, 0) BOTTOM
        (cx + size * c, cy_z),               # (1, 1) RIGHT
        (cx, cy_z + size * s),               # (0, 1) TOP
    )

    if circular:
        theta = np.linspace(0.0, 2.0 * np.pi, 96, endpoint=True)
        cu = 0.5 + 0.5 * np.cos(theta)
        cv = 0.5 + 0.5 * np.sin(theta)
        px, py = iso_project(cu, cv, z=0.0, cx=cx, cy=cy_z, size=size, angle_deg=angle_deg)
        clip_verts = np.column_stack([px, py])
    else:
        clip_verts = np.array(corners, dtype=float)

    clip_poly = Polygon(
        clip_verts,
        closed=True,
        facecolor="none",
        edgecolor="none",
        transform=ax.transData,
    )
    ax.add_patch(clip_poly)

    # Affine2D mapping unit square [0,1]x[0,1] -> isometric diamond
    trans = Affine2D.from_values(
        size * c,
        -size * s,
        size * c,
        size * s,
        cx - size * c,
        cy_z,
    )

    arr = np.asarray(data_2d)
    imshow_kwargs: dict[str, Any] = {
        "origin": "lower",
        "extent": [0.0, 1.0, 0.0, 1.0],
        "interpolation": "nearest" if arr.ndim == 2 and max(arr.shape) <= 64 else "bilinear",
        "alpha": alpha,
        "transform": trans + ax.transData,
        "zorder": zorder,
    }
    if arr.ndim == 2:
        imshow_kwargs["cmap"] = _resolve_cmap(cmap)
        if vmin is not None:
            imshow_kwargs["vmin"] = vmin
        if vmax is not None:
            imshow_kwargs["vmax"] = vmax

    im = ax.imshow(arr, **imshow_kwargs)
    im.set_clip_path(clip_poly)

    if border_color and border_lw > 0:
        rim = Polygon(
            clip_verts,
            closed=True,
            facecolor="none",
            edgecolor=border_color,
            linewidth=border_lw,
            joinstyle="round" if circular else "miter",
            zorder=zorder + 0.2,
        )
        ax.add_patch(rim)

    if label:
        lx, ly = iso_project(0.47, 0.14, z=0.0, cx=cx, cy=cy_z, size=size, angle_deg=angle_deg)
        txt = ax.text(
            lx,
            ly,
            label,
            fontsize=label_size,
            fontweight="medium",
            color=label_color,
            rotation=-angle_deg,
            rotation_mode="anchor",
            ha="center",
            va="center",
            zorder=zorder + 0.6,
        )
        if halo_lw > 0:
            txt.set_path_effects(
                [
                    pe.withStroke(linewidth=halo_lw, foreground=halo_color),
                    pe.Normal(),
                ]
            )

    return corners


def draw_iso_exploded_stack(
    ax: plt.Axes,
    layers: Sequence[dict[str, Any]],
    cx: float,
    cy: float,
    size: float = 2.3,
    dz: float = 0.62,
    border_color: str = "#FFFFFF",
    border_lw: float = 1.1,
    rail_color: str = "#FFFFFF",
    rail_lw: float = 0.95,
    angle_deg: float = 30.0,
    circular: bool = False,
    zorder_base: float = 4.0,
) -> list[tuple[tuple[float, float], ...]]:
    """Draw vertically exploded stack of isometric layers with vertical corner dotted rails.

    `layers`: bottom-to-top list of dicts `{data, cmap, label, vmin, vmax, alpha, ...}`.
    """
    n = len(layers)
    if n == 0:
        return []

    z_start = -0.5 * (n - 1) * (dz / size)
    all_corners: list[tuple[tuple[float, float], ...]] = []

    for i, layer in enumerate(layers):
        z_off = z_start + i * (dz / size)
        c_pts = draw_iso_layer_grid(
            ax,
            data_2d=layer["data"],
            cx=cx,
            cy=cy,
            size=size,
            z_offset=z_off,
            cmap=layer.get("cmap", "viridis"),
            vmin=layer.get("vmin"),
            vmax=layer.get("vmax"),
            border_color=layer.get("border_color", border_color),
            border_lw=layer.get("border_lw", border_lw),
            alpha=layer.get("alpha", 0.98),
            label=layer.get("label"),
            label_color=layer.get("label_color", "#111111"),
            halo_color=layer.get("halo_color", "#FFFFFF"),
            halo_lw=layer.get("halo_lw", 2.6),
            label_size=layer.get("label_size", 9.5),
            angle_deg=angle_deg,
            circular=circular,
            zorder=zorder_base + i * 0.8,
        )
        all_corners.append(c_pts)

    if rail_color and rail_lw > 0 and len(all_corners) >= 2 and not circular:
        bot = all_corners[0]
        top = all_corners[-1]
        for k in range(4):
            z_rail = zorder_base - 0.3 if k == 3 else zorder_base + n * 0.8 + 0.1
            ax.plot(
                [bot[k][0], top[k][0]],
                [bot[k][1], top[k][1]],
                color=rail_color,
                linewidth=rail_lw,
                linestyle=(0, (1.2, 1.8)),
                zorder=z_rail,
            )
    return all_corners


def draw_prism(
    ax: plt.Axes,
    u0: float,
    v0: float,
    u1: float,
    v1: float,
    z0: float,
    z1: float,
    cx: float,
    cy: float,
    size: float,
    top_color: Any = "#F4F5F7",
    left_color: Any = "#DDE1E7",
    right_color: Any = "#C2C8D2",
    edge_color: str = "#AEB6C2",
    lw: float = 0.35,
    angle_deg: float = 30.0,
    zorder: float = 4.0,
    alpha: float = 1.0,
) -> tuple[float, float]:
    """Draw a 3-face isometric rectangular prism. Returns projected top-center (x, y)."""
    p = lambda uu, vv, zz: iso_project(uu, vv, zz, cx=cx, cy=cy, size=size, angle_deg=angle_deg)

    # Top face (z = z1)
    top_poly = [p(u0, v0, z1), p(u1, v0, z1), p(u1, v1, z1), p(u0, v1, z1)]
    # Front-left face (v = v0)
    left_poly = [p(u0, v0, z0), p(u1, v0, z0), p(u1, v0, z1), p(u0, v0, z1)]
    # Front-right face (u = u1)
    right_poly = [p(u1, v0, z0), p(u1, v1, z0), p(u1, v1, z1), p(u1, v0, z1)]

    for verts, fc in ((left_poly, left_color), (right_poly, right_color), (top_poly, top_color)):
        ax.add_patch(
            Polygon(
                verts,
                closed=True,
                facecolor=fc,
                edgecolor=edge_color if lw > 0 else "none",
                linewidth=lw,
                joinstyle="miter",
                alpha=alpha,
                zorder=zorder,
            )
        )

    return p(0.5 * (u0 + u1), 0.5 * (v0 + v1), z1)


def _default_campus_blocks() -> list[tuple[float, float, float, float, float]]:
    """Curated realistic urban campus/district building footprint layout (u0, v0, du, dv, h)."""
    return [
        # Back-left academic cluster
        (0.06, 0.72, 0.14, 0.20, 0.11),
        (0.08, 0.52, 0.12, 0.14, 0.17),
        (0.24, 0.78, 0.16, 0.14, 0.08),
        (0.24, 0.54, 0.13, 0.18, 0.13),
        # Central courtyard + focal landmark zone
        (0.45, 0.74, 0.18, 0.18, 0.15),
        (0.46, 0.48, 0.17, 0.16, 0.12),  # index 5 (ideal focal building)
        (0.67, 0.76, 0.22, 0.14, 0.10),
        (0.70, 0.53, 0.19, 0.17, 0.21),
        # Mid-front blocks along avenue
        (0.08, 0.28, 0.17, 0.14, 0.09),
        (0.09, 0.09, 0.14, 0.14, 0.14),
        (0.30, 0.25, 0.13, 0.16, 0.19),
        (0.28, 0.07, 0.16, 0.12, 0.07),
        (0.51, 0.23, 0.14, 0.15, 0.11),
        (0.52, 0.06, 0.20, 0.11, 0.09),
        # Front-right cluster
        (0.73, 0.29, 0.18, 0.14, 0.16),
        (0.76, 0.08, 0.15, 0.15, 0.12),
    ]


def draw_iso_clay_city(
    ax: plt.Axes,
    cx: float,
    cy: float,
    size: float = 3.4,
    blocks: Sequence[tuple[float, float, float, float, float]] | None = None,
    seed: int = 42,
    highlight_indices: Sequence[int] | None = (5,),
    highlight_color: str = "#F0C419",
    palette: str = "clay_white",
    angle_deg: float = 30.0,
    show_roads: bool = True,
    show_trees: bool = True,
    route_pts: Sequence[tuple[float, float]] | None = None,
    route_color: str = "#D6336C",
    stems: Sequence[tuple[float, float, float, str]] | None = None,
    zorder_base: float = 4.0,
) -> dict[str, list[tuple[float, float]]]:
    """Draw a matte white-clay 3D city massing model with focal accents, route, and 3D stems.

    Returns projected anchor coordinates: {'buildings': [...], 'route': [...], 'stems': [...]}.
    """
    if palette == "clay_white":
        pal = PALETTES["editorial_white"]
        top_c, left_c, right_c, edge_c = pal["clay_top"], pal["clay_left"], pal["clay_right"], pal["clay_edge"]
    elif palette == "virtual_slate":
        pal = PALETTES["interplay_twin"]
        top_c, left_c, right_c, edge_c = pal["virtual_top"], pal["virtual_left"], pal["virtual_right"], "#A4ACB8"
    else:
        pal = PALETTES["interplay_twin"]
        top_c, left_c, right_c, edge_c = pal["physical_top"], pal["physical_left"], pal["physical_right"], "#5268B5"

    # 1. Ground plinth slab
    draw_prism(
        ax,
        0.0,
        0.0,
        1.0,
        1.0,
        -0.025,
        0.0,
        cx,
        cy,
        size,
        top_color="#F8F9FA",
        left_color="#E4E7EC",
        right_color="#CFD4DC",
        edge_color="#C3C8D1",
        lw=0.45,
        angle_deg=angle_deg,
        zorder=zorder_base,
    )

    # 2. Road corridors & green pockets on ground plane
    if show_roads:
        roads = [
            (0.0, 0.42, 1.0, 0.46),
            (0.0, 0.20, 1.0, 0.23),
            (0.40, 0.0, 0.44, 1.0),
            (0.64, 0.0, 0.67, 1.0),
        ]
        for u0, v0, u1, v1 in roads:
            pts = [
                iso_project(u0, v0, 0.001, cx, cy, size, angle_deg),
                iso_project(u1, v0, 0.001, cx, cy, size, angle_deg),
                iso_project(u1, v1, 0.001, cx, cy, size, angle_deg),
                iso_project(u0, v1, 0.001, cx, cy, size, angle_deg),
            ]
            ax.add_patch(
                Polygon(pts, closed=True, facecolor="#E6E9EE", edgecolor="none", zorder=zorder_base + 0.1)
            )
        # Subtle green park patch
        park = [
            iso_project(0.24, 0.24, 0.0015, cx, cy, size, angle_deg),
            iso_project(0.39, 0.24, 0.0015, cx, cy, size, angle_deg),
            iso_project(0.39, 0.41, 0.0015, cx, cy, size, angle_deg),
            iso_project(0.24, 0.41, 0.0015, cx, cy, size, angle_deg),
        ]
        ax.add_patch(
            Polygon(park, closed=True, facecolor="#E1ECE2", edgecolor="none", zorder=zorder_base + 0.12)
        )

    # 3. Collect all depth-sorted 3D items (buildings, trees, stems)
    block_list = list(blocks) if blocks is not None else _default_campus_blocks()
    hl_set = set(highlight_indices or [])
    items: list[tuple[float, str, int, tuple[Any, ...]]] = []

    for idx, (u0, v0, du, dv, h_val) in enumerate(block_list):
        depth = (u0 + 0.5 * du) - (v0 + 0.5 * dv)
        items.append((depth, "building", idx, (u0, v0, u0 + du, v0 + dv, h_val)))

    if show_trees:
        rng = np.random.default_rng(seed)
        tree_spots = [
            (0.26, 0.36), (0.31, 0.37), (0.35, 0.29),
            (0.47, 0.43), (0.58, 0.43), (0.69, 0.48),
            (0.22, 0.72), (0.66, 0.70), (0.87, 0.47),
        ]
        for t_idx, (tu, tv) in enumerate(tree_spots):
            jitter_h = float(0.032 + rng.uniform(0.0, 0.014))
            items.append((tu - tv, "tree", t_idx, (tu, tv, jitter_h)))

    if stems:
        for s_idx, (su, sv, sz, scol) in enumerate(stems):
            items.append((su - sv, "stem", s_idx, (su, sv, sz, scol)))

    items.sort(key=lambda row: row[0])

    building_anchors: dict[int, tuple[float, float]] = {}
    stem_anchors: dict[int, tuple[float, float]] = {}

    for step_i, (_depth, kind, idx, payload) in enumerate(items):
        z_draw = zorder_base + 0.3 + step_i * 0.05
        if kind == "building":
            u0, v0, u1, v1, h_val = payload
            is_hl = idx in hl_set
            tc = highlight_color if is_hl else top_c
            lc = _shade_hex(highlight_color, 0.90) if is_hl else left_c
            rc = _shade_hex(highlight_color, 0.78) if is_hl else right_c
            ec = _shade_hex(highlight_color, 0.65) if is_hl else edge_c
            anchor = draw_prism(
                ax, u0, v0, u1, v1, 0.0, h_val, cx, cy, size,
                top_color=tc, left_color=lc, right_color=rc, edge_color=ec,
                lw=0.45 if is_hl else 0.38, angle_deg=angle_deg, zorder=z_draw,
            )
            building_anchors[idx] = anchor
        elif kind == "tree":
            tu, tv, th = payload
            draw_prism(
                ax, tu - 0.008, tv - 0.008, tu + 0.008, tv + 0.008, 0.0, th * 0.45,
                cx, cy, size, top_color="#B9B2A8", left_color="#9C958B", right_color="#857E75",
                edge_color="none", lw=0.0, angle_deg=angle_deg, zorder=z_draw,
            )
            cx_t, cy_t = iso_project(tu, tv, th * 0.65, cx, cy, size, angle_deg)
            ax.add_patch(
                Circle(
                    (cx_t, cy_t),
                    radius=size * 0.017,
                    facecolor="#C8DEC7",
                    edgecolor="#9EB99E",
                    linewidth=0.35,
                    zorder=z_draw + 0.02,
                )
            )
        elif kind == "stem":
            su, sv, sz, scol = payload
            w_s = 0.009
            anchor = draw_prism(
                ax, su - w_s, sv - w_s, su + w_s, sv + w_s, 0.0, sz,
                cx, cy, size,
                top_color=scol,
                left_color=_shade_hex(scol, 0.85),
                right_color=_shade_hex(scol, 0.70),
                edge_color=_shade_hex(scol, 0.55),
                lw=0.35, angle_deg=angle_deg, zorder=z_draw,
            )
            stem_anchors[idx] = anchor

    # 4. Walking / sensing route on road plane
    route_xy: list[tuple[float, float]] = []
    if route_pts and len(route_pts) >= 2:
        for ru, rv in route_pts:
            route_xy.append(iso_project(ru, rv, 0.004, cx, cy, size, angle_deg))
        rxs = [pt[0] for pt in route_xy]
        rys = [pt[1] for pt in route_xy]
        ax.plot(
            rxs,
            rys,
            color=route_color,
            linewidth=2.0,
            linestyle=(0, (2.2, 1.6)),
            zorder=zorder_base + 0.25,
        )
        for rx, ry in route_xy:
            ax.add_patch(
                Circle((rx, ry), radius=0.036, facecolor="#181C20", edgecolor="#FFFFFF", linewidth=0.6, zorder=zorder_base + 0.28)
            )

    return {
        "buildings": [building_anchors[i] for i in sorted(building_anchors)],
        "route": route_xy,
        "stems": [stem_anchors[i] for i in sorted(stem_anchors)],
    }


def draw_iso_voxel_city(
    ax: plt.Axes,
    cx: float,
    cy: float,
    size: float = 2.3,
    grid_n: int = 14,
    seed: int = 7,
    angle_deg: float = 30.0,
    show_prism: bool = False,
    prism_color: str = "#FFFFFF",
    zorder_base: float = 4.0,
) -> None:
    """Render a semantic 3D isometric voxel city (terrain + water + park + buildings + trees)."""
    rng = np.random.default_rng(seed)
    n = grid_n
    cell = 1.0 / n
    zh_unit = 0.038

    # Terrain & land cover map
    # 0=urban ground, 1=road, 2=park/grass, 3=water
    lc = np.zeros((n, n), dtype=int)
    lc[:, n // 2] = 1
    lc[n // 2, :] = 1
    lc[:4, n - 4 :] = 3  # water corner
    lc[2:6, 1:5] = 2     # park block
    lc[n - 5 : n - 1, 2:6] = 2

    # Building height map in voxel levels
    bh = np.zeros((n, n), dtype=int)
    bh[8:11, 8:11] = 7   # high-rise tower 1
    bh[9:11, 9:11] = 9
    bh[1:4, 8:10] = 4    # mid-rise slab
    bh[8:12, 1:4] = 5    # tower 2
    bh[2:5, 2:4] = 3     # low-rise

    # Tree canopy voxel height (0 or 2 levels above ground)
    th = np.zeros((n, n), dtype=int)
    for ix in range(n):
        for iy in range(n):
            if lc[ix, iy] == 2 and bh[ix, iy] == 0 and rng.random() < 0.55:
                th[ix, iy] = 2
            elif lc[ix, iy] == 0 and bh[ix, iy] == 0 and rng.random() < 0.14:
                th[ix, iy] = 1

    # Subtle terrain plinth step
    draw_prism(
        ax, 0.0, 0.0, 1.0, 1.0, -0.055, 0.0, cx, cy, size,
        top_color="#A8AEB7", left_color="#949BA5", right_color="#7E8590",
        edge_color="#FFFFFF", lw=0.7, angle_deg=angle_deg, zorder=zorder_base,
    )

    lc_colors = {
        0: ("#CFD4DC", "#B6BDC8", "#9CA4B0"),  # concrete/urban
        1: ("#727983", "#5F6670", "#4F555E"),  # road
        2: ("#78A95E", "#65934E", "#527B3E"),  # park grass
        3: ("#4A89B8", "#3B739E", "#2F5E84"),  # water
    }

    # Back-to-front painter sort: (ix - iy) ascending
    coords = [(ix, iy) for ix in range(n) for iy in range(n)]
    coords.sort(key=lambda c_xy: c_xy[0] - c_xy[1])

    z_cursor = zorder_base + 0.2
    for step_i, (ix, iy) in enumerate(coords):
        u0, v0 = ix * cell, iy * cell
        u1, v1 = u0 + cell, v0 + cell
        z_local = z_cursor + step_i * 0.005

        tc, lcol, rcol = lc_colors[int(lc[ix, iy])]
        draw_prism(
            ax, u0, v0, u1, v1, 0.0, zh_unit * 0.55, cx, cy, size,
            top_color=tc, left_color=lcol, right_color=rcol,
            edge_color="#6F7680" if lc[ix, iy] == 1 else "#D8DCE2",
            lw=0.22, angle_deg=angle_deg, zorder=z_local,
        )

        b_levels = int(bh[ix, iy])
        if b_levels > 0:
            draw_prism(
                ax, u0, v0, u1, v1, zh_unit * 0.55, zh_unit * (0.55 + b_levels),
                cx, cy, size,
                top_color="#F2F4F7", left_color="#D7DCE3", right_color="#B8C0CB",
                edge_color="#8C95A2", lw=0.28, angle_deg=angle_deg, zorder=z_local + 0.001,
            )
        elif th[ix, iy] > 0:
            t_top = zh_unit * (0.55 + th[ix, iy] * 0.9)
            draw_prism(
                ax, u0 + cell * 0.1, v0 + cell * 0.1, u1 - cell * 0.1, v1 - cell * 0.1,
                zh_unit * 0.75, t_top, cx, cy, size,
                top_color="#629B47", left_color="#4D8036", right_color="#3E6A2A",
                edge_color="#325521", lw=0.22, angle_deg=angle_deg, zorder=z_local + 0.001,
            )

    if show_prism:
        h_box = zh_unit * 10.2
        p = lambda uu, vv, zz: iso_project(uu, vv, zz, cx, cy, size, angle_deg)
        top_corners = [p(0, 0, h_box), p(1, 0, h_box), p(1, 1, h_box), p(0, 1, h_box)]
        bot_corners = [p(0, 0, 0), p(1, 0, 0), p(1, 1, 0), p(0, 1, 0)]
        ax.add_patch(
            Polygon(
                top_corners, closed=True, facecolor="none", edgecolor=prism_color,
                linewidth=0.9, linestyle=(0, (1.5, 1.5)), zorder=z_cursor + 3.0,
            )
        )
        for k in range(3):
            ax.plot(
                [bot_corners[k][0], top_corners[k][0]],
                [bot_corners[k][1], top_corners[k][1]],
                color=prism_color, linewidth=0.9, linestyle=(0, (1.5, 1.5)),
                zorder=z_cursor + 3.0,
            )


# ---------------------------------------------------------------------------
# Tilted GNN Planes, Loupes, Images, Diagonal Split, Icons & Badges
# ---------------------------------------------------------------------------

def draw_gnn_planes(
    ax: plt.Axes,
    cx: float,
    cy: float,
    w: float = 2.6,
    h: float = 1.45,
    n_planes: int = 2,
    highlight_idx: int = 1,
    accent: str = "#D95F02",
    secondary: str = "#4E9A8E",
    zorder_base: float = 5.0,
) -> None:
    """Draw tilted perspective GraphSAGE / GNN message-passing planes (Lei SCS 2023/2025)."""
    pw = w / max(1.0, n_planes * 0.92)
    spacing = pw * 0.95
    start_x = cx - 0.5 * ((n_planes - 1) * spacing)

    # Normalized local node positions inside tilted parallelogram plane
    local_nodes = [
        (0.24, 0.72),
        (0.55, 0.78),
        (0.76, 0.52),
        (0.46, 0.45),  # focal node index 3
        (0.20, 0.30),
        (0.68, 0.22),
    ]
    edges = [(0, 1), (0, 3), (1, 2), (1, 3), (2, 3), (3, 4), (3, 5), (2, 5)]

    def plane_pt(px_center: float, u: float, v: float) -> tuple[float, float]:
        # Subtle architectural slant matching UAL GraphSAGE figures
        x0 = px_center - pw * 0.44 + u * pw * 0.88 + (v - 0.5) * 0.14
        y0 = cy - h * 0.44 + v * h * 0.88 - (u - 0.5) * 0.22
        return x0, y0

    plane_node_coords: list[list[tuple[float, float]]] = []
    for p_i in range(n_planes):
        px_c = start_x + p_i * spacing
        corners = [
            plane_pt(px_c, 0.0, 0.0),
            plane_pt(px_c, 1.0, 0.0),
            plane_pt(px_c, 1.0, 1.0),
            plane_pt(px_c, 0.0, 1.0),
        ]
        ax.add_patch(
            Polygon(
                corners,
                closed=True,
                facecolor="#FFFFFF",
                edgecolor="#3E454E",
                linewidth=1.0,
                alpha=0.96,
                zorder=zorder_base + p_i * 0.4,
            )
        )
        pts = [plane_pt(px_c, nu, nv) for (nu, nv) in local_nodes]
        plane_node_coords.append(pts)

        for e_a, e_b in edges:
            ax.plot(
                [pts[e_a][0], pts[e_b][0]],
                [pts[e_a][1], pts[e_b][1]],
                color="#7C828D",
                linewidth=0.85,
                zorder=zorder_base + p_i * 0.4 + 0.1,
            )

        for n_i, (nx, ny) in enumerate(pts):
            if n_i == 3:
                fc = accent if p_i == 0 else accent
            elif n_i in (0, 1, 2, 4, 5) and p_i == highlight_idx:
                fc = secondary
            else:
                fc = "#B8BEC7"
            ax.add_patch(
                Circle(
                    (nx, ny),
                    radius=0.068 if n_i == 3 else 0.052,
                    facecolor=fc,
                    edgecolor="#22262B",
                    linewidth=0.75,
                    zorder=zorder_base + p_i * 0.4 + 0.2,
                )
            )

    # Inter-plane message-passing dashed links
    if n_planes >= 2:
        pts_a = plane_node_coords[0]
        pts_b = plane_node_coords[1]
        for idx, lcol in ((3, accent), (1, secondary), (5, secondary)):
            ax.plot(
                [pts_a[idx][0], pts_b[idx][0]],
                [pts_a[idx][1], pts_b[idx][1]],
                color=lcol,
                linewidth=0.95,
                linestyle=(0, (2.2, 1.8)),
                zorder=zorder_base + 1.2,
            )


def _load_image_array(img_or_array: str | Path | np.ndarray | Image.Image) -> np.ndarray:
    if isinstance(img_or_array, (str, Path)):
        with Image.open(img_or_array) as im:
            return np.asarray(im.convert("RGBA"))
    if isinstance(img_or_array, Image.Image):
        return np.asarray(img_or_array.convert("RGBA"))
    return np.asarray(img_or_array)


def place_image_loupe(
    ax: plt.Axes,
    img_or_array: str | Path | np.ndarray | Image.Image,
    cx: float,
    cy: float,
    radius: float = 0.82,
    rim_color: str = "#FFFFFF",
    rim_lw: float = 2.0,
    label: str | None = None,
    label_pos: str = "bottom",
    label_color: str = "#181C20",
    label_size: float = 8.8,
    zorder: float = 10.0,
) -> None:
    """Clip an image or raster array into a crisp circular zoom loupe."""
    arr = _load_image_array(img_or_array)
    h_px, w_px = arr.shape[:2]
    # Center-crop to square so circle displays without distortion
    side = min(h_px, w_px)
    y0 = (h_px - side) // 2
    x0 = (w_px - side) // 2
    sq = arr[y0 : y0 + side, x0 : x0 + side]

    clip_circle = Circle(
        (cx, cy),
        radius=radius,
        facecolor="none",
        edgecolor="none",
        transform=ax.transData,
    )
    ax.add_patch(clip_circle)

    im = ax.imshow(
        sq,
        extent=[cx - radius, cx + radius, cy - radius, cy + radius],
        interpolation="bilinear",
        zorder=zorder,
    )
    im.set_clip_path(clip_circle)

    ax.add_patch(
        Circle(
            (cx, cy),
            radius=radius,
            facecolor="none",
            edgecolor=rim_color,
            linewidth=rim_lw,
            zorder=zorder + 0.3,
        )
    )

    if label:
        off = radius + 0.12
        if label_pos == "top":
            lx, ly, ha, va = cx, cy + off, "center", "bottom"
        elif label_pos == "left":
            lx, ly, ha, va = cx - off, cy, "right", "center"
        elif label_pos == "right":
            lx, ly, ha, va = cx + off, cy, "left", "center"
        else:
            lx, ly, ha, va = cx, cy - off, "center", "top"
        ax.text(
            lx,
            ly,
            label,
            fontsize=label_size,
            fontweight="bold",
            color=label_color,
            ha=ha,
            va=va,
            zorder=zorder + 0.5,
        )


def place_image_box(
    ax: plt.Axes,
    img_or_array: str | Path | np.ndarray | Image.Image,
    x: float,
    y: float,
    w: float,
    h: float,
    border_color: str | None = None,
    border_lw: float = 0.8,
    zorder: float = 5.0,
) -> None:
    """Composite a transparent RGBA PNG or raster inside exact box bounds."""
    arr = _load_image_array(img_or_array)
    ax.imshow(
        arr,
        extent=[x, x + w, y, y + h],
        interpolation="bilinear",
        zorder=zorder,
    )
    if border_color and border_lw > 0:
        ax.add_patch(
            Rectangle(
                (x, y),
                w,
                h,
                facecolor="none",
                edgecolor=border_color,
                linewidth=border_lw,
                zorder=zorder + 0.2,
            )
        )


def draw_diagonal_split(
    ax: plt.Axes,
    arr_left: np.ndarray,
    arr_right: np.ndarray,
    x: float,
    y: float,
    w: float,
    h: float,
    cmap_left: str | mpl.colors.Colormap = "inferno",
    cmap_right: str | mpl.colors.Colormap = "viridis",
    split_color: str = "#FFFFFF",
    split_lw: float = 2.0,
    label_left: str = "",
    label_right: str = "",
    zorder: float = 6.0,
) -> None:
    """Render two aligned spatial arrays split cleanly by a diagonal white divider."""
    tri_left = Polygon(
        [(x, y), (x, y + h), (x + w, y + h)],
        closed=True,
        facecolor="none",
        edgecolor="none",
        transform=ax.transData,
    )
    tri_right = Polygon(
        [(x, y), (x + w, y), (x + w, y + h)],
        closed=True,
        facecolor="none",
        edgecolor="none",
        transform=ax.transData,
    )
    ax.add_patch(tri_left)
    ax.add_patch(tri_right)

    im_l = ax.imshow(
        arr_left,
        origin="lower",
        extent=[x, x + w, y, y + h],
        cmap=_resolve_cmap(cmap_left),
        interpolation="bilinear",
        zorder=zorder,
    )
    im_l.set_clip_path(tri_left)

    im_r = ax.imshow(
        arr_right,
        origin="lower",
        extent=[x, x + w, y, y + h],
        cmap=_resolve_cmap(cmap_right),
        interpolation="bilinear",
        zorder=zorder,
    )
    im_r.set_clip_path(tri_right)

    # Outer frame & diagonal divider
    ax.add_patch(
        Rectangle(
            (x, y),
            w,
            h,
            facecolor="none",
            edgecolor=split_color,
            linewidth=1.1,
            zorder=zorder + 0.3,
        )
    )
    ax.plot(
        [x, x + w],
        [y, y + h],
        color=split_color,
        linewidth=split_lw,
        solid_capstyle="butt",
        zorder=zorder + 0.4,
    )

    if label_left:
        t_l = ax.text(
            x + 0.08,
            y + h - 0.08,
            label_left,
            fontsize=7.6,
            fontweight="bold",
            color="#111111",
            ha="left",
            va="top",
            zorder=zorder + 0.6,
        )
        t_l.set_path_effects([pe.withStroke(linewidth=2.2, foreground="#FFFFFF"), pe.Normal()])
    if label_right:
        t_r = ax.text(
            x + w - 0.08,
            y + 0.08,
            label_right,
            fontsize=7.6,
            fontweight="bold",
            color="#111111",
            ha="right",
            va="bottom",
            zorder=zorder + 0.6,
        )
        t_r.set_path_effects([pe.withStroke(linewidth=2.2, foreground="#FFFFFF"), pe.Normal()])


# ---------------------------------------------------------------------------
# Uniform-Stroke Minimalist Wireframe Icons & File Export Badges
# ---------------------------------------------------------------------------

def draw_icon(
    ax: plt.Axes,
    kind: str,
    cx: float,
    cy: float,
    size: float = 0.38,
    color: str = "#FFFFFF",
    lw: float = 1.65,
    zorder: float = 8.0,
) -> None:
    """Draw a minimal uniform-stroke geometric wireframe icon."""
    r = size * 0.5

    if kind == "cloud_download":
        t1 = np.linspace(0, np.pi, 24)
        ax.plot(cx - r * 0.35 + r * 0.35 * np.cos(t1), cy + r * 0.05 + r * 0.35 * np.sin(t1), color=color, lw=lw, zorder=zorder)
        ax.plot(cx + r * 0.25 + r * 0.42 * np.cos(t1), cy + r * 0.12 + r * 0.42 * np.sin(t1), color=color, lw=lw, zorder=zorder)
        t2 = np.linspace(np.pi * 0.5, np.pi * 1.5, 16)
        ax.plot(cx - r * 0.55 + r * 0.28 * np.cos(t2), cy - r * 0.12 + r * 0.28 * np.sin(t2), color=color, lw=lw, zorder=zorder)
        t3 = np.linspace(-np.pi * 0.5, np.pi * 0.5, 16)
        ax.plot(cx + r * 0.55 + r * 0.28 * np.cos(t3), cy - r * 0.12 + r * 0.28 * np.sin(t3), color=color, lw=lw, zorder=zorder)
        ax.plot([cx - r * 0.55, cx - r * 0.18], [cy - r * 0.40, cy - r * 0.40], color=color, lw=lw, zorder=zorder)
        ax.plot([cx + r * 0.18, cx + r * 0.55], [cy - r * 0.40, cy - r * 0.40], color=color, lw=lw, zorder=zorder)
        # Downward arrow
        ax.plot([cx, cx], [cy + r * 0.12, cy - r * 0.58], color=color, lw=lw, zorder=zorder)
        ax.plot([cx - r * 0.22, cx, cx + r * 0.22], [cy - r * 0.36, cy - r * 0.58, cy - r * 0.36], color=color, lw=lw, zorder=zorder)

    elif kind == "iso_cube":
        pts = [
            (cx, cy + r * 0.85),
            (cx + r * 0.78, cy + r * 0.40),
            (cx + r * 0.78, cy - r * 0.42),
            (cx, cy - r * 0.85),
            (cx - r * 0.78, cy - r * 0.42),
            (cx - r * 0.78, cy + r * 0.40),
        ]
        ax.add_patch(Polygon(pts, closed=True, facecolor="none", edgecolor=color, lw=lw, zorder=zorder))
        ax.plot([cx, cx], [cy, cy - r * 0.85], color=color, lw=lw, zorder=zorder)
        ax.plot([cx, cx + r * 0.78], [cy, cy + r * 0.40], color=color, lw=lw, zorder=zorder)
        ax.plot([cx, cx - r * 0.78], [cy, cy + r * 0.40], color=color, lw=lw, zorder=zorder)

    elif kind == "y_merge":
        ax.plot([cx - r * 0.55, cx, cx + r * 0.55], [cy + r * 0.55, cy, cy + r * 0.55], color=color, lw=lw, zorder=zorder)
        ax.plot([cx, cx], [cy, cy - r * 0.70], color=color, lw=lw, zorder=zorder)
        ax.plot([cx - r * 0.25, cx, cx + r * 0.25], [cy - r * 0.44, cy - r * 0.70, cy - r * 0.44], color=color, lw=lw, zorder=zorder)

    elif kind == "line_chart":
        ax.plot([cx - r * 0.65, cx - r * 0.65, cx + r * 0.65], [cy + r * 0.65, cy - r * 0.60, cy - r * 0.60], color=color, lw=lw, zorder=zorder)
        px = [cx - r * 0.45, cx - r * 0.12, cx + r * 0.16, cx + r * 0.52]
        py = [cy - r * 0.28, cy + r * 0.22, cy - r * 0.08, cy + r * 0.45]
        ax.plot(px, py, color=color, lw=lw, zorder=zorder)
        for xi, yi in zip(px, py):
            ax.add_patch(Circle((xi, yi), radius=r * 0.09, facecolor=color, edgecolor="none", zorder=zorder + 0.1))

    elif kind == "export_arrow":
        ax.plot(
            [cx + r * 0.10, cx - r * 0.68, cx - r * 0.68, cx + r * 0.62, cx + r * 0.62],
            [cy + r * 0.58, cy + r * 0.58, cy - r * 0.62, cy - r * 0.62, cy - r * 0.05],
            color=color, lw=lw, zorder=zorder,
        )
        # Curved exit arrow
        arr = FancyArrowPatch(
            (cx - r * 0.22, cy - r * 0.18),
            (cx + r * 0.72, cy + r * 0.62),
            connectionstyle="arc3,rad=-0.28",
            arrowstyle="-|>",
            mutation_scale=10,
            color=color,
            linewidth=lw,
            zorder=zorder + 0.2,
        )
        ax.add_patch(arr)

    elif kind == "gear":
        ax.add_patch(Circle((cx, cy), radius=r * 0.48, facecolor="none", edgecolor=color, lw=lw, zorder=zorder))
        ax.add_patch(Circle((cx, cy), radius=r * 0.18, facecolor="none", edgecolor=color, lw=lw, zorder=zorder))
        for k in range(8):
            ang = k * math.pi / 4.0
            ax.plot(
                [cx + r * 0.48 * math.cos(ang), cx + r * 0.76 * math.cos(ang)],
                [cy + r * 0.48 * math.sin(ang), cy + r * 0.76 * math.sin(ang)],
                color=color, lw=lw * 1.15, zorder=zorder,
            )

    elif kind == "watch":
        ax.add_patch(Rectangle((cx - r * 0.30, cy - r * 0.85), r * 0.60, r * 1.70, facecolor="none", edgecolor=color, lw=lw * 0.85, zorder=zorder))
        ax.add_patch(FancyBboxPatch((cx - r * 0.48, cy - r * 0.50), r * 0.96, r * 1.00, boxstyle=f"round,pad=0.0,rounding_size={r*0.18}", facecolor="#1F242B", edgecolor=color, lw=lw, zorder=zorder + 0.1))

    elif kind == "graph":
        nodes = [(cx - r * 0.55, cy + r * 0.25), (cx + r * 0.05, cy + r * 0.55), (cx + r * 0.58, cy + r * 0.15), (cx - r * 0.15, cy - r * 0.45), (cx + r * 0.42, cy - r * 0.48)]
        for i, j in ((0, 1), (1, 2), (0, 3), (1, 3), (2, 4), (3, 4)):
            ax.plot([nodes[i][0], nodes[j][0]], [nodes[i][1], nodes[j][1]], color=color, lw=lw * 0.8, zorder=zorder)
        for nx, ny in nodes:
            ax.add_patch(Circle((nx, ny), radius=r * 0.14, facecolor=color, edgecolor="none", zorder=zorder + 0.2))

    elif kind == "human":
        ax.add_patch(Circle((cx, cy + r * 0.55), radius=r * 0.22, facecolor="none", edgecolor=color, lw=lw, zorder=zorder))
        ax.plot([cx, cx], [cy + r * 0.32, cy - r * 0.25], color=color, lw=lw, zorder=zorder)
        ax.plot([cx - r * 0.42, cx + r * 0.42], [cy + r * 0.15, cy + r * 0.15], color=color, lw=lw, zorder=zorder)
        ax.plot([cx - r * 0.32, cx, cx + r * 0.32], [cy - r * 0.78, cy - r * 0.25, cy - r * 0.78], color=color, lw=lw, zorder=zorder)

    elif kind == "layers":
        for dy in (-0.28 * r, 0.0, 0.28 * r):
            pts = [(cx - r * 0.65, cy + dy), (cx, cy + dy + r * 0.25), (cx + r * 0.65, cy + dy), (cx, cy + dy - r * 0.25)]
            ax.add_patch(Polygon(pts, closed=True, facecolor="none", edgecolor=color, lw=lw * 0.9, zorder=zorder))

    elif kind in ("sensor", "target"):
        ax.add_patch(Circle((cx, cy), radius=r * 0.62, facecolor="none", edgecolor=color, lw=lw, zorder=zorder))
        ax.add_patch(Circle((cx, cy), radius=r * 0.26, facecolor="none", edgecolor=color, lw=lw, zorder=zorder))
        ax.plot([cx - r * 0.85, cx + r * 0.85], [cy, cy], color=color, lw=lw * 0.75, zorder=zorder)
        ax.plot([cx, cx], [cy - r * 0.85, cy + r * 0.85], color=color, lw=lw * 0.75, zorder=zorder)

    elif kind == "play_tri":
        pts = [
            (cx - r * 0.45, cy + r * 0.55),
            (cx + r * 0.55, cy),
            (cx - r * 0.45, cy - r * 0.55),
        ]
        ax.add_patch(Polygon(pts, closed=True, facecolor="none", edgecolor=color, lw=lw, joinstyle="miter", zorder=zorder))

    elif kind == "energy":
        pts = [
            (cx + r * 0.12, cy + r * 0.72),
            (cx - r * 0.40, cy + r * 0.02),
            (cx - r * 0.02, cy + r * 0.02),
            (cx - r * 0.16, cy - r * 0.72),
            (cx + r * 0.42, cy - r * 0.04),
            (cx + r * 0.02, cy - r * 0.04),
        ]
        ax.add_patch(Polygon(pts, closed=True, facecolor="none", edgecolor=color, lw=lw, joinstyle="miter", zorder=zorder))

    elif kind == "climate":
        t1 = np.linspace(0, np.pi, 20)
        ax.plot(cx - r * 0.25 + r * 0.35 * np.cos(t1), cy + r * 0.18 + r * 0.35 * np.sin(t1), color=color, lw=lw, zorder=zorder)
        ax.plot(cx + r * 0.28 + r * 0.28 * np.cos(t1), cy + r * 0.14 + r * 0.28 * np.sin(t1), color=color, lw=lw, zorder=zorder)
        ax.plot([cx - r * 0.60, cx + r * 0.56], [cy + r * 0.14, cy + r * 0.14], color=color, lw=lw, zorder=zorder)
        ax.plot([cx - r * 0.52, cx + r * 0.44], [cy - r * 0.16, cy - r * 0.16], color=color, lw=lw * 0.9, zorder=zorder)
        ax.plot([cx - r * 0.36, cx + r * 0.54], [cy - r * 0.42, cy - r * 0.42], color=color, lw=lw * 0.9, zorder=zorder)

    elif kind == "building_city":
        ax.add_patch(Rectangle((cx - r * 0.68, cy - r * 0.60), r * 0.46, r * 0.95, facecolor="none", edgecolor=color, lw=lw, zorder=zorder))
        ax.add_patch(Rectangle((cx - r * 0.22, cy - r * 0.60), r * 0.48, r * 1.25, facecolor="none", edgecolor=color, lw=lw, zorder=zorder))
        ax.add_patch(Rectangle((cx + r * 0.26, cy - r * 0.60), r * 0.42, r * 0.72, facecolor="none", edgecolor=color, lw=lw, zorder=zorder))
        for wx in (-0.04, 0.10):
            for wy in (0.05, 0.34):
                ax.plot([cx + r * wx, cx + r * wx], [cy + r * wy, cy + r * (wy + 0.12)], color=color, lw=lw * 0.85, zorder=zorder)

    elif kind == "camera":
        ax.add_patch(Rectangle((cx - r * 0.74, cy - r * 0.48), r * 1.48, r * 0.96, facecolor="none", edgecolor=color, lw=lw, zorder=zorder))
        ax.add_patch(Polygon([(cx - r * 0.32, cy + r * 0.48), (cx - r * 0.18, cy + r * 0.72), (cx + r * 0.18, cy + r * 0.72), (cx + r * 0.32, cy + r * 0.48)], closed=True, facecolor="none", edgecolor=color, lw=lw, zorder=zorder))
        ax.add_patch(Circle((cx, cy), radius=r * 0.30, facecolor="none", edgecolor=color, lw=lw, zorder=zorder))

    elif kind == "sound":
        bars = [(-0.56, 0.30), (-0.28, 0.58), (0.0, 0.82), (0.28, 0.52), (0.56, 0.32)]
        for bx, bh_s in bars:
            ax.plot([cx + r * bx, cx + r * bx], [cy - r * bh_s, cy + r * bh_s], color=color, lw=lw * 1.15, solid_capstyle="round", zorder=zorder)

    elif kind == "leaf":
        t = np.linspace(0.0, 1.0, 24)
        lx1 = cx - r * 0.55 + r * 1.10 * t
        ly_top = cy + r * 0.55 * np.sin(np.pi * t) - r * 0.10 * (1 - t)
        ly_bot = cy - r * 0.42 * np.sin(np.pi * t) - r * 0.10 * (1 - t)
        ax.plot(lx1, ly_top, color=color, lw=lw, zorder=zorder)
        ax.plot(lx1, ly_bot, color=color, lw=lw, zorder=zorder)
        ax.plot([cx - r * 0.65, cx + r * 0.45], [cy - r * 0.22, cy + r * 0.04], color=color, lw=lw * 0.9, zorder=zorder)


def draw_file_badge(
    ax: plt.Axes,
    ext: str,
    cx: float,
    cy: float,
    size: float = 0.42,
    name: str = "",
    sublabel: str = "",
    stroke: str = "#2D333B",
    text_color: str = "#181C20",
    sub_color: str = "#4B525E",
    bg_fill: str = "#FFFFFF",
    zorder: float = 7.0,
) -> None:
    """Draw a dark-slate folded-corner file icon with extension tag and short labels."""
    w = size * 0.86
    h = size * 1.12
    fold = size * 0.25
    x0 = cx - w * 0.5
    y0 = cy - h * 0.5

    doc_pts = [
        (x0, y0),
        (x0 + w, y0),
        (x0 + w, y0 + h - fold),
        (x0 + w - fold, y0 + h),
        (x0, y0 + h),
    ]
    ax.add_patch(
        Polygon(
            doc_pts,
            closed=True,
            facecolor=bg_fill,
            edgecolor=stroke,
            linewidth=1.55,
            joinstyle="miter",
            zorder=zorder,
        )
    )
    # Fold crease
    ax.plot(
        [x0 + w - fold, x0 + w - fold, x0 + w],
        [y0 + h, y0 + h - fold, y0 + h - fold],
        color=stroke,
        linewidth=1.35,
        zorder=zorder + 0.2,
    )
    # Dark extension band inside lower half of badge
    band_h = h * 0.38
    ax.add_patch(
        Rectangle(
            (x0 + 0.03, y0 + 0.05),
            w - 0.06,
            band_h,
            facecolor=stroke,
            edgecolor="none",
            zorder=zorder + 0.2,
        )
    )
    ax.text(
        cx,
        y0 + 0.05 + band_h * 0.5,
        ext.upper().lstrip("."),
        fontsize=7.6,
        fontweight="bold",
        color="#FFFFFF",
        ha="center",
        va="center",
        zorder=zorder + 0.4,
    )

    if name:
        ax.text(
            cx,
            y0 - 0.11,
            name,
            fontsize=8.8,
            fontweight="bold",
            color=text_color,
            ha="center",
            va="top",
            zorder=zorder + 0.4,
        )
    if sublabel:
        ax.text(
            cx,
            y0 - 0.30,
            sublabel,
            fontsize=7.6,
            color=sub_color,
            ha="center",
            va="top",
            zorder=zorder + 0.4,
        )


def draw_compact_colorbar(
    ax: plt.Axes,
    x: float,
    y: float,
    w: float,
    h: float,
    cmap: str | mpl.colors.Colormap,
    vmin_label: str,
    vmax_label: str,
    title: str = "",
    text_color: str = "#22262B",
    fontsize: float = 7.6,
    zorder: float = 8.0,
) -> None:
    """Draw a compact flat horizontal scientific colorbar with min/max end ticks."""
    grad = np.linspace(0.0, 1.0, 256).reshape(1, -1)
    ax.imshow(
        grad,
        extent=[x, x + w, y, y + h],
        cmap=_resolve_cmap(cmap),
        aspect="auto",
        interpolation="bilinear",
        zorder=zorder,
    )
    ax.add_patch(
        Rectangle(
            (x, y),
            w,
            h,
            facecolor="none",
            edgecolor="#FFFFFF" if text_color == "#111111" else "#9CA3AF",
            linewidth=0.75,
            zorder=zorder + 0.2,
        )
    )
    if title:
        ax.text(
            x + w * 0.5,
            y + h + 0.05,
            title,
            fontsize=fontsize,
            fontweight="bold",
            color=text_color,
            ha="center",
            va="bottom",
            zorder=zorder + 0.4,
        )
    ax.text(
        x,
        y - 0.04,
        vmin_label,
        fontsize=fontsize - 0.3,
        color=text_color,
        ha="left",
        va="top",
        zorder=zorder + 0.4,
    )
    ax.text(
        x + w,
        y - 0.04,
        vmax_label,
        fontsize=fontsize - 0.3,
        color=text_color,
        ha="right",
        va="top",
        zorder=zorder + 0.4,
    )


# ---------------------------------------------------------------------------
# Archetype C & D Specialized Primitives (Twin Arcs, Underlines, Flow Triangles)
# ---------------------------------------------------------------------------

def draw_bidirectional_arcs(
    ax: plt.Axes,
    cx: float,
    cy: float,
    w: float = 1.78,
    h: float = 1.90,
    arc_color: str = "#DCE1EA",
    arrow_color: str = "#6C737F",
    label: str = "Bidirectional\nInformation\nExchange",
    label_size: float = 8.6,
    zorder: float = 6.0,
) -> None:
    """Draw paired upper (left->right) and lower (right->left) curved exchange arcs."""
    half_w = w * 0.5
    half_h = h * 0.5
    top_p0 = (cx - half_w, cy + half_h * 0.55)
    top_p1 = (cx + half_w, cy + half_h * 0.55)
    bot_p0 = (cx + half_w, cy - half_h * 0.55)
    bot_p1 = (cx - half_w, cy - half_h * 0.55)

    for p0, p1 in ((top_p0, top_p1), (bot_p0, bot_p1)):
        # Translucent thick band
        ax.add_patch(
            FancyArrowPatch(
                p0,
                p1,
                connectionstyle="arc3,rad=-0.42",
                arrowstyle="-|>",
                mutation_scale=16,
                color=arc_color,
                linewidth=8.5,
                alpha=0.90,
                zorder=zorder,
            )
        )
        # Crisp thin directional inner centerline
        ax.add_patch(
            FancyArrowPatch(
                p0,
                p1,
                connectionstyle="arc3,rad=-0.42",
                arrowstyle="-|>",
                mutation_scale=11,
                color=arrow_color,
                linewidth=1.35,
                zorder=zorder + 0.4,
            )
        )

    if label:
        ax.text(
            cx,
            cy,
            label,
            fontsize=label_size,
            fontweight="bold",
            color="#181C20",
            ha="center",
            va="center",
            zorder=zorder + 1.0,
        )


def draw_underlined_header(
    ax: plt.Axes,
    x: float,
    y: float,
    text: str,
    fontsize: float = 9.2,
    color: str = "#181C20",
    ha: str = "left",
    italic: bool = True,
    lw: float = 0.85,
    zorder: float = 8.0,
) -> None:
    """Draw bold-italic underlined dimension header (Lei SCS 2025 GA style)."""
    ax.text(
        x,
        y,
        text,
        fontsize=fontsize,
        fontweight="bold",
        fontstyle="italic" if italic else "normal",
        color=color,
        ha=ha,
        va="bottom",
        zorder=zorder,
    )
    est_w = len(text) * fontsize * 0.0065
    if ha == "center":
        x0, x1 = x - est_w * 0.5, x + est_w * 0.5
    elif ha == "right":
        x0, x1 = x - est_w, x
    else:
        x0, x1 = x, x + est_w
    ax.plot([x0, x1], [y - 0.025, y - 0.025], color=color, linewidth=lw, zorder=zorder)


def draw_flow_triangle(
    ax: plt.Axes,
    cx: float,
    cy: float,
    direction: str = "down",
    size: float = 0.14,
    color: str = "#343A40",
    zorder: float = 7.0,
) -> None:
    """Draw solid equilateral progression triangle (up/down/left/right; Lei CEUS 2026)."""
    r = size * 0.65
    if direction == "right":
        pts = [(cx - r * 0.6, cy + r * 0.8), (cx + r * 0.9, cy), (cx - r * 0.6, cy - r * 0.8)]
    elif direction == "left":
        pts = [(cx + r * 0.6, cy + r * 0.8), (cx - r * 0.9, cy), (cx + r * 0.6, cy - r * 0.8)]
    elif direction == "up":
        pts = [(cx - r * 0.8, cy - r * 0.6), (cx + r * 0.8, cy - r * 0.6), (cx, cy + r * 0.9)]
    else:
        pts = [(cx - r * 0.8, cy + r * 0.6), (cx + r * 0.8, cy + r * 0.6), (cx, cy - r * 0.9)]
    ax.add_patch(Polygon(pts, closed=True, facecolor=color, edgecolor="none", zorder=zorder))
