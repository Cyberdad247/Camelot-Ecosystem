#!/usr/bin/env python3
"""Cognitive Service — HTTP front for the Tier-2/3 stack on cybertronia.

Endpoints (CORS-open for the deployed dashboard):
  GET  /healthz               -> status, vault count, cloud reachability
  POST /ingest  {text,source} -> Graphify extract -> MemCastle store
  POST /forage  {url}         -> fetch a URL, strip HTML, ingest its text
  GET  /search?q=&k=          -> MemCastle KNN
  POST /sync    {query}       -> //sync push+pull (MemCastle <-> NotebookLM)

forage is the GROUNDED replacement for the fictional "OpenViking OSINT fleet":
a real urllib fetch + HTML strip + Graphify ingest. No distributed WASM scrapers,
no Lightpanda — just a real web fetch into the real pipeline.

A background scheduler runs //sync every COGNITIVE_SYNC_INTERVAL seconds (0 =
off). All MemCastle access is serialized by a lock so the scheduler thread and
HTTP handler thread never touch SQLite concurrently.
"""
from __future__ import annotations

import html
import importlib.util
import json
import os
import re
import sys
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

_CP = Path(__file__).resolve().parent
sys.path.insert(0, str(_CP))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, _CP / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


memcastle = _load("memcastle")
graphify = _load("graphify")
mcsync = _load("memcastle_sync")

GF = graphify.Graphify()
BRIDGE = mcsync._DEFAULT_BRIDGE          # patchable in tests
_LOCK = threading.Lock()                  # serializes all SQLite access


def html_to_text(raw: str) -> str:
    """Strip scripts/styles/tags and unescape entities -> plain text."""
    raw = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    raw = html.unescape(raw)
    return re.sub(r"\s+", " ", raw).strip()


def fetch_url(url: str, timeout: float = 15.0) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Camelot-Forager/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        charset = r.headers.get_content_charset() or "utf-8"
        return r.read(2_000_000).decode(charset, errors="replace")  # cap 2 MB


def forage(gf, url: str, fetcher=None) -> dict:
    """Real web forage: fetch URL -> text -> Graphify ingest -> MemCastle.

    `fetcher` is injectable (defaults to the module-level fetch_url, looked up
    dynamically) so the pipeline is tested without network.
    """
    f = fetcher or fetch_url
    try:
        raw = f(url)
    except Exception as e:
        return {"status": "error", "url": url, "reason": f"{type(e).__name__}: {e}"}
    text = html_to_text(raw)
    if not text:
        return {"status": "error", "url": url, "reason": "no text extracted"}
    with _LOCK:
        triplets = gf.ingest(text, source=url)
        total = gf.mc.count()
    return {"status": "ok", "url": url, "chars": len(text),
            "triplets": len(triplets), "vault_total": total}


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def _send(self, code: int, payload: dict):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body_json(self) -> dict:
        n = int(self.headers.get("Content-Length", 0) or 0)
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return {}

    def do_OPTIONS(self):
        self._send(204, {})

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        if u.path == "/healthz":
            ok, reason = mcsync._cloud_ok(BRIDGE)
            with _LOCK:
                items = GF.mc.count()
            self._send(200, {"status": "ok", "vault_items": items,
                             "cloud_reachable": ok, "cloud": reason})
        elif u.path == "/search":
            query = (q.get("q") or [""])[0]
            k = int((q.get("k") or ["5"])[0])
            if not query:
                self._send(400, {"error": "missing q"})
                return
            with _LOCK:
                results = GF.mc.search(query, k=k)
            self._send(200, {"query": query, "results": results})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        u = urlparse(self.path)
        data = self._body_json()
        if u.path == "/ingest":
            text = data.get("text", "")
            if not text:
                self._send(400, {"error": "missing text"})
                return
            with _LOCK:
                triplets = GF.ingest(text, source=data.get("source", "service"))
                total = GF.mc.count()
            self._send(200, {
                "triplets": [{"head": t.head, "relation": t.relation, "tail": t.tail} for t in triplets],
                "count": len(triplets), "vault_total": total,
            })
        elif u.path == "/forage":
            url = data.get("url", "")
            if not url:
                self._send(400, {"error": "missing url"})
                return
            self._send(200, forage(GF, url))
        elif u.path == "/sync":
            query = data.get("query", "Summarize the current Camelot-OS state.")
            with _LOCK:
                result = mcsync.sync(GF.mc, query, bridge=BRIDGE)
            self._send(200, result)
        else:
            self._send(404, {"error": "not found"})


def _scheduler_loop(interval: float):
    """Periodic //sync (edge-first: skips cleanly when cloud is down)."""
    while True:
        time.sleep(interval)
        try:
            with _LOCK:
                mcsync.sync(GF.mc, "Periodic Camelot-OS state sync.", bridge=BRIDGE)
        except Exception:
            pass  # never let the scheduler crash the service


def serve(addr: str = "127.0.0.1", port: int = 8090) -> HTTPServer:
    return HTTPServer((addr, port), Handler)


def main():
    port = int(os.environ.get("COGNITIVE_PORT", "8090"))
    interval = float(os.environ.get("COGNITIVE_SYNC_INTERVAL", "0") or "0")
    if interval > 0:
        threading.Thread(target=_scheduler_loop, args=(interval,), daemon=True).start()
        print(f"[cognitive_service] scheduled //sync every {interval}s", flush=True)
    httpd = serve("0.0.0.0", port)
    with _LOCK:
        n = GF.mc.count()
    print(f"[cognitive_service] serving on :{port} (vault items={n})", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
