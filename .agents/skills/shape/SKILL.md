---
name: shape
description: Use when you have a rough product idea and want a complete PRD without sitting through an interactive grilling. Walk the full decision tree, self-answer with software-engineering best practices, stream the Q&A live, and write the PRD locally.
---

# Shape - Auto-Grill to PRD

Take a rough product idea and turn it into a complete PRD in one shot. No interactive grilling: walk the decision tree, answer each question using codebase facts and engineering best practices, stream the Q&A live so the operator can spot bad assumptions, and write the PRD.

Use `/shape` when the operator trusts the agent's judgment and wants speed. Use `/grill-me` plus `/write-a-prd` when the operator wants hands-on control over every decision.

## Pipeline Position

| Step | Command | What It Does |
|------|---------|--------------|
| 1a | `/grill-me` + `/write-a-prd` | Manual path: interactive interview, then PRD |
| 1b | `/shape` | Fast path: auto-grill + PRD in one shot |
| 2 | `/prd-to-issues` | Break the PRD into vertical-slice sub-issues |
| 3 | `/ralph` | Implement each sub-issue autonomously with TDD + code review |

`shape` produces the same PRD format as `write-a-prd`, so `/prd-to-issues` and `/ralph` consume its output without changes.

## Instructions

### 1. Capture the idea

If the user passed an idea as an argument, use it. Otherwise ask once:

> What do you want to build? (one paragraph is fine)

Then proceed without further interactive questions until step 8.

### 2. Explore the codebase

Before answering anything, ground decisions in reality:

- Read `README.md`, `CLAUDE.md`, `AGENTS.md`, and architecture docs where present.
- Identify existing modules, conventions, test patterns, and prior art.
- Verify factual assertions in the idea.
- Note language, framework, test runner, and directory layout.

If there is no codebase, skip to step 3 and record this in the PRD's Further Notes.

### 3. Walk the decision tree

For each branch, generate the questions a thorough engineer would ask, then answer each one yourself:

- Actors & user stories.
- Happy-path flow.
- Edge cases.
- Data model & schema.
- Module boundaries.
- API contracts.
- Testing strategy.
- Security.
- Observability.
- Out of scope.
- Dependencies & blockers.

### 4. Best-practice defaults

Prefer:

- boring over clever;
- deep modules behind simple interfaces;
- matching the codebase over external standards;
- TDD-friendly design;
- validation at system boundaries;
- YAGNI;
- parameterized queries;
- rate limits on auth endpoints;
- never logging secrets, tokens, or PII;
- mocking only at system boundaries.

Codebase facts always beat generic best practices.

### 5. Stream the Q&A live

For every decision, emit:

```text
Q: <the question>
A: <the chosen answer>
Why: <one sentence; cite a codebase reference if relevant>
```

Do not batch the decision log.

### 6. Write the PRD

Use this template exactly:

```markdown
## Problem Statement

The problem the user is facing, from the user's perspective.

## Solution

The solution, from the user's perspective.

## User Stories

A long, numbered list:
1. As a <actor>, I want a <feature>, so that <benefit>

Cover every aspect of the feature surfaced in your decision tree.

## Implementation Decisions

- Modules to build or modify
- Public interfaces of those modules
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include file paths or code snippets; they go stale fast.

## Testing Decisions

- What makes a good test here
- Which modules will be tested
- Prior art for the tests

## Out of Scope

Explicit non-goals.

## Further Notes

Anything else worth recording.

## Decisions Log

Every Q/A/Why block from step 5, in the order they were decided.
```

### 7. Save the PRD locally

- Generate a kebab-case slug from the idea.
- Create `./prds/` if it does not exist.
- Write the PRD to `./prds/<slug>.md`.
- Print the absolute path.

### 8. Offer to push to GitHub

After saving, ask once:

> Push this as a GitHub issue? [y/N]

On `y`, run:

```bash
gh issue create --title "<slug>" --body-file ./prds/<slug>.md
```

Print the issue URL.

On `n` or no answer, stop. The local file is enough.

## Camelot Integration Notes

- Treat `shape` as a `ResearchKnight` or `ForgeKnight` planning skill depending on the product idea.
- For Camelot-native work, sync major PRD decisions to Cloud Brain only after the PRD is saved.
- Do not let `/shape` execute implementation. It creates the PRD only.
- For high-risk domains, route the PRD through `SentinelKnight` or the proper Paladin before `/prd-to-issues`.

## Rules

- Do not ask questions during the decision tree.
- Do not skip branches.
- Codebase facts beat generic best practices.
- No speculative scope.
- The PRD template is fixed.
