# Local Environment Backplane — v10001.00-CYBERTRONIA
@ctx|camelot-os.dev/ukg/v10001/local_env @typ|Hardware_Ceilings_Topology id|Ω_ENV_V10001

| Parameter | Specification | Invariant / Enforcement |
| :--- | :--- | :--- |
| **Node Architecture** | 4GB Edge Node (Cybertronia Windows + Cleveland Edge Anchor) | 4GB_EDGE_NODE_STRICT — Floor: <480MB Active (Heaviside Trigger at 3686 MB / 90%) |
| **Sovereign Server Hub** | Bifrost Gateway / Central Postgres DB / Vector Hub | 8GB_SERVER_ALLOWANCE_STRICT (Up to 8192 MB for Central Sovereign Gateway only) |
| **Primary Orchestrator** | cybertronia (100.118.224.52, Windows 11 Root) | Root host for VFS World Tree, Bifrost Gateway, and Antigravity |
| **VFS World Tree Root** | vfs://worldtree/cybertronia/ (Tether: a0a4bfb9-e847-4c38-be39-7aee398f0795) | Position-addressed VFS coordinates across all Round Table nodes |
| **Edge Defense (Aegis)** | cloudflare-go programmatic WAF & Zero Trust Tunnels | Real-time dynamic IP blocking, edge rate-limiting, and Kyber-768 mTLS boundary |
| **Agent Execution Core** | PiG (Go-Native Agent Harness) + Wasmtime | Sub-5ms startup, static Go binary, concurrent goroutine slices (Δ ≤ 0.12 MiB) |
| **Sir Helios Harness** | FastMCP / agy (Gemini 3.8 Flash / Pro) | Dynamic CloudBrain UUID ab8aa359-2b3b-4bc1-b41f-34979cdc184e + Graphiti DB |
| **Shared Memory** | ZeroClaw memory-mapped IPC slabs (.agent/) | Atomic reader-writer file locks with stale PID reclamation & MADV_DONTNEED |
| **Lattice Geometry** | 24D_LEECH_LATTICE_Λ24_ACTIVE | Leech Lattice Λ24 spatial indexing for episodic vector memories |
| **Security Perimeter** | Post-Quantum Kyber-768 WireGuard / Tailscale tunnels | mTLS on 100.110.180.18 + Sir Heimdall Zero-Trust perimeter lock |
| **Telemetry Transport** | WSS / SSE stream on Port :8095 and Bifrost :3001 | Canonical 2-Strand HTMX fragments & Bifrost Board on :5173 |
| **FOSS System-2 Core** | SmolLM3-3B 1.58-bit Ternary Core (Jev Ω) | Zero-cloud offline reasoning fallback with Lightbot WASM |
