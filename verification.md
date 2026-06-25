# CAMELOT OS Review Remediation Verification

**Compiler:** Anya Gate / Prompt Engineering Cartridge  
**Date:** 2026-05-14

## V1 - Command Surface

```powershell
cd C:\Users\vizio\CAMELOT_OS
cmd /c camelot --json ledger status
cmd /c camelot ledger status
cmd /c camelot codex status
cmd /c ks --list
cmd /c knight-session --route
```

Pass:

- control-plane commands parse through `control_plane.camelot_cli`.
- `ks` and `knight-session` still render OmniRoute tables.

## V2 - Ledger Safety

```powershell
cmd /c camelot --json ledger status
Get-Content .\03_VAULT\runtime_state\forensic_checks.jsonl -Tail 3
```

Pass:

- forensic check events appear in runtime JSONL, not as passive rows in `PROVENANCE_LEDGER.md`.
- `mirrors_aligned` is `true` after reconciliation.

## V3 - Support Auth Gate

No token configured:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5173/api/camelot-os/support/activate -Body "{}" -ContentType "application/json"
```

Pass:

- returns `403` with `operator token required`.

With token configured:

```powershell
$env:CAMELOT_DASHBOARD_OPERATOR_TOKEN="REDACT"
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5173/api/camelot-os/support/activate -Headers @{"X-Camelot-Operator-Token"="REDACT"} -Body '{"reason":"verification"}' -ContentType "application/json"
```

Pass:

- returns active support session and one-time token.

## V4 - Vox Fallback

```powershell
.\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0, '01_KERNEL'); from senses.audio.vox_service import VoxService; print(VoxService().synthesize('hello', 'tasha', type('S', (), {'style':'neutral','speed':1,'texture':'clean'})())['engine'])"
```

Pass:

- command returns `KOKORO`, `PIPER`, or `SIMULATED`.
- Redis or Kitten cache failure does not abort synthesis.

## V5 - Dashboard

```powershell
cd C:\Users\vizio\CAMELOT_OS\02_FORGE\PORTAL_CORE\Anya_Dashboard
cmd /c npm run verify
```

Pass:

- TypeScript lint, Vitest, and Vite build pass.

## V6 - Architecture Docs

```powershell
cd C:\Users\vizio\CAMELOT_OS
.\.venv\Scripts\python.exe scripts\verify_architecture_docs.py
.\.venv\Scripts\python.exe -m pytest tests\test_architecture_docs.py
```

Pass:

- root `entiremap.md` and the L7 mirror hash to the same content.
- canonical architecture docs only point at live paths that exist in this checkout.
- the source-of-truth chain still records the banned stale anchors as stale, not as current truth.
