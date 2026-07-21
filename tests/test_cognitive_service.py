"""Integration tests for the Cognitive Service HTTP front."""
import importlib.util
import json
import sys
import threading
import urllib.request
from pathlib import Path

import pytest

_CP = Path(__file__).resolve().parent.parent / "control_plane"


@pytest.fixture()
def server(tmp_path, monkeypatch):
    monkeypatch.setenv("MEMCASTLE_DB", str(tmp_path / "svc.db"))
    spec = importlib.util.spec_from_file_location("cognitive_service", _CP / "infra" / "cognitive_service.py")
    svc = importlib.util.module_from_spec(spec)
    sys.modules["cognitive_service"] = svc
    spec.loader.exec_module(svc)

    # Inject a fake, reachable NotebookLM bridge so /sync needs no network.
    class FakeBridge:
        def health_probe(self):
            return (True, "ok", 1.0)
        def sync_state(self, *, content=None, note_title=None):
            return {"action": "created", "note_id": "n", "content_chars": len(content or "")}
        def synthesize(self, q):
            return f"synthesis: {q}"
    svc.BRIDGE = FakeBridge()

    httpd = svc.serve("127.0.0.1", 0)  # ephemeral port
    port = httpd.server_address[1]
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{port}", svc
    httpd.shutdown()


def _get(url):
    return json.loads(urllib.request.urlopen(url, timeout=5).read())


def _post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    return json.loads(urllib.request.urlopen(req, timeout=5).read())


def test_healthz(server):
    base, _ = server
    r = _get(f"{base}/healthz")
    assert r["status"] == "ok"
    assert r["cloud_reachable"] is True  # fake bridge


def test_ingest_then_search(server):
    base, _ = server
    ing = _post(f"{base}/ingest", {"text": "go_router uses the rust rtk engine", "source": "t"})
    assert ing["count"] >= 1
    res = _get(f"{base}/search?q=rust%20engine&k=3")
    assert any("rtk" in r["text"].lower() or "rust" in r["text"].lower() for r in res["results"])


def test_sync_route(server):
    base, svc = server
    out = _post(f"{base}/sync", {"query": "summarize"})
    assert out["push"]["status"] == "ok"
    assert out["pull"]["status"] == "ok"


def test_cors_preflight(server):
    base, _ = server
    req = urllib.request.Request(f"{base}/ingest", method="OPTIONS")
    resp = urllib.request.urlopen(req, timeout=5)
    assert resp.headers.get("Access-Control-Allow-Origin") == "*"


def test_html_to_text(server):
    _, svc = server
    txt = svc.html_to_text("<html><body><p>Hi <b>there</b></p><script>x=1</script></body></html>")
    assert txt == "Hi there"


def test_forage_function_ingests(server):
    _, svc = server
    fake = lambda url: "<p>go_router uses the rust rtk engine</p>"
    r = svc.forage(svc.GF, "http://example.test/page", fetcher=fake)
    assert r["status"] == "ok" and r["triplets"] >= 1
    hits = svc.GF.mc.search("rust engine", k=2)
    assert any("rtk" in h["text"].lower() or "rust" in h["text"].lower() for h in hits)
    assert hits[0]["source"] == "http://example.test/page"


def test_forage_endpoint(server, monkeypatch):
    base, svc = server
    monkeypatch.setattr(svc, "fetch_url", lambda url, timeout=15.0: "<div>memcastle stores vectors</div>")
    r = _post(f"{base}/forage", {"url": "http://x.test"})
    assert r["status"] == "ok"
    assert r["triplets"] >= 1


def test_forage_fetch_error(server):
    _, svc = server
    def boom(url):
        raise ConnectionError("dns fail")
    r = svc.forage(svc.GF, "http://nope.test", fetcher=boom)
    assert r["status"] == "error" and "dns fail" in r["reason"]


def test_cybertronia_graph_stubs(server):
    """Phase 4 SSE endpoints return 501 + a hand-off payload anchored on
    CAMELOT_OS/docs/cybertronia-graph-ui-spec.md so the PWA Cockpit lazy
    cartridge and the Anya Dashboard panel can mount the GraphSnapshotStub
    (spec §4.3) deterministically and learn exactly which Phase 4 contract
    will replace each stub. Phase 4 wiring is additive on a green audit.
    """
    import urllib.error
    import urllib.request

    base, _ = server
    SPEC = "CAMELOT_OS/docs/cybertronia-graph-ui-spec.md"

    def _hit(url):
        try:
            resp = urllib.request.urlopen(url, timeout=5)
            return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    # === /snapshot ===
    code, body = _hit(f"{base}/api/cybertronia-graph/snapshot")
    assert code == 501
    assert body["status"] == "not_implemented"
    assert body["endpoint"] == "/api/cybertronia-graph/snapshot"
    assert body["method"] == "GET"
    assert body["expected_status"] == 200
    assert "GraphSnapshot" in body["expected_response_class"]
    assert "304" in body["expected_response_class"]
    assert body["phase"] == {"audit": "green", "compile": "pending",
                             "transport": "not_yet_built"}
    assert body["contract_ref"]["spec"] == SPEC
    assert "§8" in body["contract_ref"]["section"]
    assert body["contract_ref"]["schema_version"] == "cybertronia.snapshot/v1"
    assert body["phase4_hand_off"]["additive"] is True
    assert body["phase4_hand_off"]["dependency"].startswith("Phase 2")
    assert body["pre_sse_bootstrap"]["type"] == "GraphSnapshotStub"
    assert body["pre_sse_bootstrap"]["snapshot"] is None
    assert body["pre_sse_bootstrap"]["fallback_2d"] is True
    assert body["audit_blurb"].startswith("Phase 1 audit GREEN")
    assert "35/35 PASS" in body["audit_blurb"]

    # === /stream ===
    code, body = _hit(f"{base}/api/cybertronia-graph/stream")
    assert code == 501
    assert body["endpoint"] == "/api/cybertronia-graph/stream"
    assert "stream" in body["contract_ref"]["section"].lower()
    assert body["contract_ref"]["schema_version"] == "cybertronia.delta/v1"
    assert body["media_type_target"] == "text/event-stream"
    assert body["cadence_floor_ms"] == 160
    assert "GraphDelta" in body["expected_response_class"]

    # === /sync-status === (Phase 4 wiring DRAFT: NOW REAL, always 200)
    # The first endpoint to drop 501: serves the 4 spec §8 row 4 fields by
    # reading control_plane/cybertronia_compile.py's compile_cursor.json.
    # When Phase 2 hasn't shipped, responds 200 with null/0 fallback so the
    # PWA Cockpit + Anya Dashboard mount GraphSnapshotStub with no flicker.
    code, body = _hit(f"{base}/api/cybertronia-graph/sync-status")
    assert code == 200, "sync-status must be real (spec §8 row 4)"
    assert body["phase"]["audit"]     == "green"
    assert body["phase"]["transport"] == "live"
    assert "row 4 (sync-status)" in body["contract_ref"]["section"]
    assert SPEC in body["contract_ref"]["spec"]
    # Spec §8 row 4 mandates these four field names verbatim.
    for k in ("last_digest", "last_seen_at_ms", "lag_batches", "divergence_pending"):
        assert k in body, f"spec §8 row 4 missing field: {k}"
    # Phase 2 hasn't shipped in this test fixture, so fallback is null/0.
    assert body["status"] == "phase2_not_ready"
    assert body["last_digest"] is None
    assert body["last_seen_at_ms"] == 0
    assert body["lag_batches"] == 0
    assert body["divergence_pending"] is False

    # === /nodes/:id (well-formed) ===
    code, body = _hit(f"{base}/api/cybertronia-graph/nodes/abc123")
    assert code == 501
    assert body["endpoint"] == "/api/cybertronia-graph/nodes/:id"
    assert body["node_id"] == "abc123"
    assert "NodeRef" in body["expected_response_class"]
    assert "404" in body["expected_response_class"]
    assert body["contract_ref"]["schema_version"] == "cybertronia.snapshot/v1"

    # === defenders: malformed node ids → 400 (NOT 501) ===
    for bad in ("", "/", "//"):
        url = f"{base}/api/cybertronia-graph/nodes"
        if bad:
            url = f"{url}/{bad}"
        code, body = _hit(url)
        assert code == 400, f"expected 400 for nodes/{bad!r}, got {code}"
        assert body["error"] == "invalid or empty node id"
        assert body["path_pattern"] == "/api/cybertronia-graph/nodes/:id"
        assert SPEC in body["contract_ref"]
    code, body = _hit(f"{base}/api/cybertronia-graph/nodes/foo/extra/path")
    assert code == 400
    assert body["error"] == "invalid or empty node id"

    # === unknown cyber endpoint → 404 with available-list ===
    code, body = _hit(f"{base}/api/cybertronia-graph/banana")
    assert code == 404
    assert body["error"] == "unknown cybertronia-graph endpoint"
    assert body["known_prefix"] == "/api/cybertronia-graph/"
    assert set(body["available"]) == {"snapshot", "stream", "sync-status", "nodes/:id"}
    assert SPEC in body["contract_ref"]

    # === non-cyber unknown route still 404s from the generic fallback ===
    code, body = _hit(f"{base}/totally-bogus")
    assert code == 404
    assert body["error"] == "not found"


def test_cybertronia_graph_hand_off_is_deterministic(server):
    """Two consecutive calls return identical payloads — the hand-off
    is stable (no wall-clock leakage / random ids bleed into Phase 4)."""
    import urllib.error
    base, _ = server

    def _fetch(url):
        # The stub returns 501; urlopen() raises HTTPError, so we re-raise
        # via the body so the test can still inspect the hand-off payload.
        try:
            return json.loads(urllib.request.urlopen(url, timeout=5).read())
        except urllib.error.HTTPError as e:
            return json.loads(e.read())

    a = _fetch(f"{base}/api/cybertronia-graph/snapshot")
    b = _fetch(f"{base}/api/cybertronia-graph/snapshot")
    assert a == b
    assert a["phase"]["audit"] == "green"
