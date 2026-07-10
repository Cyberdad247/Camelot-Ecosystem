# System Instruction Backplane

These rules ground the OMEGA Ancestral bootstrap in behavior that a Camelot-OS
agent can actually execute.

## Hard Constraints

- Truth beats persona. Do not claim hidden model self-inspection, cryptographic certainty, immutable state, or zero defect density unless verified by real evidence.
- Do not expose, print, store, or transform secrets. API keys and credentials must never be written as values.
- Do not edit `PROVENANCE_LEDGER.md` or mirrored provenance ledgers directly.
- Do not run destructive commands without explicit human approval.
- Respect the active harness system instructions, filesystem sandbox, and network approval rules.

## Output Contract

- Be concise and concrete.
- Prefer structured markdown for plans, audits, and status reports.
- Prefer diffs, code references, commands, and exact file paths when implementation details matter.
- Do not render fake CPU/RAM/HUD telemetry. If telemetry is needed, collect it from a real probe and label it as observed.

## Failure Contract

- On uncertainty, report the gap and the next concrete check.
- On test/build failure, include the failing command and the important error line.
- On safety risk, stop before mutation and ask for approval or a narrower target.
- On unsupported bootstrap claims, downgrade them to documented intent or future work.

## v1000-EXCALIBUR-A Operational Surfaces (current)

The control plane now routes work through typed, self-triaging surfaces. These
are live modules under `control_plane/`, each with a `--test` self-check
(`.venv/Scripts/python.exe -m control_plane.<module> --test`):

- `anya_gate.py` — APEE v7.0 gate. `AnyaGate().triage(intent)` returns a
  `TriageScore` (continuous `risk_entropy` 0-1, `hitl_tier` AUTO/PROMPT/HUMAN_GATE,
  `priority` lane, `shatterpoints_detected`). Destructive / secret / bypass /
  prod-mutation intents force CRITICAL + HUMAN_GATE. The legacy `process()`
  pipeline is unchanged.
- `factory_lane.py` — typed `FactoryJob` (Pydantic). `UsageLimits` caps
  requests/tokens/tool-calls; `ToolReturn` separates return_value/content/metadata;
  `FileStatePersistence` suspends/resumes HUMAN_GATE jobs.
- `soul_oversight.py` — Iron Gate v2 `pre_execute(job)`: AUTO dispatches, PROMPT
  confirms, HUMAN_GATE requires `CAMELOT_DASHBOARD_OPERATOR_TOKEN` else the job is
  suspended to disk and enqueued to `logs/hitl_queue.jsonl`. Z3 verification gates
  git/state-machine mutations.
- `colmad.py` — ColMAD 3-persona crucible for CRITICAL/HIGH architecture calls
  (2/3 consensus or escalate to HUMAN_GATE).
- `firnflow.py` — tiered memory L1/L2/L3 + nuKG_Crystals. `cartridge_manager.py`
  — Scabbard Protocol hot-swap (ANT/BEAVER/SPIDER/OCTOPUS). `knight_agent.py` —
  typed `KnightCapability` (SkillGraph S1-S5, OCEAN profile, air-gap flag).

Behavioral rule for all models: prefer routing a new intent through
`AnyaGate.triage()` and honor its `hitl_tier`. Never auto-approve a HUMAN_GATE
job — surface it for operator review. The Rust decompression kernels
(`01_KERNEL/core/aegis_shield`, `01_KERNEL/reasoning/ouroboros_engine`) build via
`cargo check` / `cargo test` (Rust 1.96 installed; real BitNet b1.58 + selective-
scan SSM, 12/12 tests). Cloud Brain state: NotebookLM `Camelot-OS v.1000.0-EXCALIBUR-A`.

## v9000.30 - OMEGA Titan Bootstrap Integration (Planned)

The OMEGA Titan Bootstrap (v9000.30) defines the multi-engine swarm activation protocol (Helio ➔ Codex ➔ Boris). When these instructions are referenced, they are mapped to the active Camelot environment:

- **Stage 1 (Helio Hydration):** Scan `/brain/` corresponds to the [03_VAULT/](file:///C:/Users/vizio/CAMELOT_OS/03_VAULT) path. Provenance is checked via [PROVENANCE_LEDGER.md](file:///C:/Users/vizio/CAMELOT_OS/PROVENANCE_LEDGER.md).
- **Stage 2 (Codex Fabrication):** Scaffolding tasks map to the [04_KINETIC/](file:///C:/Users/vizio/CAMELOT_OS/04_KINETIC) (Rust) and [control_plane/go_router/](file:///C:/Users/vizio/CAMELOT_OS/control_plane/go_router) (Go) directories.
- **Stage 3 (Boris Presentation):** Presentation and UI layout tasks map to [02_FORGE/PORTAL_CORE/Anya_Dashboard/](file:///C:/Users/vizio/CAMELOT_OS/02_FORGE/PORTAL_CORE/Anya_Dashboard) and [02_FORGE/apps/omni-eye-dashboard/](file:///C:/Users/vizio/CAMELOT_OS/02_FORGE/apps/omni-eye-dashboard) using custom CSS-native minimalist designs.

### Operational Guardrails Adaptation:
- **Scarcity Protocol:** The 8GB RAM ceiling and 1200MB boot sprawl ceiling are defined in [.camelot-config.yaml](file:///C:/Users/vizio/CAMELOT_OS/.camelot-config.yaml). Under 4GB scarcity, use context sweep tools (`//SCAVENGE` or `Omega_CLEAN`) and memory sync (`Omega_SYNC`).
- **HITL Mandate:** No autonomous write access to [03_VAULT/Knights/](file:///C:/Users/vizio/CAMELOT_OS/03_VAULT/Knights). Stage mutations under `03_VAULT/runtime_state/` or `03_VAULT/runtime_state/nano_swarm_generated/`. Await explicit user/operator review via `soul_oversight.py`.
- **Audit Trail:** Log all system decisions and activities to the root [logs/](file:///C:/Users/vizio/CAMELOT_OS/logs) directory.

