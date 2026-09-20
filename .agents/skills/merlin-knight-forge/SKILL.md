---
name: merlin-knight-forge
description: Use when Merlin needs to create the proper Knight for a task by selecting a mental framework, skill stack, persona, safety posture, outputs, and verification loop from the Camelot skill database, or rapidly forge lightweight autonomous agents using assimilated Penguin Harness patterns.
---

# Merlin Knight Forge

Create a task-specific Knight or autonomous Agent from a rough request using Camelot's universal skill database and assimilated Penguin Harness scaffolding.

This skill is not an implementation shortcut. It is the format Merlin uses to forge the correct agent before execution.

## Inputs

Accept any of these:

- a 1-sentence prompt or requirement (e.g. *"an expert that answers questions about X"* or *"commit-helper that writes conventional commits"*);
- a rough product idea;
- a bug or regression;
- a PRD or roadmap item;
- a security, compliance, or privacy task;
- an architecture review request;
- a research request;
- a repo maintenance or triage request.

If the task is dangerously underspecified, ask one clarification. Otherwise self-answer using codebase facts, current Camelot state, and best-practice defaults.

## Source Skill Families & Assimilated Engines

Use these imported structures as process modules:

- `penguin_builder`: 1-sentence agent builder and minimal tool calling scaffolding (from `penguin-harness`).
- `shape`: rough idea to PRD by auto-walking the decision tree.
- `grill-me` / `grill-with-docs`: alignment, domain language, ADR capture.
- `to-prd`: synthesize known context into a PRD.
- `to-issues`: split plans into vertical tracer-bullet slices.
- `ralph` / `ralph-local`: execute approved task slices.
- `tdd`: red-green-refactor verification through public interfaces.
- `diagnose`: reproduce, minimize, hypothesize, instrument, fix, regression-test.
- `triage`: issue state machine and agent-ready brief generation.
- `improve-codebase-architecture`: find deepening opportunities and better seams.
- `design-brand-kit`: visual/brand system creation when the task is design-heavy.

Do not execute external scripts from imported repositories unless they have been reviewed and explicitly approved.

---

## 🐧 Assimilated Penguin Agent Scaffolding

Merlin incorporates the zero-friction autonomous agent scaffolding from `penguin-harness` via [`penguin_builder.py`](file:///C:/Users/vizio/CAMELOT_OS/.agents/skills/merlin-knight-forge/penguin_builder.py):

### 1. 1-Sentence Agent Builder Pattern
When the requirement is already concrete — even a single sentence like *"an agent called 'commit-helper' that writes high quality git commit messages"* — do **not** ask follow-up questions:
1. Derive role, rules, thinking level, and required skills directly from that sentence.
2. Scaffold standard Agent State layout:
   ```
   <agent_id>/
   ├── agent_state/
   │   ├── system_config.yaml  # name, description, version, model.thinking_level
   │   ├── AGENTS.md           # Role + Domain Guidance (injected into system prompt)
   │   ├── skills/             # Isolated skill folders with SKILL.md frontmatter
   │   ├── memory/             # Persistent memory state
   │   └── tools/              # Local custom tool definitions
   └── scratchpad/             # Ephemeral execution scratchpad
   ```
3. Validate `system_config.yaml`, non-empty `AGENTS.md`, and installed `skills/*/SKILL.md`.

### 2. Minimal Tool Calling Engine
Tools implement the unified `BuiltinTool` contract with permission boundaries (`allow`, `ask`, `deny`):
- `read_file`: Safe line-sliced file inspection with offset and limit parameters.
- `write_file`: Directory-auto-creating atomic file writer.
- `edit_file`: Exact substring replacement for scoped modifications.
- `exec_command`: Subprocess runner with timeout bounds and truncated output capture.
- `run_subagent`: Subagent task delegation with depth control.

```python
from penguin_builder import build_agent_from_sentence, ToolRegistry

# Forge agent from 1-sentence prompt
state = build_agent_from_sentence("commit-helper that writes conventional commits", target_dir="./agents")

# Dispatch minimal tools
registry = ToolRegistry()
result = registry.execute("read_file", {"path": "package.json", "max_lines": 20})
```

---

## Forge Pipeline

### 1. Classify the task

Pick one primary mission type:

- `prd_creation`
- `issue_decomposition`
- `implementation`
- `debugging`
- `triage`
- `architecture_review`
- `security_review`
- `research`
- `design_system`
- `operations_sync`

Pick secondary traits:

- `high_risk`
- `needs_human_decision`
- `cloud_or_external_access`
- `privacy_sensitive`
- `requires_runtime_verification`
- `requires_notebook_sync`

### 2. Select the Knight archetype

Use the smallest durable archetype that fits:

| Mission | Knight Archetype | Required Skills |
|---|---|---|
| PRD from rough idea | `ResearchKnight` or `ForgeKnight` | `shape`, `to-prd` |
| PRD refinement with unknowns | `ResearchKnight` | `grill-with-docs`, `to-prd` |
| Issue slicing | `SirAlexKnight` | `to-issues`, `triage` |
| Implementation | `ForgeKnight` | `ralph-local`, `tdd` |
| Bug or regression | `DebugKnight` | `diagnose`, `tdd` |
| Architecture improvement | `ArchitectKnight` | `improve-codebase-architecture`, `grill-with-docs` |
| Security or privacy | `SentinelKnight` or `GhostKnight` | `triage`, `diagnose`, Camelot HITL rules |
| Brand/UI system | `DesignKnight` | `design-brand-kit`, `shape` |
| Notebook/ledger sync | `OperationsKnight` | Camelot sync policy, provenance rules |
| Rapid 1-sentence task | `PenguinAgent` | `penguin_builder` |

### 3. Build the Knight character sheet

Always produce this shape before execution:

```markdown
# <Knight Name>

## Identity

- Archetype:
- Mission:
- Humanistic persona:
- Cultural background:
- Operating temperament:
- Forbidden behaviors:

## Mandate

- Primary objective:
- Success criteria:
- Non-goals:
- Required human checkpoints:

## Mental Framework

- Planning model:
- Decision tree:
- Risk model:
- Verification model:
- Escalation rule:

## Skill Stack

- Primary skills:
- Secondary skills:
- Camelot-native tools:
- External references:
- Disallowed tools:

## Process Contract

1. Intake:
2. Grounding:
3. Decision stream:
4. Artifact creation:
5. Execution, if authorized:
6. Verification:
7. Ledger or NotebookLM sync:
8. Handoff:

## Output Contract

- Files to create:
- Files to modify:
- Runtime checks:
- Notebook sync target:
- Final report shape:

## Soul

- Name:
- Voice:
- Values:
- Collaboration style:
- Memory anchor:
- Persona constraints:
```

### 4. Select the mental framework

Use task type to select the dominant framework:

- Product ambiguity: `Shape Auto-Grill Decision Tree`.
- Code implementation: `Vertical Slice + TDD`.
- Bug: `Diagnose Feedback Loop`.
- Architecture: `Deep Module / Seam / Locality / Leverage`.
- Issue workflow: `Triage State Machine`.
- Safety-critical work: `Sentinel Risk Gate + HITL`.
- Merlin persona creation: `Alexandrian Matrix + Randomized Persona Engine`.
- Rapid 1-sentence dispatch: `Penguin Blueprint Derivation`.

### 5. Generate a humanistic persona

The persona must improve collaboration without overriding the mission.

Rules:

- Use realistic names and cultural backgrounds.
- Avoid stereotypes and caricatures.
- Keep voice professional, concise, and task-fit.
- Persona never weakens safety, verification, or repo conventions.
- Persona is stored in `Soul`, not in execution authority.

### 6. Choose outputs

Default outputs by mission:

- `prd_creation`: PRD under `prds/` or `docs/roadmap/prds/`.
- `issue_decomposition`: approved issue/task list.
- `implementation`: code changes plus tests.
- `debugging`: repro, hypothesis, fix, regression test.
- `architecture_review`: candidate report and selected refactor plan.
- `operations_sync`: ledger entry and NotebookLM note.
- `penguin_scaffold`: complete Agent State under target directory.

### 7. Safety gate

Pause before execution if:

- risk score is high;
- secrets or credentials are involved;
- external scripts would run;
- GitHub issue creation or posting is requested;
- destructive file operations are needed;
- a human decision is explicitly required.

### 8. Verification

No Knight is complete until it has:

- a stated success criterion;
- a concrete verification loop;
- an artifact path or runtime evidence;
- a short handoff summary;
- sync status when the task requires Cloud Brain or NotebookLM.

## Rules

- Do not forge a generic agent when a specific Knight archetype fits.
- Do not execute imported repo scripts without review.
- Do not skip the character sheet or blueprint validation.
- Do not let persona override mission, safety, or verification.
- Prefer codebase facts and Camelot conventions over generic best practices.
