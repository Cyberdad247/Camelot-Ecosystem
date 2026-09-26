# OMNI_FORGE Mission Artifact Layout — runtime_state isolation

**Status:** ADR (accepted) · **Version:** 1.0.0 · **Date:** 2026-09-24
**Owners:** MERLIN_OMEGA (design) · ANYA_GATE (ratification) · SIR_FORGE (kinetic)
**Seal:** ⚜️_SOVEREIGN_TRUTH

## Context

The OMNI_FORGE_SUPER_AGENT spec (ukg/v4000) proposed writing factory artifacts
to `docs/blueprint.md`, `docs/task.md`, `docs/verification.md`, and
`/agent/skills.md`. That collides with two hard constraints:

1. `docs/*.md` are governance artifacts — AGENTS.md forbids agent flows from
   regenerating them (`docs/blueprint.md`, `docs/task.md`,
   `docs/verification.md` are repo-level law, not per-job scratch).
2. `/agent/skills.md` does not exist (real surface: `vfs/skills.md`,
   `.agent/Skills.md`), and runtime mutation of skill files contradicts the
   immutable Knight/Soul admission property validated by
   `harness/contracts/validate_authority_closure.py`.

## Decision

Each factory mission gets an isolated, hash-pinned workspace:

```
03_VAULT/runtime_state/missions/<mission_id>/
  mission.json          intent snapshot (id, objective, steps, status)
  blueprint.json        frozen schemas/types/HLD        (Step_2 artifact)
  task_dag.json         decomposed task DAG             (Step_3 artifact)
  skills_manifest.json  per-mission tool contracts      (Step_4 artifact)
  verification.json     crucible / Rigor Ladder results (Step_5 artifact)
  receipts/NNN_step.json  append-only sha256 write receipts
```

Mapping from the spec's prose artifacts:

| Spec artifact | Replaced by | Why |
|---|---|---|
| `/docs/blueprint.md` | `missions/<id>/blueprint.json` | governance doc stays authoritative |
| `/docs/task.md` | `missions/<id>/task_dag.json` | ditto; JSON is machine-consumable by squires |
| `/docs/verification.md` | `missions/<id>/verification.json` | verdicts are data, not prose |
| `/agent/skills.md` | `missions/<id>/skills_manifest.json` | no runtime mutation of global skill surface |

### Enforcement (`control_plane/mission_layout.py`)

- `MissionSession._safe_child` refuses absolute paths, `..` escapes, and any
  `is_governance_path()` hit — governance basenames (`PROVENANCE_LEDGER.md`,
  `HELIO_PATCH.json`, `config.json`, `omnivoice-router.js`) and any path
  under `docs/` are unwritable **at any depth**, defense in depth on top of
  the root confinement itself.
- Every `write_artifact` emits a sha256 receipt; `verify_mission()` re-hashes
  and reports `PINNED` / `MUTATED` / `MISSING` per artifact. Post-hoc
  tampering is detectable, mirroring the Gate 5 provenance philosophy.
- Only the five canonical artifact basenames are accepted, keeping the
  layout deterministic for the crucible and downstream consumers.

### Governance-doc write policy

Nothing under `docs/` or any ledger mirror is written by mission flows.
Aggregated, human-readable summaries may be *proposed* as new files under
`docs/architecture/` or `03_VAULT/runtime_state/` via a separate reviewed
change — never auto-emitted by a mission.

## Alternatives considered

- **Write per-mission files next to governance docs** (`docs/missions/<id>/`):
  rejected — blurs the governance/runtime boundary and grows a
  human-authoritative tree with machine artifacts.
- **VFS position-addressed endpoints** (`vfs://worldtree/...`): viable later
  once the mission runner is VFS-registered; runtime_state is the
  established staging home (`03_VAULT/runtime_state/` precedent, and
  AGENTS.md names it as proposed-crystal staging).
- **Global skills mutation with rollback**: rejected — contradicts immutable
  authority closure; per-mission manifests referenced by the harness are
  strictly safer.

## Consequences

- Mission artifacts are ephemeral-by-default, hash-pinned, and crucible-auditable.
- `//CARTRIDGE_VERIFY`-style checks can assert "no governance writes" by
  construction, not by diff review.
- Downstream squires consume `task_dag.json` directly instead of parsing prose.
- The five factory runes (when wired — deferred work) route their outputs to
  this layout rather than to `docs/`.

## Verification

- `python -m control_plane.mission_layout --test` — 11/11 PASS
  (governance guard, hash pinning, mutation detection, escape/unknown-artifact guards).
- `python -m control_plane.infra.cartridge_crucible --test` — 13/13 PASS
  (5 gates incl. Z3-grounded HITL and seal→verify drift detection).
