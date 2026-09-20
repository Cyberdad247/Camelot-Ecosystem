# HIVE-CORE WORKSPACE: SOCKET IPC ENCLAVE
=========================================
VFS Coordinate: `/hive-core/workspace/socket/`
Security Enclave: **AgentArmor**

## Operational Invariants
- **ZeroClaw Zero-Copy IPC (`memfd_create`):** High-speed inter-container communication using lock-free ring buffers in shared memory.
- **Zero Duplicate Token State:** Data payloads are shared via memory descriptors rather than serialization passes.
- **AgentArmor Bound:** Restricts IPC traffic to authorized peer agents and prevents memory snooping.
