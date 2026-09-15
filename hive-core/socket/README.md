# HIVE-CORE: Zero-Copy AgentBus Socket
======================================
VFS Scaffolding Matrix: `/hive-core/socket/`

## Operational Contracts
- **Zero-Copy IPC:** Uses kernel memfd / shared memory channels for inter-process communication between backend logic and UI.
- **Task-Local AgentBus:** Routes streaming telemetry and control packets without serializing through disk or incurring network hops.
- **Sub-100ms Telemetry Enclave:** Synchronous state updates flow at sub-millisecond speeds.
