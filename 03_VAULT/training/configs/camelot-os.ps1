# Camelot OS -- PowerShell entry point
# Usage: camelot-os [--no-hud] [--status] [--ask "question"] [-p provider]

$env:PYTHONIOENCODING = "utf-8"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
python "$ScriptDir\hud.py" @args
