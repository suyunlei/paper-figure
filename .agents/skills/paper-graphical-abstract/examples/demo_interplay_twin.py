"""
demo_interplay_twin.py — Archetype C Showcase
Isometric Conceptual Interplay & Digital Twin Mirror
(Distilled from Binyu Lei: Cities 2026 Fig. 1, SCS 2025 Urban Comfort GA, 3D GeoInfo 2024).

Generates high-resolution PNG + editable vector SVG at:
  .agents/skills/paper-graphical-abstract/examples/output/demo_archetype_c_interplay_twin.{png,svg}
"""

from __future__ import annotations

from pathlib import Path
import sys

from matplotlib.patches import Circle, FancyBboxPatch
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ual_ga_kit import (
    PALETTES,
    create_canvas,
    draw_bidirectional_arcs,
    draw_icon,
    draw_iso_clay_city,
    draw_ortho_leader,
    draw_underlined_header,
    save_publication_figure,
)


def _draw_twin_callout(
    ax,
    x: float,
    y: float,
    w: float,
    h: float,
    icon_kind: str,
    accent: str,
    title: str,
    subtitle: str,
    zorder: float = 8.0,
) -> None:
    """Draw clean hairline rounded callout with circled accent glyph & underlined italic header."""
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.0,rounding_size=0.12",
        facecolor="#FFFFFF",
        edgecolor="#C6CCD6",
        linewidth=0.88,
        zorder=zorder,
    )
    ax.add_patch(box)

    icon_r = min(0.24, h * 0.29)
    icx = x + 0.16 + icon_r
    icy = y + h * 0.5
    ax.add_patch(
        Circle(
            (icx, icy),
            radius=icon_r,
            facecolor="#F7F8FA",
            edgecolor=accent,
            linewidth=1.15,
            zorder=zorder + 0.2,
        )
    )
    draw_icon(ax, icon_kind, icx, icy, size=icon_r * 1.18, color=accent, lw=1.35, zorder=zorder + 0.4)

    tx = icx + icon_r + 0.14
    draw_underlined_header(
        ax,
        tx,
        y + h * 0.54,
        title,
        fontsize=8.6,
        color="#181C20",
        ha="left",
        italic=True,
        lw=0.80,
        zorder=zorder + 0.5,
    )
    ax.text(
        tx,
        y + h * 0.40,
        subtitle,
        fontsize=7.6,
        color="#4A525E",
        ha="left",
        va="top",
        zorder=zorder + 0.5,
    )


def build_demo(out_stem: Path) -> None:
    pal = PALETTES["interplay_twin"]
    fig, ax = create_canvas(
        figsize=(16.0, 10.0),
        theme="interplay_twin",
        dpi=300,
        title="Urban Digital Twins: Bidirectional Physical-Virtual Interplay",
        subtitle="Coupling real-world urban sensing and human perception with virtual physics simulation and adaptive planning",
        title_x=0.40,
        title_y=9.66,
    )

    # -----------------------------------------------------------------------
    # Left & Right Subtle Framing Panels (#F1F3F6 for crisp architectural separation)
    # -----------------------------------------------------------------------
    for px, heading in ((0.40, "Physical Environment"), (9.14, "Virtual Environment")):
        ax.add_patch(
            FancyBboxPatch(
                (px, 1.18),
                6.46,
                7.46,
                boxstyle="round,pad=0.0,rounding_size=0.14",
                facecolor="#F1F3F6",
                edgecolor="#CED4DE",
                linewidth=0.95,
                zorder=1.5,
            )
        )
        ax.text(
            px + 3.23,
            8.44,
            heading,
            fontsize=11.6,
            fontweight="bold",
            color=pal["title"],
            ha="center",
            va="top",
            zorder=4,
        )

    # -----------------------------------------------------------------------
    # Left Twin: Periwinkle Physical City Diorama + 4 Callouts
    # -----------------------------------------------------------------------
    p_cx, p_cy, p_sz = 4.86, 4.78, 1.82
    draw_iso_clay_city(
        ax,
        cx=p_cx,
        cy=p_cy,
        size=p_sz,
        highlight_indices=(),
        palette="interplay_twin",
        show_roads=True,
        show_trees=True,
        zorder_base=4.0,
    )

    # Callout cards placed strictly outside diorama footprint [3.28..6.44] x [3.87..6.05]
    _draw_twin_callout(ax, 1.85, 6.94, 3.88, 0.84, "energy", "#5D73C9", "Energy & Mobility Demand", "Buildings, transit & urban flows")
    draw_ortho_leader(ax, (4.86, 5.74), (4.20, 6.94), elbow="vh", color="#7C828D")

    _draw_twin_callout(ax, 0.56, 4.28, 2.52, 1.02, "climate", "#4E9A8E", "Microclimate", "Heat, wind & solar")
    draw_ortho_leader(ax, (3.44, 4.79), (3.08, 4.79), elbow="hv", color="#7C828D")

    _draw_twin_callout(ax, 0.56, 1.56, 2.94, 0.90, "building_city", "#D49B35", "3D Urban Morphology", "Street canyon & form")
    draw_ortho_leader(ax, (4.12, 4.10), (2.25, 2.46), elbow="vh", color="#7C828D")

    _draw_twin_callout(ax, 3.72, 1.56, 2.96, 0.90, "human", "#5B9A59", "Human Perception", "Comfort & walking routes")
    draw_ortho_leader(ax, (5.52, 4.14), (5.52, 2.46), elbow="vh", color="#7C828D")

    # -----------------------------------------------------------------------
    # Center Bidirectional Exchange Bridge
    # -----------------------------------------------------------------------
    draw_bidirectional_arcs(
        ax,
        cx=8.00,
        cy=4.78,
        w=1.84,
        h=1.96,
        arc_color="#DCE1EA",
        arrow_color="#6C737F",
        label="Bidirectional\nInformation\nExchange",
        label_size=8.6,
        zorder=6.0,
    )
    ax.text(8.00, 6.18, "Sensing & Telemetry", fontsize=8.0, fontweight="bold", color="#4A525E", ha="center", va="bottom", zorder=7)
    ax.text(8.00, 3.38, "Adaptive Interventions", fontsize=8.0, fontweight="bold", color="#4A525E", ha="center", va="top", zorder=7)
    ax.text(8.00, 2.66, "Urban Digital Twin", fontsize=10.6, fontweight="bold", color=pal["title"], ha="center", va="top", zorder=7)

    # -----------------------------------------------------------------------
    # Right Twin: Silver-Slate Virtual City Diorama + 4 Mirrored Callouts
    # -----------------------------------------------------------------------
    v_cx, v_cy, v_sz = 11.14, 4.78, 1.82
    draw_iso_clay_city(
        ax,
        cx=v_cx,
        cy=v_cy,
        size=v_sz,
        highlight_indices=(),
        palette="virtual_slate",
        show_roads=True,
        show_trees=True,
        zorder_base=4.0,
    )

    _draw_twin_callout(ax, 10.27, 6.94, 3.88, 0.84, "energy", "#5D73C9", "Efficiency Monitoring", "Real-time load & tracking")
    draw_ortho_leader(ax, (11.14, 5.74), (11.80, 6.94), elbow="vh", color="#7C828D")

    _draw_twin_callout(ax, 12.92, 4.28, 2.52, 1.02, "climate", "#4E9A8E", "Physics Simulation", "CFD wind & radiation")
    draw_ortho_leader(ax, (12.56, 4.79), (12.92, 4.79), elbow="hv", color="#7C828D")

    _draw_twin_callout(ax, 9.32, 1.56, 2.96, 0.90, "building_city", "#D49B35", "What-If Planning", "Pre- & post-design tests")
    draw_ortho_leader(ax, (10.48, 4.14), (10.48, 2.46), elbow="vh", color="#7C828D")

    _draw_twin_callout(ax, 12.50, 1.56, 2.94, 0.90, "human", "#5B9A59", "Quality-of-Life Nudges", "JITAI shade & route tips")
    draw_ortho_leader(ax, (11.88, 4.10), (13.75, 2.46), elbow="vh", color="#7C828D")

    # -----------------------------------------------------------------------
    # Bottom Concise Thesis Anchor
    # -----------------------------------------------------------------------
    ax.text(
        8.00,
        0.66,
        "Continuous two-way feedback couples dynamic urban environments with human-centric spatial decisions.",
        fontsize=9.4,
        fontstyle="italic",
        color=pal["subtitle"],
        ha="center",
        va="center",
        zorder=8,
    )

    save_publication_figure(fig, out_stem, formats=("png", "svg"), dpi=300)


if __name__ == "__main__":
    out = ROOT / "examples" / "output" / "demo_archetype_c_interplay_twin"
    build_demo(out)
    print(f"[OK] Saved {out}.png and {out}.svg")
