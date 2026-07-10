# CAMELOT OS Publication Blueprint

**Compiler:** Anya Gate / Cognitive Council / Forge Titan Bootstrap  
**Date:** 2026-07-09  
**Objective:** Make Camelot-OS publication-ready as a real Digital Factory with a full UI/UX GUI, a usable CLI, synchronized cloudbrain sources, guarded autonomy, and a human release gate.

## Council

The implementation will be coordinated through a cognitive council with explicit lanes:

- **Anya Gate**: intake, routing, operator UX, and release gating.
- **Merlin Omega**: DAG-level orchestration and dependency ordering.
- **Sir Hermes**: cross-knight workflow relay, handoff normalization, and task fan-out.
- **Sir Codex**: implementation of code paths, tests, and CLI/UI wiring.
- **Sir Helios**: cloudbrain/source refresh and research synchronization.
- **Sir Boris**: architecture review and production boundary validation.
- **Sir Ghost**: isolated execution and unsafe-path containment.
- **Sir Hashimoto**: security, trust boundaries, and secret handling.
- **Lady Alexandria**: documentation, provenance, and knowledge capture.

## Publication Standard

Publication means the repo must do all of the following:

- boot predictably from a clean checkout,
- expose the same product through GUI and CLI,
- validate cloudbrain-backed options before selecting them,
- keep autonomous workflow actions within a controlled boundary,
- fail loudly when an unsafe or missing dependency appears,
- ship with test and verification commands that map to the real surfaces.

## Target Surface

### GUI

- The main UI must present the Digital Factory state clearly.
- Primary flows must be visible without digging through implementation files.
- The UI must expose status, queue state, cloudbrain sync state, and release readiness.
- Operator-only actions must be visually separated from read-only telemetry.

### CLI

- The CLI must remain the production control plane.
- Help, status, cloudbrain, routing, and verification commands must be discoverable.
- CLI output must be deterministic enough to support automation and release checks.

### Cloudbrain

- Cloudbrain sources must be synchronized before option selection.
- Provider and endpoint selection must be driven by current repo state and env config.
- The plan should prefer live configuration over hard-coded defaults.

### Autonomy

- Sir Hermes may coordinate and normalize workflows across knights.
- Sir Hermes may not bypass operator approval for destructive or publication actions.
- Autonomous paths must remain observable, logged, and recoverable.

## Implementation Phases

### Phase 1 - Surface Mapping

- Inventory the current GUI, CLI, control-plane, cloudbrain, and ledger entrypoints.
- Identify missing env vars, missing scripts, and missing verification steps.
- Map which modules are shipped, which are historical, and which are optional.

### Phase 2 - Publication Wiring

- Align the GUI and CLI with the same source-of-truth state.
- Wire cloudbrain configuration refresh into the option-selection flow.
- Add or repair operator-safe boundaries around executable surfaces.

### Phase 3 - Verification Hardening

- Add repeatable verification for GUI, CLI, and control-plane flows.
- Add negative tests for missing env vars, invalid tokens, and unsafe commands.
- Make the publication gate explicit and human-approved.

### Phase 4 - Release Readiness

- Produce a concise release briefing with risks, blockers, and rollback steps.
- Confirm that the repo can be run and validated from a clean checkout.
- Stop at the Iron Gate until `//GO` is received.

## Non-Negotiables

- No silent pass-through from operator prompts to shell execution.
- No release without a visible verification path.
- No autonomous publication.
- No hidden dependency on stale cloudbrain values.

## Success Criteria

- A human can run the Digital Factory from GUI or CLI.
- Cloudbrain options are current and synchronized.
- Autonomy is useful but bounded.
- Verification is explicit, repeatable, and tied to the actual shipped surface.
- The repo is ready for publication only after a manual gate.
