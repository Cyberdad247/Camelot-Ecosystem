# Graduation Checklist — HiveIDE_Apex_v1000 (aspirational → planned → confirmed)

Per the AGENTS.md Codex Meta-Harness Adapter, each crystal proposal must
graduate through the four evidence classes:

  aspirational -> planned -> confirmed (operational stage gate)
              -> rejected (rejected by evidence)

The HiveIDE_Apex_v1000 crystal is filed as **aspirational** today.

## Planned (works in test environments, documented, but optional in prod)

- [ ] `cargo build -p pmcp` compiles with stable Rust + tokio
- [ ] `cargo test -p pmcp` runs the stdio smoke test
- [ ] `02_FORGE/kinetic/pmcp` README cross-links to the published `@modelcontextprotocol/sdk`
      TypeScript client as a parity reference
- [ ] `scripts/wsl2_preflight.sh` returns verdict=GO; the verdict JSON is captured at
      `03_VAULT/runtime_state/hive_ide_apex_v1000/wsl2_verdict.json`
- [ ] A reversible shell script at `02_FORGE/kinetic/cut-node-mcps.sh` exists and is
      dry-run by default; it requires an explicit `--apply` to mutate
- [ ] The RustClaw `main.rs` comment marks the `camelot-mcp-edge.exe` spawn line as
      `[CUT-DEPRECATED]` with a pointer to the new pmcp endpoint
- [ ] Goose-mcp dual-stack can be safely booted alongside pmcp at port 3002

## Confirmed (operational state)

- [ ] All `02_FORGE/kinetic/*/package.json` files referencing `mcp` or
      `@modelcontextprotocol` are archived under `02_FORGE/kinetic/_mcp_archive/`
- [ ] `bin/awaken.py` invokes `pmcp-server` on port 3002 and no longer invokes
      `camelot-mcp-edge.exe` on 3001; verified by `verify_omniroute.py`
- [ ] `tests/test_legion_mcp_purge.py` writes a no-op shell that asserts no Node.js
      MCP processes are spawned under `bin/awaken.py --quick`
- [ ] `scripts/design_lint.py --repo .` exits 0 with no violations OR any violation
      is documented in PROVENANCE_LEDGER with `CAMELOT_LINT_WAIVER_TOKEN` override
- [ ] `system_triage.py --deep` reports `microVM cold-boot latch == GO` with a
      reproducible cold-boot < 12 ms measurement on the WSL2 substrate

## Rejection paths (if graduated-confirmed is unreachable)

- [ ] If `libkrun` cold-boot cannot reach < 12 ms on any substrate within two
      quarters, document the gap in PROVENANCE_LEDGER and demote the crystal to
      `planned`, retiring the < 12 ms target to the Phase 3 quad-2 backlog.
- [ ] If Tailwind v4 + Lucide-React enforcement creates irreconcilable frictions
      in any sub-package, demote the lint rule to WARN-only and document the
      regression in PROVENANCE_LEDGER.

## WSL2 GO evidence (Phase 3 prerequisite)

The WSL2 GO verdict must include:

- `wsl2`         = present
- `kvm`          = `/dev/kvm` accessible
- `nested_virt`  = intel=K or amd=K
- `userfaultfd`  = kernel >= 4.3
- `libkrun`      = installed

This verdict is captured by:

```sh
bash scripts/wsl2_preflight.sh \
  > 03_VAULT/runtime_state/hive_ide_apex_v1000/wsl2_verdict.json
```

The crystal may **not** be promoted from `aspirational` to `planned` until this
file exists with verdict=GO.
