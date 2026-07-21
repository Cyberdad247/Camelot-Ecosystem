# Universal Critical Thinking Skill Report

## Integrated Sources

- `ChristopherKahler/paul` provides the Plan-Apply-Unify loop and explicit loop closure.
- `xhd2015/skills` provides installable workflow tooling and a reusable CLI pattern.
- `Portkey-AI/portkey-python-sdk` provides gateway-style routing, fallback behavior, observability, and confidence-aware execution surfaces.

## What Was Implemented

- `control_plane/critical_thinking.py`
- `docs/skills/universal_critical_thinking.md`

## Intended Use

- Shared reasoning frame for all Camelot knights.
- Can be imported by knight-specific workflows as a consistent preflight and qualification layer.

## Design Notes

- The helper is intentionally lightweight and dependency-free.
- The skill is written as a universal contract, not a one-off task prompt.
- The protocol preserves evidence, separates assumptions, and requires a qualification step before execution.

