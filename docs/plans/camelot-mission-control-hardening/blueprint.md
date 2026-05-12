# Camelot Mission Control Hardening Blueprint

Generated: 2026-05-12

## Objective

Turn the next Camelot hardening pass into two concrete upgrades:

1. Restore a real `security.warden` Iron Gate so risky commands are governed by an explicit permission engine instead of fallback logic.
2. Move Harness heartbeat noise out of `PROVENANCE_LEDGER.md` so the canonical ledger records decisions and material events, not constant runtime ticks.

## Alex Skepticism: Operator Experience

Alex's concern is that Mission Control cannot feel trustworthy if the command surface behaves differently depending on which optional module happens to exist.

Current risk:

- `camelot cloudbrain sync` works only because the CLI now allows low-risk sync/status commands when `security.warden` is missing.
- That fallback is acceptable as a temporary bridge, but it is not a complete governance model.
- Harness heartbeat rows make `PROVENANCE_LEDGER.md` noisy, which makes humans less likely to read it and makes real changes harder to spot.

Alex's design requirement:

- The operator should see one clear status: `Iron Gate: active`, `degraded`, or `blocked`.
- The ledger should read like a decision history, not a process log.
- Mission Control should expose heartbeat health from runtime state files or dashboard panels, not by rewriting the canonical provenance ledger every few minutes.

## Octavian Skepticism: Security And Operations

Octavian's concern is that fallback security can become accidental policy.

Current risk:

- Missing `security.warden` creates a blind spot unless the replacement module defines hard allow/deny rules.
- Low-risk fallback must stay narrow and test-covered.
- Heartbeat writes to a tracked ledger create dirty worktrees, merge churn, and possible sync loops.

Octavian's governance requirement:

- Risky verbs such as delete, remove, purge, reset, secret, key, credential, token, payment, and deploy must remain blocked when the warden is unavailable.
- The warden must emit structured decisions: allow, deny, require approval.
- Harness heartbeat must be append-only runtime telemetry under `03_VAULT/runtime_state/` or `logs/`, with summarized ledger entries only when state materially changes.

## Proposed Architecture

### 1. `security.warden`

Create `security/warden.py` with:

- `SecurityException`
- `SecurityDecision`
- `SecurityWarden.verify_permission(...)`
- a singleton `warden`
- risk classification for command intents
- structured reasons suitable for CLI, dashboard, and verification logs

Decision model:

| Decision | Meaning | Behavior |
| --- | --- | --- |
| `allow` | Low-risk status/read/sync operation | Continue |
| `require_approval` | Material write, deploy, credential, external push | Prompt in interactive shells; block in non-interactive shells unless preapproved |
| `deny` | Secret exfiltration, destructive cleanup without target boundary, unsafe shell | Block |

### 2. Harness Heartbeat Relocation

Change Harness heartbeat writes from `PROVENANCE_LEDGER.md` to a runtime artifact:

- preferred: `03_VAULT/runtime_state/harness_heartbeat.jsonl`
- acceptable: `logs/harness_heartbeat.jsonl`

Ledger policy:

- Write to `PROVENANCE_LEDGER.md` only when a heartbeat state crosses a threshold, such as `GREEN -> DEGRADED`, failed probes increase, or a service recovers.
- Keep mirror ledgers reconciled only after canonical ledger events, not every runtime tick.

## Mission Control Outcome

After this hardening pass, Mission Control should have:

- deterministic Iron Gate behavior
- clean low-risk sync/status flows
- blocked risky flows when security is unavailable
- stable Git worktree during normal runtime
- readable provenance ledgers
- runtime heartbeat available without ledger spam

