#!/usr/bin/env python3
"""
check_bifrost_audit.py — Re-runs the audit verify_cmd strings from
control_plane/bifrost_triage_swarm.TASK_PLAN against the current code,
so the 2026-06-24 Bifrost dispatch-core audit findings (and any future
additions to TASK_PLAN) cannot silently re-open.

Usage:
    python scripts/check_bifrost_audit.py
    CAMELOT_OS_HOME=/path/to/camelot python scripts/check_bifrost_audit.py

Exit codes:
    0 — every audit verify_cmd string passed
    1 — one or more verify_cmd strings failed (regression detected)
    2 — environment error (CAMELOT_OS root not found, TASK_PLAN import failed)

Sync assumption: this script imports TASK_PLAN at runtime, so adding a
new T6 / T7 to the audit picks up automatically — no edit to this file
needed. The single source of truth is
control_plane/bifrost_triage_swarm.TASK_PLAN.

The script is the canonical verifier for the `bifrost-audit-verify`
pre-commit hook (see .pre-commit-config.yaml) and the
`bifrost-audit` GitHub Actions job (see .github/workflows/verify_os.yml).
"""
from __future__ import annotations

import os
import shlex
import subprocess
import sys
from pathlib import Path


def _resolve_python() -> str:
    """Return the absolute path to a working Python interpreter.

    Tries `python` first, then falls back to `python3` if the first
    fails (e.g. on Linux distros where only `python3` is on PATH, or on
    Windows dev hosts where `python` is not in the bash subshell's
    $PATH). If both fail, returns sys.executable (the interpreter that
    ran this script) as a last resort.
    """
    for cmd in ("python", "python3"):
        try:
            proc = subprocess.run(
                [cmd, "-c", "import sys; print(sys.executable)"],
                capture_output=True, text=True, timeout=10,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                return proc.stdout.strip()
        except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
            continue
    return sys.executable


def _camelot_root() -> Path:
    env = os.environ.get("CAMELOT_OS_HOME")
    if env:
        return Path(env).resolve()
    # scripts/check_bifrost_audit.py -> CAMELOT_OS/
    return Path(__file__).resolve().parent.parent


def main() -> int:
    root = _camelot_root()
    if not (root / "control_plane" / "bifrost_triage_swarm.py").is_file():
        print(f"[FATAL] CAMELOT_OS root not found at {root}", file=sys.stderr)
        print("        (set CAMELOT_OS_HOME or run from inside the repo)", file=sys.stderr)
        return 2

    sys.path.insert(0, str(root))
    try:
        from control_plane.dispatch.bifrost_triage_swarm import TASK_PLAN
    except Exception as e:
        print(f"[FATAL] could not import control_plane.bifrost_triage_swarm: "
              f"{type(e).__name__}: {e}", file=sys.stderr)
        return 2

    print(f"Bifrost Audit Re-verification ({len(TASK_PLAN)} task(s); "
          f"CAMELOT_OS={root})\n")

    # Resolve a working Python interpreter (python, then python3, then
    # sys.executable). We bypass bash entirely for any verify_cmd whose
    # first token is `python` or `python3` -- run those via direct
    # subprocess.run with the resolved absolute path as argv[0]. This
    # sidesteps two Windows-specific bash issues we hit trying to go
    # through bash:
    #   (1) `subprocess.run(["bash", "-c", cmd])` -- list2cmdline on
    #       Windows mangles quoting of semicolons / $vars, so $PYTHON_BIN
    #       export inside the cmd expands to empty.
    #   (2) writing bash_cmd to a tempfile in the Windows temp dir --
    #       bash on this host cannot access files under
    #       `C:\Users\...\AppData\Local\Temp\` regardless of POSIX path.
    # Direct subprocess with absolute python path works on both Windows
    # and Linux/macOS without any indirection.
    python_path = _resolve_python()

    failures: list[tuple[str, str, int, str]] = []
    for task in TASK_PLAN:
        # Tokenize verify_cmd and detect python-prefixed tasks.
        try:
            argv = shlex.split(task.verify_cmd)
        except ValueError as e:
            print(f"  [FAIL] {task.id:5} {task.title}  (parse error: {e})")
            failures.append((task.id, task.verify_cmd, 2, f"shlex: {e}"))
            continue

        if argv and argv[0] in ("python", "python3"):
            argv[0] = python_path
            proc = subprocess.run(
                argv,
                cwd=str(root),
                env=os.environ,
                capture_output=True,
                text=True,
            )
        else:
            # bash -c for tasks with bash-specific syntax (T1 uses `!`,
            # T2/T4 use `&&`, T5 uses `test -f`). Simple grep/test
            # commands work fine through bash -c on both platforms.
            proc = subprocess.run(
                ["bash", "-c", task.verify_cmd],
                cwd=str(root),
                env=os.environ,
                capture_output=True,
                text=True,
            )
        if proc.returncode == 0:
            print(f"  [PASS] {task.id:5} {task.title}")
        else:
            err = (proc.stderr or "").strip().splitlines()
            out = (proc.stdout or "").strip().splitlines()
            tail = (err[-1] if err else out[-1] if out else "")[:200]
            print(f"  [FAIL] {task.id:5} {task.title}  (exit={proc.returncode})")
            print(f"          cmd: {task.verify_cmd}")
            if tail:
                print(f"          msg: {tail}")
            failures.append((task.id, task.verify_cmd, proc.returncode, tail))

    print()
    if failures:
        print(f"[AUDIT-FAIL] {len(failures)} of {len(TASK_PLAN)} audit check(s) FAILED:", file=sys.stderr)
        for tid, cmd, rc, _ in failures:
            print(f"  - {tid} (exit={rc}): {cmd}", file=sys.stderr)
        return 1
    print(f"[AUDIT-PASS] all {len(TASK_PLAN)} audit check(s) passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
