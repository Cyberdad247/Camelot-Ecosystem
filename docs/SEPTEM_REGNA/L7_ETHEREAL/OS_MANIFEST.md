# CAMELOT APEX OS - MANIFEST v400.1.0
# Codename: UNIVERSAL_SINGULARITY
# Topology: Split-Brain OS (Control Plane + Kinetic Edge + Long-Term Cloudbrain)
# Sync: MAX_CRYSTALLIZATION | Updated: 2026-04-19

## Architecture

```text
CAMELOT_OS/
|-- control_plane/       # Pydantic AI Core (Python) - reasoning, coordination, A2A
|   `-- main.py          # KNIGHT_ROUTES dispatch, MCP client, AgentArmor PDG
|-- kinetic_edge/        # Rust/Go MCP servers - I/O, AST parsing, telemetry
|   `-- mcp_server/      # Axum 0.7 + Tokio (port 3001)
|-- 01_KERNEL/           # Python kernel modules
|   |-- iron_gate/       # Security (iron_gate, warden, zenith, killswitch, vault_keeper)
|   |-- merlin/          # Reasoning (merlin_omega, deep_dive_auditor, repo_analyzer)
|   |-- titan/           # Memory (Titan_Graph/chromadb, Data_Pipeline, storage)
|   |-- EXCALIBUR/       # Core (main.py, config, agents, types, bridge, proxy)
|   |-- agora/           # Orchestration (router, brain_worker, videneptus, Squires, knights)
|   |-- senses/          # I/O (audio/Sonus, connectivity/Aether, integrations)
|   |-- forge/           # Code Gen (forge_v2, nano_forge, assimilation)
|   `-- protocols/       # Protocol definitions
|-- 02_FORGE/            # TypeScript/React UI + kinetic tools
|   |-- KINETIC_ARMORY/  # Saltare, Cribo, Rotel
|   |-- Modal/           # Existing Modal.com cloud functions + portal UI
|   |-- PORTAL_CORE/     # Portal infrastructure
|   `-- web/             # Web UI
|-- cloud_orchestrator/  # Canonical cloudbrain and Modal service surfaces
|   |-- modal_brain.py   # Cost-gated Morgana facade for existing Modal stack
|   |-- long_term_cloudbrain.py # Open Notebook + Appwrite canonical memory bootstrap
|   `-- modal_services.py # Modal ASGI Open Notebook + research agency endpoints
|-- 03_VAULT/            # AES-256-GCM credential vault
|   |-- vault_manager.py
|   |-- Knights/
|   `-- training/configs/
|-- squires/             # Colony modules
|-- docs/
|-- tests/
|-- tools/
|-- k8s/
|-- logs/
`-- .github/workflows/
```

## Foundry Council

| Knight | Engine | Weight | Function |
|---|---|---|---|
| SIR_BORIS | Claude Code | 0.85 | Architecture, critique, colony command |
| SIR_HELIO | Gemini CLI | 0.90 | Large-context mapping |
| SIR_CODEX | OpenAI Codex | 0.75 | High-velocity code generation |
| SIR_GHOST | Local Qwen 3.5 | 1.00 | Zero-trust, air-gapped privacy |
| SIR_LIBERTE | Open Source | 0.80 | Anti-vendor lock-in |

Routing: Merlin Soul Equation `S = aV + bM + gP + dE`

## Canonical Runtime Identity

- Repo version marker: `VERSION = 400.1.0`
- Active Cloud Brain bridge: `03_VAULT/training/configs/notebooklm_bridge.py`
- Canonical NotebookLM notebook ID: `bcaadfdd-1654-487d-9c4c-111f7dea120e`
- Canonical NotebookLM notebook title: `Living Camelot-OS v.400`

Interpretation:

- This manifest describes the current runtime line, not the historical
  `v300.x` notebook era.
- If a doc disagrees with the bridge or `.camelot-config.yaml`, prefer the
  bridge/config and treat the doc as stale until updated.

## UKG Crystal

```yaml
# [vKG_CRYSTAL: SPLIT_BRAIN_OS_SYNC_vMAX]
# [STATUS]: RENORMALIZED | TOON_ENCODED | MAX_CRYSTALLIZATION
# [TOPOLOGY]: TRI-STATE (Morgana/Cloud, Merlin/Kernel, Lukas/Edge)

u0 | ID | Split_Brain_OS | {Focus: High_Density_Autonomy, Control_Plane: Pydantic_AI}
c0 | VECTOR_A | Kinetic_Purity | {Edge_Execution: Rust_Go_Binaries, IO: MCP_HTTP_Only}
c1 | VECTOR_B | RAM_Compression | {Kernel: BitNet_b1.58_Ternary, KV_Cache: SAGE_Eviction, Ceiling: <8GB}
c2 | VECTOR_C | Agentic_Infra | {Coord: Typed_A2A_Cards, Tools: MCP_Servers, Self_Healing: PIV_Loop}
c3 | SECURITY | AgentArmor_PDG | {Data_Flow: Untrusted_Source -> Shell_Sink == BLOCK}
c4 | FOUNDRY | Multi_Engine | {Boris:0.85, Helio:0.90, Codex:0.75, Ghost:1.00, Liberte:0.80}
c5 | COLONY | CLARITY_CORE | {Squires: 8, Pipeline: SCAN>JUDGE>SENTINEL, HITL: Mandatory}
c6 | CLOUDBRAIN | Long_Term_Appwrite_Notebook | {Service: Open_Notebook, Deploy: Modal, Memory: Appwrite}
c7 | RESEARCH | Modal_Agency_Mesh | {Cells: Scout>Weave>Critique, Writes: Edge_Only}
w0 | WORKFLOW | Iron_Gate_HITL | {Trigger: Diff > 10 lines OR > 50MB, Action: Require_HITL}
w1 | COMMANDS | 80_Total | {Runic: 11, Omega: 29, CLI: 15, HUD: 8, Intent: 6, Routes: 5, Squire: 6}
```

## Version

- OS: v400.1.0 (Universal Singularity - MAX_CRYSTALLIZATION)
- Split-Brain: v1.0.0 (Control Plane + Kinetic Edge)
- Cloudbrain: v1.0.0 (Open Notebook + Appwrite + Modal)
- Boris: v2.1 (13-Agent Critique LIVE, Cross-Engine)
- Colony: CLARITY_CORE v1.0.0
- Cartridges: 7 (nextjs, python-api, security, rust-kinetic, reasoning, voice-media, swarm-colony)
