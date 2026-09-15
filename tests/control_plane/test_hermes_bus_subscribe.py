# SPDX-License-Identifier: MIT
"""
Regression tests for HermesBus.subscribe message tracking.

Pins the contract that subscribe() must NEVER permanently skip valid
messages because of:
- corrupt/torn JSONL lines mixed with valid messages
- a torn final line (partial write without trailing newline)
- file truncation or rotation (file shrinking below the cursor)

Historical defect: subscribe() tracked position by *line count*. Any
corrupt line, torn write, or truncation desynced that count from the
logical message stream, so valid JSON messages were silently skipped
on later polls. The fix tracks position by raw byte offset, which is
immune to all three failure modes.

Cursor semantics (unchanged from the historical behavior, pinned here
so future refactors don't drift): the cursor lives for ONE subscribe()
invocation. A fresh subscribe() call re-reads the channel from the
beginning (at-least-once per invocation). Single-poll tests below
therefore capture delivery per-call with separate lists.
"""

import threading
import time
from pathlib import Path

from control_plane.infra.hermes_bridge import HermesBus


def _make_bus(tmp_path: Path) -> HermesBus:
    return HermesBus(hermes_home=tmp_path)


def _channel_file(tmp_path: Path, channel: str) -> Path:
    return tmp_path / "sessions" / f"{channel.replace('.', '_')}.jsonl"


def _run_bounded_forever(bus, channel, callback, interval=0.01):
    """Drive run_forever=True until callback raises KeyboardInterrupt."""
    try:
        bus.subscribe(channel, callback, poll_interval=interval, run_forever=True)
    except KeyboardInterrupt:
        pass


def test_subscribe_single_poll_delivers_around_midstream_corrupt_line(tmp_path):
    """Corrupt line in the middle: valid neighbors delivered in the same poll."""
    bus = _make_bus(tmp_path)
    path = _channel_file(tmp_path, "corrupt.mid")

    bus.publish("corrupt.mid", {"seq": 1})
    path.write_text(
        path.read_text(encoding="utf-8") + "{corrupt torn line not json\n",
        encoding="utf-8",
    )
    bus.publish("corrupt.mid", {"seq": 2})

    call1 = []
    bus.subscribe("corrupt.mid", call1.append, run_forever=False)
    # Old line-count cursor delivered only [1] here (corrupt line consumed
    # one count, seq 2 was treated as already-seen).
    assert [m["seq"] for m in call1] == [1, 2]

    bus.publish("corrupt.mid", {"seq": 3})
    call2 = []
    bus.subscribe("corrupt.mid", call2.append, run_forever=False)
    assert [m["seq"] for m in call2] == [1, 2, 3]


def test_subscribe_delivers_after_leading_corrupt_line(tmp_path):
    """Corrupt content BEFORE any valid message must not block what follows."""
    bus = _make_bus(tmp_path)
    path = _channel_file(tmp_path, "corrupt.lead")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not json at all\n", encoding="utf-8")
    bus.publish("corrupt.lead", {"seq": 1})

    call1 = []
    bus.subscribe("corrupt.lead", call1.append, run_forever=False)
    assert [m["seq"] for m in call1] == [1]

    bus.publish("corrupt.lead", {"seq": 2})
    call2 = []
    bus.subscribe("corrupt.lead", call2.append, run_forever=False)
    assert [m["seq"] for m in call2] == [1, 2]


def test_subscribe_ignores_torn_final_line_until_complete(tmp_path):
    """A partial write without trailing newline must not be delivered or counted."""
    bus = _make_bus(tmp_path)
    path = _channel_file(tmp_path, "torn.tail")

    bus.publish("torn.tail", {"seq": 1})
    path.write_text(path.read_text(encoding="utf-8") + '{"seq": 2', encoding="utf-8")

    call1 = []
    bus.subscribe("torn.tail", call1.append, run_forever=False)
    assert [m["seq"] for m in call1] == [1]

    # The writer finishes the torn line; message 2 must NOT be permanently
    # skipped. (Old line-count cursor counted the torn line as consumed and
    # never delivered seq 2.)
    with open(path, "a", encoding="utf-8") as f:
        f.write("}\n")
    bus.publish("torn.tail", {"seq": 3})

    call2 = []
    bus.subscribe("torn.tail", call2.append, run_forever=False)
    assert [m["seq"] for m in call2] == [1, 2, 3]


def test_subscribe_forever_delivers_completed_torn_line(tmp_path, monkeypatch):
    """Within one long-lived subscription, a completed torn line is delivered."""
    monkeypatch.setattr(time, "sleep", lambda _s: None)
    bus = _make_bus(tmp_path)
    path = _channel_file(tmp_path, "torn.forever")

    bus.publish("torn.forever", {"seq": 1})
    path.write_text(path.read_text(encoding="utf-8") + '{"seq": 2', encoding="utf-8")

    seen = []

    def _complete_line_later():
        with open(path, "a", encoding="utf-8") as f:
            f.write("}\n")
        bus.publish("torn.forever", {"seq": 3})

    timer = threading.Timer(0.05, _complete_line_later)
    timer.start()

    def _callback(msg):
        seen.append(msg["seq"])
        if len(seen) >= 3:
            raise KeyboardInterrupt

    try:
        _run_bounded_forever(bus, "torn.forever", _callback)
    finally:
        timer.join()

    assert seen == [1, 2, 3]


def test_subscribe_single_poll_resets_after_truncation(tmp_path):
    """Log rotation/truncation must not permanently wedge or skip the cursor."""
    bus = _make_bus(tmp_path)
    path = _channel_file(tmp_path, "rotated.log")

    bus.publish("rotated.log", {"seq": 1})
    call1 = []
    bus.subscribe("rotated.log", call1.append, run_forever=False)
    assert [m["seq"] for m in call1] == [1]

    path.write_text("", encoding="utf-8")
    bus.publish("rotated.log", {"seq": 2})

    call2 = []
    bus.subscribe("rotated.log", call2.append, run_forever=False)
    assert [m["seq"] for m in call2] == [2]


def test_subscribe_forever_delivers_around_midstream_corruption(tmp_path, monkeypatch):
    """run_forever=True loop delivers every valid message around a corrupt line."""
    monkeypatch.setattr(time, "sleep", lambda _s: None)
    bus = _make_bus(tmp_path)
    path = _channel_file(tmp_path, "forever.corrupt")

    bus.publish("forever.corrupt", {"seq": 1})
    path.write_text(
        path.read_text(encoding="utf-8") + "{corrupt\n", encoding="utf-8"
    )
    bus.publish("forever.corrupt", {"seq": 2})

    seen = []

    def _callback(msg):
        seen.append(msg["seq"])
        if len(seen) >= 2:
            raise KeyboardInterrupt

    _run_bounded_forever(bus, "forever.corrupt", _callback)
    assert seen == [1, 2]


def test_subscribe_forever_no_duplicate_delivery_on_steady_state(tmp_path, monkeypatch):
    """Happy path: a long-lived subscription never re-delivers old messages."""
    monkeypatch.setattr(time, "sleep", lambda _s: None)
    bus = _make_bus(tmp_path)
    bus.publish("steady.state", {"seq": 0})

    seen = []
    state = {"n": 0}

    def _callback(msg):
        seen.append(msg["seq"])
        state["n"] += 1
        if state["n"] >= 4:
            raise KeyboardInterrupt
        bus.publish("steady.state", {"seq": msg["seq"] + 1})

    _run_bounded_forever(bus, "steady.state", _callback)
    assert seen == [0, 1, 2, 3]


def test_subscribe_missing_channel_is_noop(tmp_path):
    bus = _make_bus(tmp_path)
    seen = []
    bus.subscribe("does.not.exist", seen.append, run_forever=False)
    assert seen == []
