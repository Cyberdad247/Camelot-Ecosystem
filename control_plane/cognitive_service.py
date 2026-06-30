#!/usr/bin/env python3
"""Cognitive Service — HTTP front for the Tier-2/3 stack on cybertronia.

Exposes the built cognitive components as a networked edge service so go_router,
the dashboard, and the mesh can drive the vault:

  GET  /healthz              -> status, vault item count, cloud reachability
  POST /ingest  {text,source}-> Graphify extract -> MemCastle store; returns triplets
  GET  /search?q=&k=         -> MemCastle KNN
  POST /sync    {query}      -> //sync push+pull (MemCastle <-> NotebookLM)

Stdlib only (no web framework). Single-threaded HTTPServer keeps the shared
SQLite connection safe. CORS open so the deployed (HTTPS) dashboard can call it.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
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

# Shared pipeline (single-threaded server -> one SQLite connection is safe).
GF = graphify.Graphify()
BRIDGE = mcsync._DEFAULT_BRIDGE  # patchable in tests


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):  # quiet
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
            self._send(200, {"status": "ok", "vault_items": GF.mc.count(),
                             "cloud_reachable": ok, "cloud": reason})
        elif u.path == "/search":
            query = (q.get("q") or [""])[0]
            k = int((q.get("k") or ["5"])[0])
            if not query:
                self._send(400, {"error": "missing q"})
                return
            self._send(200, {"query": query, "results": GF.mc.search(query, k=k)})
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
            triplets = GF.ingest(text, source=data.get("source", "service"))
            self._send(200, {
                "triplets": [{"head": t.head, "relation": t.relation, "tail": t.tail} for t in triplets],
                "count": len(triplets), "vault_total": GF.mc.count(),
            })
        elif u.path == "/sync":
            query = data.get("query", "Summarize the current Camelot-OS state.")
            self._send(200, mcsync.sync(GF.mc, query, bridge=BRIDGE))
        else:
            self._send(404, {"error": "not found"})


def serve(addr: str = "127.0.0.1", port: int = 8090) -> HTTPServer:
    httpd = HTTPServer((addr, port), Handler)
    return httpd


def main():
    port = int(os.environ.get("COGNITIVE_PORT", "8090"))
    httpd = serve("0.0.0.0", port)
    print(f"[cognitive_service] serving on :{port} (vault items={GF.mc.count()})", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
