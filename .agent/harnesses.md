# Execution Harnesses

**Domain**: `Kinetic_Boundaries`  
**Standard**: `Zero-Trust Boundary Enforcement`

## Sandboxing Engine Specifications
- **Primary Sandbox**: `Deer_Flow` Dockerless Sandboxing (Rust-embedded QuickJS engine).
- **MicroVM Subsystem**: `forkd` Copy-on-Write (CoW) Linux sandboxes with `Δ ≤ 0.12 MiB` startup overhead.
- **Resource Constraints**: Strict 8GB ARM64 edge node quota enforcement.
- **Verification**: Gideon verdict emission with cryptographic proof envelope.
