# Quickstart gate demo

This example runs without CAD software or third-party Python packages. It demonstrates the narrow deterministic gates bundled with the Skill; it is not a finished product-design case study.

Run from PowerShell:

```powershell
.\run_demo.ps1
```

Expected results:

| Input | Expected status | Reason |
| --- | --- | --- |
| `brief-pass.json` | `PASS` | Required pre-CAD fields and immutable design DNA are present |
| `dimensions-pass.json` | `PASS` | Critical USB geometry is based on controlled measurement; public AC data stays `TBD` |
| `dimensions-fail.json` | `FAIL` | A brand-page-derived AC opening is incorrectly marked `CONFIRMED` |

Reports are written to ignored `output/`. Compare them with the tracked files under `expected/`.

These validators check structured evidence contracts only. They do not prove appearance, ergonomics, electrical safety, standard conformity, or manufacturability.
