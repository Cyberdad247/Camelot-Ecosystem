# ⚙️ PHASE H WEEK 1: Observability Infrastructure

**Status:** ACTIVE (2026-06-22 → 2026-06-29)  
**Goal:** Build metrics collection, anomaly detection, and performance baseline  
**Deliverable:** Foundation for autonomous learning loop

---

## 🎯 Week 1 Objectives

1. ✅ **Metrics Collection Engine**
   - Capture latency, throughput, errors from all operations
   - Store in SQLite (append-only event log)
   - Configurable sampling (start at 10%, increase as needed)

2. ✅ **Anomaly Detection System**
   - Define normal behavior baseline (from Phase G tests)
   - Detect deviations (latency spike, error rate increase, resource leak)
   - Alert when anomalies detected

3. ✅ **Performance Baseline Documentation**
   - Catalog healthy metrics from production tests
   - Document p50/p95/p99 for each operation type
   - Create reference for comparing future performance

---

## 📋 Week 1 Tasks (Kanban)

### Task 1: Metrics Collection Engine
**Status:** 🟦 IN PROGRESS  
**Files:** `control_plane/phase_h_metrics.py`  
**Time:** 1-2 days

**Spec:**
```python
class MetricsCollector:
    def __init__(self, sample_rate=0.1):
        """
        sample_rate: 0.1 = capture 10% of operations
        Can increase to 0.5 or 1.0 for debugging
        """
        
    def record_operation(self, operation_type, duration_ms, success, tags={}):
        """
        Record a single operation.
        operation_type: 'read', 'write', 'route', 'compress'
        duration_ms: latency in milliseconds
        success: True/False
        tags: {'agent_id': 'a1', 'workload': 'heavy'} etc
        """
        
    def get_statistics(self, operation_type=None, time_window_sec=3600):
        """
        Return aggregated stats for last N seconds.
        Returns: {'p50': 1.2, 'p95': 5.3, 'p99': 12.1, 'error_rate': 0.02}
        """
```

**Deliverables:**
- [ ] MetricsCollector class (append-only SQLite)
- [ ] Sample rate configuration (dynamic)
- [ ] Statistics aggregation (p50/p95/p99)
- [ ] Error tracking and classification
- [ ] Unit tests (8+ tests)

---

### Task 2: Anomaly Detection System
**Status:** 🟦 IN PROGRESS  
**Files:** `control_plane/phase_h_anomaly_detector.py`  
**Time:** 1-2 days

**Spec:**
```python
class AnomalyDetector:
    def __init__(self, baseline_metrics):
        """
        baseline_metrics: {'read_p95_ms': 1.3, 'write_p99_ms': 5.8, ...}
        From Phase G test results
        """
        
    def check(self, current_metrics):
        """
        Compare current metrics to baseline.
        Return: {'anomalies': [...], 'severity': 'warning'|'critical'}
        """
        
    def get_alert(self):
        """
        Return pending alert (if any anomaly detected)
        """
```

**Anomalies to detect:**
- Latency spike (p95 > baseline × 1.5)
- Error rate increase (> 0.1%)
- Memory leak (growth > 10MB/min)
- Timeout spike (queue depth growing)
- Resource exhaustion (CPU > 80%, memory > 95%)

**Deliverables:**
- [ ] AnomalyDetector class
- [ ] Baseline definition from Phase G
- [ ] Alert generation (warning/critical)
- [ ] Alert logging
- [ ] Unit tests (10+ tests)

---

### Task 3: Baseline Documentation
**Status:** 🟦 IN PROGRESS  
**Files:** `PHASE_H_BASELINE.md`  
**Time:** 1 day

**Content:**
```markdown
# Production Baseline (from Phase G Tests)

## Healthy Latencies
- SQLite read: p95 = 0.018ms, p99 = 0.05ms
- Routing decision: p95 = 0.0009ms, p99 = 0.002ms
- Compression: p95 = 1.586ms, p99 = 10ms

## Healthy Throughput
- Sustained: 1000 RPS sustainable
- Spike: 2000 RPS acceptable for <1 min
- Error rate: 0.0% (target: < 0.1%)

## Healthy Resources
- Memory: stable at 28MB baseline
- CPU: <30% under 1000 RPS load
- Disk: no excessive I/O

## Alert Thresholds
- CRITICAL: p95 latency > 5ms (3x baseline)
- WARNING: p95 latency > 2.5ms (2x baseline)
- CRITICAL: error rate > 1%
- WARNING: error rate > 0.1%
- CRITICAL: memory > 95% of available
- WARNING: memory > 90%
```

**Deliverables:**
- [ ] PHASE_H_BASELINE.md (complete)
- [ ] Thresholds defined (warning/critical)
- [ ] Reference tables for each operation type
- [ ] Comparison guidance (how to use baseline)

---

### Task 4: Integration with Main System
**Status:** 🟦 READY  
**Files:** `control_plane/main.py` (update)  
**Time:** 1 day

**Changes:**
```python
# In main event loop:
from phase_h_metrics import MetricsCollector
from phase_h_anomaly_detector import AnomalyDetector

metrics = MetricsCollector(sample_rate=0.1)
anomaly_detector = AnomalyDetector(baseline_metrics)

# Every operation:
start = time.perf_counter()
try:
    result = do_operation()
    duration = (time.perf_counter() - start) * 1000
    metrics.record_operation('read', duration, success=True)
except Exception as e:
    duration = (time.perf_counter() - start) * 1000
    metrics.record_operation('read', duration, success=False)

# Every 60 seconds:
current = metrics.get_statistics()
alerts = anomaly_detector.check(current)
if alerts['anomalies']:
    logger.warning(f"Anomalies detected: {alerts}")
```

**Deliverables:**
- [ ] Integration in main event loop
- [ ] Metrics recording on every operation
- [ ] Anomaly check loop (every 60s)
- [ ] Alert logging to SQLite
- [ ] No performance impact (< 0.1ms overhead)

---

### Task 5: Dashboard/Monitoring Output
**Status:** 🟦 READY  
**Files:** `dashboards/phase_h_metrics.txt`  
**Time:** 1 day

**Output format (human-readable):**
```
=== PHASE H METRICS (Last 1 hour) ===
Timestamp: 2026-06-22T22:30:00Z

OPERATIONS:
  Read:    p50=0.4ms  p95=1.2ms  p99=5.1ms  count=45,230  errors=0
  Write:   p50=0.5ms  p95=1.3ms  p99=5.9ms  count=12,100  errors=0
  Route:   p50=0.0ms  p95=0.1ms  p99=0.3ms  count=57,330  errors=0
  Compress:p50=0.2ms  p95=1.5ms  p99=8.2ms  count=3,400   errors=0

RESOURCES:
  Memory:  28MB (6% of 432MB)  ← Healthy
  CPU:     15% avg             ← Healthy
  Disk I/O: 2.3MB/s            ← Healthy

ALERTS:
  ✅ No anomalies detected
  ✅ All metrics normal

COMPARISON TO BASELINE:
  Read p95:   1.2ms vs baseline 1.3ms  ✅ 8% better
  Errors:     0 vs baseline 0          ✅ Perfect
  Memory:     28MB vs baseline 28MB    ✅ Stable
```

**Deliverables:**
- [ ] Real-time metrics display
- [ ] Comparison to baseline
- [ ] Alert status
- [ ] Export to JSON for dashboarding

---

## 📊 Success Criteria (Week 1)

### Tier 1: Must Complete
```
✅ MetricsCollector captures all operations
✅ AnomalyDetector detects baseline deviations
✅ Baseline documented from Phase G tests
✅ Integration in main system (no performance impact)
✅ Unit test coverage > 80%
```

### Tier 2: Should Complete
```
✅ Dashboard shows real-time metrics
✅ Alert logging to SQLite
✅ Sample rate tuning guidance
```

### Tier 3: Nice to Have
```
✅ Historical metrics trending (last 24h)
✅ Comparison graph vs baseline
✅ Export to CSV for analysis
```

---

## 🔄 Week 1 Timeline

**Day 1 (Mon 2026-06-24)**
- [ ] Create MetricsCollector skeleton
- [ ] Define SQLite schema for event log
- [ ] Unit tests framework

**Day 2 (Tue 2026-06-25)**
- [ ] Complete MetricsCollector implementation
- [ ] Create AnomalyDetector skeleton
- [ ] Define baseline thresholds

**Day 3 (Wed 2026-06-26)**
- [ ] Complete AnomalyDetector implementation
- [ ] Integration testing (MetricsCollector + AnomalyDetector)
- [ ] Baseline documentation

**Day 4 (Thu 2026-06-27)**
- [ ] Integration with main system
- [ ] Performance testing (ensure < 0.1ms overhead)
- [ ] Dashboard/output formatting

**Day 5 (Fri 2026-06-28)**
- [ ] Full system testing (integration tests)
- [ ] Documentation (how to read metrics, what thresholds mean)
- [ ] Week 1 sign-off

**Day 6-7 (Sat-Sun 2026-06-29)**
- [ ] Buffer/catch-up time
- [ ] Week 2 planning (Learning Engine)

---

## 📁 Week 1 Deliverables

```
control_plane/
├── phase_h_metrics.py (450+ lines)
│   ├── MetricsCollector class
│   ├── SQLite event log schema
│   ├── Statistics aggregation
│   └── Sampling logic
│
├── phase_h_anomaly_detector.py (350+ lines)
│   ├── AnomalyDetector class
│   ├── Baseline comparison
│   ├── Alert generation
│   └── Severity classification
│
├── tests/
│   ├── test_phase_h_metrics.py (200+ lines, 8+ tests)
│   └── test_phase_h_anomaly_detector.py (250+ lines, 10+ tests)
│
└── main.py (updated with metrics integration)

dashboards/
└── phase_h_metrics.txt (real-time display)

docs/
└── PHASE_H_BASELINE.md (baseline + thresholds)
└── PHASE_H_WEEK1_INTEGRATION.md (how to use metrics in code)
```

---

## 🚀 What Happens in Week 1

1. **Metrics start flowing** — Every operation recorded (10% sample)
2. **Baseline established** — Reference created from Phase G test data
3. **Anomaly detection armed** — System watches for deviations
4. **Silent learning begins** — Foundation laid for Week 2 (Pattern Learning)

By end of Week 1:
- ✅ System collects high-fidelity performance data
- ✅ Anomalies can be detected automatically
- ✅ Foundation ready for Week 2 learning engine
- ✅ Production monitoring infrastructure in place

---

## 📖 Key Concepts

**Observability**: Seeing what your system is doing (metrics, events, alerts)  
**Baseline**: Definition of "healthy" behavior (from Phase G tests)  
**Anomaly Detection**: Automatically spotting deviations from healthy  
**Sampling**: Collecting 10% of operations (reduces overhead)  
**Event Log**: Append-only SQLite table (immutable history)

---

## ❓ Configuration Options

**For Week 1, defaults are:**
- Sample rate: 10% (capture 1 in 10 operations)
- Anomaly threshold: 1.5x baseline (warning), 3x baseline (critical)
- Alert check interval: 60 seconds
- Retention: Keep last 7 days of events

Can tune these based on Week 1 learnings.

---

## 🎯 Ready to Start?

Week 1 is **AUTONOMOUS DEVELOPMENT** — these are straightforward Python classes that can be built in parallel. 

**Questions before we begin?**

1. Sample rate: OK to start at 10%? (or go higher for more data?)
2. Baseline: Should we pull from Phase G test results or measure fresh?
3. Alert channels: Just log to SQLite, or also to stdout/file?
4. Priority: Accuracy or speed? (affects threshold tuning)

👉 **Ready to code?** Say "begin" and I'll start building Week 1 components.
