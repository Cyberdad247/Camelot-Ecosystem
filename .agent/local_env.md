# Local Environment Backplane — v10001.00-CYBERTRONIA
@ctx|camelot-os.dev/ukg/v10001/local_env @typ|Hardware_Ceilings_Topology id|Ω_ENV_V10001

| Parameter | Specification | Invariant / Enforcement |
| :--- | :--- | :--- |
| **Node Architecture** | 4GB Edge Node (Cybertronia Windows + Cleveland Edge Anchor) | 4GB_EDGE_NODE_STRICT — Floor: <480MB Active |
| **Primary Orchestrator** | cybertronia (100.118.224.52, Windows 11 Root) | Root host for VFS World Tree, Bifrost Gateway, and Antigravity |
| **VFS World Tree Root** | fs://worldtree/cybertronia/ (Tether: 0a4bfb9-e847-4c38-be39-7aee398f0795) | Position-addressed VFS coordinates across all Round Table nodes |
| **Topology Descriptor** | WASM-REYA-SMOLLM3-S2S-OMNI-NEXUS-Λ24 | 6 Core Glyph Mechanisms bound across live runtime |
| **Sir Helios Harness** | FastMCP / agy (Gemini 3.8 Flash / Pro) | Dynamic CloudBrain UUID b8aa359-2b3b-4bc1-b41f-34979cdc184e + Graphiti DB |
| **Memory Ceiling** | 4096 MB RAM Edge Ceiling (Heaviside Trigger at 3686 MB / 90%) | Active memory floor <480 MB; automatic cold page NVMe flush |
| **Shared Memory** | ZeroClaw memory-mapped IPC slabs (.agent/) | Atomic reader-writer file locks with stale PID reclamation |
| **Lattice Geometry** | 24D_LEECH_LATTICE_Λ24_ACTIVE | Leech Lattice Λ24 spatial indexing for episodic vector memories |
| **Security Perimeter** | Post-Quantum Kyber-768 WireGuard / Tailscale tunnels | mTLS on 100.110.180.18 + Sir Heimdall Zero-Trust perimeter lock |
| **Telemetry Transport** | WSS / SSE stream on Port :8095 and Bifrost :3001 | Canonical 2-Strand HTMX fragments (htmx-docs.vercel.app) |
| **FOSS System-2 Core** | SmolLM3-3B 1.58-bit Ternary Core (Jev Ω) | Zero-cloud offline reasoning fallback with Lightbot WASM |
