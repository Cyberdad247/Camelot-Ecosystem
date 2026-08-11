# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""Tests for control_plane.tracing — the no-Docker tracer."""
import json

import pytest
from control_plane.infra.tracing import Tracer, get_tracer


def _read(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").strip().splitlines()]


def test_active_span_records_tags_and_writes_jsonl(tmp_path):
    t = Tracer("test-svc")
    t._sink = tmp_path / "spans.jsonl"
    with t.start_active_span("op1") as scope:
        scope.span.set_tag("entry_id", 42).set_tag("phase", "commit")
    recs = _read(t._sink)
    assert len(recs) == 1
    rec = recs[0]
    assert rec["operation"] == "op1"
    assert rec["service"] == "test-svc"
    assert rec["tags"] == {"entry_id": 42, "phase": "commit"}
    assert rec["duration_ms"] is not None and rec["parent_id"] is None


def test_parent_child_nesting_shares_trace_and_links_parent(tmp_path):
    t = Tracer("svc")
    t._sink = tmp_path / "s.jsonl"
    with t.start_active_span("parent") as parent:
        with t.start_active_span("child") as child:
            assert child.span.trace_id == parent.span.trace_id
            assert child.span.parent_id == parent.span.span_id
    ops = {r["operation"] for r in _read(t._sink)}
    assert ops == {"parent", "child"}


def test_exception_tags_error_and_reraises(tmp_path):
    t = Tracer("svc")
    t._sink = tmp_path / "e.jsonl"
    with pytest.raises(ValueError):
        with t.start_active_span("boom"):
            raise ValueError("kaboom")
    rec = _read(t._sink)[0]
    assert rec["tags"].get("error") is True
    assert any(log.get("event") == "error" for log in rec["logs"])


def test_get_tracer_is_cached_per_service():
    assert get_tracer("alpha") is get_tracer("alpha")
    assert get_tracer("alpha") is not get_tracer("beta")
