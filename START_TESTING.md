# 🚀 START CAMELOT-OS TESTING NOW

**Generated**: 2026-06-18  
**Status**: Ready to Execute  
**Duration**: 7 days (or ~30 min for quick validation)

---

## ⚡ IMMEDIATE ACTIONS (Next 5 Minutes)

### Step 1: Verify Prerequisites

Open terminal and run:

```bash
# 1. Go to project directory
cd /path/to/CAMELOT_OS

# 2. Verify scripts exist
ls -la load_testing_suite.py chaos_engineer.py run_tests.sh

# 3. Make scripts executable
chmod +x run_tests.sh load_testing_suite.py chaos_engineer.py

# 4. Verify Python3 installed
python3 --version

# 5. Install required packages (if needed)
pip3 install aiohttp numpy
```

### Step 2: Verify Cluster is Reachable

```bash
# Test SSH access to each node
for ip in 192.168.1.{10,11,12}; do
  echo "Testing $ip..."
  ssh root@$ip "systemctl status camelot-consensus" | grep Active
done

# Expected: Active: active (running) on all 3 nodes
```

### Step 3: Verify Cluster Health

```bash
# Quick health check
for ip in 192.168.1.{10,11,12}; do
  echo "Node $ip:"
  curl -s http://$ip:8443/health | jq '.status, .nodes_in_agreement'
done

# Expected:
# Node 192.168.1.10:
# "healthy"
# 3
# (repeat for other nodes)
```

---

## 🎯 OPTION A: Full Test Suite (RECOMMENDED)

### Execute Full Test Suite

```bash
# From CAMELOT_OS directory
./run_tests.sh

# This will:
# ✅ Verify cluster health
# ✅ Run load tests (30 min)
# ✅ Run chaos tests (45 min)
# ✅ Generate detailed report
# ✅ Save results to: test_results_YYYYMMDD_HHMMSS/
```

**What happens during execution:**
- Terminal 1: Test progress (color-coded)
- Monitoring: See live metrics in Grafana (open in browser)
- Results: Real-time logs in test_results/ directory

### Monitor in Real-Time (4 Terminal Windows)

**Window 1: Consensus Health**
```bash
watch -n 2 'curl -s http://192.168.1.10:8443/health | jq "{status: .status, agreement: .nodes_in_agreement, latency: .latency_ms}"'
```

**Window 2: Agent Network**
```bash
watch -n 3 'curl -s http://192.168.1.10:8400/agents/status | jq "{agents: (.agents | length), healthy: (.agents | map(select(.healthy==true)) | length)}"'
```

**Window 3: Knowledge Sync**
```bash
watch -n 5 'curl -s http://192.168.1.10:6379/knight/sync-status | jq "{lag_ms: .replication_lag_ms, conflicts: .conflicts_detected, consistency: .consistency_percent}"'
```

**Window 4: Grafana Dashboard**
```bash
# Open browser to:
http://localhost:3000
# Login: admin / admin123
# View: System Overview dashboard
```

---

## 🎯 OPTION B: Load Testing Only (1 Hour)

If you want just load testing first:

```bash
python3 load_testing_suite.py

# Runs:
# - Baseline ramp (100-1000 RPS, 5 min)
# - Sustained load (1000 RPS, 1 hour)
# - Spike test (5000 RPS, 30 sec)
# - Consensus load (100 RPS, 10 min)
# - Sync load (500 RPS, 10 min)
# - Mixed load (2000 RPS, 30 min)

# Output:
# - Console: Live metrics
# - File: /tmp/load_test_report_*.json
```

---

## 🎯 OPTION C: Chaos Engineering Only (1 Hour)

If you want just chaos tests:

```bash
python3 chaos_engineer.py

# Runs:
# - Single node failure
# - Network partition
# - Byzantine attack
# - Cascading failure

# Output:
# - Console: Test progress
# - File: /tmp/chaos_test_report_*.json
```

---

## 📊 Understanding the Output

### Load Testing Results

```
📊 Running Baseline Ramp-Up...
   Target RPS: 100
   Duration: 300s
   Load Type: routing

   ✅ Results:
      RPS: 98 (target: 100)
      Latency: p95=45.2ms, p99=62.1ms
      Success Rate: 99.9%
      Consensus: 100%
      CPU: 35% | Memory: 60%
```

### Chaos Testing Results

```
🔴 TEST: Single Node Failure
   Action: Kill camelot-consensus on Node 2
   Expected: Cluster continues with 2/3, no data loss

   [1/5] Killing Node 2 consensus...
   [2/5] Verifying Node 1 detects failure...
      ✅ Node 1 detected failure: 2/3 agreement
   [3/5] Verifying no data loss...
   [4/5] Restarting Node 2 consensus...
   [5/5] Verifying recovery to 3/3...
      ✅ Recovery successful: 3/3 agreement

   Final Verdict: PASS ✅
```

---

## 📈 Success Criteria (During Test)

### Watch For ✅

```
✅ Load Testing:
   - Latency stays < 100ms p95
   - Success rate > 99%
   - Memory doesn't spike
   - No crashes

✅ Chaos Testing:
   - Node failures detected < 5 sec
   - Recovery < 30 seconds
   - System continues during failure
   - Data consistency maintained
```

### Watch For ❌

```
❌ If you see:
   - Latency > 200ms sustained
   - Error rate > 5%
   - Memory growing continuously
   - Crash/restart of services
   - Consensus broken (agreement < 2/3)
```

Then stop tests and investigate.

---

## 🔍 After Tests Complete

### View Results

```bash
# Go to results directory
cd test_results_YYYYMMDD_HHMMSS/

# Read summary
cat SUMMARY.md

# Check detailed logs
cat load_test.log
cat chaos_test.log

# View raw metrics
head -100 metrics_192.168.1.10.txt
```

### Generate Final Report

The test suite automatically creates:
- `SUMMARY.md` - Executive summary
- `load_test.log` - Detailed load results
- `chaos_test.log` - Detailed chaos results
- `metrics_*.txt` - Raw metrics from each node
- `output.log` - Full execution log

---

## 🎬 READY? START HERE

Choose your option:

### OPTION A (Full - RECOMMENDED)
```bash
cd /path/to/CAMELOT_OS && ./run_tests.sh
```

### OPTION B (Load Only)
```bash
cd /path/to/CAMELOT_OS && python3 load_testing_suite.py
```

### OPTION C (Chaos Only)
```bash
cd /path/to/CAMELOT_OS && python3 chaos_engineer.py
```

---

## ⏱️ Timeline

**If you start now:**

### Quick Validation (30 minutes)
- Load test baseline → sustained → spike
- View results
- Verdict: System ready? YES/NO

### Full Validation (7 days)
- Day 1: Load testing
- Days 2-4: Chaos scenarios
- Days 5-7: Edge cases + documentation

---

## 💬 During Testing

**You can:**
- Monitor in Grafana (http://localhost:3000)
- Watch real-time logs in terminals
- Check test_results/ directory for live progress
- Review metrics as they come in

**Do NOT:**
- Kill the test process (let it complete)
- Restart cluster services (test needs to)
- Make changes to code (during testing)

---

## 📋 After Testing Completes

Regardless of results, you'll have:

1. **Performance Baselines** - p95 latency, RPS capacity, recovery times
2. **Resilience Report** - Byzantine safety validated, failure handling verified
3. **Operational Guidelines** - Safe operating parameters, alert thresholds
4. **Next Steps** - Ready for Phase H or issues to fix first

---

## 🚀 EXECUTE NOW

```bash
# Copy-paste this:
cd /path/to/CAMELOT_OS && ./run_tests.sh
```

**Status**: Ready to begin ✅  
**Time to start**: < 1 minute  
**Expected completion**: 30 min - 7 days (depending on depth)

---

**Questions during testing?**
- Check: TESTING_QUICKSTART.md
- Check: LOAD_TESTING_PLAN.md
- Check: BARE_METAL_DEPLOYMENT.md

**Problems?**
- Check test_results_*/output.log for errors
- Verify cluster health: `curl http://192.168.1.10:8443/health`
- Check SSH access: `ssh root@192.168.1.10 systemctl status camelot-consensus`

---

**Let's begin! 🔥**

```
🚀 CAMELOT-OS Load Testing & Chaos Engineering
🎯 Validating Production Readiness
📊 Starting Now...
```

