# CAMELOT OS Review Remediation Tasks

**Compiler:** Anya Gate / Prompt Engineering Cartridge  
**Date:** 2026-05-14

## P0 - Command Surface

- [x] Restore `camelot` and `Camelot-OS` entrypoints to `control_plane.camelot_cli:main`.
- [x] Keep `ks` and `knight-session` pointed at `bin.knight_session:main`.
- [x] Decide whether `ai` should stay with the knight wrapper or control plane; prefer no regression for existing Camelot control-plane commands.
- [x] Verify `camelot --json ledger status`.
- [x] Verify `ks --list`.

## P0 - Ledger Safety

- [x] Change `ForensicEngine.log_check()` to append JSONL runtime events to `03_VAULT/runtime_state/forensic_checks.jsonl`.
- [x] Stop passive forensic checks from writing to `PROVENANCE_LEDGER.md`.
- [x] Reconcile provenance mirrors after the write-path fix.
- [x] Verify `mirrors_aligned: true`.

## P0 - Support Mutation Auth

- [x] Add `X-Camelot-Operator-Token` validation in `scripts/serve_anya_dashboard.py`.
- [x] Require `CAMELOT_DASHBOARD_OPERATOR_TOKEN` for support activate/revoke and node registration.
- [x] Return `403` when mutation is attempted without a configured token or with a bad token.
- [x] Update dashboard client to send the token only when provided by local operator environment/session storage.

## P1 - Vox Fallback

- [x] Wrap Kitten/Redis cache lookup in `VoxService.synthesize()`.
- [x] Ignore malformed cache hits and continue fallback.
- [x] Verify the fallback path with a forced failing Kitten import/cache call.

## P1 - Regression Verification

- [x] Run Python compile checks for touched Python files.
- [x] Run Anya Dashboard `npm run verify`.
- [x] Run CLI smoke checks for `camelot`, `ks`, and `knight-session`.
- [x] Record remaining known risks, especially deleted Kinetic Edge MCP source, without broad cleanup.

## P1 - Architecture Source Of Truth

- [x] Rebuild root `entiremap.md` from live runtime surfaces.
- [x] Sync `docs/SEPTEM_REGNA/L7_ETHEREAL/entiremap.md` to the root map.
- [x] Replace broken manifest mirrors with source-of-truth redirect docs.
- [x] Mark historical architecture docs as historical where they still contain stale path references.
- [x] Add a repo-local architecture doc validator and pytest check.
