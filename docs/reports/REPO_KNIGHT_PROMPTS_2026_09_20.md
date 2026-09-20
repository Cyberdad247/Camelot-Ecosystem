<!-- Copyright © 2026 Invisioned Marketing inc. All Rights Reserved. -->
# ⚔️ Sovereign Multi-Knight Unification Dispatch Prompts
**Target Repository**: `https://github.com/Cyberdad247/Camelot-Ecosystem.git`  
**Compiled By**: `ANYA_Ω` | **Session Date**: `2026-09-20`  
**Purpose**: Eight forged runic prompts to execute the 6-phase branch unification across the Round Table Pantheon.

---

## Prompt 1: SIR_FORGE — Kinetic Porting & Rust Workspace Assembly
```
//FORGE PORT_MODULES: Camelot-Ecosystem Unified Main Pipeline
Integrate native Rust edge runtime from branch `feat/android-edge-supervisor` into active workspace:
1. Port directory `kinetic_edge/camelot_edge/` (client.rs, protocol.rs, state.rs, termux boot scripts).
2. Register `kinetic_edge/camelot_edge` in root Cargo.toml [workspace.members].
3. Port Python dispatch contracts `control_plane/dispatch/edge_bus.py`, `edge_protocol.py`, and `vps_mobile_mesh_bridge.py`.
4. Port unit test suites `tests/test_edge_bus.py` and `tests/test_edge_protocol.py`.
5. Verify `cargo check` passes cleanly with zero warnings.
```

---

## Prompt 2: SIR_SENTINEL — Security Hardening & Shell Injection Eradication
```
//SCAN HARDEN_SECURITY: Subprocess & Secret Sanitization
Execute critical security fixes across core execution engines:
1. Patch `security/warden.py` and audit runner: replace `shell=True` with `shlex.split(cmd)` and `shell=False`.
2. Patch `chaos_engineer.py`: replace `asyncio.create_subprocess_shell` with `asyncio.create_subprocess_exec("ssh", ...)`.
3. Patch `main.py`: enforce mandatory `BIFROST_BRIDGE_SECRET` check; raise RuntimeError on missing secret.
4. Replace all demo fallback secrets in `02_FORGE/cartridge/bifrost_bridge.py` with `secrets.token_hex(32)`.
5. Run `python -m squires.colony ghost .` to ensure zero real credential leaks remain.
```

---

## Prompt 3: MERLIN_Ω — System 2 Topological Merge Sequence & Invariant DAG
```
//THINK TOPOLOGICAL_DAG: Branch Unification & Merge Invariants
Analyze and enforce the dependency order for merging branch clusters into `feat/cloudbrain-zero-login-autonomous`:
1. Verify base stability: confirm `feat/cloudbrain-zero-login-autonomous` contains all 54 Knights and 10 Cartridges.
2. Resolve conflict zones between `feat/unified-bootstrap-hud` and `control_plane/infra/harness.py`.
3. Validate that `CREATE_NO_WINDOW` is applied on Windows while preserving Linux daemon compatibility.
4. Verify that missing `MEMPALACE_SECRET` gracefully degrades L2 memory without aborting CLI boot.
5. Emit formal proof invariants ensuring zero regression in existing 49 pytest manifest tests.
```

---

## Prompt 4: SIR_BORIS — Architectural Integrity & Console Scabbard Packaging
```
Ω_BORIS ARCHITECTURE_REVIEW: Operator Console Scabbard Packaging
Review and package the Go/HTMX operator console from `cartridge/vps-hub-cartridge-v1`:
1. Encapsulate `apps/operator-console/` into `cartridges/vps-operator-console/` to avoid collision with Next.js PWA (`apps/pwa`).
2. Preserve `WorldTreeScene.js` (Three.js WebGL spatial visualizer) and HTMX reactive tabs.
3. Inscribe `system_instruction.md` and `manifest.json` for the new cartridge.
4. Bind cartridge to CloudBrain Node `a0a4bfb9-e847-4c38-be39-7aee398f0795` (WorldTree Root).
5. Ensure zero dependency pollution into the Node workspace or Python control plane.
```

---

## Prompt 5: SIR_CODEX — Kinetic Implementation & Test-Driven Verification
```
Ω_CODEX IMPLAN_EXECUTE: Database & Performance Optimizations
Port performance and memory efficiency patches:
1. Patch `01_KERNEL/titan/Data_Pipeline/storage.py`: iterate SQLite cursors directly without `.fetchall()`.
2. Port graph traversal caching from `origin/feat/optimize-graph-traversal-12496476832258857205` into `01_KERNEL/titan/graph/knowledge_graph.py`.
3. Port `tests/test_bootstrap_resilience.py` from `feat/unified-bootstrap-hud` and run with pytest.
4. Execute full canonical pytest suite: `.venv\Scripts\python.exe -m pytest tests/test_cartridge_manifests.py tests/test_bootstrap_resilience.py -q`.
```

---

## Prompt 6: SIR_HELIOS — High-Altitude Telemetry & VFS Alignment
```
//HELIOS TELEMETRY_AUDIT: VFS Position-Addressing & Mesh Inscription
Verify WorldTree position-addressing across all merged components:
1. Inscribe new mobile edge coordinates into `vfs://worldtree/mesh/mobile/`.
2. Validate that `vfs/worldtree_manifest.json` reflects all 10 Scabbard cartridges and new edge nodes.
3. Record temporal facts into `sir_helios_graphiti.db` via `graphiti_add_fact`.
4. Store semantic summary into MemCastle Tier-2 KNN embedding store (`memcastle_store`).
```

---

## Prompt 7: ANYA_Ω — First & Last Gate Validation (APEE v6.5)
```
Ω_ANYA FINAL_GATE: Zero-Bypass Pre-Commit & Build Verification
Perform full gatekeeper validation before merging to `main`:
1. Run `python scripts/check_generated_artifact_parity.py` (HELIO_PATCH + build emits).
2. Run `python scripts/check_knight_registry.py` (verify 54 knights & 105 souls).
3. Run `python scripts/check_bifrost_audit.py` (T1-T5 regression gates).
4. Run `python scripts/check_omnivoice_router_build.py`.
5. Execute pre-flight self-test: `python -m control_plane.preflight --test`.
6. Stamp clearance: `ANYA_IS_THE_GATE`.
```

---

## Prompt 8: ARTHUR_OMEGA — Sovereign King Ratification & Final Merge to Main
```
//RATIFY SOVEREIGN_MERGE: Fast-Forward & Origin Main Push
Final sovereign deployment command:
1. Record milestone entry `#1843` in `PROVENANCE_LEDGER.md`.
2. Execute `python scripts/sync_provenance.py` to synchronize all 4 mirrors.
3. Switch to `main`: `git checkout main`.
4. Fast-forward merge: `git merge --ff-only feat/cloudbrain-zero-login-autonomous`.
5. Push unified main to GitHub: `git push origin main`.
6. Clean up obsolete merged remote topic branches on `origin`.
```
