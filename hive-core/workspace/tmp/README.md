# HIVE-CORE WORKSPACE: TMP SCRATCH ENCLAVE
=========================================
VFS Coordinate: `/hive-core/workspace/tmp/`
Security Enclave: **cgroups v2 Gate**

## Operational Invariants
- **Quota-Limited Scratch Execution Zone:** Hard 64MB memory ceiling enforced per linear memory instance.
- **Volatile Lifespan:** Files created here are strictly ephemeral and automatically purged upon sandbox termination.
- **OOM Protection:** Guarantees that runaway loops or massive allocations cannot cause host kernel out-of-memory interruptions under the 8GB Scarcity Protocol.
