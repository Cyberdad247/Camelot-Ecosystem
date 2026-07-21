# CAMELOT OS Review Remediation Blueprint

**Compiler:** Anya Gate / Prompt Engineering Cartridge  
**Date:** 2026-05-14  
**Objective:** Convert the `/review` recommendations into a guarded implementation that preserves day-to-day Camelot commands, prevents passive checks from mutating canonical ledgers, gates break-glass support mutations, and keeps voice synthesis fallback resilient.

## Intent

The review found four live-risk surfaces:

1. `camelot` was redirected away from the full control-plane CLI.
2. forensic checks appended to `PROVENANCE_LEDGER.md` during read-only commands.
3. dashboard support mutation APIs could mint or revoke support sessions without an operator token.
4. Vox synthesis could fail before fallback if the Redis/Kitten cache path is unavailable.

The implementation must repair these without broad refactors or unrelated cleanup.

## Target Architecture

### 1. Command Surface Split

`camelot` remains the sovereign control-plane command:

- `camelot ledger status`
- `camelot codex status`
- `camelot team roster`
- `camelot cloudbrain ...`

`ks` and `knight-session` own the interactive OmniRoute knight router:

- `ks --list`
- `knight-session --route`
- `ks --knight sir_helio`

The lightweight `bin.camelot` wrapper may remain available for direct use, but it must not replace the control-plane CLI entrypoint.

### 2. Forensic Runtime Logging

Forensic checks are allowed during command intake, but read-only checks must write to runtime state:

`03_VAULT/runtime_state/forensic_checks.jsonl`

`PROVENANCE_LEDGER.md` is reserved for durable operator-significant events such as deployments, repairs, support activation, and ledger syncs.

### 3. Support Mutation Gate

Dashboard read APIs stay open to localhost users. Mutation APIs require an operator token:

- `/api/camelot-os/frontier-nodes/register`
- `/api/camelot-os/support/activate`
- `/api/camelot-os/support/revoke`

Accepted token source:

- environment variable `CAMELOT_DASHBOARD_OPERATOR_TOKEN`

Accepted header:

- `X-Camelot-Operator-Token`

If no token is configured, mutation APIs are disabled and return `403`.

### 4. Voice Fallback Contract

Kitten/Redis cache is an optimization, not a dependency. `VoxService.synthesize()` must continue to Kokoro/Piper/SIMULATED fallback if:

- `kitten_service` import fails
- Redis is unreachable
- cache payload is malformed
- cache lookup raises any exception

## Non-Goals

- Do not rewrite the dashboard UX.
- Do not delete or reorganize unrelated files.
- Do not repair the deleted Kinetic Edge MCP source in this pass unless explicitly requested.
- Do not add secrets to frontend code.

## Acceptance Criteria

- `camelot --json ledger status` succeeds.
- `camelot ledger status` succeeds.
- `camelot codex status` reaches the control-plane parser.
- `ks --list` succeeds.
- `knight-session --route` succeeds.
- read-only ledger status does not append a new root provenance row.
- dashboard verify passes.
- support activation without `CAMELOT_DASHBOARD_OPERATOR_TOKEN` returns `403`.
- Vox synthesis survives an unavailable Kitten/Redis path and reaches fallback.
