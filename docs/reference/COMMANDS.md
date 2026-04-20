# CAMELOT-OS COMMAND REFERENCE v300.4.0
# Codename: UNIVERSAL_SINGULARITY
# Generated: 2026-03-31 by SIR_BORIS (Architecture Sync)

---

## RUNIC COMMANDS (`//` Prefix)

| Rune | Handler | Layer | Function |
|---|---|---|---|
| `//BOOT` | hud.py | L2 Kinetic | Rehydrate session, anchor UKG truth, restart Defense Grid |
| `//PLAN` | anya.py -> architect | L3 Neural | Merlin ToT architecture planning (no execution, visualization only) |
| `//FORGE` | hud.py -> cribo | L2 Kinetic | Lukas AST-aware code execution + Rust bundler invocation |
| `//FLEET` | camelot.py | L5 Agentic | Parallel Map-Reduce swarm deployment |
| `//SWARM` | camelot.py | L5 Agentic | Full Hive Swarm v2.0 with A2A protocol |
| `//HEAL` | anya.py -> debug | L3 Neural | Self-healing E2E validation loop (PIV cycle x3) |
| `//GENESIS` | camelot.py | L7 Ethereal | Spawn new agent via Proteus MPI vectors |
| `//ASSIMILATE` | camelot.py | L4 Semantic | ETL ingestion into UKG graph |
| `//SCAVENGE` | camelot.py | L2 Kinetic | Context hygiene sweep (token reclamation) |
| `//vocal` | boris.py | L5 Agentic | Voice AI pipeline: Oracle -> Veritas -> Lazarus |
| `//DEFENSE_INIT` | hud.py | L6 Governance | Initialize Defense Grid daemon |

---

## OMEGA RUNES (`Omega_` Prefix)

Accepted variants: `Ω_`, `Omega_`, `omega_`

### Core Operations
| Rune | Function |
|---|---|
| `Ω_SYNC` | Ouroboros bi-directional state synchronization |
| `Ω_PURGE` | Cache/memory purge |
| `Ω_STATUS` | System health beacon |
| `Ω_SILENCE` | Emergency halt all loops |
| `Ω_CLEAN` | Context hygiene enforcement |

### Reasoning & Compression
| Rune | Function |
|---|---|
| `Ω_THINK` | Council Debate (GoT-powered multi-agent deliberation) |
| `Ω_GRAPH` | GoT/DoT reasoning graph generation |
| `Ω_COMPRESS` | Triple compression stack (SAC>CCF>QFT) |
| `Ω_GLYPH` | Compress entity to UKG (Tier 3 crystal) |
| `Ω_ORACLE` | Simulation engine execution |
| `Ω_STACK` | Full Idea Stacking cycle |
| `Ω_GATEWAY` | Idea Stacking connection search |

### Generation & Deployment
| Rune | Function |
|---|---|
| `Ω_KINETIC` | Generate/deploy compiled code |
| `Ω_ACTUATE` | Singularity Engine (video/audio generation) |
| `Ω_REFORGE` | Refine output to Titanium Standard |
| `Ω_COMPILE` | DSPy prompt optimization |
| `Ω_PROMETHEUS` | Asset Factory decomposition |

### Security & Governance
| Rune | Function |
|---|---|
| `Ω_AUDIT` | Deep forensic scan |
| `Ω_SHIELD` | DoT security verification |
| `Ω_KERNEL` | Kernel scheduling state management |

### Identity & Persona
| Rune | Function |
|---|---|
| `Ω_ANYA` | 5-stage prompt compilation (APEE v6.5) |
| `Ω_PERSONA` | NPE persona binding |
| `Ω_ARCHETYPE` | Model archetype selection |
| `Ω_BESTIARY` | Manage swarm familiars |
| `Ω_EVOLVE` | Meta-agent self-improvement loop |

### Media & Research
| Rune | Function |
|---|---|
| `Ω_VOICE` | Voice AI pipeline |
| `Ω_VISION` | Visual/video generation |
| `Ω_RESEARCH` | Deep web research execution |

---

## CLI SUBCOMMANDS

Entry points: `camelot` (CLI) or `camelot-os` (HUD + REPL)

### Core Operations
| Command | Arguments | Function |
|---|---|---|
| `exec` | `"directive"` `--write` `--llm` `-p provider` | Execute directive through Anya compiler -> knight pipeline |
| `ask` | `"question"` `-p provider` `-m model` | Direct LLM query (bypasses knight routing) |
| `llm` | | List LLM providers and connection status |
| `knights` | | List available knights and their status |
| `kernel` | `"intent"` | Send intent directly to Excalibur kernel |

### Information
| Command | Arguments | Function |
|---|---|---|
| `history` | `-n count` (default: 20) | Show execution history from ouroboros.db |
| `stats` | | Knight performance statistics (calls, success rate) |
| `export` | `-o file` (default: camelot_export.json) | Export memory/state to JSON |
| `cartridges` | | List loaded knowledge cartridges |
| `bridge` | | Show CAMELOT_OS kernel bridge status (11 components) |

### Security & Storage
| Command | Subcommands | Function |
|---|---|---|
| `vault` | `list` `set` `get` `delete` | Manage AES-256-GCM encrypted secrets |
| `warden` | `status` `lockdown` `unlock` `audit` `spotlight` | Security system controls |
| `quarantine` | `status` `scan` `purge-temp` | DefenseGrid quarantine management |

### Memory & Planning
| Command | Subcommands | Function |
|---|---|---|
| `memory` | `status` `query` `session` `store` | Titan Omega memory system |
| `plan` | `list` `create` `next` `complete` `export` | Planning engine (task DAG management) |

---

## HUD INTERACTIVE MODE

Launched via `camelot-os` bash alias -> hud.py

| Input | Function |
|---|---|
| `help` | Show available commands |
| `hud` | Refresh Rich dashboard panels |
| `clear` | Clear terminal |
| `ask` / `ask@provider` | LLM query with optional provider routing |
| Any `//` prefix | Runic command dispatch |
| Any `Ω_` prefix | Omega rune dispatch via Ouroboros |
| Natural language | Saltare MCP gateway -> knight pipeline fallback |
| `exit` / `quit` / `q` | Exit Camelot OS |

---

## ANYA INTENT COMPILER

Automatic intent detection from natural language directives:

| Intent | Trigger Patterns | Routed To |
|---|---|---|
| PLAN | `plan`, `architect`, `design system`, `structure` | Sir Architect |
| CREATE | `create`, `build`, `generate`, `implement`, `write`, `scaffold` | Sir Forge |
| RESEARCH | `research`, `analyze`, `compare`, `investigate`, `explain` | Sir Researcher |
| DEBUG | `debug`, `fix`, `diagnose`, `troubleshoot`, `error`, `optimize` | Sir Debug |
| SECURE | `audit`, `security`, `vulnerab`, `harden`, `encrypt` | Sir Warden |
| DESIGN | `design`, `ui`, `ux`, `style`, `layout`, `mockup` | Sir Creative |

---

## CONTROL PLANE KNIGHT_ROUTES

Dispatch table in `control_plane/main.py`:

| Route Keywords | Knight | Domain |
|---|---|---|
| `orchestration`, `architecture`, `colony`, `critique`, `vocal` | SIR_BORIS | Multi-agent synthesis |
| `technical`, `scaffold`, `code_gen` | SIR_FORGE | Code generation |
| `security_review`, `audit` | SIR_SENTINEL | Security |
| `financial`, `roi` | SIR_VALERIAN | Finance |
| *(default fallback)* | SIR_FORGE | General execution |

---

## SQUIRE COLONY CLI

`python -m squires.colony [command] [path]`

| Command | Function |
|---|---|
| `scan` | SQUIRE_SCAN: Ghost file vs active tissue detection |
| `index` | SQUIRE_INDEX: B-Tree directory scanner (<1% CPU) |
| `ghost` | SQUIRE_GHOST: Alien process detector + quarantine |
| `vector` | SQUIRE_VECTOR: Semantic file clustering (19 intents) |
| `triage` | Full pipeline: SCAN -> JUDGE -> SENTINEL (HITL gate) |
| `status` | Colony health report |

---

## TOTALS

| Category | Count |
|---|---|
| Runic Commands (`//`) | 11 |
| Omega Runes (`Ω_`) | 29 |
| CLI Subcommands | 15 |
| HUD Interactive | 8 |
| Intent Patterns | 6 |
| Knight Routes | 5 |
| Squire Commands | 6 |
| **TOTAL** | **80** |
