# Honcho Self-Hosted L4 Memory & Hermes Integration

## 1. Executive Summary & Teleology

Under the sovereign direction of King Arthur (VaShawn O. Head / Vizion), Camelot-OS has integrated **Self-Hosted Honcho** ([elkimek/honcho-self-hosted](https://github.com/elkimek/honcho-self-hosted)) into the **WorldTree Root Lattice** (`a0a4bfb9-e847-4c38-be39-7aee398f0795`) and specifically tethered it into **`HERMES_PRIME`** (`28f89cb6-5048-4b5d-9e94-376082d24744`) on the VPS Hub (`KVM563` / `162.35.107.134` / Tailscale `100.71.218.75`).

This provides Hermes Agent and the Round Table with an autonomous, cross-session **Layer 4 Metamemory & Dialectic User-Modeling Engine**, maintaining complete data sovereignty with zero external cloud memory leakage.

---

## 2. 4-Layer Memory Topology in Camelot-OS

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CAMELOT-OS MULTI-TIER MEMORY STACK                   │
├────────┬─────────────────────────┬──────────────────────────────────────────┤
│ Layer  │ Subsystem Engine        │ Operational Focus                        │
├────────┼─────────────────────────┼──────────────────────────────────────────┤
│ **L1** │ Working Window / AST    │ Fast ephemeral prompt tokens (<72μs SLA)  │
│ **L2** │ MemCastle & Redis Cache │ Rolling session buffers & hot TTL caches │
│ **L3** │ Titan Omega / UKG Graph │ Structured JSON-LD truths & vector index │
│ **L4** │ **Self-Hosted Honcho**  │ **Cross-session user modeling & dialectic│
│        │                         │  theory-of-mind (Zero cloud leak)**     │
└────────┴─────────────────────────┴──────────────────────────────────────────┘
```

---

## 3. Architecture & Service Topology

```
┌───────────────────────────────┐
│     HERMES_PRIME / Agent      │
│  (VPS KVM563 / Cybertronia)   │
└───────────────┬───────────────┘
                │
                │ HTTP API (:8000) / HonchoBridge
                ▼
┌───────────────────────────────────────────────────────────────┐
│            SELF-HOSTED HONCHO STACK (:8000)                   │
│                                                               │
│   ┌───────────────────┐               ┌───────────────────┐   │
│   │ Honcho REST API   │               │ Deriver & Workers │   │
│   │ (FastAPI / Py3.11)│               │ (Dialectic Logic) │   │
│   └─────────┬─────────┘               └─────────┬─────────┘   │
│             │                                   │             │
│             ▼                                   ▼             │
│   ┌───────────────────┐               ┌───────────────────┐   │
│   │ PostgreSQL 15     │               │ Redis 7           │   │
│   │ + pgvector        │               │ (Ephemeral Cache) │   │
│   └───────────────────┘               └───────────────────┘   │
└───────────────────────────────────────────────────────────────┘
                ▲
                │ VFS Mirror
┌───────────────┴───────────────┐
│     WorldTree Root Node       │
│  vfs://worldtree/memory/honcho│
└───────────────────────────────┘
```

---

## 4. Key Capabilities Provided to Hermes

1. **Persistent Operator Metamemory:**
   Automatically tracks King Arthur's preferences, project goals, architectural directives (e.g. Rule 7 hotpath purity), and communication style across weeks of discontinuous sessions.

2. **Deductive Observation Extraction:**
   The background Deriver engine analyzes conversation messages asynchronously, extracting implicit facts and deductive conclusions without consuming online LLM latency in the primary agent path.

3. **Data Sovereignty (Zero Cloud Leaks):**
   Unlike default Plastic Labs cloud configurations where memories reside on third-party servers, this self-hosted stack stores 100% of conversation histories, vectors, and metamemory in local PostgreSQL (`pgvector`) and Redis instances deployed either on the local workstation or the VPS KVM563 hub.

4. **Multi-Router Awareness:**
   Deriver workers can route their background reasoning through Camelot's `OmniRoute` (`:20128`) or `CLIProxyAPI` (`:8080`), utilizing OpenAI-compatible endpoints with primary and backup providers.

---

## 5. File & Component Inventory

* **Deployment Configuration:** [`deploy/honcho-self-hosted/`](../../deploy/honcho-self-hosted)
  - `docker-compose.yml`: API, deriver, PostgreSQL + pgvector, Redis.
  - `config.toml`: App settings, pool sizing, LLM provider routing slots.
  - `env.example`: Environment variables for provider base URLs and embedding models.
  - `setup.sh`: Automated installer script.
* **Control Plane Bridge:** [`control_plane/infra/honcho_bridge.py`](../../control_plane/infra/honcho_bridge.py)
  - `HonchoBridge`: Resilient HTTP client with fallback to local VFS cache (`03_VAULT/runtime_state/honcho_memory_cache.json`).
* **Hermes Bus Integration:** [`control_plane/infra/hermes_bridge.py`](../../control_plane/infra/hermes_bridge.py)
  - Channels added: `honcho.memory`, `honcho.dialectic`.
* **VFS Coordinates:** `vfs://worldtree/memory/honcho/` and `vfs://worldtree/knights/hermes_prime/honcho_l4_memory.json`.
* **Runic Commands:**
  - `//HONCHO_SYNC <user_id>`: Reconciles user observations and metamemory state.
  - `//HONCHO_QUERY <query>`: Recalls semantic context across past sessions.

---

## 6. Verification & Operational Status

The Honcho bridge and Hermes integration have been tested and verified:
- Unit test suite: [`tests/control_plane/test_hermes_honcho_integration.py`](../../tests/control_plane/test_hermes_honcho_integration.py)
- Pass status: 100% Green with graceful zero-crash resilience when container is offline.
