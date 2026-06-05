# CAMELOT GLOBAL DEPLOY — TASK LIST
# Codename: WARP_GATE v1.0.0
# Lead: SIR_BORIS | Date: 2026-05-14
# Linked Blueprint: CAMELOT_GLOBAL_DEPLOY.blueprint.md
# Verification: CAMELOT_GLOBAL_DEPLOY.verification.md

---

## PHASE 0 — IMMEDIATE: System Prompt Injection into `ks`
> Unlocks Camelot-aware responses NOW. Zero new files required.
> **Knight:** LADY_MNEMOSYNE + SIR_FORGE
> **Risk Score:** LOW (edit existing file only)

- [ ] **T-00** `bin/knight_session.py` — add `_build_system_prompt()` function
  - Read `CLAUDE.md` from `_REPO` (or embedded fallback string if not found)
  - Read active cartridge: scan `os.getcwd()` for `package.json`/`Cargo.toml`/`pyproject.toml`
    → load matching `.yaml` cartridge from `03_VAULT/training/configs/cartridges/`
  - Read knight persona block from `03_VAULT/Knights/README.md` (first 30 lines for knight)
  - Merge: constitution (≤1500 tok) + cartridge (≤300 tok) + persona (≤200 tok)
  - Return single string

- [ ] **T-01** `_repl()` — inject system prompt into every new session
  - `conversation_history` starts with `{"role": "system", "content": _build_system_prompt()}`
  - System message NOT shown in `/history` output (filter role == "system" from display)
  - On `/clear`: re-inject system prompt (don't lose Camelot context on clear)

- [ ] **T-02** Add `--no-context` flag to `knight_session.py`
  - Skips `_build_system_prompt()` — raw LLM mode
  - Prompt label changes to `raw|omni`

- [ ] **T-03** Add `--system <file>` flag
  - Override: load system prompt from specified file instead of CLAUDE.md
  - Useful for domain-specific Camelot boot (e.g., `--system cartridges/rust-kinetic.yaml`)

- [ ] **T-04** Boot banner update
  - Show: `Context: <cartridge_name> detected | Constitution: injected (<N> tokens)`
  - Show: `System prompt: <N> tokens` in `/status` output

---

## PHASE 1 — SPRINT 1a: `camelot` Entry Point
> The primary global command. Replaces `ks` as the canonical name; `ks` becomes alias.
> **Knight:** SIR_BORIS
> **Risk Score:** LOW (new file)

- [ ] **T-10** Create `bin/camelot.py`
  - `main()` → argparse with sub-commands: `warp`, `configure`, `install`, `status`, `build`, `update`
  - Default (no sub-command) → `warp` (same as `camelot warp`)
  - Pass-through flags: `--knight`, `--tier`, `--system`, `--no-context`, `--portable`, `--verbose`
  - `warp` → calls `knight_session.main()` with args forwarded

- [ ] **T-11** Register `camelot` + `ai` as entry points in `pyproject.toml`
  ```toml
  camelot = "bin.camelot:main"
  ai      = "bin.camelot:main"
  ```

- [ ] **T-12** Create `.venv/Scripts/camelot.cmd` wrapper (same pattern as `ks.cmd`)
  ```batch
  @echo off
  "C:\Users\vizio\CAMELOT_OS\.venv\Scripts\python.exe" -X utf8 "C:\Users\vizio\CAMELOT_OS\bin\camelot.py" %*
  ```

- [ ] **T-13** Create `.venv/Scripts/ai.cmd` wrapper (alias)

---

## PHASE 1 — SPRINT 1b: Auto-Configuration Engine
> **Knight:** SIR_ALEX + SIR_HELIO
> **Risk Score:** LOW (new file; reads only, no destructive ops)

- [ ] **T-14** Create `bin/camelot_configure.py`

- [ ] **T-15** `probe_cliproxy()` — GET `http://127.0.0.1:8080/health`, timeout 1s
  - Returns: `{url, models, latency_ms}` or `None`

- [ ] **T-16** `probe_ollama()` — GET `http://127.0.0.1:11434/api/tags`, timeout 1s
  - Returns: `{url, models}` or `None`

- [ ] **T-17** `scan_api_keys()` — non-blocking key discovery
  - Order: `os.environ` → `~/.anthropic/` → `~/.config/google/` → `~/.cli-proxy-api/claude.json`
  - Returns: `{anthropic, google, openai}` — missing keys are `None`

- [ ] **T-18** `detect_hardware()` — RAM (psutil), GPU (try nvidia-smi subprocess), OS, arch

- [ ] **T-19** `detect_portable()` — check if exe/script is on removable media
  - Windows: `win32api.GetDriveType()` → `DRIVE_REMOVABLE`
  - Linux: parse `/proc/mounts` for sdcard/usb paths
  - Mac: `diskutil info <path>` for `Removable Media: Yes`
  - Fallback: `--portable` flag

- [ ] **T-20** `resolve_tier()` — waterfall logic (see blueprint Component 2)
  - Returns: `T0`, `T1`, `T2`, `T3`

- [ ] **T-21** `resolve_default_knight()` — per-tier knight selection (see blueprint)

- [ ] **T-22** `write_config()` — write `~/.camelot/config.json`
  - In portable mode: write `./camelot_config.json` adjacent to binary
  - Fields: tier, default_knight, cliproxy_url, ollama_url, anthropic_key_present (bool, not value),
    google_key_present (bool), ram_gb, gpu_detected, portable, last_configured (ISO timestamp)

- [ ] **T-23** `run_configure()` — orchestrates T-15→T-22, prints summary table (Rich)
  - Invoked by `camelot configure` OR on first boot if `~/.camelot/config.json` missing

- [ ] **T-24** `camelot.py` auto-configure gate
  - On `camelot warp`: if `~/.camelot/config.json` missing → run `run_configure()` first
  - If config exists and `last_configured` > 7 days ago → show one-line stale warning (non-blocking)

---

## PHASE 1 — SPRINT 1c: Context Injector (ELEPHAS Mode)
> **Knight:** LADY_MNEMOSYNE
> **Risk Score:** LOW (read-only; embedded fallback if files missing)

- [x] **T-25** Create `bin/camelot_context.py` ✅ 2026-06-05

- [x] **T-26** `load_constitution()` — read `CLAUDE.md` ✅
  - Try: `CAMELOT_OS_HOME/CLAUDE.md` (env var)
  - Try: `_REPO/CLAUDE.md` (relative to binary)
  - Try: embedded string (PyInstaller `_MEIPASS` asset)
  - QFT compress if > 1,500 tokens: keep `## TITANIUM LAWS`, `## IDENTITY`, `## RUNIC COMMANDS`,
    `## KNIGHT DISPATCH` sections; strip tables to headers + first/last rows

- [x] **T-27** `detect_cartridge(cwd)` — scan working directory ✅
  - `package.json` → `nextjs.yaml`
  - `Cargo.toml` → `rust-kinetic.yaml`
  - `pyproject.toml` / `setup.py` / `requirements.txt` → `python-api.yaml`
  - `*.sol` → `security.yaml`
  - `Makefile` + `*.c`/`*.cpp` → custom (use `reasoning.yaml` as default)
  - No match → `reasoning.yaml`

- [x] **T-28** `load_cartridge(name)` — read YAML cartridge file ✅
  - Try repo path → Try `_MEIPASS` embedded → Return `""` if not found (non-blocking)
  - Truncate to 300 tokens if larger

- [x] **T-29** `load_knight_persona(knight_id)` — extract persona block from `03_VAULT/Knights/README.md` ✅
  - Static 14-knight dict (sir_boris, sir_alex, sir_sentinel, sir_mnemo, sir_codex, sir_helio,
    sir_link, sir_liberte, sir_forge, sir_ghost, sir_forge_master, sir_gideon, sir_octavian, lady_apis)

- [x] **T-30** `load_ukg_anchor()` — read `toon_ukg_full.json`, extract top 5 nodes by weight ✅
  - Returns TOON-compressed anchor block ≤500 tokens (entity + OCEAN + culture + rune + code_rules)
  - Falls back to nukg_crystals.json top-5 if toon missing
  - Skip silently if neither file found

- [x] **T-31** `build_system_prompt(knight_id, cwd, verbose=False)` — assembles final prompt ✅
  - 4 layers merged with section headers and token budget enforcement
  - verbose: prints per-layer token counts to stderr

- [x] **T-32** Integrate `camelot_context.build_system_prompt()` into `knight_session._build_system_prompt()` ✅
  - Delegates via import; graceful inline fallback if module unavailable
  - Verified: 616 tok total (160+318+32+100) on CAMELOT_OS root

---

## PHASE 2 — SPRINT 2a: Installer Scripts
> **Knight:** SIR_FORGE + SIR_HELIO

- [x] **T-33** Create `scripts/install.sh` (Linux/Mac) ✅ 231 lines — full implementation
- [x] **T-34** Create `scripts/install.ps1` (Windows) ✅ 289 lines — full implementation
- [x] **T-35** Create `scripts/install_portable.py` (zero deps, Python stdlib only) ✅ 354 lines
- [x] **T-36** Create `scripts/build_portable.py` ✅ 180 lines
- [x] **T-37** Create `camelot.spec` (PyInstaller spec template) ✅ exists
- [x] **T-38** `bin/camelot.py` — `_MEIPASS` asset resolution ✅ lines 30-34
- [ ] **T-39** Build + test Windows binary: `python scripts/build_portable.py --platform windows`
  - Output: `dist/camelot.exe` — **DEFERRED** (requires PyInstaller in venv)
- [ ] **T-40** Build + test Linux binary (**DEFERRED** — needs WSL/CI)
- [ ] **T-41** Create `scripts/sign_windows.ps1` (optional) — **DEFERRED** (requires code-signing cert)

---

## PHASE 3 — SPRINT 3: Shell Integration + Tab Completion
> **Knight:** SIR_HELIO

- [x] **T-42** `bin/camelot.py` — `completion` sub-command ✅ 2026-06-05
  - `camelot completion bash` → emits `bin/camelot_completion_bash.sh`
  - `camelot completion zsh` → same bash script (compatible)
  - `camelot completion fish` → fish-native complete calls
  - `camelot completion powershell` → Register-ArgumentCompleter block

- [x] **T-43** Create `bin/camelot_completion_bash.sh` ✅ 2026-06-05
  - Completes: subcommands, `--knight` (14 knights), `--tier` (T0-T3), `--system` (files)
  - Registers for both `camelot` and `ai` aliases

- [x] **T-44** `bin/camelot.py` — `shell-setup` sub-command ✅ exists at line 114 + 202

- [ ] **T-45** PS1/prompt integration (optional `--prompt-integration` flag) — **DEFERRED**

---

## PHASE 3 — SPRINT 3: Security Hardening
> **Knight:** SIR_SENTINEL
> **Risk Score:** MEDIUM

- [ ] **T-46** Integrate `keyring` library into `scan_api_keys()` — **DEFERRED** (optional)
- [x] **T-47** `camelot_configure.py` — never log API key values ✅
  - `scan_api_keys()` returns presence booleans only (`anthropic_key_present: true`)
- [x] **T-48** Thumbdrive paranoia mode ✅ — `detect_portable()` in camelot_configure.py line 213
- [x] **T-49** `.gitignore` additions ✅ — `dist/`, `camelot_config.json` present

---

## PHASE 0 QUICK WINS (Can be done TODAY, ≤2 hours)

| Task | File | LOC | Priority |
|---|---|---|---|
| T-00 `_build_system_prompt()` | `bin/knight_session.py` | ~60 | P0 NOW |
| T-01 inject into `_repl()` | `bin/knight_session.py` | ~10 | P0 NOW |
| T-02 `--no-context` flag | `bin/knight_session.py` | ~5 | P0 NOW |
| T-10 `bin/camelot.py` stub | new file | ~80 | P0 |
| T-12 `camelot.cmd` wrapper | `.venv/Scripts/` | 3 lines | P0 |
| T-23 `camelot configure` basic | `bin/camelot_configure.py` | ~150 | P0 |

---

## DEPENDENCIES MAP

```
T-00 → T-01 → T-02          (system prompt: sequential)
T-14 → T-15,16,17,18,19     (configure: T-14 is parent, rest parallel)
     → T-20 → T-21 → T-22   (tier resolution: sequential)
     → T-23 → T-24           (orchestration: after config ready)
T-25 → T-26,27,28,29,30     (context: T-25 is parent, rest parallel)
     → T-31 → T-32           (merge: sequential)
T-10 → T-11,12,13            (entry: T-10 first)
T-36 → T-37 → T-38 → T-39   (binary: sequential)
```

---

## LEDGER LOG REQUIREMENT

Every completed task must add a PROVENANCE_LEDGER row:
```
| <ID> | **WARP_GATE T-<N>: <description>** | SIR_BORIS | ✅ DEPLOYED | <notes> |
```

---

*Tasks forged by SIR_BORIS v3.0 — cross-checked by SIR_ALEX (cognitive) · SIR_FORGE (build) · SIR_SENTINEL (security)*
*2026-05-14*
