# SPDX-License-Identifier: MIT

"""Tests for the Cognitive MCP server (scoped: memcastle_search, graphify_ingest,
cognitive_sync, cognitive_forage). Mirrors tests/test_cognitive_service.py's
fresh-module-per-test fixture so SQLite state never leaks between tests."""
import asyncio
import importlib.util
import sys
from pathlib import Path

import pytest

_CP = Path(__file__).resolve().parent.parent / "control_plane"


@pytest.fixture()
def mcp_mod(tmp_path, monkeypatch):
    monkeypatch.setenv("MEMCASTLE_DB", str(tmp_path / "mcp.db"))
    monkeypatch.setenv("COGNITIVE_CONFIG_PATH", str(tmp_path / "cognitive_config.json"))
    spec = importlib.util.spec_from_file_location("cognitive_mcp", _CP / "cognitive_mcp.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["cognitive_mcp"] = mod
    spec.loader.exec_module(mod)

    # Inject a fake, reachable NotebookLM bridge so cognitive_sync needs no network.
    class FakeBridge:
        def health_probe(self):
            return (True, "ok", 1.0)

        def sync_state(self, *, content=None, note_title=None):
            return {"action": "created", "note_id": "n", "content_chars": len(content or "")}

        def synthesize(self, q):
            return f"synthesis: {q}"

    mod.cs.BRIDGE = FakeBridge()
    return mod


def test_tools_list_exposes_exactly_four(mcp_mod):
    names = {t["name"] for t in mcp_mod._tools()}
    assert names == {"memcastle_search", "graphify_ingest", "cognitive_sync", "cognitive_forage"}


def test_graphify_ingest_then_memcastle_search(mcp_mod):
    out = mcp_mod._tool_graphify_ingest({"text": "go_router uses the rust rtk engine", "source": "t"})
    assert out["count"] >= 1
    assert out["vault_total"] >= 1
    assert {"head", "relation", "tail"} <= out["triplets"][0].keys()

    res = mcp_mod._tool_memcastle_search({"query": "rust engine", "k": 3})
    assert res["query"] == "rust engine"
    assert any("rtk" in r["text"].lower() or "rust" in r["text"].lower() for r in res["results"])


def test_cognitive_sync_uses_fake_bridge(mcp_mod):
    out = mcp_mod._tool_cognitive_sync({"query": "summarize"})
    assert out["push"]["status"] == "ok"
    assert out["pull"]["status"] == "ok"


def test_cognitive_sync_default_query(mcp_mod):
    # No 'query' supplied -> falls back to the periodic sync default, no crash.
    out = mcp_mod._tool_cognitive_sync({})
    assert out["push"]["status"] == "ok"
    assert out["pull"]["status"] == "ok"


def test_cognitive_forage_with_fake_fetcher(mcp_mod):
    # forage() looks up the module-global `fetch_url` dynamically, so patching the
    # attribute on the freshly-loaded cognitive_service module avoids real network.
    mcp_mod.cs.fetch_url = lambda url, timeout=15.0: "<p>memcastle stores vectors</p>"
    out = mcp_mod._tool_cognitive_forage({"url": "http://x.test"})
    assert out["status"] == "ok"
    assert out["triplets"] >= 1
    assert out["vault_total"] >= 1


def test_missing_required_arg_raises(mcp_mod):
    with pytest.raises(ValueError):
        mcp_mod._tool_memcastle_search({})
    with pytest.raises(ValueError):
        mcp_mod._tool_graphify_ingest({})
    with pytest.raises(ValueError):
        mcp_mod._tool_cognitive_forage({})


def test_tools_call_dispatch_surfaces_error_without_crashing(mcp_mod):
    # Full tools/call path: a handler exception must come back as isError=True
    # content, not an unhandled exception or a raw traceback on stdout.
    resp = asyncio.run(mcp_mod._dispatch({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": "memcastle_search", "arguments": {}},
    }))
    assert resp["result"]["isError"] is True
    assert "Error" in resp["result"]["content"][0]["text"]


def test_tools_call_unknown_tool_is_jsonrpc_error(mcp_mod):
    resp = asyncio.run(mcp_mod._dispatch({
        "jsonrpc": "2.0", "id": 2, "method": "tools/call",
        "params": {"name": "not_a_real_tool", "arguments": {}},
    }))
    assert "error" in resp
    assert resp["error"]["code"] == -32602


def test_initialize_handshake(mcp_mod):
    resp = asyncio.run(mcp_mod._dispatch({"jsonrpc": "2.0", "id": 0, "method": "initialize"}))
    assert resp["result"]["protocolVersion"] == mcp_mod.PROTOCOL_VERSION
    assert resp["result"]["serverInfo"]["name"] == "camelot-cognitive"
