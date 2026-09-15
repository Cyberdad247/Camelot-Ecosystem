# SPDX-License-Identifier: MIT
"""
Regression tests for Bifrost gateway swarm-event reads on the hardened
HermesBus subscribe path (byte-offset cursor, corruption-immune).

Pins:
- poll_swarm_events() routes through HermesBus.subscribe(run_forever=False)
- delivery survives corrupt lines / torn tails in swarm.events channel
- subscribe_swarm_events() forwards streaming parameters unchanged
- CLI `events --poll` exercises the hardened path
"""

import json
from pathlib import Path

from control_plane.dispatch import bifrost_gateway
from control_plane.infra.hermes_bridge import HermesBus


def _swarm_file(tmp_path: Path) -> Path:
    # The gateway publishes/reads the canonical 'swarm.events' channel.
    return tmp_path / "sessions" / "swarm_events.jsonl"


def _make_bus(tmp_path: Path) -> HermesBus:
    return HermesBus(hermes_home=tmp_path)


def test_poll_swarm_events_survives_corrupt_line(tmp_path):
    bus = _make_bus(tmp_path)
    path = _swarm_file(tmp_path)

    bus.publish(bifrost_gateway.SWARM_EVENTS_CHANNEL, {"event": "command", "seq": 1})
    path.write_text(
        path.read_text(encoding="utf-8") + "{corrupt torn line not json\n",
        encoding="utf-8",
    )
    bus.publish(bifrost_gateway.SWARM_EVENTS_CHANNEL, {"event": "command", "seq": 2})

    events = bifrost_gateway.poll_swarm_events(bus=bus)
    assert [e["seq"] for e in events if "seq" in e] == [1, 2]


def test_poll_swarm_events_retries_torn_tail_after_completion(tmp_path):
    bus = _make_bus(tmp_path)
    path = _swarm_file(tmp_path)

    bus.publish(bifrost_gateway.SWARM_EVENTS_CHANNEL, {"seq": 1})
    path.write_text(path.read_text(encoding="utf-8") + '{"seq": 2', encoding="utf-8")

    first = bifrost_gateway.poll_swarm_events(bus=bus)
    assert [e["seq"] for e in first if "seq" in e] == [1]

    with open(path, "a", encoding="utf-8") as f:
        f.write("}\n")
    second = bifrost_gateway.poll_swarm_events(bus=bus)
    assert [e["seq"] for e in second if "seq" in e] == [1, 2]


def test_subscribe_swarm_events_forwards_streaming_params(tmp_path):
    bus = _make_bus(tmp_path)
    received: list[dict] = []

    bus.publish(bifrost_gateway.SWARM_EVENTS_CHANNEL, {"seq": 7})

    captured: dict = {}

    def _spy(channel, callback, poll_interval=5.0, run_forever=True):
        captured["channel"] = channel
        captured["poll_interval"] = poll_interval
        captured["run_forever"] = run_forever
        callback({"seq": 7})

    # subscribe_swarm_events must delegate to bus.subscribe unchanged.
    class _SpyBus(HermesBus):
        def subscribe(self, channel, callback, poll_interval=5.0, run_forever=True):
            _spy(channel, callback, poll_interval=poll_interval, run_forever=run_forever)

    bifrost_gateway.subscribe_swarm_events(
        received.append,
        poll_interval=1.5,
        run_forever=False,
        bus=_SpyBus(hermes_home=tmp_path),
    )
    assert captured["channel"] == "swarm.events"
    assert captured["poll_interval"] == 1.5
    assert captured["run_forever"] is False
    assert received == [{"seq": 7}]


def test_cli_events_poll_uses_hardened_path(tmp_path, capsys):
    bus = _make_bus(tmp_path)
    bus.publish(bifrost_gateway.SWARM_EVENTS_CHANNEL, {"seq": 1})

    rc_called: dict = {}

    def _fake_poll(bus=None):
        rc_called["used"] = True
        return [{"seq": 1}]

    original = bifrost_gateway.poll_swarm_events
    bifrost_gateway.poll_swarm_events = _fake_poll
    try:
        bifrost_gateway._main(["events", "--poll"])
    finally:
        bifrost_gateway.poll_swarm_events = original

    out = capsys.readouterr().out.strip().splitlines()
    assert rc_called["used"] is True
    assert json.loads(out[0])["seq"] == 1


def test_cli_events_history_still_reads_last_n(tmp_path, capsys, monkeypatch):
    # Isolate: CLI constructs its own HermesBus; point that constructor at tmp.
    monkeypatch.setattr(
        bifrost_gateway, "HermesBus", lambda: _make_bus(tmp_path)
    )
    bus = _make_bus(tmp_path)
    for i in range(5):
        bus.publish(bifrost_gateway.SWARM_EVENTS_CHANNEL, {"seq": i})

    bifrost_gateway._main(["events", "--last", "3"])
    out = capsys.readouterr().out.strip().splitlines()
    assert len(out) == 3
    assert [json.loads(line)["seq"] for line in out] == [2, 3, 4]
