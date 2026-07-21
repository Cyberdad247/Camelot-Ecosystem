# Knight Interaction Guide: Maximizing Distributed Architecture

**Date**: 2026-06-18  
**Version**: 1.0  
**Purpose**: Practical examples for chatting with Knights to leverage CAMELOT-OS fully

---

## What Are Knights?

Knights are **autonomous agent operators** that make decisions, coordinate consensus, and route traffic across your 3-node CAMELOT-OS cluster.

```
Your Request
    ↓
Knight receives & analyzes
    ↓
Proposes decision (with confidence score)
    ↓
Other Knights validate (consensus)
    ↓
Decision executed + logged
    ↓
You get response with reasoning
```

---

## Knight Types & Their Ports

| Knight | Role | Port | Interaction |
|--------|------|------|-------------|
| **Consensus** | Proposes/validates using PBFT | 8443 | Critical decisions |
| **Routing** | Discovers agents, selects best route | 8400-8410 | Request routing |
| **Sync** | Manages L1→L2 replication | 6379 | Knowledge consistency |
| **Inference** | Analyzes & scores decisions | 8500 | Dynamic triage |

---

## Quick Start: Chat with Your First Knight

### 1. SSH to Node 1

```bash
ssh root@192.168.1.10
```

### 2. Ask a Routing Knight for Help

```bash
curl -X POST http://localhost:8400/knight/decide \
  -H "Content-Type: application/json" \
  -d '{
    "query": "I have 1000 incoming requests. How should I route them?",
    "context": {
      "request_volume": 1000,
      "request_types": ["data_synthesis", "cache_lookup", "consensus"],
      "priority_distribution": {"high": 100, "medium": 500, "low": 400},
      "latency_requirement_ms": 200
    },
    "confidence_threshold": 0.85,
    "consensus_required": true
  }' | jq .
```

**Knight Response** (example):
```json
{
  "decision": "Distribute across all 24 agents using load-aware routing",
  "confidence": 0.91,
  "reasoning": [
    "Current cluster load: 45% (healthy)",
    "Agent capacity: 2000+ RPS available",
    "Route 100 high-priority → least-loaded (Agent 3, 8, 15)",
    "Route 500 medium → balanced load (agents 1-24)",
    "Route 400 low → background queue (batch processing)"
  ],
  "consensus": {
    "routing_knights_agreed": 3,
    "disagreed": 0,
    "final": true
  },
  "expected_latency_ms": 45,
  "confidence_factors": {
    "load_available": 0.95,
    "agent_health": 0.98,
    "network_health": 0.99,
    "experience_match": 0.92
  }
}
```

---

## Real-World Scenarios

### Scenario 1: "I Need Fast Consensus"

**Problem**: You need to make a critical cluster decision in < 100ms

```bash
# Ask Consensus Knight for fast agreement
curl -X POST http://localhost:8443/knight/fast-consensus \
  -H "Content-Type: application/json" \
  -d '{
    "proposal": "Temporarily increase agent cache TTL from 60s to 300s",
    "reason": "Spike in repeated queries detected",
    "expected_impact": "25% reduction in database load",
    "rollback_plan": "Auto-revert to 60s if CPU > 80%",
    "priority": "high"
  }' | jq .
```

**Knight Response**:
```json
{
  "proposal_id": "prop_8f2c1a9e",
  "status": "agreed",
  "phases": {
    "pre_prepare": {
      "duration_ms": 15,
      "nodes_acknowledged": 3
    },
    "prepare": {
      "duration_ms": 20,
      "nodes_prepared": 3
    },
    "commit": {
      "duration_ms": 10,
      "executed_at": "2026-06-18T16:45:32Z"
    }
  },
  "total_consensus_time_ms": 45,
  "all_nodes_executing": true,
  "monitoring": "Enabled - auto-rollback if CPU > 80%"
}
```

---

### Scenario 2: "Route This Request Intelligently"

**Problem**: You have a data synthesis request that needs the fastest possible response

```bash
# Ask Routing Knight for optimal routing
curl -X POST http://localhost:8400/knight/intelligent-route \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "req_xyz789",
    "task": "Synthesize customer data from 5 sources",
    "requirements": {
      "expertise": ["data_synthesis", "cross_source_aggregation"],
      "latency_max_ms": 150,
      "data_freshness": "within 5 minutes"
    },
    "context": {
      "user_priority": "enterprise",
      "similar_requests_count": 247,
      "time_of_day": "peak_hours"
    }
  }' | jq .
```

**Knight Response**:
```json
{
  "routing_decision": "Agent 7 on Node 1",
  "confidence": 0.94,
  "reasons": [
    "Agent 7: 247 similar requests handled (99.2% success)",
    "Currently at 25% load (others 60-85%)",
    "On same node (0ms latency)",
    "Has cached 80% of required data sources"
  ],
  "backup_agents": [
    {"agent": 12, "confidence": 0.88, "reason": "Second most experienced"},
    {"agent": 19, "confidence": 0.82, "reason": "Least loaded"}
  ],
  "expected_latency_ms": 42,
  "estimated_success": 0.99,
  "data_sources": {
    "cached": ["source_a", "source_b", "source_c"],
    "live_fetch": ["source_d", "source_e"]
  }
}
```

---

### Scenario 3: "Check If My Decision Is Safe"

**Problem**: You want to validate a risky system change before executing

```bash
# Ask Inference Knight for triage/safety check
curl -X POST http://localhost:8500/knight/validate-decision \
  -H "Content-Type: application/json" \
  -d '{
    "decision": "Expand cluster from 3 to 5 nodes",
    "risk_factors": {
      "cluster_restart_required": true,
      "data_migration_needed": true,
      "potential_downtime_minutes": 5
    },
    "benefits": {
      "capacity_increase": "50%",
      "latency_reduction": "20%",
      "reliability_improvement": "4-nines to 5-nines"
    },
    "timing": "immediate"
  }' | jq .
```

**Knight Response**:
```json
{
  "decision": "APPROVED with conditions",
  "confidence": 0.87,
  "safety_score": 0.89,
  "risks": {
    "cluster_restart": {
      "severity": "high",
      "mitigation": "Execute during 2:00-3:00 AM (lowest traffic)",
      "impact": "All consensus halted for 5 minutes"
    },
    "data_migration": {
      "severity": "medium",
      "mitigation": "Use async migration with fallback",
      "impact": "No data loss, eventual consistency maintained"
    }
  },
  "recommendations": [
    "Schedule for off-peak hours (2:00-3:00 AM)",
    "Enable continuous backup before starting",
    "Monitor consensus latency during migration",
    "Have rollback plan ready (< 2 min revert)"
  ],
  "success_probability": 0.92,
  "estimated_completion_minutes": 15
}
```

---

### Scenario 4: "I Need Multi-Agent Agreement"

**Problem**: Your decision requires consensus from multiple Knights

```bash
# Ask for consensus on a critical business decision
curl -X POST http://localhost:8400/knight/multi-agent-consensus \
  -H "Content-Type: application/json" \
  -d '{
    "decision": "Should we enable automatic cost optimization?",
    "factors": {
      "current_cost": 1025,
      "projected_cost_optimized": 600,
      "savings_percent": 41,
      "implementation_effort_hours": 4,
      "risk_of_service_degradation": 0.02
    },
    "required_agreement": {
      "routing_knights": 2,
      "inference_knights": 2,
      "consensus_knights": 1
    }
  }' | jq .
```

**Knight Response**:
```json
{
  "decision": "YES - Enable cost optimization",
  "confidence": 0.91,
  "consensus_details": {
    "routing_knights": {
      "agreed": 2,
      "disagreed": 0,
      "reasoning": ["Load will remain optimal", "Cost reduction doesn't impact performance"]
    },
    "inference_knights": {
      "agreed": 2,
      "disagreed": 0,
      "reasoning": ["Risk is minimal (2%)", "ROI is excellent (41% savings)"]
    },
    "consensus_knights": {
      "agreed": 1,
      "disagreed": 0,
      "reasoning": ["All parties agreed, consensus not required"]
    }
  },
  "implementation_steps": [
    {
      "step": 1,
      "action": "Enable aggressive caching (30 min TTL)",
      "expected_savings": "$200/month"
    },
    {
      "step": 2,
      "action": "Auto-scale down during off-peak",
      "expected_savings": "$150/month"
    },
    {
      "step": 3,
      "action": "Compress data in transit (TOON protocol)",
      "expected_savings": "$75/month"
    }
  ],
  "rollout_time_minutes": 15,
  "monitoring_required": true
}
```

---

### Scenario 5: "Monitor Knowledge Sync Health"

**Problem**: You want to ensure your L1→L2 knowledge pyramid is consistent

```bash
# Check sync status from Sync Knight
curl -s http://localhost:6379/knight/sync-status | jq .
```

**Knight Response**:
```json
{
  "sync_health": "excellent",
  "replication_lag_ms": 45,
  "conflict_detection": "none",
  "sync_efficiency": 0.99,
  "details": {
    "L1_to_L1_5": {
      "sync_time_ms": 20,
      "items_synced": 1247,
      "status": "healthy"
    },
    "L1_5_to_L2": {
      "sync_time_ms": 25,
      "vectors_consolidated": 1247,
      "status": "healthy"
    },
    "consistency_check": {
      "verified": true,
      "checksum_matches": 3,
      "conflicts_resolved": 0
    }
  },
  "next_full_sync": "2026-06-18T17:15:00Z",
  "backup_status": "daily backup completed"
}
```

---

## Advanced: Chatting with Knights

### Pattern 1: Delegation

Let Knights make decisions autonomously:

```bash
# Enable autonomous decisions (high confidence only)
curl -X POST http://localhost:8500/knight/enable-autonomy \
  -H "Content-Type: application/json" \
  -d '{
    "rule": "If agent_load > 80%, automatically load-balance",
    "confidence_threshold": 0.92,
    "max_decisions_per_hour": 10,
    "require_approval": false
  }' | jq .
```

### Pattern 2: Learning

Ask Knights to improve over time:

```bash
# Knights learn from decisions
curl -X POST http://localhost:8500/knight/learn \
  -H "Content-Type: application/json" \
  -d '{
    "from_decision": "prop_8f2c1a9e",
    "outcome": "success",
    "metrics": {
      "actual_latency_ms": 42,
      "predicted_latency_ms": 45,
      "confidence_was": 0.91,
      "confidence_should_be": 0.95
    },
    "feedback": "Prediction was accurate"
  }' | jq .
```

### Pattern 3: Conflict Resolution

When consensus fails, Knights propose alternatives:

```bash
# Knights negotiate when agreement is hard
curl -X POST http://localhost:8443/knight/negotiate \
  -H "Content-Type: application/json" \
  -d '{
    "failed_proposal": "Increase consensus timeout from 10s to 5s",
    "disagreement": "Node 2 worried about false failures",
    "ask": "What alternative satisfies everyone?"
  }' | jq .
```

---

## Performance Tips for Knight Interactions

### 1. Batch Requests

```bash
# Instead of multiple single requests, batch them
curl -X POST http://localhost:8400/knight/batch-decide \
  -H "Content-Type: application/json" \
  -d '{
    "decisions": [
      {"query": "Route request A", "priority": "high"},
      {"query": "Route request B", "priority": "medium"},
      {"query": "Route request C", "priority": "low"}
    ],
    "process_concurrently": true
  }' | jq .
```

### 2. Use Confidence Threshold Wisely

```bash
# High confidence = slower but more reliable
# Low confidence = faster but less certain

# Critical decisions: require 0.95 confidence
# Normal decisions: require 0.85 confidence
# Fast decisions: accept 0.75 confidence
```

### 3. Cache Knight Recommendations

```bash
# Knights remember similar decisions
curl -X POST http://localhost:8400/knight/cached-decision \
  -H "Content-Type: application/json" \
  -d '{
    "similar_to": "route_data_synthesis_requests",
    "use_cache": true,
    "cache_ttl_seconds": 300
  }' | jq .
```

---

## Monitoring Knight Decisions

### View Decision History

```bash
# See all knight decisions from the last hour
curl -s http://localhost:8500/knight/decisions/history?hours=1 | jq .

# Example response shows:
# - Decision ID
# - Confidence score
# - Nodes that agreed
# - Outcome (success/failure)
# - Execution time
```

### Real-Time Knight Activity

```bash
# Watch Knights making decisions in real-time
ssh root@192.168.1.10
journalctl -u camelot-agents -f | grep "knight"

# Output shows:
# [16:45:32] Knight: Routing decision made (conf: 0.91)
# [16:45:32] Knight: Consensus on cache TTL (3/3 agree)
# [16:45:33] Knight: Agent 7 executing request
```

---

## Knight Communication Examples

### Example 1: Optimize for Low Latency

```bash
# Tell Knights you prioritize speed
curl -X POST http://localhost:8400/knight/optimize-for \
  -d '{
    "optimize": "latency",
    "max_latency_ms": 100,
    "accept_lower_throughput": true
  }'
```

### Example 2: Optimize for Throughput

```bash
# Tell Knights to maximize requests per second
curl -X POST http://localhost:8400/knight/optimize-for \
  -d '{
    "optimize": "throughput",
    "target_rps": 5000,
    "accept_higher_latency": true
  }'
```

### Example 3: Optimize for Cost

```bash
# Tell Knights to minimize resource usage
curl -X POST http://localhost:8400/knight/optimize-for \
  -d '{
    "optimize": "cost",
    "target_monthly_cost": 500,
    "acceptable_latency_degradation_percent": 10
  }'
```

---

## Troubleshooting Knight Interactions

### Knight Is Not Responding

```bash
# Check if Knight is healthy
curl -s http://localhost:8400/knight/health | jq .

# Check Knight logs
journalctl -u camelot-agents -p err | grep knight

# Restart Knight service
systemctl restart camelot-agents
```

### Low Confidence Scores

```bash
# Check why Knight is uncertain
curl -X POST http://localhost:8500/knight/explain-confidence \
  -d '{
    "decision": "last_routing_decision",
    "ask": "Why only 0.75 confidence?"
  }' | jq .
```

### Consensus Not Forming

```bash
# Check if all 3 nodes can reach each other
for node in 192.168.1.{10,11,12}; do
    ssh root@$node "ping -c 1 192.168.1.10"
done

# Check consensus logs
journalctl -u camelot-consensus -p err -n 50
```

---

## Best Practices

### ✅ DO

- Use `consensus_required: true` for critical decisions
- Let Knights batch multiple requests together
- Monitor confidence scores (track trends)
- Enable autonomous decisions for routine tasks
- Ask Knights to explain their reasoning

### ❌ DON'T

- Require 0.99 confidence for routine routing (slows decisions)
- Override Knight decisions without understanding reasoning
- Disable monitoring (you won't see issues)
- Force synchronous consensus for non-critical changes
- Ignore low confidence scores (investigate why)

---

## Next Steps

### Phase H: Adaptive Learning (Coming Soon)

Knights will automatically:
- Adjust confidence thresholds based on accuracy
- Learn optimal routing patterns
- Predict load spikes
- Recommend scaling before bottlenecks
- Auto-tune consensus parameters

---

## Resources

- **README.md** — Complete system overview
- **BARE_METAL_DEPLOYMENT.md** — How to deploy
- **observability/OBSERVABILITY_SETUP.md** — Monitor Knight decisions
- **terraform/INFRASTRUCTURE_GUIDE.md** — Day-2 operations

---

## Quick Command Reference

```bash
# Health check
curl -s http://localhost:8400/knight/health | jq .

# Get agent status
curl -s http://localhost:8400/agents/status | jq .

# Make a decision
curl -X POST http://localhost:8400/knight/decide \
  -d '{"query": "...", "confidence_threshold": 0.85}'

# Check sync health
curl -s http://localhost:6379/knight/sync-status | jq .

# View decision history
curl -s http://localhost:8500/knight/decisions/history?hours=1 | jq .

# Watch live decisions
journalctl -u camelot-agents -f | grep "knight"
```

---

**Happy chatting with your Knights!** 🎯

They're waiting to help you maximize every aspect of your CAMELOT-OS distributed system.

