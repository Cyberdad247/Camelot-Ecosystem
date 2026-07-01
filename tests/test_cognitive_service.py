"""Integration tests for the Cognitive Service HTTP front."""
import importlib.util
import json
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

_CP = Path(__file__).resolve().parent.parent / "control_plane"


@pytest.fixture()
def server(tmp_path, monkeypatch):
    monkeypatch.setenv("MEMCASTLE_DB", str(tmp_path / "svc.db"))
    monkeypatch.setenv("COGNITIVE_CONFIG_PATH", str(tmp_path / "cognitive_config.json"))
    spec = importlib.util.spec_from_file_location("cognitive_service", _CP / "cognitive_service.py")
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


def test_config_defaults(server):
    base, _ = server
    r = _get(f"{base}/config")
    assert r == {"sync_interval": 0.0, "sync_query": "Periodic Camelot-OS state sync."}


def test_config_post_persists_and_merges(server, tmp_path):
    base, svc = server
    r = _post(f"{base}/config", {"sync_interval": 30})
    assert r["sync_interval"] == 30.0
    assert json.loads(svc.CONFIG_PATH.read_text())["sync_interval"] == 30.0
    # A second write only touching unrelated/unknown keys must not clobber it.
    r2 = _post(f"{base}/config", {"unknown_key": "ignored"})
    assert r2["sync_interval"] == 30.0
    assert "unknown_key" not in r2


def test_config_post_rejects_bad_type(server):
    base, _ = server
    req = urllib.request.Request(
        f"{base}/config", data=json.dumps({"sync_interval": "soon"}).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=5)
        assert False, "expected HTTPError"
    except urllib.error.HTTPError as e:
        assert e.code == 400


def test_config_survives_reload(server):
    base, svc = server
    _post(f"{base}/config", {"sync_interval": 12.5})
    assert svc.load_config()["sync_interval"] == 12.5


def test_config_post_sync_query_persists(server):
    base, svc = server
    r = _post(f"{base}/config", {"sync_query": "summarize the lattice"})
    assert r["sync_query"] == "summarize the lattice"
    assert json.loads(svc.CONFIG_PATH.read_text())["sync_query"] == "summarize the lattice"


def test_config_post_rejects_empty_sync_query_without_corrupting(server):
    base, svc = server
    _post(f"{base}/config", {"sync_interval": 30, "sync_query": "keep me"})
    req = urllib.request.Request(
        f"{base}/config", data=json.dumps({"sync_query": "   "}).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=5)
        assert False, "expected HTTPError"
    except urllib.error.HTTPError as e:
        assert e.code == 400
    # Previously saved config must be untouched.
    current = json.loads(svc.CONFIG_PATH.read_text())
    assert current["sync_interval"] == 30.0
    assert current["sync_query"] == "keep me"


def test_config_post_rejects_negative_interval_without_corrupting(server):
    base, svc = server
    _post(f"{base}/config", {"sync_interval": 15})
    req = urllib.request.Request(
        f"{base}/config", data=json.dumps({"sync_interval": -5}).encode(),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=5)
        assert False, "expected HTTPError"
    except urllib.error.HTTPError as e:
        assert e.code == 400
    assert json.loads(svc.CONFIG_PATH.read_text())["sync_interval"] == 15.0
