# Camelot Mission Control Hardening Tasks

## Track A: Restore `security.warden`

- [ ] Create `security/__init__.py`.
- [ ] Create `security/warden.py`.
- [ ] Define `SecurityException` and `SecurityDecision`.
- [ ] Implement `SecurityWarden.verify_permission(...)`.
- [ ] Add allow rules for read/status/sync/config-audit commands.
- [ ] Add approval-required rules for write/deploy/push/install commands.
- [ ] Add deny rules for unsafe secret, credential, destructive, and unbounded filesystem actions.
- [ ] Update `control_plane/camelot_cli.py` to use structured warden decisions.
- [ ] Keep current missing-warden fallback only for low-risk status/sync commands.
- [ ] Add tests for low-risk allow, risky block, and missing-module fallback behavior.

## Track B: Move Harness Heartbeats Out Of Provenance Ledger

- [ ] Find the Harness code path that appends `Harness Heartbeat` rows to `PROVENANCE_LEDGER.md`.
- [ ] Add a runtime heartbeat writer at `03_VAULT/runtime_state/harness_heartbeat.jsonl`.
- [ ] Stop writing routine heartbeat ticks to `PROVENANCE_LEDGER.md`.
- [ ] Add a material-state-change detector for events worth recording in the provenance ledger.
- [ ] Preserve existing ledger append behavior for real governance events.
- [ ] Update any dashboard/status readers to use the runtime heartbeat artifact.
- [ ] Add `.gitignore` coverage if the heartbeat artifact is generated runtime state.
- [ ] Verify normal Harness runtime does not dirty Git.

## Track C: Docs, Ledger, And Cloud Brain

- [ ] Update the provenance ledger with the hardening completion entry.
- [ ] Reconcile mirror ledgers.
- [ ] Sync Cloud Brain after verification.
- [ ] Confirm Cloud Brain queue remains `pending: 0`.
- [ ] Commit and push the hardening pass.

