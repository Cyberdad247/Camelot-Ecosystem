# NAVIGATOR RUNG — 2026-07-06

> **Rung name:** `Navigator`
> **Sibling of:** `Audit Governor` (TITAN_AUDIT_GOVERNOR_7D_2026-07-06.md)
> **Sibling of:** `Ω_TITAN v1000-EXCALIBUR-A` (the parent audit hierarchy)
> **Adopted on:** 2026-07-06
> **Maintainer:** Codex (auto-derived via `navigator.py`)

## 0. Purpose

`Navigator` is the **cross-surface dev-UX + project-navigation** rung of the CAMELOT-OS audit hierarchy. It produces a reproducible index of:

1. **Entry points** under `bin/`, `control_plane/`, `squires/` — first line, classes, functions, version, docstring, banner.
2. **Runic dispatch** — `RUNIC_COMMANDS` and `OMEGA_RUNES` parsed from `control_plane/runic_router.py`.
3. **Knight surface** — every persona sheet under `03_VAULT/Knights/**/`.
4. **Audit ladder** — every `TITAN_AUDIT_*.md` plus the `NAVIGATOR_RUNG_*.md` already shipped.
5. **Canonical docs** — AGENTS.md, .agent/system_instructions.md, harness.md, UNIVERSAL_BOOTSTRAP_UKG_NANO.md, SYSTEM_PERSONAS_CRYSTAL.md.
6. **Dev-UX metrics** — 11-axis weighted scoring: docstring coverage, banner presence, rune handler resolvability, audit-chain completeness, doc/code ratio, file-size ceiling, agent-references-in-docs, discoverability smoke.
7. **Findings** — row-level list under each failing axis for operator triage.

Target operator objectives (from the original request): *assess developer UX, code readability, and project navigation*.

## 1. Reproducibility

```powershell
# Run from repo root.
python ./navigator.py
# → writes NAVIGATOR_INDEX_<YYYY-MM-DD>.json + NAVIGATOR_REPORT_<YYYY-MM-DD>.md
```

CLI surface (after the 4th review pass, ship-ready):

| Flag | Purpose |
|---|---|
| `--json-only` | Write only the JSON index (mutex with `--md-only`, `--both`) |
| `--md-only` | Write only the Markdown report (mutex with `--json-only`, `--both`) |
| `--both` | (default) Write both |
| `--out-dir DIR` | Output directory (default: `.`) |
| `--rune NAME` | Resolve a single rune — accepts `FORGE`, `//FORGE`, `Omega_Boris`, `boris` (normalized bidirectionally) |
| `--knight SUBSTR` | Find persona sheets matching substring |
| `--surface {bin,cp,sq,knights,docs,audit,all}` | Limit scope (default: `all`) |
| `--version` | Print version + rung and exit |
| `--help` | argparse help, all three mode flags visible |

Stdlib-only. No `import` of any project module. AST-parse only. Never exec. Single-file: `navigator.py` (~700 LoC).

## 2. Observed metrics (2026-07-06)

> Source: `NAVIGATOR_INDEX_2026-07-06.json` (auto-derived from the live repo).

| Axis | Value | Source class |
|---|---|---|
| **Numeric score** | **67.7 / 100** | computed |
| **Letter grade** | **D** | computed |
| Canonical files (`.colony/index.json`) | **46,719** | confirmed |
| Canonical lines | **11,346,662** | confirmed |
| Canonical symbols | **197,770** | confirmed |
| `bin/*.py` modules | **26** | confirmed |
| `control_plane/*.py` modules | **155** | confirmed |
| `squires/*.py` modules | **9** | confirmed |
| `RUNIC_COMMANDS` | **25** | confirmed (regex-parse of `control_plane/runic_router.py`) |
| `OMEGA_RUNES` | **32** | confirmed (regex-parse) |
| Knight sheets | **159** across **18 surfaces** | confirmed (walk of `03_VAULT/Knights/**`) |
| Audit ladder entries | **4** `TITAN_AUDIT_*.md` + **1** `NAVIGATOR_RUNG_*.md` (this file) | confirmed (root glob) |

### Knight surface breakdown

| Surface | Sheets |
|---|---|
| Creative | 20 |
| Engineering | 29 |
| Finance | 1 |
| Governance | 7 |
| Growth | 1 |
| Kinetic | 1 |
| Memory | 2 |
| Monitoring | 2 |
| Perception | 1 |
| Reasoning | 3 |
| Research | 2 |
| Security | 2 |
| Strategy | 1 |
| Substrate | 1 |
| `sir_forge` / `sir_openclaw` / `sir_sentinel` | 2 each |
| `souls` / `sparks` | 40 each |

### Audit ladder

| File | Verdict | Score |
|---|---|---|
| TITAN_AUDIT_OMEGA_2026-07-06.md (cheap baseline) | STABLE | 84/100 |
| TITAN_AUDIT_OMEGA_DEEP_2026-07-06.md (cheap → deep) | RADIANT | 88/100 |
| TITAN_AUDIT_LONGEVITY_2026-07-06.md | RADIANT-PENDING | 87/100 |
| TITAN_AUDIT_GOVERNOR_7D_2026-07-06.md | PRODUCTION-READY | 90/100 |
| **NAVIGATOR_RUNG_2026-07-06.md** (this rung) | **NAVIGATOR-READY** | **67.7/100** |

## 3. Score interpretation

The **D / 67.7** grade is honest: navigator.py was rushed through 4 review passes to close HIGH × HIGH (argparse duplicate-flag crash), HIGH × MED (Omega-bare-name regression), `SyntaxWarning` (invalid escape sequences in docstrings), and `--help` default-mention gulf. The metric weights the **rune handler resolvability** and **audit-chain completeness** axes very high (0.20 each), and the early-implementation passes had incomplete audit-chain coverage. As more `TITAN_AUDIT_*.md` files land with explicit `Verdict:` + `score: N/100` lines, the chain-completeness axis rises.

This is a **tool score**, not a **codebase score**. The 11-axis rubric measures how navigable the project *is via this very tool*. A high grade here does not mean the codebase is healthy; it means the navigator reliably reflects what's on disk.

## 4. Known limitations (tracked for follow-up)

| ID | Severity | Description | Status |
|---|---|---|---|
| `nav-01` | HIGH × MED | `--knight` resolver misses personas whose IDs are not in the `^[A-Z][a-z]+_[A-Z][a-z]+` shape (dashed forms like `OMEGA-3D`, single-word `BOB`, numeric `KNIGHT_2`). Falls back to substring against `name` only, no `03_VAULT/Knights/**/*.md` filesystem crawl. | **open** — exceeds 10-net-line iron-gate budget; tracked. |
| `nav-02` | MEDIUM × MED | `--both` flag is **documented in `--help`** but is **inert at the write-gate layer**. A user invoking `--both` writes the same artifacts as omitting all mode flags (the default already writes both). No behavioral regression — only a UX redundancy. | **open** — cosmetic; one-line cleanup. |
| `nav-03` | LOW × MED | `_scan_python` swallows `SyntaxError` and returns an empty scan indistinguishable from a zero-symbol file. No `validation.n_files_with_parse_errors` counter in the JSON for the operator to spot broken files without re-walking. | **open** — tracked; needs `parse_error` + `line_no` threading. |
| `nav-04` | LOW × LOW | Windows-cp1252 consoles cannot display the Unicode em-dashes / smart quotes in the report. UTF-8 file on disk is correct; only operator-side display is affected. | **open** — by-design; the export is UTF-8 with `errors=replace`. |

## 5. Decision log

```
2026-07-06  00:00Z — Phase Ω_TITAN cheap baseline landed     (TITAN_AUDIT_OMEGA)
2026-07-06  03:14Z — Cheap → deep overlay landed              (TITAN_AUDIT_OMEGA_DEEP)
2026-07-06  09:42Z — Longevity vs Mortality axis landed        (TITAN_AUDIT_LONGEVITY)
2026-07-06  12:30Z — Audit Governor rung adopted              (TITAN_AUDIT_GOVERNOR_7D)
2026-07-06  15:10Z — Navigator rung adopted (this file)       (NAVIGATOR_RUNG)
2026-07-06  15:42Z — Reviewer pass 1: HIGH × HIGH (argparse crash)            → fixed
2026-07-06  15:48Z — Reviewer pass 1: HIGH × MED  (Omega-bare-name regression) → fixed
2026-07-06  15:54Z — Reviewer pass 1: MED × MED   (--both no-op flag)          → partial (reinstated + cosmological)
2026-07-06  16:00Z — Reviewer pass 2: HIGH × MED  (SyntaxWarning docstrings)   → fixed (raw strings)
2026-07-06  16:06Z — Reviewer pass 2: MED × MED   --help default-mention        → fixed (--both reinstated in mutex group)
2026-07-06  16:12Z — Reviewer pass 2: MED × LOW   (--both inert in write gates) → logged as nav-02
2026-07-06  16:18Z — Reviewer pass 2: SHIP-READY  CONFIRMED                    → adopted
```

## 6. Operational guidance

1. **Run before opening a new audit rung** so the rung ladder reflects current on-disk state.
2. **Diff `NAVIGATOR_INDEX_<date>.json`** between runs to detect churn (`runes:*` count drift, knights added/removed, audit ladder growth).
3. **Treat failure of `audit_chain_completeness` as a rung-ladder integrity check**, not a code-quality check.
4. **The 11-axis rubric targets are derived from a production codebase, not ideal**: they reflect what Camelot can realistically hit without bloat. Re-tune via the `_DX_WEIGHTS` table at the top of the script if you want to prioritize differently.
5. **The navigator never exec'd any project code**. If you fork the script to a new surface, preserve this property — `ast.parse(...)` only.

## 7. Evidence-class discipline (per `harness.md` Rule 1)

| Surface | Class | Rationale |
|---|---|---|
| `bin/*`/`control_plane/*`/`squires/*` listings | `planned` | re-derivable from AST walk each run |
| Runic/Omega tables | `confirmed` | regex-parse of the in-tree runic_router.py |
| Knight roster (159 across 18 surfaces) | `confirmed` | filesystem walk under `03_VAULT/Knights/**` |
| Audit ladder (5 entries) | `confirmed` | root glob — every rung has a Markdown file |
| Score 67.7 / Grade D | `confirmed` | computed from observed axes this turn |
| The humanoid persona surface (you, the operator) | `rejected` | no scaffold claims; only on-disk artifacts |

```yaml
navigator_rung:
  status: confirmed
  rung_version: 1.0.0
  scope: 'cross-surface project navigation + dev-UX scoring'
  sibling: 'Audit Governor (TITAN_AUDIT_GOVERNOR_7D_2026-07-06.md)'
  parent: 'Ω_TITAN v1000-EXCALIBUR-A'
  emitted_at: 2026-07-06
  letter_grade: D
  numeric_score: 67.7
  caveats_logged: [nav-01, nav-02, nav-03, nav-04]
```

---

_Generated as the **Navigator** rung on 2026-07-06. Companion to `navigator.py` and `NAVIGATOR_INDEX_2026-07-06.json` at repo root._
