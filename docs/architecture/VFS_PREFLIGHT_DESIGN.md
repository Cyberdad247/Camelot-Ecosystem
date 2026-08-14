# VFS_PREFLIGHT_DESIGN.md

**Status:** Draft for sovereign review
**Date:** 2026-08-13
**Tier:** APEX (Architectural Augmentation)
**Vertical Slice:** #1 of N (sequence below in §6)
**Substrate:** `v1000-EXCALIBUR-A` (augmentation layer, no replacement)
**Home:** This document. Companion manifests live under `vfs/checks/`.

> **Co-equal contract:** This spec defines a vertical slice. It does **not**
> replace `v1000-EXCALIBUR-A` modules (`anya_gate`, `soul_oversight`,
> `factory_lane`, `firnflow`, `knight_agent`, `cartridge_manager`,
> `inspira_metrics`). The preflight reuses `anya_gate.triage()` directly.

---

## 1. Context & Motivation

The VFS scaffolding under `vfs/*.md` is currently **declarative prose**:
five manifest files totalling ~64 lines. They name good checks ("tool
registry presence", "port readiness scans") but nothing executes them,
nothing emits evidence, and nothing prevents a malformed catalog from
leaking into a boot.

The Ω_VFS_ARCHITECTURE_SCAFFOLD_vMAX deposit_note classifies the VFS
scaffold as `confirmed` evidence — but that classification is about the
scaffold's *deposition*, not whether it enforces itself at runtime.

**This slice turns VFS preflight from prose into a gate.**

---

## 2. Out of Scope (Explicit Non-Goals for Slice #1)

These are features the spec does **not** deliver. They are listed here so
later slices don't have to re-litigate them:

- **No nano-knight promotion gating.** Slice #1 is boot-time only. Cartridge
  load and `//NANO_SWARM_EXPAND --promote` triggers are slice #2 / #3.
- **No replacement of `runic_router.py`, `cartridge/`, `01_KERNEL/`, or
  `04_KINETIC/`.** Augmentation only.
- **No replacement of anya_gate / soul_oversight.** Preflight **borrows**
  `anya_gate.triage()` for evidence-class assertion.
- **No swiss-army bulkhead.** Only the 8 checks enumerated in §4 below;
  expansion is opt-in via YAML, never via hidden code.
- **No retroactive claims about prior boots.** The first run is the
  baseline; prior boots are unexplored territory.

---

## 3. Architecture & Components

### 3.1 Boot entry

```
bin/awaken.py
  ├── stage 0: VFS preflight  (NEW — gate, halts on REJECTED after first-run graduation)
  │     ├── python -m control_plane.preflight --mode boot
  │     │     (delegates to control_plane.preflight.runner.run)
  │     ├── loads vfs/checks/*.yaml in lexicographic order
  │     ├── executes each check in order
  │     │     - first run: advisor-mode (continue on REJECTED, surface findings)
  │     │     - subsequent: strict-mode (fail-fast on first REJECTED)
  │     └── writes JSON artifacts then either continues or halts
  ├── stage 1..N: existing boot stages (knights, cartridges, bifrost, …)
  └── runic_router, anya_gate, soul_oversight (unchanged)
```

### 3.2 New artifacts

| Path | Purpose |
|------|---------|
| `vfs/checks/*.yaml` | Declarative check catalog (8 entries + `_README.md`) |
| `vfs/checks/_README.md` | Operator-facing guide to YAML fields and authoring rules |
| `control_plane/preflight/__init__.py` | Package |
| `control_plane/preflight/__main__.py` | CLI: `--run`, `--test`, `--list` |
| `control_plane/preflight/runner.py` | Loads YAML → executes → writes artifacts |
| `control_plane/preflight/checks/*.py` | One callable per check_id |
| `control_plane/preflight/state.py` | Graduation flag (`_graduated.flag`) handling |
| `control_plane/preflight/probe_*.py` | Reusable probes (ports, env, file presence) |
| `tests/test_awaken.py` | **E2E folded in here** (refinement §4): adds preflight block |
| `tests/preflight/test_catalog_integrity.py` | YAML parse + schema validation |
| `tests/preflight/test_runner.py` | Runner unit tests (fail-fast, manifest, write collision, advisor-vs-strict) |
| `03_VAULT/runtime_state/preflight/<UTC>/<check_id>.json` | Per-check evidence |
| `03_VAULT/runtime_state/preflight/<UTC>/_manifest.json` | Run-level evidence |
| `03_VAULT/runtime_state/preflight/_graduated.flag` | Marks that strict-mode has been activated |

### 3.3 Reuse, not replacement

**Substrate reference (verified 2026-08-13 against
`control_plane/core/anya_gate.py`):**

- `AnyaGate.triage(raw_intent: str) -> TriageScore` is a risk-based routing
  helper. It takes a `str` and returns the `TriageScore` Pydantic model
  (defined in `control_plane/core/factory_lane.py:63`) with fields
  `auto_dispatchable, priority, hitl_tier, risk_entropy, risk_reason,
  assigned_knight, estimated_tokens, cost_ceiling_usd,
  shatterpoints_detected, requires_z3_verification, cartridge_hint`.
  **It does not assert evidence class.**
- Preflight therefore **owns** `evidence_class` itself based on check
  outcome, and uses `AnyaGate.triage()` **advisory** — passing a small
  `raw_intent` string describing the check (e.g.
  `"preflight_check rejected: <id> reason <…>"`) and reading
  `triage_score.priority`, `triage_score.hitl_tier`,
  `triage_score.shatterpoints_detected` to populate the `evidence_assertion`
  advisory block in the per-check JSON. Lane values are restricted to
  `Literal["CRITICAL", "HIGH", "NORMAL", "BACKGROUND"]` — `LOW` is not a
  valid lane value and should never appear.
- `soul_oversight.IronGateV2(GateKeys.PREFLIGHT).pre_execute(...)` is
  called only when a check has `hitl_on_fail: true` AND a non-AUTO tier is
  generated. (Not exercised in slice #1; reserved for Task 6 wiring.)
- No new file is created under `cartridges/`, `01_KERNEL/`, `04_KINETIC/`, or
  within the runic router.
- Failure to import or call `AnyaGate` does **not** crash the gate — it is
  replaced with an inline sentinel `{"method": "advisory_unavailable", "lane":
  "NORMAL", "hitl_tier": "AUTO", "shatterpoints_detected": []}` so the
  preflight still produces evidence even when anya_gate is unavailable.
  This keeps preflight independent of substrate availability — correct
  augmentation posture.

---

## 4. Check Catalog (Initial 8)

Defined in `vfs/checks/*.yaml`. Each YAML has these fields:
`sequence (int, unique), id, display_name, command_type ("python_module"
| "shell"), command (list of strings, never a shell command), timeout_s,
retry (0-2, discouraged), expected_evidence_class (always CONFIRMED),
hitl_on_fail (bool), remediation_hint (string).`

Execution order = ascending `sequence` field. The catalog below is the
authoritative ordering; lexicographic fallback only applies if `sequence`
is missing or duplicated.

| seq | check_id | Purpose | hitl_on_fail |
|-----|----------|---------|---|
| 010 | `env_dependency_match` | Python 3.x, Rust 1.96, Node 20, Ollama availability | false |
| 020 | `foss_validation_constraints` | License header scan over `01_KERNEL/`, `02_FORGE/`, `vfs/` | false |
| 030 | `northstar_brief_currency` | `NORTHSTAR_ARCHITECTURE_BRIEF.md` age ≤ 60 days | true |
| 040 | `port_readiness_scan` | 8080/8011/11434/4433/4434 | true |
| 050 | `provenance_ledger_writable` | `PROVENANCE_LEDGER.md` writable, hook chain reachable | false |
| 060 | `tool_registry_presence` | Imports for required Python modules succeed | false |
| 070 | `vfs_scaffold_integrity` | All required `vfs/*.md` present, frontmatter parseable | true |
| 080 | `lattice_yaml_consistency` | `docs/architecture/lattice.yaml` parses; subprojects exist | false |

Sequences are 010/020/…/080 (stride 10) so authors can insert checks at
a natural position without renumbering the catalog. The three
`hitl_on_fail: true` checks (`northstar_brief_currency`,
`port_readiness_scan`, `vfs_scaffold_integrity`) are the operator-visible
ones. The other five are strict-AUTO: a rejection halts boot **without**
prompting — interruptible only via the strict-mode halt itself.

Total target runtime: **≤ 2s p95** on a warm environment.

---

## 5. Data Flow & Evidence Schema

### 5.1 Run identity

```
run_id = f"preflight-{UTC_ISO8601}-{scene_hash[:6]}"
scene_hash = sha256(vfs/rosters.md content + lattice.yaml subproject list)
```

Same-minute re-runs get a per-second counter suffix to avoid collisions.

### 5.2 Execution flow

```
load YAML → for each check i:
   dispatch check → run command → capture exit_code, stdout, stderr, duration_ms
   if first-run AND check REJECTED → mark advisor_finding, continue
   if strict-mode AND check REJECTED → fail-fast, halt
   assert evidence_class via anya_gate.triage()
   write per-check JSON
write _manifest.json
```

### 5.3 Per-check JSON

```json
{
  "schema": "camelot.preflight.check/v1",
  "run_id": "preflight-2026-08-13T00-12-04Z-a4f9c2",
  "check_id": "port_readiness_scan",
  "display_name": "Port Readiness Scan",
  "command_observed": ["python", "-m", "control_plane.preflight.probe_ports",
                       "--ports", "8080,8011,11434,4433,4434"],
  "command_raw": "vfs/checks/port_readiness_scan.yaml",
  "exit_code": 0,
  "started_at": "2026-08-13T00:12:04.211Z",
  "duration_ms": 184,
  "stdout_excerpt": "...",
  "stderr_excerpt": "",
  "evidence_class": "CONFIRMED",
  "evidence_assertion": {
    "method": "anya_gate.triage",
    "lane": "LOW",
    "shatterpoints": 0,
    "hitl_tier": "AUTO"
  },
  "hitl_required": false,
  "halt_decision": "continue",
  "advisor_finding": false,
  "remediation_hint": null,
  "artifact_path": "..."
}
```

State combinations on REJECTED:

| Mode | `evidence_class` | `halt_decision` | `advisor_finding` | `rejection_reasons` |
|------|------------------|-----------------|-------------------|---------------------|
| Strict, non-hitl check | `REJECTED` | `block_boot` | `false` | non-empty |
| Strict, hitl check | `REJECTED` | `block_boot` or `await_hitl` | `false` | non-empty |
| First-run advisor | `REJECTED` | `continue` | `true` | non-empty |

`continue` runs in advisor-mode indicate the boot proceeded; `advisor_finding:
true` is the mark that the field-surfaced issue was acknowledged but not a
blocker on this boot.

`evidence_assertion` is **advisory metadata**, computed by
`AnyaGate.triage(raw_intent)` from the rejection-reasons text. Its shape
maps to `TriageScore` fields (`priority` -> `lane`,
`shatterpoints_detected` -> `shatterpoints`, etc.) and may be absent if
the substrate is unavailable (see §3.3 fallback). It does **not** influence
`evidence_class`: preflight decides CONFIRMED/REJECTED itself.

### 5.4 Run manifest

```json
{
  "schema": "camelot.preflight.run/v1",
  "run_id": "...",
  "started_at": "...",
  "ended_at": "...",
  "total_ms": 1814,
  "checks_total": 8,
  "checks_passed": 5,
  "checks_failed": 1,
  "checks_skipped": 2,
  "halted_at_check": "port_readiness_scan",
  "halt_decision": "block_boot",
  "scene_hash": "a4f9c2",
  "catalog_hash": "sha256-of-vfs/checks/*.yaml",
  "first_run": false,
  "graduated_to_strict": true
}
```

### 5.5 Idempotency

Each run writes into its own UTC-stamped directory; no overwrites. Two
runs in the same minute produce distinct run_ids and dirs.

No PROVENANCE_LEDGER.md writes from preflight itself. The hook chain
already emits a `PREFLIGHT` entry; preflight only writes JSON. Avoids a
bootstrap-loop.

---

## 6. Failure Modes & First-Run Advisor

### 6.1 Failure matrix

| Failure | Detection | Behavior |
|---|---|---|
| Check exits non-zero | OS exit code | Mark REJECTED, gather stderr, halt (strict) / advisor (first-run) |
| Timeout | `subprocess.communicate(timeout=…)` | Mark REJECTED with `rejection_reasons: ["timeout: Xms exceeded"]` |
| Command missing | `FileNotFoundError` | Mark REJECTED with subclass `MISSING_TOOL` |
| YAML broken | runner load | Write `_catalog_error.json`, exit 1, halt |
| `vfs/checks/` missing | runner load | Write `_catalog_missing.json`, exit 1, halt |
| JSON disk write fail | `OSError` on write | `_WRITE_FAILED`, halt, stderr log |
| Ctrl-C | `KeyboardInterrupt` | `_INTERRUPTED`, leave prior artifacts intact, exit 130 |
| `vfs/rosters.md` change | Scene-hash diff | Surface as `scene_change_observed: true`, **not** a failure |

### 6.2 First-run advisor-mode (refinement)

- New boot, no `03_VAULT/runtime_state/preflight/_graduated.flag` present.
- All checks run. Any REJECTED check is recorded with `advisor_finding:
  true` and `halt_decision: "continue"`. Boot **continues**.
- On first run where **all 8 checks reach CONFIRMED**, the runner writes
  `_graduated.flag` and emits `graduated_to_strict: true` in the manifest.
- Next run reads the flag → strict-mode → fail-fast on REJECTED.
- Rollback to advisor-mode is a manual deletion of `…/preflight/_graduated.flag`.

### 6.3 Sovereign escape hatch — DELETED

Per refinement §3: there is **no** `CAMELOT_SKIP_PREFLIGHT` env var, no
`--skip-sovereign` flag, no per-check bypass. A strict-mode halt is a
hard halt. The flag mechanism above is the only mechanism.

`runner.py` will explicitly fail if either env var or flag is supplied,
with a stderr message that explains the design choice.

### 6.4 Operator-visible summary

Success:

```
[VFS_PREFLIGHT] run_id=preflight-2026-08-13T00-12-04Z-a4f9c2
[VFS_PREFLIGHT] 8/8 CONFIRMED · 1.81s · catalog_hash=3ed2…
[VFS_PREFLIGHT] graduated_to_strict=true · next: knight roster load
```

Strict halt:

```
[VFS_PREFLIGHT] run_id=...
[VFS_PREFLIGHT] 5/8 CONFIRMED · 1 REJECTED · 2 SKIPPED · halted at port_readiness_scan · 1.42s
[VFS_PREFLIGHT] REJECTED: port_readiness_scan
[VFS_PREFLIGHT]   exit_code=2 · rejection_reasons=["port 8011 expected open, observed closed"]
[VFS_PREFLIGHT]   remediation_hint: scripts/ops/start-bifrost.sh
[VFS_PREFLIGHT] BOOT HALTED
```

First-run (advisor):

```
[VFS_PREFLIGHT] run_id=...
[VFS_PREFLIGHT] (advisor-mode · first run) 7/8 CONFIRMED · 1 advisor_finding · 1.81s
[VFS_PREFLIGHT] ADVISOR: northstar_brief_currency
[VFS_PREFLIGHT]   vfs/rosters.md unchanged · lattice.yaml unchanged
[VFS_PREFLIGHT] NORTHSTAR_ARCHITECTURE_BRIEF.md age: 92 days (limit 60)
[VFS_PREFLIGHT]   remediation_hint: refresh NORTHSTAR brief or raise limit
[VFS_PREFLIGHT] Continuing boot (advisor-mode). Will enter strict-mode on next successful run.
```

---

## 7. Testing & Acceptance Criteria

### 7.1 Test layers

| Layer | Path |
|---|---|
| Unit | `tests/preflight/test_<check_id>.py` |
| Catalog | `tests/preflight/test_catalog_integrity.py` |
| Runner | `tests/preflight/test_runner.py` |
| Integration | folded into `tests/test_awaken.py` (refinement §4) |

### 7.2 Acceptance criteria (Merlin / sovereign sign-off)

- **AC1.** All 8 checks reach CONFIRMED in a clean boot on Cybertronia.
- **AC2.** Total runtime < 2s p95.
- **AC3.** Manifest hashes are reproducible across same-scene re-runs.
- **AC4.** Deliberately broken boot (e.g. delete `vfs/preflight.md`) yields
  REJECTED, exit 1, with `rejection_reasons` citing the missing file. In
  advisor-mode this logs an advisor finding and continues; in strict-mode
  it halts.
- **AC5.** No spurious PROVENANCE_LEDGER.md entries generated by preflight
  itself (`pre_stage_0 enters == post_stage_0 enters`).
- **AC6.** First-run advisory → strict-mode graduation works. Verified by
  presence of `_graduated.flag` and `graduated_to_strict: true` field.
- **AC7.** `bin/awaken.py --stage 0` is idempotent (two runs in same
  minute = two distinct run dirs, no corruption, no false positives).
- **AC8.** `python -m control_plane.preflight --test` returns 0 with all
  8 inline-synthetic checks passing (per existing module self-test
  pattern in `control_plane/`).
- **AC9.** Operator summary text appears on stdout for success, strict
  halt, and advisor modes — verified by golden-string capture in
  `test_awaken.py`.

### 7.3 Code-review gate (per AGENTS.md Rule 2)

Before any preflight code is merged:
1. Synthetic catalog + synthetic checks pass locally.
2. Real catalog + real checks pass on a clean venv.
3. A second reviewer or independent validator (per `requesting-code-review`
   skill) reviews the diff.
4. Sovereign signs off on AC1–AC9 evidence.

---

## 8. Decisions Log (Refinements During Brainstorm)

| # | Topic | Original | Final |
|---|-------|----------|-------|
| 1 | Trigger surface | Boot / nano-promote / cartridge-load (multi) | Boot only (slice #1) |
| 2 | Architecture mode | Replacement / twin / augmentation / docs-only | Augmentation above v1000 |
| 3 | Spec location | Spec docs / docs/architecture / ADR / chat-only | docs/architecture/ |
| 4 | Sovereign escape hatch | env + flag + hitl_on_fail | **Dropped**; first-run advisor only |
| 5 | Failure behavior | fail-fast (confirmed) | fail-fast (strict) + first-run advisor |
| 6 | E2E test home | New `test_merlin_e2e.py` | Folded into `tests/test_awaken.py` |
| 7 | Catalog ordering | Lexicographic (default) | Explicit `sequence` field, stride 10 |
| 8 | Anti-correlation principle | Preflight writes JSON evidence | No direct `PROVENANCE_LEDGER.md` writes from preflight itself; hook chain handles ledger entries |
| 9 | Evidence-class origin | `AnyaGate.triage()` would be the source | Preflight owns CONFIRMED/REJECTED; `AnyaGate.triage()` is **advisory only**; graceful-degradation sentinel when substrate unavailable; `lane` constrained to `CRITICAL/HIGH/NORMAL/BACKGROUND` |

A paired ADR is at `docs/adr/0006-vfs-preflight-strict-mode.md`.

> **Substrate-vs-spec patch (2026-08-13):** Originally the spec claimed
> `AnyaGate.triage()` would assert the evidence class. Substrate read at
> execution time showed `AnyaGate.triage(raw_intent: str) -> TriageScore`
> is a risk-based routing helper with no evidence-class semantics, and that
> `TriageScore.priority` accepts only `CRITICAL/HIGH/NORMAL/BACKGROUND`
> (no `LOW`). Spec §3.3, §5.3, and Decisions Log rows 8/9 are updated
> to reflect: preflight owns evidence class; anya_gate is advisory
> (graceful degradation if unavailable); `evidence_assertion.lane` is
> constrained to the four valid priority values. Plan Task 6 step 2 also
> shifts `anya_triage_fn` signature from `(payload: dict, expected_class)`
> to `(raw_intent: str)` and adds an inline sentinel fallback.

---

## 9. Sequence: This Slice + Later Slices

| # | Slice | Description | Depends on |
|---|-------|-------------|-----|
| 1 | **VFS Preflight Scaffold (THIS)** | Boot-time gate, JSON evidence, advisor→strict mode | (none) |
| 2 | Cartridge Load Gate | Wire preflight as the gate before cardinal-knight binding | #1 |
| 3 | Nano-Knight Promotion Gate | Wire preflight as the gate before `//NANO_SWARM_EXPAND --promote`; consume `EvidenceClass` from §5.3 | #1, #2 |
| 4 | Bio-Kinetic Swarm Harness | Bio-inspired swarm controller bound to verified UKG crystals via the new gate | #3 |
| 5 | Cartridge ↔ Knight Reforge | Typed binding layer over `cartridges/` and `knight_agent` | #2 |

This doc says nothing about #4-#5 beyond listing them. They get their own
brainstorm cycles.

---

## 10. Cross-References

- **Substrate:** `docs/architecture/Ω_VFS_ARCHITECTURE_SCAFFOLD_vMAX.deposit_note.md` (confirmed evidence class, 2026-07-23)
- **Lattice:** `docs/architecture/lattice.yaml` (frozen 2026-07-10; `surface.sot: docs/architecture/lattice_map.md`)
- **Earlier audit:** `docs/architecture/NORTHSTAR_ARCHITECTURE_BRIEF.md` (2026-05-13; 5 blockers unrelated to this slice)
- **Existing scaffolding:** `vfs/{preflight,systeminstructions,skills,rosters,protocols}.md`
- **Augmentation partner:** `control_plane/anya_gate.py` (provides `triage()`)
- **HITL partner:** `control_plane/soul_oversight.py` (provides `IronGateV2`)
- **Source-of-truth map:** `docs/architecture/SOURCE_OF_TRUTH_MAP.md`

---

## 11. Resolved Questions

1. **Graduation trigger:** All 8 checks CONFIRMED on first run. (ADR
   `docs/adr/0006-vfs-preflight-strict-mode.md` records this.)
2. **Catalog order:** Explicit `sequence` field, stride 10, ascending.
3. **Age limit:** 60 days. NOTE: NORTHSTAR_ARCHITECTURE_BRIEF.md is
   2026-05-13; today is 2026-08-13. Age is **92 days on day 0**, which is
   over the 60-day limit. The first-run advisor will fire on this. The
   auditor recommendation: refresh the NORTHSTAR brief (or formally
   supersede it via a new architecture note) before strict-mode
   graduation. This is not a design issue; it is a real finding about the
   existing substrate that the new gate surfaces.
4. **ADR:** Written at `docs/adr/0006-vfs-preflight-strict-mode.md`.
5. **AnyaGate advisory boundary (substrate-verified 2026-08-13):**
   `AnyaGate.triage(raw_intent: str) -> TriageScore` is a risk-based
   routing helper, not evidence-class confirmer. Preflight owns
   CONFIRMED/REJECTED. Run with graceful-degradation sentinel when
   AnyaGate is unavailable. (Spec §3.3, §5.3, §8 row 6 patched.)

## 12. Remaining Action Surface (Informational)

- Refresh `NORTHSTAR_ARCHITECTURE_BRIEF.md` (or supersede) before
  graduation runs are expected.
- Implement Slice #1 against this spec using the `writing-plans` skill
  before any code is written.
- Code is gated on AC1–AC9 + paired code review per AGENTS.md Rule 2.
