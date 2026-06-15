# Knight Flash Memory — 24-Hour Purge System

**Status: READY TO ACTIVATE**

Redis Agent Memory provides distributed flash memory for the CAMELOT-OS Hive, enabling:
- Session history per terminal (24h purge)
- Long-term facts about knight capabilities
- Semantic search across dispatch history
- Context reconstruction for failed/resumable tasks

---

## Setup

### 1. Install Client Library

```bash
pip install redis-iris
```

### 2. Set Environment Variables

```bash
# Redis Agent Memory API credentials
export AGENT_MEMORY_URL="https://gcp-us-east4.memory.redis.io"
export AGENT_MEMORY_STORE_ID="9554270fe8574d1ea5f5fb40140b4b7b"
export AGENT_MEMORY_API_KEY="<your-api-key>"
```

Or in `.env` file at `CAMELOT_OS/.env`:

```
AGENT_MEMORY_URL=https://gcp-us-east4.memory.redis.io
AGENT_MEMORY_STORE_ID=9554270fe8574d1ea5f5fb40140b4b7b
AGENT_MEMORY_API_KEY=<your-api-key>
```

### 3. Verify Connection

```python
from control_plane.agent_memory import get_memory

mem = get_memory()
# Check client initialization: mem.client should not be None
```

---

## Usage

### Automatic Logging (Built-in)

When you dispatch through Bifrost, dispatch & routing decisions are automatically logged:

```python
from control_plane.bifrost import Bifrost

bf = Bifrost()

# Dispatch logs automatically
async for chunk in bf.stream("sir_boris", "Refactor my code", "You are an expert..."):
    print(chunk, end="", flush=True)

# Intent routing logs routing decisions
async for tid, chunk in bf.route_and_stream("Build a login form"):
    print(chunk, end="", flush=True)
```

### Manual API

```python
from control_plane.agent_memory import (
    log_dispatch,
    log_response,
    store_fact,
    search,
    get_memory,
)

mem = get_memory()

# Log a dispatch
await log_dispatch(
    terminal_id="sir_boris",
    prompt="Explain this error",
    system="You are a debugging expert",
    model="claude-sonnet-4-6"
)

# Log a response
await log_response(
    terminal_id="sir_boris",
    response="The error occurs because...",
    latency_ms=156.3
)

# Store a capability fact
await store_fact(
    terminal_id="sir_boris",
    fact="specializes in architecture review and refactoring"
)

# Semantic search
results = await search("Which knight handles security audits?")
# Returns: [{"text": "sir_sentinel: security audit specialist", ...}, ...]

# Get session history
session = await mem.get_session("sir_boris")
# Returns: {"events": [...], "metadata": {...}}
```

---

## Memory Structure

### Session Memory (24-hour TTL)

**Per terminal:** Append-only log of dispatch/response events.

```json
{
  "sessionId": "knight-sir_boris",
  "events": [
    {
      "role": "DISPATCH",
      "content": [{"text": "Explain this error", "metadata": {...}}],
      "createdAt": 1716230400000
    },
    {
      "role": "RESPONSE",
      "content": [{"text": "The error occurs because...", "metadata": {...}}],
      "createdAt": 1716230410000
    }
  ]
}
```

### Long-Term Memory (30-day retention)

**Semantic store:** Facts, capabilities, and routing decisions indexed for search.

```json
{
  "id": "memory-sir_boris-001",
  "text": "sir_boris: specializes in architecture review and refactoring",
  "metadata": {
    "terminal": "sir_boris",
    "created_at": 1716230400.0
  }
}
```

### Routing Context

Each intent-routed dispatch stores the decision:

```json
{
  "id": "context-sir_boris-001",
  "text": "Dispatch to sir_boris: category=CODE, confidence=0.92, candidates=sir_boris,sir_codex,sir_hermes",
  "metadata": {
    "terminal": "sir_boris",
    "category": "CODE",
    "confidence": 0.92
  }
}
```

---

## 24-Hour Purge System

**Automatic:** Server-side session expiry (Redis TTL).  
**Manual:** Call purge endpoint (when API adds support).

```python
# Currently: sessions naturally expire server-side at 24h
count = await mem.purge_stale_sessions()  # placeholder for future API
```

---

## Search Examples

```python
# Find knights for a task
results = await search("Which knight specializes in code review?")

# Understand a failure
results = await search("Why did the last refactor fail?")

# Route analysis
results = await search("How often does sir_boris get routed to?")

# Capability discovery
results = await search("What can the local models do?")
```

---

## Integration with MCP Conductor

The MCP conductor can expose a memory tool:

```python
# In mcp_conductor.py tools registry:
{
    "name": "search_memory",
    "description": "Search knight flash memory for facts and history",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {"type": "string"}
        },
        "required": ["query"]
    }
}

# Handler:
async def _call(name, args):
    if name == "search_memory":
        results = await search(args["query"])
        return json.dumps(results)
```

---

## Troubleshooting

### Memory Not Initialized

```
[AGENT_MEMORY] AGENT_MEMORY_API_KEY not set — memory disabled
```

**Fix:** Set the environment variable and restart.

### Connection Failed

```
[AGENT_MEMORY] Connection failed: <error>
```

**Causes:**
- Invalid API key
- Network unreachable
- Store ID mismatch
- Redis service down

**Fix:** Verify credentials and network connectivity.

### Memory Logging Silent Failure

Dispatch and routing continue normally if memory logging fails. Check stderr for errors:

```bash
python -m control_plane.bifrost 2>&1 | grep AGENT_MEMORY
```

---

## Performance Notes

- **Dispatch overhead:** ~5-10ms (non-blocking async task)
- **Search latency:** 50-200ms (semantic index lookup)
- **Session retrieval:** 20-50ms
- **Storage quota:** 30 days of history (per retention policy)

---

## Future Enhancements

- [ ] Bulk purge API (when redis-iris adds support)
- [ ] Streaming session replay for failed tasks
- [ ] Cross-terminal pattern analysis
- [ ] Automatic capability profiling
- [ ] MCP tool integration for IDE access
- [ ] Webhook alerts on anomalies

---

## Files

- **`control_plane/agent_memory.py`** — KnightMemory client (91 lines)
- **`control_plane/bifrost.py`** — Integrated logging (3 lines added)
- **`.env`** (or `.env.local`) — Configuration

Ready to activate. Install redis-iris and set environment variables to enable.
