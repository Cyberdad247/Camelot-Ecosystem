# CAMELOT-OS Load Testing & Chaos Engineering Plan

**Phase**: Validation & Hardening  
**Duration**: 1 week  
**Goal**: Prove system stability under 5000+ RPS, Byzantine conditions, and failure scenarios

---

## Executive Summary

This plan validates CAMELOT-OS production readiness through:
1. **Load Testing** (Scaling from 100 RPS → 5000+ RPS)
2. **Chaos Engineering** (Node failures, network partitions, Byzantine attacks)
3. **Consistency Verification** (Zero data loss under all conditions)
4. **Performance Validation** (Latency, throughput, recovery time)

---

## Part 1: Load Testing Architecture

### Load Generators (3 types)

#### Type 1: Routing Load (Consensus-Independent)
```
Target: /knight/decide endpoint
Volume: 1000 → 3000 RPS
Pattern: Distributed across 24 agents
Metric: Latency p95, success rate, agent load distribution
```

#### Type 2: Consensus Load (Agreement Required)
```
Target: /consensus/propose endpoint
Volume: 100 → 500 RPS
Pattern: Proposals requiring 3/3 agreement
Metric: Consensus latency, agreement rate, phase breakdown
```

#### Type 3: Knowledge Sync Load (L1→L2 Replication)
```
Target: /sync/{operation} endpoints
Volume: 500 → 2000 RPS
Pattern: Writes to L1, verify sync to L2
Metric: Replication lag, conflicts, consistency
```

### Load Test Phases

**Phase 1: Baseline (Ramp-up)**
- Start: 100 RPS (routing only)
- Increment: +200 RPS every 5 minutes
- Duration: 30 minutes total
- Measure: Latency, throughput, error rate
- **Success Criteria**: All metrics stay healthy

**Phase 2: Sustained Load (Steady State)**
- Target: 1000 RPS (consensus + routing + sync)
- Duration: 1 hour
- Measure: CPU/memory stability, no memory leaks, consistent latency
- **Success Criteria**: p95 latency < 100ms, CPU < 70%, memory stable

**Phase 3: Spike Test (Peak Load)**
- Target: 3000 RPS (burst to 5000 for 30s)
- Duration: 5 minutes total
- Measure: Recovery time, error handling, queue behavior
- **Success Criteria**: System recovers within 30 seconds

**Phase 4: Sustained Peak (Stress Test)**
- Target: 2000 RPS continuous
- Duration: 2 hours
- Measure: Endurance, thermal stability, graceful degradation
- **Success Criteria**: Zero crashes, recoverable errors only

---

## Part 2: Chaos Engineering Scenarios

### Scenario 1: Single Node Failure
```
Action: Kill camelot-consensus on Node 2
Expected: 
  - Node 1 detects failure (~5s)
  - Cluster continues with 2/3 consensus (minimum viable)
  - No data loss
  - Request processing continues
Recovery: systemctl start camelot-consensus on Node 2
Expected: Auto-rejoin, catch up, return to 3/3 agreement
Measure: Downtime, consistency, recovery time
```

### Scenario 2: Network Partition (Split Brain)
```
Action: Block network between Node 1 and Nodes 2-3
Expected:
  - Node 1: Detects partition, stops processing (safe)
  - Nodes 2-3: Form quorum, continue processing
  - No Byzantine decisions
Recovery: Restore network connectivity
Expected: Node 1 catches up, cluster reunites, consistency maintained
Measure: Partition handling, data reconciliation, healing time
```

### Scenario 3: Cascading Failure
```
Action: Kill Node 2 consensus, then Node 3 consensus (30s apart)
Expected:
  - After Node 2 failure: 2/3 quorum, continues
  - After Node 3 failure: 1/3 (minority), stops new proposals
  - Existing data preserved
Recovery: Restart both nodes
Expected: Quick recovery, no data loss
Measure: Graceful degradation, safety under partial failure
```

### Scenario 4: Byzantine Node (Slow Responder)
```
Action: Add 5s artificial delay to Node 2 consensus responses
Expected:
  - Leader detects slow node
  - Consensus still completes (uses fastest 2 of 3)
  - Latency increases but remains acceptable
Recovery: Remove delay
Expected: Latency returns to normal
Measure: Byzantine resilience, performance impact
```

### Scenario 5: Memory Pressure
```
Action: Reduce Redis maxmemory to 1GB (from default), generate writes
Expected:
  - L1 cache evicts using LRU policy
  - L1→L2 sync accelerates (backfill)
  - No data loss (L2 has everything)
  - Graceful degradation (L1 hit rate drops)
Recovery: Restore memory limit
Expected: Performance returns to baseline
Measure: Graceful degradation, eviction policy correctness
```

### Scenario 6: Byzantine Proposal Attack
```
Action: Send malformed consensus proposals (wrong format, huge size, negative values)
Expected:
  - Proposals rejected immediately
  - No Byzantine agreement
  - Error logged
  - System continues normally
Recovery: System stays operational
Measure: Input validation, attack resistance
```

### Scenario 7: Sync Lag Spike
```
Action: Artificially delay all L1→L2 sync operations (+500ms)
Expected:
  - L1 cache fills (may hit limits)
  - L1.5 vector consolidation stalls
  - L2 falls behind
  - Eventual consistency maintained
Recovery: Remove delay
Expected: Sync lag normalizes, backlog processes
Measure: Queue handling, consistency under lag
```

### Scenario 8: Agent Network Degradation
```
Action: Kill 8 agents (33% of network), then kill 8 more (66% total)
Expected:
  - Routing adapts to healthy agents only
  - Load shifts to remaining agents
  - No request loss (queued)
  - Latency increases but processing continues
Recovery: Restart agents
Expected: Smooth reintegration, load rebalancing
Measure: Agent failure resilience, load adaptation
```

---

## Part 3: Consistency Verification

### Data Consistency Tests (During All Scenarios)

**Test 1: Write Verification**
- Write N items to L1
- Read from L1 (should be fast)
- Wait 100ms, read from L1.5 (should exist)
- Wait 200ms, read from L2 (should exist and match)
- **Success**: 100% of writes visible at all layers by deadline

**Test 2: Cross-Node Consistency**
- Write to Node 1
- Immediately read from Nodes 2, 3
- **Success**: All nodes read same value (or "not yet synced" for L1-only)

**Test 3: Replication Under Failure**
- Write while Node 2 is down
- Verify Node 1 has data
- Restart Node 2
- Verify Node 2 received data (catch-up)
- **Success**: Zero data loss

**Test 4: Consensus Agreement**
- Propose decision on Node 1
- Verify all 3 nodes recorded same decision
- Verify decision persisted to L2
- **Success**: 3/3 agreement, persistence guaranteed

**Test 5: Byzantine Detection**
- Submit conflicting decisions from different nodes
- Verify only one "wins" per consensus round
- Verify losing proposals logged but not executed
- **Success**: No Byzantine divergence

---

## Part 4: Test Execution Plan

### Day 1: Baseline & Load Testing
```
Morning:
  ✓ Deploy monitoring (Prometheus, Grafana live)
  ✓ Run baseline (100-1000 RPS, 30 min)
  ✓ Document healthy metrics
  
Afternoon:
  ✓ Ramp-up test (1000-3000 RPS, 30 min)
  ✓ Identify breaking point
  ✓ Run sustained load (1000 RPS, 1 hour)
  ✓ Check for memory leaks, CPU stability
  
Evening:
  ✓ Spike test (burst to 5000 RPS)
  ✓ Measure recovery time
  ✓ Document results
```

### Day 2: Chaos - Single Points of Failure
```
Morning:
  ✓ Node failure scenario (kill Node 2)
  ✓ Monitor recovery (< 30s expected)
  ✓ Verify data consistency
  ✓ Restart node, verify rejoin
  
Afternoon:
  ✓ Network partition scenario
  ✓ Verify quorum still processes
  ✓ Verify minority stops (doesn't diverge)
  ✓ Heal partition, verify recovery
  
Evening:
  ✓ Cascading failure (Node 2, then Node 3)
  ✓ Verify graceful degradation
  ✓ Verify data preservation
  ✓ Restart and verify recovery
```

### Day 3: Chaos - Performance Under Stress
```
Morning:
  ✓ Byzantine node (slow responder)
  ✓ Verify consensus still works
  ✓ Measure latency impact
  
Afternoon:
  ✓ Memory pressure test
  ✓ Verify graceful eviction
  ✓ Verify no data loss
  
Evening:
  ✓ Sync lag spike
  ✓ Verify eventual consistency
  ✓ Verify queue handling
```

### Day 4: Chaos - Attack Scenarios
```
Morning:
  ✓ Byzantine proposal attack
  ✓ Malformed consensus messages
  ✓ Verify rejection/handling
  
Afternoon:
  ✓ Agent network degradation (33%, 66%)
  ✓ Verify load adaptation
  ✓ Verify no request loss
  
Evening:
  ✓ Combined chaos (multiple failures simultaneously)
  ✓ Verify system stability
```

### Day 5-7: Sustained Testing & Documentation
```
Day 5:
  ✓ 4-hour sustained peak load (2000 RPS)
  ✓ Monitor all metrics continuously
  ✓ Document thermal behavior
  ✓ Verify no cascading failures
  
Day 6:
  ✓ Repeat critical scenarios
  ✓ Verify reproducible results
  ✓ Validate edge cases
  
Day 7:
  ✓ Generate report
  ✓ Identify any issues found
  ✓ Document breaking points
  ✓ Create operational guidelines
```

---

## Part 5: Success Criteria

### Load Testing Success
```
✅ Baseline (100-1000 RPS):
   - p95 latency: < 50ms (target)
   - p99 latency: < 100ms (target)
   - Error rate: < 0.1%
   - CPU: < 50%
   - Memory: stable

✅ Sustained Load (1000 RPS, 1 hour):
   - p95 latency: < 100ms (target)
   - Error rate: < 0.5% (acceptable)
   - Memory: no growth over time
   - No crashes

✅ Spike Test (burst to 5000 RPS):
   - Recovery time: < 30 seconds
   - No data loss
   - No cascading failures

✅ Sustained Peak (2000 RPS, 2 hours):
   - System remains stable
   - No memory leaks
   - Graceful degradation (if needed)
```

### Chaos Engineering Success
```
✅ Single Node Failure:
   - Detected within 5 seconds
   - Cluster continues with 2/3
   - Recovery time: < 30 seconds
   - Zero data loss

✅ Network Partition:
   - Minority stops (safe)
   - Majority continues
   - Healing: < 10 seconds
   - Consistency maintained

✅ Byzantine Attack:
   - Attack rejected
   - System unaffected
   - Continues normal operation

✅ Cascading Failure:
   - Graceful degradation
   - Data preserved
   - Recovery possible
```

### Consistency Success
```
✅ Zero Data Loss:
   - All writes persist (L1→L2)
   - All failures recover data
   - All partitions reconcile

✅ Consensus Correctness:
   - 3/3 agreement always
   - No divergence
   - Byzantine safety maintained

✅ Knowledge Consistency:
   - L1.5 consolidation works
   - Replication lag < 200ms
   - No conflicts
```

---

## Part 6: Monitoring During Tests

### Key Metrics to Track

**Consensus Layer**
- Proposals per second
- Agreement rate (3/3, 2/3, 1/3)
- Latency (pre-prepare, prepare, commit phases)
- Leader stability (changes)

**Agent Network**
- Routing decisions per second
- Agent health (24/24)
- Load distribution (% per agent)
- Average confidence score

**Knowledge Pyramid**
- L1 hit rate
- L1→L2 sync lag
- Replication conflicts
- Cache evictions

**System Resources**
- CPU usage per node
- Memory usage per node
- Network throughput
- Disk I/O

**Error Tracking**
- HTTP error codes
- Timeouts
- Network errors
- Processing errors

### Grafana Dashboards to Monitor
1. **Real-Time Load**: RPS, latency, errors
2. **Consensus**: Latency breakdown, agreement rate
3. **Agents**: Load distribution, confidence
4. **Memory**: Per-node usage, evictions
5. **Errors**: Error rate, types, trends

---

## Part 7: Reporting

After all tests complete, deliver:

1. **Executive Summary**
   - System verdict: PASS/FAIL
   - Breaking points identified
   - Key risks (if any)

2. **Detailed Results**
   - Load test graphs (latency, throughput, errors)
   - Chaos test outcomes (recovery times, data loss)
   - Consistency verification results

3. **Breaking Points**
   - Maximum sustainable RPS
   - Failure recovery times
   - Memory limits
   - Network tolerance

4. **Operational Guidelines**
   - Safe operating ranges
   - Alert thresholds
   - Recovery procedures
   - Scaling recommendations

5. **Issues Found & Fixes**
   - Any bugs discovered
   - Performance issues
   - Recommendations for hardening

---

## Next Steps

1. **Approve this plan** ✓
2. **Build load testing framework** (load_testing_suite.py)
3. **Build chaos engineering framework** (chaos_engineer.py)
4. **Execute tests** (Day 1-7)
5. **Analyze results** (comprehensive report)
6. **Document findings** (operational guidelines)

**Ready to begin implementation?** 🚀

