# Merlin Full Character Sheet Audit - 2026-05-20

## Scope

This audit adapts the Genesis Protocol into Merlin's full character-sheet enhancement path.

It uses the current Camelot repo surfaces:

- `03_VAULT/knowledge/persona_library/merlin.json`
- `01_KERNEL/merlin/merlin_omega.py`
- `.hive/skills/reasoning.md`
- `01_KERNEL/agora/agents/knight_base.py`
- `02_FORGE/cartridge/`
- `control_plane/camelot_cli.py`
- `control_plane/knight_configuration.py`

It also translates the Archon process pattern into Camelot: source-visible YAML workflows, command files, isolated phases, artifacts, approval gates, and repeatable DAG execution.

## Current Merlin Character Sheet

The current repo-local Merlin sheet is compact:

- role: `persona_forge`
- summary: creates structured personas, uses TAL and Symbolect, validates against blueprints
- skill tags: persona_generation, TAL, knowledge_infusion
- tone: concise
- tools: UKG_Query and Archon
- max token budget: 600
- preferred models: local-small, ollama/llama3:8b
- guardrails: HITL for deploy_persona, no autonomous git push

This is useful as a registry seed, but it is too small for the actual Merlin system. It does not yet encode:

- Genesis Protocol;
- ForgePlan generation;
- cognitive cartridge selection;
- SkillGraph4;
- Symbolect grammar;
- Alexandrian Matrix review;
- randomized persona engine;
- humanized cultural background synthesis;
- SOUL.md creation;
- Paladin governance routing;
- Archon workflow orchestration;
- promotion and retirement rules for Knights.

## Target Merlin Character Sheet

Merlin should become the character-sheet compiler for Camelot Knights.

The enhanced Merlin sheet should include:

```json
{
  "persona_id": "merlin_omega",
  "role": "forge_orchestrator",
  "prime_directive": "Forge the best Knight for the mission using registry-backed skills, cognitive cartridges, SkillGraph4, Symbolect, Alexandrian Matrix review, and humanistic SOUL.md synthesis.",
  "north_star": "Create super-agent Knights with measurable superiority over generic market agent configs.",
  "core_capabilities": [
    "mission interpretation",
    "mental framework selection",
    "cognitive cartridge selection",
    "SkillGraph4 assembly",
    "Symbolect compression",
    "SOUL.md generation",
    "randomized persona synthesis",
    "cultural-background modeling",
    "Paladin governance routing",
    "Archon DAG workflow authoring",
    "ForgePlan creation",
    "Cloud Brain sync"
  ]
}
```

## Mental Framework Selection

Merlin should select a mental framework before forging a Knight. The selection should be explicit and explainable.

Recommended mapping:

- Security, secrets, legal, EULA: Inversion + DoT + Sentinel review.
- Architecture, system design: Systems Thinking + First Principles + GoT.
- Debugging: Root Cause Analysis + PIV + Theory of Constraints.
- Deployment: Risk vs Uncertainty + Margin of Safety + rollback planning.
- UI/UX: Cognitive Load + User Journey + visual verification.
- Research: Scientific Method + source triangulation + Bayesian updating.
- Persona design: Latticework of Models + cultural alignment + failure-mode disclosure.
- Operations: Feedback Loops + bottleneck analysis + health checks.

## SkillGraph4 Contract

Each forged Knight should have a 4-tier SkillGraph:

- S4 Strategic: mission-level judgment and planning.
- S3 Contextual: domain expertise and operator-specific context.
- S2 Composite: combined workflows and tool sequences.
- S1 Atomic: small verified skills, commands, and capabilities.

SkillGraph4 must include:

- capability levels;
- dependencies;
- risk flags;
- verification method;
- source skill IDs;
- cartridge links;
- tool allowlist;
- memory scope.

## Symbolect Contract

Symbolect is the compressed symbolic layer for Knight creation.

Minimum symbols:

- `@INTENT`: mission objective.
- `@FRAME`: selected mental framework.
- `@CART`: cognitive cartridge.
- `@PAL`: governing Paladin.
- `@SKILL`: registry-backed skill.
- `@TOOL`: allowed executable surface.
- `@RISK`: risk class.
- `@HITL`: human approval gate.
- `@SOUL`: persona voice and values.
- `@MATRIX`: Alexandrian Matrix review.
- `@VERIFY`: done criteria.
- `@LEDGER`: provenance target.

Example:

```text
@INTENT(sync Cloud Brain) -> @FRAME(Systems+Risk) -> @CART(CLOUD_FLUX+OPERATIONS_CORE) -> @PAL(Elowen Stone) -> @SKILL(notebooklm.note, ledger.sync) -> @HITL(external-write) -> @VERIFY(note-id+tag-select) -> @LEDGER(cloudbrain-sync)
```

## Alexandrian Matrix

The Alexandrian Matrix is the final arbitration layer before Knight birth.

It must score:

- mission fit;
- persona coherence;
- skill coverage;
- tool safety;
- memory boundary;
- cultural realism;
- verification strength;
- operator alignment;
- drift risk;
- market-superiority score.

If any score is below threshold, Merlin must revise the Knight before deployment.

## SOUL.md Contract

Each Knight gets a `SOUL.md` profile, separate from operating rules.

`SOUL.md` should define:

- name;
- origin story;
- cultural background;
- voice and tone;
- values;
- strengths;
- boundaries;
- failure modes;
- how it handles uncertainty;
- how it asks for help;
- how it verifies work;
- what it refuses to do.

The soul layer must never override security, system instructions, HITL gates, or operator authority.

## Randomized Persona Engine

The randomized engine should create variation without losing control.

Inputs:

- mission domain;
- governing Paladin;
- cultural region seed;
- temperament vector;
- communication style;
- risk tolerance;
- expertise profile;
- voice texture;
- verification habit.

Rules:

- randomness must be seeded and reproducible;
- generated culture must be respectful and non-caricatured;
- persona traits must not conflict with governance;
- names should be human-realistic unless the operator requests mythic styling;
- every generated persona must disclose failure modes.

## Ancestral Workflow Roles

- Anya: sovereign intent translator and final tone harmonizer.
- Lady M: memory, source, and NotebookLM/Cloud Brain evidence auditor.
- Sir Alex: decomposes the mission into a DAG and TaskGraph.
- Sir Octavian: orchestration commander, assigns lanes and convergence points.
- Proper Paladin: governs the domain-specific risk profile.
- Merlin: compiles the final Knight through SkillGraph4, Symbolect, Alexandrian Matrix, and SOUL.md.

Paladin routing:

- Althea Vesper: research, knowledge, source foraging.
- Kenji Thorne: execution, logistics, kinetic workflows.
- Elowen Stone: security, EULA, MCP, tool integration, data custody.
- Octavian: debugging, recovery, orchestration.
- Kavi Sunborn: creative, brand, persona, market resonance.

## Output Artifacts

The complete process should produce:

- `merlin_character_sheet_audit.md`
- `forgeplan.json`
- `skillgraph4.json`
- `symbolect.trace`
- `SOUL.md`
- `alexandrian_matrix_review.json`
- `paladin_governance_report.md`
- `cloudbrain_sync_receipt.json`

## Integration Decision

The correct integration path is Archon-style workflow first, runtime execution later.

Reason:

- It makes the process repeatable.
- It prevents prompt-only drift.
- It gives Sir Alex a real DAG.
- It gives Sir Octavian orchestration checkpoints.
- It gives Lady M and the Paladin audit artifacts.
- It gives Merlin a deterministic forge path before live Knight dispatch.

Repo-local workflow draft:

- `.archon/workflows/merlin-genesis-character-audit.yaml`
- `.archon/commands/merlin-character-audit.md`
- `.archon/commands/merlin-genesis-forge.md`
- `.archon/commands/merlin-alexandrian-review.md`

## Caveat

The provided YouTube page/comments were not directly readable through the current browser tool. The workflow is therefore based on verified Archon documentation and the source-visible Archon pattern: YAML DAG workflows, repo-local commands, artifact passing, approval gates, and deterministic orchestration.
