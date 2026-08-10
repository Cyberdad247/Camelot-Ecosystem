# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""Tests for control_plane.observability — the traced_op instrumentation facade."""
import json

import pytest

pytest.importorskip("prometheus_client")
from control_plane.tracing import get_tracer  # noqa: E402
from prometheus_client import REGISTRY  # noqa: E402

from control_plane import observability  # noqa: E402


def _count(op: str, status: str) -> float:
    return REGISTRY.get_sample_value(
        "camelot_operation_total", {"operation": op, "status": status}
    ) or 0.0


def test_traced_op_emits_span_and_increments_counter(tmp_path):
    get_tracer()._sink = tmp_path / "t.jsonl"

    @observability.traced_op("unit.op")
    def handler(body, loop):
        return 200, {"ok": True}

    before = _count("unit.op", "ok")
    code, obj = handler({}, None)

    assert code == 200 and obj == {"ok": True}
    assert _count("unit.op", "ok") == before + 1
    rec = json.loads((tmp_path / "t.jsonl").read_text(encoding="utf-8").strip().splitlines()[-1])
    assert rec["operation"] == "unit.op"
    assert rec["tags"].get("http.status") == 200


def test_traced_op_records_error_and_reraises(tmp_path):
    get_tracer()._sink = tmp_path / "e.jsonl"

    @observability.traced_op("unit.boom")
    def handler(body, loop):
        raise RuntimeError("kaboom")

    before = _count("unit.boom", "error")
    with pytest.raises(RuntimeError):
        handler({}, None)

    assert _count("unit.boom", "error") == before + 1
    rec = json.loads((tmp_path / "e.jsonl").read_text(encoding="utf-8").strip().splitlines()[-1])
    assert rec["tags"].get("error") is True
