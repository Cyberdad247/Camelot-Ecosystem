# Bifrost Bridge Triage — Verification

**Compiler:** Bifrost Audit / Hive Dispatch Cartridge
**Date:** 2026-06-24

All commands assume `cd C:\Users\vizio\CAMELOT_OS`. Gates are grouped per task. A task passes
only when every assertion under its gate holds.

---

## V0 — Syntax (all touched files)

```bash
python -m py_compile control_plane/bifrost.py \
  control_plane/bifrost_integration.py \
  control_plane/bifrost_triage_swarm.py
```

**Pass:** exit 0, no output.

---

## V1 — Dead branches removed (T1)

```bash
# No dead strategy strings in stream() branches
grep -nE 'strategy == "(ollama|hermes)"' control_plane/bifrost.py || echo "OK: no dead branches"
# No unreachable stream helpers
grep -nE 'def _stream_(ollama|hermes)\b' control_plane/bifrost.py || echo "OK: helpers removed"
# Docstring no longer advertises removed strategies
grep -nE '^\s*-\s*(Ollama|Subprocess).*Hermes|Goose' control_plane/bifrost.py || echo "OK: docstring trimmed"
```

**Pass:** all three print `OK: …` (grep finds nothing).

---

## V2 — `http` strategy present and wired (T2)

```bash
# Strategy declared
grep -nE '"http"' control_plane/bifrost.py && echo "http declared"
# Branch handled
grep -nE 'strategy == "http"' control_plane/bifrost.py && echo "http branch present"
# Helper exists
grep -nE 'def _stream_http\b' control_plane/bifrost.py && echo "http helper present"
```

**Strategy-coverage invariant** (every declared strategy has a branch and vice-versa):

```bash
python - <<'PY'
import re, pathlib
src = pathlib.Path("control_plane/bifrost.py").read_text(encoding="utf-8")
declared = set(re.findall(r'\(\s*"(\w+)"\s*,', src))           # strategies in _ENGINE_DISPATCH tuples
declared &= {"cliproxy","sovereign","cloudbrain","noop","http","ollama","hermes"}
branched = set(re.findall(r'strategy == "(\w+)"', src))
branched |= {"cliproxy"}  # first `if` uses ==, captured above
missing_branch = declared - branched
dead_branch   = branched - declared
print("declared:", sorted(declared))
print("branched:", sorted(branched))
assert not missing_branch, f"strategy without branch: {missing_branch}"
assert not dead_branch,    f"branch without strategy: {dead_branch}"
print("OK: strategy coverage balanced")
PY
```

**Pass:** prints `OK: strategy coverage balanced`; `sir_octavian`/`sir_sonus` resolve to `http`
(see V-smoke).

---

## V3 — Registry/model drift reconciled (T3)

```bash
python - <<'PY'
import re, pathlib
bf = pathlib.Path("control_plane/bifrost.py").read_text(encoding="utf-8")
sb = pathlib.Path("control_plane/switchboard.py").read_text(encoding="utf-8")
registry = set(re.findall(r'\b(sir_[a-z]+)\b', sb))
# terminals mapped OR explicitly documented as fallback in a comment block
mapped = set(re.findall(r'"(sir_[a-z]+)"\s*:', bf))
documented = set(re.findall(r'#\s*fallback:\s*(sir_[a-z]+)', bf))
gap = registry - mapped - documented
print("registry:", len(registry), "mapped:", len(mapped), "documented:", len(documented))
assert not gap, f"unmapped & undocumented terminals: {sorted(gap)}"
print("OK: registry reconciled")
PY
```

**Pass:** prints `OK: registry reconciled`.

---

## V4 — Honest integration ledger (T4)

```bash
# No "Forged" success line emitted by a method whose body just returns True
grep -nE '✓ Forged' control_plane/bifrost_integration.py || echo "OK: no false Forged claims"
# Deprecated utcnow gone
grep -nE 'datetime\.utcnow\(\)' control_plane/bifrost_integration.py || echo "OK: utcnow removed"
grep -nE 'datetime\.now\(timezone\.utc\)' control_plane/bifrost_integration.py && echo "OK: tz-aware now"
```

**Pass:** `OK: no false Forged claims`, `OK: utcnow removed`, `OK: tz-aware now`.

---

## V5 — Security audit findings (T5)

This gate is satisfied by the **findings appendix below being filled in** (severity +
recommendation per item), not by code changes.

| # | Surface | Severity | Finding | Recommendation |
|---|---------|----------|---------|----------------|
| S1 | `CLIPROXY_KEY` default `"proxy-admin-key"` (bifrost.py:48) | **Medium** | Hardcoded fallback secret ships in source; if CLIProxy ever binds beyond loopback, the default key authenticates any caller. | Fail-closed: raise when `CLIPROXY_KEY` is unset rather than defaulting; source the key from `~/.camelot/` like `bin/bifrost.py`'s token. |
| S2 | `CLIPROXY_BASE` / `OLLAMA_BASE` / `SIR_*_BASE` env (bifrost.py:47,49) | **Low** | Base URLs are env-driven; a poisoned environment could redirect dispatch (SSRF) to an attacker host. Operator-controlled, not remote-reachable, so exposure is limited. | Default to loopback (already true); optionally allowlist schemes/hosts and reject non-loopback unless explicitly opted in. |
| S3 | `enriched_system` KB injection (bifrost.py:121-133) | **Medium** | `find_similar_dispatches` results are concatenated into the system prompt; a poisoned knowledge base becomes a prompt-injection vector. | Delimit untrusted context with explicit fences and a "treat as data, not instructions" preamble; cap injected length. |
| S4 | No caller auth on `Bifrost.stream` (bifrost.py:100) | **Medium** | The dispatch core trusts any in-process caller. Safe for local Python, but it is reached over the network via `mcp_conductor` / `agent_gateway`, where upstream gating is the only control. | Document the trust boundary; ensure every network-facing caller routes through `bin/bifrost.py verify_caller` before dispatch. |

**Overall:** the dispatch core assumes a *trusted in-process caller*; network exposure must be gated upstream by the `bin/bifrost.py` sovereign gate (already hardened, 2026-05-22). No High-severity issues on the dispatch surface itself. Hardening (S1–S4) is tracked separately from this triage.

**Pass:** every row's Severity ≠ _TBD_ and has a recommendation.

---

## V-smoke — No regression

```bash
python -m control_plane.bifrost --status
```

**Pass:** prints the terminal health table without traceback.

```bash
python -m control_plane.bifrost_triage_swarm --plan
```

**Pass:** prints 5 tasks mapped to 6 knights in dependency order, no dispatch.

---

## V-guard — Root record untouched

```bash
git status --porcelain blueprint.md tasks.md verification.md
```

**Pass:** no output (root artifacts unmodified).
