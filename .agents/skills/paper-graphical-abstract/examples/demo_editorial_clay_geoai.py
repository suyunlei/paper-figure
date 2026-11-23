"""
demo_editorial_clay_geoai.py — Archetype B Showcase
Editorial White Clay-3D + Circular Context Loupes & Modular Method Column
(Distilled from Binyu Lei: SCS 2023, ISPRS 2024, SCS 2025, Cities 2026).

Generates high-resolution PNG + editable Type-42 vector PDF at:
  .agents/skills/paper-graphical-abstract/examples/output/demo_archetype_b_editorial_clay.{png,pdf}
"""

from __future__ import annotations

from pathlib import Path
import sys

from matplotlib.patches import Circle, Rectangle
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ual_ga_kit import (
    PALETTES,
    create_canvas,
    draw_bracket_list,
    draw_dashed_zone,
    draw_gnn_planes,
    draw_header_panel,
    draw_icon,
    draw_iso_clay_city,
    draw_iso_layer_grid,
    draw_leader_line,
    draw_micro_table,
    draw_pill_tag,
    draw_stage_arrow,
    place_image_loupe,
    save_publication_figure,
)


def _make_street_loupe_vignette(kind: str, n: int = 140) -> np.ndarray:
    """Create crisp architectural streetscape / microclimate photo-style vignettes."""
    yy, xx = np.meshgrid(np.linspace(0.0, 1.0, n), np.linspace(0.0, 1.0, n))
    img = np.ones((n, n, 3), dtype=float)

    if kind == "street":
        # Sky gradient + road perspective + warm facade + tree canopy
        sky = np.array([0.74, 0.85, 0.96])
        road = np.array([0.36, 0.39, 0.43])
        facade_l = np.array([0.84, 0.85, 0.88])
        facade_r = np.array([0.76, 0.78, 0.82])
        tree = np.array([0.32, 0.56, 0.34])

        img[:, :] = sky
        # Road trapezoid bottom
        road_m = yy < (0.44 - 0.16 * np.abs(xx - 0.5))
        img[road_m] = road
        # Left building facade
        bld_l = (xx < 0.30) & (yy > 0.25) & (yy < 0.82 - 0.25 * xx)
        img[bld_l] = facade_l
        # Right building facade
        bld_r = (xx > 0.68) & (yy > 0.25) & (yy < 0.78 - 0.22 * (1.0 - xx))
        img[bld_r] = facade_r
        # Tree cluster right-mid
        canopy = ((xx - 0.64) ** 2 + (yy - 0.54) ** 2) < 0.045
        img[canopy] = tree
        # Center dashed road marking
        dash = (np.abs(xx - 0.50) < 0.015) & (yy < 0.32) & ((np.floor(yy * 18) % 2) == 0)
        img[dash] = np.array([0.92, 0.92, 0.92])

    elif kind == "canopy":
        # Shaded green walkway vignette
        img[:, :] = np.array([0.76, 0.87, 0.95])
        ground = yy < 0.38
        img[ground] = np.array([0.45, 0.52, 0.44])
        path = (np.abs(xx - 0.5) < (0.06 + 0.18 * (0.38 - yy))) & ground
        img[path] = np.array([0.72, 0.73, 0.70])
        for cx_c, cy_c, rad, col in [
            (0.28, 0.56, 0.22, [0.24, 0.50, 0.27]),
            (0.72, 0.58, 0.24, [0.28, 0.56, 0.30]),
            (0.50, 0.74, 0.20, [0.34, 0.62, 0.34]),
        ]:
            m = ((xx - cx_c) ** 2 + (yy - cy_c) ** 2) < rad ** 2
            img[m] = col

    else:
        # Focal amber building context vignette
        img[:, :] = np.array([0.78, 0.86, 0.94])
        plaza = yy < 0.34
        img[plaza] = np.array([0.82, 0.83, 0.85])
        # Amber focal courtyard block
        focal = (xx > 0.24) & (xx < 0.76) & (yy >= 0.30) & (yy < 0.74)
        img[focal] = np.array([0.94, 0.77, 0.14])
        side = (xx >= 0.56) & (xx < 0.76) & (yy >= 0.30) & (yy < 0.74)
        img[side] = np.array([0.80, 0.63, 0.09])
        # Subtle window grid
        win = focal & ((np.floor(yy * 24) % 2) == 0) & ((np.floor(xx * 24) % 2) == 0) & (yy < 0.68)
        img[win] = np.array([0.42, 0.34, 0.08])

    return np.clip(img, 0.0, 1.0)


def _make_disc_grid(kind: str, n: int = 36) -> np.ndarray:
    """Create restrained monochrome/duotone spatial feature disc matrices."""
    yy, xx = np.meshgrid(np.linspace(-1.0, 1.0, n), np.linspace(-1.0, 1.0, n))
    rng = np.random.default_rng({"morph": 1, "socio": 2, "perc": 3, "micro": 4}[kind])
    base = np.exp(-((xx - 0.15) ** 2 + (yy + 0.10) ** 2) / 0.55)
    noise = 0.28 * rng.random((n, n))
    if kind == "morph":
        return np.clip(base * 0.75 + noise, 0.05, 1.0)
    if kind == "socio":
        return np.clip(np.exp(-((xx + 0.25) ** 2 + (yy - 0.20) ** 2) / 0.45) * 0.8 + noise, 0.05, 1.0)
    if kind == "perc":
        return np.clip(0.5 + 0.4 * np.sin(xx * 3.1) * np.cos(yy * 2.5) + 0.2 * noise, 0.05, 1.0)
    return np.clip(0.65 * np.exp(-((xx) ** 2 + (yy) ** 2) / 0.65) + noise, 0.05, 1.0)


def build_demo(out_stem: Path) -> None:
    pal = PALETTES["editorial_white"]
    fig, ax = create_canvas(
        figsize=(16.0, 10.0),
        theme="editorial_white",
        dpi=300,
        title="Human-Centric Urban Digital Twin & Explainable Comfort Analytics",
        subtitle="Fusing wearable human sensing, white-clay 3D city massing, and inductive GNNs for outdoor comfort prediction",
        title_x=0.38,
        title_y=9.66,
    )

    # -----------------------------------------------------------------------
    # LEFT HALF: Spatial & Human-Sensing Anchor (Clay 3D + Loupes + Table)
    # -----------------------------------------------------------------------
    ax.text(
        0.38, 8.78, "Spatial Context & Human-in-the-Loop Sensing",
        fontsize=11.5, fontweight="bold", color=pal["title"], ha="left", va="top", zorder=12,
    )

    route = [(0.16, 0.44), (0.42, 0.44), (0.42, 0.22), (0.65, 0.22), (0.65, 0.68), (0.86, 0.68)]
    stems = [
        (0.32, 0.45, 0.20, pal["stem_cobalt"]),
        (0.41, 0.60, 0.23, pal["stem_cobalt"]),
        (0.42, 0.50, 0.28, pal["stem_cobalt"]),
        (0.24, 0.21, 0.22, pal["stem_magenta"]),
        (0.64, 0.34, 0.17, "#8E97A4"),
    ]

    anchors = draw_iso_clay_city(
        ax,
        cx=4.38,
        cy=4.15,
        size=3.20,
        highlight_indices=(5,),
        highlight_color=pal["focal_gold"],
        palette="clay_white",
        route_pts=route,
        route_color=pal["stem_magenta"],
        stems=stems,
        zorder_base=4.0,
    )

    # 3 Circular Context Loupes with Dotted Leader Lines (labels clear of leaders)
    loupe_street = _make_street_loupe_vignette("street")
    loupe_canopy = _make_street_loupe_vignette("canopy")
    loupe_focal = _make_street_loupe_vignette("focal")

    place_image_loupe(
        ax, loupe_street, cx=1.35, cy=7.02, radius=0.86,
        rim_color="#4B525E", rim_lw=1.3, label="Streetscape Exposure", label_pos="top",
        label_color=pal["title"], label_size=8.8, zorder=10,
    )
    draw_leader_line(ax, anchors["route"][0], (1.84, 6.32), style="dotted", color=pal["leader"], curved=-0.16)

    place_image_loupe(
        ax, loupe_canopy, cx=7.28, cy=7.02, radius=0.84,
        rim_color="#4B525E", rim_lw=1.3, label="Canopy & Shade Path", label_pos="top",
        label_color=pal["title"], label_size=8.8, zorder=10,
    )
    draw_leader_line(ax, anchors["route"][4], (6.80, 6.32), style="dotted", color=pal["leader"], curved=0.14)

    place_image_loupe(
        ax, loupe_focal, cx=7.28, cy=1.58, radius=0.84,
        rim_color="#4B525E", rim_lw=1.3, label="Focal 3D Building", label_pos="top",
        label_color=pal["title"], label_size=8.8, zorder=10,
    )
    # Anchor directly onto highlighted focal building #5
    draw_leader_line(ax, anchors["buildings"][5], (6.50, 1.92), style="dotted", color=pal["leader"], curved=0.18)

    # Floating Semantic Pill Callouts linked to 3D Stems
    draw_pill_tag(ax, 4.32, 7.22, "Urban Comfort: High", bg=pal["stem_cobalt"], fg="#FFFFFF", fontsize=8.8)
    draw_leader_line(ax, anchors["stems"][2], (4.32, 7.02), style="dotted", color=pal["stem_cobalt"], lw=1.05, curved=0.06)

    draw_pill_tag(ax, 1.54, 3.96, "Heat Stress Alert", bg=pal["stem_magenta"], fg="#FFFFFF", fontsize=8.8)
    draw_leader_line(ax, anchors["stems"][3], (2.25, 3.86), style="dotted", color=pal["stem_magenta"], lw=1.05)

    # Bottom-Left Hairline Attribute Micro-Table
    ax.text(0.42, 2.52, "Multidimensional Point Attributes", fontsize=9.0, fontweight="bold", color=pal["title"], ha="left", va="bottom", zorder=7)
    draw_micro_table(
        ax,
        x=0.42,
        y=0.48,
        w=3.55,
        h=1.94,
        headers=["Index", "Feature", "Value"],
        rows=[
            ["01", "canopy_portion", "0.36"],
            ["02", "building_volume", "508.4 m3"],
            ["03", "ambient_noise", "68.2 dBA"],
            ["04", "solar_irradiance", "664.5 W/m2"],
        ],
        highlight_row=3,
        highlight_bg="#FFF6D6",
        fontsize=7.8,
    )

    # -----------------------------------------------------------------------
    # Transfer Arrow: Spatial Anchor -> Analytical Method Column
    # -----------------------------------------------------------------------
    draw_stage_arrow(ax, (8.36, 4.75), (8.94, 4.75), color="#4A525E", lw=2.3, head_scale=14)

    # -----------------------------------------------------------------------
    # RIGHT HALF: 3-Step Structured Methodological Pipeline
    # -----------------------------------------------------------------------
    col_x, col_w = 9.04, 6.58

    # Step 1: Multidimensional Urban Features (Circular Discs + Brackets)
    draw_header_panel(
        ax, col_x, 5.74, col_w, 3.04,
        "Step 1: Multidimensional Urban Features",
        header_h=0.36, header_bg=pal["header_band"], body_bg="#FFFFFF", border_color=pal["border"],
    )
    dim_specs = [
        ("Dim 1: 3D Morphology", _make_disc_grid("morph"), "Greys", ["Building height", "Sky view factor"], 8.05),
        ("Dim 2: Socio-Economic", _make_disc_grid("socio"), "Purples", ["POI density", "Transit access"], 7.42),
        ("Dim 3: Visual Perception", _make_disc_grid("perc"), "RdPu", ["Green view index", "Enclosure score"], 6.79),
        ("Dim 4: Microclimate", _make_disc_grid("micro"), "YlGn", ["Solar irradiance", "Acoustic noise"], 6.16),
    ]
    for idx, (d_title, d_arr, d_cmap, d_items, ry) in enumerate(dim_specs):
        draw_icon(ax, "play_tri", col_x + 0.24, ry, size=0.14, color=pal["title"], lw=1.05, zorder=6)
        ax.text(col_x + 0.38, ry, d_title, fontsize=8.8, fontweight="bold", color=pal["title"], ha="left", va="center", zorder=6)
        draw_iso_layer_grid(
            ax, d_arr, cx=col_x + 3.06, cy=ry, size=0.60,
            cmap=d_cmap, border_color="#9CA3AF", border_lw=0.8,
            circular=True, zorder=6.0 + idx * 0.2,
        )
        draw_bracket_list(
            ax, col_x + 3.88, ry - 0.22, 2.52, 0.44,
            items=d_items, color=pal["bracket"], text_color="#2B3139", fontsize=8.0,
        )

    draw_stage_arrow(ax, (col_x + col_w * 0.5, 5.70), (col_x + col_w * 0.5, 5.38), color="#4A525E", lw=2.0, head_scale=13)

    # Step 2: Spatial Graph & Inductive GNN (Dashed Zone)
    draw_dashed_zone(
        ax, col_x, 3.00, col_w, 2.34,
        title="Step 2: Spatial Graph & Inductive GNN (GraphSAGE)",
        fill=pal["dashed_bg"], border_color=pal["dashed_border"], lw=0.95, title_size=10.2,
    )
    draw_gnn_planes(
        ax, cx=col_x + 1.68, cy=3.96, w=2.70, h=1.32,
        n_planes=2, highlight_idx=1, accent=pal["gnn_orange"], secondary=pal["gnn_teal"], zorder_base=5,
    )
    # Compact technical specs beside GNN planes
    spec_x = col_x + 3.45
    specs = [
        ("Nodes:", "Street & neighborhood centroids"),
        ("Edges:", "k-NN spatial connectivity (k = 10)"),
        ("Encoder:", "2-layer GraphSAGE aggregation"),
        ("Validation:", "70% train / 30% spatial hold-out"),
    ]
    for s_i, (sk, sv) in enumerate(specs):
        sy = 4.56 - s_i * 0.36
        ax.text(spec_x, sy, sk, fontsize=8.5, fontweight="bold", color=pal["title"], ha="left", va="center", zorder=6)
        ax.text(spec_x + 0.88, sy, sv, fontsize=8.3, color=pal["subtitle"], ha="left", va="center", zorder=6)

    draw_stage_arrow(ax, (col_x + col_w * 0.5, 2.96), (col_x + col_w * 0.5, 2.64), color="#4A525E", lw=2.0, head_scale=13)

    # Step 3: Explainable AI (SHAP) & Comfort Outcomes
    draw_header_panel(
        ax, col_x, 0.46, col_w, 2.14,
        "Step 3: Explainable AI (SHAP) & Comfort Prediction",
        header_h=0.35, header_bg=pal["header_band"], body_bg="#FFFFFF", border_color=pal["border"],
    )

    # Genuine Matplotlib horizontal SHAP bar chart inset on left side of Step 3
    w_fig, h_fig = 16.0, 10.0
    shap_ax = fig.add_axes(
        [(col_x + 1.06) / w_fig, 0.74 / h_fig, 2.98 / w_fig, 1.32 / h_fig],
        facecolor="#FFFFFF",
    )
    shap_feats = ["Solar Heat", "Noise Level", "Sky View", "Tree Canopy"]
    shap_vals = [-0.37, -0.29, 0.26, 0.44]
    shap_cols = ["#D97757" if v < 0 else "#4A7C9B" for v in shap_vals]
    y_pos = np.arange(len(shap_feats))
    shap_ax.barh(y_pos, shap_vals, height=0.56, color=shap_cols, edgecolor="none", zorder=3)
    shap_ax.axvline(0.0, color="#6C737F", linewidth=0.85, zorder=4)
    shap_ax.set_yticks(y_pos)
    shap_ax.set_yticklabels(shap_feats, fontsize=7.8, color="#22262B")
    shap_ax.set_xlim(-0.52, 0.58)
    shap_ax.tick_params(axis="x", labelsize=7.0, colors="#4A525E", length=2.5)
    shap_ax.tick_params(axis="y", length=0)
    shap_ax.set_xlabel("Mean SHAP Impact", fontsize=7.6, color="#3E454E", labelpad=2)
    for sp in ("top", "right", "left"):
        shap_ax.spines[sp].set_visible(False)
    shap_ax.spines["bottom"].set_color("#9CA3AF")
    shap_ax.spines["bottom"].set_linewidth(0.75)
    for yp, val in zip(y_pos, shap_vals):
        off = 0.025 if val >= 0 else -0.025
        ha = "left" if val >= 0 else "right"
        shap_ax.text(val + off, yp, f"{val:+.2f}", fontsize=7.2, fontweight="bold", color="#22262B", va="center", ha=ha)

    # Vertical hairline separator & Outcome Strip on right of Step 3
    sep_x = col_x + 4.35
    ax.plot([sep_x, sep_x], [0.64, 2.08], color="#D2D6DC", lw=0.9, zorder=5)

    ax.text(sep_x + 0.22, 1.98, "Predicted Comfort Class", fontsize=8.8, fontweight="bold", color=pal["title"], ha="left", va="top", zorder=6)
    outcomes = [
        ("Comfortable", pal["stem_cobalt"], 1.56),
        ("Neutral", "#8E97A4", 1.24),
        ("Uncomfortable", pal["stem_magenta"], 0.92),
    ]
    for lbl, col, oy in outcomes:
        ax.add_patch(Circle((sep_x + 0.34, oy), radius=0.075, facecolor=col, edgecolor="none", zorder=6))
        ax.text(sep_x + 0.52, oy, lbl, fontsize=8.4, color="#2B3139", ha="left", va="center", zorder=6)

    ax.text(sep_x + 0.22, 0.62, "R2 = 0.84  |  RMSE = 0.19", fontsize=8.0, fontweight="bold", color=pal["subtitle"], ha="left", va="bottom", zorder=6)

    save_publication_figure(fig, out_stem, formats=("png", "svg"), dpi=300)


if __name__ == "__main__":
    out = ROOT / "examples" / "output" / "demo_archetype_b_editorial_clay"
    build_demo(out)
    print(f"[OK] Saved {out}.png and {out}.svg")
