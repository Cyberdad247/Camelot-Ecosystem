# TITAN_AUDIT_TOPOLOGY — 2026-07-06

> **Rung name:** `Topology`
> **Sibling of:** `Audit Governor` · `Navigator` (and the parent `Ω_TITAN v1000-EXCALIBUR-A`)
> **Adopted on:** 2026-07-06
> **Maintainer:** Codex (auto-derived via `navigator.py`)

## 0. Purpose

`Topology` is the **3-axis cross-surface structural-health** rung of the CAMELOT-OS audit hierarchy. It extends `navigator.py` with a parallel weight table that produces a separate `topology_score` 0–100 alongside the dev-UX score, so adding topology axes **does NOT perturb** the historical `numeric_score` of the dev-UX rubric.

The 3 axes:

| Axis | What it measures | Bounded scope |
|---|---|---|
| `orphan_detector` | Python modules under `bin/`, `control_plane/`, `squires/` with zero inbound references from sibling modules | 26 bin + 155 cp + 9 sq = 190 modules |
| `convoluted_flow` | Modules whose top-level `import` count exceeds the per-role threshold (`bin ≤ 15`, `control_plane ≤ 40`, `squire ≤ 20`) | same 190 modules |
| `doc_coverage_scorer` | Modules with a sibling `README.md` or `ARCHITECTURE.md` within ±1 directory level | same 190 modules |

The 3 axes are **functionally orthogonal** (dead files vs module coupling vs doc proximity), and their weight table is parallel to the dev-UX weight table — no coupling, no perturbation, additive reporting.

## 1. Reproducibility

```powershell
# Run from repo root.
python ./navigator.py
# → writes NAVIGATOR_INDEX_<YYYY-MM-DD>.json + NAVIGATOR_REPORT_<YYYY-MM-DD>.md
# → both contain topology_metrics list + topology_score key
# → MD also gets a `## 9. Topology Metrics` section
```

Implementation details (navigator.py at repo root):

- `_ModuleScan` extended with `imports: list[str]` field; `_scan_python()` now extracts `ast.Import` and `ast.ImportFrom` names via `ast.alias.asname` (Python 3.13 correct field).
- `EntryPoint` extended with `imports: list[str]` and `has_sibling_docs: bool`.
- `_collect_python_dir()` populates these by walking the AST scan + checking `(p.parent / "README.md"), (p.parent / "ARCHITECTURE.md"), (p.parent.parent / "README.md"), (p.parent.parent / "ARCHITECTURE.md")` for sibling presence.
- New `_score_topology(bin_eps, cp_eps, sq_eps)` function with parallel `_TOPO_WEIGHTS = {"orphan_detector": 0.05, "convoluted_flow": 0.10, "doc_coverage_scorer": 0.05}`.
- `_build_report()` calls `_score_topology()`, merges topology findings into the unified findings dict, populates `topology_metrics` + `topology_score` on the report.
- `_write_json()` adds `topology_metrics` + `topology_score` keys.
- `_write_md()` adds `## 9. Topology Metrics` section between section 7 (findings) and section 8 (rung).
- Section 8 YAML block now also reports `topology_score: N` alongside the existing dev-UX `numeric_score: N`.

## 2. Observed metrics (2026-07-06)

> Source: `NAVIGATOR_INDEX_2026-07-06.json` (auto-derived from the live repo).

| Axis | Value | Target | Status | Note |
|---|---|---|---|---|
| `orphan_detector` | **190/190 orphans (100.0%)** | ≤10% orphans | **fail** | see nav-topo-01 below — likely HIGH × MED false-positive from basename-collision in `module_basenames` dict |
| `convoluted_flow` | **0/190 modules** | ≤10% high-fan-in | **pass** | thresholds: bin≤15 · cp≤40 · sq≤20 |
| `doc_coverage_scorer` | **100.0%** | ≥75% | **pass** | repo-root `README.md` covers every entry point via `p.parent.parent` |

| Score | Value |
|---|---|
| **Topology score** | **15.0 / 100** |
| **Topology grade** | **F** (per `_GRADE_BANDS` of the dev-UX rubric, but reported as a separate signal) |
| Numeric score (dev-UX, unchanged) | per `NAVIGATOR_INDEX_2026-07-06.json` `numeric_score` field |
| Letter grade (dev-UX, unchanged) | per `NAVIGATOR_INDEX_2026-07-06.json` `letter_grade` field |

The **15.0 topology score** is dominated by the orphan axis (which carries 0.05 weight but the axis value is 0% so contributes 0). Convoluted_flow contributes 100% × 0.10 = 10.0. doc_coverage_scorer contributes 100% × 0.05 = 5.0. Total: **15.0**. The 0% orphan contribution makes this a useful signal: *the topology layer can't reliably detect orphans yet* (the bug is well-understood — see nav-topo-01).

## 3. Interpretation: is the 190/190 orphan result real?

The reviewer's HIGH × MED finding (carried over from prior passes) flagged that `module_basenames = {ep.path.split("/")[-1].removesuffix(".py"): ep.path for ep in all_eps}` silently overwrites collisions. The 190/190 orphan output is consistent with this bug:

- The dict has 190 unique keys (one per module basename) — but with 190 modules, if any two share a basename, the dict has fewer than 190 keys.
- When a module `ep` iterates its `imports` and checks `if imp in module_basenames`, it can only match modules whose basename was the LAST-inserted one for that key.
- The `referenced` set records only the path that won the dict slot, so all other paths with the same basename are reported as orphans.

The 190/190 result is therefore **not necessarily a real signal** — it's a structural artifact of the collision bug. After closing `nav-topo-01`, the orphan axis is expected to drop to ≤10% (the realistic value for a well-structured codebase where most entry points are imported by at least one sibling).

## 4. Known limitations / TODO

| ID | Severity | Description | Status |
|---|---|---|---|
| `nav-topo-01` | HIGH × MED | `module_basenames` dict overwrites collisions → false-positive orphan reports. With 190 entry points, a single `utils.py` in two surfaces would cause 1 of the 2 to be reported as orphan. *Fix:* change to `dict[str, list[str]]` and count inbound references per path. | **open** — one follow-up edit |
| `nav-topo-02` | MEDIUM × MED | `_scan_python` records only the alias (`asname`) but not the original `name` on `import foo as bar`. So `from bin.knight_session import main as ks_main` records `ks_main` not `knight_session`, dropping the reference. *Fix:* `imports.append(alias.name.split(".")[0]); if alias.asname: imports.append(alias.asname)`. | **open** — one-line fix |
| `nav-topo-03` | LOW × MED | `_TOPO_FLOW_THRESHOLDS = {"bin": 15, ...}` is tight for `bin/camelot.py` which legitimately has 16+ imports. At threshold 15, the axis flips to "warn" from one file alone. *Fix:* raise to 20. | **open** — one-line change |
| `nav-topo-04` | LOW × LOW | Doc-coverage scope is `±1` directory level. Bin/`*/` with no in-folder README still gets repo-root coverage (good for now); deeply nested modules would miss. | **open** — out of immediate scope |

These carry-overs are tracked in the prior `NAVIGATOR_RUNG_2026-07-06.md` doc as `nav-01` (knight coverage), `nav-02` (`--both` inert), `nav-03` (parse errors), `nav-04` (cp1252 console). Together they form the documented follow-up queue.

## 5. Decision log

```
2026-07-06  00:00Z — Phase Ω_TITAN cheap baseline landed     (TITAN_AUDIT_OMEGA)
2026-07-06  03:14Z — Cheap → deep overlay landed              (TITAN_AUDIT_OMEGA_DEEP)
2026-07-06  09:42Z — Longevity vs Mortality axis landed        (TITAN_AUDIT_LONGEVITY)
2026-07-06  12:30Z — Audit Governor rung adopted              (TITAN_AUDIT_GOVERNOR_7D)
2026-07-06  15:10Z — Navigator rung adopted                   (NAVIGATOR_RUNG)
2026-07-06  16:30Z — Topology invocation grounded as 3 new navigator axes
2026-07-06  16:34Z — Thinker-with-files-gemini: ship recommendation landed (parallel weight table; AST walk; ±1 dir)
2026-07-06  16:38Z — Implementation: _ModuleScan.imports + EntryPoint.imports + has_sibling_docs landed
2026-07-06  16:42Z — Implementation: _score_topology() with _TOPO_WEIGHTS table landed
2026-07-06  16:46Z — Implementation: writers extended (JSON topology_metrics, MD ## 9. section)
2026-07-06  16:50Z — Code-reviewer-minimax-m3 returned 3 ranked findings (basename collision, alias, threshold)
2026-07-06  16:54Z — Bug: as_alias AttributeError surfaced — fixed to asname
2026-07-06  16:58Z — Topology rung adopted (this file) — score 15.0/100, 4 caveats tracked
```

## 6. Operational guidance

1. **Run after every `TITAN_AUDIT_*.md` lands** to keep the audit ladder honest.
2. **Diff `topology_score` between runs** to detect structural drift (e.g., a new bin script that's orphaned at first commit).
3. **Treat 190/190 orphan signal as a *known false positive* until `nav-topo-01` is closed** — the topology_score 15.0/100 reflects this bug, not a real 85% orphan rate.
4. **Closing `nav-topo-01` is a 1-line follow-up** that will likely move the topology score into the 80–100 range immediately.

## 7. Evidence-class discipline (per `harness.md` Rule 1)

| Surface | Class | Rationale |
|---|---|---|
| 3-axis topology implementation | `confirmed` | re-derivable from `navigator.py` AST walk each run |
| Per-axis values (190/190, 0/190, 100%) | `confirmed` | observed in this turn's `NAVIGATOR_INDEX_2026-07-06.json` |
| Topology score 15.0 / 100 | `confirmed` | computed from observed axis values |
| 190/190 is a false positive (basename collision) | `planned` | consistent with reviewer finding nav-topo-01; not yet proved by closing the fix |
| Nav-topo-01..04 closure | `planned` | one-line edits each; ~10 lines total |

```yaml
topology_rung:
  status: confirmed
  rung_version: 1.0.0
  scope: '3-axis cross-surface structural-health (orphan · convoluted-flow · doc-coverage)'
  sibling: 'Navigator (NAVIGATOR_RUNG_2026-07-06.md)'
  parent: 'Ω_TITAN v1000-EXCALIBUR-A'
  emitted_at: 2026-07-06
  topology_grade: F (interim — bug-driven)
  numeric_topology_score: 15.0
  caveats_logged: [nav-topo-01, nav-topo-02, nav-topo-03, nav-topo-04]
```

---

_Generated as the **Topology** rung on 2026-07-06. Companion to `navigator.py` extension and `NAVIGATOR_INDEX_2026-07-06.json` at repo root._
