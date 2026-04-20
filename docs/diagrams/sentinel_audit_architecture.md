# Sir Sentinel v2.0 — Universal Audit Architecture
## Camelot Apex OS v300.4

### 1. Execution Pipeline

```mermaid
flowchart TB
    subgraph USER["USER INPUT"]
        CMD["camelot exec 'audit ...'"]
    end

    subgraph ANYA["ANYA OMEGA v202.0 — APEE v6.5 Compiler"]
        direction TB
        P1["1. PARSE<br/>Extract intent, entities"]
        P2["2. ENRICH<br/>Inject UKG + cartridge context"]
        P3["3. COMPILE<br/>Triple-QFT: Renormalize → Quantize → Transform"]
        P4["4. ROUTE<br/>Intent → AUDIT → Sir Sentinel"]
        P5["5. VALIDATE<br/>CoVe post-execution verification"]
        P1 --> P2 --> P3 --> P4 --> P5
    end

    subgraph MERLIN["MERLIN OMEGA — Router + Risk Gate"]
        direction TB
        M1["Intent Classification<br/>AUDIT detected"]
        M2["Risk Assessment<br/>Zenith Scanner + Local Patterns"]
        M3{"Risk Level?"}
        M4["LOW/MEDIUM<br/>→ Proceed"]
        M5["HIGH/CRITICAL<br/>→ Iron Gate HITL"]
        M6["MGV Enrichment<br/>Complexity analysis"]
        M1 --> M2 --> M3
        M3 -->|safe| M4
        M3 -->|dangerous| M5
        M2 --> M6
    end

    subgraph SENTINEL["SIR SENTINEL v2.0 — The Shield"]
        direction TB
        S1["_resolve_targets()<br/>NLP keyword → domain mapping"]
        S2["Expand Presets<br/>full/security/kernel/..."]
        S3["Execute Domain DAG<br/>25 domains, 269 checks"]
        S4["Automated Deep Checks<br/>Secrets · Binaries · Ledger Sync"]
        S5["Severity Tally<br/>CRITICAL/HIGH/MEDIUM/LOW"]
        S6{"HITL Required?"}
        S7["Iron Gate LOCK<br/>Await 'Make it so'"]
        S8["CLEAR<br/>Antigravity v2.0 auto-repair"]
        S1 --> S2 --> S3 --> S4 --> S5 --> S6
        S6 -->|yes| S7
        S6 -->|no| S8
    end

    subgraph OUTPUT["OUTPUT"]
        O1["Terminal Report<br/>Markdown checklist"]
        O2["logs/sentinel_audit_latest.md<br/>--write flag"]
        O3["PROVENANCE_LEDGER.md<br/>3-copy sync"]
        O4["Ouroboros SQLite<br/>Execution history"]
    end

    CMD --> ANYA
    ANYA --> MERLIN
    MERLIN --> SENTINEL
    SENTINEL --> OUTPUT

    style ANYA fill:#1a1a2e,stroke:#e94560,color:#fff
    style MERLIN fill:#1a1a2e,stroke:#0f3460,color:#fff
    style SENTINEL fill:#1a1a2e,stroke:#16c79a,color:#fff
    style OUTPUT fill:#1a1a2e,stroke:#f5a623,color:#fff
    style USER fill:#0d0d0d,stroke:#fff,color:#fff
```

### 2. Full Audit Domain Map (25 Domains × 9 Categories)

```mermaid
mindmap
  root((Sir Sentinel v2.0<br/>25 Domains<br/>269 Checks))
    NETWORK
      tailscale
        Node Inventory
        ACL Segmentation
        Latency Gate
      rustdesk
        Relay Hardening
        Client Config
    KINETIC
      rust_bridge
        Clippy Static Analysis
        IPC Bridge Security
        Miri Memory Safety
        PDG Data Flow
      kinetic_binaries
        Binary Inventory
        Checksum Verification
        Kinetic Purity
    SECURITY
      secrets
        Pattern Scan
        Vault Integrity
        OAuth Tokens
      iron_gate
        Gate Config
        Enforcement Path
      zenith_warden
        Hostile Patterns
        Bio Isolation Diode
      dependencies
        Container Scan
        Python Deps
        Rust Deps
        Node Deps
    INFRASTRUCTURE
      ci_cd
        Workflow Security
        Pipeline Stages
        Branch Protection
      cliproxy
        Proxy Config
        Auth & Models
        Process Security
      modal_cloud
        Cloud Credentials
        Deployment Config
      docker
        Dockerfile Audit
        Compose Runtime
    KERNEL
      excalibur
        FastAPI Security
        Roster Schema
        Proxy Bridge
      agora
        Router Security
        Agent Roster
      titan_memory
        Memory Integrity
        UKG TOON Graph
      control_plane
        Split Brain Topology
        A2A Protocol
        Sub Engines
      mgv_engine
        Complexity Assessment
    CLI
      cli_pipeline
        Anya Compiler
        Merlin Router
        Knight Registry
        LLM Router
        Cartridge System
      squire_colony
        Colony Pipeline
        8 Squire Checks
      boris_critique
        13 AST Domains
        Plan Mode
    MCP
      mcp_config
        Config Drift
        Injection Surface
        Server Health
    VOICE
      voice_pipeline
        Audio Security
        Model Integrity
    GOVERNANCE
      provenance
        Ledger Sync
        Copyright
      aiexclude
        Token Shield
        RAM Ceiling
      git_hygiene
        Repo Structure
        History Security
```

### 3. Camelot OS Full System Architecture with Sentinel Coverage

```mermaid
flowchart TB
    subgraph L7["L7 ETHEREAL"]
        ANYA_O["Anya Omega v202.0<br/>APEE v6.5 Compiler"]
        SONUS["Sir Sonus<br/>Voice Pipeline"]
    end

    subgraph L6["L6 GOVERNANCE"]
        SENTINEL_K["Sir Sentinel v2.0<br/>Universal Audit"]
        IRON["Iron Gate<br/>HITL Enforcement"]
        ZENITH["Zenith Scanner<br/>Hostile Pattern Detection"]
        WARDEN["Warden<br/>Zero-Trust Diode"]
        OCTAVIAN["Sir Octavian<br/>GIGO Filter"]
    end

    subgraph L5["L5 AGENTIC"]
        BORIS["Sir Boris v2.1<br/>13-Agent Critique"]
        APIS["Lady Apis<br/>Research Forager"]
        AGORA_K["Agora Orchestrator<br/>Swarm Controller"]
        SQUIRES["Squire Colony<br/>8 Sub-Agents"]
    end

    subgraph L4["L4 SEMANTIC"]
        CHRONOS["Chronos<br/>Titan Memory + UKG"]
        GLYPH["Sir Glyph<br/>Provenance Ledger"]
        OURO["Ouroboros<br/>SQLite WAL"]
    end

    subgraph L3["L3 NEURAL"]
        MERLIN_O["Merlin Omega<br/>GoT/DoT Router"]
        MGV["MGV Engine<br/>Complexity Analysis"]
        VIDEN["Videneptus<br/>Graph of Thoughts"]
    end

    subgraph L2["L2 KINETIC"]
        LUKAS["Lukas Edge<br/>Saltare/Cribo/Rotel"]
        KINETIC_E["Kinetic Edge MCP<br/>Rust Axum :3001"]
        IPC["Anya IPC Bridge<br/>Named Pipes"]
    end

    subgraph L1["L1 SUBSTRATE"]
        MORGANA["Morgana<br/>Modal Cloud + Docker"]
        CLIPROXY_K["CLIProxyAPI<br/>Go Binary :8080"]
        TAILSCALE_K["Tailscale Mesh<br/>Encrypted Overlay"]
        RUSTDESK_K["RustDesk Relay<br/>Remote Desktop"]
    end

    subgraph EXTERNAL["EXTERNAL"]
        GH["GitHub Actions<br/>CI/CD Pipeline"]
        MCP_S["MCP Servers<br/>NotebookLM/Gemini/Ollama"]
        LLM_P["LLM Providers<br/>29 Models via Proxy"]
    end

    %% Sentinel audit coverage arrows
    SENTINEL_K -.->|audit| ANYA_O
    SENTINEL_K -.->|audit| SONUS
    SENTINEL_K -.->|audit| IRON
    SENTINEL_K -.->|audit| ZENITH
    SENTINEL_K -.->|audit| WARDEN
    SENTINEL_K -.->|audit| BORIS
    SENTINEL_K -.->|audit| AGORA_K
    SENTINEL_K -.->|audit| SQUIRES
    SENTINEL_K -.->|audit| CHRONOS
    SENTINEL_K -.->|audit| GLYPH
    SENTINEL_K -.->|audit| OURO
    SENTINEL_K -.->|audit| MERLIN_O
    SENTINEL_K -.->|audit| MGV
    SENTINEL_K -.->|audit| LUKAS
    SENTINEL_K -.->|audit| KINETIC_E
    SENTINEL_K -.->|audit| IPC
    SENTINEL_K -.->|audit| MORGANA
    SENTINEL_K -.->|audit| CLIPROXY_K
    SENTINEL_K -.->|audit| TAILSCALE_K
    SENTINEL_K -.->|audit| RUSTDESK_K
    SENTINEL_K -.->|audit| GH
    SENTINEL_K -.->|audit| MCP_S
    SENTINEL_K -.->|audit| LLM_P

    %% Execution flow
    ANYA_O --> MERLIN_O
    MERLIN_O --> SENTINEL_K
    SENTINEL_K --> IRON
    IRON -->|approved| LUKAS
    IRON -->|blocked| GLYPH

    %% Data flow
    BORIS --> SQUIRES
    AGORA_K --> BORIS
    CHRONOS --> OURO
    GLYPH --> OURO
    LUKAS --> KINETIC_E
    KINETIC_E --> IPC
    IPC --> TAILSCALE_K
    CLIPROXY_K --> LLM_P
    MORGANA --> CLIPROXY_K

    style L7 fill:#2d1b69,stroke:#a855f7,color:#fff
    style L6 fill:#1b3a4b,stroke:#22d3ee,color:#fff
    style L5 fill:#1b4332,stroke:#4ade80,color:#fff
    style L4 fill:#422006,stroke:#f59e0b,color:#fff
    style L3 fill:#1e1b4b,stroke:#818cf8,color:#fff
    style L2 fill:#4a1d1d,stroke:#f87171,color:#fff
    style L1 fill:#0f172a,stroke:#94a3b8,color:#fff
    style EXTERNAL fill:#0d0d0d,stroke:#666,color:#fff
    style SENTINEL_K fill:#064e3b,stroke:#10b981,color:#fff,stroke-width:3px
```

### 4. Preset Routing Matrix

```mermaid
flowchart LR
    subgraph PRESETS["11 AUDIT PRESETS"]
        FULL["full<br/>25 domains"]
        NET["network<br/>3 domains"]
        KIN["kinetic<br/>2 domains"]
        SEC["security<br/>5 domains"]
        BRG["bridge<br/>3 domains"]
        INF["infrastructure<br/>4 domains"]
        KER["kernel<br/>5 domains"]
        CLI_P["cli<br/>3 domains"]
        AGT["agents<br/>3 domains"]
        GOV["governance<br/>4 domains"]
        VOX["voice<br/>1 domain"]
    end

    subgraph DOMAINS["25 AUDIT DOMAINS"]
        D01["tailscale<br/>13 checks"]
        D02["rustdesk<br/>8 checks"]
        D03["rust_bridge<br/>17 checks"]
        D04["kinetic_binaries<br/>12 checks"]
        D05["secrets<br/>13 checks"]
        D06["iron_gate<br/>8 checks"]
        D07["zenith_warden<br/>9 checks"]
        D08["dependencies<br/>14 checks"]
        D09["ci_cd<br/>12 checks"]
        D10["cliproxy<br/>12 checks"]
        D11["modal_cloud<br/>7 checks"]
        D12["docker<br/>9 checks"]
        D13["excalibur<br/>12 checks"]
        D14["agora<br/>8 checks"]
        D15["titan_memory<br/>10 checks"]
        D16["control_plane<br/>12 checks"]
        D17["mgv_engine<br/>4 checks"]
        D18["cli_pipeline<br/>21 checks"]
        D19["squire_colony<br/>12 checks"]
        D20["boris_critique<br/>16 checks"]
        D21["mcp_config<br/>13 checks"]
        D22["voice_pipeline<br/>9 checks"]
        D23["provenance<br/>9 checks"]
        D24["aiexclude<br/>12 checks"]
        D25["git_hygiene<br/>8 checks"]
    end

    NET --> D01 & D02 & D21
    KIN --> D03 & D04
    SEC --> D05 & D06 & D07 & D08 & D25
    BRG --> D01 & D03 & D02
    INF --> D09 & D10 & D11 & D12
    KER --> D13 & D14 & D15 & D16 & D17
    CLI_P --> D18 & D19 & D20
    AGT --> D19 & D20 & D16
    GOV --> D23 & D24 & D25 & D06
    VOX --> D22

    style PRESETS fill:#1a1a2e,stroke:#e94560,color:#fff
    style DOMAINS fill:#1a1a2e,stroke:#16c79a,color:#fff
```

### 5. Automated Check Execution Flow

```mermaid
sequenceDiagram
    participant U as User
    participant C as camelot.py
    participant A as Anya (Compiler)
    participant M as Merlin (Router)
    participant S as Sir Sentinel
    participant T as Tool Runner
    participant IG as Iron Gate
    participant L as Ledger

    U->>C: camelot exec "audit security"
    C->>A: compile_intent(directive)
    A-->>C: {intent: AUDIT, domain: SECURITY}

    C->>M: route(compiled_intent)
    M->>M: assess_risk(directive)
    M-->>C: {knight: Sir Sentinel, module: sentinel}

    C->>S: execute(directive, intent)
    S->>S: _resolve_targets("audit security")
    Note over S: Expands preset: secrets +<br/>iron_gate + zenith_warden +<br/>dependencies + git_hygiene

    loop Each Domain (5)
        S->>S: Build phase checklists
        loop Each Phase Command
            S->>T: _run_check(cmd)
            T-->>S: {returncode, stdout, stderr}
        end
    end

    S->>S: _scan_secrets(CAMELOT_OS)
    Note over S: 6 regex patterns ×<br/>500 files scanned

    S->>S: _check_ledger_sync()
    S->>S: Tally severity counts

    alt CRITICAL or HIGH found
        S->>IG: HITL LOCK ENGAGED
        IG-->>U: Awaiting "Make it so"
    else All clear
        S-->>U: CLEAR — auto-repair authorized
    end

    S-->>C: {status, output, files_created}
    C->>L: log_provenance(CLI/Sir Sentinel, ...)
    C->>L: log_execution(ouroboros)
    C-->>U: Formatted audit report
```

### 6. Split-Brain Topology — Control vs Kinetic with Sentinel Overlay

```mermaid
flowchart TB
    subgraph CONTROL["CONTROL PLANE (Pure Reasoning)"]
        direction TB
        CP_MAIN["control_plane/main.py<br/>Pydantic AI"]
        SOUL["SoulRouter<br/>Route decisions"]
        OMC["OMCTeam<br/>Multi-agent coordination"]
        SARDA["SARDAEngine<br/>Structured analysis"]
        DEER["DeerFlowSandbox<br/>Isolated execution"]
        A2A_MSG["A2AMessage<br/>Typed envelopes"]

        CP_MAIN --> SOUL
        CP_MAIN --> OMC
        CP_MAIN --> SARDA
        CP_MAIN --> DEER
        SOUL --> A2A_MSG
    end

    subgraph KINETIC["KINETIC EDGE (I/O + Execution)"]
        direction TB
        KE_MCP["kinetic_edge/mcp_server<br/>Rust Axum :3001"]
        SALT["Saltare<br/>Go CLI Gateway"]
        CRIBO_B["Cribo<br/>Rust Code Bundler"]
        ROTEL_B["Rotel<br/>Rust Telemetry"]
        IPC_B["anya_ipc_bridge.rs<br/>Named Pipes"]
        LEDGER_B["ledger.exe<br/>Go Binary"]

        KE_MCP --> SALT
        KE_MCP --> CRIBO_B
        KE_MCP --> ROTEL_B
        KE_MCP --> IPC_B
        KE_MCP --> LEDGER_B
    end

    subgraph NETWORK_L["NETWORK LAYER"]
        TS["Tailscale Mesh<br/>100.x.x.x overlay"]
        RD["RustDesk Relay<br/>hbbs/hbbr on TS IP"]
        PROXY["CLIProxyAPI<br/>Go :8080 → 29 models"]
    end

    subgraph AUDIT_OVERLAY["SENTINEL AUDIT OVERLAY"]
        direction TB
        SA["Sir Sentinel v2.0"]
        SA_N["Network Audit<br/>tailscale + rustdesk"]
        SA_K["Kinetic Audit<br/>rust_bridge + binaries"]
        SA_CP["Control Audit<br/>control_plane + a2a"]
        SA_S["Security Audit<br/>secrets + iron_gate + zenith"]

        SA --> SA_N & SA_K & SA_CP & SA_S
    end

    %% Split-brain boundary
    CONTROL <-->|"httpx only<br/>NO direct I/O"| KINETIC
    KINETIC <--> NETWORK_L

    %% Audit coverage
    SA_N -.->|covers| TS
    SA_N -.->|covers| RD
    SA_N -.->|covers| PROXY
    SA_K -.->|covers| KE_MCP
    SA_K -.->|covers| SALT
    SA_K -.->|covers| IPC_B
    SA_CP -.->|covers| CP_MAIN
    SA_CP -.->|covers| A2A_MSG
    SA_S -.->|covers| CONTROL
    SA_S -.->|covers| KINETIC

    style CONTROL fill:#1e1b4b,stroke:#818cf8,color:#fff
    style KINETIC fill:#4a1d1d,stroke:#f87171,color:#fff
    style NETWORK_L fill:#0f172a,stroke:#94a3b8,color:#fff
    style AUDIT_OVERLAY fill:#064e3b,stroke:#10b981,color:#fff,stroke-width:2px
    style SA fill:#064e3b,stroke:#10b981,color:#fff,stroke-width:3px
```

### 7. Knight Dispatch Matrix

```mermaid
flowchart LR
    subgraph INTENTS["Anya Intent Classification"]
        I1["PLAN"]
        I2["CREATE"]
        I3["RESEARCH"]
        I4["DESIGN"]
        I5["SECURE"]
        I6["AUDIT"]
        I7["DEBUG"]
    end

    subgraph KNIGHTS["Knight Registry"]
        K1["Sir Systema<br/>architect.py"]
        K2["Sir Forge<br/>coder.py"]
        K3["Lady Apis<br/>researcher.py"]
        K4["Lady Muse<br/>creative.py"]
        K5["Sir Zenith<br/>warden.py"]
        K6["Sir Sentinel<br/>sentinel.py"]
        K7["Sir Debug<br/>debug.py"]
        K8["Sir Boris<br/>boris.py"]
    end

    I1 --> K1
    I2 --> K2
    I3 --> K3
    I4 --> K4
    I5 --> K5
    I6 --> K6
    I7 --> K7
    K6 -.->|"13-Agent Critique<br/>sub-dispatch"| K8

    style I6 fill:#064e3b,stroke:#10b981,color:#fff,stroke-width:3px
    style K6 fill:#064e3b,stroke:#10b981,color:#fff,stroke-width:3px
    style INTENTS fill:#1a1a2e,stroke:#e94560,color:#fff
    style KNIGHTS fill:#1a1a2e,stroke:#16c79a,color:#fff
```
