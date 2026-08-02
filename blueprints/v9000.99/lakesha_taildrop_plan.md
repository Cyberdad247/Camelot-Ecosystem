# CAMELOT-OS v9000.99 Lakesha Taildrop Plan

Date: 2026-07-07
Scope: Pivot from blocked inbound SSH to Taildrop plus local execution on Lakesha

## Network Reality

- Prior KBA SSH target `100.115.92.4:22` timed out.
- The proposed target is Lakesha at `100.100.155.55`.
- Inbound remote-execution ports are treated as closed by design unless the operator verifies otherwise.
- Deployment strategy: transfer a non-secret bootstrap script with Taildrop, then execute locally on Lakesha.

## Secret Handling

Do not store `WEBHOOK_SECRET`, `CAMELOT_CARTRIDGE_HMAC_KEY`, API keys, tokens, or passwords in this repo or in the bootstrap file. Set them only in the local Lakesha PowerShell session before running the script.

## Excalibur Transfer

Run from `C:\Users\vizio\CAMELOT_OS` on Excalibur:

```powershell
tailscale status
tailscale file cp blueprints\v9000.99\bootstrap_lakesha.ps1 <lakesha-tailscale-name>:
```

Replace `<lakesha-tailscale-name>` with the exact name from `tailscale status`.

## Lakesha Local Execution

Run locally on Lakesha:

```powershell
tailscale file get .

$env:WEBHOOK_SECRET = Read-Host "WEBHOOK_SECRET"
$env:CAMELOT_CARTRIDGE_HMAC_KEY = Read-Host "CAMELOT_CARTRIDGE_HMAC_KEY"

.\bootstrap_lakesha.ps1 -HostAddress "100.100.155.55" -Port 9000
```

## Acceptance Criteria

- `bootstrap_lakesha.ps1` contains no literal secrets.
- Lakesha clones or reuses `Cyberdad247/Camelot-Ecosystem`.
- Python dependency installation succeeds on Lakesha.
- `control_plane.drone_node` starts on `100.100.155.55:9000`.
- Omni-Router or Bifrost status confirms `kba-drone-lakesha` is reachable.

## Stop Conditions

- Stop if `tailscale status` does not show the expected Lakesha node.
- Stop if secrets are accidentally pasted into a repo file.
- Stop if the Lakesha host address differs from `100.100.155.55`.
- Stop if dependency installation fails.
- Stop if `control_plane.drone_node` fails to import or bind.
