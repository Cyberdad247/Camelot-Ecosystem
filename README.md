# CAMELOT-OS: Sovereign Distributed Intelligence & Agent Swarm

**Version**: 1000-EXCALIBUR-A (Phase H Active)  
**Status**: 🟢 Production Ready & Verified  
**Core Technologies**: Python 3.11+, Rust 1.96, Go 1.23.4, Redis, Qdrant, SQLite (WAL)  
**Security Posture**: Zero-Trust, HITL-gated, Air-gapped Privacy Isolation (Sir Ghost)

---

## 📖 Introduction

CAMELOT-OS is a sovereign, self-improving, distributed AI operating system designed to run on private, memory-constrained hosts (8GB RAM ceiling). It combines a layered multi-agent roundtable (Agentic Knights), a three-tier hierarchical memory model (Knowledge Pyramid), and a robust codebase intelligence pipeline (Squire Colony) to orchestrate tasks securely and autonomously.

Unlike typical agent frameworks, CAMELOT-OS features **direct compile-to-binary kinetic execution**, a typed control plane with real-time biometric and intent triage, and a mathematical state compression engine that compresses 500KB systems states down to a 1.2KB "TOON Crystal".

---

## 🏛️ System Architecture

```
                       ┌────────────────────────────────────────┐
                       │           RUNIC ROUTER CLI             │
                       │   //FORGE, //SWARM, //STATUS, //SCAN   │
                       └───────────────────┬────────────────────┘
                                           │
                                           ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                           01_KERNEL (Reasoning & Memory)                         │
├───────────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────┐  ┌─────────────────────────┐  ┌────────────────────┐  │
│  │   APEE v7.0 Triage     │  │   ROUNDTABLE KNIGHTS    │  │  3-TIER MEMORY     │  │
│  │  • Anya Triage score   │  │  • 8 specialized agents │  │  • L1 Redis        │  │
│  │  • Human HITL Gate     │  │  • Parallel consensus   │  │  • L1.5 Qdrant     │  │
│  │  • Z3 formal check     │  │  • Switchboard router   │  │  • L2 CloudBrain   │  │
│  └────────────────────────┘  └─────────────────────────┘  └────────────────────┘  │
└──────────────────────────────────────────┬────────────────────────────────────────┘
                                           │
                                           ▼
┌───────────────────────────────────────────────────────────────────────────────────┐
│                           02_FORGE (Kinetic Capabilities)                         │
├───────────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────┐  ┌─────────────────────────┐  ┌────────────────────┐  │
│  │     KINETIC ARMORY     │  │   ANYA DASHBOARD API    │  │   SQUIRE COLONY    │  │
│  │  • saltare / rotel     │  │  • FastAPI controller   │  │  • 8-stage pipeline│  │
│  │  • cribo / ledger      │  │  • Live telemetry dashboard│ • SCAN -> MASON  │  │
│  └────────────────────────┘  └─────────────────────────┘  └────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Realworld Implements

The repository is built around several concrete modules and pipelines:

### 1. Runic Command & Routing Engine (`control_plane/`)
Runic commands (prefixed by `//` or `Omega_`) bypass LLM routing entirely and are dispatched through `runic_router.py` to target specialized agent execution loops:
*   **`//FORGE <task>`**: Launches SIR_FORGE to generate, lint, and run kinetic code changes.
*   **`//SWARM <task>`**: Deploys the roundtable agents concurrently to reach a consensus.
*   **`//SCAN [path]`**: Runs CLARITY_CORE triage over the target path (secrets, dead code, duplicates).
*   **`//BOOT`**: Triggers `bin/awaken.py` to warm boot all systemd services and sidecars.
*   **`//PLAN <task>`**: Enters AST Plan Mode to output a task DAG before code modification.
*   **`//HEAL`**: Initiates SIR_DEBUG in a Plan-Implement-Validate (PIV) healing loop on the last error.
*   **`//STATUS`**: Dispatches SIR_SENTINEL to execute active host port probes and mesh checks.
*   **`Omega_<Knight> <task>`**: Routes intent to a specific knight harness (e.g. `Omega_Merlin`).

### 2. The Roundtable Knights (`01_KERNEL/EXCALIBUR/`)
The agent framework maps model capabilities to typed structures (`KnightCapability`):
*   **`SIR_BORIS`**: Lead architect. Conducts 13-agent critique pipeline, checking AST structures, nested loops, and type safety.
*   **`SIR_ALEX`**: Task planner. Generates validated execution DAGs.
*   **`SIR_FORGE`**: Kinetic executor. Writes, compiles, and formats code locally.
*   **`SIR_CODEX`**: Direct code-generation pipeline (OpenAI Codex).
*   **`SIR_SENTINEL`**: Security warden. Enforces the **Iron Gate** HITL validation and secret scans.
*   **`SIR_DEBUG`**: Self-healing agent. Runs test suites and recovers failing processes.
*   **`SIR_GHOST`**: Air-gapped secrets handler. Runs local-only (Ollama Qwen3) to scan logs and config files without cloud leaks.
*   **`LADY_APIS`**: Research and context agent.
*   **`MERLIN_OMEGA`**: Deep reasoning. Uses Tree-of-Thought (ToT) / Graph-of-Thought (GoT) logic.
*   **`SIR_HELIO`**: Voice pipeline interface.

### 3. Squire Colony (`squires/` - CLARITY_CORE v1.0.0)
An 8-squire codebase intelligence pipeline that analyzes code health and verifies policy adherence:
```
SCAN (File walk/hash) ──> INDEX (Symbol graph) ──> GHOST (Privacy/secrets scan) 
  ──> VECTOR (TF-IDF index) ──> SWEEP (Pruning/duplicates) ──> JUDGE (Severity scoring)
    ──> SENTINEL (HITL lock threshold >= 50) ──> MASON (Markdown report builder)
```
Run triage with:
```powershell
python -m squires.colony triage .
```

### 4. Knowledge Pyramid (`03_VAULT/`)
A hierarchical three-tier memory architecture designed for private contexts:
*   **L1 (Redis)**: Volatile, high-speed session state (24-hour TTL).
*   **L1.5 (Qdrant)**: Semantic memory storing 384D vector embeddings (30-day TTL).
*   **L2 (CloudBrain)**: Persistent consolidated knowledge base, hydrated from L1/L1.5.

### 5. Kinetic Armory (`02_FORGE/KINETIC_ARMORY/`)
Contains source-compiled binary utilities that run as low-level sidecars:
*   **`saltare.exe`**: Tailscale mesh proxy and coordinator (Go, 35.9 MB).
*   **`saltare-mcp.exe`**: MCP server-to-agent wiring middleware (Go, 8.0 MB).
*   **`cribo` / `rotel`**: High-performance Rust-based IPC and named-pipe media bridges.
*   **`ledger.exe`**: Append-only log validator for governance checks (Go, 2.4 MB).
*   **`cli-proxy-api.exe`**: Zero-burn local API proxy (Go, 49.4 MB).

### 6. Adaptive Learning Infrastructure (Phase H)
Self-monitoring framework that tracks metrics (`control_plane/metrics.db`) with `< 0.1ms overhead`:
*   **Pattern Recognition**: Automatically parses log streams to extract recurring performance behaviors.
*   **Anomaly Detection**: Flags metrics deviating by more than `1.5x (warning)` or `3.0x (critical)` from the historical baseline.
*   **Auto-Tuning Engine**: Dynamically shifts operations between Performance Tiers (T1/T2/T3) depending on resource utilization.

---

## 🚀 Quick Start Guide

### 1. Booting the Environment
Initiate all sidecars, databases, and agent layers:
```powershell
# Full boot (Redis, Qdrant, FastAPI core, sidecars)
python bin/awaken.py

# Quick boot (skips heavy vector models)
python bin/awaken.py --quick

# Start the interactive agent console REPL
python bin/knight_session.py
```

### 2. Performing a Security & Triage Scan
Verify that the codebase contains no exposed secrets, that the three mirrors of `PROVENANCE_LEDGER.md` are in sync, and that all kinetic binaries are present:
```powershell
# Run the automated Sentinel check
python scripts/run_sentinel_audit.py
```
View the results in `logs/sentinel_audit_latest.md`.

### 3. Syncing the Provenance Ledger
If a ledger drift warning occurs between the root, vault, and docs mirrors, run the reconciliation script:
```powershell
python scripts/sync_provenance.py
```

### 4. Running the Test Suite
Validate the system across low-level and high-level integration parameters:
```powershell
# Run standard tests
.venv\Scripts\python.exe -m pytest

# Run resilience and chaos simulation tests
python test_phase_g_resilience.py
```

---

## 📜 Repository Constraints

To maintain sovereign compliance, all developers and agentic sessions must adhere to:
1.  **API Key Management**: Private API keys **must never** be written to disk in plain text. Use environment variables (e.g. `AGENT_MEMORY_API_KEY`) or the vault manager. `config.json` must contain boolean flags only (`"has_key": true`).
2.  **Sovereign Gate Limits (Titanium Law III)**: Any file edit modifying more than `10 net lines` or proposing more than `50MB` of deletions requires explicit Sovereign Commander confirmation (`Make it so`).
3.  **Provenance Ledger**: All kinetic file changes must be appended to the root `PROVENANCE_LEDGER.md` via the automated hooks. Manual modifications to this ledger are strictly prohibited.
4.  **Unicode Sanitization**: Windows Console runs under `CP1252` encoding by default. Avoid printing raw emoji glyphs (e.g. `✅`, `❌`) in script outputs; use text markers (e.g. `[OK]`, `[MISSING]`) to prevent encoder crashes.

---

* Sir Sentinel stands watch. The Round Table protects the kingdom. *
