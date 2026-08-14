# VFS Preflight AC Verification Evidence

**Date:** 2026-08-14 (slice #1 completion — Tasks 1-9 of
`docs/superpowers/plans/2026-08-13-vfs-preflight.md`)
**Runner:** `scripts/ops/check_preflight_ac.sh`
**Host profile:** cybertronia-win (Windows, Python 3.13, Git Bash)

## Result table

| AC | Result | Notes |
|----|--------|-------|
| AC1 | BLOCK | 3/8 CONFIRMED; halted at `port_readiness_scan` (substrate ports closed at stage 0) |
| AC2 | PASS | 1664 ms total (budget < 2000 ms p95) |
| AC3 | PASS | catalog_hash `1c8abe1f…` reproducible across same-scene re-runs |
| AC4 | PASS | deliberately broken boot → strict REJECT with reasons (`vfs_present_run` on missing path) |
| AC5 | PASS | PROVENANCE_LEDGER.md entries before=4381 after=4381 (no preflight-driven writes) |
| AC6 | PASS | advisor → strict graduation: `_graduated.flag` written; second run reads strict |
| AC7 | PASS | two runs in same minute → distinct run dirs (`2026-08-14T15-32-46` / `…48`) |
| AC8 | PASS | `python -m control_plane.preflight --test` → 0, all 8 inline-synthetic checks pass |
| AC9 | PASS | `[VFS_PREFLIGHT] run_id=…` operator summary on stdout |

**Summary:** 8 PASS / 0 FAIL / 1 BLOCK. Exit code 0 (no hard mechanism
assertion failed).

## Interpretation of AC1 (BLOCK)

Strict mode is live (`03_VAULT/runtime_state/preflight/_graduated.flag`).
On this machine **no substrate services are listening** at stage 0
(8080 CLIProxy, 8011 Bifrost sidecar, 11434 Ollama, 4433 Bifrost WS,
4434 Bifrost gRPC — all closed), so check 040 `port_readiness_scan`
REJECTs and the boot hard-halts per ADR 0006. This is the design
working as intended with the sovereign's "leave strict mode" decision:
the boot gate blocks until the operator starts the substrate
(`scripts/ops/start-bifrost.sh` and/or the boot's own later stages) or
re-opens the ports. AC1 becomes PASS on a host with the substrate up.

Checks 010/020/030 reach CONFIRMED in this run (0.2–1.2 s each);
050–080 are skipped after the strict halt. See the newest run manifest
under `03_VAULT/runtime_state/preflight/<UTC>/_manifest.json`.

## What changed vs. the pre-fix baseline

| Finding | Fix | Evidence |
|---|---|---|
| Check 020 license scan unbounded (>120 s over vendored `02_FORGE`; SIGKILL exit 143 every run) | Re-scoped to slice-owned code (`control_plane/preflight`, `tests/preflight`), skip-dirs + `MAX_FLAGGED` cap, SPDX headers added to the 35 slice files | 020 now CONFIRMED in ~0.1–0.2 s; total run 1.6 s (AC2 PASS) |
| Boot-path root mismatch (`first_run: True` while halting strict; graduation wrote to nested unread path) | Single state root: artifacts at `<runtime_state>/preflight/<UTC>/`, flag at `<runtime_state>/preflight/_graduated.flag` for CLI and boot paths | manifests now show `first_run: False` under strict; graduation flag lands on the path strict detection reads (AC6) |
| `--test` wrote self-test artifacts + `_graduated.flag` into live runtime state | `--test` uses an isolated tmp run_root | no new artifacts at `runtime_state/` root; live flag untouched (AC8 still green) |
| Strict REJECT only surfaced as a WARN row (boot continued, exit 1 at end) | Stage-0 wrapper raises `SystemExit(1)` on strict REJECT — hard halt before later stages | AC4 (strict REJECT surfaces + halts) |
| 040 rejection reason opaque | Runner flattens nested bool dicts (`results.<port> = False`) | operator-readable reasons in manifest |

## Rerun

```bash
bash scripts/ops/check_preflight_ac.sh
```

Regenerate this evidence doc with the current output when the substrate
state changes (e.g. after `scripts/ops/start-bifrost.sh`).
