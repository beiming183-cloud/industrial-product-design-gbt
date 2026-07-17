"""Concept A massing: static linear comb, simple but no rotary interaction."""

from build123d import Align, Box, Color, Compound, Cylinder, Location, RectangleRounded, extrude, fillet


def gen_step():
    body = extrude(RectangleRounded(108, 50, 12), amount=14)
    body = fillet(body.edges(), 1.6)
    for x in (-40, -20, 0, 20, 40):
        stem = Box(7, 18, 9, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(
            Location((x, 19, 6))
        )
        end = Cylinder(3.5, 9, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(
            Location((x, 10, 6))
        )
        body = body - (stem + end)
    body.label = "A:static-linear-comb"
    body.color = Color(0.82, 0.83, 0.80)
    return Compound(children=[body], label="Concept A static comb")

