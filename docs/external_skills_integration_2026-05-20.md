# External Skills Integration - 2026-05-20

## Integrated Sources

Two external skill repositories were cloned into Camelot as reference sources:

- `https://github.com/nemanjadotcom/skills.git`
  - Local path: `03_VAULT/Reference_Architectures/skills/nemanjadotcom-skills`
- `https://github.com/mattpocock/skills.git`
  - Local path: `03_VAULT/Reference_Architectures/skills/mattpocock-skills`

The operator-provided `shape` skill was added as a first-class Camelot-local skill:

- `.agents/skills/shape/SKILL.md`

Registry manifest:

- `03_VAULT/runtime_state/external_skill_sources_manifest.json`

## Integration Policy

External repos are reference-backed skill sources, not automatically trusted runtime code.

Rules:

- Do not execute external scripts until reviewed.
- Treat external skills as `review_required` by default.
- Promote individual skills to active adapters only after reading their `SKILL.md`, command surface, shell scripts, and dependencies.
- Generated or imported skills must preserve source URL and local path.
- Merlin may select these skills only through the universal skill database with trust, platform, and risk metadata attached.

## Notable Skills From nemanjadotcom/skills

- `shape`: auto-grill to PRD.
- `grill-me`: interactive product/plan questioning.
- `to-prd`: convert context or plan into a PRD.
- `to-issues`: break PRD into vertical GitHub issues.
- `ralph`: autonomous PRD implementation loop.
- `ralph-local`: local-file PRD implementation loop.
- `prd-to-tasks`: local PRD to task specs.
- `design-brand-kit`: brand system generation.

## Notable Skills From mattpocock/skills

- `diagnose`: disciplined debugging loop.
- `grill-with-docs`: requirements grilling plus domain docs and ADRs.
- `triage`: issue triage state machine.
- `improve-codebase-architecture`: architecture deepening.
- `setup-matt-pocock-skills`: per-repo configuration.
- `tdd`: red-green-refactor implementation.
- `to-issues`: vertical-slice issue generation.
- `to-prd`: PRD generation.
- `zoom-out`: system-context explanation.
- `prototype`: disposable prototypes.
- `handoff`: conversation handoff.
- `write-a-skill`: skill authoring workflow.

## Merlin Forge Usage

Merlin should use these skills as planning and implementation process upgrades:

- `shape` maps to `ResearchKnight` / `ForgeKnight` planning and PRD creation.
- `to-issues` maps to `Sir Alex` decomposition and vertical-slice task planning.
- `ralph` maps to `ForgeKnight` execution after PRD and issue approval.
- `tdd` maps to `ForgeKnight` implementation verification.
- `diagnose` maps to `BootKnight`, `ForgeKnight`, or `DefenseGridKnight` failure analysis.
- `improve-codebase-architecture` maps to `ResearchKnight` and `SentinelKnight` architecture review.
- `grill-with-docs` maps to `ResearchKnight` for domain-language and ADR capture.

## Shape Skill Status

`shape` is active locally as `.agents/skills/shape/SKILL.md`.

It should:

- capture a rough idea;
- inspect the codebase;
- walk the decision tree without repeated user questioning;
- stream Q/A/Why decisions live;
- write a fixed-template PRD to `./prds/<slug>.md`;
- optionally offer GitHub issue creation.

It must not:

- execute implementation;
- skip decision branches;
- ignore codebase facts;
- invent speculative scope;
- auto-push to GitHub without operator approval.

## Next Safe Step

Add a skill registry importer that reads:

- `.agents/skills/**/SKILL.md`
- `03_VAULT/Reference_Architectures/skills/**/SKILL.md`
- plugin skill metadata
- Gemini adapter skills

Then expose:

```powershell
camelot skills sources
camelot skills query --capability prd
camelot merlin forge --task "build PRD for X" --dry-run
```
