# SYSTEM INSTRUCTION: Microsandbox Hardware MicroVM Cartridge
@ctx|camelot-os.dev/ukg/v10001/cartridges/microsandbox_microvm id|Ω_CARTRIDGE_MICROSANDBOX_MICROVM_V10001

## 1. Architectural Charter & Identity
- **Cartridge ID**: `microsandbox-microvm`
- **Schema**: `camelot-cartridge/1` (Risk Cap: `T1`)
- **Primary Substrates**: Hardware Hypervisor Isolation (KVM / WHPX / `libkrun`), vsock, OCI Container Runner
- **Compatible Knights**: `engineering_builder`, `inference_worker`, `SIR_OCTAVIAN`, `SIR_BORIS`
- **Supported Node Profiles**: `hub`, `engineering`, `experience` (Cross-platform: Windows Cybertronia, Linux Hub, macOS)

## 2. Authorized Entrypoints
- `execute`: Spawn isolated microVM sandbox with hardware boundary enforcement.
- `forge`: Build and verify untrusted OCI images and multi-agent scripts.
- `test`: Run end-to-end sandbox evaluations with zero host contamination.

## 3. Capability Boundary Constraints & Scarcity Governance (Global Law 03)
- **Granted**: `process.allowlisted`, `network.scoped`, `vfs.read`, `vfs.worktree_write`.
- **Strictly Denied**: `lease.issue`, `policy.admin`, `secret.export`, `unrestricted.network`, `direct_main_branch_write`, `auto_merge`, `auto_deploy`.
- **RAM Governor Law**: MicroVM instance strictly constrained to 512 MB RAM max (`resource_profile.memory_mb: 512`).
- **Secret Isolation**: In-VM secret leakage strictly prohibited; credentials injected via host-side proxy over vsock.
