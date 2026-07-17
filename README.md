# Mechanical Design GB/T

A comprehensive, client-neutral skill for industrial and mechanical product design before manufacturing release.

The skill covers design briefs, concept comparison, human factors, form language, reference-image learning, backend routing, refined native 3D gates, surface and render review, motion configurations, engineering evidence, DFM, and a revision-bound handoff to downstream GB/T drafting.

## Install

Copy `skills/mechanical-design-gbt` into the skills directory used by your Codex or compatible skill runner.

The required entry point is:

```text
skills/mechanical-design-gbt/SKILL.md
```

Keep `mechanical-drafting-gbt` installed separately when full GB/T manufacturing drawings, GPS/GD&T, inspection, plotting, exchange verification, or formal release evidence are required.

## Deterministic checks

The skill includes validators for:

- active document and revision identity;
- 2D/3D interface alignment;
- named motion states and limits;
- render camera and image integrity;
- model and handoff manifest consistency;
- local CAD and image library inventory.

Validator success is deliberately narrow. It does not by itself prove aesthetics, usability, physical performance, safety, manufacturability, compliance, or approval.

## Local reference libraries

Personal CAD/JPG manifests are ignored by Git. Generate them locally with `catalog_reference_library.py` from the included portable example schema. Do not commit private absolute paths or third-party source assets.

## License

MIT License. See `LICENSE`.
