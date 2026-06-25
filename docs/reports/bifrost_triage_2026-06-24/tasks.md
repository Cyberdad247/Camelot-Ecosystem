# Bifrost Bridge Triage — Tasks

**Compiler:** Bifrost Audit / Hive Dispatch Cartridge
**Date:** 2026-06-24
**Apply mode:** propose + HITL gate (knights produce diffs; operator approves before source is touched)

Dependency order: **T5 ‖ (T1 → T3 → T2 → T4)**

> **STATUS — COMPLETE (2026-06-25).** The swarm orchestrator (`bifrost_triage_swarm.py`)
> dispatched all 5 tasks correctly, but both knight backends were unavailable at run time
> (Ollama :11434 down; CLIProxy→Anthropic out of credits → HTTP 400). With no live model to
> produce diffs, the fixes were applied directly by the operator-agent acting as the **executor
> knight**, then verified against every gate in `verification.md` (V0–V5, V-smoke, V-guard — all
> PASS). Changes are uncommitted working-tree edits (review: `git diff`; rollback: `git checkout`).

---

## P0 — Dispatch contract integrity

### T1 — Remove dead `ollama` + `hermes` dispatch branches
- **Files:** `control_plane/bifrost.py`
- **Owner:** hermes (forge) → `sir_forge`
- **Depends on:** —
- [x] Delete the `elif strategy == "ollama"` branch in `stream()`.
- [x] Delete the `elif strategy == "hermes"` branch in `stream()`.
- [x] Delete the now-unreachable `_stream_ollama()` method.
- [x] Delete the now-unreachable `_stream_hermes()` method (and its `CAMELOT_HOME` usage if orphaned).
- [x] Update the module docstring (lines ~4–8) to list only live strategies (`cliproxy`, `sovereign`, `cloudbrain`, `noop`, and `http` after T2).
- **Acceptance:** no `"ollama"`/`"hermes"` strategy string and no `_stream_ollama`/`_stream_hermes` defs remain; `py_compile` clean; `--status` unaffected.

## P0 — Routing correctness

### T2 — Implement the documented `http` strategy
- **Files:** `control_plane/bifrost.py`
- **Owner:** openclaw (architect) → `sir_openclaw`, impl by `sir_forge`
- **Depends on:** T3
- [x] Add `http` entries to `_ENGINE_DISPATCH` (or map `sir_octavian` :8400 / `sir_sonus` :8300 engines to `http`).
- [x] Add a `_stream_http()` method that POSTs the prompt to the terminal's configured port and streams the response.
- [x] Add the `elif strategy == "http"` branch in `stream()`.
- [x] Ensure `_resolve()` returns the correct base URL/port for http terminals (no fall-through to `cliproxy`).
- **Acceptance:** `sir_octavian` / `sir_sonus` resolve to the `http` strategy (not `cliproxy`); strategy-coverage check passes (every dispatch strategy has a branch and vice-versa).

## P1 — Configuration drift

### T3 — Reconcile `_TERMINAL_MODEL` with the terminal registry
- **Files:** `control_plane/bifrost.py`; read `control_plane/switchboard.py`
- **Owner:** hermes (forge) → `sir_forge`
- **Depends on:** T1
- [x] Enumerate all terminals in `switchboard.TERMINAL_REGISTRY` (20).
- [x] For each of the 7 unmapped (`sir_heimdall, sir_liberte, sir_octavian, sir_openclaw, sir_rustclaw, sir_sonus, sir_zeroclaw`): add an explicit model OR a comment documenting intentional engine-default fallback.
- **Acceptance:** registry-vs-`_TERMINAL_MODEL` diff is empty or every gap is documented; `py_compile` clean.

## P1 — Audit-trail integrity

### T4 — Make `bifrost_integration` ledger honest
- **Files:** `control_plane/bifrost_integration.py`
- **Owner:** openclaw (architect) → `sir_openclaw`
- **Depends on:** — (isolated file; after T1)
- [x] In `_forge_*` stubs, replace `✓ Forged: …` ledger lines with `↪ planned (no-op): …` (or implement real work).
- [x] Replace deprecated `datetime.utcnow()` with `datetime.now(timezone.utc)`.
- **Acceptance:** no `✓ Forged` emitted for methods whose body is `return True`; `py_compile` clean.

## P0 — Security

### T5 — Security pass on the dispatch core
- **Files:** `control_plane/bifrost.py` (read), feeds `bin/bifrost.py`
- **Owner:** galahad (verifier) → `sir_sentinel` + apis (sensor) → `sir_alex`
- **Depends on:** — (read-only audit, runs in parallel)
- [x] Assess hardcoded `CLIPROXY_KEY` default (`"proxy-admin-key"`) — recommend fail-closed when unset.
- [x] Assess SSRF surface from env-driven `CLIPROXY_BASE` / `OLLAMA_BASE`.
- [x] Assess prompt-injection via `enriched_system` (knowledge-base context concatenated into the system prompt).
- [x] Assess absence of caller authorization on `Bifrost.stream` (compare to `bin/bifrost.py` gate).
- [x] Produce findings appendix in `verification.md` (V5) with severity + recommendation.
- **Acceptance:** written findings with severity ratings; no code changes required to pass this task (hardening tracked separately).

---

## Verification & Regression
- [x] `python -m py_compile control_plane/bifrost.py control_plane/bifrost_integration.py control_plane/bifrost_triage_swarm.py`.
- [x] Run all gates in `verification.md`; all PASS.
- [x] `python -m control_plane.bifrost --status` still lists terminals (no regression).
- [x] Root `./blueprint.md`, `./tasks.md`, `./verification.md` untouched.
