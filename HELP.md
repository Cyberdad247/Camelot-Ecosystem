# 🆘 CAMELOT-OS HELP & COMMAND REFERENCE

**Complete guide to using your live CAMELOT-OS cluster**

---

## 📚 Documentation Index

### Quick Start Guides
```
README.md
├─ System overview
├─ Architecture diagram
├─ Quick start (10 minutes)
└─ Performance baselines

DEPLOYMENT_VERIFICATION.md
├─ Post-deployment checks
├─ Testing procedures
├─ First Knight interaction
└─ Observability setup
```

### Operational Guides
```
BARE_METAL_DEPLOYMENT.md
├─ Complete operations manual
├─ Day-2 operations
├─ Scaling procedures
├─ Disaster recovery
└─ Troubleshooting

KNIGHT_INTERACTION_GUIDE.md
├─ Chat with Knights
├─ Decision examples
├─ Real-world scenarios
└─ Advanced patterns

ARCHITECTURE_USAGE_GUIDE.md
├─ How the system works
├─ Optimization patterns
├─ Cost vs performance
└─ Common mistakes
```

### Live Operations
```
LIVE_MONITORING_DASHBOARD.md
├─ Real-time monitoring commands
├─ Grafana dashboards
├─ Health checks
└─ Emergency procedures

SYSTEM_LIVE_STATUS.md
├─ Current system state
├─ What's running now
├─ Quick commands
└─ Next steps
```

### Design & Implementation
```
UI_UX_ARCHITECTURE.md
├─ Service-to-UI mapping
├─ API contracts
├─ Component specs
└─ Frontend ready

EPIC_UI_DESIGN.md
├─ Complete UI mockups
├─ Component hierarchy
├─ Design system
└─ Implementation roadmap
```

---

## 🎯 Common Tasks (Copy-Paste Ready)

### Check Cluster Health

```bash
# Quick status
curl -s http://192.168.1.10:8443/health | jq .

# Full check
for node in 192.168.1.{10,11,12}; do
  echo "Node: $node"
  curl -s http://$node:8443/health | jq '.status'
done
```

### Chat with Knights

```bash
# Ask for routing decision
curl -X POST http://192.168.1.10:8400/knight/decide \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Route this request optimally",
    "confidence_threshold": 0.85,
    "consensus_required": false
  }' | jq .

# Ask for consensus decision
curl -X POST http://192.168.1.10:8443/consensus/propose \
  -H "Content-Type: application/json" \
  -d '{
    "proposal": "Enable caching",
    "priority": "medium"
  }' | jq .

# Get triage score
curl -X POST http://192.168.1.10:8500/knight/triage \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Should we scale?",
    "factors": {"load": 0.5, "cpu": 0.4}
  }' | jq .
```

### Monitor in Real-Time

```bash
# Terminal 1: Consensus
watch -n 2 'curl -s http://192.168.1.10:8443/health | jq "{status: .status, agreement: .nodes_in_agreement, latency: .latency_ms}"'

# Terminal 2: Agents
watch -n 3 'curl -s http://192.168.1.10:8400/agents/status | jq "{total: (.agents | length), healthy: (.agents | map(select(.healthy==true)) | length)}"'

# Terminal 3: Sync
watch -n 5 'curl -s http://192.168.1.10:6379/knight/sync-status | jq "{lag: .replication_lag_ms, conflicts: .conflicts_detected}"'
```

### View Knowledge Pyramid

```bash
# L1 (Redis) cache
redis-cli -h 192.168.1.10 KEYS "user:*" | head -5

# L1.5 (Qdrant) vectors
curl -s http://192.168.1.30:6333/collections/knowledge | jq '.result.points_count'

# L2 (CloudBrain) persistent
curl -X POST http://cloudbrain/query \
  -d 'SELECT * FROM decisions WHERE confidence > 0.90 LIMIT 5'
```

### Watch Live Logs

```bash
# SSH to node 1
ssh root@192.168.1.10

# Watch consensus decisions
journalctl -u camelot-consensus -f | grep -E "proposal|latency"

# Watch agent routing
journalctl -u camelot-agents -f | grep "route\|decision"

# Watch sync operations
journalctl -u camelot-sync -f | grep "sync\|lag"

# Watch for errors (should be quiet)
journalctl PRIORITY=err -u camelot-\* -f
```

### Manage Services

```bash
# Check all services
systemctl list-units camelot-* --no-pager

# Restart a service
systemctl restart camelot-consensus
systemctl restart camelot-sync
systemctl restart camelot-agents

# Check service logs
journalctl -u camelot-consensus -n 50
journalctl -u camelot-agents -p err -n 20
```

---

## 🔍 Troubleshooting Commands

### Consensus Issues

```bash
# Check consensus health
curl -s http://192.168.1.10:8443/health | jq .

# Check which node is leader
curl -s http://192.168.1.10:8443/health | jq '.role'

# Check if all nodes agree
for node in 192.168.1.{10,11,12}; do
  ssh root@$node "curl -s http://localhost:8443/health | jq '.nodes_in_agreement'"
done

# Restart consensus if stuck
ssh root@192.168.1.10 systemctl restart camelot-consensus
sleep 10
curl -s http://192.168.1.10:8443/health | jq '.nodes_in_agreement'
```

### Agent Issues

```bash
# Count healthy agents
curl -s http://192.168.1.10:8400/agents/status | jq '.agents | map(select(.healthy==true)) | length'

# Show unhealthy agents
curl -s http://192.168.1.10:8400/agents/status | jq '.agents[] | select(.healthy==false)'

# Show agents by node
curl -s http://192.168.1.10:8400/agents/status | jq '.agents | group_by(.node) | map({node: .[0].node, count: length})'

# Restart agents
ssh root@192.168.1.10 systemctl restart camelot-agents
```

### Sync Issues

```bash
# Check sync status
curl -s http://192.168.1.10:6379/knight/sync-status | jq .

# Check replication lag
curl -s http://192.168.1.10:6379/knight/sync-status | jq '.replication_lag_ms'

# Check for conflicts
curl -s http://192.168.1.10:6379/knight/sync-status | jq '.conflicts_detected'

# Force sync cycle
curl -X POST http://192.168.1.10:6379/knight/force-sync
```

### System Issues

```bash
# Check CPU/Memory on all nodes
for node in 192.168.1.{10,11,12}; do
  echo "Node: $node"
  ssh root@$node "free -h && echo && top -bn1 | head -3"
done

# Check disk usage
for node in 192.168.1.{10,11,12}; do
  echo "Node: $node"
  ssh root@$node "df -h /opt/camelot"
done

# Check network connectivity
for node in 192.168.1.{10,11,12}; do
  echo "Testing: $node"
  ping -c 1 $node && echo "OK" || echo "FAILED"
done
```

---

## 📊 Monitoring Dashboards

### Grafana (http://localhost:3000)
```
Dashboards Available:
├─ System Overview        - CPU, Memory, Network, Disk
├─ Consensus Performance  - Latency, agreement rate, proposals
├─ Knowledge Sync         - Replication lag, conflicts, consistency
├─ Agent Network          - Load distribution, routing, confidence
├─ Error Rates            - By service, by node, trending
└─ SLO Dashboard          - Availability, latency SLOs, error budget
```

### Prometheus (http://localhost:9090)
```
Query Examples:
├─ camelot_consensus_proposals_total
├─ camelot_agent_health_status
├─ camelot_sync_replication_lag_ms
├─ camelot_error_rate_percent
└─ node_memory_MemAvailable_bytes
```

### Jaeger (http://localhost:16686)
```
Features:
├─ Distributed tracing
├─ Request flow visualization
├─ Latency analysis
└─ Service dependencies
```

---

## 🚨 Emergency Procedures

### Consensus Broken (< 2/3 Agreement)

```bash
# 1. Check all nodes
for node in 192.168.1.{10,11,12}; do
  echo "Node: $node"
  ping -c 1 $node
done

# 2. Check service status
ssh root@192.168.1.10 systemctl status camelot-consensus

# 3. Restart service
ssh root@192.168.1.10 systemctl restart camelot-consensus

# 4. Verify recovery
sleep 10
curl -s http://192.168.1.10:8443/health | jq '.nodes_in_agreement'
```

### Agent Network Degraded (< 20/24)

```bash
# 1. Check agent status
curl -s http://192.168.1.10:8400/agents/status | jq '.agents | map(select(.healthy==true)) | length'

# 2. Which nodes have issues?
curl -s http://192.168.1.10:8400/agents/status | jq '.agents | group_by(.node) | map({node: .[0].node, healthy: map(select(.healthy==true)) | length})'

# 3. Restart agents
ssh root@192.168.1.10 systemctl restart camelot-agents

# 4. Verify
sleep 5
curl -s http://192.168.1.10:8400/agents/status | jq '.agents | map(select(.healthy==true)) | length'
```

### High Sync Lag (> 500ms)

```bash
# 1. Check current lag
curl -s http://192.168.1.10:6379/knight/sync-status | jq '.replication_lag_ms'

# 2. Check Redis memory
ssh root@192.168.1.10 redis-cli INFO memory

# 3. Check Qdrant
curl -s http://192.168.1.30:6333/collections/knowledge | jq '.result.points_count'

# 4. Force sync
curl -X POST http://192.168.1.10:6379/knight/force-sync

# 5. Monitor improvement
watch -n 2 'curl -s http://192.168.1.10:6379/knight/sync-status | jq .replication_lag_ms'
```

### High CPU/Memory

```bash
# 1. Check which node
for node in 192.168.1.{10,11,12}; do
  echo "Node: $node"
  ssh root@$node "top -bn1 | grep -E 'Cpu|Mem'"
done

# 2. Check which service
ssh root@192.168.1.10 ps aux | grep camelot | head -5

# 3. Reduce load
# Option A: Restart service
systemctl restart camelot-sync

# Option B: Enable compression
curl -X POST http://192.168.1.10:8400/configure \
  -d '{"compression": "enabled"}'

# Option C: Increase TTL (reduce refresh rate)
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

---

## 🔧 Configuration Commands

### Enable Caching
```bash
curl -X POST http://192.168.1.10:8400/configure \
  -d '{"cache_ttl": 300, "compression": "enabled"}'
```

### Optimize for Latency
```bash
curl -X POST http://192.168.1.10:8400/configure \
  -d '{"routing_strategy": "geographic", "batching": "disabled"}'
```

### Optimize for Throughput
```bash
curl -X POST http://192.168.1.10:8400/configure \
  -d '{"routing_strategy": "least_loaded", "batching": "enabled"}'
```

### Enable Autonomous Decisions
```bash
curl -X POST http://192.168.1.10:8500/knight/enable-autonomy \
  -d '{"confidence_threshold": 0.90, "require_approval": false}'
```

---

## 📖 When to Read What

**I want to...**

```
Understand the system
└─ Read: README.md

Deploy/troubleshoot
└─ Read: BARE_METAL_DEPLOYMENT.md

Chat with Knights
└─ Read: KNIGHT_INTERACTION_GUIDE.md

Optimize performance
└─ Read: ARCHITECTURE_USAGE_GUIDE.md

Monitor the cluster
└─ Read: LIVE_MONITORING_DASHBOARD.md

Build a frontend
└─ Read: UI_UX_ARCHITECTURE.md + EPIC_UI_DESIGN.md

See current status
└─ Read: SYSTEM_LIVE_STATUS.md
```

---

## 🆘 Getting Help

### For Specific Issues

```
Service won't start?
└─ BARE_METAL_DEPLOYMENT.md → Troubleshooting section

Consensus latency high?
└─ LIVE_MONITORING_DASHBOARD.md → Deep Dive Investigation

Can't route requests?
└─ KNIGHT_INTERACTION_GUIDE.md → Routing Knight examples

Need to scale?
└─ ARCHITECTURE_USAGE_GUIDE.md → Scaling section
```

### For Knowledge

```
How does consensus work?
└─ README.md → Architecture section

What are Knights?
└─ KNIGHT_INTERACTION_GUIDE.md → What Are Knights section

How does the knowledge pyramid work?
└─ ARCHITECTURE_USAGE_GUIDE.md → Knowledge Pyramid section

How do I optimize my system?
└─ ARCHITECTURE_USAGE_GUIDE.md → Optimizing for Your Use Case
```

---

## 🎯 Quick Reference Matrix

| Task | Command | File |
|------|---------|------|
| Check health | `curl http://192.168.1.10:8443/health` | - |
| Chat with Knight | `curl -X POST http://192.168.1.10:8400/knight/decide` | KNIGHT_INTERACTION_GUIDE.md |
| View dashboards | Go to http://localhost:3000 | LIVE_MONITORING_DASHBOARD.md |
| Watch logs | `journalctl -u camelot-consensus -f` | BARE_METAL_DEPLOYMENT.md |
| Check metrics | `curl http://192.168.1.10:8000/metrics` | LIVE_MONITORING_DASHBOARD.md |
| Restart service | `systemctl restart camelot-consensus` | BARE_METAL_DEPLOYMENT.md |
| Scale cluster | See ARCHITECTURE_USAGE_GUIDE.md | ARCHITECTURE_USAGE_GUIDE.md |
| Emergency help | See Emergency Procedures above | BARE_METAL_DEPLOYMENT.md |

---

## 📞 Support Resources

**Documentation Files** (all in CAMELOT_OS directory):
- README.md
- KNIGHT_INTERACTION_GUIDE.md
- ARCHITECTURE_USAGE_GUIDE.md
- BARE_METAL_DEPLOYMENT.md
- LIVE_MONITORING_DASHBOARD.md
- UI_UX_ARCHITECTURE.md
- SYSTEM_LIVE_STATUS.md
- HELP.md (this file)

**Dashboards**:
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090
- Jaeger: http://localhost:16686

**Direct Access**:
- Consensus API: http://192.168.1.10:8443
- Agent Registry: http://192.168.1.10:8400
- Knowledge Sync: http://192.168.1.10:6379
- Metrics: http://192.168.1.10:8000

---

## ✨ Pro Tips

1. **Always check health first**
   ```bash
   curl -s http://192.168.1.10:8443/health | jq .
   ```

2. **Open Grafana in a browser tab**
   - http://localhost:3000
   - Keep it open for visual monitoring

3. **Use watch for real-time updates**
   ```bash
   watch -n 2 'curl -s http://192.168.1.10:8443/health | jq .status'
   ```

4. **SSH to nodes for deep investigation**
   ```bash
   ssh root@192.168.1.10
   journalctl -u camelot-consensus -f
   ```

5. **Save helpful commands as aliases**
   ```bash
   alias camelot-health='curl -s http://192.168.1.10:8443/health | jq .'
   alias camelot-agents='curl -s http://192.168.1.10:8400/agents/status | jq ".agents | length"'
   ```

---

**🎉 You're all set! Your CAMELOT-OS cluster is operational and you have all the tools to monitor and manage it.**

**Start here:**
1. Open 3 terminals with the monitoring commands
2. Open Grafana dashboard
3. Make your first Knight decision
4. Read the documentation that matches your needs

**Need more help?** All documentation is in the CAMELOT_OS directory. Pick the file that matches what you want to do! 📚

