"""
SPRINT 8 — Cloud Brain Enrichment (Full Pipeline Closure + Qdrant)
Protocol: URL source injection + UKG delta for S8 state

S8-01: Qdrant vector DB docs (qdrant_store.py semantic memory)
S8-02: sentence-transformers docs (embedding ref for qdrant_store)
S8-03: UKG_SPRINT8_DELTA_V706 delta note (S8 state)
"""
from __future__ import annotations

import asyncio
import importlib.util
import json
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

from control_plane.ledger_sync import append_provenance_entry  # noqa: E402

_BRIDGE = HOME / "03_VAULT" / "training" / "configs" / "notebooklm_bridge.py"
_spec = importlib.util.spec_from_file_location("notebooklm_bridge", _BRIDGE)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

CANONICAL_ID = _mod.CANONICAL_NOTEBOOK_ID

SOURCES: list[dict] = [
    # S8-01: Qdrant Python client docs
    {"url": "https://python-client.qdrant.tech/",
     "tag": "S8-01-qdrant-python-client",  "sprint": "S8-01"},
    # S8-02: sentence-transformers (embedding models for Qdrant vectors)
    {"url": "https://www.sbert.net/docs/sentence_transformer/usage/usage.html",
     "tag": "S8-02-sentence-transformers",  "sprint": "S8-02"},
]

_UKG_DELTA_S8 = """\
# UKG_SPRINT8_DELTA_V706
> TOON_v2 manual delta — Sprint 8 complete
> Generated: {ts}

## SPRINT 8 — FULL PIPELINE CLOSURE + QDRANT [DEPLOYED 2026-05-17]
| Item | File | Detail |
|------|------|--------|
| run_turn wired | 01_KERNEL/senses/audio/audio_session.py | run_turn() enqueues via _enqueue_task(), streams real harness response via _response_stream_from_harness() — end-to-end voice pipeline closed |
| Shell response | control_plane/worker.py | _dispatch() shell tier now calls _write_response() so //BOOT //SCAN //STATUS results reach AudioSession |
| QdrantStore | 01_KERNEL/memory/qdrant_store.py | QdrantStore + _DarkStore fallback; upsert/search/delete; cosine similarity; auto-collection create; module singleton |
| qdrant-client | .venv | pip install qdrant-client — qdrant_client.QdrantClient available |

## AUDIO PIPELINE — END-TO-END STATUS [S8 COMPLETE]
VAD (OmniVoice :3002) → AudioSession.run_turn()
  → _enqueue_task() → harness_queue.jsonl
  → worker._dispatch() → LLM/shell → _write_response()
  → _response_stream_from_harness() polls logs/harness_responses/{{id}}.json
  → vad.synthesize_interruptible() → KittenTTS :8300
  → PCM audio chunks → speaker

## MEMORY STACK
- Short-term : integration_brain (ST tier, Modal)
- Long-term  : integration_brain (LT tier, SQLite :8200)
- Semantic   : QdrantStore (:6333 live | _DarkStore fallback)
- Cloud Brain: NotebookLM (TOON_v2 auto-sync every 6h via harness)
"""


async def main() -> dict:
    print("\n[S8] SPRINT 8 — CLOUD BRAIN ENRICHMENT")
    print("    Full Pipeline Closure + Qdrant")
    print("=" * 60)

    ok, msg, ms = await _mod.async_health_probe()
    print(f"\n[PROBE] {msg}  ({ms:.0f}ms)")
    if not ok:
        print("[ABORT] Cloud Brain offline")
        sys.exit(1)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    results = {"ts": ts, "sources_added": [], "sources_failed": [], "ukgdelta": None}

    print(f"\n[SOURCES] Injecting {len(SOURCES)} URLs")
    for i, src in enumerate(SOURCES):
        tag, url, sprint = src["tag"], src["url"], src["sprint"]
        print(f"  [{i+1}/{len(SOURCES)}] [{sprint}] {tag}")
        try:
            r = await _mod.async_sources_add(url=url, notebook_id=CANONICAL_ID, wait=False)
            sid = r.get("source_id") or "?"
            print(f"           OK  source_id={sid}")
            results["sources_added"].append({"tag": tag, "url": url, "source_id": sid})
        except Exception as e:
            errmsg = str(e)[:120]
            print(f"           WARN  {errmsg}")
            results["sources_failed"].append({"tag": tag, "url": url, "error": errmsg})
        await asyncio.sleep(1.5)

    print("\n[UKG] Injecting UKG_SPRINT8_DELTA_V706...")
    delta_content = _UKG_DELTA_S8.format(ts=ts)
    try:
        r = await _mod.async_sync_state(
            notebook_id=CANONICAL_ID,
            note_title="UKG_SPRINT8_DELTA_V706",
            content=delta_content,
        )
        print(f"  OK  {r['action']}  |  {r['content_chars']:,} chars  |  note_id={r['note_id']}")
        results["ukgdelta"] = r
    except Exception as e:
        print(f"  WARN  UKG delta failed: {e}")
        results["ukgdelta"] = {"error": str(e)}

    added    = len(results["sources_added"])
    failed   = len(results["sources_failed"])
    delta_ok = results["ukgdelta"] and "error" not in results["ukgdelta"]

    print("\n" + "=" * 60)
    print(f"[S8] RESULT  sources={added}/{len(SOURCES)}  UKG={'OK' if delta_ok else 'FAIL'}")

    source_list = "; ".join(s["tag"] for s in results["sources_added"])
    ledger = append_provenance_entry(
        title="SPRINT 8 - FULL PIPELINE CLOSURE + QDRANT",
        actor="NORTHSTAR S8",
        scope=[
            f"S8-01/02: {added} URLs ({source_list[:120]})",
            f"S8-03: {'UKG_SPRINT8_DELTA_V706 created/updated' if delta_ok else 'FAILED'}",
        ],
        verification=[
            f"sources_added={added}",
            f"sources_failed={failed}",
            f"ukg_delta={'ok' if delta_ok else 'failed'}",
        ],
        tag="sprint8_enrichment",
    )
    print(f"[LEDGER] {ledger['status']} via append_provenance_entry")

    out_path = HOME / "logs" / "sprint8_enrichment_output.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
    print(f"[LOG]    {out_path}")

    return results


if __name__ == "__main__":
    asyncio.run(main())
