# Ouroboros Prefetcher Integration: Architectural Proposals

**Module:** 01_KERNEL/reasoning/ouroboros_engine
**Objective:** Seamlessly integrate the asynchronous UFS-to-RAM double-buffer prefetcher (SPECS-B2 & B3) and handle inline dequantization constraints (SPECS-B4).

## Context
The Ouroboros engine manages tiered KV-cache offloading to UFS 4.0 flash storage. To prevent stalling the NPU during token generation, we must prefetch the next layer's KV pages into LPDDR5X RAM asynchronously. Concurrently, when merging 4-bit (IQ4_NL) cached prefixes with 16-bit (FP16) generated suffixes, we must handle scale collisions dynamically.

---

## Approach 1: Dedicated Prefetch Thread Pool (Worker per Block)
**Architecture:** 
- A dedicated thread pool inside `ouroboros_engine` monitors the attention layer progression.
- As layer `L` computes, a worker thread asynchronously issues a Direct I/O read for layer `L+1`'s KV blocks from UFS 4.0 into a pre-allocated pinned RAM buffer.

**Data Flow:**
`Aegis Shield (NPU/CPU)` -> Signals Layer `L` -> `Ouroboros Thread Pool` -> Direct I/O Read (UFS) -> `Pinned RAM Buffer (L+1)`.

**Dequantization Handling (SPECS-B4):**
- The pinned RAM buffer is memory-mapped directly into the compiler's attention kernel.
- The kernel uses a fused inline dequantization step: it multiplies the incoming 4-bit weights by their stored scaling factors directly during the MAC (Multiply-Accumulate) operation with the FP16 suffix.

**Pros:** Simple to implement, deterministic scaling logic.
**Cons:** Thread context-switching overhead could impact low-power CPU cores.

---

## Approach 2: Global Async I/O Event Loop (`io_uring`)
**Architecture:**
- Utilize Linux `io_uring` (via Rust bindings) to manage all UFS-to-RAM transfers without dedicated threads.
- `ouroboros_engine` submits non-blocking read SQEs (Submission Queue Entries) for upcoming layers.
- The `aegis_shield` polls the CQE (Completion Queue) just-in-time before executing the layer.

**Data Flow:**
`Aegis Shield` -> Submit SQE (L+1) -> Execute L -> Poll CQE (L+1) -> Context Merge.

**Dequantization Handling (SPECS-B4):**
- Dequantization is vectorized (SIMD/NEON) and executed in a pipeline stage immediately after the CQE indicates the buffer is ready, just before the attention kernel runs.

**Pros:** Zero thread context-switch overhead; maximizes throughput on ARM64.
**Cons:** Platform-specific (`io_uring` limits portability), higher complexity in error handling (e.g., if a CQE isn't ready in time).

---

## Approach 3: Speculative-Driven Prefetch (Tied to Aegis Gate)
**Architecture:**
- Tie the prefetch depth to the `Speculator` accept-rate gating (SPECS-A1). 
- If the `Speculator` is active (high accept rate), `ouroboros` aggressively prefetches multiple future layers into a ring buffer. 
- If speculative decoding is suspended, prefetching drops to a standard single-layer lookahead.

**Data Flow:**
`Aegis Speculator` -> Broadcast Accept Rate -> `Ouroboros Engine` -> Dynamically sizes Async Read requests -> `Ring Buffer`.

**Dequantization Handling (SPECS-B4):**
- Scale collision matrices are pre-computed during the speculative draft phase. When the actual token is accepted, the dequantization scales are already loaded into L1 cache, allowing immediate fusion with the FP16 suffix.

**Pros:** Highly adaptive; saves memory bandwidth when speculation is suspended.
**Cons:** High coupling between `ouroboros` memory manager and `aegis_shield` logic.

---

## Recommendation
**Approach 2 (Global Async I/O Event Loop)** combined with the adaptive sizing from **Approach 3** provides the best balance of performance (zero-copy, zero-thread-switch) and efficiency on our ARM64 architecture.

**Next Steps:**
1. Review proposals.
2. Select the target architecture.
3. Flesh out the detailed architecture and interface contracts between `ouroboros_engine` and `aegis_shield`.