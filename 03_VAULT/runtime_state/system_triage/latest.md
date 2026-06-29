# CAMELOT-OS System Triage

- Generated: `2026-06-21T07:57:05.860476+00:00`
- Root: `C:\Users\vizio\CAMELOT_OS`
- Mode: `rapid`
- Verdict: **DEGRADED**

| Check | Stage | Required | Evidence class | Status | Summary |
|---|---|---:|---|---|---|
| repository-fingerprint | rapid | yes | confirmed | PASS | Git state captured; 58 changed or untracked entries |
| source-of-truth | rapid | yes | confirmed | PASS | Canonical files present |
| excalibur-preflight | rapid | yes | confirmed | PASS | EXCALIBUR substrate verdict: GO |
| required-boot-contract | rapid | yes | confirmed | PASS | Required boot phases are declared |
| targeted-control-plane-tests | rapid | yes | confirmed | PASS | Targeted architecture tests passed |
| rust-kernel-compile | rapid | yes | confirmed | PASS | Aegis and Ouroboros compile |
| security-hitl-contract | rapid | yes | confirmed | PASS | Adaptive HITL and HUMAN_GATE contracts are present |
| verification-ledger-integrity | rapid | yes | confirmed | PASS | Verification ledger chain valid (380 entries) |
| provenance-ledger-alignment | rapid | yes | confirmed | PASS | Ledger mirrors aligned |
| notebooklm-live | rapid | yes | confirmed | PASS | NotebookLM reachable: Camelot-OS v.1000 (0 sources) |
| excalibur-cloudbrain-health | rapid | yes | confirmed | PASS | Long-term Excalibur Cloud Brain is alive |
| cloudbrain-sync-queue | rapid | no | confirmed | PASS | 0 queued Cloud Brain event(s) |
| aspirational-v1000-claims | rapid | no | aspirational | WARN | Aspirational architecture claims remain non-blocking pending reproducible evidence |
| planned-v1000-capabilities | rapid | no | planned | SKIP | Planned capabilities are recorded but do not affect runtime readiness |
| rejected-legacy-architecture | rapid | no | rejected | PASS | Legacy v999-only architecture is excluded from release gates |
| tracked-source-read-only-guard | guard | yes | confirmed | PASS | No pre-existing tracked changes were altered |

## Evidence Policy

NotebookLM defines architectural intent. A capability is operational only when live repository code, commands, tests, endpoints, or artifacts prove it.
