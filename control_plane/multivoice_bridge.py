# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Multivoice Bridge — OmniRoute, LMCache KV Affinity & Realtime S2S / PBX Telemetry.
==================================================================================
Reads live affinity and LMCache KV cache stats from the Go Multivoice-Router /
LMCache Affinity Adapter and RealtimeVoiceBridge (cache-hit rate, SLO escapes,
active pins, TTFT/TTFA savings, chunk evictions, P2P transfers, per-engine TTFT,
realtime S2S sessions, Fonoster PBX telephony calls) and renders a Bifrost panel —
so you can watch **KV-cache routing efficiency, realtime voice latency, and PBX calls**
in real time.

Graceful degradation: if the router or adapter isn't running, it returns
``connected=False`` and the panel shows "router offline" rather than erroring.

Run as module:
    python -m control_plane.multivoice_bridge --test
"""
from __future__ import annotations

__version__ = "9000.25"  # CYBERTRONIA - REALTIME VOICE & FONOSTER ASSIMILATED

import json
import os
import sys
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_URL = os.environ.get("MULTIVOICE_URL", "http://127.0.0.1:7680")
DEFAULT_VOICE_URL = os.environ.get("REALTIME_VOICE_URL", "http://127.0.0.1:8765")


@dataclass
class AffinityStats:
    connected: bool = False
    routes: int = 0
    cache_hits: int = 0
    escapes: int = 0
    pins: int = 0
    cache_hit_pct: float = 0.0
    slo_ms: float = 0.0
    avg_ttft: dict[str, float] = field(default_factory=dict)
    # LMCache & TTFT Telemetry extensions
    tokens_cached: int = 0
    tokens_hit: int = 0
    ttft_savings_pct: float = 0.0
    p2p_transfers: int = 0
    evictions: int = 0
    memory_usage_bytes: int = 0
    # Realtime Voice S2S & Fonoster PBX Telemetry extensions
    realtime_sessions: int = 0
    active_pbx_calls: int = 0
    ttfa_ms: float = 0.0
    vad_active: bool = False
    speech_duration_s: float = 0.0
    pbx_verbs_executed: int = 0
    # 9router & Voice-Pro Telemetry extensions
    rtk_bytes_saved: int = 0
    rtk_savings_pct: float = 0.0
    voice_pro_jobs: int = 0
    voice_pro_audio_s: float = 0.0
    detail: str = ""


def parse_metrics(payload: dict[str, Any]) -> AffinityStats:
    if payload.get("affinity") is False:
        return AffinityStats(connected=True, detail="affinity layer disabled")
    avg_ttft_raw = payload.get("avg_ttft_ms")
    if isinstance(avg_ttft_raw, dict):
        avg_ttft = {k: round(float(v), 1) for k, v in avg_ttft_raw.items()}
    elif isinstance(avg_ttft_raw, (int, float)):
        avg_ttft = {"realtime_voice": round(float(avg_ttft_raw), 1)}
    else:
        avg_ttft = {}

    return AffinityStats(
        connected=True,
        routes=int(payload.get("routes", 0)),
        cache_hits=int(payload.get("cache_hits", 0)),
        escapes=int(payload.get("escapes", 0)),
        pins=int(payload.get("pins", 0)),
        cache_hit_pct=round(float(payload.get("cache_hit_pct", 0.0)), 1),
        slo_ms=float(payload.get("slo_ms", 0.0)),
        avg_ttft=avg_ttft,
        tokens_cached=int(payload.get("stored_tokens") or payload.get("tokens_cached", 0)),
        tokens_hit=int(payload.get("hit_tokens") or payload.get("tokens_hit", 0)),
        ttft_savings_pct=round(float(payload.get("ttft_savings_pct", 0.0)), 1),
        p2p_transfers=int(payload.get("p2p_transfers", 0)),
        evictions=int(payload.get("evictions", 0)),
        memory_usage_bytes=int(payload.get("memory_usage_bytes", 0)),
        realtime_sessions=int(payload.get("realtime_sessions", payload.get("active_sessions", 0))),
        active_pbx_calls=int(payload.get("active_pbx_calls", 0)),
        ttfa_ms=round(float(payload.get("avg_ttfa_ms", payload.get("ttfa_ms", 0.0))), 1),
        vad_active=bool(payload.get("vad_active", False)),
        speech_duration_s=round(float(payload.get("speech_duration_s", 0.0)), 2),
        pbx_verbs_executed=int(payload.get("pbx_verbs_executed", 0)),
        rtk_bytes_saved=int(payload.get("rtk_bytes_saved", 0)),
        rtk_savings_pct=round(float(payload.get("rtk_savings_pct", 0.0)), 1),
        voice_pro_jobs=int(payload.get("voice_pro_jobs", payload.get("completed_jobs", 0))),
        voice_pro_audio_s=round(float(payload.get("voice_pro_audio_s", payload.get("total_audio_seconds", 0.0))), 2),
        detail="ok",
    )


class MultivoiceBridge:
    def __init__(
        self,
        base_url: str = DEFAULT_URL,
        voice_url: str = DEFAULT_VOICE_URL,
        timeout_s: float = 2.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.voice_url = voice_url.rstrip("/")
        self.timeout_s = timeout_s
        self._adapter: Optional[Any] = None
        self._realtime_bridge: Optional[Any] = None
        self._nine_router: Optional[Any] = None
        self._voice_pro: Optional[Any] = None

    def attach_adapter(self, adapter: Any) -> None:
        """Attach an in-process LMCacheAffinityAdapter instance."""
        self._adapter = adapter

    def attach_realtime_bridge(self, bridge: Any) -> None:
        """Attach an in-process RealtimeVoiceBridge instance."""
        self._realtime_bridge = bridge

    def attach_nine_router(self, router: Any) -> None:
        """Attach an in-process NineRouterEngine instance."""
        self._nine_router = router

    def attach_voice_pro(self, adapter: Any) -> None:
        """Attach an in-process VoiceProAdapter instance."""
        self._voice_pro = adapter

    @property
    def metrics_url(self) -> str:
        return f"{self.base_url}/metrics"

    @property
    def voice_usage_url(self) -> str:
        return f"{self.voice_url}/v1/usage"

    def fetch_affinity(self) -> AffinityStats:
        """Fetch affinity metrics; checks in-process adapters first, then network endpoint."""
        metrics: dict[str, Any] = {}
        connected = False

        if self._adapter is not None:
            try:
                metrics = self._adapter.export_metrics()
                connected = True
            except Exception as exc:
                return AffinityStats(connected=False, detail=f"adapter error ({type(exc).__name__})")
        else:
            try:
                with urllib.request.urlopen(self.metrics_url, timeout=self.timeout_s) as r:
                    if r.status == 200:
                        metrics = json.loads(r.read().decode("utf-8"))
                        connected = True
            except Exception:
                pass

        # Overlay in-process RealtimeVoiceBridge if attached
        if self._realtime_bridge is not None:
            try:
                v_metrics = self._realtime_bridge.get_aggregate_metrics()
                metrics.update(v_metrics)
                connected = True
            except Exception:
                pass

        # Overlay in-process NineRouterEngine if attached
        if self._nine_router is not None:
            try:
                nr_telemetry = self._nine_router.export_telemetry()
                metrics.update(nr_telemetry)
                connected = True
            except Exception:
                pass

        # Overlay in-process VoiceProAdapter if attached
        if self._voice_pro is not None:
            try:
                vp_telemetry = self._voice_pro.get_telemetry()
                metrics.update(vp_telemetry)
                connected = True
            except Exception:
                pass

        if not connected:
            return AffinityStats(connected=False, detail="router offline")

        return parse_metrics(metrics)


def render_panel(s: AffinityStats, gold: str = "#D4AF37") -> str:
    if not s.connected:
        return (
            '<div id="omniroute" class="card">'
            f'<span class="label">OMNIROUTE AFFINITY</span>'
            f'<span class="val">router offline</span>'
            f'<div style="font-size:10px;opacity:.6">{s.detail}</div></div>'
        )
    ttft = "".join(
        f'<div style="display:flex;justify-content:space-between;font-size:11px">'
        f'<span>{k}</span><span>{v:.0f}ms</span></div>'
        for k, v in sorted(s.avg_ttft.items())
    )
    extra_stats = ""
    if s.ttft_savings_pct > 0 or s.tokens_hit > 0 or s.p2p_transfers > 0:
        extra_stats = (
            f'<div style="font-size:10px;opacity:.85;margin-top:2px;color:{gold}">'
            f'TTFT Saved: {s.ttft_savings_pct:.0f}% · {s.tokens_hit} hit tokens · '
            f'{s.p2p_transfers} P2P transfers</div>'
        )

    voice_stats = ""
    if s.realtime_sessions > 0 or s.active_pbx_calls > 0 or s.ttfa_ms > 0:
        voice_stats = (
            f'<div style="font-size:10px;opacity:.9;margin-top:4px;border-top:1px solid rgba(212,175,55,0.2);padding-top:2px;color:{gold}">'
            f'S2S / PBX Voice: {s.realtime_sessions} ws sess · {s.active_pbx_calls} pbx calls · '
            f'TTFA: {s.ttfa_ms:.0f}ms</div>'
        )

    nine_stats = ""
    if s.rtk_savings_pct > 0 or s.voice_pro_jobs > 0:
        nine_stats = (
            f'<div style="font-size:10px;opacity:.9;margin-top:4px;border-top:1px solid rgba(212,175,55,0.2);padding-top:2px;color:{gold}">'
            f'9Router RTK: {s.rtk_savings_pct:.1f}% saved · Voice-Pro: {s.voice_pro_jobs} dubs ({s.voice_pro_audio_s:.1f}s)</div>'
        )

    return (
        '<div id="omniroute" class="card">'
        f'<span class="label">OMNIROUTE AFFINITY</span>'
        f'<span class="val">{s.cache_hit_pct:.0f}% cache</span>'
        f'<div style="font-size:10px;opacity:.7">{s.routes} routes · {s.cache_hits} hits · '
        f'{s.escapes} escapes · {s.pins} pins · SLO {s.slo_ms:.0f}ms</div>'
        + extra_stats
        + voice_stats
        + nine_stats
        + (f'<div style="margin-top:4px;color:{gold}">TTFT/engine</div>{ttft}' if ttft else '')
        + '</div>'
    )


# ── Self-test ────────────────────────────────────────────────────────────────

def _selftest() -> int:
    failures = 0

    def check(name: str, cond: bool) -> None:
        nonlocal failures
        if not cond:
            failures += 1
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")

    print("MultivoiceBridge self-test")

    s = parse_metrics({"routes": 10, "cache_hits": 7, "escapes": 1, "pins": 3,
                       "cache_hit_pct": 70.0, "slo_ms": 2000,
                       "avg_ttft_ms": {"sir_codex": 120.0},
                       "hit_tokens": 1400, "ttft_savings_pct": 45.0, "p2p_transfers": 2,
                       "realtime_sessions": 2, "active_pbx_calls": 1, "avg_ttfa_ms": 180.0,
                       "rtk_savings_pct": 32.5, "completed_jobs": 4, "total_audio_seconds": 42.0})
    check("parse aggregates", s.connected and s.cache_hit_pct == 70.0 and s.pins == 3)
    check("parse lmcache fields", s.tokens_hit == 1400 and s.ttft_savings_pct == 45.0 and s.p2p_transfers == 2)
    check("parse realtime voice & pbx fields", s.realtime_sessions == 2 and s.active_pbx_calls == 1 and s.ttfa_ms == 180.0)
    check("parse 9router & voice-pro telemetry", s.rtk_savings_pct == 32.5 and s.voice_pro_jobs == 4 and s.voice_pro_audio_s == 42.0)
    check("panel shows cache %", "70% cache" in render_panel(s) and "OMNIROUTE" in render_panel(s))
    check("panel shows ttft saved", "TTFT Saved: 45%" in render_panel(s))
    check("panel shows voice telemetry", "S2S / PBX Voice" in render_panel(s) and "180ms" in render_panel(s))
    check("panel shows 9router rtk and voice-pro", "9Router RTK: 32.5% saved" in render_panel(s) and "Voice-Pro: 4 dubs" in render_panel(s))

    bad = MultivoiceBridge("http://127.0.0.1:1", timeout_s=0.3).fetch_affinity()
    check("unreachable -> disconnected (no raise)", bad.connected is False)
    check("offline panel renders", "router offline" in render_panel(bad))

    # live round-trip against a mock /metrics
    import http.server
    import socketserver
    import threading
    body = json.dumps({"routes": 4, "cache_hits": 2, "escapes": 0, "pins": 2,
                       "cache_hit_pct": 50.0, "slo_ms": 2000, "avg_ttft_ms": {}}).encode()

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200); self.send_header("Content-Type", "application/json")
            self.end_headers(); self.wfile.write(body)
        def log_message(self, *a): pass

    with socketserver.TCPServer(("127.0.0.1", 0), H) as srv:
        port = srv.server_address[1]
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            live = MultivoiceBridge(f"http://127.0.0.1:{port}").fetch_affinity()
            check("live mock fetch", live.connected and live.cache_hit_pct == 50.0)
        finally:
            srv.shutdown()

    print(f"\n{'ALL PASS' if failures == 0 else f'{failures} FAILURE(S)'} — multivoice_bridge")
    return failures


if __name__ == "__main__":
    if "--test" in sys.argv:
        raise SystemExit(1 if _selftest() else 0)
    print(json.dumps(MultivoiceBridge().fetch_affinity().__dict__, indent=2, default=str))
