# CAMELOT-OS v9000.96 Go-Live Readiness

Date: 2026-07-07
Scope: Final remote deployment gate after local Wasmtime Sentinel pass

## Local Gates Passed

- Frontend build: `npm run build` passed in `02_FORGE/generated/ukg_omega_glyph_v1000/Node_A_Frontend`.
- Vercel CLI: present, `54.18.5`.
- Aaliyah WASM artifact: present at `target/wasm32-wasip1/release/aaliyah_comms.wasm`.
- Aaliyah WASM SHA-256: `9D8CF6B5F8E13622B1087FB596B722A30E58CABF953F4A4B7A55AA24C72F1095`.
- Wasmtime runtime gate: passed on `46.0.1`.

## Remote Blockers

- The frontend folder is not linked to a Vercel project; `.vercel/` is absent.
- `npx vercel whoami` ran but did not print an account identity in this shell.
- Windows OpenSSH `ssh.exe` and `scp.exe` are available; use `scp` instead of `rsync` from this host.
- The KBA node IP and SSH path have not been verified from this shell.
- Remote mutation still requires explicit operator approval.

## Corrected Deployment Commands

Run from the repo root unless otherwise noted.

```powershell
# 1. Commit only the scoped production files.
git add Cargo.toml rust-toolchain.toml kinetic_edge/aaliyah_comms `
  02_FORGE/generated/ukg_omega_glyph_v1000/Node_A_Frontend/src `
  blueprints/v9000.95 blueprints/v9000.96
git commit -m "feat(production): add OpenHuman UI and Aaliyah WASM preflight"
git push origin main
```

```powershell
# 2. Authenticate, link, and verify the Vercel project before production deploy.
cd 02_FORGE/generated/ukg_omega_glyph_v1000/Node_A_Frontend
npx vercel login
npx vercel whoami
npx vercel link
npx vercel deploy --prod
```

```powershell
# 3. Non-mutating KBA preflight from Windows PowerShell.
# Replace with the verified KBA Tailscale IP.
$KBA_IP = "100.115.92.4"
$WASM_SHA = "9D8CF6B5F8E13622B1087FB596B722A30E58CABF953F4A4B7A55AA24C72F1095"

ssh "root@$KBA_IP" "hostname && wasmtime --version && test -d /opt/camelot/cartridges/pills && echo pills_dir_present"
```

```powershell
# 4. Approved KBA mutation block from repo root.
# Only run after Vercel link/auth and KBA preflight are green.
cd C:\Users\vizio\CAMELOT_OS

ssh "root@$KBA_IP" "mkdir -p /opt/camelot/cartridges/pills"

scp target\wasm32-wasip1\release\aaliyah_comms.wasm "root@$KBA_IP:/opt/camelot/cartridges/pills/aaliyah_comms.wasm"

ssh "root@$KBA_IP" "sha256sum /opt/camelot/cartridges/pills/aaliyah_comms.wasm && wasmtime --version"
ssh "root@$KBA_IP" "systemctl restart camelotd && systemctl status camelotd --no-pager"
```

## KBA Acceptance Criteria

- Remote `sha256sum` matches `9D8CF6B5F8E13622B1087FB596B722A30E58CABF953F4A4B7A55AA24C72F1095`.
- Remote `wasmtime --version` reports `46.0.1` or newer.
- The non-mutating preflight confirms `/opt/camelot/cartridges/pills` already exists, or the approved mutation block creates it before copy.
- `camelotd` restarts cleanly.
- Router status shows the Aaliyah pill/tool endpoint registered.
