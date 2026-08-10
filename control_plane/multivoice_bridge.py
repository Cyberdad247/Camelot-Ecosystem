# -*- coding: utf-8 -*-
"""
Multivoice Bridge — OmniRoute affinity telemetry for the Bifrost Board (v9000.14).
=================================================================================
Reads the live affinity stats from the Go Multivoice-Router's ``/metrics``
endpoint (cache-hit rate, SLO escapes, active pins, per-engine TTFT) and renders
a Bifrost panel — so you can watch **KV-cache routing efficiency** in real time.

Same graceful-degradation contract as the Aperture bridge: if the router isn't
running it returns ``connected=False`` and the panel shows "router offline"
rather than erroring.

Run as module:
    python -m control_plane.multivoice_bridge --test
"""
from __future__ import annotations

__version__ = "9000.14"  # CYBERTRONIA

import json
import os
import sys
import urllib.request
from dataclasses import dataclass, field
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_URL = os.environ.get("MULTIVOICE_URL", "http://127.0.0.1:7680")


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
    detail: str = ""


def parse_metrics(payload: dict[str, Any]) -> AffinityStats:
    if payload.get("affinity") is False:
        return AffinityStats(connected=True, detail="affinity layer disabled")
    return AffinityStats(
        connected=True,
        routes=int(payload.get("routes", 0)),
        cache_hits=int(payload.get("cache_hits", 0)),
        escapes=int(payload.get("escapes", 0)),
        pins=int(payload.get("pins", 0)),
        cache_hit_pct=round(float(payload.get("cache_hit_pct", 0.0)), 1),
        slo_ms=float(payload.get("slo_ms", 0.0)),
        avg_ttft={k: round(float(v), 1) for k, v in (payload.get("avg_ttft_ms") or {}).items()},
        detail="ok",
    )


class MultivoiceBridge:
    def __init__(self, base_url: str = DEFAULT_URL, timeout_s: float = 2.0):
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s

    @property
    def metrics_url(self) -> str:
        return f"{self.base_url}/metrics"

    def fetch_affinity(self) -> AffinityStats:
        """Fetch affinity metrics; never raises — disconnected summary on error."""
        try:
            with urllib.request.urlopen(self.metrics_url, timeout=self.timeout_s) as r:
                if r.status != 200:
                    return AffinityStats(connected=False, detail=f"HTTP {r.status}")
                return parse_metrics(json.loads(r.read().decode("utf-8")))
        except Exception as exc:
            return AffinityStats(connected=False, detail=f"router offline ({type(exc).__name__})")


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
    return (
        '<div id="omniroute" class="card">'
        f'<span class="label">OMNIROUTE AFFINITY</span>'
        f'<span class="val">{s.cache_hit_pct:.0f}% cache</span>'
        f'<div style="font-size:10px;opacity:.7">{s.routes} routes · {s.cache_hits} hits · '
        f'{s.escapes} escapes · {s.pins} pins · SLO {s.slo_ms:.0f}ms</div>'
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
                       "avg_ttft_ms": {"sir_codex": 120.0}})
    check("parse aggregates", s.connected and s.cache_hit_pct == 70.0 and s.pins == 3)
    check("panel shows cache %", "70% cache" in render_panel(s) and "OMNIROUTE" in render_panel(s))

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
