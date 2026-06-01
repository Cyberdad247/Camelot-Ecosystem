# CAMELOT GLOBAL DEPLOY — BLUEPRINT
# Codename: WARP_GATE v1.0.0
# Lead: SIR_BORIS v3.0 | Multi-Knight: SIR_ALEX · SIR_FORGE · SIR_SENTINEL · SIR_HELIO · LADY_MNEMOSYNE · LADY_APIS
# Date: 2026-05-14 | Status: FORGE_READY

---

## MISSION STATEMENT

Deploy Camelot-OS as a **first-class global terminal AI** — indistinguishable in UX from `claude`,
`gemini`, or `codex` in terms of install simplicity and accessibility, but infinitely more powerful:
a sovereign multi-knight OS that auto-configures to available hardware/API keys, injects the full
Camelot constitution as live context, and routes every prompt through OmniRoute to the optimal
frontier model. Works from fresh install, existing machine, or thumbdrive — zero friction, zero
configuration required from the user.

**North Star:** `camelot` typed anywhere on any machine → you are inside Camelot-OS in ≤3 seconds.

---

## DESIGN PRINCIPLES (SIR_BORIS)

1. **Zero-config first boot** — auto-probe environment; never block on missing config
2. **Graceful tier degradation** — T3 cloud → T2 standard → T1 local-hybrid → T0 air-gapped (Ollama only)
3. **Context is sovereign** — CLAUDE.md constitution + active cartridge always injected as system prompt
4. **Portable by default** — single binary that runs from thumbdrive, no install required
5. **Privacy-first routing** — sensitive keywords → SIR_GHOST (air-gapped) before any cloud call
6. **Parity with incumbents** — `pip install camelot-os`, shell integration, tab completion like `claude`/`gemini`

---

## SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CAMELOT WARP GATE v1.0.0                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [USER]                                                                     │
│    │ types: camelot / ks / camelot warp                                     │
│    ▼                                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    ENTRY POINT (bin/camelot.py)                    │    │
│  │  Sub-commands: warp | configure | install | status | build         │    │
│  └─────────────────┬───────────────────────────────────────────────────┘    │
│                    │                                                        │
│         ┌──────────▼──────────┐                                            │
│         │  AUTO-CONFIG ENGINE  │  (bin/camelot_configure.py)               │
│         │  ─────────────────  │                                            │
│         │  1. Probe CLIProxy  │  → :8080 → T3                             │
│         │  2. Probe Ollama    │  → :11434 → T0/T1                         │
│         │  3. Scan env keys   │  → ANTHROPIC/GOOGLE/OPENAI                │
│         │  4. Detect RAM/GPU  │  → tier ceiling                           │
│         │  5. Detect portable │  → thumbdrive mode                        │
│         │  6. Write config    │  → ~/.camelot/config.json                 │
│         └──────────┬──────────┘                                            │
│                    │                                                        │
│         ┌──────────▼──────────┐                                            │
│         │  CONTEXT INJECTOR   │  (bin/camelot_context.py — LADY_MNEMOSYNE) │
│         │  ─────────────────  │                                            │
│         │  CLAUDE.md          │  → Camelot constitution (full)             │
│         │  Active cartridge   │  → domain-detected (python/rust/nextjs)    │
│         │  Knight persona     │  → selected knight's identity block        │
│         │  UKG snapshot       │  → compressed toon_ukg_full.json anchor    │
│         └──────────┬──────────┘                                            │
│                    │                                                        │
│         ┌──────────▼──────────┐                                            │
│         │  OMNIROUTE ENGINE   │  (control_plane/cli_intercept.py)          │
│         │  ─────────────────  │                                            │
│         │  Privacy Override   │  → keywords → SIR_GHOST                   │
│         │  Soul Equation      │  → S_ω = αV+βM+γP+δE                      │
│         │  Tier Classifier    │  → T0/T1/T2/T3                            │
│         │  Fallback Chain     │  → cliproxy→gemini→codex→open_coder        │
│         └──────────┬──────────┘                                            │
│                    │                                                        │
│         ┌──────────▼──────────┐                                            │
│         │  CLIProxy :8080     │  (127.0.0.1:8080/v1 — OpenAI compatible)  │
│         │  or Direct API      │  (Anthropic/Google/OpenAI direct)          │
│         │  or Ollama :11434   │  (air-gapped local)                        │
│         └─────────────────────┘                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## COMPONENT DESIGNS

### COMPONENT 1 — `camelot` Entry Point (SIR_BORIS + SIR_FORGE)

**File:** `bin/camelot.py`

Sub-commands:
```
camelot warp         # Boot into Camelot-OS REPL (default if no sub-command)
camelot configure    # Run auto-configuration engine
camelot install      # First-time setup + PATH registration
camelot status       # Probe all services, show tier matrix
camelot build        # Build portable binary (PyInstaller)
camelot update       # Pull latest CLAUDE.md / cartridges from git
camelot --knight <id> --prompt "<text>"   # single-shot non-interactive
```

Global flags:
```
--knight <id>      Force specific knight
--tier <T0-T3>     Force tier ceiling
--system <file>    Override system prompt file
--no-context       Skip CLAUDE.md injection (raw LLM mode)
--portable         Run in thumbdrive mode (no ~/.camelot writes)
--verbose          Show routing decisions in real-time
```

---

### COMPONENT 2 — Auto-Configuration Engine (SIR_ALEX + SIR_HELIO)

**File:** `bin/camelot_configure.py`

**Detection Pipeline (in order, non-blocking):**

```python
# Step 1: Service discovery
probe_cliproxy()     → { url, models[], latency_ms }   # :8080/health
probe_ollama()       → { url, models[], ram_usage }    # :11434/api/tags
probe_omc_team()     → { url, status }                 # :8090 if running

# Step 2: API key discovery (priority order)
scan_env_vars()      → { ANTHROPIC_API_KEY, GOOGLE_API_KEY, OPENAI_API_KEY }
scan_keyring()       → system credential store
scan_config_files()  → ~/.anthropic/*, ~/.config/google-cloud/*, ~/.openai/*
scan_claude_json()   → ~/.cli-proxy-api/claude.json (OAuth token)

# Step 3: Hardware profiling
detect_ram_gb()      → psutil.virtual_memory().total / 1e9
detect_gpu()         → nvidia-smi / torch / ROCm
detect_portable()    → check if exe path is on removable drive (win32api / lsblk)
detect_os()          → platform.system() + platform.machine()

# Step 4: Tier resolution
resolve_tier():
  T3 (Full Cloud)    → CLIProxy :8080 live OR any cloud API key present
  T2 (Standard)      → any single cloud key without CLIProxy
  T1 (Local-Hybrid)  → Ollama live + at least 1 cloud key
  T0 (Air-Gapped)    → Ollama only, no cloud access

# Step 5: Default knight selection
resolve_default_knight():
  T0 → sir_ghost      (qwen2.5-coder:3b, W=1.00, privacy absolute)
  T1 → sir_forge      (qwen2.5-coder:3b local + cloud fallback)
  T2 → sir_link       (gemini-2.5-flash, fast + cheap)
  T3 → auto via soul_equation (sir_boris for complex, sir_helio for context)

# Step 6: Write config
~/.camelot/config.json  ← persisted, read on every boot
CAMELOT_OS_HOME/        ← repo config (if available)
```

**Portable mode (thumbdrive):** if `--portable` or exe path on removable drive:
- Skip `~/.camelot/` writes entirely
- Store config in `./camelot_config.json` adjacent to binary
- Warn if cloud keys are missing; offer to enter once per session (not persisted)

---

### COMPONENT 3 — Context Injector / ELEPHAS Mode (LADY_MNEMOSYNE)

**File:** `bin/camelot_context.py`

Builds the system prompt injected before every REPL session. Three sources merged in order:

```
[LAYER 1] CLAUDE.md Constitution (Camelot core identity + Titanium Laws)
          Source: CAMELOT_OS_HOME/CLAUDE.md → embedded asset if portable

[LAYER 2] Active Cartridge (domain-specific rules)
          Auto-detection:
            - Scan cwd for package.json → nextjs.yaml
            - Scan cwd for Cargo.toml   → rust-kinetic.yaml
            - Scan cwd for pyproject.toml / setup.py → python-api.yaml
            - Scan cwd for *.sol        → security.yaml
            - Default: reasoning.yaml
          Source: CAMELOT_OS_HOME/03_VAULT/training/configs/cartridges/*.yaml
                  → embedded in portable binary

[LAYER 3] Knight Persona Block
          Selected knight's identity: name, domain, Titanium Laws filter,
          engine weight, routing tier.

[LAYER 4] UKG Anchor (compressed, ≤500 tokens)
          Latest UKG snapshot from toon_ukg_full.json → top 5 anchor nodes
          by recency + weight. Prevents hallucination on Camelot internals.
```

Token budget management:
- Total system prompt target: ≤2,000 tokens
- If CLAUDE.md > 1,500 tokens: compress via QFT (key headings + Titanium Laws only)
- If cartridge > 500 tokens: use frontmatter + first 20 lines only
- UKG anchor: always ≤500 tokens (TOON compressed)

---

### COMPONENT 4 — Installer Scripts (SIR_FORGE + SIR_HELIO)

**4a: pip package (`pip install camelot-os`)**

`pyproject.toml` additions:
```toml
[project]
name = "camelot-os"
version = "1.0.0"

[project.scripts]
camelot        = "bin.camelot:main"
ks             = "bin.knight_session:main"
knight-session = "bin.knight_session:main"

[project.optional-dependencies]
portable = ["pyinstaller>=6.0", "nuitka>=2.0"]
```

**4b: Shell installer (`scripts/install.sh` — Linux/Mac)**
```bash
#!/usr/bin/env bash
# curl -fsSL https://camelot.sh/install | bash
# OR: bash ./scripts/install.sh (local)

CAMELOT_VERSION="1.0.0"

detect_os() { uname -s; }
detect_arch() { uname -m; }

# 1. Check Python ≥ 3.11
# 2. pip install camelot-os (or uv pip install)
# 3. camelot configure (auto-probe)
# 4. Add to PATH: ~/.local/bin or /usr/local/bin
# 5. Shell completion: bash/zsh/fish
# 6. Print: "Camelot is online. SIR_BORIS awaits."
```

**4c: PowerShell installer (`scripts/install.ps1` — Windows)**
```powershell
# iex (iwr https://camelot.sh/install.ps1).Content
# OR: .\scripts\install.ps1 (local)

# 1. Check Python ≥ 3.11 (offer winget install if missing)
# 2. pip install camelot-os OR uv pip install
# 3. camelot configure
# 4. [System.Environment]::SetEnvironmentVariable("PATH", ..., "User")
# 5. PowerShell profile: Set-Alias ai camelot
# 6. Print: "Camelot is online. SIR_BORIS awaits."
```

**4d: Portable installer (`scripts/install_portable.py` — zero deps)**
```python
#!/usr/bin/env python3
# python install_portable.py
# No pip, no curl — just Python 3.11+ standard library
# Downloads camelot binary for detected OS/arch → extracts → configures
```

---

### COMPONENT 5 — Portable Binary Builder (SIR_FORGE)

**File:** `scripts/build_portable.py`

Uses PyInstaller to produce a single executable that runs anywhere:

```python
# Embedded assets (frozen into binary):
EMBEDDED_ASSETS = [
    "CLAUDE.md",                          # Camelot constitution
    "03_VAULT/training/configs/config/omniroute.json",
    "03_VAULT/training/configs/cartridges/*.yaml",  # all cartridges
    ".claude/skills/*.md",                # skill bibles
    "01_KERNEL/EXCALIBUR/roster.yaml",   # knight roster
]

# PyInstaller command:
# pyinstaller --onefile --name camelot
#   --add-data "CLAUDE.md;."
#   --add-data "cartridges;cartridges"
#   --add-data "omniroute.json;."
#   bin/camelot.py

# Output: dist/camelot.exe (Windows) / dist/camelot (Linux/Mac)
# Size target: ≤50MB (no heavy ML deps in binary)
```

Thumbdrive auto-detection logic:
```python
def _is_portable() -> bool:
    exe = Path(sys.executable)
    # Windows: check drive type via win32api
    # Linux: check /proc/mounts for removable
    # Mac: check diskutil info
    # Fallback: check if ~/.camelot/ is writable
    return _on_removable_drive(exe) or not Path.home().joinpath(".camelot").exists()
```

---

### COMPONENT 6 — Shell Integration (SIR_HELIO + SIR_FORGE)

**`camelot shell-setup` writes:**

Bash/Zsh (`~/.bashrc` / `~/.zshrc`):
```bash
# Camelot-OS integration
export CAMELOT_OS_HOME="$HOME/CAMELOT_OS"
alias ai="camelot warp"
alias ks="camelot warp"
source <(camelot completion bash)   # tab completion
# PS1 integration: shows current knight
```

PowerShell (`$PROFILE`):
```powershell
$env:CAMELOT_OS_HOME = "C:\Users\vizio\CAMELOT_OS"
Set-Alias ai camelot
Set-Alias ks camelot
# Register argument completer
Register-ArgumentCompleter -CommandName camelot -ScriptBlock { ... }
```

Fish (`~/.config/fish/config.fish`):
```fish
set -x CAMELOT_OS_HOME ~/CAMELOT_OS
alias ai "camelot warp"
camelot completion fish | source
```

---

### COMPONENT 7 — Security Layer (SIR_SENTINEL)

API key handling (never stored in plaintext in source):
```
Priority order (read):
  1. OS keyring (keyring library)         ← most secure
  2. ~/.camelot/config.json (AES-256 if available, else plain)
  3. Environment variables                ← user-managed
  4. Session-only (prompted, not persisted)

Never:
  - API keys in pyproject.toml or source files
  - API keys in git history
  - API keys logged to PROVENANCE_LEDGER
```

Sandboxed execution:
- All file I/O through ANTIGRAVITY engine (atomic writes + backup)
- Thumbdrive mode: read-only access to host filesystem by default
- `--no-context` flag: skip CLAUDE.md for minimal attack surface in untrusted environments

---

### COMPONENT 8 — WARP UX (SIR_BORIS — "The Feel")

Boot sequence (≤3 seconds):
```
$ camelot
[0.1s] ⚔  CAMELOT-OS v400.1.0  //  WARP_GATE
[0.3s] Scanning environment...
[0.5s] CLIProxy :8080 ✓  |  Ollama :11434 ✓  |  Anthropic ✓  |  Google ✓
[0.7s] Tier: T3 (Full Cloud)  |  Default knight: SIR_BORIS (claude-opus-4-6)
[0.9s] Context: python-api.yaml detected  |  Constitution: injected (1,847 tokens)
[1.0s] OmniRoute: privacy shield active (6 keywords → SIR_GHOST)
[1.2s] ─────────────────────────────────────────────────────
[1.2s]  The Spire is online. SIR_BORIS awaits your command.
[1.2s] ─────────────────────────────────────────────────────
sir_boris|claude-opus-4-6|auto|omni > _
```

Portable/Thumbdrive boot:
```
$ ./camelot.exe
[PORTABLE MODE] Running from removable drive — no writes to host system
[0.2s] ⚔  CAMELOT-OS v400.1.0  //  WARP_GATE (Portable)
[0.4s] No CLIProxy detected. Probing direct APIs...
[0.6s] Anthropic API key found in environment ✓
[0.8s] Tier: T2 (Standard)  |  Knight: SIR_LINK (gemini-2.5-flash)
[1.0s]  The Spire is online (portable). Ready.
sir_link|gemini-2.5-flash|auto|omni > _
```

---

## DEPLOYMENT TOPOLOGY

```
                    INSTALL PATHS
                    ─────────────
   pip install camelot-os          → global Python package
   curl | sh install.sh            → shell one-liner (Linux/Mac)
   iex install.ps1                 → PowerShell one-liner (Windows)
   python install_portable.py      → cross-platform, no curl
   ./camelot.exe (thumbdrive)      → zero-install portable

                    RUNTIME PATHS
                    ─────────────
   camelot warp                    → full Camelot REPL
   camelot --prompt "..."          → single-shot non-interactive
   camelot configure               → (re)run auto-config
   camelot status                  → probe all services
   ks / ai / knight-session        → aliases → camelot warp
```

---

## KNIGHT ASSIGNMENT MATRIX

| Component | Lead Knight | Support Knights | Priority |
|---|---|---|---|
| Entry point + CLI | SIR_BORIS | SIR_FORGE | P0 |
| Auto-config engine | SIR_ALEX | SIR_HELIO | P0 |
| Context injector | LADY_MNEMOSYNE | SIR_BORIS | P0 |
| `ks` system prompt injection | LADY_MNEMOSYNE | SIR_FORGE | P0 |
| install.sh / install.ps1 | SIR_FORGE | SIR_HELIO | P1 |
| PyInstaller portable binary | SIR_FORGE | SIR_SENTINEL | P1 |
| Shell integration + completions | SIR_HELIO | SIR_FORGE | P1 |
| Security / key handling | SIR_SENTINEL | SIR_ALEX | P1 |
| pip package (pyproject.toml) | SIR_FORGE | SIR_BORIS | P2 |
| Tab completion | SIR_HELIO | SIR_FORGE | P2 |

---

## PHASE ROADMAP

| Phase | Deliverable | Knights | Estimated LOC |
|---|---|---|---|
| 0 (Immediate) | `ks` + system prompt injection | LADY_MNEMOSYNE | ~80 |
| 1 (Sprint 1) | `camelot` entry point + `configure` engine | SIR_BORIS + SIR_ALEX | ~400 |
| 2 (Sprint 1) | install.sh + install.ps1 | SIR_FORGE + SIR_HELIO | ~200 |
| 3 (Sprint 2) | PyInstaller portable binary | SIR_FORGE | ~100 + build script |
| 4 (Sprint 2) | pip package + PyPI publish | SIR_FORGE | pyproject.toml edits |
| 5 (Sprint 3) | Shell integration + tab completion | SIR_HELIO | ~150 |
| 6 (Sprint 3) | Security: keyring + AES config | SIR_SENTINEL | ~120 |

---

## RISK REGISTER

| Risk | Severity | Mitigation | Owner |
|---|---|---|---|
| PyInstaller binary > 100MB | Medium | Exclude heavy deps (torch/transformers) | SIR_FORGE |
| CLIProxy not running on target machine | High | Direct API fallback always available | SIR_ALEX |
| API key plaintext in config.json | High | keyring library + warn on plain storage | SIR_SENTINEL |
| Windows Defender flags portable .exe | Medium | Code signing cert / Defender exclusion guide | SIR_SENTINEL |
| CLAUDE.md too large for system prompt | Low | QFT compression; budget 2K tokens | LADY_MNEMOSYNE |
| Ollama not installed on fresh machine | Medium | Graceful T2 fallback; offer install link | SIR_HELIO |

---

*Blueprint forged by SIR_BORIS v3.0 — WARP_GATE v1.0.0 — 2026-05-14*
*Cross-critique: SIR_ALEX (cognitive) · SIR_SENTINEL (security) · SIR_HELIO (cross-platform)*
