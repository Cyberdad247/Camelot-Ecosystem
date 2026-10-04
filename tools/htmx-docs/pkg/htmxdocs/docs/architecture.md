---
id: DOC-002
title: Full-Stack Architecture and Implementation Specification
author: ANYA_Ω / SIR_HELIOS / MERLIN_Ω / ARTHUR_OMEGA
date: 2026-10-04
status: active
tags: [architecture, full-stack, vMAX, specification, governance, security]
---

# Conform: Full-Stack Architecture and Implementation Specification

**Document ID:** `CAMELOT-OS-MASTER-SUITE-vMAX-20260913`  
**Version:** `3.0.0-PROD-CONFORMED`  
**Status:** `LIVING BASELINE | CONVERGED | IMPLEMENTATION GOVERNED`  
**Authority Layer:** `L2 (SAD / TDD / LLDD Continuum)`  
**Baseline Hash:** `SHA-256: 9051a46 / 95a3c7dd`  

---

## 1. Executive Summary & Convergence Invariants

Camelot-OS operates as a zero-trust, agentic cognitive operating fabric designed to bridge the gap between high-level autonomous agent planning and mathematically verified, auditable execution.

```text
Business Intent ➔ Product Requirement ➔ Typed Proposal (Anya) ➔ Policy Decision (Sentinel)
  ➔ Immutable Effect Manifest ➔ Human Approval (Excalibur) ➔ Capability Lease
  ➔ Bounded Native / WASM Execution (Moon) ➔ Independent Verification (Gideon)
  ➔ Cryptographic Hash Chain (Ledger) ➔ Verified UI Projection (World Tree / HTMX)
```

### Core Architecture Invariants

| Superseded Paradigm | Canonical vMAX Production Decision |
|---|---|
| **Docker / Kubernetes Overhead** | Signed native micro-binaries sandboxed via systemd and cgroup v2 memory limits (<350MB RSS). |
| **Python Monolith Authority** | High-performance Rust control plane; Go serverless transport & doc engines; Wasmtime/WASI sandboxing. |
| **Direct Agent Mutex Writes** | Agents propose; Sentinel authorizes; Excalibur approves; Gideon verifies; Ledger proves. |
| **Static Documentation** | Living VKG (Vector Knowledge Graph) with machine-actionable WebMCP endpoints and ETag-cached markdown. |
| **Network Trust Assumptions** | Tailscale mTLS + Bifrost envelope signatures (`ed25519`); zero implicit network authority. |

---

## 2. Full-Stack Plane Decomposition

The architecture is partitioned into 8 decoupled operational planes with strictly enforced authority perimeters:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   1. EXPERIENCE PLANE (HTMX / PWA / WebMCP)           │
│         Zero-JS Declarative DOM · Responsive Tokens · ETag Caching     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ mTLS / Bifrost Envelopes
┌───────────────────────────────────▼────────────────────────────────────┐
│                    2. CONTROL & GOVERNANCE PLANE                       │
│    Sentinel (Policy/Leases) · Excalibur (HITL) · Arthur (Resolutions)  │
└───────────────────┬────────────────────────────────┬───────────────────┘
                    │                                │
┌───────────────────▼──────────────┐   ┌─────────────▼───────────────────┐
│     3. SAFETY & VFS PLANE        │   │       4. CLOUDBRAIN PLANE       │
│  VFS Guardian · Resource Quotas  │   │ Hybrid Search · MemCastle KNN   │
│  cgroups (<350MB) · Janitorial   │   │ Inverted Index · QFT Compiler   │
└───────────────────┬──────────────┘   └─────────────┬───────────────────┘
                    │                                │
┌───────────────────▼────────────────────────────────▼───────────────────┐
│                    5. BOUNDED EXECUTION PLANE                          │
│     Wasmtime WASI · Disposable Sandboxes · Ephemeral Worktrees         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Evidence Bundles
┌───────────────────────────────────▼────────────────────────────────────┐
│                    6. EVIDENCE & LEDGER PLANE                          │
│     Gideon Verification · Merkle Chained Receipts · PROVENANCE_LEDGER  │
└────────────────────────────────────────────────────────────────────────┘
```

### Plane Responsibilities

1. **Experience Plane:** Owns user intent input, markdown rendering, and headless WebMCP agent streaming. Prohibited from evaluating policies or managing raw secrets.
2. **Control Plane:** Owns identity validation, capability leases, entitlement evaluation, and revocation epochs. Prohibited from raw source parsing.
3. **Trust & Transport Plane (Bifrost):** Enforces envelope validation, replay attack mitigation, and cryptographic message routing (`ed25519`).
4. **Safety Plane:** Enforces memory ceilings (<350MB RSS), working set trimming (`EmptyWorkingSet`), and VFS write path confinement (`/runtime/camelot/tasks/<id>/worktree/`).
5. **CloudBrain Plane:** Handles multi-provider semantic embeddings, context compilation, and token budgeting (<27.8MB PSS baseline).
6. **Execution Plane:** Dispatches sandboxed workloads with read-only fixtures, synthetic credentials, and zero default internet egress.
7. **Evidence Plane:** Verifies mathematical proofs (Gideon), enforces Iron Gates, and writes append-only SHA-256 receipt chains (`verification_ledger.jsonl`).
8. **Data Plane:** Manages PostgreSQL with Row-Level Security (RLS), SQLite-VSS, and NVMe-backed write-ahead logs.

---

## 3. Authority & Capability Lease Protocol

Agents are never granted perpetual credentials. Every operational write requires a cryptographically signed **Capability Lease**:

```text
Anya (Proposes Effect Manifest)
  │
  ▼
Sentinel (Evaluates Entitlements & Data Risk Tier)
  │
  ├─► [Risk R0–R1] ──► Auto-Lease Issued
  └─► [Risk R2–R4] ──► Excalibur Human-in-the-Loop (HITL) Modal
                            │ (Approved)
                            ▼
              Capability Lease Generated & Signed
              - Pinned Task ID & Node Target
              - Ephemeral VFS Sandbox Scope
              - Bounded Hardware Ceilings (300M High / 350M Max)
              - Monotonic Epoch Timeout
                            │
                            ▼
              Workload Executes in Isolated VFS
                            │
                            ▼
              Gideon Verifies Proof & Diff
                            │
                            ▼
              Ledger Seals Cryptographic Receipt
```

---

## 4. Hardware Resource & Memory Architecture

Adhering to `BIOKINETIC_BAREMETAL_AUDIT_v3_CORRECTED.md` on 8 GB DDR5 physical platforms:

1. **Kernel Memory Compression (`MemCompression`):** Real-time in-RAM LZ compression of cold process frames (PID 3664), eliminating SSD bus bottlenecking.
2. **Locked NVMe Pagefile Geometry:** `AutomaticManagedPagefile = False` with a fixed **8,192 MB initial / 16,384 MB maximum** allocation on `C:\pagefile.sys`, preventing dynamic filesystem allocation stutter during parallel agent loops.
3. **Working Set Trimming:** Automated invocation of Win32 `psapi!EmptyWorkingSet` purging idle working set allocations from long-lived daemons.
4. **VFS Janitorial Sweep:** Enforces strict isolation between `SAFE` (ephemeral build caches), `REVIEW` (stale dist trees), and `PROTECT` (authored source, `.venv`, `node_modules`, and vault ledgers).

---

## 5. WebMCP & Agent-Native Surface (DOC-002 Conformance)

The documentation site itself conforms to the agent-native architecture:
- **`/.well-known/mcp.json`:** Exposes typed RPC schemas for `search_docs`, `get_doc`, `verify_doc_hash`, `search_cloudbrain`, and `cloudbrain_status`.
- **`/api/agent/dump`:** Infinite context compilation endpoint providing zero-overhead, chunked streaming of the entire markdown corpus directly from binary `.rodata`.
- **Inverted Index Engine:** O(1) keyword indexing paired with Gate 2 SHA-256 verification against local canonical source hashes.

```text
⚜ STRUCTURE IS FREEDOM. EVIDENCE IS AUTHORITY. REFLECTION IS TRUTH. ⚜
```
