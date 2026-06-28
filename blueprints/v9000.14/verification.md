# Camelot-OS v9000.14-CYBERTRONIA — Verification & Acceptance Criteria

> **Document Version**: 1.0.0
> **Classification**: OPERATIONAL — SIR_SENTINEL reviewed
> **Date**: 2026-06-27
> **Owner**: SIR_BORIS (Architect) · SIR_SENTINEL (Verification Gate)

---

## 1. Verification Philosophy

### 1.1 Core Principles

| Principle | Enforcement |
|---|---|
| **Evidence-Grounded** | Every claim MUST have a reproducible CLI command that produces verifiable output. No aspirational assertions accepted as passing. |
| **Three-Tier Testing** | Unit → Integration → System. No phase gate opens without all three tiers green at that phase's scope. |
| **Adversarial Crucible** | Red-Green-Refactor cycle: write a failing test first, implement to pass, then refactor. ColMAD 3-persona vote required for CRITICAL-risk changes. |
| **HITL Gates** | Destructive operations (git force-push, schema migration, secret rotation) require explicit human approval. Never auto-approve `HUMAN_GATE` tier. |
| **Evidence Classification** | All claims tagged: `confirmed` (backed by live artifact), `planned` (implementation steps named), `aspirational` (narrative only), `rejected` (conflicts with verified state). |

### 1.2 Test Execution Environment

```powershell
# Required environment
$env:CAMELOT_ROOT = "C:\Users\vizio\CAMELOT_OS"
$env:VIRTUAL_ENV  = "$env:CAMELOT_ROOT\.venv"
$env:PATH         = "$env:VIRTUAL_ENV\Scripts;$env:PATH"

# Rust toolchain (1.96+)
rustup default stable

# Verify baseline
python --version   # 3.11+
cargo --version    # 1.96+
node --version     # 20+
```

### 1.3 Evidence Classification Legend

| Tag | Meaning | Gate Eligibility |
|---|---|---|
| ✅ `confirmed` | Backed by live command output, test log, or manifest | May pass gate |
| 🔨 `planned` | Implementation steps exist, not yet executed | Blocks gate until confirmed |
| 💭 `aspirational` | Narrative/design claim, no repo artifact | Cannot pass gate |
| ❌ `rejected` | Conflicts with verified runtime state | Must be resolved or removed |

---

## 2. Phase 1 (IRON) — Foundation Verification Matrix

> **Objective**: Unified control plane, single-class modules, clean imports, no orphan references.

| Task ID | Test Command | Expected Output | Pass/Fail Criteria | Status |
|---|---|---|---|---|
| P1-T01 | `python -c "from control_plane.anya_gate import __version__; print(__version__)"` | `9000.14` | All 13 control_plane modules report `9000.14` | ⬜ |
| P1-T02 | `python -m pytest tests/test_colmad_wiring.py -v` | `PASSED` | CRITICAL intent triggers 3-persona vote; consensus requires 2/3 | ⬜ |
| P1-T03 | `python -m control_plane.knight_agent --test` | All V5.x checks pass | Unified roster count matches `FOUNDRY_COUNCIL`; no duplicate spark IDs | ⬜ |
| P1-T04 | `python -c "import control_plane.triage_score as t; t.get_triage_scorer()"` | No error | Not orphaned — live confidence-scorer with test consumers (test_validation, test_phase_f); disambiguated in docstring from `factory_lane.TriageScore`; imports clean | ⬜ |
| P1-T05 | `python -m control_plane.soul_oversight --test` | `PASSED` | Single coherent `IronGateV2` class; AUTO/PROMPT/HUMAN_GATE tiers verified | ⬜ |
| P1-T06 | `python -c "import re, pathlib; c=pathlib.Path('control_plane/anya_gate.py').read_text(); print(len(re.findall(r'class\s+AnyaCompiler', c)))"` | `1` | Exactly one `AnyaCompiler` in anya_gate.py — no in-file duplicate; documented as distinct from the APEE pipeline and the titan/memory compiler; CLI consumer intact | ⬜ |
| P1-T07 | `python -c "from control_plane.soul_oversight import pre_execute"` | No warnings/errors | Clean import path; no deprecation shims | ⬜ |
| P1-T08 | `python -m control_plane.inspira_metrics --test` | Non-zero metrics dict | `mamba_compression_ratio > 0` when ouroboros engine available | ⬜ |
| P1-T09 | `cargo build -p rtk --release` | Compiles without error | `rtk.dll` produced in `target/release/`; no linker warnings | ⬜ |
| P1-T10 | `python -m squires.colony triage control_plane --auto-approve` | Exit code `0` | Active-source scope (full `.` tree of 40k+ vendored/archive files is impractical): LOW risk 2.0/100, zero CRITICAL findings | ✅ |

### P1 Batch Verification Script

```powershell
# Run all Phase 1 checks in sequence
$results = @()
$checks = @(
    @{id="P1-T01"; cmd='python -c "from control_plane.anya_gate import __version__; print(__version__)"'; expect="9000.14"},
    @{id="P1-T03"; cmd='python -m control_plane.knight_agent --test'; expect="PASSED"},
    @{id="P1-T05"; cmd='python -m control_plane.soul_oversight --test'; expect="PASSED"},
    @{id="P1-T08"; cmd='python -m control_plane.inspira_metrics --test'; expect="Non-zero"},
    @{id="P1-T10"; cmd='python -m squires.colony triage . --auto-approve'; expect="Exit 0"}
)
foreach ($c in $checks) {
    Write-Host "[$($c.id)] Running: $($c.cmd)" -ForegroundColor Cyan
    $output = Invoke-Expression $c.cmd 2>&1
    $results += @{id=$c.id; output=$output; expect=$c.expect}
}
$results | ForEach-Object { Write-Host "[$($_.id)] $($_.expect) → $($_.output)" }
```

---

## 3. Phase 2 (SOUL) — Orchestration Verification Matrix

> **Objective**: Kinetic loop fires 6 stages, Z3 verification real, 11 Obsidian Pillars validated, provenance atomic.

| Task ID | Test Command | Expected Output | Pass/Fail Criteria | Status |
|---|---|---|---|---|
| P2-T01 | `python -m pytest tests/test_kinetic_loop.py -v` | `PASSED` | 6 stages fire in order: `TRIAGE → PLAN → APPROVE → EXECUTE → VERIFY → RECORD` | ⬜ |
| P2-T02 | `python -m pytest tests/test_z3_verification.py -v` | `Z3_BLOCK` for dangerous patch | Real PDDL encoding works; Z3 rejects state-violating mutations | ⬜ |
| P2-T03 | `python -m control_plane.obsidian_pillars --test` | `11/11 pillars validated` | Each pillar has both positive AND negative test case | ⬜ |
| P2-T04 | `python -c "from control_plane.soul_router import SoulRouter; print(SoulRouter().resolve_knight('SIR_HELIOS'))"` | `sir_helio` | All 8 v9000.14 Pantheon aliases resolve to canonical knight_ids (separator/case-insensitive); `route()` remains the intent router | ⬜ |
| P2-T05 | `python -m control_plane.firnflow --test` | V3.x checks pass | Directory-scoped context loads; L1/L2/L3 tiering functional | ⬜ |
| P2-T06 | `python -m pytest tests/test_crucible.py -v` | `PASSED` | Ephemeral execution runs in isolation; temp artifacts cleaned on exit | ⬜ |
| P2-T07 | `python -m pytest tests/test_provenance_sqlite.py -v` | `PASSED` | Atomic commit + rollback verified; `.shadow` file restored on failure | ⬜ |

### P2 Integration Smoke Test

```powershell
# End-to-end kinetic loop with mock intent
python -c @"
from control_plane.anya_gate import AnyaGate
from control_plane.factory_lane import FactoryJob

gate = AnyaGate()
score = gate.triage('Add retry logic to api.py')
print(f'Risk: {score.risk_entropy:.2f}, HITL: {score.hitl_tier}, Lane: {score.lane}')
assert score.hitl_tier in ('AUTO', 'PROMPT', 'HUMAN_GATE'), 'Invalid HITL tier'
print('P2 integration smoke: PASSED')
"@
```

---

## 4. Phase 3 (BRAIN) — Dashboard & Visualization Verification Matrix

> **Objective**: HTMX dashboard renders, MDX schema validates, SSE telemetry flows live.

| Task ID | Test Command | Expected Output | Pass/Fail Criteria | Status |
|---|---|---|---|---|
| P3-T01 | `python -m control_plane.mdx_schema --test` / `pytest tests/test_phase3_brain.py -k mdx_schema` | `ALL PASS` | Valid MDX passes; malformed MDX (bad version/kind/component/risk) rejected | ✅ |
| P3-T02 | `python -m control_plane.bifrost_server --test` (TestClient) | board 200 w/ `hx-get`, `hx-swap`, `hx-trigger` + Luxora Gold `#D4AF37` | Board renders with htmx reactive attributes | ✅ |
| P3-T03 | `python -m control_plane.mdx_renderers --test` / `pytest -k visual_plan` | `ALL PASS` | Intent → valid MDX plan with mermaid diagram + ApprovalButton | ✅ |
| P3-T04 | `python -m control_plane.mdx_renderers --test` / `pytest -k visual_recap` | `ALL PASS` | Post-execution `/visual-recap` valid MDX with outcome/verify results | ✅ |
| P3-T05 | `pytest tests/test_phase3_brain.py -k sse` | `PASSED` | SSE `event: metrics` + `data:` frames parse as valid JSON | ✅ |
| P3-T06 | `pytest tests/test_phase3_brain.py -k approval` | `PASSED` | ApprovalButton registers HITL gate; click resumes kinetic loop into EXECUTE | ✅ |

### P3 Manual Verification Checklist

- [ ] Start Bifrost server: `python -m control_plane.bifrost_server`
- [ ] Open `http://127.0.0.1:8080/bifrost` in browser
- [ ] Verify knight cards render with status indicators
- [ ] Verify SSE telemetry updates without page refresh
- [ ] Verify approval button pauses and resumes a mock job
- [ ] Verify MDX plan renders as formatted mermaid diagram
- [ ] Verify dark mode / Luxora Gold (`#D4AF37`) theming applied

---

## 5. Phase 4 (MESH) — Distributed Communication Verification Matrix

> **Objective**: tsnet mesh established, post-quantum crypto verified, zero-copy IPC measured.

| Task ID | Test Command | Expected Output | Pass/Fail Criteria | Status |
|---|---|---|---|---|
| P4-T01 | `cd 01_KERNEL/mesh/node_c && TS_AUTHKEY=... go test -v -run TestTwoNodeMesh` | `PASS` (or SKIP w/o key) | tsnet node scaffolded — **compiles clean** (`go build`/`go vet` exit 0); test runs + skips w/o key. Live 2-node mesh needs a tailnet auth key | 🔨 scaffolded |
| P4-T02 | `cargo test -p camelot-pqcrypto --release` | `3 passed` | ML-KEM-768 handshake round-trips (shared secrets match); wrong-key diverges; ML-DSA-65 sign/verify + tamper-detect | ✅ |
| P4-T03 | `python -m control_plane.empire_drone --test` / `pytest tests/test_phase45_edge.py -k drone` | `ALL PASS` | New drone auto-registers on join; idempotent re-announce; stale drones reaped | ✅ |
| P4-T04 | `cargo audit` / `cargo test -p camelot-pqcrypto` | `exit 0` / `3 passed` | **Migrated** pqcrypto→RustCrypto ml-kem 0.3.2 + ml-dsa 0.1.1; pqcrypto/pqclean removed from lockfile; `cargo audit` clean (172 deps, 0 advisories); round-trip tests pass | ✅ |
| P4-T05 | `bash scripts/wsl_verify.sh` (memfd section) | zero-copy across fork + latency | **Verified on WSL2**: `memfd_create` page visible across `fork`; ~0.126µs/page round-trip (target <10µs) | ✅ (WSL2) |

### P4 Platform Notes

> [!WARNING]
> P4-T01 (tsnet), P4-T05 (memfd_create), and P5-T02 (MicroVM) require **Linux or WSL2**.
> On native Windows they are marked `planned`/`blocked` with a WSL2 execution path. Do not mark as `rejected`.

All four environment-gated tasks (P4-T01, P4-T04, P4-T05, P5-T02) plus the P5-T01
`wasmtime` run-check are driven by **`scripts/wsl_verify.sh`**, which preflights the
toolchain, exercises the real Linux primitives (e.g. `memfd_create` zero-copy across
`fork`), and reports PASS/FAIL/SKIP per task:

```powershell
# From Windows, launch the driver inside WSL2 Ubuntu:
wsl -d Ubuntu -- bash -c "cd /mnt/c/Users/vizio/CAMELOT_OS && bash scripts/wsl_verify.sh"

# With a Tailscale auth key to attempt the live tsnet mesh (P4-T01):
wsl -d Ubuntu -- bash -c "cd /mnt/c/Users/vizio/CAMELOT_OS && TS_AUTHKEY=tskey-... bash scripts/wsl_verify.sh"
```

---

## 6. Phase 5 (EDGE) — Edge Runtime Verification Matrix

> **Objective**: WASM pipeline produces artifact, MicroVM boots, Swarm storage pins, memory budget holds.

| Task ID | Test Command | Expected Output | Pass/Fail Criteria | Status |
|---|---|---|---|---|
| P5-T01 | `cargo build --target wasm32-wasip1 -p camelot-edge --release` | `camelot-edge.wasm` produced | Valid WASM binary built (`\0asm` MVP magic, 65KB); `wasmtime run` pending a wasmtime install on this host | ✅ build |
| P5-T02 | `python scripts/microvm_boot.py --self-test` (machinery) / `--health-check` (real boot) | `ALL PASS` / health 200 | Launcher **scaffolded + self-test verified** (mock VM, cross-platform); real boot needs WSL2 `/dev/kvm` + hypervisor + pill image (exit 3 → SKIP until present) | 🔨 scaffolded |
| P5-T03 | `python -m control_plane.swarm_pin --test` | `ALL PASS` | BZZ content address round-trips; idempotent pin; tamper-evident fetch | ✅ |
| P5-T04 | `python -m control_plane.scarcity_protocol --test` | `ALL PASS` | 3GiB main + 1GiB ZRAM envelope enforced; breach refused; reclaim frees budget (real `MADV_DONTNEED` on Linux) | ✅ |
| P5-T05 | `python -m control_plane.voice_ingress --test` / `pytest -k voice` | `ALL PASS` | Wake-word + filler stripped; command → kinetic intent dispatched; chatter ignored | ✅ |
| P5-T06 | `python -m control_plane.preview_drone --test` | `ALL PASS` | Local preview deploy + health-check gates Swarm pin; unhealthy artifact blocked | ✅ |

### P5 Platform Notes

> [!IMPORTANT]
> Phase 5 tests require specialized infrastructure:
> - **P5-T01**: Requires `rustup target add wasm32-wasip1` and `wasmtime` installed
> - **P5-T02**: Requires WSL2 + KVM for MicroVM (Firecracker/Cloud Hypervisor)
> - **P5-T03**: Requires Swarm node or mock endpoint
> - **P5-T04**: Requires Linux for `MADV_DONTNEED` / ZRAM; Windows uses simulated budget

```powershell
# Pre-flight: install WASM target
rustup target add wasm32-wasip1

# Pre-flight: verify wasmtime
wasmtime --version

# Pre-flight: verify WSL2 + KVM (for MicroVM)
wsl -d Ubuntu -- bash -c "ls /dev/kvm && echo 'KVM available' || echo 'KVM not available'"
```

---

## 7. Regression Test Battery

All existing test suites MUST remain green throughout the upgrade. Run before and after each phase.

### 7.1 Python Test Suite

```powershell
# Full Python test suite
.venv\Scripts\python.exe -m pytest -v --tb=short 2>&1 | Tee-Object -FilePath regression_python.log
```

### 7.2 Rust Test Suite

```powershell
# All Rust workspace crates
cargo test --workspace 2>&1 | Tee-Object -FilePath regression_rust.log

# Static analysis
cargo check 2>&1  # All 8 workspace crates
cargo clippy --workspace -- -D warnings 2>&1
```

### 7.3 Node.js Test Suite

```powershell
npm test 2>&1 | Tee-Object -FilePath regression_node.log
```

### 7.4 Control Plane Module Self-Tests

```powershell
$modules = @(
    "control_plane.knight_agent",
    "control_plane.factory_lane",
    "control_plane.colmad",
    "control_plane.firnflow",
    "control_plane.cartridge_manager",
    "control_plane.inspira_metrics",
    "control_plane.anya_gate",
    "control_plane.soul_oversight"
)
foreach ($mod in $modules) {
    Write-Host "`n=== Testing $mod ===" -ForegroundColor Yellow
    python -m $mod --test 2>&1
    if ($LASTEXITCODE -ne 0) { Write-Host "FAIL: $mod" -ForegroundColor Red }
    else { Write-Host "PASS: $mod" -ForegroundColor Green }
}
```

### 7.5 Squire Colony Triage

```powershell
# Non-interactive full triage
python -m squires.colony triage . --auto-approve 2>&1 | Tee-Object -FilePath regression_colony.log
```

---

## 8. System-Level Acceptance Tests

### 8.1 Full Boot Sequence

```powershell
# Full boot must complete all 6 phases without error
python bin/awaken.py 2>&1 | Tee-Object -FilePath boot_log.txt

# Verify boot phases
Select-String -Path boot_log.txt -Pattern "Phase \d" | ForEach-Object { $_.Line }
```

- [ ] Boot completes 6 phases without error
- [ ] All knights register in roster
- [ ] Port probes return expected services

### 8.2 Version Consistency

```powershell
# All version surfaces must report v9000.14
$surfaces = @(
    'python -c "from control_plane.anya_gate import __version__; print(__version__)"',
    'python -c "from control_plane.soul_oversight import __version__; print(__version__)"',
    'python -c "from control_plane.knight_agent import __version__; print(__version__)"',
    'python -c "from control_plane.factory_lane import __version__; print(__version__)"',
    'python -c "from control_plane.colmad import __version__; print(__version__)"',
    'python -c "from control_plane.firnflow import __version__; print(__version__)"'
)
foreach ($s in $surfaces) {
    $ver = Invoke-Expression $s 2>&1
    if ($ver -ne "9000.14") {
        Write-Host "VERSION MISMATCH: $s → $ver" -ForegroundColor Red
    } else {
        Write-Host "OK: $ver" -ForegroundColor Green
    }
}
```

- [ ] All control_plane modules report `9000.14`
- [ ] `dist/camelot.exe --version` reports `9000.14`
- [ ] `//STATUS` displays `v9000.14-CYBERTRONIA`

### 8.3 Provenance Integrity

```powershell
# Verify provenance ledger has entries for this upgrade
Select-String -Path PROVENANCE_LEDGER.md -Pattern "9000.14" | Measure-Object | Select-Object Count
```

- [ ] `PROVENANCE_LEDGER.md` contains entries tagged with `9000.14`
- [ ] Entries are append-only (no prior entries modified)
- [ ] Each phase gate records a provenance entry

### 8.4 Security Sweep

```powershell
# Ghost squire — no secrets in repo
python -m squires.colony ghost . 2>&1 | Tee-Object -FilePath security_sweep.log

# Verify clean
Select-String -Path security_sweep.log -Pattern "SECRET|CRITICAL" | Measure-Object | Select-Object Count
```

- [ ] No secrets detected by GHOST squire
- [ ] No CRITICAL findings in colony triage
- [ ] API keys remain boolean-only in `config.json`

### 8.5 Portable Binary

```powershell
# Portable binary version check
dist\camelot.exe --version 2>&1

# Basic REPL smoke test
echo "//STATUS" | dist\camelot.exe --batch 2>&1
```

- [ ] `dist/camelot.exe` launches without error
- [ ] Reports `v9000.14`
- [ ] `//STATUS` command executes successfully

---

## 9. Evidence Artifact Requirements

Each phase MUST produce the following evidence artifacts before its gate can open:

### 9.1 Per-Phase Evidence Files

| Phase | Evidence Path | Contents |
|---|---|---|
| IRON (P1) | `03_VAULT/runtime_state/nano_swarm_evidence/v9000_phase_1_evidence.json` | P1-T01 through P1-T10 results, timestamps, command outputs |
| SOUL (P2) | `03_VAULT/runtime_state/nano_swarm_evidence/v9000_phase_2_evidence.json` | P2-T01 through P2-T07 results, Z3 proof artifacts |
| BRAIN (P3) | `03_VAULT/runtime_state/nano_swarm_evidence/v9000_phase_3_evidence.json` | P3-T01 through P3-T06 results, screenshot of Bifrost board |
| MESH (P4) | `03_VAULT/runtime_state/nano_swarm_evidence/v9000_phase_4_evidence.json` | P4-T01 through P4-T05 results, Kyber handshake log |
| EDGE (P5) | `03_VAULT/runtime_state/nano_swarm_evidence/v9000_phase_5_evidence.json` | P5-T01 through P5-T06 results, WASM artifact hash |

### 9.2 Evidence JSON Schema

```json
{
  "phase": "P1-IRON",
  "version": "9000.14",
  "timestamp": "2026-06-27T00:00:00Z",
  "tests": [
    {
      "id": "P1-T01",
      "command": "python -c \"from control_plane.anya_gate import __version__; print(__version__)\"",
      "expected": "9000.14",
      "actual": "",
      "status": "pending",
      "evidence_class": "planned",
      "executor": "SIR_FORGE",
      "duration_ms": 0
    }
  ],
  "gate_recommendation": "BLOCK|PASS",
  "reviewer": "SIR_SENTINEL"
}
```

### 9.3 Supporting Artifacts

- [ ] `colony_report.md` updated after each phase's colony triage
- [ ] `PROVENANCE_LEDGER.md` entries for each file created/modified
- [ ] Regression test logs archived: `regression_python.log`, `regression_rust.log`, `regression_node.log`
- [ ] Boot log archived: `boot_log.txt`
- [ ] Security sweep log archived: `security_sweep.log`

---

## 10. Acceptance Gates

### Gate Summary Table

| Gate | Phase | Criteria | Blocking? | Status |
|---|---|---|---|---|
| **Gate 1 — IRON** | P1 | All P1-T01…T10 pass; no CRITICAL colony findings; version `9000.14` on all modules | ✅ Yes | ⬜ PENDING |
| **Gate 2 — SOUL** | P2 | Kinetic loop end-to-end (6 stages); Z3 real verification blocks dangerous patch; 11/11 Obsidian Pillars validated; provenance atomic | ✅ Yes | ⬜ PENDING |
| **Gate 3 — BRAIN** | P3 | HTMX board renders at `/bifrost`; MDX schema validates; SSE telemetry flows; approval button resumes loop | ✅ Yes | ⬜ PENDING |
| **Gate 4 — MESH** | P4 | tsnet 2-node mesh + ML-KEM-768 mTLS working; `cargo audit` clean; IPC latency < 10µs (Linux/WSL2 — may defer to `planned` on native Windows) | ⚠️ Partial | ⬜ PENDING |
| **Gate 5 — EDGE** | P5 | WASM pipeline produces artifact; MicroVM boot < 12ms; Swarm pin round-trips (blocked on WSL2+KVM for MicroVM — may defer to `planned`) | ⚠️ Partial | ⬜ PENDING |
| **FINAL** | ALL | `//STATUS` returns `v9000.14-CYBERTRONIA` across all surfaces; all evidence JSONs committed; no `rejected` claims outstanding | ✅ Yes | ⬜ PENDING |

### Gate Escalation Protocol

```
IF gate fails:
  1. SIR_DEBUG runs //HEAL on failing test
  2. Up to 3 PIV iterations (Plan → Implement → Validate)
  3. If still failing after 3 iterations → HUMAN_GATE escalation
  4. Failing evidence logged with class "rejected" and remediation plan

IF gate passes:
  1. Evidence JSON updated with "confirmed" class
  2. PROVENANCE_LEDGER.md entry appended
  3. SIR_SENTINEL signs off
  4. Next phase unlocked
```

### Final Acceptance Command

```powershell
# This command validates the complete upgrade
python -m control_plane.runic_router --rune STATUS --task "" 2>&1

# Expected output must contain:
# - Version: v9000.14-CYBERTRONIA
# - All knights: ONLINE or IDLE
# - Colony: HEALTHY
# - Evidence: 5/5 phases confirmed
```

---

## Appendix A: Quick-Reference Test Commands

```powershell
# === ONE-LINER FULL VERIFICATION ===
# Run this after all phases complete to verify the entire upgrade

$ErrorActionPreference = "Continue"

Write-Host "=== CAMELOT-OS v9000.14 FULL VERIFICATION ===" -ForegroundColor Magenta

# 1. Python tests
Write-Host "`n[1/6] Python tests..." -ForegroundColor Cyan
.venv\Scripts\python.exe -m pytest --tb=line -q

# 2. Rust tests
Write-Host "`n[2/6] Rust tests..." -ForegroundColor Cyan
cargo test --workspace --quiet

# 3. Control plane self-tests
Write-Host "`n[3/6] Control plane..." -ForegroundColor Cyan
@("knight_agent","factory_lane","colmad","firnflow","cartridge_manager","inspira_metrics") |
    ForEach-Object { python -m "control_plane.$_" --test 2>&1 | Select-Object -Last 1 }

# 4. Colony triage
Write-Host "`n[4/6] Colony triage..." -ForegroundColor Cyan
python -m squires.colony triage . --auto-approve 2>&1 | Select-Object -Last 3

# 5. Security sweep
Write-Host "`n[5/6] Ghost sweep..." -ForegroundColor Cyan
python -m squires.colony ghost . 2>&1 | Select-Object -Last 3

# 6. Version check
Write-Host "`n[6/6] Version check..." -ForegroundColor Cyan
python -c "from control_plane.anya_gate import __version__; print(f'v{__version__}')"

Write-Host "`n=== VERIFICATION COMPLETE ===" -ForegroundColor Magenta
```

---

> **Sign-Off Chain**: SIR_FORGE (executor) → SIR_SENTINEL (verifier) → SIR_BORIS (architect) → KING_ARTHUR (final authority)
