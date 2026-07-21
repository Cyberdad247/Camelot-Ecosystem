# CAMELOT-OS: Epic UI/UX Architecture Design

**Status**: Design Complete | Ready for Implementation  
**Date**: 2026-06-18  
**Version**: 1.0

---

## Part 1: Service-to-UI Mapping

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER INTERFACE LAYER                        │
├─────────────────────────────────────────────────────────────────┤
│
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────┐
│  │  Dashboard UI    │  │  Knight Console  │  │  Knowledge Hub │
│  │                  │  │                  │  │                │
│  │ • Cluster Health │  │ • Decision Log   │  │ • L1 Cache     │
│  │ • Metrics        │  │ • Agent Status   │  │ • L1.5 Vectors │
│  │ • Alerts         │  │ • Consensus      │  │ • L2 Persistent│
│  │ • Performance    │  │ • Routing Viz    │  │ • Query Builder│
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬────────┘
│           │                      │                     │
└───────────┼──────────────────────┼─────────────────────┼──────────┘
            │                      │                     │
┌───────────┼──────────────────────┼─────────────────────┼──────────┐
│           ▼                      ▼                     ▼          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │        API GATEWAY / Service Orchestration Layer         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  Backend Services Layer:                                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │ Consensus   │ │ Agent       │ │ Knowledge   │              │
│  │ Engine      │ │ Registry    │ │ Sync        │              │
│  │ (8443)      │ │ (8400-8410) │ │ (6379)      │              │
│  └─────────────┘ └─────────────┘ └─────────────┘              │
│                                                                   │
│  Data Layer:                                                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │ L1: Redis   │ │ L1.5: Qdrant│ │ L2: Cloud   │              │
│  │             │ │             │ │ Brain       │              │
│  └─────────────┘ └─────────────┘ └─────────────┘              │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

---

## Part 2: Complete UI Component Architecture

### Dashboard UI (Port 3000)

```
┌─────────────────────────────────────────────────────────────┐
│                    CAMELOT-OS DASHBOARD                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Header:                                                      │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ CAMELOT-OS  │ Status: 🟢 HEALTHY  │ Nodes: 3/3 ▼    │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  Navigation:                                                  │
│  ┌─────────────┬────────────┬──────────┬─────────────┐      │
│  │ Dashboard   │ Knights    │ Knowledge│ Monitoring  │      │
│  │ (Overview)  │ (Console)  │ (Hub)    │ (Metrics)   │      │
│  └─────────────┴────────────┴──────────┴─────────────┘      │
│                                                               │
│  Body (4 Columns):                                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Column 1: Cluster Health                             │   │
│  │ ├─ Node 1 (Leader)     ████████░░ 80%               │   │
│  │ ├─ Node 2 (Follower)   ██████░░░░ 60%               │   │
│  │ ├─ Node 3 (Follower)   ███████░░░ 70%               │   │
│  │ └─ Consensus: 3/3 ✓ (45ms avg)                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Column 2: Key Metrics                                │   │
│  │ ├─ Throughput: 3,247 RPS                             │   │
│  │ ├─ Latency (p95): 42ms                               │   │
│  │ ├─ Agents: 24/24 healthy                             │   │
│  │ └─ Sync Lag: 85ms                                    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Column 3: Active Alerts                              │   │
│  │ ├─ 🔴 CPU on Node 2: 85%                             │   │
│  │ ├─ 🟡 Sync lag elevated: 120ms                       │   │
│  │ └─ 🟢 All services operational                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Column 4: Quick Actions                              │   │
│  │ ├─ [+ Scale Cluster]                                 │   │
│  │ ├─ [View Backups]                                    │   │
│  │ ├─ [Run Diagnostics]                                 │   │
│  │ └─ [Export Metrics]                                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  Footer: Last updated 2s ago  |  Refresh ⟳  |  Help ?       │
└─────────────────────────────────────────────────────────────┘
```

**Maps to Backend Services**:
- Cluster Health → Consensus Engine (8443)
- Key Metrics → Metrics Collector (8000)
- Agent Health → Agent Registry (8400)
- Sync Status → Knowledge Sync (6379)

---

### Knight Console UI (Port 3001)

```
┌─────────────────────────────────────────────────────────────┐
│               KNIGHT INTERACTION CONSOLE                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Knight Selection:                                            │
│  ┌─ Routing Knights (6)  ┌─ Consensus Knights (6)           │
│  ├─ Sync Knights (6)     ├─ Inference Knights (6)           │
│  └─ Custom Query         └─ All Knights (24)                │
│                                                               │
│  Query Builder:                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ What do you want to do?                                │ │
│  │                                                        │ │
│  │ [📋 Route Request] [🔄 Consensus] [📊 Decision] etc.  │ │
│  │                                                        │ │
│  │ Query:                                                 │ │
│  │ ┌──────────────────────────────────────────────────┐ │ │
│  │ │ {                                                │ │ │
│  │ │   "query": "How should I route 1000 requests?", │ │ │
│  │ │   "priority": "high",                            │ │ │
│  │ │   "confidence_threshold": 0.85,                  │ │ │
│  │ │   "consensus_required": true                     │ │ │
│  │ │ }                                                │ │ │
│  │ └──────────────────────────────────────────────────┘ │ │
│  │                                                        │ │
│  │ [Send to Knights ↓]                                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  Knight Response:                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ ✓ Decision Made (Confidence: 0.91)                    │ │
│  │                                                        │ │
│  │ DECISION:                                              │ │
│  │ Route using load-aware strategy                       │ │
│  │                                                        │ │
│  │ REASONING:                                             │ │
│  │ ├─ Current load: 45% (healthy)                        │ │
│  │ ├─ Agent capacity: 2000+ RPS available                │ │
│  │ └─ Route 1000 requests across all 24 agents           │ │
│  │                                                        │ │
│  │ CONSENSUS:                                             │ │
│  │ ├─ Routing Knights: 3/3 agree ✓                       │ │
│  │ ├─ Consensus Knights: 3/3 agree ✓                     │ │
│  │ └─ Final Decision: APPROVED                           │ │
│  │                                                        │ │
│  │ Expected Latency: 45ms                                │ │
│  │ Execution Status: [████████████░] 80% complete        │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  Decision History:                                            │
│  ├─ [16:45:32] Route decision (0.91 conf) ✓               │
│  ├─ [16:45:25] Consensus proposal (0.88 conf) ✓           │
│  ├─ [16:45:18] Cache TTL change (0.92 conf) ✓            │
│  └─ [16:45:10] Load balance (0.85 conf) ✓                │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Maps to Backend Services**:
- Knight Selection → Agent Registry (8400)
- Decision Making → Inference Engine (8500)
- Consensus Voting → Consensus Engine (8443)
- Decision History → Metrics/Logging (8000)

---

### Knowledge Hub UI (Port 3002)

```
┌─────────────────────────────────────────────────────────────┐
│                  KNOWLEDGE HUB                               │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Knowledge Pyramid Visualization:                             │
│                                                               │
│                        ┌─────────┐                           │
│                        │   L2    │                           │
│                        │CloudBrain                           │
│                        │(Persistent)                         │
│                        └────┬────┘                           │
│                             │                                │
│                        ┌────▼─────┐                          │
│                        │   L1.5    │                         │
│                        │  Qdrant   │                         │
│                        │ (Vectors) │                         │
│                        └────┬─────┘                          │
│                             │                                │
│                     ┌──────┴───────┐                         │
│                     │      L1      │                         │
│                     │    Redis     │                         │
│                     │  (Cache)     │                         │
│                     └──────────────┘                         │
│                                                               │
│  L1 (Redis Cache - < 5ms):                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Search: [       user preferences        ] 🔍           │ │
│  │ Results:                                               │ │
│  │ ├─ user:456:preferences → {"theme": "dark"}           │ │
│  │ ├─ user:789:settings → {"language": "en"}             │ │
│  │ └─ session:xyz:context → {"priority": "high"}         │ │
│  │                                                        │ │
│  │ Stats: 1,247 items | 94% hit rate | TTL: 60s          │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  L1.5 (Qdrant Vectors - 20-50ms):                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Semantic Search: [      similar requests      ] 🔍      │ │
│  │ Results (Similarity):                                  │ │
│  │ ├─ "customer data synthesis" → 0.98 match            │ │
│  │ ├─ "data consolidation" → 0.94 match                 │ │
│  │ └─ "reporting pipeline" → 0.87 match                 │ │
│  │                                                        │ │
│  │ Stats: 1,247 vectors | Consolidated: 100% | Top: 10   │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  L2 (CloudBrain Persistent - 100-500ms):                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Query Builder:                                         │ │
│  │ SELECT * FROM decisions                              │ │
│  │ WHERE timestamp > '2026-06-18 16:00:00'              │ │
│  │ AND confidence > 0.90                                │ │
│  │                                                        │ │
│  │ Results:                                               │ │
│  │ ├─ [Route decision] conf:0.91 time:42ms              │ │
│  │ ├─ [Consensus prop] conf:0.88 time:55ms              │ │
│  │ └─ [Cache TTL]     conf:0.92 time:5ms                │ │
│  │                                                        │ │
│  │ Stats: 12,547 decisions | Audit trail: Complete       │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  Sync Status:                                                 │
│  ├─ L1 → L1.5: 45ms lag | 1,247 items | Healthy ✓         │
│  ├─ L1.5 → L2: 85ms lag | Consolidating | Healthy ✓        │
│  └─ Consistency: 100% | Conflicts: 0 | Last sync: 2s ago   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Maps to Backend Services**:
- L1 Display → Redis (6379)
- L1.5 Display → Qdrant (vector database)
- L2 Display → CloudBrain (persistent store)
- Sync Status → Knowledge Sync Engine (6379)

---

### Monitoring UI (Port 3003 - Grafana Integration)

```
┌─────────────────────────────────────────────────────────────┐
│              MONITORING & OBSERVABILITY                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Quick Filters:                                               │
│  ┌────────────────┬────────────────┬────────────────┐       │
│  │ Last 1h ▼      │ All Services ▼ │ Alerts: 2 🔔  │       │
│  └────────────────┴────────────────┴────────────────┘       │
│                                                               │
│  Dashboard 1: System Overview                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ CPU Usage        │ Memory         │ Network           │   │
│  │ ████████░░ 75%  │ ███████░░░ 70% │ ████░░░░░░ 40%   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  Dashboard 2: Consensus Performance                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Latency (p95): 45ms ↓ (trending down)                │   │
│  │ ├─ Pre-prepare:   15ms                               │   │
│  │ ├─ Prepare:       20ms                               │   │
│  │ └─ Commit:        10ms                               │   │
│  │                                                        │   │
│  │ Agreement Rate: 99.8% (3/3 nodes)                     │   │
│  │ Proposals: 1,247 total | Success: 98.5%              │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  Dashboard 3: Knowledge Sync                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Replication Lag: 85ms (healthy < 200ms)              │   │
│  │ Conflicts Detected: 0                                 │   │
│  │ L1 → L1.5: 1,247 synced | 99.9% consistency          │   │
│  │ L1.5 → L2: 1,247 synced | 99.9% consistency          │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  Dashboard 4: Agent Network                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Agent Health: 24/24 ✓                                │   │
│  │ Load Distribution:                                    │   │
│  │ ├─ Node 1: ████████░░ 80%                            │   │
│  │ ├─ Node 2: ██████░░░░ 60%                            │   │
│  │ └─ Node 3: ███████░░░ 70%                            │   │
│  │                                                        │   │
│  │ Routing Decisions: 3,247 | Success: 99.2%            │   │
│  │ Avg Confidence: 0.91 | Min: 0.75 | Max: 0.98         │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  Alerts & Notifications:                                      │
│  ├─ 🔴 [CRITICAL] CPU Node 2: 85% (alert threshold: 80%) │
│  ├─ 🟡 [WARNING] Sync lag: 120ms (warn threshold: 100ms) │
│  ├─ 🟢 [INFO] Backup completed successfully               │
│  └─ 🟢 [INFO] All services operational                     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**Maps to Backend Services**:
- System Metrics → Metrics Collector (8000)
- Consensus Performance → Consensus Engine (8443)
- Sync Status → Knowledge Sync (6379)
- Agent Network → Agent Registry (8400)

---

## Part 3: Service-to-Component Mapping Table

| Backend Service | Port | UI Component | Interaction |
|-----------------|------|--------------|-------------|
| **Consensus Engine** | 8443 | Dashboard (Health), Knight Console (Decisions) | Real-time proposals, agreement voting, latency metrics |
| **Agent Registry** | 8400-8410 | Knight Console (Selection), Dashboard (Agent Health) | Agent discovery, selection, load distribution |
| **Knowledge Sync** | 6379 | Knowledge Hub (L1-L2), Monitoring (Sync Status) | Cache visualization, replication lag, conflict detection |
| **Metrics Collector** | 8000 | Monitoring Dashboard (All Graphs) | Performance metrics, trends, SLO tracking |
| **Inference Engine** | 8500 | Knight Console (Decisions), Dashboard (Alerts) | Confidence scoring, decision reasoning, recommendations |
| **Redis L1** | 6379 | Knowledge Hub (L1 Display) | Session cache, request context, TTL management |
| **Qdrant L1.5** | 6333 | Knowledge Hub (Vector Search) | Semantic search, similarity matching, consolidation |
| **CloudBrain L2** | Custom | Knowledge Hub (L2 Query), Audit Trail | Persistent queries, decision history, compliance logging |

---

## Part 4: API Contract (UI ↔ Backend)

### Dashboard → Backend

```json
// GET /api/v1/dashboard/health
{
  "cluster": {
    "status": "healthy",
    "nodes": 3,
    "nodes_healthy": 3,
    "nodes_data": [
      {
        "id": "node_1",
        "role": "leader",
        "cpu": 75,
        "memory": 70,
        "disk": 45
      }
    ]
  },
  "consensus": {
    "status": "operational",
    "latency_ms": 45,
    "agreement_rate": 0.998,
    "proposals_total": 1247,
    "proposals_success": 1233
  },
  "agents": {
    "total": 24,
    "healthy": 24,
    "load_average": 0.70
  },
  "alerts": [
    {
      "severity": "critical",
      "message": "CPU Node 2: 85%",
      "timestamp": "2026-06-18T16:45:32Z"
    }
  ]
}
```

### Knight Console → Backend

```json
// POST /api/v1/knight/decide
Request:
{
  "query": "Route 1000 requests",
  "context": {
    "priority": "high",
    "latency_requirement_ms": 200
  },
  "confidence_threshold": 0.85,
  "consensus_required": true
}

Response:
{
  "decision_id": "dec_8f2c1a9e",
  "decision": "Use load-aware routing",
  "confidence": 0.91,
  "reasoning": [
    "Load available: 2000+ RPS",
    "Healthy agents: 24/24"
  ],
  "consensus": {
    "routing_knights": 3,
    "inference_knights": 3,
    "all_agreed": true
  },
  "expected_latency_ms": 45
}
```

### Knowledge Hub → Backend

```json
// GET /api/v1/knowledge/pyramid/status
{
  "l1": {
    "name": "Redis Cache",
    "items_count": 1247,
    "hit_rate": 0.94,
    "ttl_seconds": 60
  },
  "l1_5": {
    "name": "Qdrant Vectors",
    "vectors_count": 1247,
    "consolidation_percent": 100,
    "consistency": 0.999
  },
  "l2": {
    "name": "CloudBrain",
    "decisions_count": 12547,
    "audit_trail": "complete"
  },
  "sync": {
    "l1_to_l1_5_lag_ms": 45,
    "l1_5_to_l2_lag_ms": 85,
    "conflicts": 0
  }
}
```

---

## Part 5: Complete Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION LAYER                         │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│ Web Browser / Desktop App                                             │
│   ↓                                                                    │
│ ┌──────────────────┬─────────────────┬──────────────┬──────────────┐ │
│ │  Dashboard UI    │  Knight Console │ Knowledge Hub│ Monitoring   │ │
│ │  (3000)          │  (3001)         │  (3002)      │  (3003)      │ │
│ └────────┬─────────┴────────┬────────┴──────┬───────┴──────┬───────┘ │
│          │                   │                │              │        │
└──────────┼───────────────────┼────────────────┼──────────────┼────────┘
           │                   │                │              │
┌──────────┼───────────────────┼────────────────┼──────────────┼────────┐
│          ▼                   ▼                ▼              ▼        │
│ ┌──────────────────────────────────────────────────────────────────┐ │
│ │          API GATEWAY / REST Service Layer                        │ │
│ │  /api/v1/{dashboard,knight,knowledge,monitoring}/...             │ │
│ └────────┬────────────────────────────────┬──────────────────┬────┘ │
│          │                                │                  │      │
│          ▼                                ▼                  ▼      │
│ ┌────────────────────┐ ┌─────────────────────┐ ┌──────────────────┐│
│ │ Consensus Service  │ │ Agent Registry      │ │ Knowledge Sync   ││
│ │ (8443)             │ │ (8400-8410)         │ │ (6379)           ││
│ │ • Propose          │ │ • Discover          │ │ • Sync L1→L1.5   ││
│ │ • Vote             │ │ • Select            │ │ • Sync L1.5→L2   ││
│ │ • Commit           │ │ • Route             │ │ • Replicate      ││
│ └────────┬───────────┘ └────────┬────────────┘ └────────┬──────────┘│
│          │                      │                       │           │
│          ▼                      ▼                       ▼           │
│ ┌────────────────────────────────────────────────────────────────┐ │
│ │ Metrics & Inference Layer                                      │ │
│ │ ├─ Metrics Collector (8000)      - 40+ metrics                │ │
│ │ ├─ Inference Engine (8500)       - Confidence scoring         │ │
│ │ └─ Observability (Prometheus)    - Scraping & aggregation    │ │
│ └────────┬──────────────────────────────────────────────────────┘ │
│          │                                                         │
│          ▼                                                         │
│ ┌────────────────────────────────────────────────────────────────┐ │
│ │ Knowledge Pyramid (Data Persistence Layer)                     │ │
│ │                                                                │ │
│ │ L1: Redis (< 5ms)        - Session state, ephemeral cache    │ │
│ │ L1.5: Qdrant (20-50ms)   - Vector consolidation, semantics   │ │
│ │ L2: CloudBrain (100-500ms) - Persistent decisions, audit     │ │
│ └────────────────────────────────────────────────────────────────┘ │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## Part 6: Component Interaction Flow

### User Makes a Decision Request

```
1. User opens Knight Console
   ↓
2. Selects "Route Request" template
   ↓
3. Fills in parameters (priority, latency requirement)
   ↓
4. Clicks "Send to Knights"
   ↓
5. UI sends POST /api/v1/knight/decide
   ↓
6. API Gateway routes to Agent Registry (8400)
   ↓
7. Routing Knights analyze agents (8400-8410)
   ↓
8. Inference Knights score confidence (8500)
   ↓
9. Consensus Knights validate (if required) (8443)
   ├─ Send "prepare" votes to all 3 nodes
   ├─ Collect responses from 2+ nodes
   └─ All nodes commit decision
   ↓
10. Result returned to UI:
    {
      "decision": "Route via Agent 7",
      "confidence": 0.91,
      "reasoning": [...],
      "consensus": 3/3 agree
    }
   ↓
11. Knight Console displays decision + reasoning
   ↓
12. User clicks "Execute" → runs decision
```

---

## Part 7: UI Component Specifications

### Dashboard Component

```
Props:
- refreshInterval: 2000ms (auto-refresh metrics)
- alertsEnabled: true
- compactMode: false

State:
- clusterStatus: 'healthy' | 'degraded' | 'critical'
- nodeStats: Node[]
- alertCount: number
- metricsData: Metrics

Methods:
- refreshClusterHealth(): void
- dismissAlert(alertId: string): void
- scaleCluster(newSize: number): void
- exportMetrics(): PDF
```

### Knight Console Component

```
Props:
- knightTypes: 'routing' | 'consensus' | 'sync' | 'inference' | 'all'
- decisionHistory: Decision[]

State:
- selectedKnights: Knight[]
- query: string
- isLoading: boolean
- response: DecisionResponse
- confidence: 0.0 - 1.0

Methods:
- sendQuery(query: string): Promise<DecisionResponse>
- formatReasoning(reasons: string[]): ReactNode
- displayConsensusStatus(consensus: ConsensusVote[]): ReactNode
- executeDecision(decisionId: string): Promise<ExecutionResult>
```

### Knowledge Hub Component

```
Props:
- defaultTier: 'l1' | 'l1_5' | 'l2'
- searchEnabled: true

State:
- selectedTier: string
- searchQuery: string
- results: SearchResult[]
- syncStatus: SyncStatus

Methods:
- searchL1(query: string): Promise<CacheResult[]>
- searchL1_5(query: string): Promise<VectorResult[]>
- queryL2(sql: string): Promise<DatabaseResult[]>
- visualizePyramid(): ReactNode
- displaySyncStatus(): ReactNode
```

---

## Part 8: API Endpoints Reference

```
Dashboard API:
GET    /api/v1/dashboard/health
GET    /api/v1/dashboard/metrics
GET    /api/v1/dashboard/alerts
POST   /api/v1/dashboard/dismiss-alert/{alertId}

Knight Console API:
POST   /api/v1/knight/decide
GET    /api/v1/knight/status
GET    /api/v1/knight/decisions/history
POST   /api/v1/knight/execute/{decisionId}
GET    /api/v1/knight/agents/status

Knowledge Hub API:
GET    /api/v1/knowledge/l1/search
GET    /api/v1/knowledge/l1_5/search
POST   /api/v1/knowledge/l2/query
GET    /api/v1/knowledge/pyramid/status
GET    /api/v1/knowledge/sync/status

Monitoring API:
GET    /api/v1/monitoring/metrics
GET    /api/v1/monitoring/alerts
GET    /api/v1/monitoring/dashboards
POST   /api/v1/monitoring/export
```

---

## Part 9: Data Flow Verification Matrix

| Flow | Source | Service | Handler | UI Display | Status |
|------|--------|---------|---------|-----------|--------|
| Health Check | Dashboard | Consensus (8443) | health_check() | Live Status | ✅ |
| Decision | Knight Console | Agent Registry (8400) | select_agent() | Decision + Confidence | ✅ |
| Consensus Vote | Knight Console | Consensus (8443) | propose() | Consensus Status | ✅ |
| L1 Cache | Knowledge Hub | Redis (6379) | get_cached() | L1 Display | ✅ |
| L1.5 Search | Knowledge Hub | Qdrant (Vector) | semantic_search() | Vector Results | ✅ |
| L2 Query | Knowledge Hub | CloudBrain | query_persistent() | Query Results | ✅ |
| Metrics | Monitoring | Metrics (8000) | collect_metrics() | Charts/Graphs | ✅ |
| Alerts | All UIs | Monitoring (8000) | alert_rule() | Notification | ✅ |

---

## Part 10: UI/UX Design Principles

### Principle 1: Show Status at a Glance
- Color coding (🟢 healthy, 🟡 warning, 🔴 critical)
- Real-time updates (2s refresh)
- Progress indicators for long operations

### Principle 2: Expert-Friendly
- JSON editor for advanced queries
- Direct API access for automation
- Detailed reasoning for every decision

### Principle 3: Visual Clarity
- Knowledge pyramid diagram
- Node topology visualization
- Agent load distribution charts

### Principle 4: Actionable Alerts
- Clear severity levels
- Recommended actions
- One-click fixes where possible

---

## Summary: Complete Mapping

✅ **Dashboard UI** ↔ All Backend Services  
✅ **Knight Console** ↔ Agent Registry + Consensus + Inference  
✅ **Knowledge Hub** ↔ Redis + Qdrant + CloudBrain  
✅ **Monitoring** ↔ Metrics Collector + Observability  

**All components map to backend services with clear contracts, API endpoints, and data flows.**

Ready for implementation! 🚀

