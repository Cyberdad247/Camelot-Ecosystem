# 🧪 LOCAL ARCHITECTURE LOAD TESTING — Cybertronia Single-Host Strategy

**Status:** 2026-06-22 — Cluster-independent, local-first validation  
**Target:** Windows dev box (Cybertronia) — v1000-EXCALIBUR-A architecture  
**Hardware Baseline:** 8GB RAM (per `.agent/local_env.md`), multi-core CPU  
**Architecture:** Single-host, SQLite, Tailscale mesh, no distributed consensus  

---

## 📋 Test Philosophy

The June-18 load test failure revealed that **3-node Byzantine distributed consensus cannot handle aggressive load under chaotic conditions**. Rather than fix the distributed model, the team pivoted to:

- ✅ **Single-host design** (Cybertronia) — no distributed consistency overhead
- ✅ **Local SQLite** — no Redis/Qdrant network round-trips
- ✅ **Stateless mesh** (Tailscale) — control plane only, no data plane
- ✅ **v1000-EXCALIBUR-A** — purpose-built for this architecture

**New test strategy validates what was actually built, not what failed in June.**

---

## 🎯 Test Objectives

| Objective | Old Target (Failed) | New Target (Local) | Success Criteria |
|-----------|-------------------|-------------------|------------------|
| **Load capacity** | 5000 RPS distributed | 3000 RPS single-host | p95 latency < 150ms |
| **Consistency** | 3/3 node consensus | SQLite transactions | ACID compliance 100% |
| **Memory** | 2.5-3.5GB per node | 8GB total (per spec) | Stable, no runaway growth |
| **Compression** | 416x TOON ratio | Symbolect validation | Context < 5% overhead |
| **Mesh routing** | Geographic failover (3 nodes) | Tailscale redundancy | <50ms mesh latency |
| **Cascade** | Byzantine graceful degrade | Watchdog auto-restart | <5s recovery on crash |

---

## 📊 Three-Phase Test Plan

### Phase 1: Baseline Profiling (10 min)

**Goal:** Establish healthy baselines before stress.

**Tests:**
1. ✅ **System health check**
   - SQLite connectivity
   - Tailscale mesh status
   - Process monitoring (watchdog alive)
   - Memory snapshot
   
2. ✅ **Single-request latency**
   - Routing decision (local agent)
   - Knowledge lookup (SQLite L1 read)
   - Compression encode/decode
   - Expected: all < 50ms

3. ✅ **Steady-state throughput**
   - 100 RPS sustained for 1 min
   - Monitor: memory, CPU, latency percentiles (p50/p95/p99)
   - Expected: p95 < 50ms, zero errors

---

### Phase 2: Load Ramp & Sustained (20 min)

**Goal:** Find the breaking point; validate stable operation under target load.

**Tests:**

1. 🔵 **Baseline ramp** (100 → 500 RPS, 2-min steps)
   ```
   100 RPS × 2 min → 200 RPS × 2 min → 300 RPS × 2 min → 500 RPS × 2 min
   ```
   - Track: p95, p99, error rate, CPU, memory
   - Expected: linear latency growth, no errors

2. 🟡 **Sustained load** (1000 RPS × 5 min)
   - This is the v1000-EXCALIBUR-A design target
   - Monitor memory for leaks
   - Expected: p95 < 100ms, < 0.1% errors

3. 🔴 **Spike test** (burst to 2000 RPS × 30 sec)
   - Sudden 2x load increase
   - Watchdog should NOT auto-restart
   - Expected: latency spike < 200ms, recovery < 10 sec after load drops

4. ⚫ **Exhaustion point** (3000 RPS until failure)
   - Find where system degrades (queue backlog, timeout)
   - Note: threshold for operational limits documentation
   - Expected: graceful queue buildup, no crash

---

### Phase 3: Graceful Degradation (10 min)

**Goal:** Validate that failure modes are safe (not Byzantine chaos, but expected behaviors).

**Tests:**

1. **SQLite write contention**
   - Simulate concurrent writes from multiple agents
   - Expected: locks held < 10ms, no deadlock

2. **Memory pressure**
   - Fill memory to 90% (synthetic load)
   - Watchdog should NOT crash; should shed load gracefully
   - Expected: request timeouts, no OOM crash

3. **Tailscale mesh latency spike**
   - Simulate high mesh latency (add 500ms synthetic delay)
   - Verify routing still works (fallback to local)
   - Expected: requests succeed with degraded latency

4. **Process restart cycle**
   - Kill main process intentionally
   - Watchdog should detect and restart within 5 sec
   - Verify state recovery (SQLite should be clean)
   - Expected: automatic restart, zero data loss

---

## ✅ Success Criteria

### Tier 1: Must Pass (Production Ready)
```
✅ Phase 1: All baselines healthy
✅ Phase 2 sustained (1000 RPS, 5 min): p95 < 100ms, error rate < 0.1%
✅ Phase 3 restart: < 5 sec recovery, zero data loss
✅ Memory: stable (no growth > 50MB over 10 min)
✅ SQLite: ACID verified, zero transaction rollbacks under load
```

### Tier 2: Should Pass (Recommended)
```
✅ Phase 2 spike (2000 RPS): recovers cleanly in < 10 sec
✅ Phase 3 memory pressure: graceful timeout, no crash
✅ Phase 3 mesh latency: requests still succeed
```

### Tier 3: Nice to Have (Optimizations)
```
✅ Phase 2 exhaustion: documented threshold (e.g., "stable to 2500 RPS")
✅ Compression: Symbolect overhead < 2% latency impact
✅ Watchdog: detects degradation and logs alert before user sees it
```

---

## 🔧 Test Suite Implementation

**File:** `local_load_testing_suite.py`

**Modules:**
1. `SystemHealthCheck` — SQLite, Tailscale, process monitoring
2. `LatencyProfiler` — baseline single-request latency
3. `LoadGenerator` — async load generator (adjustable RPS)
4. `MemoryMonitor` — track memory growth
5. `GracefulDegradationTester` — simulated failures + recovery
6. `ReportGenerator` — JSON + markdown output

**Command:**
```bash
cd C:\Users\vizio\CAMELOT_OS
python local_load_testing_suite.py --phase 1,2,3 --output test_results_local_/
```

---

## 📈 Expected Results (Healthy System)

```
[Phase 1 - Baseline]
  ✅ SQLite latency: 12ms
  ✅ Routing latency: 8ms
  ✅ Compression: 3ms
  ✅ Memory baseline: 512MB

[Phase 2 - Load Ramp]
  100 RPS  → p95=45ms
  200 RPS  → p95=58ms
  300 RPS  → p95=72ms
  500 RPS  → p95=89ms

[Phase 2 - Sustained 1000 RPS × 5 min]
  ✅ p95 latency: 98ms (< 100ms target)
  ✅ Error rate: 0.03% (< 0.1% target)
  ✅ Memory growth: +12MB (stable)

[Phase 2 - Spike 2000 RPS × 30 sec]
  ✅ Peak latency: 185ms
  ✅ Recovery time: 8 sec
  ✅ No crash, no restart

[Phase 3 - Graceful Degradation]
  ✅ SQLite write contention: no deadlock
  ✅ Memory pressure at 90%: graceful timeout
  ✅ Mesh latency spike: requests succeed
  ✅ Process restart: 4.2 sec, zero data loss

[Overall Verdict]
  🟢 PRODUCTION_READY
```

---

## 📁 Output Files

```
test_results_local_YYYYMMDD_HHMMSS/
├── phase1_baseline.json          # Single-request latencies
├── phase2_load_ramp.json         # RPS scaling data
├── phase2_sustained.json         # 1000 RPS × 5 min metrics
├── phase2_spike.json             # 2000 RPS burst metrics
├── phase3_degradation.json       # Failure mode tests
├── memory_profile.txt            # Memory growth over time
├── cpu_profile.txt               # CPU usage timeline
├── error_log.txt                 # Any errors encountered
├── SUMMARY.md                    # Executive summary
└── RECOMMENDATIONS.md            # Operational limits & tuning
```

---

## ⏱️ Timeline

```
Start → Phase 1 baseline (10 min)
      → Phase 2 load ramp (20 min)
      → Phase 3 degradation (10 min)
      → Report generation (2 min)
      ────────────────────────────
      Total: ~42 minutes
```

---

## 🚀 Next Steps

**When Phase 1 completes:**
- Verify SQLite is working (check `test_results_local_*/phase1_baseline.json`)
- Check Tailscale mesh status
- Monitor memory — should be < 800MB

**When Phase 2 completes:**
- If p95 < 100ms @ 1000 RPS → System is production-ready
- If p95 > 100ms @ 1000 RPS → Diagnose bottleneck (SQLite lock contention? compression? routing?)

**When Phase 3 completes:**
- Verify all graceful degradation modes pass
- Document operational limits based on exhaustion test
- Proceed to Phase H (Adaptive Learning) if all tiers pass

---

## 📊 Comparison: Old vs. New Test Strategy

| Aspect | Old (3-Node, Failed) | New (Local, Designed) |
|--------|---------------------|----------------------|
| **Architecture** | Distributed consensus | Single-host SQLite |
| **Network** | 3-node PBFT protocol | Tailscale mesh (control only) |
| **Storage** | Redis + Qdrant | Local SQLite |
| **Failure mode** | Byzantine chaos | Graceful degradation |
| **Target RPS** | 5000 (distributed) | 1000-3000 (single-host) |
| **Consensus** | 3/3 agreement | ACID transactions |
| **Test approach** | Chaos engineering | Load ramping + degradation |

---

**Test Suite Status: READY FOR EXECUTION**

Run it now → analyze results → document operational limits → proceed to Phase H.

