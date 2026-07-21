# 🧪 CAMELOT-OS Load Testing & Chaos Engineering Quick Start

**Estimated Time**: 7 days (full suite)  
**Purpose**: Validate production readiness, identify breaking points, ensure Byzantine safety

---

## 🚀 Quick Start (5 minutes)

### 1. Verify Cluster is Healthy

```bash
# Check all 3 nodes
for ip in 192.168.1.{10,11,12}; do
  echo "Node: $ip"
  curl -s http://$ip:8443/health | jq .status
done

# Expected output: "healthy" on all 3 nodes
```

### 2. Run Full Test Suite

```bash
cd /path/to/CAMELOT_OS

# Make script executable
chmod +x run_tests.sh

# Run all tests (will take ~30 minutes first time)
./run_tests.sh

# Results saved to: test_results_YYYYMMDD_HHMMSS/
```

### 3. Review Results

```bash
# Open results directory
cd test_results_YYYYMMDD_HHMMSS/

# Read summary
cat SUMMARY.md

# Check detailed logs
cat load_test.log
cat chaos_test.log

# View metrics
head -50 metrics_192.168.1.10.txt
```

---

## 📊 What Gets Tested

### Load Testing
- ✅ Routing requests (100 → 5000 RPS)
- ✅ Consensus proposals (100 → 500 RPS)
- ✅ Knowledge sync (500 → 2000 RPS)
- ✅ Latency, throughput, errors
- ✅ Memory/CPU stability

### Chaos Engineering
- ✅ Single node failure (recovery time)
- ✅ Network partition (quorum behavior)
- ✅ Byzantine attacks (rejection/safety)
- ✅ Cascading failures (graceful degradation)
- ✅ Agent degradation (load adaptation)
- ✅ Memory pressure (eviction policy)

---

## ⏱️ Time Breakdown

### Day 1: Load Testing
```
Morning (2 hours):
  - Baseline ramp-up (100 → 1000 RPS)
  - Sustained load test (1 hour at 1000 RPS)
  
Afternoon (3 hours):
  - Spike test (burst to 5000 RPS)
  - Peak sustained load (2 hours at 2000 RPS)
```

### Days 2-4: Chaos Engineering
```
Day 2 (3 hours):
  - Single node failure
  - Network partition
  - Cascading failures

Day 3 (2 hours):
  - Byzantine attack
  - Agent degradation
  - Memory pressure

Day 4 (3 hours):
  - Combined chaos scenarios
  - Stress under multiple failures
```

### Days 5-7: Validation & Documentation
```
Day 5 (4 hours):
  - Sustained peak load (2000 RPS, 4 hours)
  - Continuous monitoring
  
Day 6 (3 hours):
  - Repeat critical tests
  - Verify reproducibility
  
Day 7 (4 hours):
  - Generate final report
  - Document breaking points
  - Create operational guidelines
```

---

## 🎯 Success Criteria

### Load Testing ✅
```
Baseline (100-1000 RPS):
  ✓ p95 latency < 50ms
  ✓ p99 latency < 100ms
  ✓ Error rate < 0.1%
  ✓ CPU < 50%
  ✓ Memory stable

Sustained (1000 RPS, 1 hour):
  ✓ p95 latency < 100ms
  ✓ Error rate < 0.5%
  ✓ Memory no growth
  ✓ No crashes

Peak (5000 RPS burst):
  ✓ Recovery < 30 seconds
  ✓ No data loss
  ✓ No cascading failures
```

### Chaos Engineering ✅
```
Single Node Failure:
  ✓ Detected in < 5 seconds
  ✓ Cluster continues with 2/3
  ✓ Recovery < 30 seconds
  ✓ Zero data loss

Network Partition:
  ✓ Minority stops (safe)
  ✓ Majority continues
  ✓ Healing < 10 seconds
  ✓ Consistency maintained

Byzantine Attack:
  ✓ Attack rejected
  ✓ System unaffected
  ✓ Normal operation continues

Cascading Failure:
  ✓ Graceful degradation
  ✓ Data preserved
  ✓ Recovery possible
```

---

## 📝 Manual Testing (If Needed)

### Individual Load Test

```bash
# Only load testing (skip chaos)
python3 load_testing_suite.py

# This will:
# - Baseline ramp (100-1000 RPS, 5 min)
# - Sustained load (1000 RPS, 1 hour)
# - Spike test (5000 RPS, 30 sec)
# - Consensus load (100 RPS, 10 min)
# - Sync load (500 RPS, 10 min)
# - Mixed load (2000 RPS, 30 min)
```

### Individual Chaos Test

```bash
# Only chaos engineering (skip load)
python3 chaos_engineer.py

# This will:
# - Single node failure
# - Network partition
# - Byzantine attack
# - Cascading failure
```

---

## 🔍 Monitoring During Tests

### Open 4 Terminal Windows

**Terminal 1: Consensus**
```bash
ssh root@192.168.1.10
journalctl -u camelot-consensus -f | grep -E "proposal|latency|agreement"
```

**Terminal 2: Agents**
```bash
watch -n 2 'curl -s http://192.168.1.10:8400/agents/status | jq "{total: (.agents | length), healthy: (.agents | map(select(.healthy==true)) | length)}"'
```

**Terminal 3: Sync Status**
```bash
watch -n 5 'curl -s http://192.168.1.10:6379/knight/sync-status | jq "{lag_ms: .replication_lag_ms, conflicts: .conflicts_detected}"'
```

**Terminal 4: System Resources**
```bash
watch -n 2 'for ip in 192.168.1.{10,11,12}; do echo "Node $ip:"; ssh root@$ip "free -h && top -bn1 | grep Cpu"; done'
```

---

## 📊 Grafana Dashboards

Keep these open during testing:

1. **System Overview** (CPU, Memory, Network)
   - http://localhost:3000/d/system

2. **Consensus Performance** (Latency, Agreement, Proposals)
   - http://localhost:3000/d/consensus

3. **Agent Network** (Load Distribution, Routing Success)
   - http://localhost:3000/d/agents

4. **Knowledge Sync** (Replication Lag, Conflicts, Consistency)
   - http://localhost:3000/d/sync

5. **Error Rates** (By Service, Trending)
   - http://localhost:3000/d/errors

---

## 🛠️ Troubleshooting

### Load Test Fails with Connection Errors

```bash
# Verify node is reachable
ping 192.168.1.10

# Verify ports are open
curl -v http://192.168.1.10:8400/agents/status

# Check service status
ssh root@192.168.1.10 systemctl status camelot-agents
```

### Chaos Test Fails to Kill Node

```bash
# Verify SSH access works
ssh root@192.168.1.11 "systemctl status camelot-consensus"

# Try manual stop
ssh root@192.168.1.11 "sudo systemctl stop camelot-consensus"

# Check for errors
ssh root@192.168.1.11 "journalctl -u camelot-consensus -n 50"
```

### Results Directory Not Created

```bash
# Verify write permissions
ls -la /tmp/

# Create manually
mkdir -p test_results_$(date +%Y%m%d_%H%M%S)

# Run tests with explicit path
./run_tests.sh > test_results_$(date +%Y%m%d_%H%M%S)/output.log 2>&1
```

---

## 📈 Expected Results

### Load Test Summary
```
┌─────────────────────────────────────────────┐
│ Phase          │ RPS    │ p95ms  │ Success │
├─────────────────────────────────────────────┤
│ Baseline       │ 500    │ 45     │ 99.9%   │
│ Sustained      │ 1000   │ 85     │ 99.8%   │
│ Spike          │ 5000   │ 150    │ 98%     │
│ Consensus      │ 100    │ 55     │ 99.9%   │
│ Sync           │ 500    │ 40     │ 99.7%   │
│ Mixed          │ 2000   │ 110    │ 99%     │
└─────────────────────────────────────────────┘
```

### Chaos Test Results
```
✅ Single Node Failure: PASS
   - Detection: 3 seconds
   - Recovery: 25 seconds
   - Data Loss: 0 items

✅ Network Partition: PASS
   - Minority stops: YES
   - Majority continues: YES
   - Healing: 8 seconds

✅ Byzantine Attack: PASS
   - Attacks rejected: 4/4
   - System impact: None

✅ Cascading Failure: PASS
   - Graceful degradation: YES
   - Data preserved: YES
```

---

## 📋 After Testing

### 1. Review Report
```bash
cat test_results_YYYYMMDD_HHMMSS/SUMMARY.md
```

### 2. Document Findings
```bash
# Create operational guidelines
# Based on actual breaking points found
# E.g., "Safe to run 2000 RPS sustained"
```

### 3. Address Issues
```bash
# If tests found problems:
# 1. Create GitHub issues
# 2. Schedule fixes
# 3. Re-test after fixes
```

### 4. Proceed to Phase H
```bash
# Once all tests pass:
# - System is production-ready
# - Can proceed to Phase H (Adaptive Learning)
# - Can begin frontend development
```

---

## 🎯 Next Commands After Completion

```bash
# 1. View detailed results
head -100 test_results_*/load_test.log
head -100 test_results_*/chaos_test.log

# 2. Check for any warnings
grep -i "warning\|error\|fail" test_results_*/

# 3. Extract metrics
cat test_results_*/metrics_192.168.1.10.txt | grep "camelot_"

# 4. Generate comparison
# (if running tests multiple times)
diff test_results_1/SUMMARY.md test_results_2/SUMMARY.md
```

---

## ✅ Completion Checklist

After all tests complete:

- [ ] Load testing passed (latency < 100ms p95)
- [ ] Chaos tests passed (single failure < 30s recovery)
- [ ] Zero data loss confirmed
- [ ] No cascading failures observed
- [ ] Results documented
- [ ] Operational guidelines created
- [ ] Team trained on limits
- [ ] Ready for Phase H (Adaptive Learning)

---

**Ready to begin?** Run:
```bash
cd /path/to/CAMELOT_OS && ./run_tests.sh
```

**Questions?** Check:
- LOAD_TESTING_PLAN.md (detailed testing strategy)
- BARE_METAL_DEPLOYMENT.md (operations manual)
- HELP.md (quick command reference)

