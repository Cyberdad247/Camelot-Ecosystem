"""Tests for //sync — MemCastle <-> NotebookLM orchestration (mocked bridge)."""
import importlib.util
import sys
from pathlib import Path

_CP = Path(__file__).resolve().parent.parent / "control_plane"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, _CP / "infra" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


memcastle = _load("memcastle")
mcsync = _load("memcastle_sync")


class HealthyBridge:
    """Fake NotebookLM bridge that is reachable."""

    def __init__(self):
        self.pushed = None

    def health_probe(self):
        return (True, "ok", 12.0)

    def sync_state(self, *, content=None, note_title=None):
        self.pushed = content
        return {"action": "created", "note_id": "note_x", "content_chars": len(content or "")}

    def synthesize(self, query):
        return f"Synthesis for: {query}\n- cybertronia is online"


class DownBridge:
    def health_probe(self):
        return (False, "auth expired — run notebooklm login", 0.0)

    def sync_state(self, **k):  # should never be called
        raise AssertionError("sync_state called while cloud down")

    def synthesize(self, q):
        raise AssertionError("synthesize called while cloud down")


class SynthFailBridge(HealthyBridge):
    def synthesize(self, query):
        return "[Living Notebook synthesis failed: AuthError: 401]"


def _mc(tmp_path):
    return memcastle.MemCastle(db_path=tmp_path / "sync.db", dim=64)


def test_push_healthy(tmp_path):
    mc = _mc(tmp_path)
    mc.store("go_router wires runes to rust", source="phase3")
    b = HealthyBridge()
    r = mcsync.push(mc, bridge=b)
    assert r["status"] == "ok"
    assert "go_router wires runes to rust" in b.pushed  # snapshot carried the vault
    mc.close()


def test_pull_healthy_stores_crystal(tmp_path):
    mc = _mc(tmp_path)
    before = mc.count()
    r = mcsync.pull(mc, "what is online?", bridge=HealthyBridge())
    assert r["status"] == "ok"
    assert mc.count() == before + 1  # synthesis stored as a new vault entry
    hit = mc.search("cybertronia online", k=1)[0]
    assert hit["source"] == "notebooklm"
    mc.close()


def test_cloud_down_skips_cleanly(tmp_path):
    mc = _mc(tmp_path)
    rp = mcsync.push(mc, bridge=DownBridge())
    rq = mcsync.pull(mc, "anything", bridge=DownBridge())
    assert rp["status"] == "skipped" and "auth expired" in rp["reason"]
    assert rq["status"] == "skipped"
    assert mc.count() == 0  # nothing stored, no crash
    mc.close()


def test_bridge_none_is_skip(tmp_path):
    mc = _mc(tmp_path)
    assert mcsync.push(mc, bridge=None)["status"] == "skipped"
    assert mcsync.pull(mc, "q", bridge=None)["status"] == "skipped"
    mc.close()


def test_synthesis_failure_not_stored(tmp_path):
    mc = _mc(tmp_path)
    r = mcsync.pull(mc, "q", bridge=SynthFailBridge())
    assert r["status"] == "error"
    assert mc.count() == 0  # the error string was NOT stored as knowledge
    mc.close()


def test_bidirectional_sync(tmp_path):
    mc = _mc(tmp_path)
    mc.store("memcastle depends on sqlite-vec", source="phase4")
    out = mcsync.sync(mc, "summarize", bridge=HealthyBridge())
    assert out["push"]["status"] == "ok"
    assert out["pull"]["status"] == "ok"
    mc.close()
