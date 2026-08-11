# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
ColonyNexus v1.0 — Colony Scanner → Defense Grid Live Sensor
=============================================================
Parses colony_report.md and exposes a ColonyState with risk_entropy
suitable for Iron Gate pre_execute() escalation.

HermesBus integration: fires delta event on colony.risk channel
whenever risk_score changes by ≥ DELTA_THRESHOLD points.
"""
from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

log = logging.getLogger("COLONY_NEXUS")

_DEFAULT_REPORT = Path("colony_report.md")
_DELTA_THRESHOLD = 10.0   # fire Hermes event if score shifts by this much

# ── Risk label to normalised hitl_tier ─────────────────────────────────────
_RISK_TO_TIER: dict[str, str] = {
    "LOW":      "AUTO",
    "MEDIUM":   "PROMPT",
    "HIGH":     "PROMPT",
    "CRITICAL": "HUMAN_GATE",
}


@dataclass
class ColonyState:
    risk_score: float            # 0–100
    risk_label: str              # LOW / MEDIUM / HIGH / CRITICAL
    hitl_tier: str               # AUTO / PROMPT / HUMAN_GATE
    risk_entropy: float          # normalised 0.0–1.0 for Iron Gate
    secrets_count: int = 0
    duplicates_count: int = 0
    unused_imports: int = 0
    total_lines: int = 0
    report_path: str = ""
    scanned_at: float = field(default_factory=time.time)

    @property
    def is_critical(self) -> bool:
        return self.risk_label == "CRITICAL"

    @property
    def requires_human_gate(self) -> bool:
        return self.hitl_tier == "HUMAN_GATE"


class ColonyNexus:
    """Reads colony_report.md and provides structured ColonyState for the
    Defense Grid.  Can be wired into pre_execute() to escalate HITL tier
    when colony risk is CRITICAL.
    """

    def __init__(
        self,
        report_path: Path | str | None = None,
        hermes_enabled: bool = True,
    ) -> None:
        self.report_path = Path(report_path or _DEFAULT_REPORT)
        self.hermes_enabled = hermes_enabled
        self._last_score: Optional[float] = None

    # ── Public API ─────────────────────────────────────────────────────────

    def scan(self) -> ColonyState:
        """Parse colony_report.md and return a fresh ColonyState.

        Also fires a Hermes `colony.risk` event if the risk score has
        changed by ≥ DELTA_THRESHOLD since the last call.
        """
        state = self._parse_report()

        if self.hermes_enabled:
            self._maybe_emit_hermes(state)

        self._last_score = state.risk_score
        return state

    def risk_entropy_for_gate(self) -> float:
        """Convenience: return normalised risk_entropy (0–1) without Hermes."""
        old_flag = self.hermes_enabled
        self.hermes_enabled = False
        try:
            return self.scan().risk_entropy
        finally:
            self.hermes_enabled = old_flag

    # ── Parser ─────────────────────────────────────────────────────────────

    def _parse_report(self) -> ColonyState:
        if not self.report_path.exists():
            log.warning("[COLONY_NEXUS] report not found: %s — returning LOW state", self.report_path)
            return ColonyState(
                risk_score=0.0, risk_label="LOW", hitl_tier="AUTO",
                risk_entropy=0.0, report_path=str(self.report_path),
            )

        text = self.report_path.read_text(encoding="utf-8", errors="replace")
        return self._extract_state(text)

    def _extract_state(self, text: str) -> ColonyState:
        risk_score   = self._match_float(r"Risk Score\s*\|\s*([\d.]+)", text, 0.0)
        risk_label   = self._match_str(r"\*\*(CRITICAL|HIGH|MEDIUM|LOW)\*\*", text, "LOW")
        secrets      = self._match_int(r"(\d+)\s+potential secret", text, 0)
        dupes        = self._match_int(r"(\d+)\s+duplicate file", text, 0)
        unused       = self._match_int(r"(\d+)\s+unused import", text, 0)
        lines        = self._match_int(r"([\d,]+)\s+lines", text, 0)

        hitl_tier    = _RISK_TO_TIER.get(risk_label, "PROMPT")
        risk_entropy = round(risk_score / 100.0, 4)

        return ColonyState(
            risk_score=risk_score,
            risk_label=risk_label,
            hitl_tier=hitl_tier,
            risk_entropy=risk_entropy,
            secrets_count=secrets,
            duplicates_count=dupes,
            unused_imports=unused,
            total_lines=lines,
            report_path=str(self.report_path),
        )

    # ── Hermes integration ─────────────────────────────────────────────────

    def _maybe_emit_hermes(self, state: ColonyState) -> None:
        if self._last_score is None:
            delta = state.risk_score
        else:
            delta = abs(state.risk_score - self._last_score)

        if delta >= _DELTA_THRESHOLD:
            self._emit_hermes(state, delta)

    def _emit_hermes(self, state: ColonyState, delta: float) -> None:
        try:
            from control_plane.infra.hermes_bridge import HermesBus
            bus = HermesBus()
            bus.publish("colony.risk", {
                "risk_score":   state.risk_score,
                "risk_label":   state.risk_label,
                "hitl_tier":    state.hitl_tier,
                "risk_entropy": state.risk_entropy,
                "secrets":      state.secrets_count,
                "delta":        delta,
                "report_path":  state.report_path,
            })
            log.info("[COLONY_NEXUS] Hermes colony.risk event fired (delta=%.1f)", delta)
        except Exception as exc:
            log.debug("[COLONY_NEXUS] Hermes unavailable: %s", exc)

    # ── Helpers ────────────────────────────────────────────────────────────

    @staticmethod
    def _match_float(pattern: str, text: str, default: float) -> float:
        m = re.search(pattern, text)
        if m:
            try:
                return float(m.group(1).replace(",", ""))
            except ValueError:
                pass
        return default

    @staticmethod
    def _match_int(pattern: str, text: str, default: int) -> int:
        m = re.search(pattern, text)
        if m:
            try:
                return int(m.group(1).replace(",", ""))
            except ValueError:
                pass
        return default

    @staticmethod
    def _match_str(pattern: str, text: str, default: str) -> str:
        m = re.search(pattern, text)
        return m.group(1) if m else default
