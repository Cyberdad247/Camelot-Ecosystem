#!/usr/bin/env python3
"""Pre-commit gate: graft context-graph freshness (advisory by default).

Runs `graft check` and reports whether graft/ matches the working tree.
The graph is a local, regenerable cache (git-ignored), so staleness is not a
correctness problem for the commit itself — this hook surfaces it so the
committer can run `graft build` when they want fresh orientation data.

Why advisory (exit 0 on every outcome unless --strict):

* graft's tree-sitter pass is a native process that can abort with
  0xC0000409 mid-parse on memory-pressured hosts — upstream NanoNets/Graft
  issue #122 documents the same non-deterministic failure mode (crash point
  varies run to run; more likely with low commit charge, which is the norm
  on this 8 GB Windows box). A crash says nothing about the commit.
* the graft CLI may not be installed on a fresh clone or CI runner.
* a hard hang must not stall the commit; anything past the timeout degrades
  to a warning.

`--strict` flips every non-green outcome to exit 1 for environments where
enforcement is wanted (e.g. a future CI job with adequate memory).

Exit contract:
    0  graph in sync, or any degraded outcome (missing CLI, stale, crash,
       timeout, spawn error) in advisory mode
    1  --strict and not in sync
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys

CHECK_TIMEOUT_S = 60


def _warn(msg: str) -> None:
    print(f"graft-graph: {msg}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit 1 on stale/crash/timeout instead of warning (default: advisory)",
    )
    args = parser.parse_args(argv)
    fail = 1 if args.strict else 0

    graft = shutil.which("graft")
    if not graft:
        _warn("graft CLI not on PATH — skipping freshness check "
              "(npm install -g @nanonets/graft)")
        return fail

    try:
        proc = subprocess.run(
            [graft, "check"],
            capture_output=True,
            text=True,
            timeout=CHECK_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired:
        _warn(f"graft check timed out after {CHECK_TIMEOUT_S}s — treating as "
              "degraded, not a failure; retry later with: graft check")
        return fail
    except OSError as exc:
        _warn(f"could not launch graft ({exc}) — skipping")
        return fail

    output = ((proc.stdout or "") + (proc.stderr or "")).strip()
    tail = output[-500:] if output else "(no output)"

    if proc.returncode == 0:
        print("graft-graph: in sync ✓ (graft check rc=0)")
        return 0
    if proc.returncode == 1:
        _warn(f"graft graph STALE — run `graft build` when convenient.\n{tail}")
        return fail
    _warn(
        f"graft check aborted (rc={proc.returncode}, native crash) — known "
        "graft issue #122 pattern; graph state not assessed.\n"
        "manual check: graft check"
    )
    return fail


if __name__ == "__main__":
    sys.exit(main())
