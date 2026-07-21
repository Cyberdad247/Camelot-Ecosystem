# 🚀 RUN TESTS NOW - Exact Commands

**Your 3-node cluster is ready.**  
**Health check passed.**  
**Ready to validate.**

---

## ⚡ EXECUTE THIS ON YOUR LOCAL MACHINE

Copy and paste this command exactly:

```bash
cd /path/to/CAMELOT_OS && chmod +x run_tests.sh && ./run_tests.sh
```

Replace `/path/to/CAMELOT_OS` with your actual path. For example:

```bash
# Example 1:
cd ~/CAMELOT_OS && chmod +x run_tests.sh && ./run_tests.sh

# Example 2:
cd /home/user/projects/CAMELOT_OS && chmod +x run_tests.sh && ./run_tests.sh

# Example 3 (Windows with Git Bash):
cd C:/Users/vizio/CAMELOT_OS && chmod +x run_tests.sh && ./run_tests.sh
```

---

## 📊 What Happens (Next 30 Minutes)

### Phase 1: Pre-flight (1 min)
```
✓ Verify cluster health
✓ Verify SSH access
✓ Create results directory
```

### Phase 2: Load Testing (20 min)
```
✓ Baseline ramp (100 RPS → 1000 RPS)
✓ Sustained load (1000 RPS, 1 hour)
✓ Spike test (burst to 5000 RPS)
✓ Consensus load (100 RPS)
✓ Sync load (500 RPS)
✓ Mixed load (2000 RPS)
```

### Phase 3: Chaos Engineering (5 min)
```
✓ Single node failure
✓ Network partition
✓ Byzantine attack
✓ Cascading failure
```

### Phase 4: Report (2 min)
```
✓ Generate summary
✓ Save detailed results
✓ Print verdict
```

---

## 🖥️ WHAT YOU'LL SEE

### Terminal Output (Color-Coded)

```
==============================================================
🚀 CAMELOT-OS TEST SUITE
==============================================================

[CHECK] Verifying cluster health...
  Node 192.168.1.10: ✓
  Node 192.168.1.11: ✓
  Node 192.168.1.12: ✓

[COLLECT] Baseline metrics...
  Collecting metrics from 192.168.1.10...
  Collecting metrics from 192.168.1.11...
  Collecting metrics from 192.168.1.12...
  ✓ Metrics collected

[TEST] Starting load testing...
  Running routing load test (100-1000 RPS)...
  ✓ Load testing complete

[TEST] Starting chaos engineering...
  Running chaos scenarios...
  ✓ Chaos testing complete

[REPORT] Generating summary...
  ✓ Summary report generated

==============================================================
📋 TEST SUITE COMPLETE
==============================================================
✅ All tests passed
Results: test_results_20260618_170000/
```

---

## 📈 MONITOR IN REAL-TIME (Open 4 Terminal Windows)

### Window 1: Consensus Health

```bash
watch -n 2 'curl -s http://192.168.1.10:8443/health | jq .'
```

Expected output:
```json
{
  "status": "healthy",
  "role": "leader",
  "cluster_size": 3,
  "nodes_in_agreement": 3,
  "latency_ms": 45,
  "proposals_total": 1247
}
```

### Window 2: Agent Network

```bash
watch -n 3 'curl -s http://192.168.1.10:8400/agents/status | jq "{total: (.agents | length), healthy: (.agents | map(select(.healthy==true)) | length), avg_confidence: (.agents | map(.confidence) | add / length | round)}"'
```

Expected output:
```json
{
  "total": 24,
  "healthy": 24,
  "avg_confidence": 0.91
}
```

### Window 3: Knowledge Sync

```bash
watch -n 5 'curl -s http://192.168.1.10:6379/knight/sync-status | jq "{lag_ms: .replication_lag_ms, conflicts: .conflicts_detected, consistency: .consistency_percent}"'
```

Expected output:
```json
{
  "lag_ms": 85,
  "conflicts": 0,
  "consistency": 99.9
}
```

### Window 4: Grafana Dashboard

```bash
# Open in browser
http://localhost:3000
# Login: admin / admin123
# View: System Overview dashboard
```

---

## ✅ SUCCESS CRITERIA

### During Testing - You Should See ✅

```
✅ Latency stays low (< 100ms p95)
✅ Success rate > 99%
✅ All 3 nodes in agreement
✅ All 24 agents healthy
✅ No error messages
✅ Memory stable
✅ CPU < 50%
```

### During Testing - Red Flags ❌

```
❌ Latency > 200ms
❌ Error rate > 5%
❌ Agreement < 2/3
❌ Agents < 20/24
❌ Memory growth
❌ Service crashes
```

If you see red flags, **let me know immediately** and we'll investigate.

---

## 📁 AFTER TESTS COMPLETE

Results will be saved in:
```
test_results_20260618_170000/
├── SUMMARY.md              # Executive summary
├── load_test.log          # Detailed load results
├── chaos_test.log         # Detailed chaos results
├── metrics_192.168.1.10.txt
├── metrics_192.168.1.11.txt
├── metrics_192.168.1.12.txt
└── output.log             # Full execution log
```

### Quick Review

```bash
# Go to results directory
cd test_results_20260618_170000/

# Read summary (2 minutes)
cat SUMMARY.md

# Check for issues
grep -i "error\|fail\|warning" *.log

# View key metrics
head -50 load_test.log
head -50 chaos_test.log
```

---

## 🎯 THEN WHAT?

**When tests complete:**

1. **If PASS ✅**
   - System is production-ready
   - Proceed to Phase H (Adaptive Learning)
   - Begin frontend development

2. **If FAIL ❌**
   - We investigate findings
   - Fix identified issues
   - Re-test to confirm

3. **If WARNINGS ⚠️**
   - Note operational limits
   - Document safe parameters
   - Monitor those metrics

---

## ⏱️ ESTIMATED TIME

- **Load Testing**: 20-30 minutes
- **Chaos Engineering**: 5-10 minutes  
- **Report Generation**: 2 minutes
- **Total**: ~45 minutes

**You can start now and check back in 1 hour.**

---

## 🚀 START COMMAND

**Copy and paste this:**

```bash
cd /path/to/CAMELOT_OS && chmod +x run_tests.sh && ./run_tests.sh
```

**Then open your 4 monitoring windows above.**

**Come back when complete and we'll analyze results together.**

---

## 📞 DURING TESTING

If you encounter issues:
- Check: `curl http://192.168.1.10:8443/health` (is cluster still healthy?)
- Check: `ssh root@192.168.1.10 systemctl status camelot-consensus` (are services running?)
- Check: `tail -f test_results_*/output.log` (what's the test reporting?)

**I'm here to help interpret results when you're done!** 📊

