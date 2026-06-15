# Distance Travel Architecture — Multi-Agent Network

**Status: PHASE 1-3 COMPLETE + DISTRIBUTED SYSTEM INTEGRATED**  
**Date: 2026-05-21**

---

## Overview

**Distance Travel** enables agents to dispatch work to each other across the CAMELOT network:

```
Hermes ─────────┐
OpenClaw ──────┤
NanoBot ───────┼─→ Distributed Memory (Redis) ─→ Knowledge Pyramid Sync
ZeroClaw ──────┤     ↓
RustClaw ──────┘   Consensus Layer (voting)
                    ↓
              Agent Gateway (Bifrost Bridge)
                    ↓
              Bifrost Dispatch Core
                    ↓
              Knight Knights (sir_boris, sir_helio, etc.)
```

Each agent maintains the knowledge pyramid structure locally, syncs globally.

---

## 6 New Modules

| Module | Purpose | Features |
|--------|---------|----------|
| `distributed_memory.py` | Redis pub/sub for network events | Broadcast, subscribe, sync dispatch/learning/synthesis |
| `agent_registry.py` | Multi-agent definitions | Hermes, OpenClaw, NanoBot, ZeroClaw, RustClaw |
| `memory_sync.py` | Cross-agent Qdrant+CloudBrain sync | Vector replication, synthesis merging, blueprint updates |
| `consensus_layer.py` | Multi-agent voting & coordination | Consensus routing, conflict resolution, fallback selection |
| `agent_gateway.py` | Bifrost bridge for inter-agent dispatch | Direct agent-to-agent calls, parallel dispatch |
| `distance_travel.py` | Complete orchestrator | Integration of all 5 modules, high-level API |

---

## Agent Network

### Agents (5)

```python
hermes         # Kinetic tool-calling agent
               # Capabilities: tool_use, autonomous, reasoning, code_generation, file_ops, terminal
               # Port: 8401

openclaw       # Open-source reasoning engine
               # Capabilities: reasoning, analysis, research, synthesis, planning
               # Port: 8402

nanobot        # Lightweight edge agent
               # Capabilities: inference, edge_deployment, low_latency, privacy, offline
               # Port: 8403

zeroclaw       # Zero-trust privacy agent
               # Capabilities: security, encryption, sandboxing, audit, compliance, zero_trust
               # Port: 8404

rustclaw       # Systems specialist
               # Capabilities: systems, performance, optimization, infrastructure, benchmarking, profiling
               # Port: 8405
```

All agents:
- Maintain local knowledge pyramid (blueprint/tasks/verification)
- Sync via Redis pub/sub
- Participate in consensus voting
- Access shared Qdrant + CloudBrain

---

## Distance Travel API

### Single Agent Dispatch

```python
from control_plane.distance_travel import ask_agent

async for chunk in ask_agent("hermes", "openclaw", "Reason about this problem"):
    print(chunk, end="", flush=True)
```

Flow:
1. Hermes requests OpenClaw's reasoning
2. Gateway routes through Bifrost
3. OpenClaw's knight (sir_boris) processes request
4. Response streamed back to Hermes
5. Learning synced to network (Qdrant + Redis)

### Multiple Agent Dispatch

```python
from control_plane.distance_travel import ask_agents

results = await ask_agents(
    "hermes",
    ["openclaw", "nanobot", "zeroclaw"],
    "Solve this optimization problem"
)

# Output: {"openclaw": "response...", "nanobot": "response...", "zeroclaw": "response..."}
```

### Consensus-Based Dispatch

```python
from control_plane.distance_travel import ask_best_agent

selected, response = await ask_best_agent(
    "hermes",
    capability="reasoning",  # Find best agent for reasoning
    task="Complex logic problem"
)
# Returns: ("openclaw", "Here's my reasoning...")
```

---

## Knowledge Pyramid Sync

### What Gets Synced?

**L1 (Redis, 24h)**:
- Recent dispatch events
- Task queue updates
- Heartbeats

**L2 (Qdrant, 30d)**:
- Compressed vectors (dispatches)
- Cross-agent indices
- Synthesis embeddings

**L3 (CloudBrain, 30+d)**:
- Merged synthesis insights
- Cross-agent patterns
- Updated blueprints

### Example: Cross-Agent Learning

```
Hermes dispatches to OpenClaw for reasoning:
  ├─ Task: "Reason about X"
  ├─ Response: "Analysis..."
  ├─ Quality: 0.92

Learning syncs to network:
  1. Redis: dispatch event broadcast
  2. Qdrant: compress & index (dispatch_id: "hermes->openclaw:...")
  3. CloudBrain: extract insights
  4. Blueprint: update openclaw/blueprint.md with learning
  5. Qdrant: replicate vector to all agents

Next dispatch by OpenClaw:
  ├─ Load blueprint (now includes Hermes's insight)
  ├─ Search Qdrant (find Hermes's similar work)
  ├─ Enrich prompt with context
  └─ Better response
```

---

## Consensus Voting

### Scenario: Route "Optimize database query"

**Candidate agents**: openclaw (reasoning), rustclaw (systems)

**Voting process**:
1. Ask each agent: "Should I handle this?"
2. openclaw: 0.65 match score (reasoning, not systems)
3. rustclaw: 0.92 match score (systems specialist)
4. Consensus: Send to rustclaw
5. Broadcast decision via Redis

### Fallback on Failure

```
If rustclaw is offline:
  1. ConsensusLayer.handle_agent_failure(rustclaw)
  2. Find agents with overlapping capabilities
  3. Route to next-best (e.g., nanobot with systems capability)
  4. Broadcast failover event
```

---

## Data Flow: Complete Example

### "Hermes asks OpenClaw to reason about a complex problem"

```
1. INIT
   ├─ DistanceTravel.ask_agent("hermes", "openclaw", "Why does X fail?")
   └─ dispatch_id = "hermes->openclaw:1716234567"

2. BROADCAST EVENT
   ├─ Distributed Memory broadcasts:
   │  {
   │    "event_type": "dispatch",
   │    "source_agent": "hermes",
   │    "target_agents": ["openclaw"],
   │    "data": {"task": "Why does X fail?", "dispatch_id": "..."}
   │  }
   └─ All agents see this (via Redis pub/sub)

3. GATEWAY DISPATCH
   ├─ Agent Gateway routes via Bifrost
   ├─ Maps "openclaw" → knight "sir_boris"
   ├─ Enriched system prompt:
   │  "You are assisting Hermes (kinetic agent)
   │   Provide reasoning explicitly"
   └─ Dispatches to sir_boris

4. KNOWLEDGE ENRICHMENT
   ├─ Load OpenClaw's blueprint
   ├─ Search Qdrant: "reasoning about X failures"
   │  → Find: previous reasoning dispatch (score: 0.88)
   ├─ Enrich prompt with similar context
   └─ sir_boris processes enriched prompt

5. RESPONSE STREAMING
   ├─ OpenClaw: "I analyze X...
   │   Root cause: [analysis]
   │   Recommendation: [fix]"
   └─ Streamed back to Hermes

6. LEARNING SYNC
   ├─ Assess quality: 0.94 (excellent reasoning)
   ├─ Update openclaw/tasks.md:
   │  {
   │    "completed": [{
   │      "dispatch_id": "hermes->openclaw:...",
   │      "prompt": "Why does X fail?",
   │      "quality_score": 0.94
   │    }]
   │  }
   ├─ Update openclaw/verification.md with metrics
   ├─ Index in Qdrant:
   │  {
   │    "vector": [0.12, -0.34, ...],
   │    "keywords": ["reasoning", "x", "failure"],
   │    "quality": 0.94,
   │    "source_agent": "hermes",
   │    "dispatch_id": "hermes->openclaw:..."
   │  }
   └─ Broadcast learning event to all agents

7. NEXT DISPATCH
   ├─ Hermes now sees openclaw's updated blueprint
   ├─ If asking another agent about "X failure":
   │  ├─ Search Qdrant: find openclaw's analysis
   │  ├─ Enrich prompt: "Recent analysis from OpenClaw..."
   │  └─ Better context → better response

8. WEEKLY SYNTHESIS
   ├─ Sunday 11 PM: cross_agent_synthesis("reasoning")
   ├─ Query Qdrant: all reasoning dispatches (all agents, last 7 days)
   ├─ Cluster by pattern
   ├─ Ask CloudBrain: "What did we learn about reasoning?"
   ├─ Update ALL agent blueprints with learnings
   └─ Network-wide knowledge improvement
```

---

## Performance Characteristics

| Operation | Latency | Blocking? |
|-----------|---------|-----------|
| Ask agent | 100-2000ms | Yes (streaming) |
| Consensus vote | 50-200ms | Yes |
| Broadcast event | <5ms | No (async) |
| Memory sync | 20-100ms | No (async) |
| Cross-agent synthesis | 5-10 min | No (background) |

**Network overhead**: +50ms per dispatch (routing + coordination)

---

## Use Cases

### 1. Complex Reasoning (Hermes → OpenClaw)

```python
# Hermes: "I need to reason about this"
await ask_agent("hermes", "openclaw", complex_problem)
# OpenClaw gets best reasoning tools, returns analysis
```

### 2. Privacy-Critical (Anyone → ZeroClaw)

```python
# "Process this securely"
await ask_agent(source_agent, "zeroclaw", sensitive_task)
# ZeroClaw: encryption, sandboxing, audit trail
```

### 3. Performance Optimization (Hermes → RustClaw)

```python
# "Optimize this for speed"
await ask_agent("hermes", "rustclaw", perf_problem)
# RustClaw: profiling, benchmarking, systems tuning
```

### 4. Parallel Problem-Solving (Any → Many)

```python
# Ask multiple specialists
results = await ask_agents(
    "hermes",
    ["openclaw", "nanobot", "zeroclaw"],
    "Solve this from multiple angles"
)
# Each agent contributes their specialty
# Consensus merges results
```

### 5. Best-For-Capability (Dynamic Routing)

```python
# Ask whoever is best for this capability
selected, response = await ask_best_agent(
    "hermes",
    capability="optimization",
    task="Optimize database"
)
# Voting selects best match (RustClaw wins)
# Automatic fallback if selected agent is offline
```

---

## Integration with Knowledge Pyramid

Every dispatch across distance travel:

✅ Maintains local blueprint/tasks/verification per agent  
✅ Syncs learning to Qdrant (L2)  
✅ Contributes to CloudBrain synthesis (L3)  
✅ Enriches future dispatches with context  
✅ Builds cross-agent expertise over time  

**Result**: Agents become smarter by learning from each other.

---

## Testing Distance Travel

### Quick Test

```python
import asyncio
from control_plane.distance_travel import ask_agent

async def test():
    # Hermes asks OpenClaw for reasoning
    print("[1] Hermes → OpenClaw:")
    async for chunk in ask_agent("hermes", "openclaw", "Explain recursion"):
        print(chunk, end="", flush=True)
    print()

asyncio.run(test())
```

### Parallel Test

```python
import asyncio
from control_plane.distance_travel import ask_agents

async def test():
    # Ask all agents in parallel
    results = await ask_agents(
        "hermes",
        ["openclaw", "nanobot", "zeroclaw"],
        "What makes good code?"
    )
    
    for agent_id, response in results.items():
        print(f"\n{agent_id}:\n{response[:200]}...\n")

asyncio.run(test())
```

### Consensus Test

```python
import asyncio
from control_plane.distance_travel import ask_best_agent

async def test():
    # Ask best agent for reasoning
    selected, response = await ask_best_agent(
        "hermes",
        capability="reasoning",
        task="Why do trees grow?"
    )
    
    print(f"Selected: {selected}")
    print(f"Response: {response[:200]}...")

asyncio.run(test())
```

---

## Deployment

### Prerequisites

```bash
pip install redis qdrant-client sentence-transformers
```

### Services

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Qdrant
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant:latest

# Terminal 3: CAMELOT Hive
python -m control_plane.hive_boot

# Terminal 4: Run your distance travel
python distance_travel_test.py
```

### Agent Processes (Future)

In production, each agent would be a separate process:

```bash
python -m agents.hermes --port 8401
python -m agents.openclaw --port 8402
python -m agents.nanobot --port 8403
python -m agents.zeroclaw --port 8404
python -m agents.rustclaw --port 8405
```

---

## Summary

**Distance Travel** creates a distributed multi-agent network where:

✅ **Agents ask each other for help** via Bifrost  
✅ **Knowledge syncs automatically** across network  
✅ **Consensus voting selects best agent** for each task  
✅ **Knowledge pyramid maintained locally** + synced globally  
✅ **Automatic fallback** on agent failure  
✅ **Self-enhancing** through weekly synthesis  

**Result**: CAMELOT becomes a true multi-agent system where agents collaborate and learn from each other's work.
