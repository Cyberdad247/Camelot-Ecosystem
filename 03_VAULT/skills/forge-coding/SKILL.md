| name | description |
| :--- | :--- |
| forge-coding | Kinetic Builder: Unified Diff Generation & 10-line Iron Gate |

# Forge Coding Skill

**Role:** Code Design (L2) & implementation.

Use this skill to transmute planning into kinetic, secure, and testable code.

## Phase 1: Architecture Alignment

1. **AST Alignment**: Ensure changes follow the project's strict typing and linting (Biome/Cargo).
2. **Scaffold Prep**: Identify where the unit test for this logic will reside.

## Phase 2: Kinetic Iteration (10-line Rule)

1. **Incremental Diffs**: Break large changes into small, atomic patches (<10 net lines).
2. **Unified Diff Format**: Generate patches that are drop-in compatible with the existing stack.
3. **Shadow Workspace Target**: Never assume direct write to production without a verification pass.

## Phase 3: Test Integration

1. **Scaffold Unit Tests**: For every logic change, propose a minimal `pytest` or `cargo test` suite.
2. **Verify against Specs**: Ensure the code exactly matches the Oracle's PLAN criteria.

## Phase 4: Code Review Readiness

- Run `Squire Clean` (Lint/Format) and `Squire Purge` (Tree-shake) before submitting.

---
*Created by Merlin_Omega for the Camelot-OS Skills Vault (03_VAULT).*
