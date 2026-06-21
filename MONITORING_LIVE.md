# 🔴 LIVE TEST MONITORING - 2026-06-18 17:00+

Tests are RUNNING now. Monitor in real-time with these commands.

---

## 📊 OPEN THESE 4 WINDOWS SIDE-BY-SIDE

### Window 1: Consensus Health (Refresh every 2s)
```bash
watch -n 2 'curl -s http://192.168.1.10:8443/health | jq "{status: .status, role: .role, agreement: .nodes_in_agreement, latency_ms: .latency_ms, proposals: .proposals_total}"'
```

**Watch for:**
- `status`: "healthy" ✅
- `agreement`: 3 (means 3/3 nodes)
- `latency_ms`: < 100ms
- `proposals`: increasing (shows activity)

---

### Window 2: Agent Network (Refresh every 3s)
```bash
watch -n 3 'curl -s http://192.168.1.10:8400/agents/status | jq "{total: (.agents | length), healthy: (.agents | map(select(.healthy==true)) | length), avg_load: (.agents | map(.load) | add / length | round), avg_confidence: (.agents | map(.confidence) | add / length | round)}"'
```

**Watch for:**
- `total`: 24
- `healthy`: 24
- `avg_load`: 40-60% (during tests)
- `avg_confidence`: 0.85+

---

### Window 3: Knowledge Sync (Refresh every 5s)
```bash
watch -n 5 'curl -s http://192.168.1.10:6379/knight/sync-status | jq "{sync_health: .sync_health, lag_ms: .replication_lag_ms, conflicts: .conflicts_detected, consistency: .consistency_percent}"'
```

**Watch for:**
- `sync_health`: "excellent" or "healthy"
- `lag_ms`: < 200ms
- `conflicts`: 0
- `consistency`: 99%+

---

### Window 4: Test Progress Log (Live)
```bash
tail -f test_results_*/output.log
```

**Watch for:**
- Progress messages
- ✓ markers (passed checks)
- Any ✗ or error messages

---

## 🎯 EXPECTED SEQUENCE

### Phase 1: Pre-flight (0-2 min)
```
[CHECK] Verifying cluster health...
  Node 192.168.1.10: ✓
  Node 192.168.1.11: ✓
  Node 192.168.1.12: ✓
```

### Phase 2: Load Testing (2-25 min)
```
[TEST] Starting load testing...
  Running routing load test (100-1000 RPS)...
  
📊 Running Baseline Ramp-Up...
   RPS: 500 (target: 100)
   Latency: p95=45.2ms, p99=62.1ms
   Success Rate: 99.9%

📊 Running Sustained Load...
   RPS: 1000 (target: 1000)
   Latency: p95=85.1ms, p99=110.5ms
   Success Rate: 99.8%

📊 Running Spike Test...
   RPS: 5000 (target: 5000)
   Latency: p95=150.2ms, p99=180.1ms
   Success Rate: 98%
```

### Phase 3: Chaos Engineering (25-35 min)
```
[TEST] Starting chaos engineering...

🔴 TEST: Single Node Failure
   [1/5] Killing Node 2 consensus...
   [2/5] Verifying Node 1 detects failure...
      ✅ Node 1 detected failure: 2/3 agreement
   [3/5] Verifying no data loss...
   [4/5] Restarting Node 2 consensus...
   [5/5] Verifying recovery to 3/3...
      ✅ Recovery successful: 3/3 agreement
   Final Verdict: PASS ✅

🔴 TEST: Network Partition
   ...similar progression...
   Final Verdict: PASS ✅

🔴 TEST: Byzantine Attack
   ...similar progression...
   Final Verdict: PASS ✅

🔴 TEST: Cascading Failure
   ...similar progression...
   Final Verdict: PASS ✅
```

### Phase 4: Report (35-38 min)
```
[REPORT] Generating summary...
  ✓ Summary report generated

==============================================================
📋 TEST SUITE COMPLETE
==============================================================
✅ All tests passed
Results: test_results_20260618_170000/
```

---

## ⚠️ RED FLAGS TO WATCH FOR

**STOP and alert me if you see:**

```
❌ Consensus agreement drops below 2
   (means only 1 node, system unsafe)

❌ Latency p95 > 200ms sustained
   (exceeds acceptable threshold)

❌ Error rate > 5%
   (too many failures)

❌ Agent count < 20/24
   (agents failing)

❌ Memory growing continuously
   (memory leak)

❌ "FAIL" verdict on any test
   (chaos test failed)

❌ Crash/restart of services
   (unexpected failure)
```

---

## 🟢 GREEN FLAGS (You Should See These)

```
✅ Agreement stays 3/3
✅ Latency < 100ms most of the time
✅ Success rate > 99%
✅ All agents healthy
✅ No error messages
✅ Memory stable
✅ All tests PASS
```

---

## 📈 GRAFANA DASHBOARD (Optional Visual Monitoring)

Open in browser:
```
http://localhost:3000
Login: admin / admin123
```

View dashboards:
- **System Overview** - CPU, Memory, Network
- **Consensus Performance** - Latency, Agreement
- **Agent Network** - Load distribution
- **Knowledge Sync** - Replication status

---

## ⏱️ ESTIMATED TIMELINE

```
00:00 - Tests start
05:00 - Load testing begins
25:00 - Chaos engineering begins
35:00 - Report generation
38:00 - ✅ COMPLETE

(Times are approximate)
```

---

## 📊 CHECKING RESULTS DIRECTORY

While tests run, check what's being created:

```bash
# See results directory
ls -la test_results_*/

# Check file sizes growing
watch -n 10 'du -sh test_results_*/'

# Tail the output log
tail -f test_results_*/output.log

# Check individual test logs
tail -f test_results_*/load_test.log
tail -f test_results_*/chaos_test.log
```

---

## 💬 IF SOMETHING GOES WRONG

### Service stopped unexpectedly?
```bash
ssh root@192.168.1.10 systemctl status camelot-consensus
```

### Network issue?
```bash
ping 192.168.1.10
ssh root@192.168.1.10 "echo OK"
```

### Test script error?
```bash
# Check the output log
cat test_results_*/output.log | tail -50

# Check if processes are running
ps aux | grep python
```

---

## 📞 NEXT STEPS

**When tests complete (~40 minutes from start):**

1. Check the verdict in terminal (PASS/FAIL/WARNINGS)
2. Review results directory:
   ```bash
   cat test_results_*/SUMMARY.md
   ```
3. Come back here with results
4. We'll analyze findings together

---

## ✅ STATUS NOW

🔴 **TESTS RUNNING**
- Execution in progress
- Monitor windows open
- Expected completion: ~40 minutes
- Check back when done or if issues arise

---

**You're all set! Monitor the 4 windows and come back when tests complete.** 📊

