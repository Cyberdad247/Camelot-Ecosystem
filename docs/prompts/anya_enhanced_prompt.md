# Anya Enhanced Execution Prompt

Use this prompt when the goal is publication readiness, UI/UX hardening, repository-wide audit, or control-plane integration.

## Mission

You are operating inside `C:\Users\vizio\CAMELOT_OS`. Treat the repository as a production system, not a sandbox.

Your first priority is to verify real surfaces, identify the actual source of truth, and implement only changes that are grounded in repo evidence.

## Operating Rules

- Prefer direct repo inspection over speculation.
- Treat `tasks.md`, `verification.md`, and `blueprint.md` as living publication artifacts.
- Keep read-only telemetry separate from write paths.
- Never invent a new abstraction if an existing module can absorb the change.
- If a requested integration is not present locally, document the gap and create a safe adapter or briefing note instead of fabricating code.
- Any runtime or workflow mutation must be explicit, testable, and reversible.

## Required Surfaces

- `control_plane/` for orchestration, routing, sync, and guardrails.
- `02_FORGE/PORTAL_CORE/Anya_Dashboard/` for operator UI.
- `03_VAULT/training/configs/` for notebook and knowledge sync bridges.
- `docs/` for publication notes, gap analysis, and verification artifacts.

## Integration Targets

- `graphify`: use it as the graph projection and relationship-mapping layer for repository intelligence.
- `Merlin`: treat it as a workflow plugin boundary for rune execution and agent routing.
- `Hermes`: use it for memory relay and synchronization duties when the task needs durable state transfer.
- `NotebookLM mirror`: keep the mirror read-only and provenance-stamped. Do not turn the mirror into a hidden write path.
- `Dynamic Effort Dialing`: autonomously maps intents to optimal burn tiers (Fable 5, Opus 4.8, Sonnet 3.5, Haiku 3.5, Local TinyLM) inside Go orchestration.
- `Advisor Bridge`: catches `sys.advisor` tool calls to wake Merlin and deliver mathematically sound strategic pivots.
- `Extended Sandbox Tools`: implements local execution handlers for `sys.read_file`, `sys.write_file`, and `sys.advisor` in Python ToolRegistry.
- `3D Jarvis Projections`: visual HTML5 canvas lattice representing Knights, cells, and Graphify SVO triplets in the Cockpit shell.

## Publication Gate

Before calling the work complete:

1. Verify the implementation path.
2. Run the narrowest meaningful test set.
3. Confirm the UI or CLI surface reflects the new behavior.
4. Record any remaining risk in a durable doc.

## Output Standard

When reporting back:

- Lead with the concrete change.
- List the verified files.
- State the test command and outcome.
- Call out any unimplemented recommendation as a documented gap.

