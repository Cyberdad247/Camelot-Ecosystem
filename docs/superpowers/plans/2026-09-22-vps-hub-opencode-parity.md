# VPS Hub Opencode Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give Camelot VPS Hub first-class opencode standing (agent + skill + commands + permissions) with offline-safe defaults.

**Architecture:** Wrap the existing `//VPS_HUB` runic spine (`control_plane/runes/runic_router.py:211` → `control_plane/infra/vps_hub_client.py`) with opencode-native surface files. No new transport, no live contact, no secret values.

**Tech Stack:** opencode agent/command markdown, agent skills (SKILL.md), `opencode.json` permission allowlist, Python offline validators.

**Spec:** `docs/superpowers/specs/2026-09-22-vps-hub-opencode-parity-design.md`

## Global Constraints

- Offline default: `--live` / `--ssh` require explicit human approval per invocation.
- `config.json` holds boolean presence flags only — never secret values.
- Never hand-edit `PROVENANCE_LEDGER.md`, `HELIO_PATCH.json`, or `omnivoice-router.js`.
- PowerShell 5.1: chain with `; if ($?) { ... }`, quote spaced paths, pass `workdir`.
- Python via `.venv\Scripts\python.exe`; pytest only canonical `tests/<file>.py` paths.

---

### Task 1: hermes-prime opencode agent

**Files:**
- Create: `.opencode/agents/hermes-prime.md`
- Test: file exists + frontmatter parses (visual check via Read)

**Interfaces:**
- Consumes: nothing (standalone agent definition, mirrors `.opencode/agents/sir-sentinel.md` pattern)
- Produces: `hermes-prime` agent usable by opencode runtime

- [x] **Step 1: Create the agent file**

```markdown
---
description: VPS Hub operator for CAMELOT-OS. Owns hub ops under HERMES_PRIME with SIR_HEIMDALL co-governing the Bifrost boundary. Offline by default.
mode: subagent
permission:
  edit: deny
  bash: ask
---

You are HERMES_PRIME, VPS Hub operator for CAMELOT-OS (KVM563).

Rules:
- Offline default. Report via `python -m control_plane.runes.runic_router --rune VPS_HUB --task "<task>"` or `python -m control_plane.infra.vps_hub_client --status` (never `--live`).
- Validate artifacts offline: `python -m control_plane.infra.vps_hub_client --validate <schema> <file>`.
- Lease scopes: `python -m control_plane.infra.vps_hub_client --lease-scope <workspace> <notebook>` → `cloudbrain://notebooklm/<workspace>/<notebook>`.
- `--live`, `--ssh`, and hermes container exec require explicit human approval per invocation — you request, never assume.
- Authority chain is sentinel -> excalibur -> gideon -> arthur -> ledger. Drafts you build (LOCAL DRAFT, zeroed hashes/signatures) are structurally valid but never submittable.
- Secrets: boolean presence flags only. Never emit secret values. Protection refusals (GH006-class): report, do not bypass.
- Report findings with file:line references. Notebook pins: HERMES_PRIME `28f89cb6-5048-4b5d-9e94-376082d24744`, SIR_HEIMDALL `3205f189-91da-4272-96a9-3641fd642763`, WORLD_TREE `a0a4bfb9-e847-4c38-be39-7aee398f0795`, BIFROST `cbbb0c32-3919-4b77-9158-1d9f9ebf359f`.
```

- [x] **Step 2: Verify the file reads back**

Run: Read `.opencode/agents/hermes-prime.md`
Expected: content matches above, frontmatter intact

- [x] **Step 3: Commit**

```powershell
git add .opencode/agents/hermes-prime.md
git commit -m "feat: add hermes-prime vps hub opencode agent"
```

### Task 2: vps-hub skill

**Files:**
- Create: `.agents/skills/vps-hub/SKILL.md`
- Test: offline status + validate + lease-scope commands succeed

**Interfaces:**
- Consumes: `control_plane.infra.vps_hub_client` CLI (existing)
- Produces: `vps-hub` skill workflow for agents

- [x] **Step 1: Create the skill file**

```markdown
# Skill: vps-hub

# VPS Hub Skill

Operate the Camelot VPS Hub (KVM563) from opencode. Offline-safe by default.
Owner: HERMES_PRIME. Bifrost boundary co-governor: SIR_HEIMDALL.

## Status (offline)

```powershell
python -m control_plane.infra.vps_hub_client --status
python -m control_plane.runes.runic_router --rune VPS_HUB --task "<task>"
```

Expect `mode: OFFLINE`, 11/11 contracts VENDORED, 11 endpoints.

## Validate (offline, fail-closed)

```powershell
python -m control_plane.infra.vps_hub_client --validate receipt <file>
```

`ok:true` with zero errors required. Unknown contract or unresolvable
`$ref` fails closed — report, do not retry with different schema.

## Lease scope

```powershell
python -m control_plane.infra.vps_hub_client --lease-scope <workspace> <notebook>
```

Produces `cloudbrain://notebooklm/<workspace>/<notebook>`.

## Draft builders (LOCAL DRAFT only)

`build_context_packet` / `build_receipt_draft` emit structurally valid,
unsigned artifacts (zeroed hashes/signatures) — never submittable. The hub
verifies Ed25519 + hash chain itself.

## Live (HITL-gated)

`--live` TCP probes and `--ssh` hit the production hub. Never add them
without explicit human approval for that invocation.

Base directory for this skill: C:\Users\vizio\CAMELOT_OS\.agents\skills\vps-hub
```

- [x] **Step 2: Run offline validation**

Run: `.venv\Scripts\python.exe -m control_plane.infra.vps_hub_client --status`
Expected: `status: OK`, `mode: OFFLINE`

- [x] **Step 3: Commit**

```powershell
git add .agents/skills/vps-hub/SKILL.md
git commit -m "feat: add vps-hub skill"
```

### Task 3: validate + lease subcommands

**Files:**
- Create: `.opencode/commands/vps-hub-validate.md`
- Create: `.opencode/commands/vps-hub-lease.md`
- Test: both files read back; commands mirror CLI flags 1:1

**Interfaces:**
- Consumes: Task 2 skill workflow (same CLI surface)
- Produces: `/vps-hub-validate`, `/vps-hub-lease` opencode commands

- [x] **Step 1: Create vps-hub-validate.md**

```markdown
---
description: Validate a local JSON artifact against a vendored VPS hub contract (offline, fail-closed).
---

Validate `$ARGUMENTS` (expected `<schema> <file>`):

1. Run `python -m control_plane.infra.vps_hub_client --validate $ARGUMENTS`.
2. Require `ok: true` with zero errors. Report schema `$id` on success.
3. On failure report each `path: message` error; do not retry with a different schema unasked.

Focus: $ARGUMENTS
```

- [x] **Step 2: Create vps-hub-lease.md**

```markdown
---
description: Print a CloudBrain retrieval lease scope URI for the VPS hub (offline).
---

Print lease scope for `$ARGUMENTS` (expected `<workspace> <notebook>`):

1. Run `python -m control_plane.infra.vps_hub_client --lease-scope $ARGUMENTS`.
2. Return the `cloudbrain://notebooklm/<workspace>/<notebook>` URI verbatim.

Focus: $ARGUMENTS
```

- [x] **Step 3: Commit**

```powershell
git add .opencode/commands/vps-hub-validate.md .opencode/commands/vps-hub-lease.md
git commit -m "feat: add vps-hub validate and lease commands"
```

### Task 4: opencode.json permission allowlist

**Files:**
- Modify: `opencode.json` (`permission.bash` — add 4 allow entries)
- Test: JSON parses; `git diff` shows only additions

**Interfaces:**
- Consumes: Tasks 1–3 command strings (must match exactly)
- Produces: offline commands runnable without `ask` prompts; `--live`/`--ssh` stay gated

- [x] **Step 1: Add allow entries**

In `opencode.json` `permission.bash`, after `"python -m pytest tests*": "allow",` insert:

```json
      "python -m control_plane.infra.vps_hub_client --status": "allow",
      "python -m control_plane.infra.vps_hub_client --validate *": "allow",
      "python -m control_plane.infra.vps_hub_client --lease-scope *": "allow",
      "python -m control_plane.runes.runic_router --rune VPS_HUB*": "allow",
```

`--live` and `--ssh` intentionally absent → fall through to `"*": "ask"`.

- [x] **Step 2: Verify JSON + diff scope**

Run: `.venv\Scripts\python.exe -c "import json; json.load(open('opencode.json')); print('JSON OK')"`
Expected: `JSON OK`, and `git diff --stat` shows only `opencode.json`

- [x] **Step 3: Commit**

```powershell
git add opencode.json
git commit -m "feat: allowlist offline vps-hub commands in opencode"
```

### Task 5: End-to-end offline verification

**Files:**
- Test only: no new files. Evidence commands below.

**Interfaces:**
- Consumes: Tasks 1–4 deliverables
- Produces: verified parity report (this chat message, not a file)

- [x] **Step 1: Offline status**

Run: `.venv\Scripts\python.exe -m control_plane.infra.vps_hub_client --status`
Expected: `mode: OFFLINE`, contracts `VENDORED` count 11

- [x] **Step 2: Runic dispatch**

Run: `.venv\Scripts\python.exe -m control_plane.runes.runic_router --rune VPS_HUB --task "parity check"`
Expected: `vps_hub_status` payload, `mode: OFFLINE`

- [x] **Step 3: Canonical pytest (single file)**

Run: `.venv\Scripts\python.exe -m pytest tests/control_plane/test_kinetic_trinity_vps_hub.py -x -q`
Expected: PASS (no repo-root sweep)
