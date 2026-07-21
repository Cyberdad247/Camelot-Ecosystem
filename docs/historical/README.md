# ⚠️ HISTORICAL DOCUMENTATION — Pre-June 2026 Architecture

**These documents reflect the CAMELOT-OS architecture as it existed *before* the
June 2026 architectural pivot.** They are preserved for reference only and
should not be treated as current operational guidance.

## What Changed (June 2026)

In June 2026, CAMELOT-OS pivoted from a **distributed 3-node cluster architecture**
to a **single-host local-first architecture** (v1000-EXCALIBUR-A). Key changes:

| Component | Pre-Pivot (Deprecated) | Post-Pivot (Current) |
|-----------|----------------------|---------------------|
| Memory L1 | Redis | SQLite / FirnFlow |
| Memory L1.5 | Qdrant (vector DB) | FirnFlow L2 |
| Memory L2 | NotebookLM CloudBrain | NotebookLM CloudBrain |
| Deployment | Docker + 3-node cluster | Single-host + Tailscale mesh |
| Agents | 24 across 3 nodes | 23 in Switchboard (single host) |
| PBFT Consensus | 3-node Byzantine | Deprecated (single host) |

## Documents Marked Historical

The following files reference the deprecated architecture and are **archived for
reference only**. Do not use them as operational runbooks:

### In `docs/architecture/` (partially stale)
- `ARCHITECTURE.md` — References Redis L1, Qdrant L1.5, Docker deployment
- `ARCHITECTURE_USAGE_GUIDE.md` — References 3-node cluster, Redis, Qdrant
- `DISTANCE_TRAVEL_ARCHITECTURE.md` — References 5-agent network (extended later)
- `KNOWLEDGE_PYRAMID_ARCHITECTURE.md` — References 3-tier Redis/Qdrant/CloudBrain

### In `docs/guides/` (partially stale)
- `DEPLOYMENT_GUIDE.md` — References Docker deployment
- `BARE_METAL_DEPLOYMENT.md` — References 3-node cluster deployment
- `OPERATIONS_MANUAL.md` — References Redis, Qdrant for operational tasks
- `DEPLOYMENT_LIVE_2026-06-18.md` — References the now-deprecated cluster
- `DEPLOYMENT_SUMMARY.md` — References AWS deployment (deprecated)
- `INFRASTRUCTURE_COMPLETE.md` — References Terraform AWS provisioning (deprecated)

### In `docs/historical/` (delivery manifests)
- `COMPLETE_DELIVERY_SUMMARY.md` — Delivery manifest for pre-pivot release
- `DELIVERY_MANIFEST.md` — Delivery manifest
- `EXECUTION_COMPLETE.md` — Execution completion report

### In `docs/reports/` (historical reports)
- `DISTANCE_TRAVEL_TEST_RESULTS.md` — Tests against deprecated architecture
- `LOAD_TESTING_PLAN.md` — Load tests for 3-node cluster (never completed)

## Current Architecture

For the **current** single-host v1000-EXCALIBUR-A architecture, see:
- `docs/INDEX.md` — Master documentation index with staleness markers
- `README.md` — Current system README
- `AGENTS.md` — Agent constitution (always current)
- `control_plane/` — The live control plane source code

**Rule of thumb:** If a document mentions Redis, Qdrant, Docker, or a 3-node
cluster, it is historical. Trust the live source code and `AGENTS.md` over any
archived document.
