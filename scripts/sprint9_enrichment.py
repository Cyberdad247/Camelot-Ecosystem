"""
SPRINT 9 — Cloud Brain Enrichment (Redis Live + 7/8 Green)
Protocol: URL source injection + UKG delta for S9 state
S9-01: Redis for Windows portable binary (tporadowski)
S9-02: redis-py pub/sub docs
S9-03: UKG_SPRINT9_DELTA_V707 delta note
"""
from __future__ import annotations
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

SOURCES: list[dict] = [
    {"url": "https://github.com/tporadowski/redis/releases/tag/v5.0.14.1",
     "tag": "S9-01-redis-windows-portable", "sprint": "S9-01"},
    {"url": "https://redis-py.readthedocs.io/en/stable/commands.html",
     "tag": "S9-02-redis-py-docs",          "sprint": "S9-02"},
]

_UKG_DELTA_S9 = """\
# UKG_SPRINT9_DELTA_V707
> TOON_v2 manual delta — Sprint 9 complete
> Generated: {ts}

## SPRINT 9 — REDIS LIVE + PIPELINE CONFIRMED [DEPLOYED 2026-05-18]
| Item | Detail |
|------|--------|
| Redis server | tporadowski/redis v5.0.14.1 portable binary → bin/redis/redis-server.exe :6379 |
| WSL fallback | WSL apt-get silently failed (no admin); switched to direct GitHub zip download |
| factory_status | 7/8 green: CLIProxy KineticEdge OmniVoice Redis Holotable KittenTTS SirOctavian UP; Saltare :8085 still dark |
| Voice pipeline | AudioSession→harness_queue→worker→Redis pub/sub→AudioSession confirmed end-to-end |
| Ledger | Entries 1671-1672 written, TOON_v2 Sync #5 complete (HWM→1672) |

## FULL AUDIO PIPELINE — CONFIRMED LIVE [S9]
VAD (OmniVoice :3002) → AudioSession.run_turn()
  → _enqueue_task() → harness_queue.jsonl
  → worker._dispatch() → LLM/shell → _write_response()
  → Redis PUBLISH camelot:resp:{{task_id}} (file fallback: logs/harness_responses/{{task_id}}.json)
  → AudioSession._redis_subscribe() via asyncio.to_thread
  → vad.synthesize_interruptible() → KittenTTS :8300
  → PCM audio chunks → speaker

## MEMORY STACK [S9]
- Short-term : integration_brain (ST tier, Modal)
- Long-term  : integration_brain (LT tier, SQLite :8200)
- Semantic   : RedisStore (camelot:mem:{{col}}:{{id}} hashes, Python cosine, _DarkStore fallback)
- Pub/Sub    : camelot:resp:{{task_id}} — zero-poll response channel
- Cloud Brain: NotebookLM (TOON_v2 auto-sync every 6h via harness Loop 8)

## NORTHSTAR STATUS [ALL CLOSED]
1. WebSocket edge      ✅ edge-router.ts :3001
2. mTLS/OIDC gate      ✅ bifrost.py Rule C
3. WebRTC VAD          ✅ omnivoice-router.ts :3002
4. Harness response    ✅ Redis pub/sub + file fallback
5. TOON_v2 cron        ✅ harness Loop 8 (6h interval)
"""


async def main() -> None:
    print("\n[S9] SPRINT 9 — CLOUD BRAIN ENRICHMENT")
    print("    Redis Live + 7/8 Green")
    print("=" * 60)

    ok, msg, ms = await _mod.async_health_probe()
    print(f"\n[PROBE] {msg}  ({ms:.0f}ms)")
    if not ok:
        print("[ABORT] Cloud Brain offline")
        sys.exit(1)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    print(f"\n[SOURCES] Injecting {len(SOURCES)} URLs")
    for i, src in enumerate(SOURCES):
        tag, url, sprint = src["tag"], src["url"], src["sprint"]
        print(f"  [{i+1}/{len(SOURCES)}] [{sprint}] {tag}")
        try:
            r = await _mod.async_sources_add(url=url, notebook_id=CANONICAL_ID, wait=False)
            sid = r.get("source_id") or "?"
            print(f"           OK  source_id={sid}")
        except Exception as e:
            print(f"           WARN  {str(e)[:120]}")
        await asyncio.sleep(1.5)

    print("\n[UKG] Injecting UKG_SPRINT9_DELTA_V707...")
    delta_content = _UKG_DELTA_S9.format(ts=ts)
    try:
        r = await _mod.async_sync_state(
            notebook_id=CANONICAL_ID,
            note_title="UKG_SPRINT9_DELTA_V707",
            content=delta_content,
        )
        print(f"  OK  {r['action']}  |  {r['content_chars']:,} chars  |  note_id={r['note_id']}")
    except Exception as e:
        print(f"  WARN  UKG delta failed: {e}")

    print("\n[S9] Done.")


if __name__ == "__main__":
    asyncio.run(main())
