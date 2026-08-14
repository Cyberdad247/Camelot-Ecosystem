# SPDX-License-Identifier: MIT

"""Starship custom module for Camelot cockpit state."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _ensure_repo_on_path() -> None:
    repo = Path(__file__).resolve().parent.parent
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))


def build_segment() -> str:
    _ensure_repo_on_path()
    from control_plane.cockpit import prompt_payload

    payload = prompt_payload(spawn_refresh=False)
    state = "STALE" if payload.get("stale") else payload.get("services", {}).get("state", "WARN")
    queue = payload.get("queue", {}).get("pending", "?")
    mode = payload.get("mode") or "off"
    last = payload.get("last_command", {}) or {}
    knight = last.get("knight") or "idle"
    return f"Camelot:{state} q:{queue} {knight} mode:{mode}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--available", action="store_true", help="Return 0 when Camelot state can be read")
    args = parser.parse_args(argv)
    try:
        segment = build_segment()
    except Exception:
        return 1
    if not args.available:
        print(segment)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())