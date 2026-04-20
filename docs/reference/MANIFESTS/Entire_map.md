# CAMELOT APEX: ENTIRE MAP (v300.2.0 ARCHITECTURE_VERIFIED)
**Timestamp:** 2026-03-23T12:00:00Z
**Mode:** Kinetic Purity [Active] | Split-Brain OS [Validated]
**Sovereign:** VaShawn O. Head
**Architect:** Merlin_Omega + Anya_v202.0 + Lukas_Edge
**Audit:** Full local system audit — 2026-03-22

---

## I. THE SINGULARITY LATTICE (Septem Regna)
| LAYER | NAME | GUARDIAN | tech_stack |
| :--- | :--- | :--- | :--- |
| **L7** | **ETHEREAL** | Anya | Next.js / Vercel / APEE v6.5 |
| **L6** | **GOVERNANCE** | Arthur | Iron Gate / Ledger / Titanium Laws |
| **L5** | **AGENTIC** | Paladin | Swarm Protocols / A2A / SARDA |
| **L4** | **SEMANTIC** | Chronos | UKG (JSON-LD) / Titan Omega |
| **L3** | **NEURAL** | Merlin | Videneptus LaC / NDR+S / GoT+DoT+ToT |
| **L2** | **KINETIC** | Lukas | Saltare / Cribo / Rust MCP Edge |
| **L1** | **SUBSTRATE** | Morgana | Modal / Docker / 8GB RAM Ceiling |

---

## II. SPLIT-BRAIN OS ARCHITECTURE (NEW — v300.1.0)

```
[Control Plane: Python/Pydantic AI]  --A2A/HTTP-->  [Kinetic Edge: Rust/Axum MCP]
        |                                                    |
   typed messages                                      file I/O, AST
   (Task/Status/ToolRequest/ToolResponse)              (list_directory, ...)
        |                                                    |
[TestRunnerAgent: PIV self-healing]                  [AgentArmor PDG guard]
```

| Component | Location | Tech | Status |
|-----------|----------|------|--------|
| Control Plane | `CAMELOT_OS/control_plane/main.py` (mirrored: `~/.camelot/control_plane/`) | Pydantic AI, httpx | OPERATIONAL |
| Kinetic Edge MCP | `~/.camelot/kinetic_edge/mcp_server/` | Rust, axum, tokio | COMPILED + VERIFIED |
| TestRunnerAgent | `CAMELOT_OS/control_plane/test_runner_agent.py` | Python asyncio | 2/2 PASSED |
| OS Manifest | `CAMELOT_OS/OS_MANIFEST.md` (mirrored: `~/.camelot/`) | TOON vKG Crystal | SYNCED |
| Squire Index | `~/.camelot/kinetic_edge/squire_index/` | Rust lib | SCAFFOLD |

---

## III. THE TERRITORY (Core Realms)

### A. `~/.camelot/` (CLI Orchestrator)
*The lightweight CLI entry point and Split-Brain control plane.*

| File/Dir | Purpose |
|----------|---------|
| `camelot.py` | CLI orchestrator (exec, ask, llm, knights, etc.) |
| `camelot_cli.py` | CLI argument parser |
| `hud.py` | Rich TUI dashboard + CLIProxyAPI bootstrap + Runic REPL |
| `anya.py` | Sovereign Compiler (APEE pipeline) |
| `merlin.py` | System 2 reasoning router |
| `bridge.py` | Kernel bridge (11/11 components) |
| `ouroboros.py` | SQLite persistence (WAL mode) |
| `llm_router.py` | Multi-provider LLM router (8 providers, fallback chain) |
| `run_agent_cmd.sh` | Kinetic shim (venv + RAM check) |
| `control_plane/main.py` | Pydantic AI A2A control plane |
| `kinetic_edge/mcp_server/` | Rust MCP server (axum, port 3001) |
| `kinetic_edge/squire_index/` | Rust indexing library |
| `TestRunnerAgent.py` | Self-healing PIV test loop |
| `OS_MANIFEST.md` | TOON-encoded vKG topology crystal |
| `BOOTSTRAP.md` | Master bootstrap (Septem Regna, 32 runes, 14 laws) |
| `PROVENANCE_LEDGER.md` | Immutable audit ledger |
| **config/** | `mcp_config.json`, `saltare.toml` |
| **skills/** | TYPESCRIPT, PYTHON, SECURITY, REASONING, SWARM, VOICE, VISUAL, NPE_PERSONAS |
| **knights/** | architect, coder, creative, debug, researcher, warden |
| **context/** | HALLUCINATION_PROTOCOL.md |
| **memory/** | `ukg_graph.jsonld` |
| **cartridges/** | nextjs.yaml, python-api.yaml, security.yaml |
| **tests/** | test_anya, test_bridge, test_camelot_cli, test_knights, test_llm_router, test_ouroboros |
| **logs/** | ouroboros.log |
| `ouroboros.db` | SQLite database |

### B. `~/CAMELOT_OS/` (Full Kernel + Forge + Vault)

#### 01_KERNEL (The Brain)
*Logic engines, reasoning, security, memory, orchestration.*

| Subsystem | Key Files | Purpose |
|-----------|-----------|---------|
| **EXCALIBUR/** | `main.py`, `roster.yaml`, `agents/` | FastAPI process_intent gateway |
| **Engines/** | `videneptus_lac.py`, `coherence_engine.py`, `merlin_llm.py`, `prism_gateway.py`, `sentinel_compressor.py`, `ukg_runtime.py`, `mcp_adapter.py` | Core reasoning + compression engines |
| **Engines/crawl4ai/** | Full crawl4ai integration | Web crawling / research |
| **Engines/symbolect_transpiler/** | Symbolect v3.1 | Dense glyph transpilation |
| **reasoning/** | `core.py`, `planning_engine.py`, `council_debate.py`, `aurora_vision.py`, `dream_state.py`, `helix_loop.py`, `prometheus_decomp.py`, `search.py`, `titan_forge.py`, `veritas_audit.py`, `oracle_physics.py`, `omega_learn.py`, `lyricus_voice.py` | Full reasoning stack |
| **security/** | `iron_gate.py`, `warden.py`, `zenith_scanner.py`, `enforcer.py`, `hermes.py`, `shadow_mode.py`, `killswitch_controller.py`, `vault_keeper.py`, `identity_decay.py`, `biological_isolation.py`, `reforge_identity.py` | AgentArmor + Iron Gate |
| **memory/** | `titan_omega.py`, `titan_schemas.py`, `anya_memory.py`, `base_memory.py`, `compiler.py`, `reflection_engine.py`, `sentinel_compression.py`, `skillgraph.py`, `graphrag/`, `ukg_graph.json` | Titan Omega graph + flux memory |
| **orchestration/** | `think_tank.py`, `agent_dispatcher.py`, `handoff_manager.py` | Swarm orchestration |
| **DEFENSE_GRID/** | `defense_grid.py`, `sit_loop.py`, `watchtower.exe`, `knights/` (castor, kronos, octavian, sentinel) | Real-time defense grid |
| **BRIDGE/** | Kernel-to-CLI bridge | Component integration |
| **connectivity/** | Network/IPC modules | RustDesk bridge, etc. |
| **monitoring/** | System health + telemetry | Observability |
| **fusion/** | Module fusion engine | Cross-module integration |
| **Data_Pipeline/** | `storage.py` | Data ingestion |
| **Squires/** | Squire agents | Lightweight task runners |
| **agents/** | Agent implementations | Specialized agents |
| **swarms/** | Research/Vision/Voice swarms | Multi-agent protocols |
| **persona/** | Identity management | NPE personas |
| **prompts/** | System prompts | Merlin, Anya, Lukas prompts |
| **agora/** | `videneptus.py`, `router.py`, `node.py`, `protocol.py`, `context.py`, `bridge.py`, `hud_bridge.py`, `knights/`, `models/` | Agora protocol — semantic routing, ANP envelopes, Videneptus integration |
| `merlin_omega.py` | Root reasoning engine | Merlin System 2 |
| `brain_worker.py` | Background worker | Async task processing |
| `swarm_controller.py` | Swarm coordinator | SRDL loop |
| `sky_engine.py` | Cloud execution | Modal bridge |

#### 02_FORGE (The Factory)
*UI/UX, kinetic tools, and active development.*

| Subsystem | Key Files | Purpose |
|-----------|-----------|---------|
| **kinetic/cribo/** | Rust binary | Bundler (compiled) |
| **kinetic/rotel/** | Rust/Go | Telemetry collector |
| **kinetic/rustdesk-server/** | Rust | Remote access (hbbs/hbbr) |
| **kinetic/nano_knights/** | Python agents | Research swarm bots |
| **kinetic/titan_*.py** | 8 titan scripts | Alchemist, architect, evolve, grader, loom, scribe, telemetry, triage |
| **Camelot_HUD.py** | Python Rich | TUI command center |
| **PORTAL_CORE/** | Portal framework | Core portal UI |
| **Quantum_Cinematic_Engine/** | Media engine | Video/visual generation |
| **KINETIC_ARMORY/** | Tool registry | Kinetic tool manifests |
| **Nano-Browser/** | Browser extension | Research swarm browser |
| **holotable/** | Dashboard | Visual telemetry |
| **agency_factory/** | Agent factory | Agent scaffolding |
| **crawl4ai/** | Web crawler | Deep web foraging |
| **web/** | Web UI | Frontend components |
| **apps/** | Applications | anya-lyte, etc. |
| **packages/** | Shared packages | anya-domain, pocket-squire |
| **hooks/** | Git/system hooks | Pre-commit, post-deploy |
| `perplexity_distiller.py` | Research | Real-time extraction |

#### 03_VAULT (The Memory)
*Knowledge persistence, archives, external intelligence.*

| Subsystem | Purpose |
|-----------|---------|
| **UKG/** | Universal Knowledge Glyph store |
| **Titan_Graph/** | Graph memory persistence |
| **PROMPTS/** | Prompt templates vault |
| **Protocols/** | Protocol definitions |
| **Knights/** | Knight knowledge bases |
| **LEGAL/** | Constitution, IP, sovereign laws |
| **KINETIC_REFERENCES/** | Technical documentation |
| **GLYPHS/** | Glyph definitions |
| **COMMERCE/** | Business logic |
| **SENSES/** | Sensory modules |
| **BOUNTY_HUNTER/** | Task bounty system |
| **CLOUD_SYNC/** | Cloud synchronization |
| **EXTERNAL_TOOLS/** | Third-party tool configs |
| `vault_manager.py` | AES-256-GCM credential manager |
| `workspace_memory.jsonld` | Context rehydration bridge |
| `excalibur.py` | Vault-side Excalibur API |
| **00_SECURE_ARCHIVE/** | Purged/historical artifacts |
| **00_TEMPLATES/** | Document and project templates |
| **99_HISTORY/** | Historical records |
| **99_SCRATCHPAD/** | Learning logs, observations |
| **CAMELOT_NOTEBOOK/** | Decision tracking notebook |
| **HCCP-Strategy/** | HCCP strategy documents |
| **LLM-Apps-Ref/** | LLM application references |
| **Lobe-Chat/** | Lobe Chat integration (Next.js monorepo) |
| **Nano-Knights/** | Browser extension swarm agents |
| **SNIPPETS/** | Code snippet library |
| **WorkOrders/** | Task work order tracking |
| **bytebot/** | ByteBot integration |
| **data_store/** | Persistent data storage |
| **directives/** | Operational directives |
| **docs/** | Vault-level documentation |
| **dyad-apps/** | Dyad application references |
| **evidence/** | Audit evidence collection |
| **external/** | External tool/project references |
| **incoming/** | Ingest queue for new materials |
| **knowledge/** | Knowledge subsystems (Copyright, TITAN_SWARM, etc.) |
| **merlins-think-tank/** | Merlin reasoning workspace |
| **open-notebook/** | Open notebook integration (Python + React) |
| **scrcpy_release/** | Screen copy tool release |
| **skills/** | Vault skill definitions |
| **temp_mcp/** | Temporary MCP staging |
| **training/** | Training data and materials |
| **verification/** | Verification and validation artifacts |

#### Supporting Directories

| Dir | Purpose |
|-----|---------|
| **docs/** | EMPIRE_MAP, SEPTEM_REGNA_ARCH, protocols, guides, reports, manifests, laws |
| **docs/EXTERNAL/** | Vendored reference repos (unsloth, etc.) |
| **docs/GUIDES/** | Defense Grid runbook, Hive IDE manual, Nano Knights manual, Lukas bootstrap |
| **docs/PROTOCOLS/** | 15+ protocol definitions (assimilation v2-v5, iron gate, paladin HTN, etc.) |
| **docs/REPORTS/** | 28 audit JSON reports (tool evaluations) |
| **scripts/** | scan_secrets.py, security_audit.py, update_map.py, fine_tune_unsloth.py |
| **tools/** | antigravity, defense_grid_agent, scout_agent, sir_masque, sir_sonus, sir_ears, nano_physics, chronos_gate, squire_cli |
| **lab/** | Audit reports, cleanup reports, workspace map, scratch notebook |
| **.hive/** | Context, knights, ledgers, memory, profiles, protocols, skills |
| **k8s/** | Kubernetes manifests |
| **workspace/** | Nano Knights working data |
| **tmp/** | pi_mono_analysis (research), temp files |

---

## IV. SATELLITE SYSTEMS

### CLIProxyAPI (Zero-Burn Proxy)
| Item | Detail |
|------|--------|
| Binary | `~/CLIProxyAPI/cli-proxy-api.exe` (49MB Go) |
| Config | `~/CLIProxyAPI/config.yaml` (port 8080) |
| Auth | `~/.cli-proxy-api/` (gemini.json, claude.json, codex.json) |
| Models | 29 available (Gemini 2.5/3, Claude opus-4-6/sonnet-4-6, GPT 5-5.4) |
| Status | Auto-starts via HUD bootstrap |

### Defense Grid (Heartbeat)
| Item | Detail |
|------|--------|
| Daemon | `~/cmd/pulse/heartbeat.go` (5s poll) |
| Watchtower | `01_KERNEL/DEFENSE_GRID/watchtower.exe` (Rust compiled) |
| Token Shield | `~/.camelot/.aiexclude` |
| Kinetic Shim | `~/.camelot/run_agent_cmd.sh` |
| Quarantine | `~/CAMELOT_DefenseGrid_Quarantine/` (isolated browser creds, unsigned bins) |

### IDE Integrations
| Tool | Config Dir | Key Files |
|------|-----------|-----------|
| Claude Code | `~/.claude/` | settings.json, skills/sir_boris.md |
| Gemini CLI | `~/.gemini/` | GEMINI.md, settings.json, MCP servers |
| Codex | `~/.codex/` | config.toml, skills/, rules/ |
| NotebookLM MCP | `~/.notebooklm-mcp-cli/` | Chrome profiles |

### MCP Servers (Shared across IDEs)
- **ollama** — Local model inference (qwen3:0.6b default)
- **notebooklm-mcp** — NotebookLM integration
- **filesystem** — Safe file operations
- **github** — Repository operations
- **brave** — Web search

---

## V. LLM ROUTER (8 Providers)

| Priority | Provider | Endpoint | Key Env Var |
|----------|----------|----------|-------------|
| 1 | CLIProxyAPI | 127.0.0.1:8080 | (local) |
| 2 | Gemini | API | GOOGLE_API_KEY |
| 3 | OpenAI | API | OPENAI_API_KEY |
| 4 | Claude | API | ANTHROPIC_API_KEY |
| 5 | Grok | API | XAI_API_KEY |
| 6 | Mistral | API | MISTRAL_API_KEY |
| 7 | OpenRouter | API | OPENROUTER_API_KEY |
| 8 | Ollama | Local | (auto-detect) |

---

## VI. ACTIVE KINETIC STACK

| Binary | Type | Port/Path | Status |
|--------|------|-----------|--------|
| Saltare | Go gateway | 8080 | Configured |
| Cribo | Rust bundler | `02_FORGE/kinetic/cribo/target/release/` | Compiled (in PATH) |
| Rotel | Telemetry | 4317 | Configured |
| RustDesk | Rust server | hbbs/hbbr | Available |
| Watchtower | Rust defense | N/A | Compiled |
| kinetic-mcp-server | Rust axum | 3001 | Compiled + Validated |
| cli-proxy-api | Go proxy | 8080 | Running |

---

## VII. MEMORY SYSTEMS

| Store | Location | Format |
|-------|----------|--------|
| UKG Graph (CLI) | `~/.camelot/memory/ukg_graph.jsonld` | JSON-LD (30 nodes, 16 edges) |
| UKG Graph (Kernel) | `01_KERNEL/memory/ukg_graph.json` | JSON |
| Titan Omega | `01_KERNEL/memory/titan_omega.py` | Python (graph + flux, 90s TTL) |
| Ouroboros | `~/.camelot/ouroboros.db` | SQLite (WAL) |
| Provenance (CLI) | `~/.camelot/PROVENANCE_LEDGER.md` | Markdown table |
| Provenance (OS) | `CAMELOT_OS/PROVENANCE_LEDGER.md` | Markdown table |
| Workspace Memory | `03_VAULT/workspace_memory.jsonld` | JSON-LD |
| Hive Memory | `.hive/memory/` | Mixed |
| Claude Auto-Memory | `~/.claude/projects/.../memory/` | Markdown files |

---

## VIII. ENTRY POINTS

| Command | Target | What it does |
|---------|--------|-------------|
| `camelot-os` | `~/.camelot/hud.py` | Full bootstrap: CLIProxyAPI + Defense Grid + HUD + Runic REPL |
| `camelot` | `~/.camelot/camelot.py` | CLI-only mode (exec, ask, llm, knights) |
| `claude` | Claude Code | AI IDE with CLAUDE.md constitution |
| `gemini` | Gemini CLI | AI IDE with GEMINI.md |
| `codex` | Codex CLI | AI IDE with config.toml |

---

## IX. GIT STRUCTURE

| Item | Detail |
|------|--------|
| Repo root | `C:\Users\vizio` |
| Remote | `origin -> https://github.com/Cyberdad247/Authors_Page.git` |
| Main branch | `main` |
| Working branch | `master` |
| CAMELOT_OS | Subtree (NOT submodule) |
| CI/CD | `.github/workflows/verify_os.yml` (7 stages) |

---

## X. KNOWN ISSUES

1. **Windows encoding** — Kernel modules use Unicode (Omega symbol); bridge.py sets UTF-8
2. **Titan Omega flux TTL** — 90s default, events expire quickly
3. **`.modal.toml`** — Exposed API credentials, needs rotation
4. **Quarantine** — Contains isolated browser creds and SSH key
5. **MCP config duplication** — 3 copies across .gemini, .codex, .claude.json
6. **Rust target dirs** — `02_FORGE/kinetic/rustdesk-server/target/` ~5GB (run `cargo clean`)
7. **Docker compose conflicts** — Multiple conflicted backup files in CAMELOT_OS root

---

## XI. VERSION HISTORY

| Version | Codename | Date | Summary |
|---------|----------|------|---------|
| v57.0 | SOVEREIGN_ARCHITECT | pre-existing | Master bootstrap |
| v58.0 | STACK_FORGE | 2026-03-05 | + 7 modules from Idea Stacking |
| v59.0 | OBSIDIAN_HARVEST | 2026-03-05 | + 14 modules (complete harvest) |
| v60.0 | OBSIDIAN_SOVEREIGN | 2026-03-05 | + Singularity Lattice + local deployment |
| v300.0 | UNIVERSAL_SINGULARITY | 2026-03-05 | Anya v202.0 + Merlin System 2 full spec |
| v300.0.0 | UNIVERSAL_SINGULARITY | 2026-03-22 | HEAL/FORGE/SHIELD. Kernel fixed, stubs upgraded, secrets redacted |
| v300.1.0 | SPLIT_BRAIN_VALIDATED | 2026-03-22 | Split-Brain OS: Rust edge + Pydantic control plane + A2A + tests passed |

---

**SYSTEM STATUS:** SPLIT_BRAIN_VALIDATED. LATTICE STABLE.
**Made by Invisioned Marketing inc.**
