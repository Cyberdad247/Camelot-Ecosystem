# Phase 3 — MICROVM_LATCH (HiveIDE_Apex_v1000)
**Status:** `NO-GO` — Phase 3 substrate not available on this host at the time of the Phase 1/2 cut window (2026-06-25).

## Why NO-GO
- `bash scripts/wsl2_preflight.sh` reports verdict=NO-GO (WSL2 not installed).
- `libkrun` (`apt-get install libkrun0`) and `userfaultfd` (kernel >= 4.3) are Linux-only.
- The 12 ms cold-boot target requires UFFD pre-warm + `qemu-img cow` snapshotter scaffolding
  under `01_KERNEL/core/microvm_cages/`, which currently contains only `forkd_runner.sh`.
- Runtime host is Windows MINGW64; the entire Phase 3 stack pivots to WSL2 / nested-virt KVM.

## Operator prerequisites (in order; admin shell for #1)
1. **Enable WSL2** (one-time, requires an admin PowerShell on Windows):
   ```powershell
   wsl --install
   wsl --set-default-version 2
   ```
2. **Enable nested virtualization** in BIOS/UEFI for the host CPU (Intel VT-x or AMD-V).
3. **Reboot** so the WSL2 kernel initializes and `/dev/kvm` becomes accessible.
4. **Verify WSL2 readiness** by re-running the preflight:
   ```bash
   bash scripts/wsl2_preflight.sh
   ```
   Every check should report `warn:false` and verdict=`GO`.
5. **Install Phase 3 substrate** in the WSL2 dist:
   ```bash
   bash bin/install_libkrun.sh
   ```
   This installs `libkrun0 librun0` (via `apt-get`) and falls back to a `cargo install krun-cli`
   if apt is unavailable.
6. **Re-authorize the Phase 3 cut** with `[y]` so the Iron Gate clears the scaffold of
   `01_KERNEL/core/microvm_cages/` (the UFFD polling shell + cold-boot benchmark).
7. **Fire the cargo test**: `cargo test --manifest-path 01_KERNEL/reasoning/ouroboros_engine`
   so the live BitNet b1.58 + selective-scan SSM pass produces the 12 ms latency number.

## Evidence-class chain (per AGENTS.md ledger)
- `confirmed` once steps 1-7 above reproduce locally and `bash scripts/wsl2_preflight.sh` returns GO.
- `planned` while any of steps 1-7 are pending.
- `aspirational` until the 12 ms cold-boot benchmark is reproducible.
- `rejected` if WSL2 install fails or `/dev/kvm` is locked at the host.

## Reversibility
- Step 6 (`[y]`) gates the destructive edits to `01_KERNEL/core/microvm_cages/`.
- Aborting `bash bin/install_libkrun.sh` mid-flight leaves the WSL2 dist untouched
  (the script is idempotent — it re-checks before each install step).
- `git checkout HEAD -- 01_KERNEL/core/microvm_cages/` reverts any scaffolding commit.
- Phase 3 changes do NOT touch the Windows host; the Phase 1/2 cuts in this commit are
  fully independent.

## Where the artifacts will live once Phase 3 is unblocked
- `bin/install_libkrun.sh` (script committed in this turn, ready to execute).
- `01_KERNEL/core/microvm_cages/uffd_server.rs` (Rust UFFD polling shell, scaffold TBD).
- `01_KERNEL/core/microvm_cages/cow_snapshotter.sh` (qemu-img wrapper, scaffold TBD).
- `03_VAULT/runtime_state/hive_ide_apex_v1000/wsl2_verdict.json` (GO/NO-GO marker emitted
  by `scripts/wsl2_preflight.sh` on each run; promotion gate).
- Provenance ledger entry 1741+ once the operator token authorizes step #6.
