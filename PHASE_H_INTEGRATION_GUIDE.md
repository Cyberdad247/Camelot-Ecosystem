# 🔧 Phase H Integration Guide (Days 2-5)

**Timeline:** 2026-06-25 → 2026-06-28  
**Goal:** Wire metrics collection into main system  
**Overhead:** < 0.1ms per operation

---

## 📋 Integration Checklist

### Day 2 (Tue 2026-06-25): Wire Metrics
- [ ] Import MetricsMiddleware in main.py
- [ ] Initialize metrics early in startup
- [ ] Add metrics.track() to main operation loop
- [ ] Performance test (verify < 0.1ms overhead)
- [ ] Integration test (verify data collected)

### Day 3 (Wed 2026-06-26): Dashboard Setup
- [ ] Create live dashboard display
- [ ] Print metrics in real-time
- [ ] Show baseline comparison
- [ ] Show alert status
- [ ] Test dashboard output

### Day 4 (Thu 2026-06-27): Hardening
- [ ] Error handling (graceful degradation)
- [ ] Database error recovery
- [ ] Memory cleanup strategy
- [ ] Background thread management
- [ ] Performance profiling

### Day 5 (Fri 2026-06-28): Testing & Validation
- [ ] Full integration tests
- [ ] Load test (no performance impact)
- [ ] Anomaly injection test
- [ ] Documentation
- [ ] Sign-off

---

## 🚀 Quick Start Integration

### Step 1: Initialize Metrics (in main.py startup)

```python
from control_plane.phase_h_integration import init_metrics

def main():
    # Early in startup sequence
    print("[INIT] Starting metrics collection...")
    metrics = init_metrics(sample_rate=0.1)  # 10% sampling
    metrics.start_background_check(interval_sec=60)  # Check every 60s
    print("[INIT] Metrics collection ready")

    # ... rest of startup ...
    run_main_loop()

if __name__ == '__main__':
    main()
```

### Step 2: Instrument Operations

**Pattern A: Context Manager (Simplest)**
```python
from control_plane.phase_h_integration import get_metrics

metrics = get_metrics()

# Wrap any operation
with metrics.track('read', tags={'query': 'user_lookup'}):
    user = database.query("SELECT * FROM users WHERE id = ?", user_id)

with metrics.track('write', tags={'table': 'events'}):
    database.insert("events", event_data)

with metrics.track('route'):
    destination = router.select_agent(request)
```

**Pattern B: Manual Timing (for complex operations)**
```python
import time
from control_plane.phase_h_integration import get_metrics

metrics = get_metrics()

start = time.perf_counter()
try:
    result = expensive_operation()
    duration = (time.perf_counter() - start) * 1000
    metrics.record('expensive_op', duration, success=True)
except Exception as e:
    duration = (time.perf_counter() - start) * 1000
    metrics.record('expensive_op', duration, success=False, 
                   error_message=str(e))
```

**Pattern C: Decorator (for reusable functions)**
```python
from control_plane.phase_h_integration import get_metrics
from functools import wraps
import time

def track_operation(op_name):
    """Decorator for operation tracking"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            metrics = get_metrics()
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                duration = (time.perf_counter() - start) * 1000
                metrics.record(op_name, duration, success=True)
                return result
            except Exception as e:
                duration = (time.perf_counter() - start) * 1000
                metrics.record(op_name, duration, success=False, 
                               error_message=str(e))
                raise
        return wrapper
    return decorator

# Usage
@track_operation('database_query')
def query_users():
    return db.query("SELECT * FROM users")
```

---

## 📊 Instrumentation Locations

### Critical Operations (Must Track)
1. **Database reads** (`read` operation)
   - Location: Database query layer
   - Importance: Baseline for performance

2. **Database writes** (`write` operation)
   - Location: Write operations
   - Importance: Transactional performance

3. **Routing decisions** (`route` operation)
   - Location: Agent selection logic
   - Importance: Load balancing health

4. **Compression** (`compress` operation)
   - Location: Symbolect compression
   - Importance: Compression overhead tracking

### Secondary Operations (Optional)
- `cache_lookup` — Cache hit rate
- `network_request` — External API calls
- `parse_json` — JSON deserialization
- Custom operations as needed

---

## 🎯 Implementation Examples

### Example 1: SQLite Integration

**Before:**
```python
def read_user(user_id):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result
```

**After:**
```python
from control_plane.phase_h_integration import get_metrics

def read_user(user_id):
    metrics = get_metrics()
    
    with metrics.track('read', tags={'table': 'users'}):
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
    
    return result
```

### Example 2: Router Integration

**Before:**
```python
def select_agent(request):
    agents = get_available_agents()
    selected = min(agents, key=lambda a: a.load)
    return selected
```

**After:**
```python
from control_plane.phase_h_integration import get_metrics

def select_agent(request):
    metrics = get_metrics()
    
    with metrics.track('route', tags={'workload': request.workload_type}):
        agents = get_available_agents()
        selected = min(agents, key=lambda a: a.load)
    
    return selected
```

### Example 3: Error Handling

**Before:**
```python
def process_request(data):
    try:
        result = transform(data)
        save(result)
        return result
    except Exception as e:
        logger.error(f"Failed: {e}")
        raise
```

**After:**
```python
from control_plane.phase_h_integration import get_metrics

def process_request(data):
    metrics = get_metrics()
    
    try:
        result = transform(data)
        
        start = time.perf_counter()
        try:
            save(result)
            duration = (time.perf_counter() - start) * 1000
            metrics.record('write', duration, success=True)
        except Exception as e:
            duration = (time.perf_counter() - start) * 1000
            metrics.record('write', duration, success=False, 
                           error_message=str(e))
            raise
        
        return result
    except Exception as e:
        logger.error(f"Failed: {e}")
        raise
```

---

## 🖥️ Monitoring & Dashboard

### View Metrics Once
```bash
python dashboards/phase_h_live_dashboard.py --mode once
```

Output:
```
================================================================================
⚙️  PHASE H LIVE DASHBOARD — 2026-06-25T14:30:00
================================================================================

📊 OPERATION METRICS (Last 1 hour)
────────────────────────────────────────────────────────────────────────────────
Operation        Count    p50      p95      p99      Errors     Status
────────────────────────────────────────────────────────────────────────────────
read             12450    0.45     1.15     5.21     0          🟢 OK
write            3210     0.52     1.28     5.89     0          🟢 OK
route            45320    0.00     0.08     0.25     0          🟢 OK
compress         2100     0.16     1.45     8.32     0          🟢 OK

💚 SYSTEM HEALTH
────────────────────────────────────────────────────────────────────────────────
  Status:   ✅ HEALTHY
  Summary:  0 critical, 0 warnings
  Anomalies: 0 total

🚨 RECENT ALERTS
────────────────────────────────────────────────────────────────────────────────
  ✅ No anomalies detected
```

### View Metrics Continuously
```bash
python dashboards/phase_h_live_dashboard.py --mode loop --interval 30
```

### View Detailed Report
```bash
python dashboards/phase_h_live_dashboard.py --mode detailed
```

---

## 🧪 Testing Integration

### Test 1: Metrics Collected
```python
from control_plane.phase_h_integration import get_metrics

metrics = get_metrics()

# Generate some operations
with metrics.track('read'):
    pass  # Simulate read

# Check metrics
stats = metrics.get_current_metrics()
assert 'read' in stats
assert stats['read']['count'] > 0
print("✅ Test 1 passed: Metrics collected")
```

### Test 2: Performance Overhead
```python
import time
from control_plane.phase_h_integration import get_metrics

metrics = get_metrics()

# Measure overhead
iterations = 10000
start = time.perf_counter()

for i in range(iterations):
    with metrics.track('read'):
        pass  # Empty operation

elapsed = (time.perf_counter() - start) * 1000 / iterations
print(f"Average overhead: {elapsed:.4f}ms per operation")
assert elapsed < 0.1, f"Overhead too high: {elapsed}ms"
print("✅ Test 2 passed: Overhead < 0.1ms")
```

### Test 3: Anomaly Detection
```python
from control_plane.phase_h_integration import get_metrics

metrics = get_metrics()

# Generate slow operations
for i in range(10):
    metrics.record('read', 10.0, True)  # 10ms (7x baseline)

# Check anomalies
anomalies = metrics.check_anomalies()
assert anomalies['severity'] == 'critical'
print("✅ Test 3 passed: Anomalies detected")
```

### Test 4: Health Status
```python
from control_plane.phase_h_integration import get_metrics

metrics = get_metrics()

# Normal operations
for i in range(100):
    with metrics.track('read'):
        pass

health = metrics.get_health_status()
assert health['status'] == 'healthy'
print("✅ Test 4 passed: Health check working")
```

---

## 📈 Performance Expectations

### Metrics Collection Overhead

| Operation | Baseline | With Metrics | Overhead |
|-----------|----------|--------------|----------|
| SQLite read | 0.0078ms | 0.0085ms | 0.0007ms ✅ |
| Routing | 0.00039ms | 0.00048ms | 0.00009ms ✅ |
| Compression | 0.164ms | 0.165ms | 0.001ms ✅ |

**Total overhead:** < 0.002ms per operation (sampling included)

### With Sampling at 10%

- 90% of operations: 0ms overhead (not recorded)
- 10% of operations: < 0.002ms overhead (recorded)
- **Average overhead: < 0.0002ms per operation** ✅

---

## 🚨 Troubleshooting

### Issue: High Overhead
**Solution:** Reduce sample rate
```python
metrics = get_metrics()
metrics.collector.sample_rate = 0.01  # 1% sampling
```

### Issue: Database Growing
**Solution:** Run cleanup periodically
```python
metrics = get_metrics()
metrics.cleanup_old_metrics(days_to_keep=7)  # Keep 7 days
```

### Issue: Background Check Errors
**Solution:** Check logs for anomaly detection issues
```python
# Logs in control_plane/anomalies.db
# Manual check
alerts = metrics.detector.get_alerts(hours=1)
print(alerts)
```

### Issue: No Metrics Showing
**Solution:** Verify initialization
```python
from control_plane.phase_h_integration import get_metrics

metrics = get_metrics()
print(f"Event count: {metrics.collector.get_event_count()}")
print(f"Sample rate: {metrics.collector.sample_rate}")
```

---

## ✅ Integration Sign-Off Checklist

- [ ] Metrics initialized in main.py startup
- [ ] All critical operations instrumented (read, write, route, compress)
- [ ] Performance overhead verified < 0.1ms
- [ ] Dashboard displays metrics correctly
- [ ] Anomaly detection working (tested)
- [ ] Health status API responding
- [ ] Background check running every 60s
- [ ] Error handling graceful (no exceptions)
- [ ] All tests passing
- [ ] Documentation complete

**When all checked:** ✅ Week 1 Integration Complete

---

## 📞 Next: Week 2 Learning Engine

Once integration is complete:
1. Week 2 starts: Pattern Learning
2. Learn from collected metrics
3. Identify optimization opportunities
4. Generate parameter tuning candidates

**Ready for Days 2-5 integration?**
