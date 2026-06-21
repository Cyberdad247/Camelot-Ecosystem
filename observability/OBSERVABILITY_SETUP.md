# CAMELOT-OS Observability Stack Setup Guide

**Status**: Production-ready observability stack  
**Date**: 2026-06-18  
**Components**: Prometheus, Grafana, Jaeger, AlertManager

---

## Quick Start (5 minutes)

### 1. Start the Observability Stack

```bash
cd observability/
docker-compose up -d
```

**Verify all services are running:**
```bash
docker-compose ps
```

Expected output (all healthy):
```
NAME                     STATUS
camelot-prometheus       healthy
camelot-grafana          healthy
camelot-alertmanager     healthy
camelot-jaeger           healthy
camelot-redis-exporter   healthy
redis-1, redis-2, redis-3   healthy
qdrant-1, qdrant-2, qdrant-3 healthy
```

### 2. Instrument Your CAMELOT-OS Instances

In each CAMELOT-OS node's `main.py`:

```python
from control_plane.metrics_collector import get_metrics_collector

async def main():
    # Initialize metrics collector (starts HTTP server on :8000)
    metrics = get_metrics_collector(port=8000)
    
    # ... rest of your code ...
    
    # Record metrics as operations occur
    metrics.record_consensus_proposal(
        node_id="node_1",
        phase="commit",
        success=True,
        latency_seconds=0.087
    )
```

### 3. Access the Dashboards

| Service | URL | Credentials |
|---------|-----|-------------|
| **Prometheus** | http://localhost:9090 | None |
| **Grafana** | http://localhost:3000 | admin/admin123 |
| **Jaeger** | http://localhost:16686 | None |
| **AlertManager** | http://localhost:9093 | None |

---

## Component Overview

### Prometheus (http://localhost:9090)
- **Purpose**: Metrics collection and time-series database
- **Scrape Interval**: 15 seconds
- **Data Retention**: 30 days
- **Query Language**: PromQL

**Key Metrics Scraped**:
- System (CPU, memory, disk)
- Consensus (latency, proposals, leader changes)
- Knowledge Sync (replication lag, conflicts)
- Agent Network (health, latency, routing)
- Errors & Failures (rates, recovery time)

### Grafana (http://localhost:3000)
- **Purpose**: Visualization and dashboarding
- **Default Credentials**: admin/admin123

**Pre-configured Dashboards**:
1. **System Overview** — CPU, memory, disk across all nodes
2. **Consensus Performance** — Latency, success rates, leader elections
3. **Knowledge Sync** — Replication lag, conflicts, events/sec
4. **Agent Network** — Agent health, load distribution, routing
5. **Error Rates** — Error types, severity, recovery times
6. **SLO Dashboard** — SLO breaches, availability, latency

### Jaeger (http://localhost:16686)
- **Purpose**: Distributed request tracing
- **Collection Port**: 6831 (UDP)
- **Retention**: 72 hours

**Traces Captured**:
- Consensus proposals (pre-prepare → prepare → commit)
- Knowledge sync events (L1 write → L1.5 → L2)
- Agent routing decisions
- Cross-instance operations

### AlertManager (http://localhost:9093)
- **Purpose**: Alert routing and notification
- **Supported Channels**: Slack, PagerDuty, email

**Alert Levels**:
- **Critical** (immediate page): Data loss, network degraded, consensus failures
- **Warning** (notify): High latency, high CPU, conflicts
- **Info** (log only): Normal operational events

---

## Integration with CAMELOT-OS

### Metrics Collection Points

Add these to your core modules:

```python
# ── In distributed_ledger_consensus.py ──────────────────────
metrics = get_metrics_collector()

async def _decide(self, state):
    start = time.time()
    # ... consensus logic ...
    latency = time.time() - start
    
    metrics.record_consensus_proposal(
        node_id=self.node_id,
        phase="commit",
        success=True,
        latency_seconds=latency
    )

# ── In distributed_knowledge_sync.py ────────────────────────
metrics = get_metrics_collector()

async def _persist_to_l2(self, event):
    start = time.time()
    # ... persistence logic ...
    latency = time.time() - start
    
    metrics.record_sync_event(
        node_id=self.node_id,
        phase="l2_persistence",
        success=True,
        latency_seconds=latency
    )

# ── In distributed_agent_registry.py ────────────────────────
metrics = get_metrics_collector()

async def _invoke_remote_agent(self, agent, request):
    start = time.time()
    result = await self._invoke(agent, request)
    latency = time.time() - start
    
    metrics.record_agent_request(
        agent_id=agent.agent_id,
        success=result.get('status') == 'success',
        latency_seconds=latency,
        method=request.get('method', 'unknown')
    )
```

### Tracing Integration

Add Jaeger instrumentation:

```python
# ── In control_plane/tracing.py (NEW) ────────────────────
from jaeger_client import Config

tracer_obj = Config(
    config={
        'sampler': {'type': 'const', 'param': 1},
        'logging': True,
    },
    service_name='camelot-node-1',
    validate=True,
).initialize_tracer()

# Use in consensus:
with tracer_obj.start_active_span('consensus_proposal') as scope:
    scope.span.set_tag('entry_id', entry_id)
    scope.span.set_tag('phase', 'commit')
    # ... operation code ...
```

---

## Alert Severity & Response

### Critical Alerts (Immediate Page)

| Alert | Threshold | Action |
|-------|-----------|--------|
| **DataLossDetected** | Any | Page all on-call immediately |
| **ConsensusFailures** | > 0.1/sec | Page SRE lead |
| **AgentNetworkDegraded** | < 6 healthy | Page SRE lead |
| **MemoryExhaustion** | > 90% | Kill non-critical tasks |
| **LeaderElectionStorm** | > 0.5/sec | Investigate network |

### Warning Alerts (Notify Slack)

| Alert | Threshold | Action |
|-------|-----------|--------|
| **ConsensusLatencyHigh** | P95 > 500ms | Investigate load |
| **ReplicationLagHigh** | > 5s | Check network |
| **AgentHighLoad** | > 0.9 | Consider scaling |
| **CPUOverutilization** | > 80% | Monitor closely |

---

## Daily Operations

### Check System Health

```bash
# View Prometheus targets
curl http://localhost:9090/api/v1/targets

# Query consensus latency
curl 'http://localhost:9090/api/v1/query?query=camelot_consensus_latency_seconds'

# View active alerts
curl http://localhost:9093/api/v1/alerts
```

### View Dashboards

1. **Morning checklist**: Grafana System Overview
   - CPU: should be < 40% average
   - Memory: should be < 50% utilization
   - Disk: should be < 60% utilization

2. **Consensus health**: Consensus Performance dashboard
   - P95 latency: should be < 100ms
   - Success rate: should be > 99.9%
   - Leader stability: 0 changes in 24h

3. **Agent network**: Agent Network dashboard
   - Healthy agents: 6-8 online
   - Response latency: < 50ms
   - Error rate: < 0.1%

### Investigate Issues

```bash
# Find slow consensus rounds
curl 'http://localhost:9090/api/v1/query_range' \
  -d 'query=camelot_consensus_latency_seconds' \
  -d 'start=2026-06-18T00:00:00Z' \
  -d 'end=2026-06-18T01:00:00Z' \
  -d 'step=1m'

# Trace specific operation
curl 'http://localhost:16686/api/traces?service=camelot-node-1&limit=20'

# View error rate by component
curl 'http://localhost:9090/api/v1/query?query=rate(camelot_errors_total[5m])'
```

---

## Maintenance

### Data Retention

- **Prometheus**: 30 days (configured in prometheus.yml)
- **Jaeger**: 72 hours (default)
- **Grafana**: Infinite (stored in PostgreSQL)

### Backup Strategy

```bash
# Backup Prometheus data
docker exec camelot-prometheus tar czf /prometheus/backup.tar.gz /prometheus

# Backup Grafana dashboards
docker exec camelot-grafana grafana-cli admin export-dashboard --adminUser=admin --adminPassword=admin123
```

### Upgrade Prometheus

```bash
# Check current version
docker exec camelot-prometheus prometheus --version

# Upgrade
docker-compose pull prometheus
docker-compose up -d prometheus
```

---

## Troubleshooting

### Prometheus not scraping metrics

```bash
# Check targets
curl http://localhost:9090/api/v1/targets | jq .

# Expected: all targets should have "health": "up"
# If down: check CAMELOT-OS metrics endpoint (port 8000)
curl http://camelot-node-1:8000/metrics
```

### Alerts not firing

```bash
# Check AlertManager config
docker exec camelot-alertmanager cat /etc/alertmanager/alertmanager.yml

# Test notification channel
curl -X POST http://localhost:9093/api/v1/alerts \
  -H 'Content-Type: application/json' \
  -d '[{"labels":{"alertname":"TEST","severity":"critical"}}]'
```

### Jaeger not receiving traces

```bash
# Check Jaeger metrics
curl http://localhost:14269/metrics | grep accepted

# Verify your app is sending to localhost:6831 (UDP)
netstat -an | grep 6831
```

---

## Performance Tuning

### High Cardinality Issues

If metrics are growing too fast:

```yaml
# Add metric_relabel_configs to prometheus.yml
relabel_configs:
  - source_labels: [__name__]
    regex: 'camelot_agent_latency_seconds'
    action: drop
    # Keep only high-priority metrics
```

### Jaeger Sampling

For high-volume environments, reduce sampling:

```yaml
# In docker-compose.yml, Jaeger section:
environment:
  SAMPLER_TYPE: probabilistic
  SAMPLER_PARAM: 0.1  # Sample 10% of traces
```

---

## Success Criteria

✅ **Observability is ready for production when:**
- All services healthy and accessible
- All 6 Grafana dashboards populated
- Alert rules loaded and firing test alerts
- Jaeger receiving traces from all nodes
- Data flowing to all 3 Prometheus scrape targets
- Team trained on dashboard usage

---

## Next Steps

1. **Start the stack**: `docker-compose up -d`
2. **Instrument your code**: Add metrics_collector calls
3. **Configure alerts**: Update alertmanager.yml with your channels
4. **Create custom dashboards**: Add team-specific visualizations
5. **Set up on-call**: Wire PagerDuty/Slack notifications

---

**Setup Time**: ~30 minutes  
**Monthly Cost**: ~$200 (if cloud-hosted)  
**Operations Overhead**: ~2 hours/week initial, ~30 min/week steady state

