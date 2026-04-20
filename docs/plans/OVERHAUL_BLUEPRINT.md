# CAMELOT_OS Overhaul Blueprint

**Codename:** Project Excalibur
**Objective:** Rebuild CAMELOT_OS as an edge-based, multi-platform, prompt-based operating system
**Date:** 2026-03-04
**Architect:** Claude Opus 4.6 + VaShawn O. Head (Sovereign)

---

## 1. Vision

CAMELOT_OS becomes a **prompt-native operating system layer** that runs on any device — laptop, server, Raspberry Pi, browser tab, or phone. The user speaks in natural language. The OS understands, plans, confirms, executes, and reports. All computation is local-first. No cloud dependency for core function.

```
"Back up my project folder every night"
    → Intent: ScheduledCopy
    → Plan: [locate_folder, select_dest, create_cron_job]
    → HITL: "I'll copy ~/Projects to /backup nightly at midnight. Approve?"
    → Execute: register_job()
    → Ledger: logged with hash
    → Response: "Done. First backup runs tonight."
```

This is what a prompt-based OS actually does. Every system interaction follows this pipeline.

---

## 2. Why Rebuild (Not Refactor)

### What Gets Kept (Design Assets)

| Asset | Source | Destination |
|---|---|---|
| Governance model (HITL, Titanium Laws, Iron Gate) | `docs/LAWS/`, `01_KERNEL/config/hitl_gate.json` | `governance/` |
| Agent persona definitions (Anya, Merlin, Lukas) | `AGENTS.md`, `.camelot/knights/` | `agents/personas/` |
| Skill definitions | `.agent/skills/` | `agents/skills/` |
| Cartridge system (mode switching) | `.camelot/cartridges/` | `agents/cartridges/` |
| Provenance ledger schema | `PROVENANCE_LEDGER.md` | `core/ledger/` |
| Knight capability model | `.hive/rules.yaml` | `agents/manifests/` |
| Constitution & laws | `docs/LAWS/CONSTITUTION.md` | `governance/` |

### What Gets Discarded (Technical Debt)

| Discarded | Reason |
|---|---|
| All Python kernel code | Not edge-viable (500MB+ runtime) |
| All hardcoded Windows paths | Non-portable by definition |
| Git history | Permanently credential-contaminated |
| `.exe` / `.pdb` binaries | Supply chain risk, not reproducible |
| Simulated kinetic stack | Must be real or not exist |
| `node_modules/`, `__pycache__/`, `tmp*/` | Build artifacts |
| All credential files | Compromised, must rotate |

### What Gets Rebuilt From Scratch

| Component | Old Tech | New Tech | Why |
|---|---|---|---|
| Kernel | Python | Rust | 5MB binary vs 500MB runtime. Memory-safe. Cross-compiles to every target. |
| Prompt Router | Does not exist | Rust + local LLM | The core product feature |
| Agent Runtime | Markdown personas | WASM sandboxed executors | Real isolation, real capability enforcement |
| Platform Layer | Hardcoded Win32 calls | Rust PAL with per-target impls | Write once, compile everywhere |
| UI Shell | React/Vite (PORTAL_CORE) | Tauri (desktop) + WASM (browser) | Native-speed desktop app, ~3MB |
| Memory/UKG | PostgreSQL reference | Embedded DB (redb/SQLite) | No external service dependency |
| Telemetry | Rotel stub (JSONL appender) | OpenTelemetry Rust SDK | Real distributed tracing |
| CI/CD | Windows-only GitHub Actions | Multi-platform matrix build | Linux + macOS + Windows + WASM |

---

## 3. Target Architecture

### 3.1 System Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                      USER INTERFACES                         │
│                                                              │
│  ┌─────────┐  ┌──────────────┐  ┌──────────┐  ┌─────────┐  │
│  │   CLI   │  │ Desktop App  │  │ Browser  │  │   API   │  │
│  │ (stdin) │  │   (Tauri)    │  │  (WASM)  │  │ (HTTP)  │  │
│  └────┬────┘  └──────┬───────┘  └────┬─────┘  └────┬────┘  │
│       │              │               │              │        │
│       └──────────────┴───────┬───────┴──────────────┘        │
│                              │                               │
│                              ▼                               │
│  ┌───────────────────────────────────────────────────────┐   │
│  │              PROMPT ROUTER  (Anya — The Gate)         │   │
│  │                                                       │   │
│  │   Input → Tokenize → Classify Intent → Route          │   │
│  │                                                       │   │
│  │   Intents: file.*, process.*, network.*, system.*,    │   │
│  │            agent.*, memory.*, config.*                 │   │
│  │                                                       │   │
│  │   Local LLM: Phi-3-mini / Qwen2-0.5B / TinyLlama    │   │
│  │   Fallback: Pattern matching for common commands      │   │
│  └───────────────────────┬───────────────────────────────┘   │
│                          │                                   │
│                          ▼                                   │
│  ┌───────────────────────────────────────────────────────┐   │
│  │              PLANNER  (Merlin — The Reasoner)         │   │
│  │                                                       │   │
│  │   Intent → Decompose → Dependency Graph → Plan        │   │
│  │                                                       │   │
│  │   Plan = ordered list of agent invocations with       │   │
│  │   declared inputs, outputs, and rollback actions      │   │
│  │                                                       │   │
│  │   For complex multi-step tasks, uses Tree-of-Thought  │   │
│  │   reasoning via local LLM. For simple tasks, uses     │   │
│  │   direct intent-to-action mapping (no LLM needed).    │   │
│  └───────────────────────┬───────────────────────────────┘   │
│                          │                                   │
│                          ▼                                   │
│  ┌───────────────────────────────────────────────────────┐   │
│  │                  HITL GATE                             │   │
│  │                                                       │   │
│  │   Review plan → Present to user → Await confirmation  │   │
│  │                                                       │   │
│  │   Auto-approve: read-only operations, status queries  │   │
│  │   Require approval: writes, deletes, network, config  │   │
│  │   Always require: system changes, security ops,       │   │
│  │                    agent installation, key rotation    │   │
│  └───────────────────────┬───────────────────────────────┘   │
│                          │                                   │
│                          ▼                                   │
│  ┌───────────────────────────────────────────────────────┐   │
│  │          EXECUTOR  (Lukas — The Forger)               │   │
│  │                                                       │   │
│  │   ┌──────────┐ ┌──────────┐ ┌──────────┐             │   │
│  │   │ Knight A │ │ Knight B │ │ Knight C │  ...        │   │
│  │   │(FileOps) │ │(Network) │ │(Process) │             │   │
│  │   │  [WASM]  │ │  [WASM]  │ │  [WASM]  │             │   │
│  │   └────┬─────┘ └────┬─────┘ └────┬─────┘             │   │
│  │        │             │            │                   │   │
│  │        └─────────────┼────────────┘                   │   │
│  │                      │                                │   │
│  │              Capability-Based Security                │   │
│  │        Each knight declares what it can access.       │   │
│  │        The runtime enforces those declarations.       │   │
│  │        A file knight CANNOT touch network.            │   │
│  └──────────────────────┬────────────────────────────────┘   │
│                         │                                    │
│                         ▼                                    │
│  ┌───────────────────────────────────────────────────────┐   │
│  │       PLATFORM ABSTRACTION LAYER  (PAL)               │   │
│  │                                                       │   │
│  │   Filesystem │ Process │ Network │ Memory │ Scheduler │   │
│  │   Display    │ Audio   │ Input   │ Crypto │ Storage   │   │
│  │                                                       │   │
│  │   Compile-time target selection:                      │   │
│  │     Windows  → Win32 API                              │   │
│  │     Linux    → syscalls / procfs                      │   │
│  │     macOS    → Darwin frameworks                      │   │
│  │     WASM     → Web APIs (sandboxed subset)            │   │
│  │     ARM/IoT  → minimal POSIX subset                   │   │
│  └───────────────────────┬───────────────────────────────┘   │
│                          │                                   │
│                          ▼                                   │
│  ┌───────────────────────────────────────────────────────┐   │
│  │             GOVERNANCE & MEMORY LAYER                 │   │
│  │                                                       │   │
│  │  ┌─────────────┐ ┌──────────────┐ ┌───────────────┐  │   │
│  │  │ Provenance  │ │    UKG       │ │   Titanium    │  │   │
│  │  │   Ledger    │ │  (Knowledge  │ │     Laws      │  │   │
│  │  │ (append-    │ │    Graph)    │ │  (Capability  │  │   │
│  │  │  only log)  │ │              │ │   Policies)   │  │   │
│  │  └─────────────┘ └──────────────┘ └───────────────┘  │   │
│  │                                                       │   │
│  │  All stored in embedded DB (redb/SQLite)              │   │
│  │  No external database dependency                      │   │
│  │  Encrypted at rest with user-held key                 │   │
│  └───────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
```

### 3.2 Repository Structure

```
camelot-os/
│
├── Cargo.toml                    # Rust workspace root
├── Cargo.lock
├── .github/
│   └── workflows/
│       ├── ci.yml                # Multi-platform build + test matrix
│       ├── release.yml           # Tagged release builds
│       └── security.yml          # Trivy + cargo-audit scanning
│
├── core/                         # The Rust kernel (library crate)
│   ├── Cargo.toml
│   └── src/
│       ├── lib.rs                # Public API surface
│       ├── prompt/               # PROMPT ROUTER (Anya)
│       │   ├── mod.rs
│       │   ├── tokenizer.rs      # Input normalization
│       │   ├── classifier.rs     # Intent classification (LLM or pattern)
│       │   ├── intents.rs        # Intent enum + parameter schemas
│       │   └── router.rs         # Intent → agent dispatch
│       │
│       ├── planner/              # PLANNER (Merlin)
│       │   ├── mod.rs
│       │   ├── decompose.rs      # Break intent into steps
│       │   ├── plan.rs           # Plan data structure
│       │   └── reasoning.rs      # Tree-of-Thought for complex tasks
│       │
│       ├── executor/             # EXECUTOR (Lukas)
│       │   ├── mod.rs
│       │   ├── runtime.rs        # WASM agent sandbox (wasmtime)
│       │   ├── capabilities.rs   # Capability declarations + enforcement
│       │   └── dispatch.rs       # Plan step → knight invocation
│       │
│       ├── pal/                  # PLATFORM ABSTRACTION LAYER
│       │   ├── mod.rs
│       │   ├── traits.rs         # Platform trait definitions
│       │   ├── fs.rs             # Filesystem abstraction
│       │   ├── process.rs        # Process management
│       │   ├── network.rs        # Network operations
│       │   ├── system.rs         # System info (RAM, CPU, disk)
│       │   ├── scheduler.rs      # Cron/scheduled tasks
│       │   ├── windows.rs        # Win32 implementations
│       │   ├── linux.rs          # Linux implementations
│       │   ├── macos.rs          # macOS implementations
│       │   └── web.rs            # WASM/browser implementations
│       │
│       ├── governance/           # GOVERNANCE LAYER
│       │   ├── mod.rs
│       │   ├── hitl.rs           # Human-in-the-loop gate
│       │   ├── iron_gate.rs      # Cryptographic confirmation (ported)
│       │   ├── laws.rs           # Titanium Laws enforcement
│       │   └── policy.rs         # Per-agent capability policies
│       │
│       ├── memory/               # MEMORY & KNOWLEDGE
│       │   ├── mod.rs
│       │   ├── store.rs          # Embedded DB interface (redb)
│       │   ├── ukg.rs            # Universal Knowledge Graph
│       │   ├── ledger.rs         # Provenance ledger (append-only)
│       │   └── session.rs        # Session context / working memory
│       │
│       ├── llm/                  # LOCAL LLM INFERENCE
│       │   ├── mod.rs
│       │   ├── engine.rs         # Inference engine abstraction
│       │   ├── gguf.rs           # GGUF model loading (llama.cpp)
│       │   ├── candle.rs         # Candle backend (optional)
│       │   └── models.rs         # Model registry + selection
│       │
│       └── telemetry/            # OBSERVABILITY
│           ├── mod.rs
│           ├── traces.rs         # OpenTelemetry spans
│           ├── metrics.rs        # System + agent metrics
│           └── export.rs         # OTLP / file / stdout exporters
│
├── edge/                         # PLATFORM-SPECIFIC SHELLS
│   ├── cli/                      # Terminal interface
│   │   ├── Cargo.toml
│   │   └── src/
│   │       └── main.rs           # REPL: read prompt → core → print result
│   │
│   ├── desktop/                  # Tauri desktop app (Win/Mac/Linux)
│   │   ├── Cargo.toml
│   │   ├── tauri.conf.json
│   │   └── src/
│   │       ├── main.rs           # Tauri bootstrap
│   │       └── commands.rs       # Tauri IPC → core bridge
│   │
│   ├── web/                      # Browser WASM target
│   │   ├── Cargo.toml
│   │   ├── src/
│   │   │   └── lib.rs            # wasm-bindgen exports
│   │   └── www/
│   │       ├── index.html
│   │       └── app.js            # Minimal JS glue
│   │
│   └── api/                      # HTTP API server (for integrations)
│       ├── Cargo.toml
│       └── src/
│           └── main.rs           # Axum server exposing core over HTTP
│
├── agents/                       # AGENT DEFINITIONS (not Rust — config)
│   ├── knights/                  # Knight manifests (TOML)
│   │   ├── sir_file_ops.toml
│   │   ├── sir_network.toml
│   │   ├── sir_process.toml
│   │   ├── sir_system.toml
│   │   ├── sir_memory.toml
│   │   └── sir_sentinel.toml
│   │
│   ├── personas/                 # Triad persona prompts (ported from AGENTS.md)
│   │   ├── anya.toml             # The Compiler — prompt parsing personality
│   │   ├── merlin.toml           # The Reasoner — planning personality
│   │   └── lukas.toml            # The Forger — execution personality
│   │
│   ├── cartridges/               # Mode cartridges (ported from .camelot/)
│   │   ├── ant.toml
│   │   ├── beaver.toml
│   │   ├── spider.toml
│   │   ├── octopus.toml
│   │   └── alchemist.toml
│   │
│   ├── skills/                   # Skill definitions (ported from .agent/skills/)
│   │   ├── security_audit.toml
│   │   ├── research_forager.toml
│   │   ├── tdd_architect.toml
│   │   └── mcp_builder.toml
│   │
│   └── wasm/                     # Compiled WASM knight binaries
│       └── .gitkeep              # Built by CI, not committed
│
├── governance/                   # GOVERNANCE DOCUMENTS (ported)
│   ├── CONSTITUTION.md
│   ├── TITANIUM_LAWS.md
│   ├── CONTRIBUTING.md
│   ├── SECURITY.md
│   └── policies/
│       ├── hitl_policy.toml      # What requires confirmation
│       ├── capability_matrix.toml # Knight → capability mapping
│       └── data_sovereignty.toml  # Where data can flow
│
├── models/                       # LOCAL LLM MODELS (gitignored)
│   ├── .gitkeep
│   └── README.md                 # Instructions to download models
│
├── tests/                        # INTEGRATION TESTS
│   ├── prompt_routing.rs
│   ├── plan_generation.rs
│   ├── agent_sandbox.rs
│   ├── hitl_flow.rs
│   ├── cross_platform.rs
│   └── ledger_integrity.rs
│
├── .gitignore
├── LICENSE
├── README.md
└── PROVENANCE_LEDGER.md          # Append-only audit trail (real hashes only)
```

---

## 4. Core Components In Detail

### 4.1 Prompt Router (Anya — The Gate)

The prompt router is the front door. Every user interaction enters here. It has two modes:

**Fast Path (Pattern Matching)**
For common, well-known commands, no LLM is needed:
```
"list files"           → Intent::File(List { path: cwd })
"show memory"          → Intent::System(MemoryInfo)
"what time is it"      → Intent::System(DateTime)
"open terminal"        → Intent::Process(Spawn { cmd: "shell" })
```

This is a trie/regex-based classifier that handles ~80% of interactions at microsecond latency.

**Deep Path (Local LLM)**
For ambiguous, complex, or novel requests:
```
"find all the PDFs I worked on last week and zip them up"
    → LLM classifies: Intent::File(Search + Archive)
    → Parameters: { pattern: "*.pdf", modified_after: "7d ago", action: "zip" }
```

The LLM runs locally. Candidate models (all runnable on CPU):

| Model | Size | RAM | Use Case |
|---|---|---|---|
| Qwen2-0.5B-Instruct | 400MB | 1GB | Minimum viable, IoT/Pi |
| Phi-3-mini-4k-instruct | 2.2GB | 4GB | Good balance, laptop |
| TinyLlama-1.1B-Chat | 700MB | 2GB | Fast, decent accuracy |
| Mistral-7B-Instruct (Q4) | 4GB | 8GB | Best accuracy, desktop |

The model is loaded once at boot and stays in memory. Intent classification is a constrained generation task (output must be valid JSON matching the intent schema), which small models handle well.

**Intent Schema**
```rust
pub enum Intent {
    File(FileOp),
    Process(ProcessOp),
    Network(NetworkOp),
    System(SystemOp),
    Agent(AgentOp),
    Memory(MemoryOp),
    Config(ConfigOp),
    Meta(MetaOp),       // "help", "status", "version"
    Unknown(String),     // Fallback: echo back with "I don't understand"
}

pub enum FileOp {
    List { path: PathBuf, recursive: bool, filter: Option<String> },
    Read { path: PathBuf, encoding: Option<String> },
    Write { path: PathBuf, content: String },
    Copy { source: PathBuf, dest: PathBuf },
    Move { source: PathBuf, dest: PathBuf },
    Delete { path: PathBuf },
    Search { pattern: String, scope: PathBuf },
    Archive { sources: Vec<PathBuf>, dest: PathBuf, format: ArchiveFormat },
    Watch { path: PathBuf, on_change: Box<Intent> },
}
```

### 4.2 Planner (Merlin — The Reasoner)

The planner takes a classified intent and produces an execution plan.

**Simple intents** map directly to a single agent call:
```
Intent::File(List { path: "/home/user", recursive: false, filter: None })
    → Plan { steps: [
        Step { knight: "sir_file_ops", action: "list", params: {...} }
    ]}
```

**Complex intents** decompose into a dependency graph:
```
"Find all PDFs from last week and zip them up"
    → Plan { steps: [
        Step { id: 1, knight: "sir_file_ops", action: "search",
               params: { pattern: "*.pdf", modified_after: "7d" },
               output: "found_files" },
        Step { id: 2, knight: "sir_file_ops", action: "archive",
               params: { sources: "$found_files", format: "zip" },
               depends_on: [1] },
    ]}
```

**Rollback support**: Each step can declare a rollback action. If step 3 of 5 fails, steps 2 and 1 are rolled back in reverse order (if rollback actions are defined).

```rust
pub struct Plan {
    pub id: PlanId,
    pub intent: Intent,
    pub steps: Vec<Step>,
    pub hitl_required: bool,      // Does this plan need user confirmation?
    pub estimated_impact: Impact,  // read_only | writes | destructive | system
    pub rollback: Option<Vec<Step>>,
}

pub struct Step {
    pub id: StepId,
    pub knight: String,
    pub action: String,
    pub params: serde_json::Value,
    pub depends_on: Vec<StepId>,
    pub output_key: Option<String>,
    pub rollback_action: Option<String>,
}
```

### 4.3 HITL Gate (Governance Core)

The HITL gate inspects every plan before execution. Classification:

| Impact Level | Action | Example |
|---|---|---|
| `read_only` | Auto-approve | "list files", "show memory", "what version" |
| `writes` | Confirm once | "create a file", "rename folder" |
| `destructive` | Confirm with details | "delete all .log files", "kill process" |
| `system` | Confirm + require token | "change startup config", "install agent", "modify permissions" |

Confirmation flow:
```
[CAMELOT] Plan: Delete 47 .log files older than 7 days from ~/Projects
          Impact: DESTRUCTIVE
          Rollback: Not available (deletion is permanent)

          Approve? [y/N] ▌
```

For `system`-level actions, a confirmation token is required (ported from current `iron_gate.py` using `secrets.compare_digest()`).

### 4.4 Executor & Knight Sandbox (Lukas — The Forger)

Knights are compiled to **WebAssembly** and run in a **wasmtime** sandbox. This provides:

1. **Memory isolation**: Each knight gets its own linear memory. A buggy knight cannot corrupt another knight's state or the kernel.
2. **Capability enforcement**: A knight can only call PAL functions it has been granted. The WASM runtime intercepts all host calls and checks the capability manifest.
3. **Resource limits**: CPU time, memory allocation, and I/O bandwidth are capped per-knight.
4. **Hot-reloading**: New knights can be loaded at runtime without restarting the OS. Users can install community knights.

**Knight manifest format:**

```toml
# agents/knights/sir_file_ops.toml
[knight]
name = "Sir FileOps"
version = "1.0.0"
description = "Filesystem operations — read, write, copy, move, delete, search, archive"
author = "CAMELOT Core"
wasm = "sir_file_ops.wasm"

[capabilities]
filesystem = ["read", "write", "delete", "list", "watch", "archive"]
network = []
process = []
system = ["clock"]     # Needs timestamps for file operations
memory = ["session"]   # Can store session context

[limits]
max_memory_mb = 128
max_cpu_ms_per_call = 5000
max_file_size_mb = 500

[triggers]
intents = [
    "file.list", "file.read", "file.write", "file.copy",
    "file.move", "file.delete", "file.search", "file.archive",
    "file.watch"
]
```

**Knight WASM interface (what a knight sees):**

```rust
// This is the API available to knight WASM modules
// Implemented as wasmtime host functions

// Filesystem (only if granted)
fn pal_fs_read(path: &str) -> Result<Vec<u8>>;
fn pal_fs_write(path: &str, data: &[u8]) -> Result<()>;
fn pal_fs_list(path: &str) -> Result<Vec<DirEntry>>;
fn pal_fs_delete(path: &str) -> Result<()>;
fn pal_fs_metadata(path: &str) -> Result<Metadata>;

// System (only if granted)
fn pal_clock_now() -> Result<u64>;

// Memory (only if granted)
fn pal_session_get(key: &str) -> Result<Option<Vec<u8>>>;
fn pal_session_set(key: &str, value: &[u8]) -> Result<()>;

// Logging (always available)
fn pal_log(level: u8, message: &str);
```

If a knight tries to call `pal_fs_delete` but its manifest doesn't include `filesystem.delete`, the call traps immediately with a `CapabilityDenied` error. This is the Titanium Laws made real.

### 4.5 Platform Abstraction Layer (PAL)

Every system interaction goes through platform traits. At compile time, `#[cfg(target_os)]` selects the implementation:

```rust
// core/pal/src/traits.rs

pub trait Filesystem: Send + Sync {
    fn read(&self, path: &Path) -> Result<Vec<u8>>;
    fn write(&self, path: &Path, data: &[u8]) -> Result<()>;
    fn append(&self, path: &Path, data: &[u8]) -> Result<()>;
    fn delete(&self, path: &Path) -> Result<()>;
    fn list(&self, path: &Path) -> Result<Vec<DirEntry>>;
    fn exists(&self, path: &Path) -> bool;
    fn metadata(&self, path: &Path) -> Result<Metadata>;
    fn watch(&self, path: &Path) -> Result<Receiver<FsEvent>>;
    fn temp_dir(&self) -> PathBuf;
    fn home_dir(&self) -> Option<PathBuf>;
}

pub trait SystemInfo: Send + Sync {
    fn os_name(&self) -> &str;
    fn os_version(&self) -> String;
    fn arch(&self) -> &str;
    fn hostname(&self) -> String;
    fn free_memory_bytes(&self) -> Result<u64>;
    fn total_memory_bytes(&self) -> Result<u64>;
    fn cpu_usage_percent(&self) -> Result<f32>;
    fn cpu_count(&self) -> usize;
    fn disk_info(&self, mount: &Path) -> Result<DiskInfo>;
    fn uptime_seconds(&self) -> Result<u64>;
}

pub trait ProcessManager: Send + Sync {
    fn spawn(&self, cmd: &str, args: &[&str]) -> Result<ProcessHandle>;
    fn kill(&self, pid: u32) -> Result<()>;
    fn list(&self) -> Result<Vec<ProcessInfo>>;
    fn wait(&self, handle: &ProcessHandle) -> Result<ExitStatus>;
}

pub trait Scheduler: Send + Sync {
    fn schedule(&self, name: &str, cron: &str, action: Intent) -> Result<JobId>;
    fn cancel(&self, id: JobId) -> Result<()>;
    fn list_jobs(&self) -> Result<Vec<ScheduledJob>>;
    fn next_run(&self, id: JobId) -> Result<Option<DateTime>>;
}

pub trait NetworkClient: Send + Sync {
    fn http_get(&self, url: &str, headers: &Headers) -> Result<Response>;
    fn http_post(&self, url: &str, body: &[u8], headers: &Headers) -> Result<Response>;
    fn download(&self, url: &str, dest: &Path) -> Result<u64>;
    fn dns_resolve(&self, hostname: &str) -> Result<Vec<IpAddr>>;
}
```

**Platform implementations:**

```rust
// core/pal/src/windows.rs
#[cfg(target_os = "windows")]
pub struct WindowsPal;

#[cfg(target_os = "windows")]
impl SystemInfo for WindowsPal {
    fn free_memory_bytes(&self) -> Result<u64> {
        // Uses GlobalMemoryStatusEx from Win32 API
        // No PowerShell, no subprocess — direct FFI
    }
}

// core/pal/src/linux.rs
#[cfg(target_os = "linux")]
pub struct LinuxPal;

#[cfg(target_os = "linux")]
impl SystemInfo for LinuxPal {
    fn free_memory_bytes(&self) -> Result<u64> {
        // Reads /proc/meminfo directly — zero overhead
    }
}

// core/pal/src/web.rs
#[cfg(target_arch = "wasm32")]
pub struct WebPal;

#[cfg(target_arch = "wasm32")]
impl SystemInfo for WebPal {
    fn free_memory_bytes(&self) -> Result<u64> {
        // navigator.deviceMemory (limited precision, ~GB granularity)
        // or performance.memory in Chrome
    }
}
```

### 4.6 Memory & Knowledge Layer

#### Provenance Ledger

Every action is logged with real cryptographic hashes:

```rust
pub struct LedgerEntry {
    pub id: u64,                   // Monotonic sequence number
    pub timestamp: DateTime<Utc>,
    pub actor: Actor,              // User, Knight, System
    pub action: String,            // "file.delete", "config.change"
    pub target: String,            // What was acted on
    pub result: ActionResult,      // Success, Failure, Denied
    pub plan_id: Option<PlanId>,   // Which plan this step belongs to
    pub prev_hash: [u8; 32],       // SHA-256 of previous entry (chain)
    pub hash: [u8; 32],            // SHA-256 of this entry
}
```

The ledger is an append-only chain (each entry hashes the previous). Tampering with any entry breaks the chain. Stored in embedded `redb` database — no external PostgreSQL.

#### Universal Knowledge Graph (UKG)

Local-first knowledge graph for:
- User preferences ("I prefer dark mode", "My backup drive is D:")
- System state ("Last backup was 2026-03-03 at midnight")
- Agent memory ("Sir FileOps has processed 1,247 file operations")
- Context ("The current project is CAMELOT_OS in ~/Projects")

Storage: `redb` key-value store with triple-based indexing (subject, predicate, object) for graph queries. No external database.

### 4.7 Local LLM Inference

The kernel embeds LLM inference for prompt understanding. Two backend options:

**Option A: llama-cpp-rs (recommended for Phase 1)**
- Bindings to llama.cpp
- Supports GGUF quantized models
- CPU inference (no GPU required)
- AVX2/NEON acceleration on modern CPUs
- ~5 tokens/sec on CPU for 0.5B model (fast enough for intent classification)

**Option B: Candle (long-term)**
- Pure Rust ML framework by HuggingFace
- No C/C++ dependency
- WASM compatible (runs in browser)
- Better for the WASM target in Phase 3

**Constrained generation**: Intent classification isn't open-ended text generation. The LLM outputs JSON matching the `Intent` schema. This is enforced via grammar-constrained decoding (llama.cpp supports GBNF grammars), which means:
- Output is always valid JSON
- Output always matches the intent schema
- Generation is faster (fewer tokens, constrained search space)
- Small models perform much better on constrained tasks than open generation

---

## 5. Multi-Platform Build Matrix

### 5.1 Targets

| Target | Triple | Shell | Size (est.) |
|---|---|---|---|
| Windows x86_64 | `x86_64-pc-windows-msvc` | CLI + Tauri | ~8MB |
| macOS x86_64 | `x86_64-apple-darwin` | CLI + Tauri | ~8MB |
| macOS ARM | `aarch64-apple-darwin` | CLI + Tauri | ~7MB |
| Linux x86_64 | `x86_64-unknown-linux-musl` | CLI + Tauri | ~6MB |
| Linux ARM | `aarch64-unknown-linux-musl` | CLI | ~5MB |
| WebAssembly | `wasm32-unknown-unknown` | Browser | ~3MB |

### 5.2 CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CAMELOT CI

on: [push, pull_request]

jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
      - run: cargo test --workspace

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cargo install cargo-audit
      - run: cargo audit
      - uses: aquasecurity/trivy-action@master
        with:
          scan-type: fs
          scan-ref: .
          scanners: vuln,secret

  wasm:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          targets: wasm32-unknown-unknown
      - run: cargo build --target wasm32-unknown-unknown -p camelot-web

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: clippy, rustfmt
      - run: cargo fmt --all -- --check
      - run: cargo clippy --workspace -- -D warnings
```

---

## 6. Implementation Phases

### Phase 1: Foundation (Weeks 1-3)

**Goal:** Rust workspace compiles. CLI takes a prompt and echoes parsed intent. One knight works.

**Deliverables:**
- [ ] New repo `camelot-os` initialized with Cargo workspace
- [ ] `core/` crate with prompt router (pattern matching only, no LLM yet)
- [ ] Intent enum with `File`, `System`, `Meta` variants
- [ ] PAL traits defined for Filesystem and SystemInfo
- [ ] PAL implementations for current dev platform (Windows)
- [ ] `edge/cli/` binary — REPL that reads prompt, classifies, prints intent
- [ ] `sir_file_ops` knight as native Rust (not WASM yet) — list, read, write, delete
- [ ] HITL gate — console confirmation for write/delete operations
- [ ] Provenance ledger — append-only log to embedded DB
- [ ] Integration tests for prompt → intent → execute → log flow
- [ ] CI pipeline (cargo test, clippy, fmt, audit)
- [ ] Port `CONSTITUTION.md`, `TITANIUM_LAWS.md`, `CONTRIBUTING.md`

**Milestone check:** User can type `"list files in Documents"` in the CLI and see directory contents. `"delete test.txt"` asks for confirmation. All actions are logged.

### Phase 2: Prompt Intelligence (Weeks 4-6)

**Goal:** Local LLM handles ambiguous prompts. Planner decomposes multi-step tasks.

**Deliverables:**
- [ ] Integrate `llama-cpp-rs` for local inference
- [ ] Download script for recommended model (Phi-3-mini or Qwen2-0.5B)
- [ ] Intent classifier using constrained LLM generation
- [ ] Planner module — decompose complex intents into step sequences
- [ ] Dependency resolution in plans (step 2 waits for step 1's output)
- [ ] Rollback support for failed multi-step plans
- [ ] Session memory — remember context within a session ("that folder" = last mentioned path)
- [ ] `sir_process` knight — spawn, list, kill processes
- [ ] `sir_system` knight — memory, CPU, disk, uptime queries
- [ ] UKG store — persist user preferences and system knowledge

**Milestone check:** User can type `"find all PDFs from last week and zip them"` and the system decomposes it into search → archive, confirms the plan, executes it, and logs it.

### Phase 3: Multi-Platform (Weeks 7-9)

**Goal:** Same binary runs on Windows, macOS, and Linux. Browser version works.

**Deliverables:**
- [ ] PAL implementations for Linux (procfs, syscalls)
- [ ] PAL implementations for macOS (Darwin frameworks)
- [ ] PAL subset for WASM (Web APIs)
- [ ] Tauri desktop shell (`edge/desktop/`)
- [ ] WASM browser target (`edge/web/`)
- [ ] Cross-compilation CI matrix (all 6 targets)
- [ ] Release workflow — tagged builds produce platform binaries
- [ ] `sir_network` knight — HTTP requests, DNS, download
- [ ] Installer/setup script for each platform

**Milestone check:** Same codebase produces working CLI on Windows, macOS, Linux. Browser version handles basic prompts. Desktop app has a terminal-style UI.

### Phase 4: Agent Ecosystem (Weeks 10-14)

**Goal:** Knights run in WASM sandbox. Community can create new knights.

**Deliverables:**
- [ ] WASM sandbox using `wasmtime`
- [ ] Knight WASM interface (host functions for PAL access)
- [ ] Capability enforcement at runtime
- [ ] Resource limits (memory, CPU time, I/O)
- [ ] Knight package format (`.toml` manifest + `.wasm` binary)
- [ ] Hot-reload — install/update knights without restart
- [ ] Port all persona definitions from CAMELOT_OS (Anya, Merlin, Lukas)
- [ ] Port cartridge system (mode switching)
- [ ] Port skill definitions as knight configurations
- [ ] `sir_sentinel` knight — file integrity monitoring, drift detection
- [ ] `sir_memory` knight — UKG queries, knowledge management
- [ ] Knight development SDK + documentation

**Milestone check:** A third-party developer can write a knight in Rust, compile to WASM, define a manifest, and install it into a running CAMELOT_OS instance. The knight can only access capabilities declared in its manifest.

### Phase 5: Hardening & Polish (Weeks 15-18)

**Goal:** Production-quality security, telemetry, and UX.

**Deliverables:**
- [ ] OpenTelemetry integration (real traces, not JSONL stubs)
- [ ] Encrypted-at-rest storage (user-held key, not committed to repo)
- [ ] Semantic prompt injection detection (embedding-based, not regex)
- [ ] Error recovery and graceful degradation
- [ ] Offline model download + management CLI
- [ ] Shell completion (bash, zsh, fish, PowerShell)
- [ ] Desktop app polish — themes, settings, keyboard shortcuts
- [ ] Performance benchmarks and optimization
- [ ] Security audit (real one, by humans)
- [ ] User documentation and tutorials
- [ ] v1.0.0 release

---

## 7. Migration Checklist

### Before Starting New Repo

- [ ] **Rotate ALL credentials** (GitHub, HuggingFace, Google, Modal) — do this FIRST
- [ ] **Export design docs** from current CAMELOT_OS to a `legacy-design/` archive
- [ ] **Archive current repo** — rename to `camelot-os-legacy`, mark as archived on GitHub
- [ ] **Create new repo** `camelot-os` (lowercase) with clean `.gitignore`

### Design Assets to Port

```bash
# From current CAMELOT_OS, copy these to the new repo's governance/ and agents/ dirs:
docs/LAWS/CONSTITUTION.md        → governance/CONSTITUTION.md
docs/LAWS/TITANIUM_LAWS.md       → governance/TITANIUM_LAWS.md
CONTRIBUTING.md                  → governance/CONTRIBUTING.md (adapt for Rust)
AGENTS.md                        → agents/personas/ (split into per-persona TOML)
.camelot/cartridges/*.md         → agents/cartridges/ (convert to TOML)
.camelot/knights/*.md            → agents/knights/ (convert to TOML manifests)
.agent/skills/*.md               → agents/skills/ (convert to TOML)
.hive/rules.yaml                 → governance/policies/ (convert to TOML)
01_KERNEL/config/hitl_gate.json  → governance/policies/hitl_policy.toml
```

### What NOT to Port

- Any `.py`, `.go`, `.rs` source code (all stubs or non-portable)
- Any credential file, `.env`, `.key`, `.toml` with secrets
- Any compiled binary (`.exe`, `.pdb`)
- Any build artifact (`target/`, `node_modules/`, `__pycache__/`)
- `PROVENANCE_LEDGER.md` (start fresh — old entries have fake hashes)
- `tmp/`, `tmp_awesome_repo/`, `dist/`
- `.git-credentials`, `.gitconfig`, `.modal.toml`

---

## 8. Technology Decisions

### 8.1 Why Rust (Not Go, Not Python, Not TypeScript)

| Requirement | Rust | Go | Python | TypeScript |
|---|---|---|---|---|
| Single binary, no runtime | Yes | Yes | No (needs interpreter) | No (needs Node/Deno) |
| WASM target | Excellent | Limited | No | Via wasm-bindgen |
| Memory safety | Guaranteed | GC pauses | GC | GC |
| Cross-compile all targets | cargo target | GOOS/GOARCH | Not viable | Not native |
| Embed LLM inference | llama-cpp-rs, candle | Limited | Good but heavy | Not viable |
| Binary size | 3-10MB | 10-20MB | N/A | N/A |
| Startup time | <10ms | <50ms | 500ms+ | 200ms+ |
| WASM sandbox (wasmtime) | Native | Not mature | Not viable | Not viable |

Go was the second choice but loses on WASM support, binary size, and the wasmtime ecosystem being Rust-native.

### 8.2 Why Tauri (Not Electron)

| | Tauri | Electron |
|---|---|---|
| Bundle size | 3-8MB | 150-300MB |
| RAM usage | 30-80MB | 200-500MB |
| Backend | Rust (our kernel) | Node.js (separate runtime) |
| Security | Process isolation, CSP | Chromium sandbox |
| Platform | Win/Mac/Linux/mobile(beta) | Win/Mac/Linux |

Tauri's backend IS Rust. The kernel code runs directly as the Tauri backend — no bridge, no serialization overhead.

### 8.3 Why redb (Not SQLite, Not PostgreSQL)

| | redb | SQLite | PostgreSQL |
|---|---|---|---|
| Dependency | Pure Rust, embedded | C library (FFI) | External server |
| Deployment | Zero config | Zero config | Requires install + admin |
| WASM compatible | Yes (with adapters) | Via sql.js (heavy) | No |
| ACID transactions | Yes | Yes | Yes |
| Binary size impact | ~200KB | ~1.5MB (C lib) | N/A |
| Use case fit | KV + structured data | Relational queries | Multi-user server |

SQLite is the fallback if relational queries are needed. PostgreSQL is eliminated — edge means no external server dependencies.

### 8.4 Why WASM Sandboxing (Not Docker, Not OS Processes)

| | WASM (wasmtime) | Docker | OS Processes |
|---|---|---|---|
| Startup time | <1ms | 500ms-5s | 50-200ms |
| Isolation | Memory + capability | Full OS | PID/uid only |
| Cross-platform | Identical everywhere | Linux only* | Platform-specific |
| Resource control | Fine-grained | cgroups (Linux) | ulimits (limited) |
| Binary size | ~50KB per agent | ~50MB per image | Varies |

*Docker Desktop exists for Win/Mac but adds 2GB+ overhead and requires Hyper-V/VirtIO.

WASM gives us sub-millisecond agent startup with memory isolation and capability enforcement, on every platform, at negligible binary size cost.

---

## 9. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Local LLM too slow on low-end devices | Medium | High | Pattern matching fast-path handles 80% of prompts; LLM is optional |
| WASM sandbox limits knight capabilities | Low | Medium | Host functions can expose any PAL capability; sandbox is permissive by design |
| Tauri mobile support immature | Medium | Low | CLI works everywhere; mobile is Phase 5+ |
| Model download size deters users | Medium | Medium | Ship with pattern matching only; LLM is opt-in download |
| Scope creep beyond OS primitives | High | High | Titanium Laws: only system operations, not application logic |
| Single developer velocity | High | Medium | Phase 1-2 are small scope; community contribution after Phase 4 |

---

## 10. Success Criteria

### v0.1.0 (Phase 1 Complete)
- [ ] CLI accepts natural language, classifies intent, executes file operations
- [ ] HITL confirmation for destructive actions
- [ ] Provenance ledger logs all actions with real SHA-256 hashes
- [ ] Compiles and runs on developer's Windows machine
- [ ] All tests pass, CI is green

### v0.5.0 (Phase 3 Complete)
- [ ] Same binary works on Windows, macOS, Linux
- [ ] Browser WASM version handles basic prompts
- [ ] Desktop app (Tauri) provides GUI terminal
- [ ] Local LLM handles ambiguous prompts
- [ ] Multi-step plans with dependency resolution

### v1.0.0 (Phase 5 Complete)
- [ ] WASM-sandboxed knights with capability enforcement
- [ ] Knight SDK for community development
- [ ] Encrypted-at-rest storage
- [ ] OpenTelemetry observability
- [ ] Production security audit passed
- [ ] Documentation and tutorials complete

---

*This blueprint is a living document. Update it as decisions are made and phases are completed. The Provenance Ledger in the new repo should record every architectural decision with rationale.*

**The Spire will be rebuilt. Stronger. Portable. Real.**
