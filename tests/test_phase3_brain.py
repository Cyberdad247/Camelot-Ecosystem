"""Phase 3 BRAIN acceptance tests (P3-T01..T06).

Covers the Agent-Native MDX schema, /visual-plan and /visual-recap renderers,
the HTMX Bifrost board, SSE telemetry, and the ApprovalButton HITL flow.
"""
from __future__ import annotations

import pytest

from control_plane.mdx_schema import validate_mdx, render_mdx
from control_plane.mdx_renderers import visual_plan, visual_recap
from control_plane.kinetic_loop import run_sync


# ── P3-T01 MDX schema ─────────────────────────────────────────────────────────

def _doc():
    return {
        "version": "9000.14", "kind": "visual-plan", "title": "t",
        "blocks": [{"type": "Summary", "text": "x", "risk": "AUTO"}],
    }


def test_mdx_schema_valid():
    ok, errors = validate_mdx(_doc())
    assert ok and errors == []


@pytest.mark.parametrize("mut", [
    lambda d: d.update(version="1.0"),
    lambda d: d.update(kind="bogus"),
    lambda d: d["blocks"].append({"type": "Nope"}),
    lambda d: d["blocks"][0].update(risk="BAD"),
])
def test_mdx_schema_rejects_malformed(mut):
    d = _doc(); mut(d)
    ok, _ = validate_mdx(d)
    assert not ok


# ── P3-T03 /visual-plan, P3-T04 /visual-recap ─────────────────────────────────

def test_visual_plan_is_valid_mdx_with_approval():
    res = run_sync("build a status dashboard", auto_approve=True)
    plan = visual_plan(res)
    ok, _ = validate_mdx(plan)
    assert ok and plan["kind"] == "visual-plan"
    assert any(b["type"] == "ApprovalButton" for b in plan["blocks"])
    assert "```mermaid" in render_mdx(plan)


def test_visual_recap_reports_outcome():
    res = run_sync("create a greeting string", auto_approve=True)
    recap = visual_recap(res)
    ok, _ = validate_mdx(recap)
    assert ok and recap["kind"] == "visual-recap"
    assert "completed" in recap["blocks"][0]["text"]


# ── P3-T02 board, P3-T05 SSE, P3-T06 approval ─────────────────────────────────

@pytest.fixture()
def client():
    fastapi = pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient
    from control_plane.bifrost_server import create_app
    return TestClient(create_app())


def test_board_has_htmx_and_luxora_gold(client):
    html = client.get("/bifrost").text
    assert "hx-get" in html and "hx-trigger" in html and "hx-swap" in html
    assert "#D4AF37" in html


def test_sse_stream_emits_metrics(client):
    r = client.get("/bifrost/metrics/stream?frames=2")
    assert r.headers["content-type"].startswith("text/event-stream")
    assert "event: metrics" in r.text and '"mamba_ratio"' in r.text


def test_approval_button_resumes_loop(client):
    client.post("/bifrost/plan", data={"intent": "build a status dashboard"})
    pending = list(client.app.state.approvals._pending.keys())
    assert pending
    r = client.post(f"/bifrost/approve/{pending[0]}")
    assert r.status_code == 200 and "approved" in r.text
    pa = client.app.state.approvals.get(pending[0])
    assert pa.approved and pa.result is not None


# ── Aperture LLM-usage panel (Bifrost dashboard visibility) ───────────────────

def test_aperture_panel_renders_on_board(client):
    html = client.get("/bifrost").text
    assert 'hx-get="/bifrost/aperture"' in html


def test_aperture_panel_endpoint(client):
    r = client.get("/bifrost/aperture")
    assert r.status_code == 200
    assert "LLM GATEWAY" in r.text and "open dashboard" in r.text


def test_aperture_parse_and_graceful_degradation():
    from control_plane.aperture_bridge import parse_usage, ApertureBridge, render_panel
    s = parse_usage({"models": [
        {"model": "anthropic/claude-opus-4-5", "tokens": 1000, "cost_usd": 0.03, "requests": 1}],
        "sessions": 1})
    assert s.connected and s.total_cost_usd == 0.03 and s.top_model.model.startswith("anthropic/")
    # unreachable Aperture -> disconnected, never raises
    bad = ApertureBridge(base_url="http://127.0.0.1:1", timeout_s=0.3).fetch_usage()
    assert bad.connected is False and "not connected" in render_panel(bad)
