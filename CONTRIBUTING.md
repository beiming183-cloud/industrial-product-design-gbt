# Contributing

Thank you for helping improve a design-first, evidence-bound workflow for physical products.

## Useful contributions

- anonymized product-design case studies with traceable revisions and review evidence;
- transferable form, ergonomics, interface, motion, DFM, or service gates;
- deterministic validator fixtures, including expected failures and boundary cases;
- backend capability tests for native B-rep, surface, rendering, motion, section, and export workflows;
- corrections that cite an authorized or public primary source without reproducing restricted material;
- Chinese and English documentation improvements.

## Before opening a pull request

1. Open an issue describing the problem, intended scope, evidence, and affected maturity level.
2. Keep `SKILL.md` concise; put detailed methods in one directly linked reference.
3. Add deterministic logic to `scripts/` only when a structured input and narrow claim are defined.
4. Run `python tools/validate_repository.py`.
5. State what the change proves and what remains outside its authority.

## Evidence and privacy rules

Do not submit:

- copyrighted standards tables or unauthorized normative text;
- proprietary CAD, customer names, private paths, credentials, or project secrets;
- unlicensed product images, trademarks used as project branding, or copied trade dress;
- remembered safety dimensions or unsupported compliance claims;
- a polished render presented as manufacturing, ergonomic, or safety proof.

Prefer minimal fixtures, synthetic examples, controlled measurements, public official sources, and bounded claims.

## Pull request checklist

- [ ] The change solves one clearly described problem.
- [ ] Skill routing points to every new reference.
- [ ] New scripts have positive and negative fixtures.
- [ ] Personal paths and local learning records are excluded.
- [ ] Documentation states limitations and required human approval.
- [ ] Repository validation passes.

By contributing, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md) and license your contribution under the repository's MIT License.
