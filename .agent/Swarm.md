# Swarm And Paladin Review Backplane

The swarm layer is a practical review model for Camelot-OS work. It does not
create autonomous workers unless the active harness and user approval allow it.

## Dispatch Defaults

- Keep parallel work bounded by the active system resources.
- Use subagents only when the current harness supports them and the user has authorized delegation.
- Do not spawn broad scans when a named live command or entrypoint should be checked first.
- Stop before any HITL, secret, destructive, or credential-sensitive action.

## Paladin Review Gate

Before treating a change as ready, review it through these four lenses:

| Lens | Checks |
|---|---|
| Velocity | Does it solve the current task without overbuilding or dragging in stale assumptions? |
| Archivist | Does it match repository conventions, docs, schemas, and existing runtime surfaces? |
| Skeptic | Does it expose secrets, weaken safety gates, introduce brittle logic, or hide failures? |
| Weaver | Does it fit adjacent systems, UI conventions, workflows, and source-of-truth hierarchy? |

## Merge Readiness

- Required checks must pass or the remaining caveat must be stated plainly.
- Runtime claims require runtime evidence.
- Documentation claims must distinguish live behavior from future work.
- Rollback means reverting only the current change set, never unrelated user work.
