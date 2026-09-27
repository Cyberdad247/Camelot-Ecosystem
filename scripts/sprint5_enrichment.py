"""
SPRINT 5 — Cloud Brain Enrichment (NORTHSTAR Phase 3 sources)
Protocol: URL source injection for Sprint 3+4 technical references

S5-01: aiohttp streaming + asyncio generators (kitten TTS HTTP server)
S5-02: WebRTC samples + VAD research (omnivoice-router / VAD interrupt)
S5-03: OIDC Core spec + PyJWT (Bifrost Rule C mobile gateway)
S5-04: Silero VAD model (energy VAD + Silero integration reference)
S5-05: UKG_SPRINT3_DELTA_V704 delta note (S3+S4 state)
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
    # S5-01: aiohttp streaming docs
    {"url": "https://docs.aiohttp.org/en/stable/web_advanced.html",
     "tag": "S5-01-aiohttp-streaming",   "sprint": "S5-01"},
    # S5-02: WebRTC samples (VAD / audio pipeline reference)
    {"url": "https://webrtc.github.io/samples/",
     "tag": "S5-02-WebRTC-samples",      "sprint": "S5-02"},
    # S5-03: OIDC Core 1.0 spec (Bifrost Rule C JWT)
    {"url": "https://openid.net/specs/openid-connect-core-1_0.html",
     "tag": "S5-03-OIDC-core-spec",      "sprint": "S5-03"},
    # S5-03b: PyJWT docs (signature verification reference)
    {"url": "https://pyjwt.readthedocs.io/en/stable/",
     "tag": "S5-03-PyJWT-docs",          "sprint": "S5-03"},
    # S5-04: Silero VAD model (energy VAD + ML VAD reference)
    {"url": "https://github.com/snakers4/silero-vad",
     "tag": "S5-04-SileroVAD",           "sprint": "S5-04"},
]

_UKG_DELTA_S3S4 = """\
# UKG_SPRINT3_DELTA_V704
> TOON_v2 manual delta — Sprint 3 + Sprint 4 complete
> Generated: {ts}

## SPRINT 3 — NORTHSTAR PHASE 1 [DEPLOYED 2026-05-17]
| Item | File | Detail |
|------|------|--------|
| Edge Router | 02_FORGE/KINETIC_ARMORY/edge-router/edge-router.ts | WebSocket :3001, bifrost token auth, harness_queue enqueue |
| Chunked TTS | 01_KERNEL/senses/audio/kitten_service.py | synthesize_chunked_async(), Kokoro TTS, HTTP stream :8300 |
| OmniVoice | 02_FORGE/KINETIC_ARMORY/omnivoice-router/omnivoice-router.ts | WebRTC signaling :3002, energy VAD (RMS 0.01, 200ms/800ms) |
| Bifrost Rule C | bin/bifrost.py | OIDC mobile gate, verify_oidc_token, MOBILE_TRUSTED_ISSUERS |

## SPRINT 4 — NORTHSTAR PHASE 2 [DEPLOYED 2026-05-17]
| Item | File | Detail |
|------|------|--------|
| Intent Router | control_plane/intent_router.py | classify_intent + route_by_intent, 8 categories, 0-LLM heuristic |
| TOON_v2 Auto | scripts/toon_v2_delta.py | Automated ledger diff + UKG injection + HWM state tracking |
| VAD Interrupt | 01_KERNEL/senses/audio/vad_interrupt.py | VadInterruptController asyncio.Event, interruptible TTS abort |
| Sir Octavian | control_plane/sir_octavian.py | Factory metrics: queue/terminals/ledger, HTTP :8400, metrics.json |

## SPRINT 5 — NORTHSTAR PHASE 3 [IN PROGRESS]
| Item | File | Detail |
|------|------|--------|
| sir_sonus | control_plane/switchboard.py | Registered kitten_tts terminal probe_port=8300 |
| Boot phases | control_plane/boot_sequence.py | OmniVoice :3002, Kitten TTS :8300, Sir Octavian :8400 |
| AudioSession | 01_KERNEL/senses/audio/audio_session.py | Full-duplex orchestrator: VAD→intent→knight→TTS |
| Cloud Brain | scripts/sprint5_enrichment.py | 5 new URL sources + this UKG delta |

## NORTHSTAR BLOCKERS STATUS
1. [DONE] WebSocket edge routing — edge-router.ts :3001 ✅
2. [DONE] mTLS/OIDC mobile gateway — Bifrost Rule C ✅
3. [PARTIAL] WebRTC full-duplex audio — energy VAD ✅; Silero VAD integration pending
4. [PARTIAL] Dynamic knight hot-swap — intent_router ✅; harness response stream TODO
5. [PARTIAL] TOON_v2 delta automation — toon_v2_delta.py ✅; cron scheduling pending
"""


async def main() -> dict:
    print("\n[S5] SPRINT 5 — CLOUD BRAIN ENRICHMENT")
    print("    NORTHSTAR Phase 3 sources + UKG delta")
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
            print(f"           ✅  source_id={sid}")
            results["sources_added"].append({"tag": tag, "url": url, "source_id": sid})
        except Exception as e:
            errmsg = str(e)[:120]
            print(f"           ⚠️   {errmsg}")
            results["sources_failed"].append({"tag": tag, "url": url, "error": errmsg})
        await asyncio.sleep(1.5)

    # ── UKG delta S3+S4 ───────────────────────────────────────────────────────
    print("\n[UKG] Injecting UKG_SPRINT3_DELTA_V704...")
    delta_content = _UKG_DELTA_S3S4.format(ts=ts)
    try:
        r = await _mod.async_sync_state(
            notebook_id=CANONICAL_ID,
            note_title="UKG_SPRINT3_DELTA_V704",
            content=delta_content,
        )
        print(f"  ✅  {r['action']}  |  {r['content_chars']:,} chars  |  note_id={r['note_id']}")
        results["ukgdelta"] = r
    except Exception as e:
        print(f"  ⚠️   UKG delta failed: {e}")
        results["ukgdelta"] = {"error": str(e)}

    # ── Summary + Ledger ──────────────────────────────────────────────────────
    added    = len(results["sources_added"])
    failed   = len(results["sources_failed"])
    delta_ok = results["ukgdelta"] and "error" not in results["ukgdelta"]

    print("\n" + "=" * 60)
    print(f"[S5] RESULT  sources={added}/{len(SOURCES)}  UKG={'✅' if delta_ok else '❌'}")
    if failed:
        for f in results["sources_failed"]:
            print(f"  ⚠️  {f['tag']}: {f['error'][:80]}")

    source_list = "; ".join(s["tag"] for s in results["sources_added"])
    ledger = append_provenance_entry(
        title="SPRINT 5 - CLOUD BRAIN ENRICHMENT",
        actor="NORTHSTAR Phase 3",
        scope=[
            f"S5-01/02/03/04: {added} URLs injected ({source_list[:120]})",
            f"S5-05: {'UKG_SPRINT3_DELTA_V704 created/updated' if delta_ok else 'FAILED'}",
        ],
        verification=[
            f"sources_added={added}",
            f"sources_failed={failed}",
            f"ukg_delta={'ok' if delta_ok else 'failed'}",
        ],
        tag="sprint5_enrichment",
    )
    print(f"[LEDGER] {ledger['status']} via append_provenance_entry")

    out_path = HOME / "logs" / "sprint5_enrichment_output.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
    print(f"[LOG]    {out_path}")

    return results


if __name__ == "__main__":
    asyncio.run(main())
