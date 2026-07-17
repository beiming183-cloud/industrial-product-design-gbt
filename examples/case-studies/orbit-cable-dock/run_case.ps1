param(
  [string]$Python = "python",
  [string]$CadSkill = "$env:USERPROFILE\.agents\skills\cad",
  [string]$DesignSkill = "D:\Codex\skills\industrial-product-design-gbt"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $Root
try {
  & $Python "$CadSkill\scripts\step" `
    "cad/orbit_model.py=output/models/orbit-final.step" `
    --stl "meshes/orbit-final.stl" `
    --glb "meshes/orbit-final.glb" `
    --mesh-tolerance 0.08 `
    --mesh-angular-tolerance 0.12 `
    --force

  & $Python "$CadSkill\scripts\step" `
    "cad/concept_a_static_comb.py=output/models/concept-a-static-comb.step" `
    "cad/concept_b_tall_drum.py=output/models/concept-b-tall-drum.step" `
    "cad/concept_c_low_orbit.py=output/models/concept-c-low-orbit.step" `
    "cad/orbit_failed_rev_a.py=output/models/orbit-failed-rev-a.step" `
    "cad/orbit_state_045.py=output/models/orbit-state-045.step" `
    "cad/orbit_state_090.py=output/models/orbit-state-090.step" `
    "cad/orbit_state_180.py=output/models/orbit-state-180.step" `
    "cad/orbit_state_270.py=output/models/orbit-state-270.step" `
    "cad/orbit_section_x.py=output/models/orbit-section-x.step" `
    --force

  & $Python "$CadSkill\scripts\inspect" refs "output/models/orbit-final.step" --facts --planes --positioning
  & $Python "source/build_case.py"
  & $Python "$DesignSkill\scripts\check_pre_cad_brief.py" "brief.json" --output "reports/brief-gate.json"
  & $Python "$DesignSkill\scripts\check_dimension_authority.py" "dimension-authority.json" --output "reports/dimension-authority.json"
  & $Python "$DesignSkill\scripts\validate_motion_states.py" "engineering/motion-states.json" --output "reports/motion-validation.json"
  & $Python "$DesignSkill\scripts\compare_render_viewset.py" "review/render-viewset.json" --output "reports/render-viewset.json"
  & $Python "$DesignSkill\scripts\check_model_manifest.py" "engineering/handoff-manifest.json" --output "reports/handoff-manifest.json"
}
finally {
  Pop-Location
}

