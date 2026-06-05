# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
HermesBus v1.0 — Sovereign Inter-Knight Message Bus
=====================================================
Bridges CAMELOT-OS knights to the ~/.hermes/ message bus.
All inter-knight communication flows through Hermes channels.

Channels:
  colony.risk       — Colony scanner risk score deltas
  iron_gate.alerts  — Iron Gate decisions + Nemesis Prime actions
  shadow.threats    — Heimdall fingerprint vector detections
  dependency.updates — Sir Link dependency proposals
  compression.status — Compression nexus progress
  organize.progress — Lady M / Lady Alexandria file org progress
  swarm.events      — NANO_SWARM node lifecycle events
"""
from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

log = logging.getLogger("HERMES_BUS")

_HERMES_HOME = Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes")))
_SESSIONS_DIR = _HERMES_HOME / "sessions"

CHANNELS = frozenset({
    "colony.risk",
    "iron_gate.alerts",
    "shadow.threats",
    "dependency.updates",
    "compression.status",
    "organize.progress",
    "swarm.events",
})


class HermesBus:
    """
    Lightweight Hermes message bus client.

    Each channel maps to a JSONL file in ~/.hermes/sessions/<channel>.jsonl
    Messages are line-delimited JSON objects with a 'ts' (timestamp) field injected.

    Usage:
        bus = HermesBus()
        bus.publish("colony.risk", {"risk_score": 75, "delta": -10})
        bus.subscribe("shadow.threats", callback=my_handler, poll_interval=5)
    """

    def __init__(self, hermes_home: Optional[Path] = None):
        self._home = hermes_home or _HERMES_HOME
        self._sessions = self._home / "sessions"
        self._sessions.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Publish
    # ------------------------------------------------------------------

    def publish(self, channel: str, payload: dict[str, Any]) -> bool:
        """Publish a message to a Hermes channel.

        Returns True on success, False on I/O error (never raises).
        """
        channel_path = self._sessions / f"{channel.replace('.', '_')}.jsonl"
        message = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "channel": channel,
            **payload,
        }
        try:
            with open(channel_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(message, default=str) + "\n")
            log.debug("[HERMES] published → %s: %s", channel, list(payload.keys()))
            return True
        except OSError as exc:
            log.warning("[HERMES] publish failed (channel=%s): %s", channel, exc)
            return False

    # ------------------------------------------------------------------
    # Subscribe / read
    # ------------------------------------------------------------------

    def read_channel(self, channel: str, last_n: int = 50) -> list[dict]:
        """Read last N messages from a channel. Returns empty list if channel empty."""
        channel_path = self._sessions / f"{channel.replace('.', '_')}.jsonl"
        if not channel_path.exists():
            return []
        try:
            lines = channel_path.read_text(encoding="utf-8").strip().splitlines()
            messages = []
            for line in lines[-last_n:]:
                try:
                    messages.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
            return messages
        except OSError:
            return []

    def subscribe(self, channel: str, callback: Callable[[dict], None],
                  poll_interval: float = 5.0, run_forever: bool = True) -> None:
        """Poll-based subscribe. Calls callback for each new message.

        Tracks last-seen line count to avoid reprocessing old messages.
        Non-blocking version: set run_forever=False for single-poll.
        """
        channel_path = self._sessions / f"{channel.replace('.', '_')}.jsonl"
        last_line = 0

        def _poll():
            nonlocal last_line
            if not channel_path.exists():
                return
            lines = channel_path.read_text(encoding="utf-8").strip().splitlines()
            new_lines = lines[last_line:]
            for line in new_lines:
                try:
                    msg = json.loads(line)
                    callback(msg)
                except Exception as exc:
                    log.debug("[HERMES] callback error on %s: %s", channel, exc)
            last_line = len(lines)

        if not run_forever:
            _poll()
            return

        log.info("[HERMES] subscribe started: channel=%s interval=%ss", channel, poll_interval)
        while True:
            try:
                _poll()
            except Exception as exc:
                log.debug("[HERMES] poll error: %s", exc)
            time.sleep(poll_interval)

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def status(self) -> dict[str, Any]:
        """Return health summary of all known channels."""
        result = {}
        for channel in sorted(CHANNELS):
            channel_path = self._sessions / f"{channel.replace('.', '_')}.jsonl"
            if channel_path.exists():
                lines = channel_path.read_text(encoding="utf-8").strip().splitlines()
                msg_count = len(lines)
                last_ts = None
                if lines:
                    try:
                        last_ts = json.loads(lines[-1]).get("ts")
                    except Exception:
                        pass
                result[channel] = {
                    "active": True,
                    "message_count": msg_count,
                    "last_message_ts": last_ts,
                    "path": str(channel_path),
                }
            else:
                result[channel] = {"active": False, "message_count": 0}
        return result
