#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""CAMELOT-OS bridge for the oh-my-codex (OmX) CLI.

This bridge keeps Camelot's root AGENTS.md and control plane authoritative.
It intentionally does not run `omx setup`, install hooks, or rewrite guidance.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _omx_command() -> str:
    command = shutil.which("omx")
    if command is None:
        raise RuntimeError(
            "omx is not on PATH; install the official package with "
            "`npm install -g oh-my-codex`"
        )
    return command


def _env() -> dict[str, str]:
    env = os.environ.copy()
    env["CAMELOT_OS_HOME"] = str(ROOT)
    env["OMX_REPO_ROOT"] = str(ROOT)
    env["OMX_MODEL_INSTRUCTIONS_FILE"] = str(ROOT / "AGENTS.md")
    env.setdefault("OMX_BYPASS_DEFAULT_SYSTEM_PROMPT", "0")
    return env


def _run(command: list[str], *, cwd: Path = ROOT) -> int:
    completed = subprocess.run(command, cwd=cwd, env=_env(), check=False)
    return completed.returncode


def _python(*parts: str) -> list[str]:
    return [sys.executable, *parts]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python scripts/omx-camelot.py",
        description="Run oh-my-codex with Camelot-OS governance and routing.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor", help="Check the installed OmX runtime")
    sub.add_parser("status", help="Run the Camelot status probe as JSON")

    boot = sub.add_parser("boot", help="Run Camelot's quick activation sequence")
    boot.add_argument("--full", action="store_true", help="Run the full boot sequence")

    route = sub.add_parser("route", help="Route a Camelot rune through the live router")
    route.add_argument("--rune", required=True, help="Rune such as FORGE or //STATUS")
    route.add_argument("--task", default="", help="Task passed to the rune handler")

    scan = sub.add_parser("scan", help="Run a read-only Camelot squire scan command")
    scan.add_argument("path", nargs="?", default=".", help="Path to inspect")
    scan.add_argument("--ghost", action="store_true", help="Run the local privacy scanner")

    launch = sub.add_parser("launch", help="Launch OmX with Camelot instructions")
    launch.add_argument("args", nargs=argparse.REMAINDER, help="Arguments forwarded to omx")

    execute = sub.add_parser("exec", help="Run an OmX non-interactive execution")
    execute.add_argument("args", nargs=argparse.REMAINDER, help="Arguments forwarded after `omx exec`")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.command == "doctor":
        return _run([_omx_command(), "doctor"])

    if args.command == "status":
        return _run(_python("scripts/camelot-status.py", "--json"))

    if args.command == "boot":
        command = _python("bin/awaken.py")
        if not args.full:
            command.append("--quick")
        return _run(command)

    if args.command == "route":
        return _run(
            _python(
                "-m",
                "control_plane.runic_router",
                "--rune",
                args.rune,
                "--task",
                args.task,
            )
        )

    if args.command == "scan":
        if args.ghost:
            return _run(_python("-m", "squires.colony", "ghost", args.path))
        return _run(_python("-m", "squires.colony", "scan", args.path))

    if args.command == "launch":
        return _run([_omx_command(), *args.args])

    if args.command == "exec":
        return _run([_omx_command(), "exec", *args.args])

    raise AssertionError(f"Unhandled bridge command: {args.command}")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"omx-camelot: {exc}", file=sys.stderr)
        raise SystemExit(127)
