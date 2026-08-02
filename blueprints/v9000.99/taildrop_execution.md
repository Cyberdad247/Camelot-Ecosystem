# CAMELOT-OS v9000.99 Taildrop Execution

Date: 2026-07-07
Executor: SIR_CODEX

## Result

Status: sanitized bootstrap transferred to Lakesha via Taildrop.

## Evidence

- `tailscale status` showed `lakesha` online at `100.100.155.55`.
- Local Taildrop command completed successfully:
  `tailscale file cp blueprints\v9000.99\bootstrap_lakesha.ps1 lakesha:`
- Corrected starter Taildrop command completed successfully:
  `tailscale file cp blueprints\v9000.99\start_lakesha_drone.ps1 lakesha:`
- `bootstrap_lakesha.ps1` passed PowerShell parser validation.
- `start_lakesha_drone.ps1` passed PowerShell parser validation.
- Secret scan over `blueprints\v9000.99` found no pasted literal secret values from the proposed payload.

## Next Operator Action On Lakesha

Preferred fast path after receiving `start_lakesha_drone.ps1`:

```powershell
tailscale file get .

.\start_lakesha_drone.ps1
```

The script prompts for `WEBHOOK_SECRET` and `CAMELOT_CARTRIDGE_HMAC_KEY` if they
are not already set, then starts the drone with packages stored under
`%LOCALAPPDATA%\Camelot\cartridge\packages`.

Manual equivalent:

```powershell
$env:WEBHOOK_SECRET = Read-Host "WEBHOOK_SECRET"
$env:CAMELOT_CARTRIDGE_HMAC_KEY = Read-Host "CAMELOT_CARTRIDGE_HMAC_KEY"
$packages = "$env:LOCALAPPDATA\Camelot\cartridge\packages"
New-Item -ItemType Directory -Path $packages -Force | Out-Null
Set-Location C:\Users\Camelot-os
py -m control_plane.drone_node --node-id kba-drone-lakesha --host 100.100.155.55 --port 9000 --packages-dir $packages
```

## Stop Conditions

- Stop if the Taildrop file is not the sanitized `bootstrap_lakesha.ps1`.
- Stop if secrets are accidentally pasted into a repo file.
- Stop if Python dependency installation fails.
- Stop if `control_plane.drone_node` fails to import or bind to port `9000`.
