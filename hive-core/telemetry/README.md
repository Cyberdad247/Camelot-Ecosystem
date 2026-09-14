# HIVE-CORE: Telemetry Buffers
==============================
VFS Scaffolding Matrix: `/hive-core/telemetry/`

## Operational Contracts
- **Real-Time Rendering Buffers:** Continuously feeds the WebGPU dashboard with live agent telemetry.
- **8GB RAM Scarcity Monitor:** Tracks active microVM memory footprints and triggers alerts if allocation exceeds 85% of edge capacity.
- **Shader Pipeline:** `glass_cockpit.wgsl` processes spatial matrices for the 3D-to-2D glass cockpit.
