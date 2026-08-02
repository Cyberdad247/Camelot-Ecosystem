# CAMELOT-OS v9000.97 Approved Mutation Block

Date: 2026-07-07
Scope: Operator-executed go-live block after v9000.96 local and remote preflight gates

## Preconditions

- Local frontend build passed.
- Local Aaliyah WASM compiled and executed under Wasmtime `46.0.1`.
- Local Aaliyah WASM SHA-256:
  `9D8CF6B5F8E13622B1087FB596B722A30E58CABF953F4A4B7A55AA24C72F1095`.
- Windows OpenSSH `ssh.exe` and `scp.exe` are available.
- Vercel account/project selection is confirmed by the operator.
- KBA IP is confirmed by the operator.

## Phase 1: Vercel Mutation

Run from PowerShell:

```powershell
cd C:\Users\vizio\CAMELOT_OS\02_FORGE\generated\ukg_omega_glyph_v1000\Node_A_Frontend

npx vercel login
npx vercel whoami
npx vercel link
npx vercel deploy --prod
```

Record the production URL returned by Vercel before proceeding to Phase 2.

## Phase 2: KBA Node Mutation

Run from PowerShell at the repository root:

```powershell
cd C:\Users\vizio\CAMELOT_OS

$KBA_IP = "100.115.92.4"
$WASM_SHA = "9D8CF6B5F8E13622B1087FB596B722A30E58CABF953F4A4B7A55AA24C72F1095"

ssh "root@$KBA_IP" "hostname && wasmtime --version"
ssh "root@$KBA_IP" "mkdir -p /opt/camelot/cartridges/pills"

scp target\wasm32-wasip1\release\aaliyah_comms.wasm "root@${KBA_IP}:/opt/camelot/cartridges/pills/aaliyah_comms.wasm"

ssh "root@$KBA_IP" "sha256sum /opt/camelot/cartridges/pills/aaliyah_comms.wasm"
ssh "root@$KBA_IP" "systemctl restart camelotd && systemctl status camelotd --no-pager"
```

## Required Operator Checks

- Vercel deploy returns the intended production URL.
- Remote `wasmtime --version` reports `46.0.1` or newer.
- Remote `sha256sum` equals `9D8CF6B5F8E13622B1087FB596B722A30E58CABF953F4A4B7A55AA24C72F1095`.
- `camelotd` reports active/running after restart.
- Router/API status confirms the Aaliyah pill endpoint is registered.

## Stop Conditions

- Stop if `npx vercel whoami` does not show the expected account.
- Stop if `npx vercel link` points to the wrong project or team.
- Stop if SSH connects to an unexpected hostname.
- Stop if remote Wasmtime is older than `46.0.1`.
- Stop if the remote hash differs from the local hash.
- Stop if `camelotd` restart fails.

## Automated Wrapper

The operator-run wrapper is staged at `blueprints/v9000.97/go_live_wrapper.ps1`.
It enforces the same gates with fail-closed PowerShell checks and stages the
WASM file under `/tmp/camelot_staging` before promoting it to the live pill
directory.
