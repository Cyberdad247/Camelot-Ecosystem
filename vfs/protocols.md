---
id: protocols
title: The Iron Gate
context: "camelot-os.dev/ukg/v4000/vfs_master_scaffold"
type: Root_Floorplan
---
# The Iron Gate Protocols & Sovereign Rules of Engagement
@ctx|camelot-os.dev/ukg/v10001/vfs_protocols id|Ω_VFS_PROTOCOLS_V10001

Strict operational laws, security perimeters, and execution standards for Camelot-OS:

## 1. The Titanium Laws & System Mandates
1. **Anya First & Last Gate**: Zero unverified code commits. All proposals require Anya Gate clearance (`ANYA_IS_THE_GATE`).
2. **Provenance Ledger Integrity**: Every kinetic change, crystal generation, or file modification MUST be recorded in `PROVENANCE_LEDGER.md` across all 4 mirrors (root, `03_VAULT/`, `docs/`, `03_VAULT/training/configs/`).
3. **Iron Gate**: Changes > 10 lines or > 50MB require explicit human-in-the-loop (HITL) authorization unless granted via session lease.
4. **Rule 7 Zero Hot-Path Bloat**: Strict 0% Python/Node in performance-critical hotpath; 100% native Rust, Go, WASM, and systemd.
5. **Rule 8 College Sophomore Summary**: Always append a clear "College Sophomore" intuitive summary translating complex distributed concepts into relatable software engineering principles.

## 2. Resource Scarcity & Boundary Protocols
- **4GB / 8GB Host Ceilings**: Strict RSS boundaries. No agent or child worker may exceed assigned memory bounds.
- **Z3 Formal SMT-LIB Gate**: Verification of DAG acyclicity, state invariance, and contract safety prior to production promotions.
- **Zero-Trust mTLS & Bifrost Bridge**: All inter-node and telemetry streams on `:3001` traverse verified mTLS channels via the Tailscale mesh.

## 3. Scabbard Cartridge Protocol (`camelot-cartridge/1`)
- **Ed25519 Signing**: Every cartridge manifest must be signed with ed25519 and verified against `signing_key.pub`.
- **Denied Authority Capabilities**: Strict denial of `lease.issue`, `policy.admin`, `secret.export`, `unrestricted.network`, `direct_main_branch_write`, `auto_merge`, `auto_deploy`.
- **Ephemeral Rollback**: Rollbacks default to `destroy_ephemeral_worktree`.

## 4. Air-Gap Privacy & Credential Protocol
- **Strict Zero-Cloud Secret Routing**: Live secrets (`secret|token|key|password`) route to `SIR_GHOST` (local Ollama container) and never touch third-party cloud LLM context windows.
- **Fixture Differentiation**: Integration test tokens and mock placeholders are explicitly annotated as `mock_secret` (severity `info`) to maintain high signal-to-noise ratio in security telemetry.

## 5. Anya Glyph Engine Protocol
- Orchestrates VFS intents and token compression through Anya's Quantum Mantra Glyph Engine (`vfs/anya_glyph_engine.py`).

