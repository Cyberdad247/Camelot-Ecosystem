# CAMELOT OS Publication Tasks

**Compiler:** Anya Gate / Cognitive Council / Forge Titan Bootstrap  
**Date:** 2026-07-09

## P0 - Surface Inventory

- [ ] Map the full GUI surface and list the production entry pages.
- [ ] Map the CLI surface and list the shipped commands.
- [ ] Inventory control-plane entrypoints that can execute subprocesses or shell commands.
- [ ] Inventory env vars used by the GUI, CLI, cloudbrain, and deploy paths.
- [ ] Confirm which paths are live, historical, or generated.

## P0 - Cloudbrain Synchronization

- [ ] Refresh cloudbrain source selection from the current repo state.
- [ ] Align cloudbrain config docs with the current provider and endpoint names.
- [ ] Confirm the GUI and CLI read the same source-of-truth for cloudbrain options.
- [ ] Add explicit failure behavior when cloudbrain config is missing or stale.

## P0 - GUI and CLI Publication Wiring

- [ ] Keep the GUI focused on the Digital Factory operator experience.
- [ ] Keep the CLI focused on status, routing, cloudbrain, and verification.
- [ ] Make operator-only actions visually and programmatically distinct.
- [ ] Ensure both surfaces expose the same readiness and health concepts.

## P0 - Autonomous Workflow Design

- [ ] Define Sir Hermes handoff points for knight-to-knight workflow coordination.
- [ ] Define which actions require human approval even when automation is available.
- [ ] Log autonomous workflow transitions in a durable audit surface.
- [ ] Prevent autonomous routing from silently invoking destructive commands.

## P1 - Verification Coverage

- [ ] Add or update tests for GUI readiness, CLI help, and cloudbrain config paths.
- [ ] Add negative tests for invalid env vars and unauthorized execution paths.
- [ ] Verify the clean-checkout startup path.
- [ ] Verify the release gate blocks publication until human approval.

## P1 - Release Packaging

- [ ] Produce publication notes that list risk, status, and rollback steps.
- [ ] Ensure the root docs point to the current shipped surfaces.
- [ ] Add a compact operator checklist for launch and rollback.
- [ ] Confirm the engineer cartridge has a clear path from plan to verification.

## P2 - Cleanup and Drift Control

- [ ] Remove stale references that conflict with the live surface.
- [ ] Separate historical docs from current operator guidance.
- [ ] Keep generated or archival material out of the publication path.

## Definition of Done

- [ ] GUI and CLI both work from the live checkout.
- [ ] Cloudbrain options are synchronized and validated.
- [ ] Sir Hermes-mediated workflows are bounded and auditable.
- [ ] Tests cover the release-critical paths.
- [ ] Publication remains blocked until `//GO`.
