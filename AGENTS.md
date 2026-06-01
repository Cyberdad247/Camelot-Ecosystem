# CAMELOT-OS — Codex Agent Constitution
## Working directory: C:\Users\vizio\CAMELOT_OS

You are operating inside **CAMELOT-OS**, a sovereign AI operating system built on the
Claude Code harness. Read this file completely before taking any action.

---

## Universal Bootstrap Adapter

The grounded OMEGA Ancestral bootstrap for this repository is
`UNIVERSAL_BOOTSTRAP_UKG_NANO.md`. Its shared local backplane lives under
`.agent/`:

- `.agent/local_env.md`
- `.agent/system_instructions.md`
- `.agent/Agents.md`
- `.agent/Skills.md`
- `.agent/Swarm.md`
- `.agent/workflows.md`

These files are operational guidance for Camelot-OS agents. They do not override
the active harness system instructions, sandbox rules, HITL gates, or the
repository constraints below. If the bootstrap vocabulary conflicts with live
runtime behavior, trust the live router and verified repository state.

---

## Identity & Constraints

- Project owner: **SIR_BORIS** (Invisioned Marketing Inc.)
- **King Arthur** is the governing body and ethical overseer of Camelot-OS.
  The King represents the authorized user within the Camelot developer
  bloodline, currently **VaShawn O. Head**, also known operationally as
  **Vizion**. This identity must not be confused with **Vizion Wealth**, which
  is the user's avatar/brand construct rather than the governing operator.
  Agentic Knights running in the background remain subordinate to this
  authority and must preserve the King's ethical and moral compass.
- Privacy rule: API keys MUST NEVER be stored as actual values — only boolean presence
  flags in `config.json`. Keywords like `secret`, `token`, `key`, `password` route to
  SIR_GHOST which is air-gapped (no cloud).
- Do not modify `PROVENANCE_LEDGER.md` directly — the hook writes AUTO entries.
- Do not run destructive shell commands without HITL confirmation.

---

## Repository Layout

```
CAMELOT_OS/
├── 01_KERNEL/          # Swarm graph, graph_orchestrator.py
├── bin/
│   ├── awaken.py       # Boot sequencer — run to start all services
│   ├── knight_session.py   # Rich REPL (ks command)
│   └── camelot_portable.py # Portable REPL (camelot command / dist/camelot.exe)
├── control_plane/
│   └── runic_router.py # //RUNE dispatch engine
├── squires/            # CLARITY_CORE v1.0.0 — 8-squire codebase intelligence
│   └── colony.py       # Main CLI entry point
├── 03_VAULT/training/configs/CLAUDE.md  # Full constitution (source of truth)
├── PROVENANCE_LEDGER.md                 # Immutable change log
├── dist/camelot.exe    # Portable binary (PyInstaller, 15.4 MB)
└── config.json         # Runtime config — boolean API key presence flags only
```

---

## Knight Roster

| Knight | Role | Primary model |
|---|---|---|
| SIR_BORIS | Lead architect, Crucible Conductor, 13-agent critique | Gemini |
| SIR_ALEX | Task planner, DAG orchestrator | Gemini |
| SIR_FORGE | Kinetic code execution, //FORGE dispatcher | Gemini |
| SIR_CODEX | High-velocity implementation and rapid prototyping | OpenAI Codex |
| SIR_SENTINEL | AgentArmor, PDG, Iron Gate HITL | Gemini |
| SIR_DEBUG | PIV self-healing loop | Gemini |
| SIR_GHOST | Privacy scanner, air-gapped secrets handler | Ollama (local only) |
| LADY_APIS | BASHR research loop, context forager | Gemini |
| MERLIN_OMEGA | GoT/ToT deep reasoning, System 2 | Gemini |
| SIR_HELIO | Voice OS, //vocal, real-time pipeline | Gemini |

---

## Runic Command System

Runic commands are prefixed with `//` or `Omega_`. They bypass LLM routing and
dispatch directly to the runic router.

### Core Runes

| Rune | Knight | What it does |
|---|---|---|
| `//FORGE <task>` | SIR_FORGE | Kinetic code generation & execution |
| `//CODEX <task>` | SIR_CODEX | Direct high-velocity Codex execution lane |
| `//CONTRACT [brief]` | SIR_FORGE | Portable runtime packaging contract |
| `//SWARM <task>` | SIR_BORIS | Multi-agent colony dispatch |
| `//SCAN [path]` | Squire Colony | Full codebase intelligence scan |
| `//BOOT` | SIR_ALEX | Run `awaken.py` full boot sequence |
| `//PLAN <task>` | SIR_ALEX | Enter AST Plan Mode + Task DAG |
| `//HEAL` | SIR_DEBUG | PIV self-healing loop on last error |
| `//STATUS` | SIR_SENTINEL | Live service status + port probes |

### Omega Dispatch

`Omega_*` commands target individual knight harnesses:

```
Omega_Boris   → SIR_BORIS     (architect review)
Omega_Forge   → SIR_FORGE     (execution)
Omega_Codex   → SIR_CODEX     (rapid implementation)
Omega_Sentinel → SIR_SENTINEL (security audit)
Omega_Debug   → SIR_DEBUG     (heal loop)
Omega_Ghost   → SIR_GHOST     (privacy scan, local only)
Omega_Apis    → LADY_APIS     (research burst)
Omega_Merlin  → MERLIN_OMEGA  (deep reasoning)
```

### CLI invocation (from project root)

```powershell
# Route a rune directly
python -m control_plane.runic_router --rune FORGE --task "add retry logic to api.py"

# List all runes
python -m control_plane.runic_router --list

# Detect rune in free-form text
python -m control_plane.runic_router --detect "//SWARM build auth service"
```

---

## Squire Colony (CLARITY_CORE v1.0.0)

8-squire codebase intelligence pipeline: SCAN → INDEX → GHOST → SWEEP → JUDGE → SENTINEL → MASON

```powershell
# Full triage (interactive HITL if risk score >= 50)
python -m squires.colony triage [path]

# Individual squires
python -m squires.colony scan [path]      # Walk + hash all files
python -m squires.colony index [path]     # Extract symbols
python -m squires.colony ghost [path]     # Secret / privacy scan
python -m squires.colony vector [path]    # TF-IDF semantic index
python -m squires.colony status           # Colony health
```

Output artifact: `colony_report.md` in the scanned directory.

HITL gate: if risk score >= 50 OR secrets found, the sentinel squire
pauses and prompts `[y/N]` before continuing. Never auto-approve these.

---

## Boot Sequence

```powershell
# Full boot (all services)
python bin/awaken.py

# Quick boot (skip heavy services)
python bin/awaken.py --quick

# Interactive REPL
python bin/knight_session.py

# Portable binary (no Python required)
dist\camelot.exe
```

---

## Key Workflows

### Starting a new feature
1. `//PLAN <feature description>` — SIR_ALEX produces Task DAG
2. `//FORGE <first task>` — SIR_FORGE executes
3. `//SCAN` — verify no secrets leaked

### Debugging a failure
1. `//HEAL` — SIR_DEBUG runs PIV loop (Plan → Implement → Validate, up to 3 iterations)
2. If HITL blocked, check `harness_queue.jsonl` for queued tasks

### Security review
1. `//SCAN` or `python -m squires.colony ghost .` — GHOST squire scans for secrets
2. `Omega_Sentinel` — SIR_SENTINEL runs AgentArmor audit

---

## Running Tests

```powershell
# Python tests
.venv\Scripts\python.exe -m pytest

# Full colony triage (CI mode, no HITL)
python -m squires.colony triage . --auto-approve
```

---

## Provenance

Every file write is logged to `PROVENANCE_LEDGER.md` via the PostToolUse hook.
Format: `| ID | Task | Author | Status | Notes |`
Do not edit the ledger manually.
