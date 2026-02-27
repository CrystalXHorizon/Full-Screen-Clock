param(
  [string]$Version = "V0.6"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$downloadDir = Join-Path $env:USERPROFILE "Downloads"
$tempRoot = Join-Path $env:TEMP "desktop_clock_build"
$workPath = Join-Path $tempRoot "build"
$specPath = Join-Path $tempRoot "spec"
$name = "DesktopClock-$Version"

if (!(Test-Path $downloadDir)) {
  New-Item -ItemType Directory -Path $downloadDir | Out-Null
}

if (Test-Path $tempRoot) {
  Remove-Item -Recurse -Force $tempRoot
}

py -3 -m PyInstaller --noconfirm --clean --onefile --windowed --name $name --distpath $downloadDir --workpath $workPath --specpath $specPath --hidden-import PIL --hidden-import PIL.Image --hidden-import PIL.ImageTk (Join-Path $projectRoot "clock_app.py")

Write-Output "Build completed: $(Join-Path $downloadDir ($name + '.exe'))"

