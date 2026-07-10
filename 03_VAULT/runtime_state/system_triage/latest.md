# CAMELOT-OS System Triage

- Generated: `2026-07-02T18:12:43.920197+00:00`
- Root: `C:\Users\vizio\CAMELOT_OS`
- Mode: `rapid`
- Verdict: **BLOCKED**

| Check | Stage | Required | Evidence class | Status | Summary |
|---|---|---:|---|---|---|
| repository-fingerprint | rapid | yes | confirmed | PASS | Git state captured; 192 changed or untracked entries |
| source-of-truth | rapid | yes | confirmed | PASS | Canonical files present |
| excalibur-preflight | rapid | yes | confirmed | PASS | EXCALIBUR substrate verdict: GO |
| required-boot-contract | rapid | yes | confirmed | PASS | Required boot phases are declared |
| bio-swarm-runtime | rapid | yes | confirmed | PASS | Bio-Swarm spawner binary and release evidence are present |
| targeted-control-plane-tests | rapid | yes | confirmed | FAIL | Targeted architecture tests failed |
| rust-kernel-compile | rapid | yes | confirmed | PASS | Aegis and Ouroboros compile |
| security-hitl-contract | rapid | yes | confirmed | PASS | Adaptive HITL and HUMAN_GATE contracts are present |
| verification-ledger-integrity | rapid | yes | confirmed | PASS | Verification ledger chain valid (688 entries) |
| provenance-ledger-alignment | rapid | yes | confirmed | FAIL | Ledger mirrors are not aligned |
| notebooklm-live | rapid | yes | confirmed | UNVERIFIED | NotebookLM live check failed: ConnectError |
| excalibur-cloudbrain-health | rapid | yes | confirmed | UNVERIFIED | Cloud Brain health check failed: URLError |
| cloudbrain-sync-queue | rapid | no | confirmed | WARN | 5 queued Cloud Brain event(s) |
| aspirational-v1000-claims | rapid | no | aspirational | WARN | Aspirational architecture claims remain non-blocking pending reproducible evidence |
| planned-v1000-capabilities | rapid | no | planned | SKIP | Planned capabilities are recorded but do not affect runtime readiness |
| rejected-legacy-architecture | rapid | no | rejected | PASS | Legacy v999-only architecture is excluded from release gates |
| tracked-source-read-only-guard | guard | yes | confirmed | PASS | No pre-existing tracked changes were altered |

## Remediation
- **targeted-control-plane-tests:** Run the failing test nodes individually and repair before deep validation.
- **provenance-ledger-alignment:** Review differences, then run `camelot ledger reconcile` under an approved change window.
- **notebooklm-live:** Run `nlm login`, then rerun `camelot triage --rapid`.
- **cloudbrain-sync-queue:** Inspect with `camelot cloudbrain queue status`; flush only after authentication and review.

## Evidence Policy

NotebookLM defines architectural intent. A capability is operational only when live repository code, commands, tests, endpoints, or artifacts prove it.
