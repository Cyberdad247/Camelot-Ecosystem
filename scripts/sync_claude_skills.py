#!/usr/bin/env python3
"""
Sync Claude Code skills and harnesses to the CAMELOT-OS Cloud Brain (NotebookLM).

Each .claude/skills/*.md  → text source titled "[CC-SKILL] <stem>"
Each .claude/agents/*.md  → text source titled "[CC-AGENT] <stem>"

Upsert = delete existing source with matching title, then add fresh content.
The NotebookLM API has no update endpoint, so delete+add is the only path.

Usage:
  python scripts/sync_claude_skills.py               # full sync (all 15 files)
  python scripts/sync_claude_skills.py --file path   # single file
  python scripts/sync_claude_skills.py --dry-run     # list only, no mutations
"""
from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

HOME = Path(os.environ.get("CAMELOT_OS_HOME", Path.home() / "CAMELOT_OS")).resolve()

# Load bridge
_BRIDGE = HOME / "03_VAULT" / "training" / "configs" / "notebooklm_bridge.py"
_spec = importlib.util.spec_from_file_location("notebooklm_bridge", _BRIDGE)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

CANONICAL_ID = _mod.CANONICAL_NOTEBOOK_ID
LOG_PATH = HOME / "logs" / "brain_sync_output.md"

_RATE_LIMIT_S = 1.5  # polite delay between API calls


def _collect_files(single: str | None) -> list[tuple[Path, str]]:
    """Return list of (path, title) for all skills + agents (or just one file)."""
    if single:
        p = Path(single)
        if not p.is_absolute():
            p = HOME / p
        folder = p.parent.name  # "skills" or "agents"
        prefix = "[CC-SKILL]" if folder == "skills" else "[CC-AGENT]"
        return [(p, f"{prefix} {p.stem}")]

    files: list[tuple[Path, str]] = []
    for md in sorted((HOME / ".claude" / "skills").glob("*.md")):
        files.append((md, f"[CC-SKILL] {md.stem}"))
    for md in sorted((HOME / ".claude" / "agents").glob("*.md")):
        files.append((md, f"[CC-AGENT] {md.stem}"))
    return files


async def _run(files: list[tuple[Path, str]], dry_run: bool) -> list[dict]:
    results = []

    # Build title → source_id map from existing notebook sources
    print("[SYNC] Fetching existing sources from Cloud Brain...")
    try:
        listing = await _mod.async_sources_list(CANONICAL_ID)
        sources = listing.get("sources", [])
        existing: dict[str, str] = {
            s.get("title", ""): s.get("source_id", "") or s.get("id", "")
            for s in sources
            if s.get("title", "").startswith(("[CC-SKILL]", "[CC-AGENT]"))
        }
        print(f"  Found {len(existing)} existing CC-* sources in notebook.")
    except Exception as e:
        print(f"  [WARN] Could not list existing sources: {e}")
        existing = {}

    for path, title in files:
        entry: dict = {"title": title, "file": str(path)}
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except FileNotFoundError:
            print(f"[SKIP]  {title} — file not found: {path}")
            entry["status"] = "not_found"
            results.append(entry)
            continue

        old_id = existing.get(title)
        print(f"[UPSERT] {title}")
        print(f"         file={path.name}  chars={len(content):,}  old_id={old_id or 'none'}")

        if dry_run:
            entry["status"] = "dry_run"
            results.append(entry)
            continue

        # Delete old source if it exists
        if old_id:
            try:
                await _mod.async_sources_delete(old_id, notebook_id=CANONICAL_ID)
                print(f"         deleted old source_id={old_id}")
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"         [WARN] delete failed: {e}")

        # Add fresh content
        try:
            r = await _mod.async_sources_add(
                text=content,
                title=title,
                notebook_id=CANONICAL_ID,
                wait=False,
            )
            new_id = r.get("source_id", "?")
            print(f"         added  source_id={new_id}  ✅")
            entry.update({"status": "ok", "source_id": new_id})
        except Exception as e:
            print(f"         [ERROR] add failed: {e}")
            entry.update({"status": "error", "error": str(e)})

        results.append(entry)
        await asyncio.sleep(_RATE_LIMIT_S)

    return results


async def main(single: str | None, dry_run: bool) -> None:
    t0 = time.monotonic()
    files = _collect_files(single)
    if not files:
        print("[SYNC] No files found.")
        return

    mode = "DRY RUN" if dry_run else f"syncing {len(files)} file(s)"
    print(f"\n[SYNC] CLOUD BRAIN ← Claude Code skills/harnesses  ({mode})")
    print("=" * 60)

    results = await _run(files, dry_run)

    ok      = sum(1 for r in results if r.get("status") == "ok")
    skipped = sum(1 for r in results if r.get("status") in ("not_found", "dry_run"))
    errors  = sum(1 for r in results if r.get("status") == "error")
    elapsed = time.monotonic() - t0

    print("\n" + "=" * 60)
    print(f"[SYNC] Done — {ok} upserted, {skipped} skipped, {errors} errors  ({elapsed:.1f}s)")

    # Write log
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
    print(f"[LOG]  {LOG_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync Claude Code skills/agents to Cloud Brain")
    parser.add_argument("--file", help="Sync a single file instead of all")
    parser.add_argument("--dry-run", action="store_true", help="List only, no API mutations")
    args = parser.parse_args()
    asyncio.run(main(args.file, args.dry_run))
