# Industrial Product Design GB/T

An industrial design and product design Skill for Codex and compatible AI agents. It develops product intent into coherent concepts, refined native 3D, review evidence, and a revision-bound GB/T engineering handoff.

面向工业设计、产品设计与硬件产品开发的 Codex Skill。它优先解决产品定位、造型比例、人机交互、CMF、接口整合、运动状态和 3D 成品质量，再把确认后的方案交给 GB/T 机械制图流程。

## Why this Skill exists

Correct dimensions and valid solids do not prove that a product looks convincing, works well, or is ready for engineering. This Skill inserts explicit design gates before manufacturing CAD and drafting:

- design brief, user scenario, task flow, and product architecture;
- meaningful concept alternatives at a common scale;
- silhouette, proportion, visual hierarchy, form language, and 360-degree coherence;
- ergonomics, controls, ports, cable routing, service access, and purchased-part envelopes;
- CMF, part breaks, gaps, flush relationships, fillet families, and detail density;
- parametric CAD massing, refined native 3D, motion configurations, and product rendering;
- surface, interference, stability, DFM, risk, evidence, and design-review gates;
- a controlled handoff to downstream GB/T drawings, GPS/GD&T, BOM, inspection, and release.

## Typical uses

Use it for consumer electronics, appliances, smart-home hardware, enclosures, controls, rotating mechanisms, desktop products, tools, equipment, and other physical products where appearance, interaction, proportion, or 3D quality affects success.

Example requests:

- Design a compact desktop charging product from a written brief.
- Redesign an appliance enclosure from reference images without copying protected details.
- Review whether a CAD model has a coherent fillet, gap, interface, and CMF language.
- Validate 0°, 90°, 180°, and 270° mechanism states before detailed engineering.
- Prepare an approved industrial-design package for GB/T mechanical drafting.

## Design and drafting are separate gates

| Skill | Primary responsibility | Completion evidence |
| --- | --- | --- |
| `industrial-product-design-gbt` | Product intent, concept selection, form, ergonomics, CMF, native 3D quality, motion, rendering, and design approval | Approved design revision, configuration set, interface table, review record, and handoff package |
| `mechanical-drafting-gbt` | Manufacturing definition, GB/T drawing rules, dimensions, fits, GPS/GD&T, BOM, inspection, plotting, exchange, and release compliance | Audited engineering drawings and release evidence |

Keep both Skills installed when a project must progress from industrial design into formal manufacturing documentation.

## Install

Clone the repository and copy `skills/industrial-product-design-gbt` into the skills directory used by Codex or another compatible skill runner.

```powershell
git clone https://github.com/beiming183-cloud/industrial-product-design-gbt.git
```

The required entry point is:

```text
skills/industrial-product-design-gbt/SKILL.md
```

## Included quality gates

The workflow includes backend capability, document identity, massing, form language, interface, motion, surface, render, design review, and engineering handoff gates. A failed gate returns the project to the preceding design stage instead of hiding the problem with extra dimensions or presentation graphics.

Deterministic scripts check:

- active document and revision identity;
- 2D/3D interface alignment;
- named motion states and limits;
- render camera and image integrity;
- model and handoff manifest consistency;
- local CAD and reference-image library inventory.

Validator success is deliberately narrow. It does not by itself prove aesthetics, usability, physical performance, safety, manufacturability, compliance, or approval.

## Reference-image and CAD-library learning

The Skill can extract reusable design-language observations from product images, sketches, competitor references, DWG libraries, and JPG previews while separating observation, inference, assumption, and confirmed requirement. Personal manifests, absolute paths, and third-party source assets remain local and are excluded from Git.

## Search topics

Industrial design, product design, consumer product design, hardware design, enclosure design, appliance design, CMF design, ergonomics, human factors, design review, concept design, parametric CAD, AutoCAD, 3D modeling, surface quality, product rendering, motion design, mechanism design, DFM, GB/T mechanical drafting, Codex Skill, AI agent Skill.

工业设计、产品设计、消费电子设计、家电设计、硬件设计、外壳设计、产品造型、CMF、人机工程、交互设计、参数化 CAD、AutoCAD、三维建模、曲面质量、产品渲染、机构设计、可制造性、GB/T 机械制图、Codex Skills。

## License

MIT License. See `LICENSE`.
