# Camelot Mission Control Hardening Tasks

## Track A: Restore `security.warden`

- [x] Create `security/__init__.py`.
- [x] Create `security/warden.py`.
- [x] Define `SecurityException` and `SecurityDecision`.
- [x] Implement `SecurityWarden.verify_permission(...)`.
- [x] Add allow rules for read/status/sync/config-audit commands.
- [x] Add approval-required rules for write/deploy/push/install commands.
- [x] Add deny rules for unsafe secret, credential, destructive, and unbounded filesystem actions.
- [x] Update `control_plane/camelot_cli.py` to use structured warden decisions.
- [x] Keep current missing-warden fallback only for low-risk status/sync commands.
- [x] Add tests for low-risk allow, risky block, and missing-module fallback behavior.

## Track B: Move Harness Heartbeats Out Of Provenance Ledger

- [x] Find the Harness code path that appends `Harness Heartbeat` rows to `PROVENANCE_LEDGER.md`.
- [x] Add a runtime heartbeat writer at `03_VAULT/runtime_state/harness_heartbeat.jsonl`.
- [x] Stop writing routine heartbeat ticks to `PROVENANCE_LEDGER.md`.
- [x] Add a material-state-change detector for events worth recording in the provenance ledger.
- [x] Preserve existing ledger append behavior for real governance events.
- [x] Update any dashboard/status readers to use the runtime heartbeat artifact.
- [x] Add `.gitignore` coverage if the heartbeat artifact is generated runtime state.
- [x] Verify normal Harness runtime does not dirty Git.

## Track C: Docs, Ledger, And Cloud Brain

- [x] Update the provenance ledger with the hardening completion entry.
- [x] Reconcile mirror ledgers.
- [x] Sync Cloud Brain after verification.
- [x] Confirm Cloud Brain queue remains `pending: 0`.
- [x] Commit and push the hardening pass.

