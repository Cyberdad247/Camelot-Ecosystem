#!/usr/bin/env python3
"""
Camelot-OS — harness run-all (single entry point for the gate checklist).

Runs the full contract-harness battery in one invocation and reports a
per-check PASS/FAIL table. This is the script behind `harness/gate.sh` and the
GitHub Actions gate (`.github/workflows/harness-gate.yml`).

Checks (order matters — documented in docs/architecture/harness-gate.md):

  1. replay-committed — verify the *committed* golden receipts and ledger
     anchors from disk under the pinned TEST-ONLY signer key. Runs first so a
     tampered, stale, or missing committed artifact fails the gate before any
     rebuild can overwrite it.
  2. build            — rebuild + emit golden receipts: schema conformance,
     §11.3 chain rule, 7-case tamper battery, ledger anchoring (STEP 5,
     N=1000) with the 4-case T-10 anchor battery.
  3. replay-emitted   — re-verify the just-emitted artifacts from disk
     (determinism: they must be byte-identical to the committed set).
  4. schema-meta      — meta-validate all 26 published schemas against the
     Draft 2020-12 meta-schema + index.json catalog conformance.

Every check runs even if an earlier one fails, so the report is complete;
the exit code is 0 only if ALL checks pass.

Usage:  python harness/run_all.py
        python harness/run_all.py --anchor-every 100 --chain-size 5000
            # stress-test the full gate under a different anchoring config
        python harness/run_all.py --check schema-meta
            # run only the schema meta-validation check (fast iteration)
        python harness/run_all.py --check replay --check schema-meta
            # run the two replay checks plus schema-meta

Flags:
    --anchor-every N   forwarded to the receipt-chain checks (default 1000)
    --chain-size N     forwarded to the receipt-chain checks (default 2000)
    --check NAME       run only checks whose id contains NAME (repeatable,
                       comma-separated; case-insensitive substring match).
                       With no --check, all checks run. If a filter matches
                       nothing, the script exits 2 listing valid ids.
    --list-checks      print the valid check ids and exit.

Output:
    Every check's full output is teed to the console AND captured to
    harness/results/<check-id>.log (UTF-8, overwritten per run, with a header
    recording the command and a footer recording the exit code). Upload
    harness/results/ as a CI artifact for post-run retention.

Env:    PYTHON overrides the interpreter used for the child checks
        (default: the interpreter running this script).
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Windows consoles default to cp1252, which cannot encode the ✓/✗ glyphs used
# in output. Force UTF-8 (with replacement fallback) so the harness never
# crashes on print, regardless of the active console codepage.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
PYTHON = os.environ.get("PYTHON") or sys.executable
RESULTS_DIR = HERE / "results"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--anchor-every", type=int, default=None,
        help="anchor every N entries (default 1000); forwarded to the receipt-chain checks",
    )
    parser.add_argument(
        "--chain-size", type=int, default=None,
        help="anchored chain size (default 2000); forwarded to the receipt-chain checks",
    )
    parser.add_argument(
        "--check", action="append", default=[], metavar="NAME",
        help="run only checks whose id contains NAME (repeatable / comma-separated; "
             "case-insensitive substring); valid ids: replay-committed, build, "
             "replay-emitted, schema-meta",
    )
    parser.add_argument(
        "--list-checks", action="store_true",
        help="print the valid check ids and exit",
    )
    return parser.parse_args(argv)


def select_checks(
    checks: list[tuple[str, list[str], str]],
    filters: list[str],
) -> list[tuple[str, list[str], str]]:
    """Filter the check list by --check filters (case-insensitive substring
    match on the check id, applied to the comma-split union of all filters).
    Empty filters keep all checks; a filter matching nothing is an error."""
    if not filters:
        return checks
    lowered = [
        part.strip().lower()
        for raw in filters
        for part in raw.split(",")
        if part.strip()
    ]
    selected = [
        c for c in checks
        if any(f in c[0].lower() for f in lowered)
    ]
    if not selected:
        valid = ", ".join(c[0] for c in checks)
        sys.stderr.write(f"error: --check matched no checks "
                         f"(valid ids: {valid})\n")
        sys.exit(2)
    return selected


def build_checks(flags: list[str]) -> list[tuple[str, list[str], str]]:
    """The four gate checks. Receipt-chain checks receive the forwarded
    anchoring flags; replay checks still use the persisted config from
    chain.verified (the flags are only meaningful at build/emit time), and
    schema-meta takes no flags."""
    return [
        (
            "replay-committed",
            [PYTHON, "contracts/verify_receipt_chain.py", "--replay", *flags],
            "Committed golden receipts + ledger anchors verify from disk (pinned key)",
        ),
        (
            "build",
            [PYTHON, "contracts/verify_receipt_chain.py", *flags],
            "Rebuild: schema conformance, §11.3 rule, 7 tamper cases, anchors emitted",
        ),
        (
            "replay-emitted",
            [PYTHON, "contracts/verify_receipt_chain.py", "--replay", *flags],
            "Emitted artifacts re-verify from disk (determinism vs committed set)",
        ),
        (
            "schema-meta",
            [PYTHON, "contracts/validate_contract_schemas.py"],
            "26 schemas meta-validate as Draft 2020-12; catalog conformance",
        ),
    ]


def run_check(name: str, cmd: list[str], purpose: str) -> int:
    """Run one check, teeing its output to the console and to
    harness/results/<name>.log (UTF-8). The log gets a header with the command
    and a footer with the exit code, so CI artifact retention captures the full
    per-check output for post-run debugging."""
    log_path = RESULTS_DIR / f"{name}.log"
    print(f"\n>>> [{name}] {purpose} (log: harness/results/{name}.log)")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8", errors="replace") as log:
        log.write(f"# check: {name}\n")
        log.write(f"# purpose: {purpose}\n")
        log.write(f"# cmd: {' '.join(cmd)}\n\n")
        try:
            proc = subprocess.Popen(
                cmd, cwd=HERE,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            )
        except OSError as e:
            line = f"[launch error] {e}\n"
            log.write(line)
            sys.stdout.write(line)
            return 127
        for raw in proc.stdout:
            line = raw.decode("utf-8", errors="replace")
            log.write(line)
            sys.stdout.write(line)
            sys.stdout.flush()
        rc = proc.wait()
        log.write(f"\n# exit code: {rc}\n")
        sys.stdout.write(f"  (log: harness/results/{name}.log, exit {rc})\n")
    return rc


def main() -> int:
    args = parse_args(sys.argv[1:])
    if args.list_checks:
        for name, _, purpose in build_checks([]):
            print(f"{name:20s} {purpose}")
        return 0
    flags = []
    if args.anchor_every is not None:
        flags += ["--anchor-every", str(args.anchor_every)]
    if args.chain_size is not None:
        flags += ["--chain-size", str(args.chain_size)]
    all_checks = build_checks(flags)
    checks = select_checks(all_checks, args.check)
    print("=" * 72)
    print("Camelot-OS harness — run-all (gate checklist)")
    print(f"per-check logs: {RESULTS_DIR.relative_to(HERE.parent)}/")
    print("=" * 72)

    results: list[tuple[str, int]] = []
    for name, cmd, purpose in checks:
        rc = run_check(name, cmd, purpose)
        results.append((name, rc))

    print("\n" + "=" * 72)
    if args.check:
        print("GATE CHECKLIST (filtered: " + ", ".join(args.check) + ")")
    else:
        print("GATE CHECKLIST")
    print("=" * 72)
    failed = [name for name, rc in results if rc != 0]
    for name, rc in results:
        print(f"  [{'FAIL' if rc else 'PASS':4}] {name}")
    print("=" * 72)
    if failed:
        print(f"✗ {len(failed)} check(s) FAILED — gate blocked: {', '.join(failed)}")
        return 1
    print("✓ ALL CHECKS PASSED — gate cleared.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
