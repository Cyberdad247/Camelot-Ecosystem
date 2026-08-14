#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""PostToolUse hook — writes AUTO entries to PROVENANCE_LEDGER.md."""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HOME = Path(os.environ.get("CAMELOT_OS_HOME", Path.home() / "CAMELOT_OS"))
LEDGER = HOME / "PROVENANCE_LEDGER.md"


def _maybe_sync_to_brain(file_path: str) -> None:
    """Fire-and-forget: sync a skill/agent file to NotebookLM when it changes."""
    if not file_path:
        return
    p = Path(file_path)
    parts = p.parts
    if ".claude" not in parts:
        return
    idx = parts.index(".claude")
    if len(parts) <= idx + 1 or parts[idx + 1] not in ("skills", "agents"):
        return
    sync = HOME / "scripts" / "sync_claude_skills.py"
    if not sync.exists():
        return
    subprocess.Popen(
        [sys.executable, str(sync), "--file", file_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
    )


def next_id(ledger_text: str) -> int:
    ids = re.findall(r"^\|\s*(\d+)\s*\|", ledger_text, re.MULTILINE)
    return max((int(i) for i in ids), default=1000) + 1


def main() -> None:
    try:
        raw = sys.stdin.read()
        event = json.loads(raw) if raw.strip() else {}
    except Exception:
        sys.exit(0)

    tool = event.get("tool_name", event.get("tool", "Unknown"))
    inp = event.get("tool_input", {})
    raw_path = inp.get("file_path") or inp.get("command") or "—"
    path = raw_path
    if isinstance(path, str) and len(path) > 80:
        path = "..." + path[-77:]

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    if LEDGER.exists():
        text = LEDGER.read_text(encoding="utf-8", errors="replace")
    else:
        text = "| ID | Task | Author | Status | Notes |\n|:--|:--|:--|:--|:--|\n"

    nid = next_id(text)
    row = f"| {nid} | **[AUTO] {tool}: `{path}`** | SIR_BORIS | ✅ AUTO | Claude Code hook — {ts} |\n"

    lines = text.splitlines(keepends=True)
    # Insert before first data row (starts with | digit)
    insert_at = next(
        (i for i, ln in enumerate(lines) if re.match(r"^\|\s*\d", ln)),
        len(lines),
    )
    lines.insert(insert_at, row)

    try:
        LEDGER.write_text("".join(lines), encoding="utf-8")
    except Exception:
        pass

    _maybe_sync_to_brain(raw_path if isinstance(raw_path, str) else "")


if __name__ == "__main__":
    main()
