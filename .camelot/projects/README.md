# Cybertron Dawning Project Workflow

This directory is the project-isolation bay for the Camelot-OS `//DAWNING`
protocol.

The Dawning protocol turns a named intent into an isolated project folder, runs a
bounded OS map audit, invokes the Lady M Cloud Brain sync path, and records the
latest state under `03_VAULT/runtime_state/cybertron_dawning_latest.json`.

## What We Are Building

The Cybertron Dawning Harness is a repeatable startup workflow for new Camelot
initiatives. It gives each project a clean local workspace without mixing its
planning, tasks, and verification artifacts into the rest of the OS.

The workflow has four jobs:

1. Wake the Dawning lane with `//DAWNING <project_name>`.
2. Audit the main Camelot surfaces: `01_KERNEL`, `02_FORGE`, `03_VAULT`,
   `control_plane`, `scripts`, and `.agent`.
3. Sync the Dawning event through Lady M / Cloud Brain when available.
4. Create or refresh `.camelot/projects/<project_name>/` with project-local
   planning files.

The implementation lives in:

- `scripts/cybertron_dawning.py`
- `control_plane/runic_router.py`
- `control_plane/harness.py`
- `03_VAULT/PROMPTS/SUPER_HARNESS.md`
- `tests/test_cybertron_dawning.py`

## How To Start A New Dawning Project

From the Camelot-OS repo root:

```powershell
.venv\Scripts\python.exe -m control_plane.runic_router --rune DAWNING --task "my_project"
```

For a direct local run without queueing through the router:

```powershell
.venv\Scripts\python.exe scripts\cybertron_dawning.py my_project
```

The project name is sanitized before it becomes a directory name. For example,
`../Alpha Nexus!` becomes `Alpha_Nexus`.

## Generated Project Files

Each Dawning project folder contains:

- `blueprint.md` - the intent, architecture, boundaries, and accepted evidence.
- `task.md` - the implementation checklist for the current work.
- `verification.md` - commands, expected results, and final proof of completion.
- `manifest.json` - the generated project name, original requested name,
  protocol marker, timestamp, and file list.

Use these files as the project contract:

- Put the "why and what" in `blueprint.md`.
- Put the "what to do next" in `task.md`.
- Put the "how we know it worked" in `verification.md`.
- Do not put secrets, tokens, passwords, or API keys in any of these files.

## Bio-Knight Workflow

The Dawning lane uses the existing Camelot control plane rather than inventing a
parallel process.

- Sir Codex implements scoped code changes and verification.
- Sir Forge executes the queued `//DAWNING` harness job because it is already
  mapped to Cloud Brain.
- Lukas Forge is recorded as the lead Bio-Knight for the Dawning audit and
  topology work.
- Lady M handles memory sync through `control_plane.cloudbrain_sync` when the
  local environment allows it.
- Merlin, Alex, Octavian, Apis, and Sir Codex are recorded in the Dawning state
  as the awakened planning, routing, memory, foraging, and implementation lane.

The router metadata keeps the Bio-Knight intent:

```json
{
  "action": "cybertron_dawning",
  "lead_bio_knight": "lukas_forge"
}
```

The queued executor remains `sir_forge` so Camelot's existing Cloud Brain
hydration map stays compatible.

## Standard Workflow

1. Create or refresh the project:

   ```powershell
   .venv\Scripts\python.exe -m control_plane.runic_router --rune DAWNING --task "project_name"
   ```

2. Open the generated folder:

   ```powershell
   Get-ChildItem .camelot\projects\project_name
   ```

3. Fill out `blueprint.md` with:

   - project goal
   - user-facing outcome
   - affected Camelot surfaces
   - accepted evidence classes: confirmed, planned, aspirational, rejected
   - rollback or pause conditions

4. Break the work into `task.md`:

   - one checklist item per implementation step
   - expected files to modify
   - expected command or test for each step
   - any HITL gate that must not be auto-approved

5. Define `verification.md` before claiming the project is complete:

   - exact commands run
   - pass/fail result
   - runtime artifacts created
   - caveats such as network, Cloud Brain, or sandbox limits

6. Implement through the normal Camelot lane:

   ```powershell
   .venv\Scripts\python.exe -m pytest tests\test_cybertron_dawning.py
   .venv\Scripts\python.exe -m py_compile scripts\cybertron_dawning.py control_plane\runic_router.py control_plane\harness.py
   ```

7. Confirm the latest Dawning state:

   ```powershell
   Get-Content 03_VAULT\runtime_state\cybertron_dawning_latest.json
   ```

## Harness Execution Path

There are two ways the protocol can run:

### Router Path

`control_plane.runic_router` accepts `//DAWNING`, adds metadata, and appends the
task to `logs/harness_queue.jsonl`.

```powershell
.venv\Scripts\python.exe -m control_plane.runic_router --rune DAWNING --task "project_name"
```

Expected result:

- rune: `//DAWNING`
- knight: `sir_forge`
- action: `cybertron_dawning`
- queued: `true`

### Harness Path

`control_plane.harness` sees queued directives that start with `//DAWNING` and
runs:

```powershell
.venv\Scripts\python.exe scripts\cybertron_dawning.py project_name
```

Expected harness result:

- status: `dawning_complete`
- returncode: `0`
- project: `<project_name>`
- state: `03_VAULT/runtime_state/cybertron_dawning_latest.json`

## Runtime State

The latest protocol state is written here:

```text
03_VAULT/runtime_state/cybertron_dawning_latest.json
```

That file records:

- protocol name
- event type
- timestamp
- repo root
- audited nodes and bounded file counts
- project directory and manifest details
- Lady M sync status
- awakened pantheon list

If Cloud Brain or NotebookLM is blocked, the Dawning script should still finish
locally and record a warning instead of blocking the project.

## Completion Rules

A Dawning project is not complete just because the folder exists.

It is complete when:

- `blueprint.md` states the project goal and boundaries.
- `task.md` lists completed implementation steps.
- `verification.md` contains the commands and results that prove the work.
- `cybertron_dawning_latest.json` reflects the latest run.
- Focused tests or compile checks pass.
- Any Cloud Brain caveat is stated honestly.

## Safety Rules

- Never store secrets or real API keys in project files.
- Never edit `PROVENANCE_LEDGER.md` directly.
- Never auto-approve a HUMAN_GATE or high-risk Sentinel prompt.
- Keep Dawning projects scoped under `.camelot/projects/`.
- Treat `03_VAULT/runtime_state/cybertron_dawning_latest.json` as runtime
  evidence, not a permanent design document.
- If a project changes shared Camelot behavior, verify through the relevant
  router, harness, test, and runtime artifact.
