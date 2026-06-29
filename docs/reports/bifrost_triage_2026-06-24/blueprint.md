# Bifrost Bridge Triage — Remediation Blueprint

**Compiler:** Bifrost Audit / Hive Dispatch Cartridge
**Date:** 2026-06-24
**Source audit:** `docs/reports/bifrost_bridge_audit_2026-06-24` (this triage); prior `docs/reports/bifrost_bridge_audit_2026-05-22.md` (auth-gate cluster).
**Objective:** Convert the 5 dispatch-core findings into a guarded remediation that removes dead code, aligns the dispatch contract with its docstring, eliminates registry drift, makes the integration ledger honest, and closes the never-audited security gap on the dispatch surface — without broad refactors.

## Intent

The audit found that "Bifrost" is an overloaded brand spanning 6 components in 4 languages. The
auth-gate cluster (`bin/bifrost.py`, Rust `morgana_bridge`, Go sidecar, `apps/bifrost/`) was
already hardened by the 2026-05-22 audit. The **dispatch core** (`control_plane/bifrost.py`) —
the surface the Hive IDE actually runs prompts through — was never reviewed and carries 5 live
defects:

1. **Dead dispatch branches.** `_ENGINE_DISPATCH` only ever emits `cliproxy` / `sovereign` /
   `cloudbrain` / `noop`, but `stream()` still branches on `ollama` and `hermes`, making
   `_stream_ollama()` and the entire `_stream_hermes()` subprocess integration unreachable.
2. **Docstring/implementation drift.** The module docstring promises an `HTTP` strategy for
   custom-port services (`sir_octavian` :8400, `sir_sonus` :8300); no such strategy exists, so
   those terminals silently fall through to `cliproxy` / `claude-sonnet-4-6`.
3. **Registry drift.** `switchboard.py` registers 20 terminals; `_TERMINAL_MODEL` overrides only
   13. Seven terminals get no model mapping.
4. **Misleading ledger.** `bifrost_integration._forge_*` methods are stubs that `return True`
   while the ledger records `✓ Forged: bifrost.py`, etc.; also uses deprecated
   `datetime.utcnow()`.
5. **Unaudited security surface.** No caller auth on dispatch; hardcoded `CLIPROXY_KEY`
   fallback (`"proxy-admin-key"`); SSRF potential via env-driven base URLs; untrusted
   `enriched_system` injected into prompts.

The remediation must repair these without touching the auth-gate cluster or the existing root
remediation record.

## Severity Matrix

| ID | Finding | Severity | Blast radius | Reversible |
|----|---------|----------|--------------|------------|
| T1 | Dead `ollama`/`hermes` branches | Medium | `bifrost.py` only | Yes (pure deletion) |
| T2 | Missing `http` strategy | High | mis-routes 2 terminals to wrong backend | Yes |
| T3 | Registry/model drift | Medium | 7 terminals on defaults | Yes |
| T4 | Misleading forge ledger | Medium | audit-trail integrity | Yes |
| T5 | Unaudited dispatch security | High | all dispatch | Findings only (no code in this pass beyond hardening recs) |

## Target Architecture

### Dispatch strategy contract (post-fix)

Every value in `_ENGINE_DISPATCH` must have exactly one branch in `stream()`, and every branch
in `stream()` must be reachable from `_ENGINE_DISPATCH`. After remediation:

| Strategy | Branch | Backend | Engines mapped |
|----------|--------|---------|----------------|
| `cliproxy` | `_stream_openai` | CLIProxyAPI :8080 | claude_code, antigravity*, openai_codex, kimi_cli, hermes_cli |
| `sovereign` | `_stream_sovereign` | SIE in-process | sovereign, local_qwen, open_coder, local_audit, open_source |
| `cloudbrain` | `_query_cloudbrain` | NotebookLM | integration_brain |
| `http` *(new, T2)* | `_stream_http` | custom port (octavian :8400, sonus :8300) | (terminal-mapped) |
| `noop` | inline | n/a | local_ops, kitten_tts |

`ollama` + `hermes` branches and their `_stream_*` methods are **removed** (T1). The module
docstring is updated to describe only the strategies that exist.

### Registry alignment (T3)

`_TERMINAL_MODEL` is reconciled against `switchboard.TERMINAL_REGISTRY` (20 terminals). Each of
the 7 unmapped terminals (`sir_heimdall, sir_liberte, sir_octavian, sir_openclaw, sir_rustclaw,
sir_sonus, sir_zeroclaw`) is either given an explicit model or documented as intentional
engine-default fallback in a comment.

### Honest integration ledger (T4)

`bifrost_integration._forge_*` either performs real work or logs `↪ planned (no-op)` instead of
`✓ Forged`. Deprecated `datetime.utcnow()` → `datetime.now(timezone.utc)`.

## Swarm Knight Orchestration

Six-role kinetic swarm (`kinetic_swarm.py` role model) executes the plan. Roles dispatch through
the **real** `Bifrost` dispatcher; the simulated `_execute_via_agent` stub is bypassed.

| Swarm role | Knight (agent_id) | Bifrost terminal | Responsibility |
|------------|-------------------|------------------|----------------|
| coordinator | rustclaw | sir_rustclaw | Sequencing, dependency gating, run ledger |
| forge | hermes | sir_forge | Code fixes T1, T3 |
| architect | openclaw | sir_openclaw | Design T2, refactor T4 |
| sensor | apis | sir_alex | Regression watch, metrics |
| verifier | galahad | sir_sentinel | Run `verification.md` gates, T5 audit |
| executor | lancelot | (local apply) | Apply approved patches |

### Dependency / sequencing graph

```
T5 (security audit, informs scope) ─┐
                                     ├─► report
T1 (remove dead code) ──► T3 (reconcile registry) ──► T2 (add http strategy) ──► T4 (honest ledger)
```

T5 runs in parallel (read-only audit). T1→T3→T2 are serial on `bifrost.py` to avoid patch
conflicts. T4 is isolated to `bifrost_integration.py` and can run any time after T1.

### Apply mode — HITL gate

Knights **propose** unified diffs only. The orchestrator writes each diff to
`03_VAULT/runtime_state/bifrost_triage/<task_id>.diff` plus a run ledger, then PAUSES. Nothing
is applied to source until the operator approves (`--apply <task_id>`). On approval, the executor
applies and the verifier runs the matching `verification.md` gate, recording PASS/FAIL.

## Risk + Rollback

- All source edits are confined to `control_plane/bifrost.py` and
  `control_plane/bifrost_integration.py`. Both are version-controlled; rollback = `git checkout`.
- T1 is pure deletion of unreachable code — zero behavioral change to live paths.
- T2 is additive (new strategy); existing strategies unaffected.
- Proposed diffs are staged out-of-tree (VAULT) until approved, so a bad proposal never reaches
  source.
- Out of scope: the TS gateway, Rust `morgana_bridge`, Go sidecar (already audited 2026-05-22),
  and the completed root remediation record (`./blueprint.md` etc.).
