"""
audit_figure.py — Automated Quantitative QA Validator for Paper Graphical Abstracts.

Checks PNG resolution, aspect ratio, outer-edge clipping, neutral-ground balance,
color-saturation restraint (90/10 UAL rule), and optional SVG / PDF vector text.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image


def _rgb_to_hsv_saturation_value(rgb_norm: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    c_max = rgb_norm.max(axis=-1)
    c_min = rgb_norm.min(axis=-1)
    delta = c_max - c_min
    sat = np.zeros_like(c_max)
    nonzero = c_max > 1e-6
    sat[nonzero] = delta[nonzero] / c_max[nonzero]
    return sat, c_max


def audit_png(png_path: Path, theme: str = "editorial_white") -> tuple[dict, list[str]]:
    findings: list[str] = []
    with Image.open(png_path) as im:
        rgb = np.asarray(im.convert("RGB"), dtype=np.uint8)

    h_px, w_px, _ = rgb.shape
    aspect = round(w_px / max(1, h_px), 3)

    # Infer background RGB from outer 4 corner 10x10 patches
    corners = np.concatenate(
        [
            rgb[:10, :10].reshape(-1, 3),
            rgb[:10, -10:].reshape(-1, 3),
            rgb[-10:, :10].reshape(-1, 3),
            rgb[-10:, -10:].reshape(-1, 3),
        ],
        axis=0,
    )
    bg_rgb = np.median(corners, axis=0)

    # 1. Resolution check
    if w_px < 1328 or h_px < 531:
        findings.append(f"[WARN] Low pixel resolution {w_px}x{h_px} (Elsevier min 1328x531).")
    else:
        findings.append(f"[OK] Resolution {w_px}x{h_px} px (aspect {aspect}:1, print {w_px/300:.2f}x{h_px/300:.2f} in @300 DPI).")

    # Expected theme background check
    if theme in ("studio_grey", "editorial_studio"):
        expected = np.array([217, 219, 222])
        if np.linalg.norm(bg_rgb - expected) > 18:
            findings.append(f"[WARN] {theme} expected ~#D9DBDE, measured corner RGB={bg_rgb.astype(int).tolist()}.")
    elif theme in ("editorial_white", "interplay_twin", "geoai_matrix"):
        expected = np.array([255, 255, 255])
        if np.linalg.norm(bg_rgb - expected) > 18:
            findings.append(f"[WARN] {theme} expected ~#FFFFFF, measured corner RGB={bg_rgb.astype(int).tolist()}.")

    # 2. Edge clipping margin check (outer 1.2% margin on each edge)
    mx = max(2, int(round(w_px * 0.012)))
    my = max(2, int(round(h_px * 0.012)))
    diff_all = np.linalg.norm(rgb.astype(float) - bg_rgb.astype(float), axis=-1)
    edge_masks = {
        "top": diff_all[:my, :] > 18.0,
        "bottom": diff_all[-my:, :] > 18.0,
        "left": diff_all[:, :mx] > 18.0,
        "right": diff_all[:, -mx:] > 18.0,
    }
    clipped_edges = [name for name, m in edge_masks.items() if float(m.mean()) > 0.02]
    if clipped_edges:
        findings.append(f"[FAIL] Content enters outer 1.2% safety margin on edge(s): {', '.join(clipped_edges)}.")
    else:
        findings.append("[OK] Clean outer 1.2% margin clearance on all four edges.")

    # 3. Neutral ground / whitespace balance
    bg_fraction = float((diff_all <= 14.0).mean())
    max_bg = 0.84 if theme in ("editorial_studio", "studio_grey") else 0.78
    if bg_fraction < 0.22:
        findings.append(f"[WARN] Overcrowded layout: neutral background only {bg_fraction*100:.1f}% (<22%).")
    elif bg_fraction > max_bg:
        findings.append(f"[WARN] Sparse layout: neutral background {bg_fraction*100:.1f}% (>{int(max_bg*100)}%).")
    else:
        findings.append(f"[OK] Balanced neutral background share: {bg_fraction*100:.1f}%.")

    # 4. Color restraint (high-saturation fraction)
    sat, val = _rgb_to_hsv_saturation_value(rgb.astype(float) / 255.0)
    vivid_fraction = float(((sat > 0.65) & (val > 0.25)).mean())
    if vivid_fraction > 0.28:
        findings.append(f"[WARN] High-saturation pixel share is {vivid_fraction*100:.1f}% (>28%), risking visual noise.")
    else:
        findings.append(f"[OK] Controlled vivid-signal share: {vivid_fraction*100:.1f}% (within UAL 90/10 restraint).")

    metrics = {
        "width_px": int(w_px),
        "height_px": int(h_px),
        "aspect_ratio": aspect,
        "corner_bg_rgb": [int(v) for v in bg_rgb],
        "neutral_bg_fraction": round(bg_fraction, 4),
        "vivid_signal_fraction": round(vivid_fraction, 4),
        "clipped_edges": clipped_edges,
    }
    return metrics, findings


def audit_svg(svg_path: Path) -> tuple[dict, list[str]]:
    findings: list[str] = []
    if not svg_path.exists():
        return {"svg_exists": False}, [f"[FAIL] Missing SVG file: {svg_path}"]

    try:
        tree = ET.parse(svg_path)
    except ET.ParseError as exc:
        return {"svg_exists": True, "valid_xml": False}, [f"[FAIL] Invalid SVG XML ({exc}): {svg_path}"]

    root = tree.getroot()
    text_elems = [
        elem for elem in root.iter()
        if elem.tag.endswith("}text") or elem.tag == "text"
    ]
    extracted_chars = sum(
        len("".join(elem.itertext()).strip())
        for elem in text_elems
    )
    view_box = root.attrib.get("viewBox", "")
    width_attr = root.attrib.get("width", "")
    height_attr = root.attrib.get("height", "")
    size_kb = round(svg_path.stat().st_size / 1024.0, 1)

    if extracted_chars < 15:
        findings.append("[FAIL] SVG contains little or no editable <text> content (check svg.fonttype='none').")
    else:
        findings.append(
            f"[OK] SVG valid XML ({size_kb} KB, {len(text_elems)} <text> nodes, "
            f"{extracted_chars} editable chars, viewBox='{view_box}')."
        )

    return {
        "svg_exists": True,
        "valid_xml": True,
        "size_kb": size_kb,
        "text_nodes": len(text_elems),
        "editable_text_chars": extracted_chars,
        "viewBox": view_box,
        "width": width_attr,
        "height": height_attr,
    }, findings


def audit_pdf(pdf_path: Path) -> tuple[dict, list[str]]:
    findings: list[str] = []
    if not pdf_path.exists():
        return {"pdf_exists": False}, [f"[FAIL] Missing PDF file: {pdf_path}"]
    try:
        import pymupdf
    except ImportError:
        try:
            import fitz as pymupdf  # type: ignore
        except ImportError:
            return {"pdf_exists": True, "checked": False}, ["[WARN] pymupdf unavailable; skipped PDF vector inspection."]

    doc = pymupdf.open(pdf_path)
    if len(doc) == 0:
        return {"pdf_exists": True, "pages": 0}, ["[FAIL] Empty PDF document."]

    page = doc[0]
    txt = page.get_text("text").strip()
    fonts = sorted({f[3] for f in page.get_fonts() if len(f) > 3})
    if len(txt) < 15:
        findings.append("[FAIL] PDF page 1 has little or no selectable vector text (check pdf.fonttype=42).")
    else:
        findings.append(f"[OK] PDF vector text verified ({len(txt)} chars, fonts: {', '.join(fonts) or 'embedded'}).")

    return {
        "pdf_exists": True,
        "pages": len(doc),
        "selectable_text_chars": len(txt),
        "fonts": fonts,
    }, findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit rendered Graphical Abstract PNG, SVG, and PDF.")
    parser.add_argument("png", type=Path, help="Path to rendered PNG figure.")
    parser.add_argument("--svg", type=Path, default=None, help="Optional path to editable SVG figure.")
    parser.add_argument("--pdf", type=Path, default=None, help="Optional path to vector PDF figure.")
    parser.add_argument(
        "--theme",
        choices=["editorial_studio", "studio_grey", "editorial_white", "interplay_twin", "geoai_matrix"],
        default="editorial_white",
        help="Expected archetype/preset theme.",
    )
    args = parser.parse_args()

    if not args.png.exists():
        print(f"[FAIL] PNG not found: {args.png}")
        return 1

    metrics, findings = audit_png(args.png, theme=args.theme)
    if args.svg is not None:
        svg_metrics, svg_findings = audit_svg(args.svg)
        metrics["svg"] = svg_metrics
        findings.extend(svg_findings)
    if args.pdf is not None:
        pdf_metrics, pdf_findings = audit_pdf(args.pdf)
        metrics["pdf"] = pdf_metrics
        findings.extend(pdf_findings)

    for line in findings:
        print(line)
    print("SUMMARY:", json.dumps(metrics))

    has_fail = any(line.startswith("[FAIL]") for line in findings)
    return 1 if has_fail else 0


if __name__ == "__main__":
    sys.exit(main())
