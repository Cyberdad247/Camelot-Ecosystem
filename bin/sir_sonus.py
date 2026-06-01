"""
SIR_SONUS — Morning Briefing Generator
Queries Cloud Brain for northstar state, generates audio briefing via NotebookLM Studio.

Usage:
    python bin/sir_sonus.py                  # default briefing
    python bin/sir_sonus.py --poll           # wait for audio completion
    python bin/sir_sonus.py --query "..."    # custom synthesis query
    python bin/sir_sonus.py --text-only      # synthesis text only, skip audio
"""
from __future__ import annotations

import argparse
import asyncio
import importlib.util
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

HOME = Path(os.environ.get("CAMELOT_OS_HOME", Path.home() / "CAMELOT_OS")).resolve()
sys.path.insert(0, str(HOME))

_BRIDGE = HOME / "03_VAULT" / "training" / "configs" / "notebooklm_bridge.py"
_spec = importlib.util.spec_from_file_location("notebooklm_bridge", _BRIDGE)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

CANONICAL_ID = _mod.CANONICAL_NOTEBOOK_ID

DEFAULT_QUERY = (
    "Provide a morning operational briefing for the CAMELOT-OS digital factory. "
    "Cover: (1) NORTHSTAR blocker status — WebRTC, WebSocket edge, mTLS gateway, "
    "knight hot-swap, TOON_v2; (2) current sprint status; "
    "(3) top 3 priorities for today. Technical tone."
)

DEFAULT_INSTRUCTIONS = (
    "Generate a morning briefing in the style of a technical project lead. "
    "Cover northstar blockers, sprint status, and today's top 3 priorities. "
    "Be direct. No filler. Target 2-3 minutes."
)

BRIEFING_DIR = HOME / "logs" / "morning_briefings"


async def run(
    query: str,
    instructions: str,
    poll: bool,
    text_only: bool,
    output_dir: Path,
) -> None:
    dt = datetime.now()
    print(f"[SONUS] Morning briefing — {dt.strftime('%Y-%m-%d %H:%M')}")

    # Health check
    ok, msg, ms = await _mod.async_health_probe()
    print(f"[SONUS] {msg}  ({ms:.0f}ms)")
    if not ok:
        print("[SONUS] ABORT — Cloud Brain offline")
        sys.exit(1)

    # Synthesize northstar state from Cloud Brain
    print("[SONUS] Querying northstar state...")
    t0 = datetime.now()
    synthesis = await _mod.async_synthesize(query, CANONICAL_ID, use_cache=False)
    elapsed = (datetime.now() - t0).total_seconds()
    char_count = len(synthesis or "")
    print(f"[SONUS] Synthesis: {char_count:,} chars ({elapsed:.1f}s)")

    if synthesis:
        output_dir.mkdir(parents=True, exist_ok=True)
        ts = dt.strftime("%Y%m%dT%H%M%S")
        brief_path = output_dir / f"brief_{ts}.md"
        header = (
            f"# CAMELOT-OS Morning Briefing\n"
            f"_Generated: {dt.strftime('%Y-%m-%d %H:%M:%S')}_\n\n"
        )
        brief_path.write_text(header + synthesis, encoding="utf-8")
        print(f"[SONUS] Text saved -> {brief_path.relative_to(HOME)}")
        print()
        print("─" * 60)
        print(synthesis[:800] + ("..." if char_count > 800 else ""))
        print("─" * 60)

    if text_only:
        print("[SONUS] --text-only mode — skipping audio generation")
        return

    # Trigger NotebookLM Studio audio
    print("\n[SONUS] Triggering Studio audio generation...")
    try:
        r = await _mod.async_studio_generate(
            "audio",
            notebook_id=CANONICAL_ID,
            instructions=instructions,
        )
        task_id = r.get("task_id") or "?"
        print(f"[SONUS] Audio task started — task_id={task_id}")
    except Exception as e:
        print(f"[SONUS] Audio generation failed: {e}")
        return

    if not poll:
        print("[SONUS] Audio generating in background. Check NotebookLM Studio to download.")
        return

    # Poll until complete
    print("[SONUS] Polling for completion (max 3 min)...")
    for attempt in range(36):
        await asyncio.sleep(5)
        try:
            status = await _mod.async_studio_list("audio", notebook_id=CANONICAL_ID)
            items = status.get("items", [])
            ready = [x for x in items if x.get("state") in ("complete", "ready", "done")]
            if ready:
                print(f"[SONUS] Audio ready — {len(ready)} artifact(s) available in NotebookLM")
                for item in ready[:3]:
                    print(f"  • {item.get('title', '?')} [{item.get('state')}]")
                break
            print(f"[SONUS]   ... generating ({attempt+1}/36, {(attempt+1)*5}s)")
        except Exception as e:
            print(f"[SONUS]   poll error: {e}")
    else:
        print("[SONUS] Still generating after 3 min — check NotebookLM Studio manually")


def main() -> None:
    ap = argparse.ArgumentParser(
        prog="sir_sonus",
        description="CAMELOT-OS Morning Briefing Generator",
    )
    ap.add_argument("--query",        default=DEFAULT_QUERY,        metavar="Q",
                    help="Cloud Brain synthesis query")
    ap.add_argument("--instructions", default=DEFAULT_INSTRUCTIONS, metavar="I",
                    help="NotebookLM Studio audio generation instructions")
    ap.add_argument("--poll",         action="store_true",
                    help="Poll until audio generation completes")
    ap.add_argument("--text-only",    action="store_true",
                    help="Synthesis text only — skip audio generation")
    ap.add_argument("--output-dir",   default=str(BRIEFING_DIR),    metavar="DIR",
                    help="Directory for briefing text files")
    args = ap.parse_args()

    asyncio.run(run(
        query=args.query,
        instructions=args.instructions,
        poll=args.poll,
        text_only=args.text_only,
        output_dir=Path(args.output_dir),
    ))


if __name__ == "__main__":
    main()
