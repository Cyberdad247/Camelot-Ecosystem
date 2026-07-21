# CYBERTRONIA_RAPID_FORGE_CARTRIDGE_V1000 — nuKG_Crystal Deposit Note

**Deposited:** 2026-06-30
**Evidence class:** `aspirational`
**Source message:** `[νKG_CRYSTAL]: CYBERTRONIA_RAPID_FORGE_CARTRIDGE_V1000` (single-token user deposition)

## What this note is

Per AGENTS.md Universal Bootstrap — `FireFlow + nuKG_Crystals` — and `harness.md`'s
Evidence Gates, every proposed νKG_Crystal routed through the camelot local
backplane must be classified into one of four evidence classes before treating
it as operational state:

1. `confirmed` — backed by live files, commands, tests, logs, or manifests.
2. `planned` — plausible design work with named implementation steps.
3. `aspirational` — narrative claims not yet backed by repo artifacts.
4. `rejected` — claims that conflict with verified runtime state.

The deposition of `CYBERTRONIA_RAPID_FORGE_CARTRIDGE_V1000` is **aspirational**
because the crystal ID:

- Does NOT appear in the live L2 crystal store `03_VAULT/firnflow/nukg_crystals.json`.
- Does NOT appear in any prior committed evidence manifest under `03_VAULT/runtime_state/`.
- Does NOT have a verifiable skill_pattern body, knight attribution, or confidence score.
- Does NOT yet have a failing-then-passing test under `tests/` that exercises the
  `FirnFlow.crystallize` + `FirnFlow.retrieve` round-trip with this crystal_id.

## Promotion path (aspirational → confirmed)

To promote this crystal to `confirmed`, at minimum:

1. Invariant: `python -c "from control_plane.firnflow import FirnFlow; ..."` exits 0.
2. Reproducible: `python -m pytest tests/test_firnflow_crystallize_roundtrip.py -v`
   asserts that after `FirnFlow.crystallize('CYBERTRONIA_RAPID_FORGE_CARTRIDGE_V1000', {...})`,
   `FirnFlow.list_crystals()` returns a `NuKGCrystal` with the expected shape
   (per `control_plane/firnflow.py:74-82`), and `FirnFlow.retrieve(...)` finds it.
3. Confidence: the crystallized pattern's `confidence` must clear
   `CRYSTAL_THRESHOLD = 0.85` (firnflow.py:53).
4. Reuse: a follow-up invocation must increment `reuse_count` from 0 → ≥ 1,
   proving the crystal is reachable from the camelot retrieval path at runtime.

When all four pass, edit `03_VAULT/runtime_state/CYBERTRONIA_RAPID_FORGE_CARTRIDGE_V1000.evidence.json`
and flip `evidence_status` to `"confirmed"`, then merge this deposit-note
into the canonical `nukg_crystals.json` lineage.

## What this note is NOT

- Not a code change. Not a CRYSTAL_STORE mutation. Not a `crystallize` call.
  The user message was a deposition of an identifier; we routed it through
  AGENTS.md evidence-class discipline and parked it.
- Not a runtime state. Until the round-trip command above is reproduced on
  a machine that can actually invoke it, this crystal is doctrinal-only.

## Relationship to `forge_nexus.sh`

A separate user directive in this same conversation (per the omni-nexus-ide
fold-in scope PR cycle) asked us NOT to scaffold `forge_nexus.sh`. The
CYBERTRONIA_RAPID_FORGE_CARTRIDGE_V1000 crystal is thematically adjacent
(`rapid` + `forge`) but lives in a different layer: it is a `FirnFlow.crystallize`
target, not a shell script. Conflating these two would conflate firnflow's
NLM-tiered memory and the omni-nexus-ide daughter project's scaffolding.
Recommendation: keep them separate crystals.

— Engineering Feedback (AGENTS.md → docs/architecture/)
