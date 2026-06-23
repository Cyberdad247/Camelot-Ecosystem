"""
SPRINT 2 — Cloud Brain Enrichment
Knights: LADY_APIS · SIR_MNEMO · SIR_SONUS
Protocol: URL source injection + UKG delta compression + morning briefing trigger

S2-01: WebRTC/VAD reference sources (MDN, Silero VAD, W3C spec)
S2-02: Enterprise factory patterns (GitLab CI, Prefect, Temporal)
S2-03: Async streaming TTS references (Kokoro HuggingFace + GitHub)
S2-04: UKG_SPRINT1_DELTA_V702 compressed delta note injected
S2-05: Morning audio briefing triggered via NotebookLM Studio (SIR_SONUS)
"""
from __future__ import annotations

import asyncio
import importlib.util
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

# ── Load bridge ───────────────────────────────────────────────────────────────

_BRIDGE = HOME / "03_VAULT" / "training" / "configs" / "notebooklm_bridge.py"
_spec = importlib.util.spec_from_file_location("notebooklm_bridge", _BRIDGE)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

CANONICAL_ID = _mod.CANONICAL_NOTEBOOK_ID
LEDGER = HOME / "PROVENANCE_LEDGER.md"

# ── Source manifest ───────────────────────────────────────────────────────────

SOURCES: list[dict] = [
    # S2-01: WebRTC + VAD
    {"url": "https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API",
     "tag": "S2-01-WebRTC-MDN",   "sprint": "S2-01"},
    {"url": "https://github.com/snakers4/silero-vad",
     "tag": "S2-01-SileroVAD",    "sprint": "S2-01"},
    {"url": "https://w3c.github.io/webrtc-pc/",
     "tag": "S2-01-WebRTC-W3C",   "sprint": "S2-01"},
    # S2-02: Enterprise factory patterns
    {"url": "https://docs.gitlab.com/ee/ci/yaml/",
     "tag": "S2-02-GitLabCI",     "sprint": "S2-02"},
    {"url": "https://docs.prefect.io/v3/develop/write-flows",
     "tag": "S2-02-Prefect",      "sprint": "S2-02"},
    {"url": "https://docs.temporal.io/develop/python",
     "tag": "S2-02-Temporal",     "sprint": "S2-02"},
    # S2-03: Async streaming TTS
    {"url": "https://huggingface.co/hexgrad/Kokoro-82M",
     "tag": "S2-03-Kokoro-HF",    "sprint": "S2-03"},
    {"url": "https://github.com/hexgrad/kokoro",
     "tag": "S2-03-Kokoro-GH",    "sprint": "S2-03"},
]

# ── UKG delta node ────────────────────────────────────────────────────────────

_UKG_DELTA_TEMPLATE = """\
# UKG_SPRINT1_DELTA_V702
> TOON_v2 compressed delta — Omega Assimilation → Sprint 1 complete
> Generated: {ts}

## SPRINT 0 — AUTH HARDENING [DEPLOYED 2026-05-17]
| Item | Detail |
|------|--------|
| `session_age_check()` | notebooklm_bridge.py; warn >21d, critical >30d |
| Boot phase | "Cloud Brain Auth" at position 6/17; non-blocking |
| Session refresh | storage_state.json re-saved via headed Playwright; age=0.0d |
| Boot state | 16/17 green (Clawdbot :18789 pre-existing fail unrelated) |

## SPRINT 1 — FACTORY THROUGHPUT [DEPLOYED 2026-05-17]
| Item | File | Detail |
|------|------|--------|
| Parallel batch | worker.py | `run_once_parallel()` asyncio.gather + Semaphore(N); `--parallel --concurrency N` |
| Sentinel gate | worker.py | `_sentinel_gate()` ghost-scans every written file; CRITICAL→.sentinel_blocked quarantine |
| Auto-ledger | worker.py | `_ledger_entry()` auto-prepends PROVENANCE_LEDGER row on every forge |
| Colony cron | colony.py | `--schedule 6h` daemon; CRITICAL findings→harness_queue.jsonl sir_sentinel p1 |
| sir_octavian | switchboard.py | engine=local_ops weight=0.82 ops/metrics/monitoring/factory |

## FACTORY STATE
- Throughput target: 50 tasks/hr (baseline ~12)
- Parallel capacity: 4 concurrent forge tasks (configurable)
- Sentinel gate: zero-trust on all LLM file writes
- Auto-ledger: PROVENANCE_LEDGER auto-maintained per forge
- Colony cron: 6h drift detection → auto-remediation → harness queue

## NORTHSTAR BLOCKERS (unchanged since Omega)
1. [OPEN] WebRTC full-duplex audio + VAD layer (SIR_SONUS S3-03)
2. [OPEN] WebSocket edge routing — HTTP POST still on hot path (S3-01)
3. [OPEN] mTLS/OIDC mobile gateway — Bifrost not deployed (S3-04)
4. [OPEN] Dynamic knight hot-swap — static TERMINAL_REGISTRY (future)
5. [OPEN] TOON_v2 delta compression automation (S2-04 = first manual delta)

## SPRINT 2 SOURCES (being injected now)
- WebRTC API: MDN reference, W3C spec
- VAD: Silero VAD (GitHub snakers4/silero-vad)
- Enterprise CI: GitLab CI YAML reference
- Workflow engines: Prefect v3, Temporal Python SDK
- TTS streaming: Kokoro-82M (HuggingFace + GitHub)
"""

# ── Ledger helper ─────────────────────────────────────────────────────────────

def _ledger_append(entry_text: str) -> int:
    existing = LEDGER.read_text(encoding="utf-8") if LEDGER.exists() else ""
    ids = [int(m.group(1)) for m in re.finditer(r"^\| *(\d+) *\|", existing, re.MULTILINE)]
    next_id = max(ids, default=1657) + 1
    LEDGER.write_text(entry_text.rstrip("\n") + "\n" + existing, encoding="utf-8")
    return next_id


# ── Main ─────────────────────────────────────────────────────────────────────

async def main() -> dict:
    print("\n[S2] SPRINT 2 — CLOUD BRAIN ENRICHMENT")
    print("    LADY_APIS · SIR_MNEMO · SIR_SONUS")
    print("=" * 60)

    # Health probe
    print("\n[PROBE] Cloud Brain health check...")
    ok, msg, ms = await _mod.async_health_probe()
    print(f"  {msg}  ({ms:.0f}ms)")
    if not ok:
        print("[ABORT] Cloud Brain offline")
        sys.exit(1)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    results: dict = {
        "ts": ts,
        "sources_added": [],
        "sources_failed": [],
        "ukgdelta": None,
        "audio_task": None,
    }

    # ── S2-01/02/03: URL source injection ─────────────────────────────────────
    print(f"\n[SOURCES] Injecting {len(SOURCES)} URLs ({len(SOURCES)} sources across S2-01/02/03)")
    for i, src in enumerate(SOURCES):
        tag = src["tag"]
        url = src["url"]
        sprint = src["sprint"]
        print(f"  [{i+1:2}/{len(SOURCES)}] [{sprint}] {tag}")
        try:
            r = await _mod.async_sources_add(url=url, notebook_id=CANONICAL_ID, wait=False)
            sid = r.get("source_id") or "?"
            print(f"            ✅  source_id={sid}")
            results["sources_added"].append({"tag": tag, "url": url, "source_id": sid})
        except Exception as e:
            errmsg = str(e)[:120]
            print(f"            ⚠️   {errmsg}")
            results["sources_failed"].append({"tag": tag, "url": url, "error": errmsg})
        await asyncio.sleep(1.5)  # polite rate-limit

    # ── S2-04: UKG delta node ──────────────────────────────────────────────────
    print("\n[S2-04] SIR_MNEMO — injecting UKG_SPRINT1_DELTA_V702...")
    delta_content = _UKG_DELTA_TEMPLATE.format(ts=ts)
    try:
        r = await _mod.async_sync_state(
            notebook_id=CANONICAL_ID,
            note_title="UKG_SPRINT1_DELTA_V702",
            content=delta_content,
        )
        print(f"  ✅  {r['action']}  |  {r['content_chars']:,} chars  |  note_id={r['note_id']}")
        results["ukgdelta"] = r
    except Exception as e:
        print(f"  ⚠️   UKG delta failed: {e}")
        results["ukgdelta"] = {"error": str(e)}

    # ── S2-05: Morning audio briefing ─────────────────────────────────────────
    print("\n[S2-05] SIR_SONUS — triggering morning audio briefing...")
    try:
        r = await _mod.async_studio_generate(
            "audio",
            notebook_id=CANONICAL_ID,
            instructions=(
                "Generate a concise morning operational briefing for the CAMELOT-OS digital factory. "
                "Cover: (1) current NORTHSTAR blocker status — WebRTC, WebSocket edge, mTLS gateway, "
                "knight hot-swap, TOON_v2 delta; (2) sprint status — Sprint 1 complete, Sprint 2 in progress; "
                "(3) top 3 priorities for today based on the sprint plan. "
                "Tone: technical, direct, no filler. Duration: 2-3 minutes."
            ),
        )
        task_id = r.get("task_id") or "?"
        print(f"  ✅  task_id={task_id}")
        results["audio_task"] = r
    except Exception as e:
        print(f"  ⚠️   Audio generation failed: {e}")
        results["audio_task"] = {"error": str(e)}

    # ── Summary ───────────────────────────────────────────────────────────────
    added    = len(results["sources_added"])
    failed   = len(results["sources_failed"])
    delta_ok = results["ukgdelta"] and "error" not in results["ukgdelta"]
    audio_ok = results["audio_task"] and "error" not in results["audio_task"]

    print("\n" + "=" * 60)
    print("[S2] RESULT")
    print(f"  Sources added  : {added}/{len(SOURCES)}")
    if failed:
        print(f"  Sources failed : {failed}")
        for f in results["sources_failed"]:
            print(f"    - {f['tag']}: {f['error'][:80]}")
    print(f"  UKG delta      : {'✅ UKG_SPRINT1_DELTA_V702' if delta_ok else '❌'}")
    print(f"  Audio briefing : {'✅ task queued' if audio_ok else '❌'}")

    # ── Ledger ────────────────────────────────────────────────────────────────
    source_list = "; ".join(s["tag"] for s in results["sources_added"])
    row = (
        f"| {{next_id}} | **SPRINT 2 — CLOUD BRAIN ENRICHMENT** | LADY_APIS · SIR_MNEMO · SIR_SONUS"
        f" | ✅ DEPLOYED | S2-01/02/03: {added} URLs injected ({source_list[:120]}). "
        f"S2-04: {'UKG_SPRINT1_DELTA_V702 created/updated' if delta_ok else 'FAILED'}. "
        f"S2-05: {'audio briefing task queued' if audio_ok else 'FAILED'}. |\n"
    )
    try:
        existing = LEDGER.read_text(encoding="utf-8") if LEDGER.exists() else ""
        ids = [int(m.group(1)) for m in re.finditer(r"^\| *(\d+) *\|", existing, re.MULTILINE)]
        next_id = max(ids, default=1657) + 1
        LEDGER.write_text(row.replace("{next_id}", str(next_id)) + existing, encoding="utf-8")
        print(f"\n[LEDGER] Entry {next_id} written")
    except Exception as e:
        print(f"\n[LEDGER] Failed: {e}")

    # Save output log
    out_path = HOME / "logs" / "sprint2_enrichment_output.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    import json
    out_path.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
    print(f"[LOG]    {out_path}")

    return results


if __name__ == "__main__":
    asyncio.run(main())
