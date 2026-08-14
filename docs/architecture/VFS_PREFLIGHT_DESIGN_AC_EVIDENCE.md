# VFS Preflight AC Verification Evidence

**Date:** 2026-08-14 (slice #1 completion — Tasks 1-9 of
`docs/superpowers/plans/2026-08-13-vfs-preflight.md`)
**Runner:** `scripts/ops/check_preflight_ac.sh`
**Host profile:** cybertronia-win (Windows, Python 3.13, Git Bash)

## Result table

| AC | Result | Notes |
|----|--------|-------|
| AC1 | PASS | **all 8 CONFIRMED** (run_id `preflight-2026-08-14T15-56-40-2588ad`) with the substrate up |
| AC2 | PASS | 1317 ms total (budget < 2000 ms p95) |
| AC3 | PASS | catalog_hash `1c8abe1f…` reproducible across same-scene re-runs |
| AC4 | PASS | deliberately broken boot → strict REJECT with reasons (`vfs_present_run` on missing path) |
| AC5 | PASS | PROVENANCE_LEDGER.md entries before=4399 after=4399 (no preflight-driven writes) |
| AC6 | PASS | advisor → strict graduation: `_graduated.flag` written; second run reads strict |
| AC7 | PASS | two runs in same minute → distinct run dirs (`2026-08-14T15-56-45` / `…48`) |
| AC8 | PASS | `python -m control_plane.preflight --test` → 0, all 8 inline-synthetic checks pass |
| AC9 | PASS | `[VFS_PREFLIGHT] run_id=…` operator summary on stdout |

**Summary: 9 PASS / 0 FAIL / 0 BLOCK.** Exit code 0.

## Substrate state (AC1)

The 040 `port_readiness_scan` ports were opened 2026-08-14 to reach
AC1 (all 8 CONFIRMED):

| Port | Service | How it was started |
|------|---------|--------------------|
| 8080 | CLIProxyAPI | `cli-proxy-api.exe` (cwd `C:\Users\vizio\CLIProxyAPI`) |
| 8011 | Bifrost Go sidecar | `boot_bifrost_go_sidecar()` (token at `~/.camelot/bifrost.token`) |
| 11434 | Ollama | `ollama serve` |
| 4433 | Bifrost WS | `bash scripts/ctl.sh start` → `bin/bifrost_engine` |
| 4434 | Bifrost gRPC | same engine (`apps/bifrost/main.go`) |

Stop: `bash scripts/ctl.sh stop` (4433/4434) + terminate the
cliproxy/sidecar/ollama processes. These are boot-time daemons; on a
normal `bin/awaken.py` boot the later stages own them.

Checks 010/020/030/040 each reach CONFIRMED in 0.1–1.2 s; 050–080 pass
when reached. See the newest run manifest under
`03_VAULT/runtime_state/preflight/<UTC>/_manifest.json`.

## What changed vs. the pre-fix baseline

| Finding | Fix | Evidence |
|---|---|---|
| Check 020 license scan unbounded (>120 s over vendored `02_FORGE`; SIGKILL exit 143 every run) | Re-scoped to slice-owned code (`control_plane/preflight`, `tests/preflight`), skip-dirs + `MAX_FLAGGED` cap, SPDX headers added to the 35 slice files | 020 now CONFIRMED in ~0.1–0.2 s; total run 1.3 s (AC2 PASS) |
| Boot-path root mismatch (`first_run: True` while halting strict; graduation wrote to nested unread path) | Single state root: artifacts at `<runtime_state>/preflight/<UTC>/`, flag at `<runtime_state>/preflight/_graduated.flag` for CLI and boot paths | manifests now show `first_run: False` under strict; graduation flag lands on the path strict detection reads (AC6) |
| `--test` wrote self-test artifacts + `_graduated.flag` into live runtime state | `--test` uses an isolated tmp run_root | no new artifacts at `runtime_state/` root; live flag untouched (AC8 still green) |
| Strict REJECT only surfaced as a WARN row (boot continued, exit 1 at end) | Stage-0 wrapper raises `SystemExit(1)` on strict REJECT — hard halt before later stages | AC4 (strict REJECT surfaces + halts) |
| 040 rejection reason opaque | Runner flattens nested bool dicts (`results.<port> = False`) | operator-readable reasons in manifest |
| Bare `python` in catalog commands resolved (via CreateProcess) to a uv-managed base interpreter without PyYAML → 060 `tool_registry_presence` rejected | Runner rewrites a leading `python`/`python3` command token to `sys.executable` — probes always run in the preflight interpreter | 060 now CONFIRMED; regression test `test_runner_runs_probes_with_own_interpreter` |
| 080 `lattice_yaml_consistency` rejected: probe resolved paths from the wrong base (relative-path parent arithmetic → `C:\Users` instead of the home dir) and the frozen lattice declared a purged `worldmonitor` subproject | Probe resolves the lattice absolutely and checks repo root + home dir + cwd; `worldmonitor` moved to `dormant_archive` in `lattice.yaml` | 080 now CONFIRMED; AC1 8/8 PASS |

## Rerun

```bash
bash scripts/ops/check_preflight_ac.sh
```

Regenerate this evidence doc with the current output when the substrate
state changes (e.g. after `scripts/ops/start-bifrost.sh`).
