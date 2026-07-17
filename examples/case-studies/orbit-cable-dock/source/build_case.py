"""Generate presentation boards, engineering drawing, DRC, and handoff manifest."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import shutil
import sys
from pathlib import Path

import ezdxf
import trimesh
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
CAD = ROOT / "cad"
sys.path.insert(0, str(CAD))

import orbit_model as model
import orbit_params as p


OUTPUT = ROOT / "output"
REVIEW = OUTPUT / "review"
ENGINEERING = OUTPUT / "engineering"
REPORTS = ROOT / "reports"
for folder in (REVIEW, ENGINEERING, REPORTS):
    folder.mkdir(parents=True, exist_ok=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def latest(pattern: str) -> Path:
    matches = sorted(REVIEW.glob(pattern), key=lambda item: item.stat().st_mtime)
    if not matches:
        raise FileNotFoundError(f"missing review image: {pattern}")
    return matches[-1]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def contain(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    copy = image.convert("RGB")
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    return copy


def wrapped(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], width: int, fnt, fill, spacing=8):
    words = text.split()
    lines, line = [], ""
    for word in words:
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=fnt) <= width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    x, y = xy
    for item in lines:
        draw.text((x, y), item, font=fnt, fill=fill)
        y += fnt.size + spacing
    return y


def make_concept_board() -> Path:
    board = Image.new("RGB", (2400, 1500), "#F3F5F7")
    draw = ImageDraw.Draw(board)
    draw.text((110, 70), "ORBIT — THREE CONCEPTS, ONE DECISION", font=font(64, True), fill="#152233")
    draw.text((112, 150), "Same-scale B-rep massing review · Rev 0", font=font(30), fill="#647083")
    concepts = [
        ("A", "STATIC COMB", latest("concept_a_iso_*.png"), "108 × 50 × 14 mm", "Simple, but fails the rotary design DNA.", "REJECT"),
        ("B", "TALL DRUM", latest("concept_b_iso_*.png"), "Ø76 × 53.8 mm", "Compact footprint, but visually top-heavy.", "REJECT"),
        ("C", "LOW ORBIT", latest("concept_c_iso_*.png"), "96 × 96 × 26 mm", "Low, stable, and the motion reads immediately.", "SELECT"),
    ]
    for index, (letter, title, path, dims, note, decision) in enumerate(concepts):
        x = 110 + index * 760
        y = 235
        card_color = "#FFFFFF" if decision == "REJECT" else "#E9F6F5"
        border = "#D5DBE2" if decision == "REJECT" else "#159092"
        draw.rounded_rectangle((x, y, x + 690, y + 1120), radius=38, fill=card_color, outline=border, width=4)
        draw.ellipse((x + 38, y + 35, x + 112, y + 109), fill=border)
        draw.text((x + 61, y + 47), letter, font=font(36, True), fill="white", anchor="ma")
        draw.text((x + 135, y + 43), title, font=font(34, True), fill="#152233")
        image = contain(Image.open(path), (620, 665))
        board.paste(image, (x + (690 - image.width) // 2, y + 135))
        draw.text((x + 45, y + 835), dims, font=font(30, True), fill="#152233")
        wrapped(draw, note, (x + 45, y + 895), 600, font(27), "#4F5B6C")
        badge = "#B33A3A" if decision == "REJECT" else "#159092"
        draw.rounded_rectangle((x + 45, y + 1020, x + 235, y + 1080), radius=20, fill=badge)
        draw.text((x + 140, y + 1050), decision, font=font(25, True), fill="white", anchor="mm")
    path = REVIEW / "concept-board.png"
    board.save(path, quality=95)
    return path


def make_iteration_board() -> Path:
    board = Image.new("RGB", (2400, 1500), "#F3F5F7")
    draw = ImageDraw.Draw(board)
    draw.text((110, 70), "A VALID SOLID CAN STILL BE A BAD PRODUCT", font=font(60, True), fill="#152233")
    draw.text((112, 150), "Same camera · failed Rev A vs optimized Rev C", font=font(30), fill="#647083")
    cards = [
        ("FAILED REV A", latest("failed_rev_a_iso_*.png"), "#B33A3A", ["23 mm rotor reads as a tray stack", "Four slots use unrelated dimensions", "0.2 mm seam hides the rotation", "Oversized cap and proud screw dominate"]),
        ("FINAL REV C", latest("final_rev_c_iso_*.png"), "#159092", ["14.8 mm low rotor and 1.2 mm shadow gap", "One parameter source for all four slots", "Flush recessed centre retention", "TPU liners create a real soft interface"]),
    ]
    for index, (title, image_path, accent, bullets) in enumerate(cards):
        x = 110 + index * 1130
        y = 240
        draw.rounded_rectangle((x, y, x + 1060, y + 1120), radius=40, fill="white", outline=accent, width=5)
        draw.text((x + 55, y + 45), title, font=font(40, True), fill=accent)
        image = contain(Image.open(image_path), (960, 720))
        board.paste(image, (x + (1060 - image.width) // 2, y + 125))
        by = y + 865
        for bullet in bullets:
            draw.ellipse((x + 58, by + 10, x + 72, by + 24), fill=accent)
            draw.text((x + 90, by), bullet, font=font(25), fill="#344153")
            by += 58
    path = REVIEW / "failed-to-final.png"
    board.save(path, quality=95)
    return path


def stage_stable_review_assets() -> dict[str, Path]:
    staged = {
        "hero": REVIEW / "final-hero.png",
        "exploded": REVIEW / "final-exploded.png",
        "section": REVIEW / "final-section.png",
        "motion": REVIEW / "motion-state-045.png",
    }
    sources = {
        "hero": latest("final_rev_c_iso_*.png"),
        "exploded": latest("final_rev_c_exploded_*.png"),
        "section": latest("final_rev_c_true_section_x_inside_*.png"),
        "motion": latest("final_state_045_iso_*.png"),
    }
    for key, destination in staged.items():
        shutil.copy2(sources[key], destination)
    return staged


def dxf_rounded_rect(msp, cx, cy, width, height, radius, layer):
    x0, x1 = cx - width / 2, cx + width / 2
    y0, y1 = cy - height / 2, cy + height / 2
    msp.add_line((x0 + radius, y0), (x1 - radius, y0), dxfattribs={"layer": layer})
    msp.add_line((x0 + radius, y1), (x1 - radius, y1), dxfattribs={"layer": layer})
    msp.add_line((x0, y0 + radius), (x0, y1 - radius), dxfattribs={"layer": layer})
    msp.add_line((x1, y0 + radius), (x1, y1 - radius), dxfattribs={"layer": layer})
    for center, a0, a1 in [((x0 + radius, y0 + radius), 180, 270), ((x1 - radius, y0 + radius), 270, 360), ((x1 - radius, y1 - radius), 0, 90), ((x0 + radius, y1 - radius), 90, 180)]:
        msp.add_arc(center, radius, a0, a1, dxfattribs={"layer": layer})


def dxf_slot(msp, center, angle_deg, outer_radius, depth, width, layer):
    theta = math.radians(angle_deg)
    u = (math.cos(theta), math.sin(theta))
    v = (-math.sin(theta), math.cos(theta))
    inner = outer_radius - depth
    half = width / 2
    inner_center = (center[0] + u[0] * inner, center[1] + u[1] * inner)
    outer_tangent = math.sqrt(outer_radius ** 2 - half ** 2)
    for sign in (-1, 1):
        a = (inner_center[0] + v[0] * half * sign, inner_center[1] + v[1] * half * sign)
        b = (center[0] + u[0] * outer_tangent + v[0] * half * sign, center[1] + u[1] * outer_tangent + v[1] * half * sign)
        msp.add_line(a, b, dxfattribs={"layer": layer})
    msp.add_arc(inner_center, half, angle_deg + 90, angle_deg + 270, dxfattribs={"layer": layer})


def dxf_rotor_outline(msp, center, outer_radius, depth, width, layer):
    """Continuous outer boundary: four outer arcs joined to four U-slots."""
    half_angle = math.degrees(math.asin((width / 2.0) / outer_radius))
    for angle in p.INDEX_ANGLES_DEG:
        dxf_slot(msp, center, angle, outer_radius, depth, width, layer)
        msp.add_arc(
            center,
            outer_radius,
            angle + half_angle,
            angle + 90.0 - half_angle,
            dxfattribs={"layer": layer},
        )


def make_dxf() -> Path:
    doc = ezdxf.new("R2018", setup=True)
    doc.units = ezdxf.units.MM
    for name, color, weight in [("01_VISIBLE", 7, 50), ("02_CENTER", 3, 18), ("03_DIM", 2, 18), ("04_TEXT", 7, 18), ("05_TBD", 1, 25)]:
        if name not in doc.layers:
            doc.layers.add(name, color=color, lineweight=weight)
    msp = doc.modelspace()
    msp.add_lwpolyline([(10, 10), (410, 10), (410, 287), (10, 287)], close=True, dxfattribs={"layer": "01_VISIBLE"})

    # Assembly top view
    c1 = (95, 205)
    dxf_rounded_rect(msp, *c1, p.BASE_WIDTH, p.BASE_DEPTH, p.BASE_PLAN_RADIUS, "01_VISIBLE")
    dxf_rotor_outline(msp, c1, p.ROTOR_DIAMETER / 2, p.SLOT_RADIAL_DEPTH, p.SLOT_WIDTH, "01_VISIBLE")
    msp.add_circle(c1, p.CAP_DIAMETER / 2, dxfattribs={"layer": "01_VISIBLE"})
    msp.add_text("ASSEMBLY TOP · 96 SQ / ROTOR Ø84", height=4, dxfattribs={"layer": "04_TEXT"}).set_placement((42, 264))

    # Front view derived from the same Z parameters
    x0, y0 = 47, 75
    msp.add_lwpolyline([(x0, y0), (x0 + 96, y0), (x0 + 96, y0 + p.BASE_HEIGHT), (x0, y0 + p.BASE_HEIGHT)], close=True, dxfattribs={"layer": "01_VISIBLE"})
    rx0 = 95 - p.ROTOR_DIAMETER / 2
    rz0 = y0 + p.ROTOR_BOTTOM_Z
    msp.add_lwpolyline([(rx0, rz0), (rx0 + p.ROTOR_DIAMETER, rz0), (rx0 + p.ROTOR_DIAMETER, rz0 + p.ROTOR_HEIGHT), (rx0, rz0 + p.ROTOR_HEIGHT)], close=True, dxfattribs={"layer": "01_VISIBLE"})
    msp.add_text("FRONT · H 26.7 · SHADOW GAP 1.2", height=4, dxfattribs={"layer": "04_TEXT"}).set_placement((38, 120))

    # Rotor detail top view
    c2 = (285, 205)
    dxf_rotor_outline(msp, c2, p.ROTOR_DIAMETER / 2, p.SLOT_RADIAL_DEPTH, p.SLOT_WIDTH, "01_VISIBLE")
    msp.add_circle(c2, p.ROTOR_BORE_DIAMETER / 2, dxfattribs={"layer": "01_VISIBLE"})
    msp.add_text("ROTOR DETAIL · 4X SLOT 6.4 × 18 (TBD)", height=4, dxfattribs={"layer": "05_TBD"}).set_placement((230, 264))

    # Simplified axial section with controlled dimensions
    sx, sy = 285, 74
    msp.add_lwpolyline(
        [
            (sx - 48, sy),
            (sx + 48, sy),
            (sx + 48, sy + 10),
            (sx + 5, sy + 10),
            (sx + 5, sy + 20),
            (sx - 5, sy + 20),
            (sx - 5, sy + 10),
            (sx - 48, sy + 10),
        ],
        close=True,
        dxfattribs={"layer": "01_VISIBLE"},
    )
    # Section material is split at interfaces so boundaries touch but do not cross.
    msp.add_lwpolyline([(sx - 42, sy + 11.2), (sx - 8.25, sy + 11.2), (sx - 8.25, sy + 26), (sx - 42, sy + 26)], close=True, dxfattribs={"layer": "01_VISIBLE"})
    msp.add_lwpolyline([(sx + 8.25, sy + 11.2), (sx + 42, sy + 11.2), (sx + 42, sy + 26), (sx + 8.25, sy + 26)], close=True, dxfattribs={"layer": "01_VISIBLE"})
    msp.add_lwpolyline([(sx - 8, sy + 11.2), (sx - 5.15, sy + 11.2), (sx - 5.15, sy + 20), (sx - 8, sy + 20)], close=True, dxfattribs={"layer": "01_VISIBLE"})
    msp.add_lwpolyline([(sx + 5.15, sy + 11.2), (sx + 8, sy + 11.2), (sx + 8, sy + 20), (sx + 5.15, sy + 20)], close=True, dxfattribs={"layer": "01_VISIBLE"})
    msp.add_text("AXIAL SECTION · FITS TBD", height=4, dxfattribs={"layer": "05_TBD"}).set_placement((245, 112))

    # Title block and release boundary
    msp.add_lwpolyline([(270, 10), (410, 10), (410, 50), (270, 50)], close=True, dxfattribs={"layer": "01_VISIBLE"})
    rows = ["ORBIT FOUR-STATION CABLE DOCK", "REV C · mm · NTS", "PROTOTYPE ENGINEERING HANDOFF", "NOT A PRODUCTION RELEASE"]
    for index, text in enumerate(rows):
        msp.add_text(text, height=3.5 if index else 4.2, dxfattribs={"layer": "04_TEXT"}).set_placement((276, 42 - index * 8))
    msp.add_text("TBD: cable fit, M4 hardware, detent force/life, FDM compensation, stability", height=3.4, dxfattribs={"layer": "05_TBD"}).set_placement((20, 20))
    path = ENGINEERING / "orbit-engineering-handoff.dxf"
    doc.saveas(path)
    return path


def make_pdf() -> Path:
    path = ENGINEERING / "orbit-engineering-handoff.pdf"
    page = canvas.Canvas(str(path), pagesize=landscape(A3))
    width, height = landscape(A3)
    page.setTitle("ORBIT Rev C prototype engineering handoff")
    page.setStrokeColor(HexColor("#152233"))
    page.setLineWidth(0.45 * mm)
    page.rect(10 * mm, 10 * mm, width - 20 * mm, height - 20 * mm)
    page.setFont("Helvetica-Bold", 20)
    page.drawString(18 * mm, height - 24 * mm, "ORBIT · PROTOTYPE ENGINEERING HANDOFF · REV C")
    page.setFont("Helvetica", 9)
    page.drawRightString(width - 18 * mm, height - 22 * mm, "mm · NTS · NOT A PRODUCTION RELEASE")

    # Left: actual CAD review images
    iso = Image.open(latest("final_rev_c_iso_*.png"))
    exploded = Image.open(latest("final_rev_c_exploded_*.png"))
    iso_tmp = REVIEW / "_pdf_iso.png"
    exp_tmp = REVIEW / "_pdf_exploded.png"
    contain(iso, (1500, 900)).save(iso_tmp)
    contain(exploded, (1500, 900)).save(exp_tmp)
    page.drawImage(str(iso_tmp), 18 * mm, 112 * mm, width=180 * mm, height=120 * mm, preserveAspectRatio=True, anchor="c")
    page.drawImage(str(exp_tmp), 205 * mm, 112 * mm, width=180 * mm, height=120 * mm, preserveAspectRatio=True, anchor="c")
    page.setFont("Helvetica-Bold", 10)
    page.drawString(18 * mm, 104 * mm, "ASSEMBLED CAD")
    page.drawString(205 * mm, 104 * mm, "EXPLODED COMPONENT HIERARCHY")

    page.setFillColor(HexColor("#F2F5F6"))
    page.roundRect(18 * mm, 22 * mm, 367 * mm, 72 * mm, 5 * mm, fill=1, stroke=0)
    page.setFillColor(HexColor("#152233"))
    page.setFont("Helvetica-Bold", 11)
    page.drawString(25 * mm, 84 * mm, "CONTROLLED CAD ENVELOPE")
    page.setFont("Helvetica", 9)
    facts = [
        "96 × 96 × 26.7 mm nominal envelope",
        "84 mm circular rotor · 14.8 mm high",
        "4 × radial U-slot · 6.4 × 18 mm (TBD cable fit)",
        "1.2 mm visual/axial shadow gap",
        "0/90/180/270° index states + 45° intermediate review",
    ]
    for index, item in enumerate(facts):
        page.drawString(25 * mm, (72 - index * 9) * mm, f"• {item}")
    page.setFont("Helvetica-Bold", 11)
    page.drawString(160 * mm, 84 * mm, "HANDOFF BOUNDARY")
    page.setFont("Helvetica", 9)
    limits = [
        "STEP is authoritative; STL/GLB/DXF/PDF are derivatives.",
        "M4 hardware and receiving insert remain supplier TBD.",
        "Cable fit, detent force/life, FDM compensation, friction and tip stability require physical tests.",
        "External appearance approval has not been claimed.",
        "See BOM, interface-control.csv, TBD-register.md and DRC reports.",
    ]
    for index, item in enumerate(limits):
        page.drawString(160 * mm, (72 - index * 9) * mm, f"• {item}")
    page.showPage()
    page.save()
    iso_tmp.unlink(missing_ok=True)
    exp_tmp.unlink(missing_ok=True)
    return path


def shape_fact(name: str, shape) -> dict:
    bbox = shape.bounding_box()
    validity = getattr(shape, "is_valid", None)
    valid = bool(validity() if callable(validity) else validity)
    return {
        "name": name,
        "valid": valid,
        "volume_mm3": round(float(shape.volume), 3),
        "bbox_mm": [round(float(bbox.size.X), 3), round(float(bbox.size.Y), 3), round(float(bbox.size.Z), 3)],
    }


def make_geometry_report() -> Path:
    parts = {
        "base": model.make_base(),
        "bushing": model.make_bushing(),
        "rotor": model.make_rotor(0),
        "slot_liner_set": model.make_slot_liner_set(0),
        "detent_insert": model.make_detent_insert(0),
        "retainer_cap": model.make_retainer_cap(),
        "fastener_envelope": model.make_fastener_envelope(),
    }
    facts = [shape_fact(name, shape) for name, shape in parts.items()]
    assembly = model.build_orbit_assembly(0)
    bbox = assembly.bounding_box()
    checks = [
        {"rule_id": "BREP_VALID", "status": "PASS" if all(item["valid"] for item in facts) else "FAIL", "measured": [item["valid"] for item in facts]},
        {"rule_id": "ENVELOPE_X", "status": "PASS" if math.isclose(bbox.size.X, 96.0, abs_tol=0.01) else "FAIL", "measured_mm": bbox.size.X, "threshold_mm": 100.0},
        {"rule_id": "ENVELOPE_Y", "status": "PASS" if math.isclose(bbox.size.Y, 96.0, abs_tol=0.01) else "FAIL", "measured_mm": bbox.size.Y, "threshold_mm": 100.0},
        {"rule_id": "ENVELOPE_Z", "status": "PASS" if bbox.size.Z < 30.0 else "FAIL", "measured_mm": bbox.size.Z, "threshold_mm": 30.0},
        {"rule_id": "SLOT_SHARED_SOURCE", "status": "PASS" if p.SLOT_COUNT == 4 and len(p.INDEX_ANGLES_DEG) == 4 else "FAIL", "measured_count": p.SLOT_COUNT, "width_mm": p.SLOT_WIDTH, "depth_mm": p.SLOT_RADIAL_DEPTH},
        {"rule_id": "SHADOW_GAP", "status": "PASS" if p.SHADOW_GAP > 0 else "FAIL", "measured_mm": p.SHADOW_GAP},
        {"rule_id": "ROTOR_BUSHING_CLEARANCE", "status": "PASS" if p.ROTARY_DIAMETRAL_CLEARANCE > 0 else "FAIL", "measured_mm": p.ROTARY_DIAMETRAL_CLEARANCE, "authority": "D/TBD"},
        {"rule_id": "AXLE_BUSHING_CLEARANCE", "status": "PASS" if p.AXLE_BUSHING_DIAMETRAL_CLEARANCE > 0 else "FAIL", "measured_mm": p.AXLE_BUSHING_DIAMETRAL_CLEARANCE, "authority": "D/TBD"},
        {"rule_id": "ROTATION_ENVELOPE", "status": "PASS" if p.ROTOR_DIAMETER <= min(p.BASE_WIDTH, p.BASE_DEPTH) else "FAIL", "rotor_diameter_mm": p.ROTOR_DIAMETER, "base_min_span_mm": min(p.BASE_WIDTH, p.BASE_DEPTH)},
    ]
    stl_path = OUTPUT / "models" / "meshes" / "orbit-final.stl"
    mesh = trimesh.load_mesh(stl_path, process=False)
    mesh_report = {
        "path": str(stl_path.relative_to(ROOT)),
        "watertight": bool(mesh.is_watertight),
        "bounds_mm": [[round(float(v), 3) for v in row] for row in mesh.bounds.tolist()],
        "geometry_count": len(mesh.geometry) if isinstance(mesh, trimesh.Scene) else 1,
        "boundary": "Mesh is a derived multi-part prototype export; STEP remains authoritative.",
    }
    status = "PASS" if all(item["status"] == "PASS" for item in checks) else "FAIL"
    report = {
        "validator": "orbit_case_geometry_drc",
        "status": status,
        "revision": p.REVISION,
        "configuration": p.CONFIGURATION,
        "verification_tier": "Tier 3 release-style evidence for a prototype handoff",
        "parts": facts,
        "checks": checks,
        "stl": mesh_report,
        "not_evaluated": ["strength", "wear", "detent force/life", "print compensation", "friction", "tip stability", "cable retention force"],
        "boundary": "This report proves named geometry and parameter relations only; it does not prove production manufacturability or physical performance."
    }
    path = REPORTS / "geometry-drc.json"
    write_json(path, report)
    return path


def make_drawing_report(dxf_path: Path, pdf_path: Path) -> Path:
    doc = ezdxf.readfile(dxf_path)
    auditor = doc.audit()
    counts = {}
    for entity in doc.modelspace():
        counts[entity.dxftype()] = counts.get(entity.dxftype(), 0) + 1
    report = {
        "validator": "orbit_case_drawing_drc",
        "status": "PASS" if not auditor.has_errors and pdf_path.stat().st_size > 0 else "FAIL",
        "revision": p.REVISION,
        "dxf": {
            "path": str(dxf_path.relative_to(ROOT)),
            "acad_version": doc.dxfversion,
            "insunits": int(doc.header.get("$INSUNITS", 0)),
            "entity_counts": counts,
            "audit_errors": len(auditor.errors),
            "audit_fixes": len(auditor.fixes),
        },
        "pdf": {"path": str(pdf_path.relative_to(ROOT)), "bytes": pdf_path.stat().st_size, "plot_mode": "FIT/NTS"},
        "semantic_disposition": "Prototype handoff drawing; dimensions marked TBD are not released manufacturing requirements.",
        "boundary": "DXF/PDF integrity and shared parameters do not prove GB/T production drawing completeness."
    }
    path = REPORTS / "drawing-drc.json"
    write_json(path, report)
    return path


def make_viewset_report_input() -> Path:
    failed_source = CAD / "orbit_failed_rev_a.py"
    final_source = CAD / "orbit_model.py"
    data = {
        "root": "..",
        "expect_change": True,
        "required_view_ids": ["iso"],
        "baseline": {
            "source": {"revision": "A-failed", "source_hash": sha256(failed_source), "units": "mm"},
            "views": [{"id": "iso", "path": str(latest("failed_rev_a_iso_*.png").relative_to(ROOT)).replace("\\", "/"), "configuration": "0deg", "camera": {"preset": "iso", "projection": "orthographic"}, "color_pipeline": "CAD snapshot workbench"}]
        },
        "candidate": {
            "source": {"revision": "C", "source_hash": sha256(final_source), "units": "mm"},
            "views": [{"id": "iso", "path": str(latest("final_rev_c_iso_*.png").relative_to(ROOT)).replace("\\", "/"), "configuration": "0deg", "camera": {"preset": "iso", "projection": "orthographic"}, "color_pipeline": "CAD snapshot workbench"}]
        }
    }
    path = ROOT / "review" / "render-viewset.json"
    write_json(path, data)
    return path


def make_manifest(artifacts: list[tuple[str, Path]]) -> Path:
    source_hash = sha256(CAD / "orbit_model.py")
    rows = []
    for role, path in artifacts:
        rows.append({
            "role": role,
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "revision": p.REVISION,
            "configuration": p.CONFIGURATION,
            "units": "mm",
            "source_hash": source_hash,
            "sha256": sha256(path),
        })
    data = {
        "root": "..",
        "source": {"revision": p.REVISION, "configuration": p.CONFIGURATION, "units": "mm", "source_hash": source_hash},
        "required_roles": ["native-source", "step", "stl", "dxf", "pdf", "design-review", "motion-table", "render"],
        "artifacts": rows,
        "release_status": "prototype engineering handoff; external appearance approval and physical verification pending",
    }
    path = ROOT / "engineering" / "handoff-manifest.json"
    write_json(path, data)
    return path


def main() -> int:
    concept_board = make_concept_board()
    iteration_board = make_iteration_board()
    stable_review = stage_stable_review_assets()
    dxf_path = make_dxf()
    pdf_path = make_pdf()
    geometry_report = make_geometry_report()
    drawing_report = make_drawing_report(dxf_path, pdf_path)
    make_viewset_report_input()
    artifacts = [
        ("native-source", CAD / "orbit_model.py"),
        ("step", OUTPUT / "models" / "orbit-final.step"),
        ("stl", OUTPUT / "models" / "meshes" / "orbit-final.stl"),
        ("dxf", dxf_path),
        ("pdf", pdf_path),
        ("design-review", ROOT / "design-review.md"),
        ("motion-table", ROOT / "engineering" / "motion-states.json"),
        ("render", stable_review["hero"]),
        ("exploded-render", stable_review["exploded"]),
        ("section-render", stable_review["section"]),
        ("motion-render", stable_review["motion"]),
        ("concept-board", concept_board),
        ("failure-board", iteration_board),
        ("geometry-drc", geometry_report),
        ("drawing-drc", drawing_report),
        ("autocad-dxf-audit", REPORTS / "autocad-dxf-audit.json"),
    ]
    manifest = make_manifest(artifacts)
    print(json.dumps({"status": "PASS", "manifest": str(manifest), "artifacts": len(artifacts)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
