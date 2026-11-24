<#
  Shorts Studio Kit: one-command install (Windows PowerShell). No git needed.

    irm https://raw.githubusercontent.com/venkyverse24/shorts-studio-kit/main/bootstrap.ps1 | iex

  Downloads the kit, installs it into the current folder (or $env:KIT_TARGET) and removes the download.
  Prefer to read it first? Save this file, read it, then run it: it only downloads the kit zip and runs
  the kit's own install.ps1.

  Settings (environment variables):
    KIT_REPO    owner/repo on GitHub, e.g. for a fork    (default: venkyverse24/shorts-studio-kit)
    KIT_REF     branch or tag, for example v1.0.0         (default: main)
    KIT_TARGET  studio folder                             (default: current folder)
    KIT_ZIP     a local zip path or URL instead of GitHub (for testing and offline use)
#>
$ErrorActionPreference = 'Stop'
$repo = if ($env:KIT_REPO) { $env:KIT_REPO } else { 'venkyverse24/shorts-studio-kit' }
$ref = if ($env:KIT_REF) { $env:KIT_REF } else { 'main' }
$target = if ($env:KIT_TARGET) { $env:KIT_TARGET } else { (Get-Location).Path }
$src = if ($env:KIT_ZIP) { $env:KIT_ZIP } else { "https://github.com/$repo/archive/$ref.zip" }

$tmp = Join-Path ([IO.Path]::GetTempPath()) ("shorts-kit-" + [guid]::NewGuid().ToString('N').Substring(0, 8))
New-Item -ItemType Directory -Path $tmp | Out-Null
try {
    Write-Host "Downloading the kit..."
    $zip = Join-Path $tmp 'kit.zip'
    if ($src -match '^https?://') { Invoke-WebRequest -Uri $src -OutFile $zip -UseBasicParsing } else { Copy-Item $src $zip }
    Expand-Archive -Path $zip -DestinationPath (Join-Path $tmp 'x') -Force
    $installer = Get-ChildItem (Join-Path $tmp 'x') -Recurse -Filter install.ps1 | Select-Object -First 1
    if (-not $installer) { throw "install.ps1 not found in the download. Nothing was installed." }
    & $installer.FullName -Target $target
}
finally {
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
}
