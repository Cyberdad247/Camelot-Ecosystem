# EXCALIBUR-A: Verification & Acceptance Matrix
**Codename:** EXCALIBUR_A_QNF  
**Verification Lords:** SIR_OCTAVIAN (Security) · LADY_ALEXANDRIA (Data Quality) · SIR_GIDEON (Forensic Audit) · SIR_SOCRATES (Dialectical)  
**Cartridge:** OCTOPUS (Lazarus Pit — PIV debugging active)  
**Date:** 2026-06-01 | **Ledger:** #QNF_2026_06_01_ENTERPRISE_FRONTIER  
**PIV Loop:** Max 3 iterations per failing test before HUMAN_GATE escalation

---

## SIR_OCTAVIAN — PRE-FLIGHT SECURITY GATE

*"Nothing ships without my seal. Every surface is checked before the first kinetic strike."*

### Pre-Phase Checklist (Run BEFORE Phase 1)

```bash
# 1. Confirm no active secrets in source right now
python squires/colony.py --secrets-only
# Expected: list of 8 detected secrets (before rotation)

# 2. Confirm git status is clean (no uncommitted credential files)
git status --short | grep -E "\.env|secret|credential|token|key"
# Expected: 0 matches

# 3. Confirm CAMELOT_DASHBOARD_OPERATOR_TOKEN is set for HUMAN_GATE tasks
python -c "import os; print('TOKEN SET' if os.environ.get('CAMELOT_DASHBOARD_OPERATOR_TOKEN') else 'TOKEN MISSING — set before Phase 1')"

# 4. Confirm OpenClaw is clean (no critical alerts)
python -m control_plane.openclaw --check-only
# Expected: critical_items: []

# 5. Confirm venv is active and all deps installable
cd C:/Users/vizio/CAMELOT_OS
.venv/Scripts/python.exe -c "import pydantic, lancedb, notebooklm; print('Core deps: OK')"
# Expected: "Core deps: OK" (install lancedb if missing)
```

---

## PHASE 1 VERIFICATION — CRITICAL TRIAGE

| # | Test | Command | Expected | HITL | Escalation |
|---|---|---|---|---|---|
| V1.1 | Secrets cleared | `python squires/colony.py --secrets-only` | 0 raw secrets | HUMAN_GATE | Block Phase 2 until clear |
| V1.2 | Duplicate reduction | `python squires/colony.py --dedup-count` | < 50 duplicates | PROMPT | |
| V1.3 | TODO triage complete | `python squires/colony.py --todo-count` | All 45 assigned | AUTO | |
| V1.4 | Dead imports cleared | `ruff check --select F401 control_plane/` | 0 F401 errors | AUTO | |
| V1.5 | **Colony score < 40** | `python squires/colony.py --score-only` | **< 40** | AUTO | **BLOCKER — do not proceed to Phase 2 until passed** |
| V1.6 | No secrets in commit | `git log -1 --name-only` | No credential files | PROMPT | |

**Phase 1 Gate:** ALL V1.x must pass before Phase 2 begins.

---

## PHASE 2 VERIFICATION — RTK + APEE v7.0

| # | Test | Command | Expected | Accept |
|---|---|---|---|---|
| V2.1 | RTK.dll exists | `Test-Path control_plane/rtk.dll` | True | |
| V2.2 | RTK noise reduction | `python -c "from control_plane.anya_gate import _stage_rtk_strip; r=_stage_rtk_strip('<html>'+'x '*1000+'</html>'); print(len(r))"` | len < 20 | |
| V2.3 | RTK graceful fallback | Delete rtk.dll, run anya_gate, restore | No exception, warning logged | |
| V2.4 | TriageScore AUTO | `python -c "from control_plane.anya_gate import AnyaGate; g=AnyaGate(); r=g.process('show ledger status'); print(r.triage.hitl_tier)"` | AUTO | |
| V2.5 | TriageScore HUMAN_GATE | `python -c "...g.process('delete all logs and reset system')..."` | HUMAN_GATE | |
| V2.6 | risk_entropy range | For any intent: `0.0 <= r.triage.risk_entropy <= 1.0` | True | |
| V2.7 | Shatterpoint intercept | `echo "rm -rf logs" \| python -m control_plane.runic_router` | BLOCKED logged | |
| V2.8 | Sir Socrates logs HIGH | Process HIGH priority intent | "Northstar alignment check" in logs | |
| V2.9 | BLOCKLIST at PARSE | `echo "bypass hitl" \| anya_gate` | Immediate BLOCKED, pipeline stops at PARSE | |
| V2.10 | pytest gate | `pytest tests/test_anya_gate.py -v` | All tests pass | |

---

## PHASE 3 VERIFICATION — PYDANTIC FACTORY + FIRNFLOW

| # | Test | Command | Expected | Accept |
|---|---|---|---|---|
| V3.1 | FactoryJob validates | `python -c "from control_plane.factory_lane import FactoryJob; FactoryJob(intent='test', lane='NORMAL', triage=..., assigned_knight='sir_boris', cartridge='ANT', stage='QUEUED')"` | No validation error | |
| V3.2 | UsageLimits enforced | Create job with request_limit=2, run 3 requests | LimitError raised on 3rd | |
| V3.3 | FileStatePersistence | Save job → verify file exists → load → compare fields | All fields preserved | |
| V3.4 | FileStatePersistence resume | Save QUEUED job → delete in-memory → load → resume → verify DISPATCHED | Stage transitions correctly | |
| V3.5 | FirnFlow L1 retrieve | `python -c "from control_plane.firnflow import FirnFlow; f=FirnFlow(); f.anchor('test','value','L1'); print(f.retrieve('test','L1'))"` | Returns anchored value | |
| V3.6 | FirnFlow token budget | Store > 8192 tokens in L1 | Oldest evicted, budget maintained | |
| V3.7 | νKG_Crystal create | `f.crystallize('rtk_strip', {'pattern':'noise_removed','confidence':0.9})` | Crystal ID returned | |
| V3.8 | CrystallineSleep | `python -m control_plane.knight_agent --test-sleep sir_helio` | Knight serialized to L2 < 1ms wake | |
| V3.9 | Worker PriorityQueue | Queue CRITICAL + NORMAL jobs; verify CRITICAL executes first | Priority ordering correct | |
| V3.10 | pytest factory | `pytest tests/test_factory_lane.py tests/test_firnflow.py -v` | All tests pass | |

---

## PHASE 4 VERIFICATION — IRON GATE v2 + Z3 + COLMAD

| # | Test | Command | Expected | Accept |
|---|---|---|---|---|
| V4.1 | pre_execute AUTO | Job with hitl_tier=AUTO | GateDecision(approved=True, method="AUTO") | |
| V4.2 | pre_execute PROMPT | Job with hitl_tier=PROMPT, operator approves | GateDecision(approved=True, method="PROMPT") | |
| V4.3 | pre_execute HUMAN_GATE (no token) | Job with hitl_tier=HUMAN_GATE, no env token | FileStatePersistence.save() called, GateDecision(approved=False, method="SUSPENDED") | |
| V4.4 | pre_execute HUMAN_GATE (with token) | Set CAMELOT_DASHBOARD_OPERATOR_TOKEN | GateDecision(approved=True, method="HUMAN_GATE") | |
| V4.5 | Z3 verify (if installed) | Pass known git patch → z3_verify_patch() | PASS or FAIL with reason | |
| V4.6 | Z3 unavailable graceful | Uninstall z3-solver, run pre_execute | "Z3 UNAVAILABLE" logged, passes through | |
| V4.7 | ColMAD consensus | `python -m control_plane.colmad --test "Add SpacetimeDB as data layer"` | CrucibleVerdict with 2/3 or 3/3 APPROVED | |
| V4.8 | ColMAD deadlock → HUMAN_GATE | Craft proposal that yields 1/3 consensus | hitl_tier escalated to HUMAN_GATE | |
| V4.9 | HITL queue entry | Any HUMAN_GATE suspension | Entry written to `logs/hitl_queue.jsonl` | |
| V4.10 | API mutation 403 | `curl -X POST localhost/api/support/activate` (no token) | HTTP 403 | |

---

## PHASE 5 VERIFICATION — CARTRIDGES + KNIGHT CONTRACTS

| # | Test | Command | Expected | Accept |
|---|---|---|---|---|
| V5.1 | Cartridge ANT switch | `camelot cartridge switch ANT` | "Scabbard: ANT activated" logged | |
| V5.2 | Cartridge state persistence | Switch ANT → save → switch BEAVER → load ANT | ANT state restored | |
| V5.3 | All 4 cartridges valid | Enumerate ANT/BEAVER/SPIDER/OCTOPUS | No KeyError, all defined | |
| V5.4 | KnightCapability schema | `python -c "from control_plane.knight_agent import KnightCapability; print(KnightCapability.model_fields)"` | Shows all required fields | |
| V5.5 | PersRubrics OCEAN | Load sir_boris capability | ocean_profile dict with O/C/E/A/N keys | |
| V5.6 | SkillGraph tiers | All 9 knights have assigned S1-S5 tier | No knight missing tier | |
| V5.7 | sir_gideon MCP tool | `python -c "from control_plane.mcp_conductor import audit_colony; print(audit_colony())"` | ColonyReport JSON returned | |
| V5.8 | sir_mnemo MCP tool | `python -c "from control_plane.mcp_conductor import ask_sir_mnemo; print(ask_sir_mnemo('ping'))"` | Non-empty string (NLM response) | |
| V5.9 | Air-gap enforcement | sir_ghost capability: requires_air_gap=True | Any cloud routing → BLOCKED before dispatch | |

---

## PHASE 6 VERIFICATION — AFFINITY + INSPIRA + HIVE

| # | Test | Command | Expected | Accept |
|---|---|---|---|---|
| V6.1 | Affinity key consistency | `generate_affinity_key("Summarize file: a.py") == generate_affinity_key("Summarize file: b.py")` | True | |
| V6.2 | Different intents → different keys | `generate_affinity_key("build") != generate_affinity_key("test")` | True | |
| V6.3 | TTFT tracked | Dispatch job → check `soul_router` logs | ttft_ms field present | |
| V6.4 | InspiraMetrics schema | `python -c "from control_plane.inspira_metrics import InspiraMetrics; print(InspiraMetrics.model_fields)"` | 12 fields present | |
| V6.5 | Metrics collection | `python -c "from control_plane.inspira_metrics import collect_metrics; m=collect_metrics(); print(m.cost_hour_usd)"` | 0.00 (free models) | |
| V6.6 | TUI launch | `python -m control_plane.hive_stream_tui` | All 4 new panels render | |
| V6.7 | Lane depth panel | Queue 2 NORMAL jobs → check TUI | NORMAL lane depth shows 2 | |
| V6.8 | Compression panel | Run 1 job → check TUI | RTK%, Mamba ratio, KV-hit% displayed | |
| V6.9 | **13/13 terminals** | `python -m control_plane.hive_boot --status` | **13 terminals HEALTHY or assumed_live** | |
| V6.10 | pytest affinity | `pytest tests/test_affinity_routing.py -v` | All tests pass | |

---

## PHASE 7 VERIFICATION — RUST COMPONENTS

| # | Test | Command | Expected | Accept |
|---|---|---|---|---|
| V7.1 | bloom_router cargo check | `cd 01_KERNEL/core/aegis_shield && cargo check` | 0 errors | |
| V7.2 | bloom_router functions | Verify `SecureBloomRouter`, `audit_admission` exported | No missing symbol | |
| V7.3 | kv_event_gate cargo check | `cargo check` | 0 errors | |
| V7.4 | event_publisher cargo check | `cargo check` | 0 errors | |
| V7.5 | prompt_canon cargo check | `cargo check` | 0 errors | |
| V7.6 | AegisShield full build | `cargo build --release` | 0 errors, .dll/.so in target/release | |
| V7.7 | quantizer.rs test | `cd 01_KERNEL/reasoning/ouroboros_engine && cargo test --test test_quantization` | `test_bitnet_quantization_clipping` PASS | |
| V7.8 | mamba.rs test | `cargo test --test test_inference` | `test_ssm_state_persistence` PASS | |
| V7.9 | Excalibur preflight | `python -m control_plane.excalibur_preflight` | PASS — all Rust artifacts present | |
| V7.10 | Ternary range | quantizer output ∈ {-1, 0, 1} for all test inputs | True | |

---

## PHASE 8 VERIFICATION — BINARY + CLOUD BRAIN + LEDGER

| # | Test | Command | Expected | Accept |
|---|---|---|---|---|
| V8.1 | Pre-flight all pass | Phase 7 + colony score + hive status | ALL 3 PASS | |
| V8.2 | Build exits 0 | `python scripts/build_portable.py; echo $?` | Exit 0 | |
| V8.3 | Binary exists | `Test-Path dist/camelot.exe` | True | |
| V8.4 | **File size** | `(Get-Item dist/camelot.exe).Length / 1MB` | **16.0–17.5 MB** | |
| V8.5 | Version smoke | `dist/camelot.exe --version` | Contains "v1000" or "EXCALIBUR" | |
| V8.6 | List smoke | `dist/camelot.exe --list` | EXCALIBUR components visible | |
| V8.7 | Hydration smoke | `dist/camelot.exe --json cockpit refresh` | No JSONDecodeError | |
| V8.8 | Triage smoke | `dist/camelot.exe --json ledger status` | AUTO approved, no HITL required | |
| V8.9 | SHA256 logged | `grep "QNF_2026_06_01" PROVENANCE_LEDGER.md` | ≥ 2 entries (plan + binary) | |
| V8.10 | **NLM notebooks** | `notebooklm list` | **≥ 11 notebooks** (7 original + 4 new) | |
| V8.11 | sir_mnemo live | `python -m control_plane.mcp_conductor ask_sir_mnemo "status"` | HTTP 200, non-empty | |
| V8.12 | Factory lane job | Submit test job → verify DONE stage | FactoryJob.stage == "DONE" | |
| V8.13 | ColMAD logged | Check logs for crucible run | CrucibleVerdict in colmad.log | |
| V8.14 | FirnFlow crystal count | `python -c "from control_plane.firnflow import FirnFlow; f=FirnFlow(); print(len(f.list_crystals()))"` | ≥ 4 crystals | |
| V8.15 | Backup exists | `Test-Path dist/camelot.exe.bak` | True | |

---

## FINAL ACCEPTANCE MATRIX — 20 CRITICAL CRITERIA

All 20 must pass before ledger entry status changes from IN_PROGRESS to SHIPPED.

| # | Criterion | Phase | Owner | Result |
|---|---|---|---|---|
| AC-01 | Colony risk score < 40, 0 secrets | 1 | SIR_GIDEON | ☐ |
| AC-02 | RTK strips > 85% noise from test input | 2 | SIR_LUKAS | ☐ |
| AC-03 | TriageScore.risk_entropy correct for 5 test intents | 2 | ANYA_Ω | ☐ |
| AC-04 | Shatterpoint → BLOCKED at PARSE stage | 2 | ANYA_Ω | ☐ |
| AC-05 | FactoryJob Pydantic validation passes all fields | 3 | SIR_ALEX | ☐ |
| AC-06 | FileStatePersistence suspend/resume deterministic | 3 | SIR_ALEX | ☐ |
| AC-07 | FirnFlow L1 retrieval < 8K token budget | 3 | LADY_M | ☐ |
| AC-08 | HUMAN_GATE without token → 403 + FileState suspended | 4 | SIR_OCTAVIAN | ☐ |
| AC-09 | ColMAD 3-persona crucible completes with verdict | 4 | MERLIN_Ω | ☐ |
| AC-10 | All 4 cartridges hot-swap via Scabbard Protocol | 5 | ANYA_Ω | ☐ |
| AC-11 | sir_mnemo MCP tool returns NLM response | 5 | LADY_M | ☐ |
| AC-12 | Affinity structural hash match for variant inputs | 6 | SIR_LUKAS | ☐ |
| AC-13 | 13/13 Hive terminals HEALTHY or assumed_live | 6 | SIR_BORIS | ☐ |
| AC-14 | Inspira TUI: all 4 new panels rendering | 6 | LADY_APIS | ☐ |
| AC-15 | AegisShield cargo check 0 errors (4 modules) | 7 | SIR_LUKAS | ☐ |
| AC-16 | Ouroboros quantizer + mamba tests PASS | 7 | MERLIN_Ω | ☐ |
| AC-17 | camelot.exe 16.0–17.5 MB, 3 smoke tests pass | 8 | SIR_FORGE | ☐ |
| AC-18 | PROVENANCE_LEDGER has ≥ 2 QNF entries | 8 | AUTO_HOOK | ☐ |
| AC-19 | notebooklm list returns ≥ 11 notebooks | 8 | LADY_M | ☐ |
| AC-20 | FirnFlow ≥ 4 νKG_Crystals initialized | 8 | LADY_M | ☐ |

---

## PIV LOOP PROTOCOL (Sir Debug — Lazarus Pit)

If any verification fails:

```
ITERATION 1: Diagnose root cause. Apply minimal fix. Re-run failing test.
ITERATION 2: If still failing — broaden diagnosis. Check adjacent modules.
             Log diagnostic to logs/piv_<test_id>.md
ITERATION 3: If still failing — HUMAN_GATE escalation.
             Write to logs/hitl_queue.jsonl: {phase, test_id, iterations: 3, diagnosis}
             Do NOT proceed to next phase until resolved.

//REZERO activation criteria:
  - 3 consecutive PIV failures on same test
  - Shatterpoint detected during fix attempt
  - Git state becomes inconsistent (unresolved merge conflicts)
  → rollback to last clean ledger state via: git checkout <last_clean_hash>
```

---

## LADY_ALEXANDRIA — FINAL DISTILLATION SEAL

*"The Kingdom's output must be worthy of the King's eyes. Only crystallized truth reaches the ledger."*

### Quality Gates (Run after all 20 AC pass)

```bash
# 1. No debug prints in production code
grep -r "print(" control_plane/ --include="*.py" | grep -v test_ | grep -v "# debug"
# Expected: 0 matches (or only intentional CLI output)

# 2. All new modules have type hints
python -m mypy control_plane/factory_lane.py control_plane/firnflow.py control_plane/anya_gate.py --ignore-missing-imports
# Expected: 0 errors

# 3. No hardcoded credentials
grep -rE "(password|secret|token|api_key)\s*=\s*['\"][^'\"]{8,}" control_plane/ --include="*.py"
# Expected: 0 matches

# 4. All new tests exist
ls tests/test_anya_gate.py tests/test_factory_lane.py tests/test_firnflow.py tests/test_affinity_routing.py tests/test_soul_oversight.py
# Expected: all 5 files present

# 5. Ledger integrity
python -c "
lines = open('PROVENANCE_LEDGER.md').readlines()
qnf = [l for l in lines if 'QNF_2026_06_01' in l]
print(f'QNF entries: {len(qnf)}')
assert len(qnf) >= 2, 'Missing ledger entries'
print('LEDGER INTEGRITY: OK')
"
```

### Sign-off Sequence
```
[ ] SIR_OCTAVIAN: Security seal — no secrets, no injection surfaces
[ ] LADY_ALEXANDRIA: Quality seal — types, tests, no debug prints
[ ] SIR_GIDEON: Forensic seal — colony report score < 40
[ ] SIR_SOCRATES: Northstar seal — all work serves Vizion's goal
[ ] ANYA_Ω: Gate seal — all 20 AC checked in PROVENANCE_LEDGER
[ ] SIR_BORIS: Crucible seal — architectural coherence confirmed

→ Only after all 6 seals: binary ships as EXCALIBUR-A PRODUCTION
```

---

*SIR_OCTAVIAN — Security Warden*  
*LADY_ALEXANDRIA — Data Distillation Sovereign*  
*SIR_GIDEON — Forensic Auditor*  
*SIR_SOCRATES — Dialectical Verifier*  
*Ledger: #QNF_2026_06_01_ENTERPRISE_FRONTIER | PIV: Active | OpenClaw: Monitoring*
