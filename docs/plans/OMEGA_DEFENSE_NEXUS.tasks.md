# OMEGA DEFENSE NEXUS — Task Plan
**Blueprint:** OMEGA_DEFENSE_NEXUS.blueprint.md  
**Conductor:** SIR_BORIS | **Gate:** ANYA_OMEGA APEE v7.0  
**Date:** 2026-06-05 | **Ledger:** #OMEGA_2026_06_05

---

## PHASE 0 — KNIGHT FORGE (LOW risk, AUTO)
*Define new knights; extend camelot_context personas + Defense Grid roster*

| # | Task | File | Accept |
|---|------|------|--------|
| 0.1 | Create `SirHeimdall` knight class | `01_KERNEL/iron_gate/DEFENSE_GRID/knights/heimdall.py` | `from .heimdall import SirHeimdall` succeeds |
| 0.2 | Create `SirGalahad` knight class | `01_KERNEL/iron_gate/DEFENSE_GRID/knights/galahad.py` | `SirGalahad().zero_trace_write(...)` succeeds |
| 0.3 | Create `SirNemesisPrime` knight class | `01_KERNEL/iron_gate/DEFENSE_GRID/knights/nemesis_prime.py` | `SirNemesisPrime().quarantine(path)` moves to quarantine dir |
| 0.4 | Add Heimdall/Galahad/Nemesis to `knights/__init__.py` | `01_KERNEL/iron_gate/DEFENSE_GRID/knights/__init__.py` | All 7 knights importable |
| 0.5 | Add 3 new knights to `KNIGHT_PERSONAS` dict | `bin/camelot_context.py` | `load_knight_persona('sir_heimdall')` returns non-empty string |
| 0.6 | Write Phase 0 tests | `tests/test_omega_knights.py` | 9 tests PASS |

---

## PHASE 1 — COLONY NEXUS (MEDIUM risk, PROMPT gate)
*Wire colony scanner into Defense Grid as live sensor*

| # | Task | File | Accept |
|---|------|------|--------|
| 1.1 | Create `ColonyNexus` class | `01_KERNEL/iron_gate/DEFENSE_GRID/colony_nexus.py` | Reads `colony_report.md`, returns `ColonyState` |
| 1.2 | Wire `ColonyState.risk_score` → `pre_execute()` risk_entropy | `control_plane/soul_oversight.py` | HIGH colony risk → HUMAN_GATE escalation |
| 1.3 | Create `HermesBus` class | `control_plane/hermes_bridge.py` | `HermesBus.publish('colony.risk', {...})` writes to `~/.hermes/sessions/` |
| 1.4 | Wire ColonyNexus → Hermes `colony.risk` channel | `01_KERNEL/iron_gate/DEFENSE_GRID/colony_nexus.py` | Delta > 10 fires Hermes event |
| 1.5 | Add colony status to `camelot status` output | `bin/camelot_configure.py` | `camelot status` shows colony risk score |
| 1.6 | Write Phase 1 tests | `tests/test_colony_nexus.py` | 6 tests PASS |
| 1.7 | Commit Phase 1 | git | Clean commit, no secrets |

---

## PHASE 2 — SHADOW VEIL (HIGH risk, HUMAN_GATE)
*Fingerprint-less Shadow System — Heimdall + Galahad + Nemesis Prime*

| # | Task | File | Accept |
|---|------|------|--------|
| 2.1 | Create `shadow_veil/` subpackage | `01_KERNEL/iron_gate/DEFENSE_GRID/shadow_veil/__init__.py` | Package importable |
| 2.2 | Implement `SirHeimdall.scan_fingerprint_vectors()` | `knights/heimdall.py` | Returns list of `FingerprintVector` namedtuples |
| 2.3 | Implement `SirHeimdall.watch(callback)` | `knights/heimdall.py` | watchdog integration; fires callback on new threat |
| 2.4 | Implement `SirGalahad.zero_trace_write(path, content)` | `knights/galahad.py` | File written, atime/mtime scrubbed |
| 2.5 | Implement `SirGalahad.stealth_exec(cmd, env_sanitize=True)` | `knights/galahad.py` | Subprocess strips USER/COMPUTERNAME/HOSTNAME |
| 2.6 | Implement `SirNemesisPrime.quarantine(path)` | `knights/nemesis_prime.py` | Moves to `CAMELOT_DefenseGrid_Quarantine/`; Hermes event emitted |
| 2.7 | Implement `SirNemesisPrime.counter_telemetry(endpoint)` | `knights/nemesis_prime.py` | Appends to hosts file — **HUMAN_GATE** |
| 2.8 | Wire Heimdall → Hermes `shadow.threats` → Nemesis AUTO response | `shadow_veil/__init__.py` | Quarantine fires on Heimdall alert |
| 2.9 | `camelot shadow-status` subcommand | `bin/camelot.py` | Shows active vectors + watcher state |
| 2.10 | Write Phase 2 tests | `tests/test_shadow_veil.py` | 10 tests PASS (hosts amendment mocked) |
| 2.11 | Commit Phase 2 | git shadow branch → PR | Iron Gate sign-off |

---

## PHASE 3 — DEPENDENCY ENGINE (MEDIUM risk, PROMPT gate)
*Dynamic dependency resolution + auto-update pipeline*

| # | Task | File | Accept |
|---|------|------|--------|
| 3.1 | Create `DependencyEngine` class | `control_plane/dependency_engine.py` | Parses pyproject.toml, requirements.txt, Cargo.toml, package.json |
| 3.2 | Implement `audit()` → returns `DepAuditResult` with current/outdated counts | same | `camelot deps audit` prints table |
| 3.3 | Implement `check_updates()` using `pip index versions` (no network if local mirror) | same | Returns proposed updates list |
| 3.4 | Implement `propose_update(pkg, ver)` → shadow branch + ruff + pytest gate | same | Shadow branch created; tests run before PR |
| 3.5 | Wire Sir Galahad `stealth_exec` for all pip/cargo fetches | same | No fingerprint on package downloads |
| 3.6 | Hermes `dependency.updates` channel integration | same | Update proposals published to Hermes |
| 3.7 | Add `deps` subcommand to `camelot.py` | `bin/camelot.py` | `camelot deps audit` works |
| 3.8 | Write Phase 3 tests (offline/mocked) | `tests/test_dependency_engine.py` | 8 tests PASS |
| 3.9 | Commit Phase 3 | git | PROMPT approval |

---

## PHASE 4 — COMPRESSION NEXUS (MEDIUM risk, PROMPT gate)
*System-wide compression: context + memory + disk*

| # | Task | File | Accept |
|---|------|------|--------|
| 4.1 | Create `CompressionNexus` class | `control_plane/compression_nexus.py` | 3-tier compress/decompress API |
| 4.2 | Tier 1: QFT context compression (wire existing Sir Alex algo) | same | CLAUDE.md compresses ≤1500 tok |
| 4.3 | Tier 2: FirnFlow L2 MessagePack conversion (graceful fallback) | `control_plane/firnflow.py` | L2 entries 40% smaller |
| 4.4 | Tier 3: Lady Alexandria file compression audit | `control_plane/lady_alexandria.py` | Identifies files >500KB; zstd compress |
| 4.5 | MASON dedup integration → auto-remove confirmed dupes | `control_plane/compression_nexus.py` | 4283 dupes report → user approves batch delete |
| 4.6 | `camelot compress status` subcommand | `bin/camelot.py` | Shows RAM%, disk delta, context ratio |
| 4.7 | Write Phase 4 tests | `tests/test_compression_nexus.py` | 7 tests PASS |
| 4.8 | Commit Phase 4 | git | PROMPT approval |

---

## PHASE 5 — FILE ORGANIZATION ENGINE (HIGH risk, HUMAN_GATE)
*System-wide file taxonomy — Lady M + Lady Alexandria + Sir Gideon audit*

| # | Task | File | Accept |
|---|------|------|--------|
| 5.1 | Create `OrganizeEngine` class | `control_plane/organize_engine.py` | Reads current tree → proposed taxonomy map |
| 5.2 | Lady M semantic clustering: 20492 files → 7-tier taxonomy | same | Cluster map in `logs/organize_proposal.json` |
| 5.3 | HUMAN_GATE approval flow for each taxonomy tier | same | User approves before any move |
| 5.4 | `organize_engine.execute_tier(tier_n)` — move files one tier at a time | same | Imports updated in moved files |
| 5.5 | Sir Gideon colony re-scan post each tier | same | Risk score decreasing after each tier |
| 5.6 | Lady Alexandria cross-reference updater (fix broken imports after moves) | same | Zero import errors post-move |
| 5.7 | Shadow branch for all moves — never on main until HUMAN_GATE | git | All moves on `organize/tier-N` branches |
| 5.8 | Write Phase 5 tests (dry-run mode) | `tests/test_organize_engine.py` | 7 tests PASS (no actual moves in test) |
| 5.9 | Commit Phase 5 | git shadow branch | HUMAN_GATE |

---

## PHASE 6 — NANO_SWARM + HERMES FUSION (MEDIUM risk, PROMPT gate)
*5 autonomous NANO_SWARM nodes wired to Hermes channels*

| # | Task | File | Accept |
|---|------|------|--------|
| 6.1 | Extend `nano_swarm_runtime.py` with 5 autonomous node defs | `control_plane/nano_swarm_runtime.py` | `swarm.colony/compress/organize/shadow/dependency` nodes |
| 6.2 | `swarm.colony` node: subscribe `colony.risk` → assign fix tasks | same | Fires when risk delta > 10 |
| 6.3 | `swarm.compress` node: subscribe `compression.status` → QFT on hot paths | same | Auto-compresses hot contexts |
| 6.4 | `swarm.organize` node: subscribe `organize.progress` → Lady M/Alexandria coord | same | Files progress events |
| 6.5 | `swarm.shadow` node: subscribe `shadow.threats` → Nemesis Prime response | same | AUTO quarantine on threat |
| 6.6 | `swarm.dependency` node: subscribe `dependency.updates` → shadow branch | same | Creates PR on proposal |
| 6.7 | `camelot swarm status` shows all 5 node states | `bin/camelot.py` | All 5 nodes shown with channel + last event |
| 6.8 | Write Phase 6 tests | `tests/test_swarm_hermes_fusion.py` | 8 tests PASS |
| 6.9 | Commit Phase 6 | git | PROMPT approval |

---

## PHASE 7 — SIR SOCRATES NORTHSTAR GATE (LOW risk, PROMPT gate)
*Full Sir Socrates implementation — 5 Socratic alignment questions*

| # | Task | File | Accept |
|---|------|------|--------|
| 7.1 | Create `SirSocrates` class (full impl from stub) | `control_plane/sir_socrates.py` | 5-question async `examine()` method |
| 7.2 | Q1: Local Sovereignty alignment check | same | Returns bool + reasoning |
| 7.3 | Q2: Fingerprint surface reduction check | same | Returns bool + reasoning |
| 7.4 | Q3: Resource efficiency check | same | Returns bool + reasoning |
| 7.5 | Q4: Iron Gate integrity preservation check | same | Returns bool + reasoning |
| 7.6 | Q5: Northstar vs. local optimum check | same | Returns bool + reasoning |
| 7.7 | Wire `SirSocrates.examine()` into `AnyaGate.process()` post-triage | `control_plane/anya_gate.py` | HIGH/CRITICAL intents examined |
| 7.8 | Verdict logging to `logs/northstar_verdicts.jsonl` via Lady Alexandria | same | JSONL entry per HIGH/CRITICAL intent |
| 7.9 | Write Phase 7 tests | `tests/test_sir_socrates.py` | 5/5 Socratic questions + wire test PASS |
| 7.10 | Commit Phase 7 | git | PROMPT approval |

---

## PHASE 8 — OMEGA INTEGRATION (HIGH risk, HUMAN_GATE)
*Full 8-pillar integration + OMEGA verification suite*

| # | Task | File | Accept |
|---|------|------|--------|
| 8.1 | Integration test suite | `tests/test_omega_integration.py` | All 8 pillar acceptance criteria pass |
| 8.2 | Colony risk score verification | colony_report.md | Risk score < 40 (after secret rotation) |
| 8.3 | Hermes channel health check | `camelot cockpit hermes status` | 5 active channels, 0 errors |
| 8.4 | Shadow Veil verification | `camelot shadow-status` | 0 fingerprint vectors active |
| 8.5 | NANO_SWARM status | `camelot swarm status` | All 5 nodes green |
| 8.6 | Final PROVENANCE_LEDGER entry | `PROVENANCE_LEDGER.md` | OMEGA_DEFENSE_NEXUS SHIPPED entry |
| 8.7 | NotebookLM Cloud Brain sync (sir_mnemo) | NLM notebooks | "OMEGA Defense Nexus v1" notebook created |

---

## TASK SUMMARY

| Phase | Tasks | Gate | Knights |
|-------|-------|------|---------|
| 0 | 6 | AUTO | SIR_BORIS |
| 1 | 7 | PROMPT | SIR_GIDEON + SIR_MERLIN |
| 2 | 11 | **HUMAN_GATE** | SIR_HEIMDALL + SIR_GALAHAD + SIR_NEMESIS |
| 3 | 9 | PROMPT | SIR_LINK |
| 4 | 8 | PROMPT | SIR_ALEX + LADY_ALEXANDRIA |
| 5 | 9 | **HUMAN_GATE** | LADY_M + LADY_ALEXANDRIA + SIR_GIDEON |
| 6 | 9 | PROMPT | SIR_MERLIN |
| 7 | 10 | PROMPT | SIR_SOCRATES |
| 8 | 7 | **HUMAN_GATE** | SIR_BORIS + ANYA_OMEGA |
| **TOTAL** | **76** | | **12 knights** |

---

*SIR_BORIS — The Anvil — Alpha Omega Forgemaster*  
*ANYA_OMEGA — The Gate — APEE v7.0 Cleared*  
*2026-06-05 | #OMEGA_2026_06_05*
