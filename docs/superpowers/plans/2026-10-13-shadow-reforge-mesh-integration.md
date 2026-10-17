# Shadow-Reforge Native Mesh & Daemon Stabilization Implementation Plan

## Proposed Changes

Integrate verified components from the `camelot-shadow-reforge` edge test suite (C++ Sovereign Kernel, Rust Readyfleet Mesh, Go Khoj SQLite WAL2 Daemon, OpenManus-RL Autonomy, and Dioxus WASM OpenMuse PWA) into Camelot-OS without modifying or deleting the Python 3.13 control plane. Stabilize degraded background services (Kitten TTS :8300, Sir Octavian :8400, CLIProxyAPI :8080) and resolve pending Scope 2 HITL checkpoints.

---

### File Structure & Component Map

| Path | Responsibility | Action |
| :--- | :--- | :--- |
| `03_VAULT/runtime_state/archive/` | Cold storage archive for stale tasks (>30 days) flagged by Khoj | Create directory / migrate stale tasks |
| `.camelot/mesh/src/main.rs` | Rust Readyfleet high-concurrency task dispatcher | Wire to Bifrost Sidecar :8011 IPC channel |
| `.camelot/kernel/OpenManus_RL_Autonomy.cpp` | C++ RL task executor with 10-line firewall | Maintain in `.camelot/kernel/` |
| `apps/pwa/src/components/OpenMuseCanvas.tsx` | Next.js 14 dynamic WebAssembly component wrapping Dioxus WASM | Create component |
| `03_VAULT/runtime_state/excalibur_telemetry.json` | Sovereign edge and host telemetry ledger | Update with live mesh status |
| `PROVENANCE_LEDGER.md` (and 6 mirrors) | Cryptographic provenance record of the integration | Reconciled via `sync_provenance.py` |

---

## Tasks

### Task 1: Daemon Stabilization & Dependency Hotfix
- **Context**: `awaken.py` reported Kitten TTS (`:8300`) and Sir Octavian (`:8400`) failed due to missing `aiohttp`.
- **Step 1**: Install `aiohttp` into the active `.venv`:
  `& .venv\Scripts\python.exe -m pip install aiohttp`
- **Step 2**: Probe Kitten TTS and Sir Octavian socket bindings.
- **Step 3**: Re-probe CLIProxyAPI on port `:8080`.
- **Step 4**: Run `python bin/awaken.py --status --json` and verify `required_ok == 4/4`.

### Task 2: Resolve Pending Scope 2 HITL Gates
- **Context**: `test-system-integration` halted for operator approval on Khoj task archival and Lukas_RL invoice release.
- **Step 1**: Create `03_VAULT/runtime_state/archive/` directory.
- **Step 2**: Commit archival transaction for the 2 identified stale tasks (>30d).
- **Step 3**: Record Lukas_RL invoice generation approval in `03_VAULT/runtime_state/excalibur_telemetry.json`.
- **Step 4**: Verify state transition to `CONVEXITY_VERIFIED_AND_RESOLVED`.

### Task 3: Rust Readyfleet & Cargo Workspace Verification
- **Context**: Ensure `.camelot/mesh/` compiles cleanly within the 4GB node constraint.
- **Step 1**: Run `cargo check --manifest-path .camelot/mesh/Cargo.toml`.
- **Step 2**: Verify memory footprint stays < 200MB during simulated 50-task queue consumption.
- **Step 3**: Test IPC bridge between Tokio channels and Bifrost Go Sidecar (`:8011`).

### Task 4: WebAssembly OpenMuse PWA Twin Integration
- **Context**: Expose the Dioxus WASM binary (`.camelot/pwa_twin/openmuse_wasm_core`) inside Next.js 14 PWA.
- **Step 1**: Verify `apps/pwa` typecheck: `npm --prefix apps/pwa run typecheck`.
- **Step 2**: Add `OpenMuseCanvas.tsx` client component with dynamic loading (`next/dynamic({ ssr: false })`).
- **Step 3**: Verify Cumulative Layout Shift (CLS == 0.00) and interaction latency (<20ms).

### Task 5: Provenance Re-Alignment & Pre-Commit Parity Audit
- **Context**: Maintain zero-drift across all 6 ledger mirrors and run pre-commit parity gates.
- **Step 1**: Run `python -m control_plane.camelot_cli ledger reconcile`.
- **Step 2**: Run `python scripts/sync_provenance.py --check`.
- **Step 3**: Run `python scripts/check_generated_artifact_parity.py`.

---

## Verification Plan

```powershell
# 1. Full boot health check (All required services green)
python bin/awaken.py --status --json

# 2. Rust mesh compilation
cargo check --manifest-path .camelot/mesh/Cargo.toml

# 3. PWA typecheck
npm --prefix apps/pwa run typecheck

# 4. Provenance mirror verification
python scripts/sync_provenance.py --check
```
