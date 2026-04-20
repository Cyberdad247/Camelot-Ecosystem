# CAMELOT-OS PROTOCOL REGISTRY v300.4.0
# All protocols governing system behavior, security, and agent coordination
# Generated: 2026-03-31

---

## TITANIUM LAWS (Immutable)

| # | Law | Enforcement |
|---|---|---|
| T1 | **Kinetic Purity**: NEVER Python if Rust/Go binary exists | Lukas_Omega (L2) |
| T2 | **Provenance**: Log all file mods to PROVENANCE_LEDGER.md | All agents |
| T3 | **Iron Gate**: >10 net lines or >50MB deletion requires HITL approval | Agent-Armor v2.0 |
| T4 | **Graph Law**: >3 reasoning steps must use GoT/DoT decomposition | Merlin_Omega (L3) |
| T5 | **Progressive Disclosure**: Root context <300 lines | Anya_Omega (L7) |
| T6 | **RAM Ceiling**: 8GB physical / 7.8GB usable | Defense Grid |
| T7 | **NPE Error Rate**: <0.7% | Sentinel |
| T8 | **Voice Latency**: Sub-second mandatory | Sonus (L7) |

---

## SECURITY PROTOCOLS

### Agent-Armor v2.0 (PDG + DoT + Spotlighting + Miri + Trivy)
- **Program Dependency Graph (PDG)**: Map data flow from untrusted sources to execution sinks. If untrusted web data touches shell/eval -> BLOCK.
- **Depth of Thought (DoT)**: Security verification tree before any privileged operation.
- **Spotlighting**: Delimiter injection defense — all user input wrapped in XML tags.
- **Miri**: Undefined behavior detection for Rust code paths.
- **Trivy**: Container/dependency vulnerability scanning.

### Iron Gate Protocol
- Location: `01_KERNEL/iron_gate/iron_gate.py`
- Protocol doc: `01_KERNEL/protocols/iron_gate_protocol.md`
- Function: GIGO filter — validates all inputs before kernel processing
- Risk classification: LOW / MEDIUM / HIGH
- HIGH risk -> GATE_REJECTED (logged to ledger)

### Defense Grid
- Heartbeat: `~/cmd/pulse/heartbeat.go` — 5s poll cycle
- RAM monitor: Hard ceiling at 8GB, alerts at 7.5GB
- Token shield: `.aiexclude` blocks node_modules, .venv, lockfiles
- Kinetic shim: `run_agent_cmd.sh` — venv activation + RAM check before execution

### Warden Security System
- Commands: `status`, `lockdown`, `unlock`, `audit`, `spotlight`
- Location: `01_KERNEL/iron_gate/security/warden.py`
- Audit trail: All actions logged to PROVENANCE_LEDGER.md

---

## REASONING PROTOCOLS

### Triple-QFT Compilation
- Protocol doc: `01_KERNEL/protocols/triple_qft_compilation.md`
- Stages: Renormalize (strip noise) -> Quantize (compress context) -> Transform (structured output)
- Used by: Anya_Omega APEE v6.5 compiler

### GoT/DoT/ToT Reasoning
- Graph of Thoughts (GoT): Non-linear reasoning with branch/merge
- Depth of Thought (DoT): Deep verification chains
- Tree of Thoughts (ToT): Branching exploration with pruning
- Trigger: Any task requiring >3 reasoning steps (Titanium Law T4)

### LaC Oscillation (Language as Compiler)
- Diverge phase: temperature 1.2 (creative exploration)
- Critical phase: temperature 0.9 (evaluation)
- Converge phase: temperature 0.2 (precise output)

### NDR+S (Neurosymbolic Dual-Representation + Synthesis)
- Neural: Pattern matching, embedding similarity
- Symbolic: Formal logic, type checking, AST analysis
- Synthesis: Merge neural intuition with symbolic proof

---

## AGENT PROTOCOLS

### ECC v1.9.0 (Everything Claude Code)
- Plan Mode: AST-Aware (MANDATORY for SIR_BORIS)
- Steps: Analyze AST -> Map dependencies -> Generate plan with rollback -> Verify -> Execute
- 13-Agent Antagonistic Critique Pipeline (real AST validation)

### PIV Self-Healing Loop (Plan-Implement-Validate)
- Max cycles: 3
- Tools: @vercel/agent-browser, Playwright headless
- Trigger: E2E test failures
- Escalation: After 3 failed cycles -> HITL

### DeerFlow 2.0
- Mode: Docker sandbox isolation
- Trigger: >5 files OR >3 steps OR cross-module refactor
- Features: Full filesystem isolation, bash in container, aggressive context compression

### SRDL (Swarm Reduce Dispatch Loop)
- Map: Oracle phase (plan decomposition)
- Reduce: Sentinel phase (critique + merge)
- Kinetic: AST patch execution

### A2A (Agent-to-Agent) Protocol
- Location: `control_plane/main.py`
- Transport: JSON-RPC over HTTP
- Message types: TaskPayload, TaskResult
- Routing: KNIGHT_ROUTES dispatch table

---

## SQUIRE PROTOCOLS

### Triage Pipeline
```
SQUIRE_SCAN (detect) -> SQUIRE_JUDGE (classify) -> SQUIRE_SENTINEL (approve)
```
- HITL gate enforced at SENTINEL stage
- All destructive actions require `.antigravity_backup`

### Colony Invocation Rules
1. Before large refactor: run `index` + `vector`
2. Before deletion: run full `triage` pipeline
3. After system change: run `status`
4. Antigravity backup mandatory for all destructive operations

---

## DEPLOYMENT PROTOCOLS

### 4-Tier Fallback Chain
```
Cerebras -> OpenRouter -> Ollama -> SLM Edge
```

### LLM Router Fallback
```
CLIProxyAPI -> Gemini -> OpenAI -> Claude -> Grok -> Mistral -> OpenRouter -> Ollama
```

### Split-Brain Topology
- **Control Plane**: Pydantic AI (reasoning, routing, A2A)
- **Kinetic Edge**: Rust Axum MCP (I/O, file ops, path guards)
- Communication: MCP protocol over HTTP (port 3001)

---

## MEMORY PROTOCOLS

### Hybrid Memory Stack
| Store | Tech | Function |
|---|---|---|
| Vector | Qdrant | Semantic similarity search |
| Graph | Neo4j | Relationship traversal |
| Ledger | SQLite WAL | Immutable audit trail |
| Crystal | UKG JSON-LD | Compressed knowledge glyphs |

### Compression Stack (SAC > CCF > QFT)
- **SAC**: Semantic Abstraction Compression (remove redundancy)
- **CCF**: Context Crystal Fusion (merge related concepts)
- **QFT**: Quantum Field Transform (final token optimization)
- Target: 97%+ compression ratio

---

## EVOLUTION PROTOCOLS

### Knight Evolution Protocol
- Location: `01_KERNEL/protocols/knight_evolution_protocol.md`
- XP economy for knight improvement
- Promotion path: Squire -> Knight -> High Knight -> Omega

### Persona Evolution Protocol
- Location: `01_KERNEL/protocols/persona_evolution_protocol.md`
- MPI vector adjustment based on task performance
- Soul Matrix recalibration

### Assimilation Protocol (v5 Evolution)
- Location: `01_KERNEL/protocols/assimilation_v5_evolution.md`
- ETL pipeline for external code/knowledge ingestion
- Stages: Scan -> Parse -> Classify -> Integrate -> Verify

---

## PROTOCOL FILE LOCATIONS

### 01_KERNEL/protocols/ (24 files)
```
agno_orchestrator.md          paladin_htn_protocol.md
assimilation_v2.md            persona_evolution_protocol.md
assimilation_v3.md            sarda_engine_v1.md
assimilation_v4_omega.md      squire_protocol.md
assimilation_v5_evolution.md  titan_protocol.md
cellular_protocol.md          triple_qft_compilation.md
distill_reconstruct_protocol.md  ukg_integration_v206.md
hive_forge_v1.md              xp_economy_protocol.md
iron_gate_protocol.md         Ω_CHIMERA_AUDIT.md
knight_evolution_protocol.md  Ω_KNIGHT_FORGE.md
lukas_architect.md            Ω_THINK_TANK_PRIME.md
merlin_identity_forge.md      ThinkTank/ WarRoom/
```

### 03_VAULT/Protocols/ (13 files)
```
AGENT_FORGE_PROTOCOL.md       KINETIC_GOOSE_INTEGRATION.md
CHIMERA_AUDIT_PROTOCOL.md     KNIGHT_FORGE_PROTOCOL.md
CHROME_WARDEN_PROTOCOL.md     NDR_S_PROTOCOL.md
DEFENSE_GRID_PROTOCOL.md      NOTTE_PROTOCOL.md
DISTILLER_PROTOCOL.md         TRIPLE_QFT_PROTOCOL.md
ENGINE_TECHNICAL_SCAN.md      VERDENT_CLAW_PROTOCOL.md
GENESIS_PROTOCOL.md
```
