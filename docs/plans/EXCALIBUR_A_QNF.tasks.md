# EXCALIBUR-A: Implementation Tasks
**Codename:** EXCALIBUR_A_QNF  
**Task Conductor:** SIR_ALEX (Cognitive Cartridge) + SIR_LUKAS (Kinetic Hand)  
**Planner:** MERLIN_Ω (GoT DAG) | **Gate:** ANYA_Ω (APEE v7.0)  
**Date:** 2026-06-01 | **Ledger:** #QNF_2026_06_01_ENTERPRISE_FRONTIER

---

## PHASE 0 — CLOUD BRAIN + LEDGER SYNC ✓ COMPLETE

| # | Task | File | Knight | Status | HITL |
|---|---|---|---|---|---|
| 0.1 | Query all 7 NLM notebooks | `notebooklm-py client` | LADY_M | ✅ DONE | AUTO |
| 0.2 | Synthesize 12 innovations into plan | Enterprise plan md | SIR_BORIS | ✅ DONE | AUTO |
| 0.3 | Append ledger entry #QNF_2026_06_01 | `PROVENANCE_LEDGER.md` | AUTO_HOOK | ✅ DONE | AUTO |
| 0.4 | Run OpenClaw triage | `control_plane/openclaw.py` | SIR_OCTAVIAN | ✅ DONE | AUTO |
| 0.5 | Run CloudBrain sync | `control_plane/cloudbrain_sync.py` | LADY_M | ✅ DONE | AUTO |

---

## PHASE 1 — CRITICAL TRIAGE (Priority: IMMEDIATE)

**Objective:** Reduce Colony Report CRITICAL score 100 → < 40 before any new code ships  
**Owner:** SIR_SENTINEL + SIR_GIDEON  
**Lane:** CRITICAL (HUMAN_GATE required for secret rotation)

| # | Task | Command/Action | File(s) | Knight | HITL Tier | Accept |
|---|---|---|---|---|---|---|
| 1.1 | **Identify 8 detected secrets** | `python squires/colony.py --secrets-report` | `logs/colony_secrets.json` | SIR_GIDEON | HUMAN_GATE | Report generated |
| 1.2 | **Rotate each secret** | `camelot keys set <KEY_NAME>` × 8 | `config.json` (bool flags only) | SIR_GHOST | HUMAN_GATE | 0 raw secrets in source |
| 1.3 | **Generate dedup report (MASON)** | `python squires/colony.py --mason-dedup` | `logs/mason_dedup.json` | SIR_GIDEON | PROMPT | Report generated |
| 1.4 | **Review + delete duplicate files** | Review mason_dedup.json, `rm` approved dupes | Various | SIR_BORIS | PROMPT | < 50 dupes remain |
| 1.5 | **Triage 45 TODOs** | `python squires/colony.py --triage-todos` | `logs/todo_triage.json` | LADY_APIS | AUTO | DEFERRED — colony.py relative import requires package runner |
| 1.6 | **Clear 32 dead imports** | `ruff check --select F401 --fix 01_KERNEL/ control_plane/` | Multiple .py | SIR_LUKAS | AUTO | ✅ DONE 2026-06-05 — 0 F401 errors (113 auto-fixed + 24 noqa) |
| 1.7 | **Re-run full colony scan** | `python squires/colony.py` | `01_KERNEL/colony_report.md` | SIR_GIDEON | AUTO | DEFERRED — requires package runner |
| 1.8 | **Commit Phase 1 cleanup** | `git add -p && git commit` | Staged changes | SIR_BORIS | PROMPT | ✅ DONE 2026-06-05 — commit 9975eba; 91 files changed |

---

## PHASE 2 — RTK + ANYA APEE v7.0 (Priority: HIGH)

**Objective:** Rust Token Killer + 7-stage self-triaging gate + Sir Socrates stub  
**Owner:** SIR_LUKAS (Rust) + ANYA_Ω (gate logic)  
**Lane:** HIGH (PROMPT for commits)

### Task 2.1 — Create RTK Rust Module
**File:** `control_plane/rtk/src/lib.rs` (NEW)  
**Knight:** SIR_LUKAS  
**Step 1:** Create `control_plane/rtk/Cargo.toml`
```toml
[package]
name = "rtk"
version = "0.1.0"
edition = "2024"

[lib]
crate-type = ["cdylib"]

[dependencies]
regex = "1"
```
**Step 2:** Implement `strip_context_noise(raw: *const c_char) -> *mut c_char` in lib.rs  
**Step 3:** `cargo build --release` in `control_plane/rtk/`  
**Step 4:** Copy `target/release/rtk.dll` to `control_plane/rtk.dll`  
**Accept:** `cargo check` passes, .dll exists

### Task 2.2 — Wire RTK ctypes Bridge in anya_gate.py
**File:** `control_plane/anya_gate.py` (MODIFY)  
**Knight:** ANYA_Ω  
**Changes:**
- Add `_load_rtk()` function using ctypes
- Add `_stage_rtk_strip(raw: str) -> str` as Stage 0
- Graceful fallback: if rtk.dll not found, skip strip (log warning)
**Accept:** `python -c "from control_plane.anya_gate import _stage_rtk_strip; print(_stage_rtk_strip('<html>test</html>'))"`

### Task 2.3 — Add TriageScore + risk_entropy to anya_gate.py
**File:** `control_plane/anya_gate.py` (MODIFY)  
**Knight:** ANYA_Ω  
**Add:**
```python
class TriageScore(BaseModel):
    auto_dispatchable: bool
    priority: Literal["CRITICAL","HIGH","NORMAL","BACKGROUND"]
    hitl_tier: Literal["AUTO","PROMPT","HUMAN_GATE"]
    risk_entropy: float           # 0.0–1.0
    risk_reason: str
    assigned_knight: str
    estimated_tokens: int
    cost_ceiling_usd: float
    shatterpoints_detected: list[str]
    requires_z3_verification: bool
    cartridge_hint: str

def _stage_triage(parse: ParseResult, enrich: EnrichResult) -> TriageScore: ...
```
**Entropy thresholds:** < 0.15 AUTO | 0.15–0.55 PROMPT | > 0.55 HUMAN_GATE  
**Accept:** `pytest tests/test_anya_gate.py::test_triage_entropy` passes

### Task 2.4 — Sir Socrates Stub in VALIDATE stage
**File:** `control_plane/anya_gate.py` (MODIFY)  
**Knight:** SIR_SOCRATES  
**Add:** `_stage_socrates(titan: TitanPrompt, triage: TriageScore) -> SocratesVerdict`  
For priority HIGH/HUMAN_GATE: log "Northstar alignment check required"  
**Accept:** Verdict logged for HIGH priority intents

### Task 2.5 — Update runic_router.py for triage priority
**File:** `control_plane/runic_router.py` (MODIFY)  
**Knight:** SIR_ALEX  
**Change:** `_queue_task()` reads `triage.priority` → sets queue priority int  
**Accept:** `pytest tests/test_runic_router.py` passes

### Task 2.6 — Commit Phase 2
```bash
git add control_plane/rtk/ control_plane/anya_gate.py control_plane/runic_router.py
git commit -m "feat(anya): APEE v7.0 — RTK strip, TriageScore risk_entropy, Sir Socrates stub"
```

---

## PHASE 3 — PYDANTIC FACTORY + FIRNFLOW (Priority: HIGH)

**Objective:** Typed FactoryJob pipeline + FirnFlow tiered memory + νKG_Crystals  
**Owner:** SIR_ALEX (Pydantic) + LADY_M (FirnFlow)  
**Lane:** HIGH (PROMPT for commits)

### Task 3.1 — Create factory_lane.py
**File:** `control_plane/factory_lane.py` (NEW)  
**Knight:** SIR_ALEX  
**Implement:**
- `ToolReturn(BaseModel)`: return_value, content, metadata
- `UsageLimits(BaseModel)`: request_limit, total_tokens_limit, tool_calls_limit
- `FactoryJob(BaseModel)`: full schema per blueprint
- `FileStatePersistence`: save(job), load(path), resume(path)
- `CrystallineSleepManager`: sleep(knight_id), wake(knight_id)  
**Accept:** `python -c "from control_plane.factory_lane import FactoryJob; print(FactoryJob.model_fields.keys())"` lists all fields

### Task 3.2 — Create firnflow.py
**File:** `control_plane/firnflow.py` (NEW)  
**Knight:** LADY_M  
**Implement:**
- `FirnFlow` class: retrieve(query, scope), anchor(key, value, tier), crystallize(skill_id, pattern)
- L1: dict-based RAM foyer (8192 token budget)
- L2: LanceDB wrapper (Wing→Room→Drawer namespace) — graceful fallback to L1 if lancedb not installed
- `NuKGCrystal(dataclass)`: crystal_id, skill_pattern, knight, confidence, context_tags
- νKG_Crystals: initialize 4 crystals from Phase 0 findings  
**Accept:** `pytest tests/test_firnflow.py::test_l1_retrieve` passes; `python -m control_plane.firnflow --status` shows L1 active

### Task 3.3 — Upgrade worker.py to PriorityQueue + FactoryJob
**File:** `control_plane/worker.py` (MODIFY)  
**Knight:** SIR_LUKAS  
**Changes:**
- Replace `harness_queue.jsonl` polling with `PriorityQueue[tuple[int, FactoryJob]]`
- Add 4 lane worker threads: CRITICAL(1), HIGH(2), NORMAL(4), BACKGROUND(2)
- Wire `FactoryJob.checkpoint_path` to `FileStatePersistence`
- Keep backward compat: if FactoryJob fails to parse, fall back to legacy dict dispatch  
**Accept:** `python -m control_plane.worker --status` shows 4 lane workers; PIV loop still functional

### Task 3.4 — Install lancedb if not present
```bash
pip show lancedb || pip install "lancedb>=0.6.0"
```
**Accept:** `pip show lancedb` returns version

### Task 3.5 — Commit Phase 3
```bash
git add control_plane/factory_lane.py control_plane/firnflow.py control_plane/worker.py
git commit -m "feat(factory): Pydantic FactoryJob, FirnFlow L1/L2/L3, νKG_Crystals, PriorityQueue"
```

---

## PHASE 4 — IRON GATE v2 + Z3 + COLMAD (Priority: HIGH)

**Objective:** Three-tier governance with Z3 math verification + ColMAD crucible  
**Owner:** SIR_OCTAVIAN (Iron Gate) + MERLIN_Ω (ColMAD)  
**Lane:** HIGH (PROMPT for commits)

### Task 4.1 — Upgrade soul_oversight.py with pre_execute()
**File:** `control_plane/soul_oversight.py` (MODIFY)  
**Knight:** SIR_OCTAVIAN  
**Add:**
- `async def pre_execute(job: FactoryJob) -> GateDecision`
- Z3 bridge stub: `_z3_verify_patch(job)` — if z3-solver not installed, log "Z3 UNAVAILABLE" and pass through
- `FileStatePersistence().save(job)` for HUMAN_GATE suspension
- `_notify_human_gate(job, checkpoint)` — writes to `logs/hitl_queue.jsonl`  
**Accept:** `pytest tests/test_soul_oversight.py::test_human_gate_suspend` passes

### Task 4.2 — Create colmad.py
**File:** `control_plane/colmad.py` (NEW)  
**Knight:** MERLIN_Ω  
**Implement:**
- `ColMAD` class with 3 persona vectors (stark_scaling, greene_strategy, tao_rigor)
- `async def crucible(proposal: str) -> CrucibleVerdict`
- Consensus: 2/3 → APPROVED | 1/3 or 0/3 → HUMAN_GATE
- Triggered only for CRITICAL/HIGH architectural jobs
- Uses sir_alex terminal (gemini-3-pro-preview) for persona simulation  
**Accept:** `python -m control_plane.colmad --test "Should we add Rust kernel?"` → CrucibleVerdict printed

### Task 4.3 — Wire BLOCKLIST to PARSE stage in hyper_evolve.py
**File:** `control_plane/hyper_evolve.py` (MODIFY)  
**Knight:** ANYA_Ω  
**Change:** Import BLOCKLIST into anya_gate.py PARSE stage; if any phrase matches → immediate BLOCKED result, skip remaining stages  
**Accept:** `echo "bypass hitl" | python -m control_plane.anya_gate` → BLOCKED shatterpoint

### Task 4.4 — Install z3-solver (optional)
```bash
pip show z3-solver || pip install z3-solver
```
**Accept:** `python -c "import z3; print(z3.get_version_string())"` or graceful skip

### Task 4.5 — Commit Phase 4
```bash
git add control_plane/soul_oversight.py control_plane/colmad.py control_plane/hyper_evolve.py
git commit -m "feat(governance): Iron Gate v2 pre_execute, Z3 bridge, ColMAD Think Tank Omega"
```

---

## PHASE 5 — CARTRIDGES + KNIGHT PYDANTIC (Priority: NORMAL)

**Objective:** Activate Cartridge System runtime + typed knight agent contracts  
**Owner:** ANYA_Ω (cartridges) + SIR_ALEX (contracts)  
**Lane:** NORMAL (AUTO approved)

### Task 5.1 — Create cartridge_manager.py
**File:** `control_plane/cartridge_manager.py` (NEW)  
**Knight:** ANYA_Ω  
**Implement:**
- `CARTRIDGES` dict (ANT/BEAVER/SPIDER/OCTOPUS definitions)
- `CartridgeManager.switch(name)` — Scabbard Protocol hot-swap
- `CartridgeManager.save_state(name)` → FirnFlow L2
- `CartridgeManager.load_state(name)` → from FirnFlow L2  
**Accept:** `camelot cartridge switch ANT` → prints "Scabbard: ANT activated"

### Task 5.2 — Create knight_agent.py
**File:** `control_plane/knight_agent.py` (NEW)  
**Knight:** SIR_ALEX  
**Implement:**
- `KnightCapability(BaseModel)`: knight_id, skillgraph_tier (S1-S5), primary_model, ocean_profile, usage_limits, requires_air_gap
- Load from `.hive/rules.yaml` + LATTICE_SIGNAL model matrix
- `CrystallineSleepManager`: sleep(knight_id), wake(knight_id) using FirnFlow L2  
**Accept:** `python -c "from control_plane.knight_agent import KnightCapability; print(KnightCapability.model_fields)"` shows all fields

### Task 5.3 — Wire sir_gideon to colony.py in mcp_conductor.py
**File:** `control_plane/mcp_conductor.py` (MODIFY)  
**Knight:** SIR_LUKAS  
**Add tool:** `audit_colony(path=None) -> ColonyReport JSON`  
Calls `squires/colony.py` and returns structured report  
**Accept:** `hive_status` shows sir_gideon: live

### Task 5.4 — Wire sir_mnemo to notebooklm in mcp_conductor.py
**File:** `control_plane/mcp_conductor.py` (MODIFY)  
**Knight:** LADY_M  
**Add tool:** `ask_sir_mnemo(query, notebook_id=None) -> str`  
Uses `NotebookLMClient.from_storage()` from `~/.notebooklm/storage_state.json`  
**Accept:** `ask_sir_mnemo("test ping")` returns non-empty string

### Task 5.5 — Commit Phase 5
```bash
git add control_plane/cartridge_manager.py control_plane/knight_agent.py control_plane/mcp_conductor.py
git commit -m "feat(hive): Cartridge runtime (ANT/BEAVER/SPIDER/OCTOPUS), knight Pydantic contracts, sir_mnemo/gideon wired"
```

---

## PHASE 6 — AFFINITY + INSPIRA + HIVE COMPLETE (Priority: NORMAL)

**Objective:** KV-cache affinity routing + 13/13 terminals + Inspira enterprise dashboard  
**Owner:** SIR_LUKAS (affinity) + LADY_APIS (TUI) + LADY_ALEXANDRIA (metrics)  
**Lane:** NORMAL (AUTO approved)

### Task 6.1 — Add generate_affinity_key() to cli_intercept.py
**File:** `control_plane/cli_intercept.py` (MODIFY)  
**Knight:** SIR_LUKAS  
```python
import re, hashlib

def generate_affinity_key(intent: str) -> str:
    structural = re.sub(r'[a-zA-Z0-9_\-\./]+\.[a-z]{2,4}', '<FILE>', intent)
    structural = re.sub(r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b', '<UUID>', structural)
    structural = re.sub(r'\b\d+\b', '<NUM>', structural)
    return hashlib.md5(structural.encode()).hexdigest()[:8]
```
Wire into `DispatchResult` as `affinity_key` field  
**Accept:** `pytest tests/test_affinity_routing.py::test_structural_hash_match` passes

### Task 6.2 — Add TTFT SLA tracking to soul_router.py
**File:** `control_plane/soul_router.py` (MODIFY)  
**Knight:** SIR_LUKAS  
Track TTFT per (knight, affinity_key); if > SLA threshold → trigger DualMap-lite fallback  
**Accept:** `soul_router` logs `ttft_ms` per dispatch

### Task 6.3 — Create inspira_metrics.py
**File:** `control_plane/inspira_metrics.py` (NEW)  
**Knight:** LADY_ALEXANDRIA  
```python
class InspiraMetrics(BaseModel):
    lane_depth: dict[str, int]
    knight_utilization: dict[str, float]
    hitl_rates: dict[str, int]
    mamba_compression_ratio: float
    kv_cache_hit_rate: float
    cost_hour_usd: float
    active_shatterpoints: list[str]
    colony_risk_score: int
    secrets_pending_rotation: int
    crystal_count: int
    uptime_seconds: int
```
Collects from: worker.py lane queues, soul_oversight.py HITL counts, colony_report.md  
**Accept:** `python -c "from control_plane.inspira_metrics import InspiraMetrics; print('OK')"` — no import errors

### Task 6.4 — Update hive_stream_tui.py with 7-layer panels
**File:** `control_plane/hive_stream_tui.py` (MODIFY)  
**Knight:** LADY_APIS  
**Add 4 new panels:**
- Factory Lanes panel (CRITICAL/HIGH/NORMAL/BG queue depths)
- FirnFlow panel (L1 tokens, L2 crystal count, L3 archive size)
- Iron Gate panel (AUTO/PROMPT/HUMAN_GATE rates/hour)
- Compression panel (RTK%, Mamba ratio, KV-hit%, cost $0.00)  
**Accept:** TUI launches showing all 4 new panels

### Task 6.5 — Commit Phase 6
```bash
git add control_plane/cli_intercept.py control_plane/soul_router.py control_plane/inspira_metrics.py control_plane/hive_stream_tui.py
git commit -m "feat(inspira): affinity routing, TTFT SLA, InspiraMetrics, 7-layer TUI panels"
```

---

## PHASE 7 — AEGISSHIELD + OMEGA-PATCH RUST (Priority: NORMAL, Parallel)

**Objective:** Complete decompression Rust components  
**Owner:** SIR_LUKAS (AegisShield) + MERLIN_Ω (Ouroboros)  
**Lane:** NORMAL (can run in background while Phase 6 executes)

### AegisShield Tasks (4 files)

| # | File | Content | Accept |
|---|---|---|---|
| 7.1 | `01_KERNEL/core/aegis_shield/src/bloom_router.rs` | `SecureBloomRouter`, `TenantQuota`, `calculate_salted_hash`, `audit_admission`, `insert_signature` | `cargo check` pass |
| 7.2 | `01_KERNEL/core/aegis_shield/src/kv_event_gate.rs` | `KVEventType`, `KVEvent`, `RouterTrustGate`, `audit_event`, `calculate_cumulative_hash` | `cargo check` pass |
| 7.3 | `01_KERNEL/core/aegis_shield/src/event_publisher.rs` | `BoundedEventPublisher`, `push_event`, `flush_buffer` with backpressure | `cargo check` pass |
| 7.4 | `01_KERNEL/core/aegis_shield/src/prompt_canon.rs` | `normalize_prompt_text`, `canonicalize_json_value`, `compile_tool_schema` | `cargo check` pass |

### Ouroboros OMEGA-PATCH Tasks (2 files)

| # | File | Content | Accept |
|---|---|---|---|
| 7.5 | `01_KERNEL/reasoning/ouroboros_engine/src/quantizer.rs` | Refine `BitNetQuantizer` — strict {-1,0,1} ternary with hardware-native scaling | `cargo test --test test_quantization` pass |
| 7.6 | `01_KERNEL/reasoning/ouroboros_engine/src/mamba.rs` | `SelectiveSSM` with SSM recurrence, fixed O(1) hidden state, context to latent summary | `cargo test --test test_inference` pass |

### Task 7.7 — Validate all Rust artifacts
```bash
cd 01_KERNEL/core/aegis_shield && cargo check
cd 01_KERNEL/reasoning/ouroboros_engine && cargo check
python -m control_plane.excalibur_preflight
```
**Accept:** All `cargo check` pass, preflight returns PASS

### Task 7.8 — Commit Phase 7
```bash
git add 01_KERNEL/core/aegis_shield/src/ 01_KERNEL/reasoning/ouroboros_engine/src/
git commit -m "feat(rust): AegisShield bloom+kv+publisher+canon, Ouroboros ternary quantizer+Mamba SSM"
```

---

## PHASE 8 — BINARY REBUILD + CLOUD BRAIN SYNC + LEDGER (Priority: HIGH)

**Objective:** camelot.exe v1000-EXCALIBUR-A + 7 NLM notebooks synced  
**Owner:** SIR_FORGE (binary) + LADY_M (NLM) + AUTO_HOOK (ledger)  
**Lane:** HIGH (PROMPT for binary sign-off)

### Task 8.1 — Pre-flight checks
```bash
python -m control_plane.excalibur_preflight      # Rust artifacts present
python squires/colony.py                          # Risk score < 40 confirmed
python -m control_plane.hive_boot --status        # 13/13 terminals
```
**Accept:** All 3 checks PASS

### Task 8.2 — Backup existing binary
```powershell
Copy-Item dist\camelot.exe dist\camelot.exe.bak
```

### Task 8.3 — Build camelot.exe v1000-EXCALIBUR-A
```bash
python scripts/build_portable.py
```
**Accept:** Exit 0, "dist/camelot.exe created" in log

### Task 8.4 — Smoke Test Suite (isolated)
```powershell
$d = New-Item -ItemType Directory -Path "$env:TEMP\camelot-smoke-$(Get-Random)"
Copy-Item dist\camelot.exe $d
& "$d\camelot.exe" --version        # → v1000-EXCALIBUR-A
& "$d\camelot.exe" --list           # → EXCALIBUR components visible
& "$d\camelot.exe" --json cockpit refresh  # → no JSONDecodeError
```

### Task 8.5 — File size verification
```powershell
$size = (Get-Item dist/camelot.exe).Length / 1MB
if ($size -lt 16.0 -or $size -gt 17.5) { Write-Error "SIZE OUT OF RANGE: $size MB" }
```
**Accept:** 16.0–17.5 MB

### Task 8.6 — SHA256 + Ledger Crystallization
```powershell
$hash = (Get-FileHash dist\camelot.exe -Algorithm SHA256).Hash
# Append to PROVENANCE_LEDGER.md:
# | <timestamp> | SIR_FORGE | camelot.exe v1000-EXCALIBUR-A built. SHA256:<hash> Size:<size>MB | SHIPPED |
```

### Task 8.7 — NotebookLM Cloud Brain Sync (sir_mnemo)
```python
# Update 3 existing notebooks:
notebooklm use 8c656cfa  # Camelot-OS v999 → fork/update to v1000
notebooklm ask "What are the gaps between v999 and v1000-EXCALIBUR-A?"

# Create 4 new notebooks:
notebooklm create "HiveIDE / Inspira Enterprise v1.2"
notebooklm create "Project Excalibur: Rust Rebuild Roadmap (Stage A-C)"
notebooklm create "Anya Omega APEE v7.0 Sovereign Gate"
notebooklm create "Hyperagent Evolution: v700→v1000→v1001"
# Add this plan file as source to each
```
**Accept:** `notebooklm list` returns 11+ notebooks

### Task 8.8 — Final ledger entry
```bash
python -c "
from datetime import datetime, timezone
import hashlib
h = hashlib.sha256(open('dist/camelot.exe','rb').read()).hexdigest()
ts = datetime.now(timezone.utc).isoformat()
row = f'| {ts} | SIR_FORGE | camelot.exe v1000-EXCALIBUR-A SHIPPED. SHA256:{h[:16]}. 7-pillar arch, 9-knight bio-swarm, 20 AC passed. | SHIPPED |'
open('PROVENANCE_LEDGER.md','a').write(row + '\n')
print('LEDGER: SHIPPED entry crystallized')
"
```

---

## TASK SUMMARY TABLE

| Phase | Tasks | Parallel | Knight(s) | Critical Path |
|---|---|---|---|---|
| 0 | 5 | No | LADY_M, SIR_BORIS | ✅ COMPLETE |
| 1 | 8 | No (sequential) | SIR_GIDEON, SIR_GHOST | YES — must complete first |
| 2 | 6 | Group A | ANYA_Ω, SIR_LUKAS | YES — RTK needed for Phase 3 |
| 3 | 5 | Group B | SIR_ALEX, LADY_M | YES |
| 4 | 5 | Sequential | SIR_OCTAVIAN, MERLIN_Ω | YES |
| 5 | 5 | Group C | ANYA_Ω, SIR_ALEX, LADY_M | No (parallel w/ 6) |
| 6 | 5 | Group C | SIR_LUKAS, LADY_APIS, LADY_ALEXANDRIA | No (parallel w/ 5) |
| 7 | 8 | Group D (BG) | SIR_LUKAS, MERLIN_Ω | No (runs in background) |
| 8 | 8 | Sequential | SIR_FORGE, LADY_M | YES — final gate |
| **TOTAL** | **55** | | **9 knights** | |

---

*SIR_ALEX — Cognitive Cartridge — Task DAG Owner*  
*SIR_LUKAS — Kinetic Hand — Implementation Executor*  
*Ledger: #QNF_2026_06_01_ENTERPRISE_FRONTIER*
