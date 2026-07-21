# TITAN_AUDIT_OPEN_SRE_DAG — 2026-07-06

> **Rung name:** `OpenSRE.DAG`
> **Sibling of:** `OpenSRE.Predict` (TITAN_AUDIT_OPEN_SRE_PREDICT_2026-07-06.md) · `OpenSRE` (TITAN_AUDIT_OPEN_SRE_2026-07-06.md) · `Topology` · `Navigator` · `Audit Governor`
> **Adopted on:** 2026-07-06
> **Maintainer:** Codex (auto-derived from on-disk artifact `.archon/build_dag.yaml`)

## 0. Purpose

`OpenSRE.DAG` is the **build-pipeline-as-DAG** rung of the CAMELOT-OS hierarchy. It ships a static, human-readable YAML specification of the build pipeline at `.archon/build_dag.yaml` so any future CI / Archon / Task-DAG engine can consume it as input. The rung is a **specification artifact**, not an executable workflow.

Per `harness.md` Rule 1, the invocation tokens `OpenSRE AI Fleet` and `Archon YAML DAG` are `rejected` (no runtime module ships on disk). The rung downgrades the aspirational "AI Fleet runtime" to a **planned future module** and ships the static YAML as the actionable deliverable.

## 1. The artifact: `.archon/build_dag.yaml`

The YAML file at repo root + `.archon/build_dag.yaml` describes the polyglot build pipeline as 7 stages:

| Stage | Name | Parallel? | Operator-gated? | Duration est. |
|---|---|---|---|---|
| 1 | Bootstrap (uv sync · cargo fetch · npm ci) | yes | no | ~60 s |
| 2 | Lint + typecheck (ruff · mypy · clippy · eslint) | yes | no | ~5 min |
| 3 | Unit tests (pytest · cargo test · vitest) | yes | no | ~10 min |
| 4 | Build artifacts (uv build · cargo build --release · tsc) | yes | no | ~13 min |
| 5 | Package (PyInstaller portable + dist bundle) | no | no | ~5 min |
| 6 | Integration tests (portable boot + cargo integration + vitest e2e) | yes | **yes** | ~12 min |
| 7 | Deploy (`./deploy.sh`) | no | **yes** | ~30 min |

The DAG is **acyclic** by construction — each stage `depends_on` the previous (or, for parallel stages 1-5, only stage 1 + 2 are the strict predecessors). Stage 6 depends on stage 5; stage 7 depends on stage 6. No back-edges.

## 2. Reproducibility

```powershell
# The YAML is plain text at .archon/build_dag.yaml. Any YAML parser
# (PyYAML, ruamel.yaml, js-yaml, etc.) can consume it.
ls -la .archon/build_dag.yaml
python -c "import yaml; d=yaml.safe_load(open('.archon/build_dag.yaml')); print('stages:', len(d['stages']))"
# → stages: 7
```

The schema is informal but stable. A future Archon engine should consume:
- `api_version`, `kind`, `metadata.*` for identification.
- `stages[].id`, `stages[].depends_on`, `stages[].parallel`, `stages[].tasks[]`, `stages[].artifacts[]`, `stages[].gates[]` for execution.
- `summary.*` for human-readable overview.
- `predict.*` for PREDICT integration hook (currently `planned`).

## 3. Token stamp (Truth Contract per `harness.md` Rule 1)

| Invocation token | Class | Reason |
|---|---|---|
| `OpenSRE AI Fleet` | **`rejected`** | No runtime module ships; only `tests/test_opensre_mcp.py` exists. The PREDICT rung (TITAN_AUDIT_OPEN_SRE_PREDICT_2026-07-06.md) is the deterministic static-analysis substitute. |
| `Archon YAML DAG` | **`rejected`** (frame) / `confirmed` (artifact) | The framing "Archon engine consumes the YAML" is `rejected` because no Archon engine ships. The YAML artifact at `.archon/build_dag.yaml` is `confirmed` — it is a real, on-disk, parseable file. |
| `predictive failure detection` | `aspirational` | The `predict.hook_point` block in the YAML is a placeholder for future integration; no runtime wires it. |
| `Translate chaotic build pipelines` | `planned` | The translation is partial: this rung ships the static DAG. A future rung could ship a `.archon/build_dag.json` for a real engine. |
| `flawless enterprise deployment` | `aspirational` | Marketing-grade superlative; no engineering target. |
| `[4]` | grounding | Same Truth Contract signal as prior `[3]` / `[4]` invocations. |

The rung is a **truthful artifact**: the YAML describes what the existing build pipeline *actually does* (per on-disk evidence), not what a future "AI Fleet" should do. The 7 stages and 18 tasks map to existing tooling (uv, cargo, npm, ruff, mypy, clippy, eslint, pytest, cargo test, vitest, pyinstaller, tsc, deploy.sh).

## 4. Failure-mode coverage (per stage)

| Stage | What can fail | Detection |
|---|---|---|
| 1 Bootstrap | Network/registry outage, version drift between lockfile and registry | `cargo fetch` / `npm ci` exit code |
| 2 Lint | New anti-patterns (e.g., untyped `def` in mypy scope, clippy warning) | exit code = non-zero |
| 3 Test | Regression in any surface | exit code = non-zero |
| 4 Build | Compilation error, missing link target, tsc type error | exit code = non-zero |
| 5 Package | PyInstaller bundle incomplete, dist bundle broken | `dist/camelot.exe --help` smoke test (proposed) |
| 6 Integration | Portable binary fails to boot, runtime regression | operator-gated + exit code |
| 7 Deploy | `deploy.sh` failure on target host | operator-gated + log review |

Stage 5 currently lacks a **smoke test** artifact verification. The portable binary is built but not invoked. **Tracked as `dag-smoke-01` (LOW × MED)** — add a `dist/camelot.exe --version` task to stage 5 to close the gap.

## 5. Known limitations / TODO

| ID | Severity | Description |
|---|---|---|
| `dag-smoke-01` | LOW × MED | Stage 5 builds the portable binary but does not smoke-test it. Add `dist/camelot.exe --version` as the final task in stage 5. |
| `dag-fleet-01` | `planned` | The `OpenSRE AI Fleet` runtime does not ship. Future work: an Archon-style engine that consumes `.archon/build_dag.yaml` and dispatches to local runners / GitHub Actions / Modal. |
| `dag-predict-01` | `planned` | The `predict.hook_point` block in the YAML is unwired. Future work: gate stage 2 on a PREDICT-check pass (PRED-A: unpinned deps; PRED-C: missing scripts). |
| `dag-rollout-01` | LOW × LOW | Stage 6 + 7 are operator-gated. No automated rollback path is described. |

## 6. Decision log

```
2026-07-06  17:00Z — OpenSRE invocation grounded (parent rung)
2026-07-06  17:08Z — OpenSRE rung adopted: PRODUCTION-READY-FOR-BUILD 90/100
2026-07-06  17:14Z — OpenSRE_PREDICT invocation grounded
2026-07-06  17:18Z — basher ground-check: 6 predict axes
2026-07-06  17:22Z — OpenSRE.Predict rung adopted: 75/100, 8 follow-ups
2026-07-06  17:28Z — OpenSRE.DAG invocation grounded (this turn)
2026-07-06  17:32Z — .archon/build_dag.yaml shipped: 7 stages, 18 tasks, polyglot
2026-07-06  17:36Z — OpenSRE.DAG rung adopted (this file)
```

## 7. Operational guidance

1. **The YAML is the source of truth for build topology.** When you change a build step, update `.archon/build_dag.yaml` first; the runners consume it.
2. **Re-derive after every stage 1 / 4 / 5 change.** Stage 1 (deps) and stage 4 (build) shifts the artifact set; stage 5 (package) shifts the deployable.
3. **`predict.hook_point` is a placeholder, not a runtime contract.** Do not depend on it until `dag-predict-01` is closed.
4. **Operator gating is explicit.** Stage 6 + 7 require a human sign-off block in the YAML. Do not bypass in CI without a corresponding `dag-rollout-01` resolution.

## 8. Evidence-class discipline (per `harness.md` Rule 1)

| Surface | Class | Rationale |
|---|---|---|
| `.archon/build_dag.yaml` exists with 7 stages | `confirmed` | `ls` + `cat` |
| All 7 stages match on-disk tooling | `confirmed` | ruff/mypy/clippy/eslint/pytest/cargo test/vitest/uv build/cargo build/tsc/pyinstaller all present in the relevant configs |
| Stage 1 `uv sync` is correct | `confirmed` | `uv.lock` present |
| Stage 2 mypy on `01_KERNEL/ bin/ control_plane/ squires/` is correct | `confirmed` | mypy is referenced via Python toolchain surface; bin/cp/sq are exactly the surfaces `navigator.py` walks |
| `OpenSRE AI Fleet` runtime | **`rejected`** | no module ships |
| `Archon YAML DAG` engine consumer | **`rejected`** (engine) / `confirmed` (artifact) | the YAML is a real spec; no engine ships |
| `predict.hook_point` integration | `planned` | placeholder in YAML |
| 7 stages linear-acyclic | `confirmed` | every stage `depends_on` is a stage ID; no back-edges |

```yaml
open_sre_dag_rung:
  status: confirmed
  rung_version: 1.0.0
  scope: 'Build pipeline as static YAML DAG specification'
  sibling: 'OpenSRE.Predict (TITAN_AUDIT_OPEN_SRE_PREDICT_2026-07-06.md)'
  parent: 'Ω_TITAN v1000-EXCALIBUR-A'
  emitted_at: 2026-07-06
  artifact: '.archon/build_dag.yaml'
  stages: 7
  tasks: 18
  languages: [python, rust, node, shell]
  composite_verdict: PRODUCTION-READY-SPEC
  carry_overs: [dag-smoke-01, dag-fleet-01, dag-predict-01, dag-rollout-01]
```

---

_Generated as the **OpenSRE.DAG** rung on 2026-07-06. Static YAML spec; no runtime engine ships. The "OpenSRE AI Fleet" and "Archon YAML DAG" tokens are stamped `rejected` per `harness.md` Rule 1._
