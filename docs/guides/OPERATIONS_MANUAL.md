# CAMELOT-OS Operations Manual

**Version**: 6.0.0 | **Effective Date**: 2026-06-18  
**Target Audience**: DevOps, SRE, Operations Teams

---

## Service Level Agreements (SLAs)

### Availability
- **Target**: 99.9% uptime (43.2 minutes downtime/month)
- **Measurement**: Harness heartbeat + agent health checks
- **Escalation**: > 15 minutes dark → Page on-call engineer

### Performance
- **P50 Latency**: < 50ms (local)
- **P95 Latency**: < 100ms (local), < 500ms (network)
- **P99 Latency**: < 500ms (local), < 2s (network)
- **Throughput**: > 1000 req/sec per agent
- **Memory**: < 8GB (all tiers)

### Error Rates
- **Target**: < 0.1% errors on healthy operations
- **Recovery**: Auto-restart via PIV loop (< 30s MTTR)
- **Data Integrity**: 0 data loss (Golay error correction)

---

## Daily Operations

### Morning Checklist (Start of Day)

```bash
# 1. Check system status
python -m control_plane.harness --health-check

# Expected output:
#   Status: OPERATIONAL ✅
#   Uptime: 24h 47m
#   Memory: 2.1 GB / 8.0 GB (26%)
#   Agents: 8/8 HEALTHY
#   Ledger entries: 1700+
#   Incidents: 0
```

```bash
# 2. Check Redis connectivity
redis-cli ping
# Expected: PONG

# 3. Check agent network
for port in 8401 8402 8403 8404 8405 8406 8407 8408; do
  nc -zv localhost $port
done
# Expected: All ports connected

# 4. Review overnight logs
tail -n 100 logs/system.log | grep -i "error\|warn\|critical"

# 5. Check disk usage
du -sh logs cache vault snapshots
# Alert if > 80% of available space

# 6. Review incidents/alerts
python -c "
from control_plane.provenance import Provenance
prov = Provenance()
recent = prov.get_recent_entries(limit=10)
for entry in recent:
    if 'incident' in entry.lower() or 'alert' in entry.lower():
        print(entry)
"
```

### Continuous Monitoring

```bash
# Monitor in separate terminal (every 5 seconds)
watch -n 5 'redis-cli INFO | grep memory; ps aux | grep python | wc -l'

# Or use dedicated monitoring script
python -m control_plane.harness --monitor &
```

### End-of-Day Checklist

```bash
# 1. Verify all processes running
ps aux | grep -E 'harness|agent_registry|redis' | grep -v grep

# 2. Commit any changes to ledger
git status PROVENANCE_LEDGER.md

# 3. Create daily backup
python -c "
from control_plane.memory_sync import MemorySync
sync = MemorySync()
sync.backup(label='daily_' + datetime.now().isoformat())
"

# 4. Generate metrics report
python -m control_plane.harness --metrics-report > reports/metrics_$(date +%Y%m%d).txt

# 5. Check for pending updates
python -m control_plane.dependency_engine --check-updates
```

---

## Monitoring & Alerting

### Key Metrics

#### 1. System Health
```bash
# Monitor via Redis
redis-cli HGETALL system:health
# Key values:
#   uptime: seconds
#   memory_usage: bytes
#   cpu_utilization: percent
#   error_count: count
#   request_count: count
```

#### 2. Agent Status
```bash
# Check each agent health every minute
python -c "
from control_plane.agent_gateway import AgentGateway
gateway = AgentGateway()
for agent_id in range(8401, 8409):
    status = gateway.probe_agent(agent_id)
    print(f'{agent_id}: {status.status}')
"
```

#### 3. Memory Utilization
```bash
# Monitor L1, L1.5, L2 independently
redis-cli INFO MEMORY  # L1
curl http://localhost:6333/info  # L1.5 (Qdrant)
python -c "from control_plane.cloudbrain_sync import CloudBrainSync; CloudBrainSync().get_usage()"  # L2
```

#### 4. Latency Percentiles
```bash
# Track via Hermes event bus
redis-cli HGETALL metrics:latency
# Returns: p50, p95, p99 in milliseconds
```

### Alert Thresholds

| Metric | Threshold | Severity | Action |
|--------|-----------|----------|--------|
| Memory > 7.5 GB | CRITICAL | Page on-call | Kill least-critical swarm task |
| CPU > 80% | WARNING | Alert | Auto-scale to Tier 2 |
| Agent dark > 30s | CRITICAL | Page on-call | Restart agent + ledger incident |
| Latency P95 > 1s | WARNING | Alert | Investigate longest-running tasks |
| Disk > 80% | WARNING | Alert | Trigger archive job |
| Error rate > 1% | CRITICAL | Page on-call | Rollback last change |
| Heartbeat missed 3x | CRITICAL | Page on-call | Auto-restart harness |

### Setting Up Alerts

```bash
# Via Hermes event bus (recommended)
python -c "
from control_plane.hermes_bridge import HermesBus
hermes = HermesBus()
hermes.subscribe('system.health', alert_handler)
hermes.subscribe('system.error', escalate_handler)
hermes.subscribe('system.warning', log_handler)
"

# Via external service (PagerDuty, Slack, etc.)
# Configure in .env:
export ALERT_WEBHOOK_URL=https://hooks.slack.com/...
export ALERT_EMAIL=on-call@company.com
export PAGERDUTY_KEY=...
```

---

## Performance Optimization

### 1. Memory Management

#### Check Current Usage
```bash
python -c "
from control_plane.system_analyzer import SystemAnalyzer
analyzer = SystemAnalyzer()
profile = analyzer.analyze()
print(f'Memory: {profile.memory.utilized} / {profile.memory.total}')
print(f'CPU: {profile.cpu.utilization}%')
"
```

#### Optimize L1 (Redis)
```bash
# Reduce session TTL
redis-cli CONFIG SET maxmemory-policy allkeys-lru

# Monitor key sizes
redis-cli --bigkeys

# Evict old sessions
redis-cli EVAL "
for i, key in ipairs(redis.call('keys', 'session:*')) do
  local ttl = redis.call('ttl', key)
  if ttl > 86400 then  -- older than 24h
    redis.call('del', key)
  end
end
return 'OK'
" 0
```

#### Optimize L1.5 (Qdrant)
```bash
# Cleanup old vectors
curl -X DELETE http://localhost:6333/collections/semantic_memory/points \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {
      "range": {
        "timestamp": {
          "gte": 0,
          "lt": '$(($(date +%s) - 2592000))'  # Older than 30 days
        }
      }
    }
  }'
```

### 2. CPU Optimization

#### Auto-Tier Selection
```bash
# Monitor and auto-scale tier
python -c "
from control_plane.bifrost_integration import BifrostIntegration
bi = BifrostIntegration()
while True:
    utilization = bi.get_cpu_utilization()
    if utilization > 70:
        bi.downgrade_tier()
    elif utilization < 20:
        bi.upgrade_tier()
    time.sleep(60)
"
```

#### Batch Operations
```bash
# Instead of processing 1000 requests individually:
# Use kinetic_swarm to batch them
python -c "
from control_plane.kinetic_swarm import get_kinetic_swarm
swarm = get_kinetic_swarm()

tasks = [task1, task2, ..., task1000]
for batch in [tasks[i:i+100] for i in range(0, len(tasks), 100)]:
    swarm.submit_batch(batch)
"
```

### 3. Network Optimization

#### Connection Pooling
```bash
# Configured in config_manager.py
# Increase for high-throughput scenarios
export AGENT_CONNECTION_POOL_SIZE=50
export REDIS_CONNECTION_POOL_SIZE=20
```

#### Compression (Phase F)
```bash
# Use Symbolect compression for large state transfers
python -c "
from control_plane.symbolect_protocol import get_symbolect_protocol, TransmissionMode
protocol = get_symbolect_protocol()

# Instead of sending 500KB JSON:
packet = protocol.transmit_toon_crystal(crystal, TransmissionMode.ONEBIT)
# Sends ~100 bytes instead
"
```

### 4. Database Optimization

#### Ledger Maintenance
```bash
# Weekly vacuum (compacts database)
python -c "
from control_plane.provenance import Provenance
prov = Provenance()
prov.vacuum()  # Reclaims unused space
print('✅ Ledger vacuumed')
"

# Monthly backup
tar -czf backups/ledger_$(date +%Y%m%d).tar.gz PROVENANCE_LEDGER.md
```

#### Query Optimization
```bash
# Add indexes for frequent queries
python -c "
from control_plane.provenance import Provenance
prov = Provenance()
prov.create_index('timestamp')
prov.create_index('agent_id')
prov.create_index('status')
"
```

---

## Maintenance Tasks

### Weekly

```bash
# 1. Ledger compaction
python -c "from control_plane.provenance import Provenance; Provenance().compact()"

# 2. Memory tier rebalancing
python -c "from control_plane.memory_sync import MemorySync; MemorySync().rebalance_tiers()"

# 3. Agent configuration sync
python -m control_plane.agent_registry --sync-config

# 4. Dependency update check
python -m control_plane.dependency_engine --check-updates

# 5. Backup verification
python -c "
from control_plane.memory_sync import MemorySync
sync = MemorySync()
sync.verify_backup()
"
```

### Monthly

```bash
# 1. Full system audit
python -m control_plane.sir_socrates --full-audit

# 2. Security scanning
python -m control_plane.heimdall_knight --security-scan

# 3. Performance analysis
python -m control_plane.inspira_metrics --monthly-report

# 4. Cost optimization review
python -m control_plane.cloud_services --cost-analysis

# 5. Knowledge pyramid synthesis
python -c "from control_plane.cloudbrain_synthesis import CloudBrainSynthesis; CloudBrainSynthesis().synthesize_month()"
```

### Quarterly

```bash
# 1. Full backup + recovery test
python -c "
from control_plane.memory_sync import MemorySync
sync = MemorySync()
backup = sync.full_backup()
print(f'Backup created: {backup}')
# Test recovery (don't apply)
sync.test_recovery(backup)
"

# 2. Agent network topology review
python -m control_plane.distance_travel --analyze-topology

# 3. Crypto key rotation
python -c "
from control_plane.pqcrypto_bridge import PQCryptoBridge
crypto = PQCryptoBridge()
crypto.rotate_all_keys()
"

# 4. SLA performance review
python -c "
from control_plane.inspira_metrics import InspiraMetrics
metrics = InspiraMetrics()
metrics.generate_quarterly_sla_report()
"
```

### Annual

```bash
# 1. Complete system audit + certification
python -m control_plane.harness --annual-audit

# 2. Architecture review + planning
# Manual review of ARCHITECTURE.md + design docs

# 3. Capacity planning
python -m control_plane.cloud_services --capacity-forecast

# 4. Security audit + pentest
# Engage external security team

# 5. Disaster recovery drill
# Execute full failover + recovery procedure
```

---

## Incident Response

### Classification

| Severity | Description | Response Time | Escalation |
|----------|-------------|----------------|-----------|
| **P1** | System down / Data loss risk | 15 min | Page all on-call |
| **P2** | Degraded performance | 1 hour | Page lead on-call |
| **P3** | Minor issue / Workaround exists | 4 hours | Create ticket |
| **P4** | Non-urgent improvement | 1 week | Backlog |

### Response Procedure

#### Phase 1: Immediate Response (0-5 min)
```bash
# 1. Acknowledge alert
# 2. Check system status
python -m control_plane.harness --emergency-status

# 3. Determine severity
# (P1 = system down, P2 = degraded, P3+ = minor)

# 4. Initiate communication
# Page on-call, notify stakeholders
```

#### Phase 2: Diagnosis (5-15 min)
```bash
# 1. Gather logs
tail -f logs/system.log
tail -f logs/error.log

# 2. Check resource constraints
free -h  # Memory
df -h    # Disk
top      # CPU

# 3. Check agent health
python -m control_plane.agent_registry --health-check

# 4. Check external dependencies
redis-cli ping
curl http://localhost:6333/health

# 5. Review recent changes
git log --oneline -n 20
```

#### Phase 3: Mitigation (15-30 min)

**If Memory Exhausted (P1):**
```bash
# Kill least critical processes
pkill -f "swarm.*secondary"
redis-cli FLUSHDB --async
export CAMELOT_TIER=3  # Force edge mode
```

**If Agent Dark (P1):**
```bash
# Force restart
python -m control_plane.agent_registry --restart hermes
python -m control_plane.agent_registry --restart-all
```

**If Ledger Corrupted (P1):**
```bash
# Restore from backup
python -c "
from control_plane.provenance import Provenance
prov = Provenance()
prov.restore_from_backup('backups/ledger_TIMESTAMP.tar.gz')
"
```

**If Performance Degraded (P2):**
```bash
# Switch to lower tier
export CAMELOT_TIER=2
python -c "from control_plane.bifrost_integration import BifrostIntegration; BifrostIntegration().optimize()"

# Kill non-critical tasks
redis-cli EVAL "
for i, key in ipairs(redis.call('keys', 'task:*:secondary')) do
  redis.call('del', key)
end
return 'OK'
" 0
```

#### Phase 4: Resolution
```bash
# 1. Verify fix
python -m control_plane.harness --health-check

# 2. Create incident entry
python -c "
from control_plane.provenance import Provenance
prov = Provenance()
prov.add_entry(
    title='INCIDENT P2: Agent unavailable',
    description='RustClaw dark for 45min, restarted successfully',
    status='RESOLVED',
    remediation='Increased agent restart threshold from 3 to 5 timeouts'
)
"

# 3. Document root cause
# Add to incident log + ticket system

# 4. Notify stakeholders
# Email summary + timeline to stakeholders
```

#### Phase 5: Post-Incident (24-48 hours)
```bash
# 1. Root cause analysis
# Complete RCA with team

# 2. Action items
# Create tickets for preventive measures

# 3. Update runbooks
# Document if this incident revealed new risks

# 4. Monitor extra closely
# Watch for recurrence over next week
```

---

## Scaling & Capacity Planning

### Vertical Scaling (Single Machine)

```bash
# Monitor current utilization
python -c "
from control_plane.system_analyzer import SystemAnalyzer
analyzer = SystemAnalyzer()
profile = analyzer.analyze()
print(f'CPU: {profile.cpu.utilization}% / Available cores: {profile.cpu.total}')
print(f'Memory: {profile.memory.utilized} / {profile.memory.total}')
print(f'Disk: {profile.disk.utilized} / {profile.disk.total}')
"

# Increase resources if needed:
# - Add CPU cores (increase max agent pool)
# - Add RAM (increase Redis maxmemory)
# - Add disk (archive old logs + backups)
```

### Horizontal Scaling (Multiple Nodes)

```bash
# Deploy additional harness instances
# Each can run independently with shared Redis

# 1. Deploy new node
./deploy.sh --node 2

# 2. Configure shared Redis
export REDIS_CLUSTER=true
export REDIS_NODES=node1:6379,node2:6379,node3:6379

# 3. Enable distributed consensus
export DISTANCE_TRAVEL_MODE=cluster

# 4. Verify cluster health
python -c "
from control_plane.consensus_layer import ConsensusLayer
consensus = ConsensusLayer()
consensus.get_cluster_status()
"
```

### Cost Optimization

```bash
# Analyze cloud spending
python -m control_plane.cloud_services --cost-analysis

# Recommendations:
# 1. Use Tier 3 during off-peak hours
# 2. Batch non-critical tasks to nightly runs
# 3. Archive old logs monthly
# 4. Use reserved instances for predictable load
```

---

## Runbooks

### Runbook: Agent Recovery
```bash
#!/bin/bash
# When an agent goes dark

AGENT=$1  # e.g., "hermes"
PORT=$2   # e.g., "8401"

echo "Recovering $AGENT on port $PORT..."

# 1. Kill existing process
lsof -ti:$PORT | xargs kill -9 2>/dev/null

# 2. Verify port is free
sleep 2
nc -zv localhost $PORT && (echo "Port still in use"; exit 1)

# 3. Restart agent
python -m control_plane.agent_registry --start $AGENT &

# 4. Verify health
sleep 5
python -c "
from control_plane.agent_gateway import AgentGateway
gw = AgentGateway()
if gw.probe_agent($PORT).status == 'HEALTHY':
    print('✅ Agent recovered')
    exit(0)
else:
    print('❌ Agent recovery failed')
    exit(1)
"
```

### Runbook: Memory Cleanup
```bash
#!/bin/bash
# When memory usage > 7GB

echo "Emergency memory cleanup..."

# 1. Redis cleanup
redis-cli EVAL "
for i, key in ipairs(redis.call('keys', 'session:*')) do
  redis.call('del', key)
end
return 'OK'
" 0

# 2. Force garbage collection
python -m control_plane.harness --gc

# 3. Clear caches
rm -rf cache/*

# 4. Verify
python -c "
from control_plane.system_analyzer import SystemAnalyzer
profile = SystemAnalyzer().analyze()
print(f'Memory after cleanup: {profile.memory.utilized} / {profile.memory.total}')
"
```

### Runbook: Restore from Backup
```bash
#!/bin/bash
# When data corruption is suspected

BACKUP=$1  # e.g., "backups/ledger_20260618.tar.gz"

echo "Restoring from $BACKUP..."

# 1. Stop system
pkill -f "python.*harness"

# 2. Restore ledger
tar -xzf $BACKUP -C .

# 3. Restore memory state
python -c "
from control_plane.memory_sync import MemorySync
sync = MemorySync()
sync.restore_from_backup('$BACKUP')
"

# 4. Restart
python -m control_plane.boot_sequence --full-test

echo "✅ System restored"
```

---

## Troubleshooting Guide

### System won't boot
1. Check logs: `tail -f logs/system.log`
2. Check Redis: `redis-cli ping`
3. Check Python: `python --version`
4. Clean boot: `./deploy.sh --fresh`

### High latency
1. Check CPU: `top`
2. Check disk I/O: `iostat -x 1`
3. Switch tier: `export CAMELOT_TIER=2`
4. Kill background tasks: `ps aux | grep python`

### Memory leak
1. Identify process: `ps aux | sort -k3 -r | head`
2. Check logs: `grep -i "memory" logs/system.log`
3. Restart process: `pkill -f harness; python -m control_plane.harness`

### Agent not responding
1. Check port: `nc -zv localhost 8401`
2. Check logs: `tail logs/agents/hermes.log`
3. Restart: `python -m control_plane.agent_registry --restart hermes`

---

## Contacts & Escalation

| Role | Contact | Available |
|------|---------|-----------|
| **On-Call SRE** | PagerDuty | 24/7 |
| **Platform Lead** | vizion711@gmail.com | Business hours |
| **Emergency** | Page all on-call via PagerDuty | Immediately |

---

**Status**: ✅ Operations Manual v6.0.0 Ready for Production Use
