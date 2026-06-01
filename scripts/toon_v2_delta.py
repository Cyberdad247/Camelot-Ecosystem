"""
[S4-02] TOON_v2 Automated Delta Sync
=====================================
Automates the manual UKG delta injection from Sprint 2.

Protocol:
  1. Read PROVENANCE_LEDGER.md — extract all entries since last sync
  2. Read logs/toon_v2_state.json — last synced ledger max_id
  3. Compute delta entries (new rows since last sync)
  4. Format as compressed UKG delta node (TOON_v2 format)
  5. Inject into Cloud Brain via async_sync_state()
  6. Update toon_v2_state.json with new high-water mark

Run on demand or schedule with colony.py cron:
    python scripts/toon_v2_delta.py
    python scripts/toon_v2_delta.py --dry-run
    python scripts/toon_v2_delta.py --note-title UKG_SPRINT3_DELTA_V703
"""
from __future__ import annotations

import argparse
import asyncio
import importlib.util
import json
import os
import re
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

CANONICAL_ID  = _mod.CANONICAL_NOTEBOOK_ID
LEDGER_PATH   = HOME / "PROVENANCE_LEDGER.md"
STATE_PATH    = HOME / "logs" / "toon_v2_state.json"


# ── State management ──────────────────────────────────────────────────────────

def _load_state() -> dict:
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"last_synced_max_id": 0, "sync_count": 0, "last_sync_ts": None}


def _save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


# ── Ledger parsing ────────────────────────────────────────────────────────────

def _parse_ledger_rows(text: str) -> list[dict]:
    """Parse PROVENANCE_LEDGER.md table rows into structured dicts."""
    rows: list[dict] = []
    for line in text.splitlines():
        m = re.match(r"^\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|", line)
        if m:
            rows.append({
                "id": int(m.group(1)),
                "title": m.group(2).strip(),
                "author": m.group(3).strip(),
                "status": m.group(4).strip(),
                "notes": m.group(5).strip(),
            })
    return rows


def _delta_rows(rows: list[dict], since_id: int) -> list[dict]:
    return [r for r in rows if r["id"] > since_id]


# ── Delta template ────────────────────────────────────────────────────────────

def _build_delta_note(delta: list[dict], ts: str, note_title: str, since_id: int) -> str:
    sprint_summary = "\n".join(
        f"| {r['id']} | {r['title'][:60]} | {r['status']} |"
        for r in sorted(delta, key=lambda r: r["id"])
    )
    return f"""\
# {note_title}
> TOON_v2 automated delta — entries {since_id + 1}+ since last sync
> Generated: {ts}
> Sync engine: scripts/toon_v2_delta.py

## DELTA ENTRIES ({len(delta)} new)
| ID | Title | Status |
|----|-------|--------|
{sprint_summary}

## FACTORY STATE (at sync time)
- Ledger max ID: {max((r['id'] for r in delta), default=since_id)}
- Delta entry count: {len(delta)}
- NORTHSTAR blockers: see UKG_SPRINT1_DELTA_V702 (unchanged)
"""


# ── Main ──────────────────────────────────────────────────────────────────────

async def main(dry_run: bool = False, note_title: str | None = None) -> dict:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"\n[TOON_V2] Delta Sync — {ts}")
    print("=" * 60)

    # Health check
    ok, msg, ms = await _mod.async_health_probe()
    print(f"[PROBE]  {msg}  ({ms:.0f}ms)")
    if not ok:
        print("[ABORT] Cloud Brain offline")
        sys.exit(1)

    # Read ledger
    if not LEDGER_PATH.exists():
        print("[ABORT] PROVENANCE_LEDGER.md not found")
        sys.exit(1)
    ledger_text = LEDGER_PATH.read_text(encoding="utf-8")
    rows = _parse_ledger_rows(ledger_text)
    print(f"[LEDGER] {len(rows)} rows parsed")

    # Compute delta
    state = _load_state()
    since_id = state["last_synced_max_id"]
    delta = _delta_rows(rows, since_id)
    print(f"[DELTA]  {len(delta)} new entries since ID {since_id}")

    if not delta:
        print("[TOON_V2] No new entries — Cloud Brain already up to date")
        return {"status": "noop", "ts": ts}

    # Auto-generate note title if not provided
    sync_n = state["sync_count"] + 1
    if not note_title:
        note_title = f"UKG_DELTA_V{700 + sync_n:03d}_AUTO"

    # Build delta content
    content = _build_delta_note(delta, ts, note_title, since_id)
    print(f"[NOTE]   {note_title}  ({len(content):,} chars)")

    if dry_run:
        print("\n[DRY-RUN] Would inject:")
        print(content[:600] + ("..." if len(content) > 600 else ""))
        return {"status": "dry_run", "delta_count": len(delta), "note_title": note_title}

    # Inject into Cloud Brain
    print(f"[SYNC]   Injecting into Cloud Brain notebook {CANONICAL_ID[:8]}...")
    try:
        r = await _mod.async_sync_state(
            notebook_id=CANONICAL_ID,
            note_title=note_title,
            content=content,
        )
        action = r.get("action", "?")
        note_id = r.get("note_id", "?")
        print(f"  ✅  {action}  |  note_id={note_id}  |  {r.get('content_chars', 0):,} chars")
    except Exception as e:
        print(f"  ❌  Sync failed: {e}")
        return {"status": "error", "error": str(e)}

    # Update state
    new_max_id = max((r2["id"] for r2 in rows), default=since_id)
    state["last_synced_max_id"] = new_max_id
    state["sync_count"] = sync_n
    state["last_sync_ts"] = ts
    _save_state(state)
    print(f"[STATE]  Updated high-water mark → {new_max_id}")
    print(f"[TOON_V2] Sync #{sync_n} complete — {len(delta)} entries synced")

    return {
        "status": "ok",
        "ts": ts,
        "delta_count": len(delta),
        "note_title": note_title,
        "note_id": r.get("note_id"),
        "new_max_id": new_max_id,
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(prog="toon_v2_delta", description="TOON_v2 Automated Delta Sync")
    ap.add_argument("--dry-run",    action="store_true", help="Preview delta without syncing")
    ap.add_argument("--note-title", default=None,        metavar="TITLE",
                    help="Override auto-generated note title")
    args = ap.parse_args()
    asyncio.run(main(dry_run=args.dry_run, note_title=args.note_title))
