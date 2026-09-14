# HIVE-CORE WORKSPACE: SOURCE ENCLAVE
=====================================
VFS Coordinate: `/hive-core/workspace/source/`
Security Enclave: **VFS Guardian**

## Operational Invariants
- **Read-Only Pinned Snapshot:** Serves as the immutable reference point for AST compilation.
- **Write Mutation Lock:** Any attempt by an ephemeral microVM worker to mutate files in this directory trips the VFS Guardian, immediately revoking the worker's capability lease and evaporating the sandbox.
- **Cryptographic Purity:** Backed by SHA-256 integrity trees.
