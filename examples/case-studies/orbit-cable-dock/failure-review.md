# Failure review — Rev A to Rev C

## Rejected Rev A

Rev A is deliberately preserved as a valid STEP model. It proves the failure was industrial-design quality, not file corruption.

- Problem: the 23 mm rotor plus 12 mm base read as stacked trays; the centre cap and fastener dominate the product; the 0.2 mm seam does not communicate rotation; four cable slots use independent widths and depths.
- Evidence: `orbit-failed-rev-a.step`, same-camera ISO/TOP renders, and the before/after view-set report.
- Escaped gate: `FORM_LANGUAGE_GATE` and `INTERFACE_GATE` were initially evaluated too late, after a geometrically valid model existed.
- Root cause: no single slot parameter source, height and cap ratios were not constrained in the massing brief, and the centre retention system was treated as exposed hardware rather than part of the product hierarchy.
- Containment: Rev A is labeled `failed` and excluded from the engineering handoff role set.
- Permanent source correction: one shared slot width/depth/radius, 1.2 mm visible shadow gap, 14.8 mm rotor, recessed 24 mm cap, flush fastener envelope, and four equal TPU floor pads.
- Process change: the case now has explicit height/footprint gates, repeated-interface checks, a same-camera failed/final comparison, and a required top plus section review.
- Recheck: Rev C must remain below 30 mm, keep four equal slots, expose a readable shadow gap, and pass the model/motion/manifest validators.

## Optimization iterations

1. C0 massing: low soft-square base plus circular rotor. Selected on posture and envelope.
2. C1 detailed model: four true U-grooves, centre bushing, cap, flexure insert, and named motion states.
3. C2 visual review: rejected the proud screw head after the first ISO snapshot; recessed the head below the cap surface.
4. C3 final candidate: added four equal TPU groove liners so cable interfaces remain legible in top and isometric views and have a plausible soft-contact strategy.

Status: the source correction and regression evidence are complete. Physical cable fit, detent force/life, foot friction, and stability remain `NOT_EVALUATED`.

