# Goal Video Resources Integration - 2026-05-20

## Integrated Source

`https://github.com/nemanjadotcom/goal-video-resources.git`

Local path:

`03_VAULT/Reference_Architectures/skills/goal-video-resources`

## What This Repository Contains

This is an experiment resource bundle, not a normal skill pack.

It contains:

- `01-goal`: prompt and repo instructions for a direct `/goal` build.
- `02-ralph`: prompt and repo instructions for `shape -> to-issues -> ralph`.
- `03-hermes-codex-claude`: prompt, AGENTS contract, and SOUL wrappers for a Hermes orchestrator using Codex as builder and Claude as reviewer.

## Camelot Integration

Created active local adapter:

` .agents/skills/goal-video-workflow/SKILL.md`

This adapter converts the experiment into a Camelot-native workflow:

1. Goal contract.
2. Visible task ledger.
3. Builder Knight.
4. Reviewer Knight.
5. Fix loop.
6. Runtime and visual verification.
7. Final evidence report.

## Merlin Usage

Merlin should use this source when the user asks for a goal-driven build, demo app, product prototype, agentic workflow comparison, Ralph-style implementation, or a visible builder/reviewer loop.

## Knight Mapping

| Experiment Role | Camelot Knight | Purpose |
|---|---|---|
| `/goal` contract | `GoalStewardKnight` or `SirAlexKnight` | Convert rough goal into constraints, acceptance criteria, and evidence requirements |
| Ralph implementation | `ForgeKnight` | Build approved vertical slices |
| Codex builder wrapper | `ForgeKnight` | Execute implementation but produce a handoff, not final approval |
| Claude reviewer wrapper | `ReviewKnight` or `SentinelKnight` | Independent review, no implementation edits |
| Hermes Kanban | `OperationsKnight` | Maintain task state, blockers, handoffs, and final report |

## Workflow Contract

For a goal-style request, Merlin should produce:

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

Then Merlin creates task cards:

1. `SPEC`
2. `BUILD`
3. `REVIEW`
4. `FIX`, only if review blocks
5. `VERIFY`

## Safety Position

The repository is stored as a review-required reference source.

Rules:

- Do not execute imported scripts automatically.
- Do not assume the video prompt constraints fit every Camelot repo.
- Do not let builder self-report count as final approval.
- Do not let reviewer agents edit implementation files unless explicitly assigned as fixers.
- Do not skip visual verification when UI is part of the goal.

## Manifest Entry

The source is registered in:

`03_VAULT/runtime_state/external_skill_sources_manifest.json`

The active adapter is:

`camelot-local:goal-video-workflow`
