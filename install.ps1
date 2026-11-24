<#
  Shorts Studio Kit installer (Windows PowerShell).

  .\install.ps1                      install into the current folder
  .\install.ps1 -Target C:\my-studio install into another folder
  .\install.ps1 -Force               overwrite kit files that differ (your brand.md and data are never overwritten)

  Installs skills and agents into <Target>\.claude\, scripts into <Target>\tools\, and creates
  brand.md, shorts-kit.json, notes\queue.md and analytics\results.csv if they do not exist yet.
#>
param([string]$Target = (Get-Location).Path, [switch]$Force)
$ErrorActionPreference = 'Stop'
$Kit = Split-Path -Parent $MyInvocation.MyCommand.Path
$Target = (New-Item -ItemType Directory -Force -Path $Target).FullName
$copied = 0; $skipped = @(); $kept = @()

# preflight: refuse to start if the kit itself is incomplete, so a bad download never leaves a half install
$need = 'templates\brand.md','templates\shorts-kit.json','templates\queue.md','templates\results.csv','templates\CLAUDE-section.md'
$bad = @($need | Where-Object { -not (Test-Path (Join-Path $Kit $_)) })
foreach ($d in 'skills','agents','tools') { if (-not (Get-ChildItem (Join-Path $Kit $d) -ErrorAction SilentlyContinue)) { $bad += "$d\" } }
if ($bad) { Write-Host "kit is incomplete, missing: $($bad -join ', ')" -ForegroundColor Red; Write-Host "Nothing was installed. Re-download the kit and try again."; exit 1 }

function Copy-Kit($src, $dst) {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dst) | Out-Null
    if (Test-Path $dst) {
        if ((Get-FileHash $src).Hash -eq (Get-FileHash $dst).Hash) { return }
        if (-not $Force) { $script:skipped += $dst; return }
    }
    Copy-Item $src $dst -Force; $script:copied++
}
function Copy-Once($src, $dst) {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dst) | Out-Null
    if (Test-Path $dst) { $script:kept += $dst; return }
    Copy-Item $src $dst; $script:copied++
}

Get-ChildItem "$Kit\skills" -Directory | ForEach-Object {
    Copy-Kit "$($_.FullName)\SKILL.md" "$Target\.claude\skills\$($_.Name)\SKILL.md"
}
Get-ChildItem "$Kit\agents" -Filter *.md | ForEach-Object { Copy-Kit $_.FullName "$Target\.claude\agents\$($_.Name)" }
Get-ChildItem "$Kit\tools" -Filter *.py | ForEach-Object { Copy-Kit $_.FullName "$Target\tools\$($_.Name)" }

Copy-Once "$Kit\templates\brand.md"        "$Target\brand.md"
Copy-Once "$Kit\templates\shorts-kit.json" "$Target\shorts-kit.json"
Copy-Once "$Kit\templates\queue.md"        "$Target\notes\queue.md"
Copy-Once "$Kit\templates\results.csv"     "$Target\analytics\results.csv"

$claude = "$Target\CLAUDE.md"; $section = Get-Content "$Kit\templates\CLAUDE-section.md" -Raw
if (-not (Test-Path $claude)) { Set-Content $claude "# Studio`n" -Encoding utf8 }
if (-not (Select-String -Path $claude -Pattern 'shorts-studio-kit:begin' -Quiet)) { Add-Content $claude $section -Encoding utf8; $copied++ }

# keep private terms out of git
$gi = "$Target\.gitignore"
if (-not (Test-Path $gi)) { New-Item -ItemType File -Path $gi | Out-Null }
foreach ($line in 'shorts-kit.json', '.env*') {
    if (-not (Select-String -Path $gi -Pattern ([regex]::Escape($line)) -SimpleMatch -Quiet)) { Add-Content $gi $line }
}

$py = (Get-Command python, python3, py -ErrorAction SilentlyContinue | Select-Object -First 1)
Write-Host ""
Write-Host "Shorts Studio Kit installed into $Target" -ForegroundColor Green
Write-Host "  files written: $copied"
if ($skipped) { Write-Host "  kept your edited versions (use -Force to overwrite):"; $skipped | ForEach-Object { Write-Host "    $_" } }
if ($kept)    { Write-Host "  already present, not touched: $($kept.Count) template file(s)" }
if (-not $py) { Write-Host "  WARNING: Python 3 not found on PATH. The scripts in tools\ need it." -ForegroundColor Yellow }
Write-Host ""
Write-Host "Next:"
Write-Host "  1. Fill in brand.md and shorts-kit.json (your private terms; this file stays out of git)."
Write-Host "  2. Open Claude Code in $Target and type:  /short <your topic>"
