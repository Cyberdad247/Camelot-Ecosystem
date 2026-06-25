# Phase 3 (MICROVM_LATCH) — Capture Plan

**Status:** capture pipeline **SCAFFOLD BUILT**; awaiting operator WSL2 enable +
`bin/phase3_one_shot.sh` final=GO run to populate the verdict file.

This document is the operator runbook for the Phase 3 (HiveIDE_Apex_v1000) capture
pipeline. It describes what the agent-side scaffolding does, what the operator
triggers, and what surfaces are still fenced behind `control_plane/soul_oversight`.

## Artifacts shipped in this planning cycle

| File | Role |
|---|---|
| `bin/phase3_one_shot.sh` | Operator-facing wrapper; chains preflight → install → post-preflight #1 → post-preflight #2 with a single JSON final verdict |
| `bin/phase3_one_shot.sh` (GO branch) | **NEW CAPTURE** — writes `{"final":"GO",…,"captured_at":"…"}` to `03_VAULT/runtime_state/hive_ide_apex_v1000/wsl2_verdict.json` whenever reached |
| `bin/cold_boot_bench.sh` | Stub capture script (HUMAN_GATE-safe); reads the verdict JSON and prints the bench hand-off commands |
| `03_VAULT/runtime_state/hive_ide_apex_v1000/wsl2_verdict.json` | Capture file written by `phase3_one_shot.sh` on GO; git-tracked so the Iron Gate ledger can pin the GO marker |
| `03_VAULT/runtime_state/phase3_pending_prerequisite.md` | (Previously shipped) pre-flight runbook for WSL2 / BIOS enablement |

## Capture flow

```
[operator]  bash bin/phase3_one_shot.sh          # inside WSL2 distro
   ├─ step 1/4  pre-install preflight           (baseline /dev/kvm + libkrun)
   ├─ step 2/4  install_libkrun.sh              (libkrun0 + librun0 install)
   ├─ step 3/4  post-install preflight #1       (verify the install actually happened)
   ├─ step 4/4  post-install preflight #2       (v7 polish #4 /dev/kvm stability)
   └─ final verdict
       ├─ final=GO     → writes wsl2_verdict.json + exits 0
       ├─ final=NO-GO  → exits 1 (no file write)
       └─ final=PARTIAL → exits 3 (no file write)

[operator]  bash bin/cold_boot_bench.sh
   ├─ reads wsl2_verdict.json (Promotes HiveIDE_Apex_v1000 evidence_class: aspirational → planned)
   └─ prints operator-actionable bench hand-off commands

[operator]  cargo test --manifest-path 01_KERNEL/reasoning/ouroboros_engine
   └─ REQUIRES A FRESH [y] for the Phase 3 destructive edits
      (01_KERNEL/core/microvm_cages/uffd_server.rs and cow_snapshotter.sh)
```

## Evidence transitions

The HiveIDE_Apex_v1000 crystal's evidence class transitions as follows
(per AGENTS.md / Codex Meta-Harness Adapter):

| Gate | Evidence class |
|---|---|
| Now (substrate not yet approved in WSL2) | `aspirational` |
| `wsl2_verdict.json` shows `final=GO` (operator runs wrapper inside WSL2) | `planned` |
| `cold_boot_bench.json` shows the 12 ms cold-boot boot reproduces locally | `confirmed` |
| Conflict with verified runtime state (eg, WSL2 fails or BIOS rejects nested virt) | `rejected` |

## Reversibility

| Surface | Reversal command |
|---|---|
| `wsl2_verdict.json` capture file | `git checkout HEAD -- 03_VAULT/runtime_state/hive_ide_apex_v1000/` |
| Wrapper extension (GO-branch file-write) | `git checkout HEAD -- bin/phase3_one_shot.sh` |
| Bench stub | `git checkout HEAD -- bin/cold_boot_bench.sh` |
| This runbook | `git checkout HEAD -- docs/architecture/phase3_capture_plan.md` |
| Phase 3 destructive surface (`01_KERNEL/core/microvm_cages/`) | **NOT YET TOUCHED** — gates on `control_plane/soul_oversight.pre_execute(HUMAN_GATE)` with `CAMELOT_DASHBOARD_OPERATOR_TOKEN` |

## Operator checkpoints

1. After the wrapper emits `final=GO` inside WSL2, run `bash bin/cold_boot_bench.sh`
   to verify the verdict file is well-formed and stage the bench hand-off.
2. Bench hand-off (`cargo test`) requires a fresh `[y]` because it triggers the
   Iron Gate HUMAN_GATE for actual UFFD + qemu-img COW scaffolding edits.
3. The 12 ms cold-boot benchmark target is `evidence_class: aspirational` until it
   reproduces locally; promotion to `confirmed` happens after `wsl2_verdict.json`
   confirms GO **and** a `cold_boot_bench.json` artifact exists.

## Out-of-scope for this scaffold

The following surfaces are intentionally NOT touched in this commit:

- `01_KERNEL/core/microvm_cages/uffd_server.rs` — Rust UFFD polling shell (HUMAN_GATE)
- `01_KERNEL/core/microvm_cages/cow_snapshotter.sh` — qemu-img COW snapshotter wrapper (HUMAN_GATE)
- `01_KERNEL/reasoning/ouroboros_engine` test scaffolding (Phase 2 already shipped the
  threshold config + starter; the bench harness lives behind the bench cut)
- `PROVENANCE_LEDGER.md` — auto-written by the camelot-ledger-hook on file changes per AGENTS.md

## See also

- `03_VAULT/runtime_state/phase3_pending_prerequisite.md` — pre-WSL2 runbook
  (operator steps: enable WSL2 via admin PowerShell + BIOS nested-virt + reboot).
  When that runbook succeeds, **this capture plan takes over automatically**
  via `bin/phase3_one_shot.sh` → `bin/cold_boot_bench.sh`.
- `bin/install_libkrun.sh` — Phase 3 substrate installer (chained by
  `phase3_one_shot.sh` step 2/4).
- `bin/phase3_one_shot.sh` — wrapper that emits the final verdict this
  document captures.
- `bin/cold_boot_bench.sh` — bench hand-off stub this document describes.
