$ErrorActionPreference = "Stop"
Write-Host "EXCALIBUR BRIDGE: GITHUB LINK ACTIVATION" -ForegroundColor Yellow

# Require a preconfigured token instead of hardcoding a PAT in source control.
if (-not $env:GITHUB_TOKEN) {
    throw "GITHUB_TOKEN is not set. Export a token in your shell before launching the bridge."
}

Write-Host "Reinstalling Dependencies..."
pip install fastapi uvicorn pydantic GitPython requests -q

Write-Host "Launching Bridge..."
python c:\Users\vizio\Applications\chimera-os\camelot-os\proxy\bridge.py
