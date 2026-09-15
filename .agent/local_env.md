# Local Environment Backplane — v10001.00-CYBERTRONIA
@ctx|camelot-os.dev/ukg/v10001/local_env @typ|Hardware_Ceilings_Topology id|Ω_ENV_V10001

| Parameter | Specification | Invariant / Enforcement |
| :--- | :--- | :--- |
| **Node Architecture** | 8GB Edge Node (Cybertronia Windows + KVM563 Linux VPS) | `8GB_EDGE_NODE_STRICT` — Zero Docker Bloat (`Docker == NULL`) |
| **Memory Ceiling** | 8.0 GB RAM Hard Ceiling (Active: 1.4 GB / 8.0 GB) | cgroups v2 slices (`camelot-critical`, `camelot-workers`) |
| **Shared Memory** | `memfd_create` anonymous shared memory slabs | O(1) Zero-Copy IPC buffer handover between local daemons |
| **Lattice Geometry** | `24D_LEECH_LATTICE_Λ24_ACTIVE` | Leech Lattice Λ24 spatial indexing for episodic vector memories |
| **Security Perimeter** | Post-Quantum Kyber-768 WireGuard / Tailscale tunnels | mTLS on `100.110.180.18` + Sir Heimdall Zero-Trust perimeter lock |
| **Telemetry Transport** | WSS / SSE stream on Port `:8095` and Bifrost `:3001` | Native WebGPU / Three.js HUD on Excalibur S26 Ultra |
