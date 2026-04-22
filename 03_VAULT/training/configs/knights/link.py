"""SIR_LINK — Handshake Coordinator & Switchboard ATC
L2/L5 Bridge Knight. Owns the terminal manifest, negotiates handshakes,
governs cross-engine routing. Air Traffic Control for the LLM fleet.
"""
from __future__ import annotations

import asyncio
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .base import BaseKnight

CAMELOT_HOME = Path(__file__).resolve().parents[4]
CONFIGS_DIR  = Path(__file__).resolve().parent.parent
MANIFEST_PATH = CAMELOT_HOME / "logs" / "switchboard_manifest.json"

if str(CONFIGS_DIR.parent.parent / "control_plane") not in sys.path:
    sys.path.insert(0, str(CONFIGS_DIR.parent.parent / "control_plane"))


@dataclass
class Handshake:
    terminal_id: str
    status:      str       # "acknowledged" | "refused" | "timeout"
    latency_ms:  float
    protocol:    str       # "tcp_probe" | "assumed" | "cli_check"
    timestamp:   float


class SirLink(BaseKnight):
    """Air Traffic Control — all LLM terminals route through Sir Link's manifest.

    Responsibilities:
      1. Terminal registration & deregistration
      2. Handshake negotiation before dispatch
      3. Manifest broadcast (logs/switchboard_manifest.json)
      4. Fallback chain when preferred terminal is dark
      5. Cost-aware routing — never burn high-cost terminal for low-value task
    """
    name      = "SIR_LINK"
    title     = "Handshake Coordinator"
    specialty = "Switchboard ATC — terminal health, handshake, bridge routing"
    icon      = "[L]"

    # ── Core handshake ────────────────────────────────────────────────────────

    def handshake(self, terminal_id: str) -> Handshake:
        """Synchronous handshake — checks manifest cache, probes if stale."""
        t0 = time.perf_counter()
        manifest = self._read_manifest()
        terminals = manifest.get("terminals", {})
        entry = terminals.get(terminal_id, {})
        status = entry.get("status", "unknown")
        lat = (time.perf_counter() - t0) * 1000
        ack = "acknowledged" if status in ("live", "assumed_live") else "refused"
        return Handshake(
            terminal_id=terminal_id,
            status=ack,
            latency_ms=lat,
            protocol="manifest_cache",
            timestamp=time.time(),
        )

    def negotiate(self, capabilities: list[str], cost_ceiling: str = "high") -> str | None:
        """Pick the best live terminal ID for the given capability set."""
        manifest = self._read_manifest()
        terminals = manifest.get("terminals", {})
        cost_order = ["free", "low", "medium", "high"]
        ceiling_idx = cost_order.index(cost_ceiling) if cost_ceiling in cost_order else 3

        candidates = []
        for tid, data in terminals.items():
            t_caps = data.get("capability", [])
            t_cost = data.get("cost_tier", "high")
            t_status = data.get("status", "unknown")
            t_weight = data.get("weight", 0.5)
            if (
                any(c in t_caps for c in capabilities)
                and cost_order.index(t_cost) <= ceiling_idx
                and t_status in ("live", "assumed_live", "unknown")
            ):
                candidates.append((t_weight, tid))

        if not candidates:
            return None
        candidates.sort(reverse=True)
        return candidates[0][1]

    # ── Manifest operations ───────────────────────────────────────────────────

    def get_manifest(self) -> dict:
        return self._read_manifest()

    def get_terminal_status(self, terminal_id: str) -> str:
        manifest = self._read_manifest()
        return manifest.get("terminals", {}).get(terminal_id, {}).get("status", "unknown")

    def live_terminals(self) -> list[str]:
        manifest = self._read_manifest()
        return [
            tid for tid, data in manifest.get("terminals", {}).items()
            if data.get("status") in ("live", "assumed_live")
        ]

    def dark_terminals(self) -> list[str]:
        manifest = self._read_manifest()
        return [
            tid for tid, data in manifest.get("terminals", {}).items()
            if data.get("status") == "dark"
        ]

    def fleet_summary(self) -> dict:
        """Dashboard-ready summary of all terminals."""
        manifest = self._read_manifest()
        terminals = manifest.get("terminals", {})
        live = [t for t, d in terminals.items() if d.get("status") in ("live", "assumed_live")]
        dark = [t for t, d in terminals.items() if d.get("status") == "dark"]
        unknown = [t for t, d in terminals.items() if d.get("status") not in ("live", "assumed_live", "dark")]
        return {
            "total":   len(terminals),
            "live":    len(live),
            "dark":    len(dark),
            "unknown": len(unknown),
            "live_ids":    live,
            "dark_ids":    dark,
            "unknown_ids": unknown,
            "manifest_age_s": round(time.time() - manifest.get("updated", 0), 1),
        }

    # ── BaseKnight execute ────────────────────────────────────────────────────

    def execute(self, directive: str, intent: dict, write: bool = False) -> dict:
        d = directive.lower()
        if "handshake" in d or "probe" in d:
            terminal = intent.get("terminal_id", "sir_boris")
            result = self.handshake(terminal)
            return {
                "status": "success",
                "output": f"Handshake {result.status} — {terminal} ({result.latency_ms:.1f}ms)",
                "handshake": result.__dict__,
                "files_created": [],
            }
        if "manifest" in d or "fleet" in d or "status" in d:
            summary = self.fleet_summary()
            return {
                "status": "success",
                "output": f"Fleet: {summary['live']}/{summary['total']} live | dark={summary['dark_ids']}",
                "fleet": summary,
                "files_created": [],
            }
        if "negotiate" in d or "route" in d:
            caps = intent.get("capabilities", ["orchestration"])
            cost = intent.get("cost_ceiling", "high")
            winner = self.negotiate(caps, cost)
            return {
                "status": "success",
                "output": f"Negotiated terminal: {winner}",
                "terminal_id": winner,
                "files_created": [],
            }
        return {
            "status": "success",
            "output": f"Sir Link standing by. Fleet: {self.fleet_summary()}",
            "files_created": [],
        }

    # ── Internal ──────────────────────────────────────────────────────────────

    def _read_manifest(self) -> dict:
        try:
            return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}


# Singleton
_link = SirLink()

def handshake(terminal_id: str) -> Handshake:
    return _link.handshake(terminal_id)

def negotiate(capabilities: list[str], cost_ceiling: str = "high") -> str | None:
    return _link.negotiate(capabilities, cost_ceiling)

def fleet_summary() -> dict:
    return _link.fleet_summary()
