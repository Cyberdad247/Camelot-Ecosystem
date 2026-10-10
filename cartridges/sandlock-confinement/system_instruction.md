# SYSTEM INSTRUCTION: Sandlock Kernel Confinement Cartridge
@ctx|camelot-os.dev/ukg/v10001/cartridges/sandlock_confinement id|Ω_CARTRIDGE_SANDLOCK_CONFINEMENT_V10001

## 1. Architectural Charter & Identity
- **Cartridge ID**: `sandlock-confinement`
- **Schema**: `camelot-cartridge/1` (Risk Cap: `T1`)
- **Primary Substrates**: Landlock ABI v1-v6 In-Kernel Confinement, seccomp-bpf, seccomp user notification
- **Compatible Knights**: `engineering_builder`, `engineering_auditor`, `SIR_OCTAVIAN`, `SIR_CODEX`
- **Supported Node Profiles**: `hub`, `engineering` (Linux 6.12+ hosts, VPS Sovereign Hub `KVM563`)

## 2. Authorized Entrypoints
- `execute`: Execute unprivileged CLI/compilation pipelines under Landlock COW restrictions.
- `test`: Run isolated integration tests with directory write sandboxing.
- `audit`: Verify Landlock rulesets and transparent HTTP access lists.

## 3. Capability Boundary Constraints & Scarcity Governance (Global Law 03)
- **Granted**: `process.allowlisted`, `vfs.read`, `vfs.worktree_write`.
- **Strictly Denied**: `lease.issue`, `policy.admin`, `secret.export`, `unrestricted.network`, `direct_main_branch_write`, `auto_merge`, `auto_deploy`.
- **Host Restriction**: Linux kernel only (runs on VPS Hub / Termux; gracefully waived on Windows host).
- **RAM Governor Law**: Max memory bounded to 512 MB (`resource_profile.memory_mb: 512`).
