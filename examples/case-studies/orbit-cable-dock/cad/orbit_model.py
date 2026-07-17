"""Parametric B-rep source for ORBIT, a four-station rotary cable dock.

Coordinate convention: origin at footprint centre on the desk plane, XY is the
desk plane, +Z is up. All dimensions are millimetres. STEP is authoritative.
"""

from __future__ import annotations

from build123d import (
    Align,
    Box,
    Color,
    Compound,
    Cylinder,
    Location,
    RectangleRounded,
    Rot,
    Sphere,
    Vector,
    extrude,
    fillet,
)

from orbit_params import *


COLORS = {
    "base": Color(0.20, 0.23, 0.27),
    "rotor": Color(0.86, 0.87, 0.84),
    "bushing": Color(0.16, 0.55, 0.56),
    "detent": Color(0.95, 0.47, 0.20),
    "liner": Color(0.10, 0.13, 0.16),
    "cap": Color(0.16, 0.55, 0.56),
    "hardware": Color(0.38, 0.41, 0.45),
}


def _named(shape, label: str, color: Color):
    shape.label = label
    shape.color = color
    return shape


def rounded_prism(width: float, depth: float, height: float, plan_radius: float, edge_radius: float):
    body = extrude(RectangleRounded(width, depth, plan_radius), amount=height)
    if edge_radius > 0:
        body = fillet(body.edges(), edge_radius)
    return body


def make_base():
    base = rounded_prism(
        BASE_WIDTH, BASE_DEPTH, BASE_HEIGHT, BASE_PLAN_RADIUS, BASE_EDGE_RADIUS
    )

    # Integrated pivot post; the pilot hole is explicitly a prototype interface.
    post = Cylinder(
        AXLE_DIAMETER / 2.0,
        AXLE_HEIGHT,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).moved(Location((0, 0, BASE_HEIGHT - 0.4)))
    base = base + post
    pilot = Cylinder(
        AXLE_PILOT_DIAMETER / 2.0,
        AXLE_HEIGHT + 2.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).moved(Location((0, 0, BASE_HEIGHT - 0.2)))
    base = base - pilot

    # Four shallow index pockets share one radial and angular parameter source.
    for angle in INDEX_ANGLES_DEG:
        pocket = Cylinder(
            DETENT_POCKET_DIAMETER / 2.0,
            DETENT_POCKET_DEPTH + 0.4,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        ).moved(Location((DETENT_RADIUS, 0, BASE_HEIGHT - DETENT_POCKET_DEPTH)))
        base = base - (Rot(0, 0, angle) * pocket)

    return _named(base, "base:soft-square", COLORS["base"])


def _slot_tool():
    inner_x = ROTOR_DIAMETER / 2.0 - SLOT_RADIAL_DEPTH
    rectangular_length = SLOT_RADIAL_DEPTH + 2.0
    centre_x = inner_x + rectangular_length / 2.0
    z0 = ROTOR_BOTTOM_Z + ROTOR_HEIGHT - SLOT_CUT_DEPTH
    box = Box(
        rectangular_length,
        SLOT_WIDTH,
        SLOT_CUT_DEPTH + 1.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).moved(Location((centre_x, 0, z0)))
    end = Cylinder(
        SLOT_END_RADIUS,
        SLOT_CUT_DEPTH + 1.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).moved(Location((inner_x, 0, z0)))
    return box + end


def make_rotor(angle_deg: float = 0.0):
    rotor = Cylinder(
        ROTOR_DIAMETER / 2.0,
        ROTOR_HEIGHT,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).moved(Location((0, 0, ROTOR_BOTTOM_Z)))
    rotor = fillet(rotor.edges(), ROTOR_EDGE_RADIUS)

    bore = Cylinder(
        ROTOR_BORE_DIAMETER / 2.0,
        ROTOR_HEIGHT + 2.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).moved(Location((0, 0, ROTOR_BOTTOM_Z - 1.0)))
    rotor = rotor - bore

    # A real shallow centre recess keeps the cap integrated rather than pasted on.
    cap_recess = Cylinder(
        CAP_DIAMETER / 2.0 + 0.25,
        CAP_RECESS_DEPTH + 0.3,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).moved(Location((0, 0, ROTOR_BOTTOM_Z + ROTOR_HEIGHT - CAP_RECESS_DEPTH)))
    rotor = rotor - cap_recess

    slot = _slot_tool()
    for station_angle in INDEX_ANGLES_DEG:
        rotor = rotor - (Rot(0, 0, station_angle) * slot)

    # Underside pocket for a replaceable printed flexure insert.
    cavity = Box(
        DETENT_INSERT_LENGTH + 0.6,
        DETENT_INSERT_WIDTH + 0.6,
        DETENT_INSERT_THICKNESS + 0.7,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).moved(Location((DETENT_RADIUS - DETENT_INSERT_LENGTH / 2.0, 0, ROTOR_BOTTOM_Z - 0.1)))
    rotor = rotor - cavity

    rotor = Rot(0, 0, angle_deg) * rotor
    return _named(rotor, "rotor:four-slot", COLORS["rotor"])


def make_bushing():
    outer = Cylinder(
        BUSHING_OD / 2.0,
        BUSHING_HEIGHT,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).moved(Location((0, 0, ROTOR_BOTTOM_Z - 0.2)))
    inner = Cylinder(
        BUSHING_ID / 2.0,
        BUSHING_HEIGHT + 1.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).moved(Location((0, 0, ROTOR_BOTTOM_Z - 0.7)))
    return _named(outer - inner, "bushing:prototype", COLORS["bushing"])


def make_slot_liner_set(angle_deg: float = 0.0):
    """Four equal TPU floor pads generated from the cable-slot parameters."""
    inner_x = ROTOR_DIAMETER / 2.0 - SLOT_RADIAL_DEPTH
    liner_length = SLOT_RADIAL_DEPTH - 4.0
    liner_width = SLOT_WIDTH - 1.0
    liner_z = ROTOR_BOTTOM_Z + ROTOR_HEIGHT - SLOT_CUT_DEPTH + 0.05
    pad = Box(
        liner_length,
        liner_width,
        0.75,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).moved(Location((inner_x + liner_length / 2.0, 0, liner_z)))
    pad_end = Cylinder(
        liner_width / 2.0,
        0.75,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).moved(Location((inner_x, 0, liner_z)))
    seed = pad + pad_end
    liners = []
    for station_angle in INDEX_ANGLES_DEG:
        liner = Rot(0, 0, angle_deg + station_angle) * seed
        liner.label = f"slot-liner:{int(station_angle):03d}deg"
        liner.color = COLORS["liner"]
        liners.append(liner)
    result = Compound(children=liners, label="slot-liner-set:TPU")
    result.label = "slot-liner-set:TPU"
    return result


def make_detent_insert(angle_deg: float = 0.0):
    beam = Box(
        DETENT_INSERT_LENGTH,
        DETENT_INSERT_WIDTH,
        DETENT_INSERT_THICKNESS,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).moved(Location((DETENT_RADIUS - DETENT_INSERT_LENGTH / 2.0, 0, ROTOR_BOTTOM_Z + 0.15)))
    nub = Sphere(DETENT_NUB_DIAMETER / 2.0).moved(
        Location((DETENT_RADIUS, 0, BASE_HEIGHT + 0.75))
    )
    insert = beam + nub
    insert = Rot(0, 0, angle_deg) * insert
    return _named(insert, "detent:flexure-insert", COLORS["detent"])


def make_retainer_cap():
    cap_z = ROTOR_BOTTOM_Z + ROTOR_HEIGHT - CAP_RECESS_DEPTH + 0.1
    cap = Cylinder(
        CAP_DIAMETER / 2.0,
        CAP_HEIGHT,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).moved(Location((0, 0, cap_z)))
    cap = fillet(cap.edges(), 0.8)
    screw_recess = Cylinder(
        3.6,
        1.1,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).moved(Location((0, 0, cap_z + CAP_HEIGHT - 1.0)))
    cap = cap - screw_recess
    return _named(cap, "retainer:centre-cap", COLORS["cap"])


def make_fastener_envelope():
    # Representation only: M4 head/shank envelope. Supplier and final engagement TBD.
    shank = Cylinder(
        2.0,
        14.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).moved(Location((0, 0, BASE_HEIGHT + 0.6)))
    head = Cylinder(
        3.5,
        3.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    ).moved(Location((0, 0, ROTOR_BOTTOM_Z + ROTOR_HEIGHT - 2.5)))
    return _named(shank + head, "fastener-envelope:M4-TBD", COLORS["hardware"])


def build_orbit_assembly(angle_deg: float = 0.0):
    """Return the assembled design at one reproducible rotary state."""
    children = [
        make_base(),
        make_bushing(),
        make_rotor(angle_deg),
        make_slot_liner_set(angle_deg),
        make_detent_insert(angle_deg),
        make_retainer_cap(),
        make_fastener_envelope(),
    ]
    assembly = Compound(children=children, label=f"ORBIT Rev {REVISION} {angle_deg:g}deg")
    assembly.label = f"ORBIT Rev {REVISION} {angle_deg:g}deg"
    return assembly


def gen_step():
    return build_orbit_assembly(0.0)
