#!/usr/bin/env python3
"""Validate the standalone Skill repository without third-party packages."""

from __future__ import annotations

import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "industrial-product-design-gbt"
EXAMPLE = ROOT / "examples" / "quickstart"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run(script: str, input_name: str, expected_exit: int) -> None:
    completed = subprocess.run(
        [sys.executable, "-B", str(SKILL / "scripts" / script), str(EXAMPLE / input_name)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    require(
        completed.returncode == expected_exit,
        f"{input_name} returned {completed.returncode}, expected {expected_exit}: {completed.stdout}{completed.stderr}",
    )


def main() -> int:
    skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    require(skill_text.startswith("---\n"), "SKILL.md must start with YAML frontmatter")
    frontmatter = skill_text.split("---", 2)[1]
    require("name: industrial-product-design-gbt" in frontmatter, "Skill name does not match folder")
    require("description:" in frontmatter, "Skill description is missing")
    require(len(skill_text.splitlines()) < 500, "SKILL.md exceeds the progressive-disclosure limit")

    for path in sorted((SKILL / "scripts").glob("*.py")):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    compile(Path(__file__).read_text(encoding="utf-8"), str(Path(__file__)), "exec")

    for path in sorted(SKILL.rglob("*.json")) + sorted(EXAMPLE.rglob("*.json")):
        json.loads(path.read_text(encoding="utf-8"))

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for required in ("Five-minute quickstart", "Honest capability boundary", "FAQ", "Roadmap", "CONTRIBUTING.md"):
        require(required in readme, f"README is missing: {required}")
    for image_name in ("hero.svg", "workflow.svg"):
        image = ROOT / "docs" / "images" / image_name
        require(image.is_file(), f"README image is missing: {image_name}")
        ET.parse(image)
    for path in (
        ROOT / "CONTRIBUTING.md",
        ROOT / "CODE_OF_CONDUCT.md",
        ROOT / "SECURITY.md",
        ROOT / ".github" / "workflows" / "validate.yml",
        ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml",
        ROOT / ".github" / "ISSUE_TEMPLATE" / "design_case.yml",
    ):
        require(path.is_file(), f"community or validation file is missing: {path.relative_to(ROOT)}")

    run("check_pre_cad_brief.py", "brief-pass.json", 0)
    run("check_dimension_authority.py", "dimensions-pass.json", 0)
    run("check_dimension_authority.py", "dimensions-fail.json", 2)

    print("Repository validation PASS")
    print(f"Skill lines: {len(skill_text.splitlines())}")
    print("Quickstart contracts: 3/3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
