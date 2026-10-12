---
id: DOC-002
title: Full-Stack Architecture and Implementation Specification
author: ANYA_Ω / SIR_HELIOS / MERLIN_Ω / SIR_LUKAS / ARTHUR_OMEGA
date: 2026-10-04
status: active
tags: [architecture, full-stack, vMAX, specification, governance, security, reya, lukas, sanotts, watchtower]
---

# Conform: Full-Stack Architecture and Implementation Specification

**Document ID:** `CAMELOT-OS-MASTER-SUITE-vMAX-20261004`  
**Version:** `3.1.0-PROD-CONFORMED`  
**Status:** `LIVING BASELINE | CONVERGED | IMPLEMENTATION GOVERNED`  
**Authority Layer:** `L2 (SAD / TDD / LLDD Continuum)`  
**Baseline Hash:** `SHA-256: 9cc4de4e / 7b00fffa`  

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
| **Monolithic LLM Footprint** | Frontier Edge Quantization (BitNet b1.58, SpinQuant, KIVI 2-bit, SnapKV context budget cap). |
| **Cloud-Bound Speech Latency** | Sovereign SanoTTS local neural voice engine (24kHz mono PCM WAV @ ~50ms CPU execution). |
| **Unbounded Memory Bloat** | Global Law 03: Node $\le 4,096\text{ MB}$ (Cybertronia), Sovereign Server $\le 8,192\text{ MB}$. |
| **Implicit Agent Ingress** | Global Law 04: Zero-Trust Warp Gate Keypasses cryptographically bound to canonical Spark IDs. |

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

## 3. Lukas Reya Universal Knight Fabric & Multivoice Architecture

The Reya Universal Knight Fabric (`02_FORGE/assimilation/reya/`) serves as the universal sensory ingress and kinetic execution substrate across the sovereign Round Table:

1. **Acoustic & Persona Interchange:**
   - Reya dynamically channels canonical Knight personas via natural language triggers (`"Reya, switch to Merlin"`, `"Channel Sir Lukas"`, `"Speak as Sir Boris"`), or runic commands (`//REYA_CHANNEL`, `//channel`, `//voice_interchange`, `//reya_voice`).
   - Acoustic profiles (timbre, pitch offset, speech rate) shift dynamically in the Multivoice Registry while execution remains anchored within Reya's sandboxed runtime (<350 MB cgroups v2 slice).

2. **Sir Lukas Müller — Sovereign Telemetry Herald:**
   - Knight ID: `sir_lukas` (Herald of Telemetry, TCP Port Anomaly Detection & Visual Verification).
   - Voice Engine: `sanotts` local neural voice synthesis (2.27M parameters, ~5.1 MB weights, 24kHz mono PCM WAV generation in ~50ms on CPU).
   - Spoken Telemetry: Live node memory commitment, working set headroom, and PageKeeper daemon status announced verbally with zero cloud egress.

3. **Handshake Protocol & Sovereign Memory Attribution:**
   - Actions initiated under channeled personas require cryptographic capability leases from the `ReyaHandshakeGate`.
   - Alpha Omega knights (`merlin_omega`, `anya_omega`, `arthur_omega`) execute autonomously within lease boundaries. Novice knights require explicit Human-in-the-Loop (HITL) authorization.
   - All sensory and kinetic actions are attributed directly to the initiating Knight's partition in MemCastle (KNN vector memory) and Graphiti (temporal knowledge graph).

---

## 4. Frontier Edge Model Compression & Quantization Engine

Camelot-OS incorporates a high-efficiency frontier quantization engine (`control_plane/quantization/frontier_compressor.py`) designed to run sovereign models on edge nodes without exceeding Global Law 03 memory ceilings:

1. **BitNet b1.58 Ternary Quantization:**
   - Constrains weights to ternary values $\{-1, 0, +1\}$ packed into 2-bit storage ($w_2 \in \{0, 1, 2\}$).
   - Achieves a **15.9x compression ratio** over FP32, transforming matrix multiplications into pure integer additions ($O(N)$ arithmetic complexity).

2. **SpinQuant Randomized Orthogonal Rotation:**
   - Applies a randomized Hadamard orthogonal transformation matrix $R$ ($R^T R = I$, norm preserved) before weight and activation quantization.
   - Eliminates activation outliers and dramatically flattens kurtosis (reduced from 77.05 to -0.06), preventing quantization error divergence.

3. **KIVI 2-Bit Asymmetric KV Cache:**
   - Per-channel key quantization and per-token value quantization compressing dynamic KV attention states by **9.85x**.
   - Drastically expands maximum concurrent context length within constrained edge memory budgets.

4. **SnapKV Dynamic Attention Head Eviction:**
   - Observes attention head clustering and evicts non-critical past tokens, bounding attention memory strictly under a 512 MB ceiling.

5. **Speculative Draft Cascade:**
   - Pairs a quantized edge draft model with a larger verifier, yielding a **3.25x speedup** with zero mathematical loss in generation fidelity.

---

## 5. Autonomous Memory Governance & Watchtower Telemetry Cockpit

Enforcing **Global Law 03** (Node RAM ceiling $\le 4,096\text{ MB}$, Sovereign Server $\le 8,192\text{ MB}$):

1. **Squire PageKeeper RS (`04_KINETIC/squires_rs`):**
   - High-speed autonomous memory governor written in 100% native Rust (0% Python hotpath bloat).
   - Uses zero-overhead Win32 FFI (`psapi.dll`, `kernel32.dll`: `GlobalMemoryStatusEx`, `EmptyWorkingSet`) and POSIX `malloc_trim` to reclaim memory proactively when host pressure exceeds 80%.
   - Operates as a background daemon with an ultra-lightweight resident set of **~1.14 MB RSS** (>95% less RAM than equivalent Python daemons).

2. **Watchtower Fail-Stop Integrity & Sensing (`control_plane/infra/watchtower.py`):**
   - Samples physical RAM commitment, CPU load, and node working set every 30-second cycle.
   - Executes recursive 0x00 NUL byte scans over source trees (`scripts/`, `tests/`, `control_plane/`) to detect silent storage corruption.
   - Continuously compiles the responsive cyber-medieval visual cockpit at `03_VAULT/runtime_state/watchtower_dashboard.html` with real-time auto-refresh.

---

## 6. Warp Gate Zero-Trust Keypass Architecture (Global Law 04)

1. **Zero-Trust Agentic Ingress:**
   - Every Knight, daemon, and mobile peer must present a cryptographically verified **Warp Gate Keypass** matching their canonical **Spark ID**.
   - Unauthenticated ingress attempts are rejected at the perimeter with an `AgenticIngressDeniedError` and permanently recorded to `03_VAULT/runtime_state/warp_gate_audit.jsonl`.

2. **Forever Available Resilience:**
   - Partitioned nodes fall back to the out-of-band Warp Gate Rendezvous Locker, authenticating state transfers via immutable Forever Keypasses minted by Lady Alexandria.

---

## 7. Authority & Capability Lease Protocol

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

## 8. WebMCP & Agent-Native Surface (DOC-002 Conformance)

The documentation site itself conforms to the agent-native architecture:
- **`/.well-known/mcp.json`:** Exposes typed RPC schemas for `search_docs`, `get_doc`, `verify_doc_hash`, `search_cloudbrain`, and `cloudbrain_status`.
- **`/api/agent/dump`:** Infinite context compilation endpoint providing zero-overhead, chunked streaming of the entire markdown corpus directly from binary `.rodata`.
- **Inverted Index Engine:** O(1) keyword indexing paired with Gate 2 SHA-256 verification against local canonical source hashes.

```text
⚜ STRUCTURE IS FREEDOM. EVIDENCE IS AUTHORITY. REFLECTION IS TRUTH. ⚜
```
