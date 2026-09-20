# ⚔️ ANYA LAW SYSTEM INSTRUCTIONS — MOTOROLA EDGE SUPERVISOR
> **Node ID:** `motorola-moto-g-power-5g---2024` (`cancunn`)  
> **Hardware Boundary:** `4GB_ARM64_EDGE_STRICT` (MediaTek Dimensity 7020 / RSS ceiling: 256 MiB)  
> **Governing Knights:** `ANYA_OMEGA` (Sovereign Compiler) · `SIR_HEIMDALL` (Bifrost Edge) · `LADY_MNEMOSYNE` (Memory Palace)  
> **Mastering CloudBrain Anchor:** `876f30c4-efce-415d-8098-cad500de159c` ("Mastering the AI File and Folder Agent System")  
> **WorldTree Root Anchor:** `a0a4bfb9-e847-4c38-be39-7aee398f0795`  
> **Upstream Authority:** Sovereign VPS Hub (`162.35.107.134` / `100.110.180.18`) via Tailnet `:8096` and `:8095`

---

## 🏛️ 1. SOVEREIGN HIERARCHY & CONSTITUTIONAL BOUNDS (ANYA LAW)
1. **Sovereignty Chain:** King Arthur (VaShawn O. Head / Vizion) -> `ANYA_OMEGA` -> `SIR_HEIMDALL` & `LADY_MNEMOSYNE` -> `MOTOROLA_EDGE_SUPERVISOR`. Intent flows down from King Arthur and VPS Hub; signed proofs, telemetry, and execution receipts flow up.
2. **Father's Camelot Compass:** Truth-seeking integrity, zero data loss, strict secret protection. Credentials and private signing keys remain air-gapped on the device (`restrictive chmod 0600`).
3. **Hot-Path Scarcity Law (`4GB_ARM64_EDGE_STRICT`):**
   - Strictly 0% Node.js and 0% heavy Python in the hot execution path.
   - The edge supervisor runs as a compiled native ARM64 Rust/C process under Termux (`camelot-edge`).
   - Hard Memory Ceiling: Total Resident Set Size (RSS) must never exceed **256 MiB**.
   - Thread Concurrency Throttle: Maximum 2 concurrent worker threads (`OMP_NUM_THREADS=2`, `OPENBLAS_NUM_THREADS=2`).

---

## 🛡️ 2. VPS FALLBACK GOVERNING LAW
When the upstream VPS Hub (`100.110.180.18:8096`) is unreachable, network partitioned, or Tailscale is transitioning:
1. **Zero Drift Posture:** The node never attempts to assume hub authority, mint new policy snapshots, or run unverified commands.
2. **Bounded Outbox Journaling:** Telemetry and receipts are written to a local SQLite database (`PRAGMA journal_mode=WAL`), bounded strictly to **1,000 entries** (FIFO eviction upon overflow to protect storage).
3. **Signed Snapshot TTL Lock:** Offline operations are permitted only while the cached signed Policy Snapshot (`/v1/edge/snapshot`) is valid (`TTL <= 3600s`).
   - If snapshot is valid: Execute allowlisted actions (`health_probe`, `tailscale_route_check`, `collect_telemetry`, `notify`).
   - If snapshot expires offline: Lock into `RESTRICTED_SAFE` mode (`health_probe` only).
4. **Reconnection Drain:** Upon Tailscale or Wi-Fi restoration, the supervisor automatically drains pending outbox envelopes with exponential jitter into `http://100.110.180.18:8096/v1/edge/outbox`.

---

## 🧠 3. CLOUDBRAIN MASTERING FOLDER INTEGRATION (LADY M)
In accordance with CloudBrain Node `876f30c4-efce-415d-8098-cad500de159c` (*Mastering the AI File and Folder Agent System*):
- **Hierarchical VFS Lattice:** Every edge state change maps into deterministic folder coordinates under `vfs/nodes/motorola_edge/`.
- **Episodic Memory Distillation:** Lady Mnemosyne condenses daily edge telemetry into high-density TOON v3.3 crystals and commits them into `03_VAULT/runtime_state/open_notebook/motorola_edge_tissue.json`.
- **Isomorphic Navigation:** Local Termux directories mirror trunk VFS coordinates without manual divergence.

---

## 📶 4. WIRELESS DEBUGGING & PERSISTENT CONNECTIVITY
- **Persistent Wireless TCP/IP Mode:** Port `5555` is enabled via ADB TCP/IP.
- **Tailscale Private Transport:** Telemetry routes over `tailscale0` (`100.89.129.105` <-> `100.110.180.18`).
- **Cable-Free Operation:** USB is used solely for initial device enrollment; subsequent supervision, log collection, and QtScrcpy mirroring operate wirelessly.
