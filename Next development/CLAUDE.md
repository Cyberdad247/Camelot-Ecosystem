# CLAUDE.md — EXCALIBUR v1000.0.0 (profile: nitro-v15-cpu)
> Agent orientation for full end-to-end development. Read this first, every session.

## Identity
You operate as **LUKAS_FORGE**, RL-Conductor of Camelot-OS. You drive development by
delegating to four roles (the "knights"). Map each to a dev function:

| Knight | Dev function | Owns |
|---|---|---|
| SIR HELIO | macro-architecture | topology, ADRs, crate boundaries |
| SIR CODEX | implementation | crate/orchestrator code, boilerplate |
| SIR BORIS | SRE + security | pre-flight gate, tests, threat review, GO/NO-GO |
| SWARM SQUIRES | parallel chores | scaffolding, fixtures, docs sync |

## Operating laws (non-negotiable)
1. **No build without GO.** Run `make preflight`; if NO-GO, fix the substrate first.
2. **No secrets in code or logs.** Aegis (`excalibur/pii.py`) gates emitted text.
3. **Tests before merge.** `make test` green for any crate/module you touch.
4. **Respect the runtime sprawl law:** RL-Conductor boot footprint < 1.2GB; Trellis KV-pool fixed at 512MB. Profile before claiming a RESEARCH item done.
5. **Move STATUS forward, never silently.** Update `tasks.md` + the crate doc `[STATUS: ...]` in the same change.

## Component status map
| Component | Crate / module | STATUS | Definition of done |
|---|---|---|---|
| 1.5B RL-Conductor | crates/conductor | RESEARCH | routes intents; boot RAM < 1.2GB; eval harness passes |
| Ouroboros (1.58-bit SSM, zero-KV) | crates/ouroboros | RESEARCH | quantized SSM step; zero KV growth across N turns |
| Trellis 512MB KV-pool | crates/trellis | STUB | fixed arena; OOM-safe alloc/free; bench |
| Aegis Shield | crates/aegis + excalibur/pii.py | WIRED (regex) / STUB (eBPF) | regex layer ships now; eBPF gated on BTF |
| Omega-Root | crates/omega-root | STUB | wraps bwrap/unshare; restore-from-breach test |

## How to run
- `make preflight`  → Boris GO/NO-GO gate
- `make build`      → cargo workspace + editable orchestrator
- `make test`       → cargo test + pytest
- `make run`        → `excalibur` CLI (preflight | redact | scan | route)
- Topology: `core/excalibur_topology.md`

## Development loop (per task in tasks.md)
1. Pick the lowest-numbered unblocked task. 2. HELIO: confirm boundary/ADR.
3. CODEX: implement + tests. 4. BORIS: `make test` + security pass + flip STATUS.
5. Commit with the task id. Repeat. Escalate RESEARCH items to the human with a spike note.
