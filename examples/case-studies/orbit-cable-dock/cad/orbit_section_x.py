"""True B-rep half-section through the X=0 datum for review rendering."""

from build123d import Align, Box, Compound

from orbit_model import (
    make_base,
    make_bushing,
    make_detent_insert,
    make_fastener_envelope,
    make_retainer_cap,
    make_rotor,
    make_slot_liner_set,
)


def gen_step():
    positive_x_half = Box(
        70,
        130,
        60,
        align=(Align.MIN, Align.CENTER, Align.MIN),
    )
    source = [
        make_base(),
        make_bushing(),
        make_rotor(0),
        make_slot_liner_set(0),
        make_detent_insert(0),
        make_retainer_cap(),
        make_fastener_envelope(),
    ]
    clipped = []
    for index, shape in enumerate(source, start=1):
        sectioned = shape & positive_x_half
        if sectioned.volume > 1e-6:
            sectioned.label = f"sectioned-component:{index}"
            sectioned.color = shape.color
            clipped.append(sectioned)
    return Compound(children=clipped, label="ORBIT Rev C X=0 half-section")

