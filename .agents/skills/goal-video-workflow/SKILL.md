---
name: goal-video-workflow
description: Use when Merlin needs to turn a goal-style build request into a visible orchestration workflow with a builder Knight, reviewer Knight, fix loop, checks, visual verification, and final evidence.
---

# Goal Video Workflow

Adapt the `nemanjadotcom/goal-video-resources` experiment into a Camelot-native orchestration pattern.

This skill is for workflow formation, not blind script execution. The imported repository is a review-required reference source.

## Source

- Repository: `https://github.com/nemanjadotcom/goal-video-resources.git`
- Local path: `03_VAULT/Reference_Architectures/skills/goal-video-resources`

## Core Pattern

The experiment compares:

- `/goal`: a persistent implementation contract.
- `shape -> to-issues -> ralph`: PRD, vertical slices, autonomous implementation loop.
- Hermes-style orchestration: visible Kanban ledger, Codex builder, Claude reviewer, fix loop, final report.

Camelot adapts this as:

1. Goal contract.
2. Visible task ledger.
3. Builder Knight.
4. Reviewer Knight.
5. Fix Knight loop if review blocks.
6. Runtime and visual verification.
7. Final evidence report.

## When To Use

Use this when the user asks for:

- a goal-driven build;
- a demo app or product prototype;
- a comparison of agentic build workflows;
- a visible implementation ledger;
- independent builder/reviewer separation;
- a Ralph-style implementation pass;
- a Codex builder plus reviewer gate.

## Knight Composition

### Goal Steward

- Archetype: `OperationsKnight` or `SirAlexKnight`
- Purpose: capture objective, constraints, acceptance criteria, allowed workspace, required checks, and final evidence.
- Skills: `shape`, `to-prd`, `to-issues`.

### Builder Knight

- Archetype: `ForgeKnight`
- Purpose: implement the approved goal or task slice.
- Skills: `ralph-local`, `tdd`.
- Rule: builder self-report is not final.

### Reviewer Knight

- Archetype: `SentinelKnight`, `ArchitectKnight`, or dedicated `ReviewKnight`
- Purpose: independently review the diff, instructions, checks, and acceptance criteria.
- Skills: code review, `diagnose`, `triage`.
- Rule: reviewer should not edit implementation files during review.

### Fix Knight

- Archetype: `ForgeKnight`
- Purpose: fix only listed reviewer blockers.
- Skills: `tdd`, `diagnose`.
- Rule: no vague rework; every fix maps to a reviewer finding.

## Process Contract

1. Write the goal contract.
2. Create task ledger cards:
   - SPEC
   - BUILD
   - REVIEW
   - FIX, only if blocked
   - VERIFY
3. Ground in repo instructions such as `AGENTS.md`, `README.md`, and architecture docs.
4. If requirements are rough, run `shape` first.
5. If a PRD exists, run `to-issues`.
6. Build one vertical slice or approved goal scope.
7. Run relevant checks.
8. Perform visual verification when UI is touched.
9. Run independent review.
10. If blocked, create a scoped fix task and repeat review.
11. Write final evidence.

## Goal Contract Template

```markdown
# Goal Contract

## Objective

## Allowed Workspace

## Constraints

## Acceptance Criteria

## Required Checks

## Visual Verification

## Builder Handoff Requirements

## Reviewer Handoff Requirements

## Final Evidence Requirements
```

## Ledger Card Template

```markdown
# <SPEC|BUILD|REVIEW|FIX|VERIFY>

## Owner Knight

## Task

## Inputs

## Exit Criteria

## Evidence Required

## Status
```

## Safety Rules

- Do not execute imported scripts automatically.
- Do not treat builder self-report as final.
- Do not let the reviewer silently become the builder.
- Do not skip checks or visual verification when required.
- Do not use external CLI tools if authentication or policy blocks them; report the blocker.
- Keep temporary orchestration artifacts in a clearly marked temp path.

## Final Report

Always report:

- what was built or specified;
- which Knight performed each phase;
- which checks passed or failed;
- whether visual verification was done;
- whether review passed or blocked;
- what changed;
- known compromises;
- where artifacts were saved.
