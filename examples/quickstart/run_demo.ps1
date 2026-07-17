$ErrorActionPreference = 'Stop'

$repo = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$skill = Join-Path $repo 'skills\industrial-product-design-gbt'
$output = Join-Path $PSScriptRoot 'output'
New-Item -ItemType Directory -Path $output -Force | Out-Null

$cases = @(
    @('check_pre_cad_brief.py', 'brief-pass.json', 'brief-pass.report.json', 0),
    @('check_dimension_authority.py', 'dimensions-pass.json', 'dimensions-pass.report.json', 0),
    @('check_dimension_authority.py', 'dimensions-fail.json', 'dimensions-fail.report.json', 2)
)

foreach ($case in $cases) {
    $script, $input, $report, $expectedExit = $case
    python -B (Join-Path $skill "scripts\$script") (Join-Path $PSScriptRoot $input) --output (Join-Path $output $report)
    if ($LASTEXITCODE -ne $expectedExit) {
        throw "$input returned $LASTEXITCODE; expected $expectedExit"
    }
    Write-Host "PASS contract: $input returned expected exit $expectedExit"
}

Write-Host "Reports: $output"
