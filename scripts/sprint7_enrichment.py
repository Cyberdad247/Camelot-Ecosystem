"""
SPRINT 7 — Cloud Brain Enrichment (NORTHSTAR Close-Out)
Protocol: URL source injection + UKG delta for S6+S7 state

S7-01: asyncio subprocess docs (harness TOON_v2 cron loop)
S7-02: aiohttp web server ref (SirOctavian + KittenTTS serve pattern)
S7-03: UKG_SPRINT6_DELTA_V705 delta note (S6+S7 state)
"""
from __future__ import annotations  # noqa: E402

import asyncio  # noqa: E402
import importlib.util  # noqa: E402
import json
import os
import sys
from datetime import datetime, timezone  # noqa: E402
from pathlib import Path  # noqa: E402

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
    # S7-01: asyncio subprocess (harness _toon_v2_loop pattern)
    {"url": "https://docs.python.org/3/library/asyncio-subprocess.html",
     "tag": "S7-01-asyncio-subprocess",  "sprint": "S7-01"},
    # S7-02: aiohttp server reference (SirOctavian + KittenTTS)
    {"url": "https://docs.aiohttp.org/en/stable/web.html",
     "tag": "S7-02-aiohttp-web-server",  "sprint": "S7-02"},
]

_UKG_DELTA_S6S7 = """\
# UKG_SPRINT6_DELTA_V705
> TOON_v2 manual delta — Sprint 6 + Sprint 7 complete
> Generated: {ts}

## SPRINT 6 — NORTHSTAR PHASE 4 [DEPLOYED 2026-05-17]
| Item | File | Detail |
|------|------|--------|
| Response Channel | control_plane/worker.py | QueueTask.source field + _write_response() + RESPONSES_DIR → logs/harness_responses/{{id}}.json |
| Silero VAD | 01_KERNEL/senses/audio/silero_vad.py | SileroVadDetector torch.hub snakers4/silero-vad + energy RMS fallback, singleton |
| Boot Probes | control_plane/harness.py | BOOT_PROBES extended 5→8 (+OmniVoice:3002, +KittenTTS:8300, +SirOctavian:8400) |
| Factory Status | bin/factory_status.py | One-shot CLI dashboard: 8 service probes + queue + ledger + octavian metrics |

## SPRINT 7 — NORTHSTAR CLOSE-OUT [DEPLOYED 2026-05-17]
| Item | File | Detail |
|------|------|--------|
| Response Fix | 01_KERNEL/senses/audio/audio_session.py | _response_stream_from_harness polls .json (was .txt), parses text field |
| Watchdog Restart | control_plane/harness.py | _watchdog_loop auto-restarts OmniVoice/KittenTTS/SirOctavian on DARK (120s cooldown) |
| TOON_v2 Cron | control_plane/harness.py | _toon_v2_loop() Loop 8 — delta sync every 6h via asyncio subprocess |
| Cloud Brain S7 | scripts/sprint7_enrichment.py | 2 URL sources + UKG_SPRINT6_DELTA_V705 |

## NORTHSTAR BLOCKERS — FINAL STATUS
1. [DONE] WebSocket edge routing — edge-router.ts :3001 ✅
2. [DONE] mTLS/OIDC mobile gateway — Bifrost Rule C ✅
3. [DONE] WebRTC full-duplex audio — energy VAD ✅ + Silero VAD wrapper ✅
4. [DONE] Harness response stream — worker._write_response() + AudioSession polling ✅
5. [DONE] TOON_v2 delta automation — toon_v2_delta.py ✅ + harness cron loop ✅

## FACTORY STATUS (6/8 green at close-out)
- CLIProxy :8080 ✅ | KineticEdge :3001 ✅ | OmniVoice :3002 ✅
- KittenTTS :8300 ✅ | SirOctavian :8400 ✅ | Holotable :3000 ✅
- Qdrant :6333 ⬛ (requires separate install)
- Saltare :8085 ⬛ (not yet deployed)
"""


async def main() -> dict:
    print("\n[S7] SPRINT 7 — CLOUD BRAIN ENRICHMENT")
    print("    NORTHSTAR Close-Out sources + UKG delta")
    print("=" * 60)

    ok, msg, ms = await _mod.async_health_probe()
    print(f"\n[PROBE] {msg}  ({ms:.0f}ms)")
    if not ok:
        print("[ABORT] Cloud Brain offline")
        sys.exit(1)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    results = {"ts": ts, "sources_added": [], "sources_failed": [], "ukgdelta": None}

    # ── URL sources ───────────────────────────────────────────────────────────
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

    # ── UKG delta S6+S7 ──────────────────────────────────────────────────────
    print("\n[UKG] Injecting UKG_SPRINT6_DELTA_V705...")
    delta_content = _UKG_DELTA_S6S7.format(ts=ts)
    try:
        r = await _mod.async_sync_state(
            notebook_id=CANONICAL_ID,
            note_title="UKG_SPRINT6_DELTA_V705",
            content=delta_content,
        )
        print(f"  OK  {r['action']}  |  {r['content_chars']:,} chars  |  note_id={r['note_id']}")
        results["ukgdelta"] = r
    except Exception as e:
        print(f"  WARN  UKG delta failed: {e}")
        results["ukgdelta"] = {"error": str(e)}

    # ── Summary + Ledger ──────────────────────────────────────────────────────
    added    = len(results["sources_added"])
    failed   = len(results["sources_failed"])
    delta_ok = results["ukgdelta"] and "error" not in results["ukgdelta"]

    print("\n" + "=" * 60)
    print(f"[S7] RESULT  sources={added}/{len(SOURCES)}  UKG={'OK' if delta_ok else 'FAIL'}")
    if failed:
        for f in results["sources_failed"]:
            print(f"  WARN  {f['tag']}: {f['error'][:80]}")

    source_list = "; ".join(s["tag"] for s in results["sources_added"])
    ledger = append_provenance_entry(
        title="SPRINT 7 - NORTHSTAR CLOSE-OUT",
        actor="NORTHSTAR S7",
        scope=[
            f"S7-01/02: {added} URLs ({source_list[:120]})",
            f"S7-03: {'UKG_SPRINT6_DELTA_V705 created/updated' if delta_ok else 'FAILED'}",
        ],
        verification=[
            f"sources_added={added}",
            f"sources_failed={failed}",
            f"ukg_delta={'ok' if delta_ok else 'failed'}",
        ],
        tag="sprint7_enrichment",
    )
    print(f"[LEDGER] {ledger['status']} via append_provenance_entry")

    out_path = HOME / "logs" / "sprint7_enrichment_output.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
    print(f"[LOG]    {out_path}")

    return results


if __name__ == "__main__":
    asyncio.run(main())
