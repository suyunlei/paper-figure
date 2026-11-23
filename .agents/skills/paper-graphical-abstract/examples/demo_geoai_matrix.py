"""
demo_geoai_matrix.py — Archetype D Showcase
Multi-Stage Spine / S-Flow Empirical Matrix
(Distilled from Binyu Lei: Building and Environment 2026 Fig. 1, CEUS 2026 Cycling Safety).

Generates high-resolution PNG + editable vector SVG at:
  .agents/skills/paper-graphical-abstract/examples/output/demo_archetype_d_geoai_matrix.{png,svg}
"""

from __future__ import annotations

from pathlib import Path
import sys

from matplotlib.patches import Circle, FancyArrowPatch, Rectangle
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from ual_ga_kit import (
    PALETTES,
    create_canvas,
    draw_flow_triangle,
    draw_gnn_planes,
    draw_header_panel,
    draw_icon,
    draw_pill_tag,
    place_image_box,
    save_publication_figure,
)


def _make_svi_feature_chip(kind: str, nh: int = 80, nw: int = 280) -> np.ndarray:
    """Create crisp panoramic street-view CV thumbnail arrays matched to wide card aspect."""
    yy, xx = np.meshgrid(np.linspace(1.0, 0.0, nh), np.linspace(0.0, 1.0, nw), indexing="ij")
    asp = nw / float(nh)
    road_m = yy < (0.36 - 0.14 * np.abs(xx - 0.5))
    bld_l = (xx < 0.24) & (yy > 0.18) & (yy < 0.88 - 0.35 * xx)
    bld_r = (xx > 0.76) & (yy > 0.18) & (yy < 0.86 - 0.30 * (1.0 - xx))
    # Aspect-corrected circles so tree canopies & hemispherical sky look geometrically round
    tree_m = (
        ((((xx - 0.27) * asp) ** 2 + (yy - 0.54) ** 2) < 0.16)
        | ((((xx - 0.72) * asp) ** 2 + (yy - 0.56) ** 2) < 0.18)
    )

    if kind == "seg":
        img = np.tile(np.array([0.52, 0.74, 0.94]), (nh, nw, 1))
        img[road_m] = np.array([0.46, 0.20, 0.50])
        img[bld_l | bld_r] = np.array([0.44, 0.44, 0.48])
        img[tree_m] = np.array([0.34, 0.66, 0.28])
        car = (xx > 0.45) & (xx < 0.55) & (yy > 0.14) & (yy < 0.30)
        img[car] = np.array([0.12, 0.26, 0.76])
        return img

    if kind == "depth":
        depth = 0.24 + 0.70 * np.exp(-((((xx - 0.50) * 1.4) ** 2) + (yy - 0.48) ** 2) / 0.22)
        depth[bld_l | bld_r] *= 0.42
        depth[tree_m] *= 0.65
        import matplotlib as mpl
        return mpl.colormaps["magma"](np.clip(depth, 0.05, 0.98))[..., :3]

    if kind == "hue":
        import matplotlib as mpl
        val = 0.25 + 0.55 * np.abs(np.sin(xx * 14.0) * np.cos(yy * 7.0))
        val[tree_m] = 0.88
        val[bld_l | bld_r] = 0.42
        return mpl.colormaps["cividis"](np.clip(val, 0.05, 0.95))[..., :3]

    import matplotlib as mpl
    rad = np.sqrt((((xx - 0.50) * asp * 0.45) ** 2) + (yy - 0.50) ** 2)
    irr = np.clip(1.0 - rad * 1.35, 0.06, 0.96)
    irr[(rad > 0.22) & (xx < 0.32)] *= 0.28
    irr[(rad > 0.22) & (xx > 0.68)] *= 0.35
    return mpl.colormaps["inferno"](irr)[..., :3]


def build_demo(out_stem: Path) -> None:
    pal = PALETTES["geoai_matrix"]
    fig, ax = create_canvas(
        figsize=(16.0, 10.0),
        theme="geoai_matrix",
        dpi=300,
        title="Multi-Sensory Exposure & Explainable GeoAI Workflow",
        subtitle="Integrating wearable physiology, street-view computer vision, and counterfactual simulation for restorative urban design",
        title_x=0.38,
        title_y=9.66,
    )

    # -----------------------------------------------------------------------
    # LEFT VERTICAL STAGE SPINE (Icons + Stage Labels + Dash-Dot Links)
    # -----------------------------------------------------------------------
    spine_x = 1.15
    spine_stages = [
        ("watch", "Quasi-Experiment &\nEMA Sensing", 7.86),
        ("camera", "Multi-Modal\nFeature Fusion", 5.66),
        ("graph", "LMM & Explainable\nGeoAI Modeling", 3.32),
        ("layers", "Design Scenario\nOptimization", 1.14),
    ]
    for idx, (ic_kind, s_label, sy) in enumerate(spine_stages):
        draw_icon(ax, ic_kind, spine_x, sy + 0.24, size=0.44, color=pal["title"], lw=1.45, zorder=8)
        ax.text(
            spine_x,
            sy - 0.08,
            s_label,
            fontsize=8.6,
            fontweight="bold",
            fontstyle="italic",
            color=pal["title"],
            ha="center",
            va="top",
            zorder=8,
        )
        if idx < len(spine_stages) - 1:
            next_sy = spine_stages[idx + 1][2]
            ax.add_patch(
                FancyArrowPatch(
                    (spine_x, sy - 0.56),
                    (spine_x, next_sy + 0.58),
                    arrowstyle="-|>",
                    mutation_scale=10,
                    color="#6C737F",
                    linewidth=1.1,
                    linestyle=(0, (3.5, 2.0, 1.0, 2.0)),
                    zorder=6,
                )
            )

    # -----------------------------------------------------------------------
    # RIGHT 4-TIER ANALYTICAL MATRIX
    # -----------------------------------------------------------------------
    mx, mw = 2.12, 13.50

    # --- TIER 1: Data Collection & Walking Protocol ---
    draw_header_panel(
        ax, mx, 6.94, mw, 1.84,
        "1. Multi-Modal Data Collection & Sequential Walking Protocol",
        header_h=0.33, header_bg=pal["header_dark"], body_bg="#FFFFFF",
        border_color=pal["border"], title_color="#FFFFFF", title_size=10.2,
    )
    # Left half: Walking Protocol Sequence
    ax.text(mx + 0.20, 8.28, "Walking Experiment Sequence", fontsize=8.8, fontweight="bold", color=pal["title"], ha="left", va="center", zorder=6)
    seq_steps = [
        ("Fatigue", "#E5E7EB", "#22262B"),
        ("Route 1\n(Urban)", "#D6DFE8", "#181C20"),
        ("Rest\n(5 min)", "#F3F4F6", "#4A525E"),
        ("Route 2\n(Green)", "#DCECE0", "#181C20"),
        ("Route 3\n(Mixed)", "#E8E2F0", "#181C20"),
    ]
    sx0 = mx + 0.20
    box_w, gap_w = 1.12, 0.24
    for i, (lbl, bgc, fgc) in enumerate(seq_steps):
        bx = sx0 + i * (box_w + gap_w)
        ax.add_patch(Rectangle((bx, 7.64), box_w, 0.46, facecolor=bgc, edgecolor="#9CA3AF", lw=0.75, zorder=5))
        ax.text(bx + box_w * 0.5, 7.87, lbl, fontsize=7.6, fontweight="bold", color=fgc, ha="center", va="center", zorder=6)
        if i < len(seq_steps) - 1:
            draw_flow_triangle(ax, bx + box_w + gap_w * 0.5, 7.87, direction="right", size=0.10, color="#6C737F", zorder=6)

    # Sensor chips underneath sequence
    sensors = ["360 Camera", "Sound Meter", "Smartwatch EMA", "Weather Station"]
    for i, sname in enumerate(sensors):
        scx = mx + 0.94 + i * 1.62
        draw_pill_tag(ax, scx, 7.26, sname, bg="#F4F5F7", fg="#2B3139", border="#B8BEC7", fontsize=7.6, pad_x=0.10, pad_y=0.05)

    # Vertical divider in Tier 1
    ax.plot([mx + 6.95, mx + 6.95], [7.06, 8.38], color="#D2D6DC", lw=0.9, zorder=5)

    # Right half: 3 Variable Categories
    var_groups = [
        ("Restoration Outcomes:", "HRV, PANAS, Restorative Outcome Scale (ROS)", 8.16),
        ("Environmental Streams:", "Acoustic dBA, Street-view visual cues, Solar flux", 7.68),
        ("Personal Covariates:", "Baseline stress, noise & thermal sensitivity", 7.20),
    ]
    for vk, vv, vy in var_groups:
        ax.add_patch(Rectangle((mx + 7.16, vy - 0.16), 6.12, 0.34, facecolor="#F4F5F7", edgecolor="#D2D6DC", lw=0.75, zorder=5))
        ax.text(mx + 7.30, vy + 0.01, vk, fontsize=8.2, fontweight="bold", color=pal["title"], ha="left", va="center", zorder=6)
        ax.text(mx + 9.28, vy + 0.01, vv, fontsize=8.0, color=pal["subtitle"], ha="left", va="center", zorder=6)

    draw_flow_triangle(ax, mx + mw * 0.5, 6.74, direction="down", size=0.14, color="#343A40", zorder=7)

    # --- TIER 2: Street-View CV & Environmental Features ---
    draw_header_panel(
        ax, mx, 4.76, mw, 1.80,
        "2. Street-View Computer Vision & Environmental Feature Extraction",
        header_h=0.33, header_bg=pal["header_dark"], body_bg="#FFFFFF",
        border_color=pal["border"], title_color="#FFFFFF", title_size=10.2,
    )
    cv_cards = [
        ("Semantic Segmentation", "seg", "sky, vegetation, building, road", mx + 0.24),
        ("Monocular Scene Depth", "depth", "depth mean, std, enclosure", mx + 3.55),
        ("Low-Level Visual Cues", "hue", "hue, lightness, edge density", mx + 6.86),
        ("Solar Irradiance Field", "solar", "SVF, direct + diffuse solar flux", mx + 10.17),
    ]
    for c_title, c_kind, c_sub, cx0 in cv_cards:
        cw = 3.08
        draw_header_panel(
            ax, cx0, 4.92, cw, 1.24, c_title,
            header_h=0.25, header_bg="#E8EAED", body_bg="#FFFFFF",
            border_color="#C5C9D0", lw=0.8, title_size=8.4, zorder=4,
        )
        chip = _make_svi_feature_chip(c_kind)
        place_image_box(ax, chip, cx0 + 0.14, 5.18, cw - 0.28, 0.68, border_color="#B8BEC7", border_lw=0.6, zorder=5)
        ax.text(cx0 + cw * 0.5, 5.04, c_sub, fontsize=7.6, color=pal["subtitle"], ha="center", va="center", zorder=6)

    draw_flow_triangle(ax, mx + mw * 0.5, 4.56, direction="down", size=0.14, color="#343A40", zorder=7)

    # --- TIER 3: Twin Modeling Panels (3a LMM/EMMs & 3b GNN+SHAP) ---
    w_half = 6.62
    gap_mid = mw - 2 * w_half
    x_3a, x_3b = mx, mx + w_half + gap_mid

    # 3a: Sequential Exposure Effects (Matplotlib Inset Line Plot)
    draw_header_panel(
        ax, x_3a, 2.22, w_half, 2.16,
        "3a. Sequential Exposure Effects (LMM / EMMs)",
        header_h=0.33, header_bg=pal["header_light"], body_bg="#FFFFFF",
        border_color=pal["border"], title_color=pal["title"], title_size=9.8,
    )
    w_fig, h_fig = 16.0, 10.0
    emm_ax = fig.add_axes(
        [(x_3a + 0.72) / w_fig, 2.52 / h_fig, (w_half - 1.10) / w_fig, 1.38 / h_fig],
        facecolor="#FFFFFF",
    )
    rx = np.array([0, 1, 2])
    emm_ax.axhline(0.0, color="#9CA3AF", lw=0.8, ls="--", zorder=1)
    emm_ax.plot(rx, [-2.4, 5.6, 1.4], marker="o", ms=4.5, lw=1.8, color=pal["sage"], label="Restorative (ROS)")
    emm_ax.plot(rx, [-1.1, 2.8, 0.6], marker="s", ms=4.2, lw=1.8, color=pal["steel"], label="Positive Affect")
    emm_ax.plot(rx, [1.5, -1.8, 0.2], marker="^", ms=4.5, lw=1.8, color=pal["coral"], label="HRV Recovery")
    emm_ax.set_xticks(rx)
    emm_ax.set_xticklabels(["Route 1 (Urban)", "Route 2 (Green)", "Route 3 (Mixed)"], fontsize=7.6, color="#22262B")
    emm_ax.set_xlim(-0.26, 2.26)
    emm_ax.set_ylabel("Delta EMMs", fontsize=7.6, color="#3E454E")
    emm_ax.set_ylim(-3.4, 6.8)
    emm_ax.tick_params(axis="y", labelsize=7.0, colors="#4A525E", length=2.5)
    for sp in ("top", "right"):
        emm_ax.spines[sp].set_visible(False)
    emm_ax.spines["left"].set_color("#9CA3AF")
    emm_ax.spines["bottom"].set_color("#9CA3AF")
    emm_ax.legend(frameon=False, fontsize=7.2, loc="upper right", ncol=1)

    # 3b: Spatial Graph & Explainable AI (GNN Planes + Genuine SHAP Bars)
    draw_header_panel(
        ax, x_3b, 2.22, w_half, 2.16,
        "3b. Spatial Graph & Explainable AI (GNN + SHAP)",
        header_h=0.33, header_bg=pal["header_light"], body_bg="#FFFFFF",
        border_color=pal["border"], title_color=pal["title"], title_size=9.8,
    )
    draw_gnn_planes(
        ax, cx=x_3b + 1.48, cy=3.18, w=2.35, h=1.24,
        n_planes=2, highlight_idx=1, accent=pal["coral"], secondary=pal["sage"], zorder_base=5,
    )
    ax.text(x_3b + 1.48, 2.34, "Inductive GraphSAGE", fontsize=8.0, fontweight="bold", color=pal["subtitle"], ha="center", va="bottom", zorder=6)

    ax.plot([x_3b + 2.86, x_3b + 2.86], [2.36, 3.92], color="#D2D6DC", lw=0.9, zorder=5)

    shap_ax = fig.add_axes(
        [(x_3b + 3.85) / w_fig, 2.60 / h_fig, 2.52 / w_fig, 1.32 / h_fig],
        facecolor="#FFFFFF",
    )
    feats = ["Noise", "Microclimate", "Scene Depth", "Low-level", "SVI Seg"]
    vals = [-0.048, -0.027, 0.030, 0.048, 0.533]
    cols = [pal["coral"] if v < 0 else pal["steel"] for v in vals]
    yp = np.arange(len(feats))
    shap_ax.barh(yp, vals, height=0.58, color=cols, edgecolor="none", zorder=3)
    shap_ax.axvline(0.0, color="#6C737F", lw=0.85, zorder=4)
    shap_ax.set_yticks(yp)
    shap_ax.set_yticklabels(feats, fontsize=7.4, color="#22262B")
    shap_ax.set_xlim(-0.18, 0.68)
    shap_ax.tick_params(axis="x", labelsize=6.8, colors="#4A525E", length=2.2)
    shap_ax.tick_params(axis="y", length=0)
    shap_ax.set_xlabel("SHAP Contribution", fontsize=7.4, color="#3E454E", labelpad=2)
    for sp in ("top", "right", "left"):
        shap_ax.spines[sp].set_visible(False)
    shap_ax.spines["bottom"].set_color("#9CA3AF")
    for yy_i, vv in zip(yp, vals):
        off = 0.02 if vv >= 0 else -0.02
        ha_s = "left" if vv >= 0 else "right"
        shap_ax.text(vv + off, yy_i, f"{vv:+.2f}", fontsize=6.9, fontweight="bold", color="#22262B", va="center", ha=ha_s)

    draw_flow_triangle(ax, mx + mw * 0.5, 2.02, direction="down", size=0.14, color="#343A40", zorder=7)

    # --- TIER 4: Counterfactual Urban Design Optimization ---
    draw_header_panel(
        ax, mx, 0.40, mw, 1.44,
        "4. Urban Design Optimization & Counterfactual Scenario Simulation",
        header_h=0.32, header_bg=pal["header_light"], body_bg="#FFFFFF",
        border_color=pal["border"], title_color=pal["title"], title_size=9.8,
    )
    # Left optimization logic card
    ax.add_patch(Rectangle((mx + 0.22, 0.54), 2.94, 0.84, facecolor="#F4F5F7", edgecolor="#C5C9D0", lw=0.8, zorder=5))
    ax.text(mx + 0.34, 1.18, "1. Target top SHAP drivers", fontsize=8.1, fontweight="bold", color=pal["title"], ha="left", va="center", zorder=6)
    ax.text(mx + 0.34, 0.80, "2. Predict counterfactual Delta ROS", fontsize=8.0, color=pal["subtitle"], ha="left", va="center", zorder=6)

    scenarios = [
        ("Sound (S)", "sound", "-14 dBA road noise", "+9.4% Delta ROS", pal["steel"], mx + 3.44),
        ("Visual (V)", "leaf", "+22% street canopy", "+14.8% Delta ROS", pal["sage"], mx + 6.90),
        ("Visual + Sound (V+S)", "target", "Combined intervention", "+21.6% Delta ROS", pal["coral"], mx + 10.36),
    ]
    for idx, (sc_title, sc_icon, sc_desc, sc_pill, sc_col, sx) in enumerate(scenarios):
        sw = 3.04
        ax.text(sx + 0.12, 1.30, sc_title, fontsize=8.8, fontweight="bold", color=pal["title"], ha="left", va="center", zorder=6)
        draw_icon(ax, sc_icon, sx + sw - 0.28, 1.30, size=0.28, color=sc_col, lw=1.45, zorder=6)
        ax.text(sx + 0.12, 1.00, sc_desc, fontsize=7.9, color=pal["subtitle"], ha="left", va="center", zorder=6)
        draw_pill_tag(ax, sx + 1.02, 0.66, sc_pill, bg=sc_col, fg="#FFFFFF", fontsize=7.9, pad_x=0.14, pad_y=0.05)
        if idx < len(scenarios) - 1:
            div_x = sx + sw + 0.21
            ax.plot([div_x, div_x], [0.54, 1.38], color="#D2D6DC", lw=0.85, zorder=5)
            draw_flow_triangle(ax, div_x, 0.96, direction="right", size=0.11, color="#555C68", zorder=7)

    save_publication_figure(fig, out_stem, formats=("png", "svg"), dpi=300)


if __name__ == "__main__":
    out = ROOT / "examples" / "output" / "demo_archetype_d_geoai_matrix"
    build_demo(out)
    print(f"[OK] Saved {out}.png and {out}.svg")
