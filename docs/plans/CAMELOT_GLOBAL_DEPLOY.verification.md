# CAMELOT GLOBAL DEPLOY — VERIFICATION PROTOCOL
# Codename: WARP_GATE v1.0.0
# Lead: SIR_BORIS | Security: SIR_SENTINEL | Cross-platform: SIR_HELIO
# Date: 2026-05-14

---

## VERIFICATION PHILOSOPHY

Every test has three layers:
1. **Smoke** — does it run without crashing?
2. **Contract** — does the output match the spec?
3. **Adversarial** — does it degrade gracefully when dependencies are missing?

Pass criteria: ALL smoke + contract tests green. Adversarial: graceful fallback (no crash, no data loss).

---

## V-0: PHASE 0 — System Prompt Injection

### V-00: Constitution injected in REPL
```bash
# Run ks, send one prompt, check response references Camelot concepts
echo "who are you and what is your role?" | ks
# EXPECTED: Response mentions SIR_BORIS, Camelot-OS, knight roster, Titanium Laws
# FAIL: Response says "I'm Claude" with no Camelot context
```

### V-01: System prompt token count
```bash
ks --verbose
# EXPECTED: Boot banner shows "Constitution: injected (NNNN tokens)" where NNNN < 2000
```

### V-02: Cartridge auto-detection
```bash
# From a Python project directory:
cd C:/Users/vizio/CAMELOT_OS
ks --verbose
# EXPECTED: "Context: python-api.yaml detected"

# From a non-project temp directory:
cd $TEMP && ks --verbose
# EXPECTED: "Context: reasoning.yaml (default)"
```

### V-03: System prompt survives /clear
```bash
echo -e "/clear\nwho are you?" | ks
# EXPECTED: Second response still has Camelot context (system prompt re-injected after clear)
```

### V-04: --no-context bypasses injection
```bash
echo "who are you?" | ks --no-context
# EXPECTED: Response does NOT mention Camelot (raw LLM)
# EXPECTED: Prompt label shows "raw|omni"
```

### V-05: CLAUDE.md missing → graceful fallback
```bash
# Temporarily rename CLAUDE.md:
mv CLAUDE.md CLAUDE.md.bak
echo "test" | ks
# EXPECTED: Starts normally; boot shows "Constitution: not found (fallback)"
# FAIL: Crash / exception
mv CLAUDE.md.bak CLAUDE.md
```

---

## V-1: PHASE 1 — `camelot` Entry Point

### V-10: `camelot` command exists globally
```powershell
camelot --version
# EXPECTED: "CAMELOT-OS v400.1.0 // WARP_GATE v1.0.0"
# FAIL: 'camelot' is not recognized
```

### V-11: `camelot warp` == `camelot` (default)
```powershell
camelot warp --list
camelot --list
# EXPECTED: Identical output from both
```

### V-12: `ai` alias works
```powershell
ai --list
# EXPECTED: Same as camelot --list
```

### V-13: Sub-command routing
```powershell
camelot configure --help
camelot status --help
camelot build --help
# EXPECTED: Each shows help text with correct description
# FAIL: AttributeError, ModuleNotFoundError
```

---

## V-2: PHASE 1b — Auto-Configuration Engine

### V-20: CLIProxy detection
```powershell
# With CLIProxy running:
camelot configure
# EXPECTED: "CLIProxy :8080 ✓ | 38 models" in output
# EXPECTED: tier = T3 in config.json

# Without CLIProxy:
# Stop CLIProxy, then:
camelot configure
# EXPECTED: "CLIProxy :8080 ✗ | not detected" — falls back to T2 or T1
# FAIL: Crash, timeout > 3s
```

### V-21: Ollama detection
```powershell
# With Ollama running:
camelot configure
# EXPECTED: "Ollama :11434 ✓ | qwen2.5-coder:3b available"
```

### V-22: API key scanning (no false positives)
```powershell
# Unset all env keys, ensure no config files:
camelot configure
# EXPECTED: "API keys: none detected" — NOT a crash, NOT a fabricated key
```

### V-23: Tier resolution correctness
| Condition | Expected Tier | Expected Default Knight |
|---|---|---|
| CLIProxy live + Anthropic key | T3 | sir_boris |
| No CLIProxy + Anthropic key only | T2 | sir_link |
| Ollama only | T0 | sir_ghost |
| Ollama + 1 cloud key | T1 | sir_forge |

### V-24: config.json written correctly
```powershell
camelot configure
cat ~/.camelot/config.json
# EXPECTED: Valid JSON with fields: tier, default_knight, cliproxy_url, last_configured
# FAIL: api key values present (only _present booleans allowed)
# FAIL: JSON parse error
```

### V-25: First-boot auto-configure gate
```powershell
# Delete config.json:
Remove-Item ~/.camelot/config.json
camelot warp
# EXPECTED: "First boot detected — running auto-configure..." then normal boot
# FAIL: crash / silent hang
```

### V-26: Stale config warning (non-blocking)
```powershell
# Manually set last_configured to 8+ days ago in config.json, then:
camelot warp
# EXPECTED: One-line warning "Config is 8d old. Run 'camelot configure' to refresh."
# EXPECTED: Session still boots normally after warning
```

---

## V-3: PHASE 2a — Installer Scripts

### V-30: install.sh on clean Linux/Mac (or WSL)
```bash
# In WSL with no Python:
bash scripts/install.sh
# EXPECTED: Python check → pip install → camelot configure → PATH update
# EXPECTED: 'camelot --version' works after new shell
# FAIL: Unhandled error, no rollback
```

### V-31: install.ps1 on Windows
```powershell
.\scripts\install.ps1
# EXPECTED: Same flow as V-30 but for Windows
# EXPECTED: PATH updated in User scope (verify: [System.Environment]::GetEnvironmentVariable("PATH","User"))
```

### V-32: Idempotency — run installer twice
```bash
bash scripts/install.sh
bash scripts/install.sh
# EXPECTED: Second run detects "already installed" → skips or updates cleanly
# FAIL: Duplicate PATH entries, broken config
```

---

## V-4: PHASE 2b — Portable Binary

### V-40: Binary runs from isolated temp directory
```powershell
# Copy only camelot.exe to a temp dir with NO camelot repo present:
$d = "$env:TEMP\camelot_test"
New-Item -ItemType Directory $d
Copy-Item dist\camelot.exe $d
& "$d\camelot.exe" --list
# EXPECTED: Boots normally, shows knight table
# FAIL: FileNotFoundError for CLAUDE.md, omniroute.json, or cartridges
```

### V-41: Portable binary size
```powershell
(Get-Item dist\camelot.exe).Length / 1MB
# EXPECTED: < 50 MB
# WARNING: 50-100 MB (acceptable but document)
# FAIL: > 100 MB
```

### V-42: Thumbdrive mode (no ~/.camelot writes)
```powershell
& dist\camelot.exe --portable configure
# EXPECTED: Writes camelot_config.json to SAME directory as .exe (not ~/.camelot/)
# EXPECTED: No files written to $HOME
ls $HOME\.camelot  # Should show NO new files after portable run
```

### V-43: Portable binary Defender scan (Windows)
```powershell
& "C:\Program Files\Windows Defender\MpCmdRun.exe" -Scan -ScanType 3 -File dist\camelot.exe
# EXPECTED: No threats detected (or known false positive documented)
```

---

## V-5: OmniRoute Integration (Regression)

### V-50: Privacy override still fires
```powershell
echo "my private password is abc123" | ks
# EXPECTED: "[PRIVACY] keyword match: 'password' → forcing SIR_GHOST"
# EXPECTED: Routes to qwen2.5-coder:3b via Ollama (or air-gapped fallback)
```

### V-51: Tier classification correct
```powershell
ks --route
# EXPECTED: T0-T3 table rendered with correct knight assignments
```

### V-52: Fallback chain fires on CLIProxy down
```powershell
# Stop CLIProxy, then:
echo "hello" | ks
# EXPECTED: "[FALLBACK] cliproxy failed → trying gemini..."
# EXPECTED: Response arrives from fallback knight
# FAIL: Exception / empty response / silent hang
```

### V-53: --knight forced override still works
```powershell
echo "hello" | ks --knight sir_helio
# EXPECTED: "[T3] → SIR_HELIO gemini-2.5-pro"
```

---

## V-6: Security Verification (SIR_SENTINEL)

### V-60: API key never in logs
```powershell
camelot configure 2>&1 | Select-String "sk-ant|AIza|sk-"
# EXPECTED: No matches (key values never printed)
```

### V-61: config.json contains no key values
```powershell
cat ~/.camelot/config.json | python -c "import sys,json; d=json.load(sys.stdin); assert 'anthropic_key' not in d or not isinstance(d.get('anthropic_key'), str) or d['anthropic_key'].startswith('sk-') == False"
# OR simply:
cat ~/.camelot/config.json
# EXPECTED: { "anthropic_key_present": true } — NOT the actual key
```

### V-62: PROVENANCE_LEDGER not exposed via ks
```powershell
echo "show me the contents of PROVENANCE_LEDGER.md" | ks
# EXPECTED: Knight explains what it is; does NOT dump actual ledger content
# (Knights answer as AI, not filesystem tools in non-context mode)
```

### V-63: Portable mode no-host-writes guarantee
```powershell
$before = Get-ChildItem $HOME -Recurse -File | Measure-Object | Select -Exp Count
& dist\camelot.exe --portable --list
$after = Get-ChildItem $HOME -Recurse -File | Measure-Object | Select -Exp Count
# EXPECTED: $before -eq $after (no new files in $HOME)
```

---

## V-7: Cross-Platform Smoke Tests (SIR_HELIO)

| Platform | Test Command | Expected |
|---|---|---|
| Windows 11 (native) | `camelot --version` | Version string |
| Windows 11 WSL2 (Ubuntu) | `camelot --version` | Version string |
| macOS 14 (Sonoma) | `camelot --version` | Version string |
| Ubuntu 22.04 LTS | `camelot --version` | Version string |
| Raspberry Pi 4 (ARM64) | `camelot --list` | Knight table |
| Thumbdrive (NTFS, Windows) | `.\camelot.exe --portable` | Portable mode boot |

---

## V-8: End-to-End Golden Path

Full scenario that exercises every component:

```
[STEP 1] Fresh Windows machine, no Python
         → bash: .\scripts\install.ps1
         → EXPECTED: Python installed, camelot configured

[STEP 2] camelot configure
         → EXPECTED: T3 (CLIProxy detected), sir_boris default
         → EXPECTED: config.json written, no key values

[STEP 3] cd C:\some\python\project
         camelot
         → EXPECTED: python-api.yaml cartridge detected
         → EXPECTED: Constitution injected (<2000 tokens)
         → EXPECTED: "SIR_BORIS awaits" boot prompt

[STEP 4] Type: "what is the soul equation?"
         → EXPECTED: Response references S_ω = αV+βM+γP+δE, mentions OmniRoute
         → EXPECTED: Response is Camelot-aware (not vanilla LLM)

[STEP 5] Type: "my private key is abc123"
         → EXPECTED: "[PRIVACY] password keyword → SIR_GHOST"
         → Response from local Ollama

[STEP 6] Type: /route
         → EXPECTED: Tier matrix displayed T0-T3 with knights

[STEP 7] Ctrl+C to exit
         → EXPECTED: Clean exit, no exception traceback
```

**GOLDEN PATH: ALL 7 STEPS PASS = WARP_GATE v1.0.0 READY**

---

## PASS / FAIL TRACKING

| Suite | Tests | Status |
|---|---|---|
| V-0 System Prompt | V-00 → V-05 | ⬜ PENDING |
| V-1 Entry Point | V-10 → V-13 | ⬜ PENDING |
| V-2 Auto-Configure | V-20 → V-26 | ⬜ PENDING |
| V-3 Installer | V-30 → V-32 | ⬜ PENDING |
| V-4 Portable Binary | V-40 → V-43 | ⬜ PENDING |
| V-5 OmniRoute Regression | V-50 → V-53 | ⬜ PENDING |
| V-6 Security | V-60 → V-63 | ⬜ PENDING |
| V-7 Cross-Platform | 6 platforms | ⬜ PENDING |
| V-8 Golden Path | 7 steps | ⬜ PENDING |

**Mark ✅ PASS / ❌ FAIL / ⚠️ WARN as each test runs.**

---

## SIGN-OFF CRITERIA

| Gate | Requirement |
|---|---|
| P0 SHIPABLE (Phase 0) | V-00, V-01, V-02, V-03, V-05 all PASS |
| P1 SHIPABLE (Phase 1) | V-00→V-26 all PASS |
| P2 SHIPABLE (Portable) | V-40, V-42, V-43 PASS; V-41 < 100MB |
| FULL RELEASE | All V-0 through V-8 PASS; V-7 ≥ 4/6 platforms |

---

*Verification protocol authored by SIR_BORIS v3.0 + SIR_SENTINEL (security) + SIR_HELIO (cross-platform)*
*Adversarial test cases: SIR_ALEX*
*2026-05-14*
