# CAMELOT-OS v9000.14-CYBERTRONIA — Task DAG

| Metric | Count |
| :--- | :--- |
| Total Tasks | 34 |
| Critical Path (P0) | 8 |

## Phase 1: IRON (Foundation Repair)
- [ ] **P1-T01** [P0] (SIR_FORGE) Size: S - Add `__version__ = '9000.14'` to all 13 control_plane modules.
  - *Criteria*: `python -c "from control_plane.anya_gate import __version__; assert __version__ == '9000.14'"` passes for all modules.
- [ ] **P1-T02** [P0] (SIR_FORGE) Size: M - Wire ColMAD into `anya_gate` pipeline (call after `_stage_triage` for CRITICAL/HIGH intents).
  - *Criteria*: Unit test shows CRITICAL intent triggers 3-persona vote.
- [ ] **P1-T03** [P0] (SIR_BORIS) Size: M - Resolve `FOUNDRY_COUNCIL` (19) vs `_SKILLGRAPH_TIER` (22) mismatch.
  - *Criteria*: Single unified roster, `knight_agent --test` passes.
- [ ] **P1-T04** [P1] (SIR_BORIS) Size: S - Decide fate of orphaned `triage_score.py`: merge useful parts into `factory_lane` or archive.
  - *Criteria*: No orphaned imports remain.
- [ ] **P1-T05** [P1] (SIR_FORGE) Size: M - Consolidate SoulOversight v1 class and Iron Gate v2 `pre_execute()` into single coherent API.
  - *Criteria*: `soul_oversight --test` passes.
- [ ] **P1-T06** [P1] (SIR_FORGE) Size: S - Remove `AnyaCompiler` duplicate from `anya_gate.py`.
  - *Criteria*: Only APEE pipeline remains, existing tests pass.
- [ ] **P1-T07** [P1] (SIR_FORGE) Size: S - Fix Colony Nexus import chain — replace try/except cascade with explicit lazy import pattern.
  - *Criteria*: Import works with and without colony module.
- [ ] **P1-T08** [P2] (SIR_FORGE) Size: M - Wire Inspira metrics to live data — `mamba_compression_ratio` from `ouroboros`, `kv_cache_hit_rate` from `soul_router`.
  - *Criteria*: `inspira_metrics --test` shows non-zero values when ouroboros is available.
- [ ] **P1-T09** [P2] (SIR_CODEX) Size: L - Build RTK noise-stripping DLL (Rust) for anya_gate Phase 7 ctypes bridge.
  - *Criteria*: `cargo build` produces `rtk.dll`, `anya_gate` loads it.
- [ ] **P1-T10** [P0] (SIR_SENTINEL) Size: M - Full squire colony triage, fix all CRITICAL findings.
  - *Criteria*: `python -m squires.colony triage . --auto-approve` exits 0.

## Phase 2: SOUL (Kinetic Execution Loop)
- [ ] **P2-T01** [P0] (SIR_FORGE) Size: L, Deps: [P1-T02, P1-T05] - Implement Kinetic Execution Loop as `control_plane/kinetic_loop.py`. 6 stages: Sense → Plan → Wait → Execute → Validate → Deploy.
  - *Criteria*: End-to-end test fires all 6 stages in order.
- [ ] **P2-T02** [P0] (MERLIN_OMEGA) Size: XL, Deps: [P1-T05] - Implement real Z3 patch verification — PDDL encoding for git/state mutations.
  - *Criteria*: Known-dangerous patch gets Z3_BLOCK.
- [ ] **P2-T03** [P1] (SIR_BORIS) Size: L, Deps: [P2-T01] - Create 11 Pillars enforcement layer — `control_plane/obsidian_pillars.py` with pillar validators.
  - *Criteria*: Each pillar has positive/negative test cases.
- [ ] **P2-T04** [P1] (SIR_BORIS) Size: M, Deps: [P1-T03] - Align Knight Pantheon — map v9000.14 names to v1000 knights, add aliases.
  - *Criteria*: `soul_router` resolves all v9000.14 names.
- [ ] **P2-T05** [P1] (SIR_FORGE) Size: M - Upgrade FirnFlow for World Tree context hydration — directory-scoped context loading.
  - *Criteria*: `firnflow --test` shows scoped retrieval.
- [ ] **P2-T06** [P2] (SIR_DEBUG) Size: L, Deps: [P2-T01] - Implement Adversarial Crucible test runner — ephemeral test execution for compiled artifacts.
  - *Criteria*: Test artifact runs in isolation, results reported.
- [ ] **P2-T07** [P2] (SIR_FORGE) Size: M - Implement Immutable Provenance via atomic SQLite with `.shadow` rollbacks.
  - *Criteria*: Rollback restores previous state on failure.

## Phase 3: BRAIN (Agent-Native MDX + Bifrost Board)
- [ ] **P3-T01** [P0] (SIR_BORIS) Size: L, Deps: [P2-T01] - Design Agent-Native MDX schema (Summary, FileMap, Diagram, ApprovalButton, ContextSources).
  - *Criteria*: JSON Schema validates sample MDX.
- [ ] **P3-T02** [P0] (SIR_CODEX) Size: XL, Deps: [P3-T01] - Build HTMX Bifrost Intelligence Board with SSE. Use Tailwind v4 + Luxora Gold (#D4AF37).
  - *Criteria*: HTTP request to board returns valid HTML with htmx attributes.
- [ ] **P3-T03** [P1] (SIR_FORGE) Size: M, Deps: [P3-T01] - `/visual-plan` MDX renderer — converts kinetic_loop DAG to MDX.
  - *Criteria*: Valid MDX output for sample intent.
- [ ] **P3-T04** [P1] (SIR_FORGE) Size: M, Deps: [P3-T01] - `/visual-recap` MDX renderer — post-execution summary.
  - *Criteria*: Valid MDX with test results.
- [ ] **P3-T05** [P1] (SIR_FORGE) Size: M, Deps: [P3-T02, P1-T08] - SSE telemetry pipe from Inspira to Bifrost Board.
  - *Criteria*: EventSource receives live metrics.
- [ ] **P3-T06** [P2] (SIR_CODEX) Size: M, Deps: [P3-T02, P2-T01] - ApprovalButton HITL flow — WebSocket approval gate.
  - *Criteria*: Button click resumes kinetic loop.

## Phase 4: MESH (Network Fabric)
- [ ] **P4-T01** [P1] (SIR_CODEX) Size: XL - Tailscale tsnet integration in Node_C_Omni_Router.
  - *Criteria*: Two nodes communicate via tsnet.
- [ ] **P4-T02** [P1] (SIR_SENTINEL) Size: L, Deps: [P4-T01] - Wire Kyber-768 into mesh transport — mTLS with ML-KEM-768.
  - *Criteria*: TLS handshake uses post-quantum key exchange.
- [ ] **P4-T03** [P1] (SIR_FORGE) Size: L, Deps: [P4-T01] - Empire Drone discovery + registration protocol.
  - *Criteria*: New drone auto-registers on mesh join.
- [ ] **P4-T04** [P2] (SIR_CODEX) Size: L, Deps: [P4-T02] - Migrate pqcrypto from unmaintained crate to ml-kem 0.3.x.
  - *Criteria*: `cargo test` passes, no RustSec advisories.
- [ ] **P4-T05** [P2] (SIR_FORGE) Size: L, Deps: [P4-T03] - ZeroClaw zero-copy shared memory (Linux/WSL2 only).
  - *Criteria*: memfd_create benchmark shows zero-copy IPC.

## Phase 5: EDGE (MicroVM + WASM + Swarm)
- [ ] **P5-T01** [P1] (SIR_CODEX) Size: XL, Deps: [P2-T06] - WASM32-WASI compilation pipeline.
  - *Criteria*: Rust → WASM → wasmtime execution.
- [ ] **P5-T02** [P1] (SIR_FORGE) Size: XL, Deps: [P4-T05] - Unikraft/libkrun MicroVM pill launcher (5MB). **BLOCKED: WSL2+KVM.**
  - *Criteria*: Boot pill, health endpoint responds.
- [ ] **P5-T03** [P2] (SIR_CODEX) Size: XL, Deps: [P5-T01] - Ethereum Swarm (BZZ) artifact pinning.
  - *Criteria*: Pin + retrieve by hash.
- [ ] **P5-T04** [P2] (SIR_FORGE) Size: L, Deps: [P5-T02] - 4GB Scarcity Protocol memory manager.
  - *Criteria*: ZRAM LZ4 + MADV_DONTNEED lease working.
- [ ] **P5-T05** [P2] (SIR_HELIO) Size: L, Deps: [P3-T02] - Hermes-Jarvis voice ingress.
  - *Criteria*: Voice command → kinetic loop intent.
- [ ] **P5-T06** [P3] (SIR_FORGE) Size: L, Deps: [P5-T02, P5-T03] - Sovereign Preview Drones.
  - *Criteria*: Local deploy before Swarm pin.
