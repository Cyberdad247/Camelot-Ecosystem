| name | description |
| :--- | :--- |
| systematic-debugging | 4-phase forensic root cause analysis (Red-Green-Refactor) |

# Systematic Debugging Skill

Use when encountering any bug, test failure, or unexpected behavior.

## Phase 1: Replication & Isolation

1. **Minimum Reproducible Example**: Create a test case that fails consistently.
2. **State Snapshot**: Record the exact variable states or DOM state at the point of failure.

## Phase 2: Hypothesis Generation

1. **Identify Flow Path**: Trace the data flow from the point of failure back to the source.
2. **List Assumptions**: What must be true for the code to work? Which assumption is likely broken?

## Phase 3: Root Cause Tracing

1. **Narrow the Search**: Use binary search (commenting out sections) or log-points to isolate the exact line.
2. **Find the Polluter**: If state is corrupt, find what *set* it, not just where it's *read*.

## Phase 4: Verification before Completion

1. **Fix the Cause, not the Symptom**: Ensure the fix addresses the root logic error.
2. **Defense in Depth**: Add a regression test and ensure no secondary side-effects.

---
*Created by Merlin_Omega for the Camelot-OS Skills Vault (03_VAULT).*
