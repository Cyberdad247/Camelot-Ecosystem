"""Tests for the moa-routing-capture cartridge (Keys-Setup two-hook port).

Covers the boundedness contract: no raw content in the routing log, explicit
pre/post correlation, retention rotation, and a deterministic weighted signal
miner (routing 1.5 / cloud-gold specialist 2.0) with dedupe + limit.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CART_DIR = ROOT / "cartridges" / "moa-routing-capture"

# The cartridge dir is not a Python package (hyphenated, manifest-only dirs are
# the convention); add it to sys.path so mine_signal's `from routing_capture
# import ...` resolves and both hooks share one module instance.
sys.path.insert(0, str(CART_DIR))

import mine_signal as mine  # noqa: E402
import routing_capture as rc  # noqa: E402


@pytest.fixture
def log_path(tmp_path):
    p = tmp_path / "routing_log.jsonl"
    return str(p)


def test_pre_route_binds_decision_without_content(log_path):
    decision = rc.pre_route("summarize the audit findings", "internal.synth", "T1", "merlin")
    assert decision["effect_class"] == "internal.synth"
    assert decision["risk_tier"] == "T1"
    assert decision["chosen_agent"] == "merlin"
    assert decision["intent_hash"].startswith("sha256:")
    # No side effect: pre_route must not write anything.
    assert not Path(log_path).exists()
    # The raw intent text must never be part of the decision.
    assert "summarize the audit findings" not in json.dumps(decision)


def test_post_route_appends_bounded_line(log_path, tmp_path):
    decision = rc.pre_route("audit auth service", "ro.audit", "T0", "sir-ant")
    line = rc.post_route(decision, "pass", latency_ms=42, evidence_refs=["receipt://gideon/a"], target=log_path)

    assert line["verdict"] == "pass"
    assert line["latency_ms"] == 42
    assert line["cloud_gold"] is False
    assert line["evidence_refs"] == ["receipt://gideon/a"]
    assert set(line) == set(rc.ROUTING_LOG_FIELDS)

    raw = Path(log_path).read_text(encoding="utf-8")
    assert "audit auth service" not in raw, "raw intent leaked into the routing log"
    assert '"intent_hash": "sha256:' in raw


def test_rotation_bounds_log_size(log_path, tmp_path, monkeypatch):
    monkeypatch.setenv("MOA_LOG_MAX_LINES", "5")
    monkeypatch.setenv("MOA_ROUTING_LOG", log_path)
    for i in range(8):
        decision = rc.pre_route(f"task number {i}", "ro.fetch", "T0", "sir-ant")
        rc.post_route(decision, "pass", target=log_path)
    lines = [json.loads(l) for l in Path(log_path).read_text(encoding="utf-8").splitlines()]
    assert len(lines) <= 5, f"rotation failed: {len(lines)} lines after 8 posts"
    rotated = Path(log_path + ".1")
    assert rotated.exists(), "rotated window missing"


def test_post_route_rejects_bad_verdict(log_path):
    decision = rc.pre_route("x", "ro.fetch", "T0", "sir-ant")
    with pytest.raises(ValueError):
        rc.post_route(decision, "arbitrary text", target=log_path)


def test_pre_route_rejects_unknown_effect_class():
    with pytest.raises(ValueError):
        rc.pre_route("x", "not.a.class", "T0", "sir-ant")


def test_miner_weights_and_dedupe(tmp_path):
    log = tmp_path / "routing_log.jsonl"
    decision = rc.pre_route("audit auth service", "ro.audit", "T0", "sir-ant")
    rc.post_route(decision, "pass", target=str(log))
    rc.post_route(decision, "pass", target=str(log))  # duplicate
    escalated = rc.pre_route("deep reasoning", "internal.synth", "T1", "merlin")
    rc.post_route(escalated, "escalated", cloud_gold=True, target=str(log))

    signals = mine.mine(rc.read_log(str(log)))
    assert len(signals) == 2, "duplicate must dedupe"
    by_task = {s["task_hash"]: s for s in signals}
    local = by_task[decision["intent_hash"]]
    gold = by_task[escalated["intent_hash"]]
    assert (local["kind"], local["weight"]) == ("routing", 1.5)
    assert (gold["kind"], gold["weight"]) == ("specialist", 2.0)
    assert "audit auth service" not in json.dumps(signals), "raw content leaked into signals"


def test_miner_deterministic(tmp_path):
    log = tmp_path / "routing_log.jsonl"
    for i in range(5):
        d = rc.pre_route(f"task {i}", "ro.fetch", "T0", "sir-ant")
        rc.post_route(d, "pass", target=str(log))
    lines = rc.read_log(str(log))
    assert mine.mine(lines) == mine.mine(lines), "miner must be deterministic"
    assert len(mine.mine(lines, limit=3)) == 3, "limit must bound output"


def test_miner_self_test():
    assert mine.main(["--self-test"]) == 0
