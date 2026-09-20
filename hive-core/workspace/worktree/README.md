# HIVE-CORE WORKSPACE: WORKTREE ENCLAVE
=======================================
VFS Coordinate: `/hive-core/workspace/worktree/`
Security Enclave: **Sentinel Lease**

## Operational Invariants
- **Ephemeral Approved-Write Sandbox:** Ephemeral WASM microVM workers compile and synthesize code exclusively within bounded subdirectories here.
- **Copy-on-Write (CoW) Isolation:** Kernel page sharing restricts memory delta to $\Delta \le 0.12\text{ MiB}$ per active agent process.
- **Sentinel Capability Lease:** Every active build process requires an Ed25519-signed lease. Expired or violated leases trigger instant sandbox evaporation.
- **Zero-Disk Clutter:** Unpromoted work evaporates upon task conclusion or verification failure.
