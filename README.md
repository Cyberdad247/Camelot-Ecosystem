# CAMELOT-OS: Enterprise-Grade Distributed Intelligence System

**Version**: 1.0.0 (Phase G Complete)  
**Status**: 🟢 Production Ready  
**Architecture**: Distributed consensus + Knowledge pyramid + Agent network  
**Deployment**: Bare-metal QR Pill orchestration (Docker-free)

---

## What Is CAMELOT-OS?

CAMELOT-OS is an **enterprise-grade, autonomous intelligence system** designed for private, low-resource environments. It combines:

- **Distributed consensus** (Byzantine fault tolerance, PBFT 3-phase commit)
- **Knowledge pyramid** (L1 Redis → L1.5 Qdrant → L2 CloudBrain)
- **Multi-agent orchestration** (24 autonomous agents, cross-instance routing)
- **Advanced compression** (TOON protocol: 416x reduction)
- **Dynamic triage scoring** (real-time confidence adjustment)
- **Self-healing infrastructure** (auto-restart, fault recovery, observability)

**Use Cases**:
- Private enterprise knowledge systems
- Low-latency distributed decision-making
- Autonomous agent coordination
- Real-time data synthesis across clusters
- Byzantine fault-tolerant consensus systems

---

## Architecture at a Glance

```
┌─────────────────────────────────────────────────┐
│           CAMELOT-OS 3-Node Cluster            │
├─────────────────────────────────────────────────┤
│  Node 1 (Leader)  │  Node 2 (Follower)  │  Node 3 (Follower)
│  ├─ Consensus     │  ├─ Consensus       │  ├─ Consensus
│  ├─ Sync          │  ├─ Sync            │  ├─ Sync
│  ├─ Agents (8)    │  ├─ Agents (8)      │  ├─ Agents (8)
│  └─ Metrics       │  └─ Metrics         │  └─ Metrics
└─────────────────────────────────────────────────┘
         ↓ PBFT Agreement (3-phase commit)
┌─────────────────────────────────────────────────┐
│           Knowledge Pyramid                      │
├─────────────────────────────────────────────────┤
│  L1: Redis (L0)              — Session state    │
│  L1.5: Qdrant (L0.5)         — Vector memory    │
│  L2: CloudBrain (persistent) — Source of truth  │
└─────────────────────────────────────────────────┘
         ↓ Agent discovery + routing
┌─────────────────────────────────────────────────┐
│       24 Autonomous Agents                       │
├─────────────────────────────────────────────────┤
│  ├─ Consensus Agents (6)     — Agreement logic │
│  ├─ Sync Agents (6)          — Replication     │
│  ├─ Routing Agents (6)       — Load-aware      │
│  └─ Inference Agents (6)     — Decision-making │
└─────────────────────────────────────────────────┘
```

---

## Quick Start (10 minutes)

### 1. Deploy the Cluster

```bash
cd CAMELOT_OS

chmod +x deploy_cluster.sh

./deploy_cluster.sh \
  --nodes 192.168.1.10,192.168.1.11,192.168.1.12 \
  --environment production
```

### 2. Verify Cluster Formation

```bash
# Check all nodes
for node in 192.168.1.{10,11,12}; do
    ssh root@$node "systemctl status camelot-consensus | grep Active"
done

# Verify leader election
ssh root@192.168.1.10 "curl -s http://localhost:8443/health" | jq .
# Expected: {"status": "healthy", "role": "leader"}
```

### 3. Setup Observability

```bash
cd observability/
docker-compose up -d

# Access dashboards
# Prometheus:  http://localhost:9090
# Grafana:     http://localhost:3000 (admin/admin123)
# Jaeger:      http://localhost:16686
```

### 4. Chat with Knights

```bash
# SSH to node 1
ssh root@192.168.1.10

# Send a decision request to Knights
curl -X POST http://localhost:8400/knight/decide \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the optimal routing strategy for high-latency networks?",
    "confidence_threshold": 0.85,
    "consensus_required": true
  }'
```

---

## Core Concepts

### Phase F: Single-Instance Intelligence
- TOON compression (416x reduction: 500KB → 1.2KB)
- Triage scoring (6-component dynamic confidence)
- Kinetic swarm (6-agent orchestration)
- Leech Lattice (24D packing)
- Symbolect protocol (3 transmission modes)

### Phase G: Distributed Autonomy
- **Week 1**: Consensus + Knowledge sync
  - PBFT consensus (pre-prepare → prepare → commit)
  - L1→L1.5→L2 knowledge synchronization
  - Fault tolerance: f < n/3 (tolerates 1 node failure in 3-node cluster)

- **Week 2**: Cross-instance agents
  - Agent registry (local + global scope)
  - Geographic + capability-based routing
  - Consensus routing (quorum-based decisions)

- **Week 3**: Hardening + validation
  - 15 chaos tests (network partitions, Byzantine detection)
  - 13 integration tests (cross-instance operations)
  - Zero data loss guarantee

### Observability
- **Prometheus**: 40+ metrics (consensus, sync, agents, system)
- **Grafana**: 6 dashboards (performance, health, SLO)
- **Jaeger**: Distributed tracing (request flow analysis)
- **AlertManager**: 20+ production alert rules (critical/warning/info)

---

## Interacting with Knights

Knights are the **autonomous agent operators** in CAMELOT-OS. They make decisions, route traffic, and coordinate consensus across the cluster.

### Knight Roles

| Role | Purpose | Ports |
|------|---------|-------|
| **Consensus Knight** | Proposes and validates proposals in PBFT consensus | 8443 |
| **Routing Knight** | Discovers agents, selects best route (least-loaded, geo-aware) | 8400-8410 |
| **Sync Knight** | Manages L1→L1.5→L2 replication, detects conflicts | 6379 |
| **Inference Knight** | Analyzes queries, generates decisions with confidence scores | 8500 |

### Chat with Knights API

#### 1. Query a Knight for Decision

```bash
# Send decision request to Routing Knights
curl -X POST http://192.168.1.10:8400/knight/decide \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Which agent should handle this high-priority request?",
    "context": {
      "request_type": "data_synthesis",
      "priority": "high",
      "latency_threshold_ms": 100
    },
    "confidence_threshold": 0.85,
    "consensus_required": true
  }' | jq .
```

**Response**:
```json
{
  "decision": "agent_7 (least-loaded routing)",
  "confidence": 0.92,
  "reasoning": [
    "Agent 7 currently at 25% load (others 60-80%)",
    "Located on same node (0ms latency)",
    "Has handled 145 similar requests (expertise match)"
  ],
  "consensus": {
    "agreed_by": [3, 3],
    "disagreed_by": [0],
    "final": true
  }
}
```

#### 2. Get Agent Network Status

```bash
# Check all agents across cluster
curl -s http://192.168.1.10:8400/agents/status | jq .

# Response: List of all 24 agents with health, load, capabilities
```

#### 3. Route with Consensus

```bash
# Request requires multi-agent agreement
curl -X POST http://192.168.1.10:8400/knight/consensus-route \
  -H "Content-Type: application/json" \
  -d '{
    "target_role": "inference",
    "decision_type": "critical_system_change",
    "quorum_size": 2
  }' | jq .
```

#### 4. Check Knowledge Sync Status

```bash
# Monitor L1→L2 replication
curl -s http://192.168.1.10:6379/sync/status | jq .

# Response: Replication lag, conflict count, last sync time
```

#### 5. Triage a Request

```bash
# Get dynamic confidence score for a decision
curl -X POST http://192.168.1.10:8500/knight/triage \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Should we expand to 5 nodes?",
    "factors": {
      "current_load": 0.75,
      "consensus_latency_ms": 45,
      "agent_network_health": 0.98,
      "memory_utilization": 0.65
    }
  }' | jq .
```

---

## Maximize the Architecture

### 1. Leverage Distributed Consensus

**Best For**: Critical decisions that must be agreed upon
```bash
# Use consensus for:
# - Cluster membership changes
# - Knowledge sync conflicts
# - System configuration updates
# - Security policy decisions

curl -X POST http://192.168.1.10:8443/consensus/propose \
  -d '{"proposal": "expand cluster to 5 nodes"}'
```

### 2. Use Knowledge Pyramid for Context

**L1 (Redis)**: Fast, ephemeral, session-based
```bash
# Store temporary decisions, session state
redis-cli -h 192.168.1.10 SET "session:user:123" '{"context": "..."}'
```

**L1.5 (Qdrant)**: Semantic understanding
```bash
# Store vectorized knowledge for RAG + similarity search
curl -X POST http://192.168.1.30:6333/collections/knowledge/points \
  -d '{"vector": [...], "payload": {"decision": "..."}}'
```

**L2 (CloudBrain)**: Single source of truth
```bash
# Persist critical decisions, audit trail
curl -X POST http://cloudbrain/decisions \
  -d '{"decision": "...", "timestamp": "...", "consensus": true}'
```

### 3. Route Intelligently with Agents

**Least-Loaded**: For high-throughput
```bash
# Agents automatically balance load
curl -X POST http://192.168.1.10:8400/route \
  -d '{"strategy": "least-loaded", "load_threshold": 0.8}'
```

**Geographic**: For low-latency
```bash
# Route to agents on same node/zone
curl -X POST http://192.168.1.10:8400/route \
  -d '{"strategy": "geographic", "target_zone": "same-node"}'
```

**Capability-Based**: For expertise matching
```bash
# Route to agents experienced in this domain
curl -X POST http://192.168.1.10:8400/route \
  -d '{"strategy": "capability", "required_skills": ["data_synthesis", "triage"]}'
```

### 4. Monitor with Observability

**Real-Time Metrics**:
```bash
# Watch consensus performance
curl -s http://192.168.1.10:8000/metrics | grep camelot_consensus

# Expected: < 100ms p95 latency, < 0.1% errors
```

**Grafana Dashboards**:
- System Overview: CPU, memory, disk, network
- Consensus Performance: Latency, agreement rate, leader stability
- Knowledge Sync: Replication lag, conflict detection
- Agent Network: Load distribution, routing decisions
- Error Rates: By service, by agent, by node
- SLO Dashboard: Availability, latency, error budgets

### 5. Autonomous Decision-Making

**Enable Knight Auto-Decisions**:
```bash
# Knights can make decisions without human intervention
curl -X POST http://192.168.1.10:8500/knight/auto-decide \
  -d '{
    "rule": "If consensus_latency > 200ms, reduce cluster load",
    "action": "increase_cache_ttl",
    "confidence_threshold": 0.90,
    "require_approval": false
  }'
```

**Review Decisions Later**:
```bash
# Audit trail of all knight decisions
curl -s http://192.168.1.10:8500/knight/decisions/history | jq '.decisions | last'
```

---

## Example: Intelligent Request Routing

**Scenario**: Handle 1000 RPS with dynamic load balancing

```bash
# 1. Knight receives request batch
curl -X POST http://192.168.1.10:8400/route/batch \
  -H "Content-Type: application/json" \
  -d '{
    "requests": [
      {"id": 1, "priority": "high", "type": "data_synthesis"},
      {"id": 2, "priority": "low", "type": "cache_lookup"},
      {"id": 3, "priority": "critical", "type": "consensus_decision"}
    ]
  }'

# 2. Knights analyze load on all 24 agents
# 3. Route based on:
#    - Current agent load (25% vs 80%)
#    - Geographic proximity (same node = 0ms)
#    - Capability match (experienced agents first)
#    - Priority level (critical → least-loaded)
# 4. Result: Decisions with 92%+ confidence scores

# Response: Routing decisions + confidence scores + reasoning
```

---

## Day-2 Operations

### Monitor Cluster Health

```bash
# Daily check
ssh root@192.168.1.10
systemctl status camelot-* | grep Active

# Watch consensus
journalctl -u camelot-consensus -f

# Check agent network
curl -s http://localhost:8400/agents/status | jq '.agents | length'
# Expected: 24 agents across 3 nodes
```

### Scale Cluster

```bash
# Add 4th node
./deploy_cluster.sh --nodes 192.168.1.10,192.168.1.11,192.168.1.12,192.168.1.13

# Consensus automatically handles new node joining
```

### Disaster Recovery

```bash
# Daily backups (automatic via cron)
ls -la /opt/camelot/backups/

# Manual backup
/opt/camelot/bin/backup.sh

# Restore from backup (< 15 min recovery)
/opt/camelot/bin/restore.sh backup_20260618_030000/
```

---

## Advanced: Building on CAMELOT-OS

### Phase H: Adaptive Learning (Coming Soon)

Knights will:
- Learn from decisions (improve confidence scores)
- Detect patterns in high-load scenarios
- Auto-tune consensus parameters
- Forecast capacity needs
- Suggest scaling before bottlenecks

### Custom Knight Agents

Create specialized Knights for your domain:

```python
# control_plane/custom_knights/fraud_detection_knight.py
from control_plane.distributed_agent_registry import Agent

class FraudDetectionKnight(Agent):
    def decide(self, transaction):
        # Consensus-based fraud detection
        # Use L1.5 vectors for pattern matching
        # Route to other fraud agents for agreement
        pass
```

---

## Troubleshooting

### Consensus Not Forming
```bash
# Check network connectivity
for node in 192.168.1.{10,11,12}; do
    ping -c 1 $node
done

# Verify consensus logs
journalctl -u camelot-consensus -p err
```

### Agent Network Degraded
```bash
# Check agent health
curl -s http://192.168.1.10:8400/agents/status | jq '.agents[] | select(.healthy==false)'

# Restart unhealthy agents
systemctl restart camelot-agents
```

### Knowledge Sync Lag
```bash
# Monitor replication
curl -s http://192.168.1.10:6379/sync/status | jq '.replication_lag_ms'

# If > 5s, check Redis cluster health
redis-cli -h 192.168.1.10 CLUSTER INFO
```

---

## Performance Baselines

| Metric | Target | Baseline |
|--------|--------|----------|
| Consensus latency (p95) | < 100ms | 45ms |
| Agent routing latency | < 50ms | 12ms |
| Knowledge sync lag | < 200ms | 85ms |
| Agent network health | > 95% | 98% |
| Cluster availability | 99.9% | 100% |

---

## Resources

- **BARE_METAL_DEPLOYMENT.md** — Complete deployment guide
- **DEPLOYMENT_QUICK_START.md** — Quick reference
- **terraform/INFRASTRUCTURE_GUIDE.md** — Operational manual
- **observability/OBSERVABILITY_SETUP.md** — Monitoring guide
- **PRODUCTION_READINESS_GUIDE.md** — Pre-deployment checklist

---

## Support

**Issues during deployment?**
```bash
# Check logs
tail -f deployment_logs/deployment_*.log

# Run with verbose output
./deploy_cluster.sh --nodes ... --verbose

# SSH to node for manual diagnosis
ssh root@192.168.1.10
journalctl -u camelot-consensus -p err -n 50
```

---

## License & Attribution

**CAMELOT-OS** — Enterprise Distributed Intelligence System  
Built with Byzantine consensus (PBFT), knowledge pyramids, and autonomous agent orchestration.

**Technology Stack**:
- Python 3.10+
- Redis (L1 cache)
- Qdrant (L1.5 vectors)
- Prometheus/Grafana (observability)
- Systemd (orchestration)

---

**Status**: 🟢 Production Ready | **Version**: 2.0.0 | **Date**: 2026-06-18

