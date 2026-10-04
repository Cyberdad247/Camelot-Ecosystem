# CloudBrain Search Integration — Interface Design Specification
**Document ID:** SPEC-CLOUDBRAIN-SEARCH-001  
**Authority Layer:** L2 (Experience Plane // VS-014 Extension)  
**Assessor / Architect:** Anya (I/O Middleware)  
**Date:** 2026-10-04  
**Status:** IMPLEMENTED & ACTIVE  

---

## 1. System Overview & Problem Statement

The Camelot Documentation Platform (`tools/htmx-docs`) operates on two distinct knowledge tiers:
1. **Tier-0 Local Canonical Corpus:** Version-controlled Markdown documents compiled directly into memory via `go:embed` with cryptographic SHA-256 integrity hashes (VCL Ledger).
2. **Tier-1/Tier-2 Sovereign CloudBrain:** High-dimensional knowledge graphs (Graphiti), Vector KNN memory banks (MemCastle sqlite-vec), and Knight-specific synthesis nodes (NotebookLM / Anya / Sir Boris).

Previously, the documentation search only operated over Tier-0 local documents. This interface design establishes a **Unified Sovereign Search Surface** allowing human operators (via HTMX hypermedia) and autonomous AI agents (via WebMCP and headless JSON) to query both layers through a single, resilient interface.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        EXTERNAL CONSUMERS                              │
│         Human Browser (HTMX)       │      AI Agent / MCP Client        │
└──────────────────────────┬─────────┴─────────────┬─────────────────────┘
                           │                       │
               Accept: text/html                   │ Accept: application/json
                           │                       │
┌──────────────────────────▼───────────────────────▼─────────────────────┐
│                 /api/cloudbrain/search (Go Engine)                     │
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │                      Query Disambiguator                       │   │
│   │        scope=all | canonical | cloudbrain | memcastle          │   │
│   └───────────────┬────────────────────────────────┬───────────────┘   │
│                   │                                │                   │
│         ┌─────────▼────────┐             ┌─────────▼─────────┐         │
│         │   Local Inverted │             │ CloudBrain Bridge │         │
│         │   Index (Tier 0) │             │ (Tiers 1 & 2)     │         │
│         └─────────┬────────┘             └─────────┬─────────┘         │
│                   │                                │                   │
│                   └────────────────┬───────────────┘                   │
│                                    ▼                                   │
│                        Unified Result Synthesizer                      │
│                  - Source Tagging ([CANONICAL], [CB])                  │
│                  - Score Normalization & Deduplication                 │
│                  - Circuit-Breaker Graceful Fallback                   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. API Contract & Schemas

### 2.1 Endpoint: `/api/cloudbrain/search`
* **Method:** `GET` or `POST`
* **Query Parameters / Form Fields:**
  * `q` (string, required): Search query or natural language question.
  * `scope` (string, optional, default: `"all"`): `"all"` | `"canonical"` | `"cloudbrain"` | `"memcastle"`.
  * `knight` (string, optional): Target Knight Persona (e.g., `"ANYA_OMEGA"`, `"SIR_BORIS"`, `"HERMES_PRIME"`).
  * `limit` (integer, optional, default: `10`): Maximum results to return.

### 2.2 Response Payloads (Content Negotiated)

#### A. Human Consumer (`Accept: text/html`)
Returns an HTMX-compatible hypermedia fragment with distinct visual origin badges and deep-links:

```html
<li class="result-item result-canonical">
  <a href="#" hx-get="/docs/getting-started" hx-target="#content" hx-push-url="true">
    <span class="source-badge badge-canonical">CANONICAL</span>
    <span class="title">Getting Started</span>
    <span class="meta">[DOC-001]</span>
  </a>
</li>
<li class="result-item result-cloudbrain">
  <div class="cloudbrain-hit">
    <span class="source-badge badge-cloudbrain">CLOUDBRAIN // ANYA</span>
    <span class="title">Lattice Signal Distributed Concurrency Protocol</span>
    <p class="snippet">Vector match (0.92) across sovereign agent deliberation memory...</p>
  </div>
</li>
```

#### B. Agent Consumer (`Accept: application/json`)
Returns a structured JSON payload ready for LLM consumption:

```json
{
  "query": "concurrency",
  "scope": "all",
  "total_hits": 2,
  "results": [
    {
      "id": "DOC-001",
      "title": "Getting Started",
      "slug": "getting-started",
      "source": "canonical",
      "confidence": 1.0,
      "snippet": "Covers high-throughput lock-free indexing."
    },
    {
      "id": "CB-MEM-8841",
      "title": "Lattice Signal Distributed Concurrency Protocol",
      "slug": "cloudbrain://anya/concurrency-protocol",
      "source": "cloudbrain",
      "knight": "ANYA_OMEGA",
      "confidence": 0.92,
      "snippet": "Vector match across sovereign agent deliberation memory."
    }
  ]
}
```

---

## 3. Resilient Fault-Tolerance (The Circuit Breaker)

CloudBrain memory nodes may reside across air-gapped hosts, remote SQLite instances, or NotebookLM proxies. In accordance with **Profile C (Minimal / Air-Gapped)**:
* If the CloudBrain bridge fails or times out (500ms ceiling), the engine **MUST NOT FAIL** the request.
* The local Inverted Index results are delivered immediately.
* A polite status indicator `<div class="cb-notice-degraded">CloudBrain link dormant — Serving Canonical Index</div>` is prepended to the response.

---

## 4. WebMCP Tool Bindings

The WebMCP Manifest (`/.well-known/mcp.json`) exposes the unified capability:
```json
{
  "name": "search_cloudbrain",
  "description": "Unified semantic search over Camelot Canonical Docs, MemCastle KNN vectors, and Knight Cloudbrains",
  "parameters": {
    "type": "object",
    "properties": {
      "query": { "type": "string" },
      "scope": { "type": "string", "enum": ["all", "canonical", "cloudbrain", "memcastle"] },
      "knight": { "type": "string" }
    },
    "required": ["query"]
  }
}
```
