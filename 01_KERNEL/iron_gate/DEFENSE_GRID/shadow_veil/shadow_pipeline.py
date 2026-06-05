# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""Shadow Veil Pipeline — Heimdall → Hermes → Nemesis AUTO response.

Iron Gate tiers:
  AUTO:       quarantine (file), terminate (local process)
  HUMAN_GATE: counter_telemetry (hosts file) — approved=True required

Thread model: ShadowVeil.start() spawns a daemon thread running
SirHeimdall.watch(callback=_on_threat). The callback dispatches Nemesis
AUTO responses and publishes to Hermes shadow.threats.
"""
from __future__ import annotations

import logging
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

log = logging.getLogger("SHADOW_VEIL")

_CAMELOT_ROOT = Path(__file__).resolve().parents[5]


@dataclass
class ShadowStatus:
    active: bool = False
    threats_detected: int = 0
    auto_responses: int = 0
    hitl_pending: int = 0
    last_scan_at: float = 0.0
    last_threat_at: float = 0.0
    vector_count: int = 0
    critical_count: int = 0
    thread_alive: bool = False
    heimdall_ok: bool = False
    nemesis_ok: bool = False
    hermes_ok: bool = False


class ShadowVeil:
    """Heimdall→Hermes→Nemesis continuous defense pipeline.

    Usage:
        sv = ShadowVeil(repo_root=Path("."))
        sv.start()           # spawns daemon watch thread
        sv.status()          # ShadowStatus snapshot
        sv.stop()            # signals thread to exit
        sv.scan_once()       # single synchronous scan (no thread)
    """

    def __init__(
        self,
        repo_root: Optional[Path] = None,
        scan_interval: int = 360,
        hermes_enabled: bool = True,
    ) -> None:
        self._root = Path(repo_root) if repo_root else _CAMELOT_ROOT
        self._interval = scan_interval
        self._hermes_enabled = hermes_enabled
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._status = ShadowStatus()
        self._lock = threading.Lock()

        self._heimdall = self._load_heimdall()
        self._nemesis = self._load_nemesis()
        self._status.heimdall_ok = self._heimdall is not None
        self._status.nemesis_ok = self._nemesis is not None

    # ── Knight loaders ──────────────────────────────────────────────────

    def _load_heimdall(self):
        try:
            import importlib.util as _ilu
            spec = _ilu.spec_from_file_location(
                "shadow_heimdall",
                self._root / "01_KERNEL/iron_gate/DEFENSE_GRID/knights/heimdall.py",
            )
            mod = _ilu.module_from_spec(spec)
            sys.modules["shadow_heimdall"] = mod
            spec.loader.exec_module(mod)
            return mod.SirHeimdall(repo_root=self._root)
        except Exception as exc:
            log.warning("[SHADOW_VEIL] heimdall load failed: %s", exc)
            return None

    def _load_nemesis(self):
        try:
            import importlib.util as _ilu
            spec = _ilu.spec_from_file_location(
                "shadow_nemesis",
                self._root / "01_KERNEL/iron_gate/DEFENSE_GRID/knights/nemesis_prime.py",
            )
            mod = _ilu.module_from_spec(spec)
            sys.modules["shadow_nemesis"] = mod
            spec.loader.exec_module(mod)
            return mod.SirNemesisPrime()
        except Exception as exc:
            log.warning("[SHADOW_VEIL] nemesis load failed: %s", exc)
            return None

    # ── Public API ───────────────────────────────────────────────────────

    def start(self) -> None:
        """Start continuous scan in daemon thread."""
        if self._thread and self._thread.is_alive():
            log.debug("[SHADOW_VEIL] already running")
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._watch_loop, daemon=True, name="shadow-veil-watch"
        )
        self._thread.start()
        with self._lock:
            self._status.active = True
        log.info("[SHADOW_VEIL] watch thread started — interval=%ds", self._interval)

    def stop(self) -> None:
        self._stop_event.set()
        with self._lock:
            self._status.active = False
        log.info("[SHADOW_VEIL] watch thread signalled to stop")

    def scan_once(self) -> ShadowStatus:
        """Run a single synchronous scan and return updated ShadowStatus."""
        if self._heimdall is None:
            log.warning("[SHADOW_VEIL] Heimdall unavailable — scan skipped")
            return self._status
        report = self._heimdall.scan_fingerprint_vectors()
        with self._lock:
            self._status.last_scan_at = time.time()
            self._status.vector_count = len(report.vectors)
            self._status.critical_count = report.critical_count
        self._process_report(report)
        return self.status()

    def status(self) -> ShadowStatus:
        with self._lock:
            snap = ShadowStatus(
                active=self._status.active,
                threats_detected=self._status.threats_detected,
                auto_responses=self._status.auto_responses,
                hitl_pending=self._status.hitl_pending,
                last_scan_at=self._status.last_scan_at,
                last_threat_at=self._status.last_threat_at,
                vector_count=self._status.vector_count,
                critical_count=self._status.critical_count,
                thread_alive=bool(self._thread and self._thread.is_alive()),
                heimdall_ok=self._status.heimdall_ok,
                nemesis_ok=self._status.nemesis_ok,
                hermes_ok=self._status.hermes_ok,
            )
        return snap

    # ── Watch loop (daemon thread) ───────────────────────────────────────

    def _watch_loop(self) -> None:
        last_vector_count = -1
        while not self._stop_event.is_set():
            try:
                report = self._heimdall.scan_fingerprint_vectors()
                now = time.time()
                with self._lock:
                    self._status.last_scan_at = now
                    self._status.vector_count = len(report.vectors)
                    self._status.critical_count = report.critical_count

                if len(report.vectors) != last_vector_count:
                    last_vector_count = len(report.vectors)
                    self._process_report(report)
            except Exception as exc:
                log.error("[SHADOW_VEIL] watch_loop error: %s", exc)

            self._stop_event.wait(timeout=self._interval)

    # ── Threat processing ────────────────────────────────────────────────

    def _process_report(self, report) -> None:
        """Called by watch loop when vector count changes.

        Publishes to Hermes shadow.threats then dispatches Nemesis AUTO responses.
        NETWORK vectors → counter_telemetry HUMAN_GATE (approved=False, queues hitl)
        PROCESS vectors → terminate AUTO
        FILE/METADATA  → quarantine AUTO
        """
        with self._lock:
            self._status.threats_detected += 1
            self._status.last_threat_at = time.time()

        self._publish_hermes(report)

        for vec in report.vectors:
            threat = {
                "type": vec.vector_type,
                "source": vec.source,
                "severity": vec.severity,
            }
            self._dispatch_nemesis_response(threat)

    def _dispatch_nemesis_response(self, threat: dict) -> None:
        if self._nemesis is None:
            return

        vec_type = threat.get("type", "")
        source = threat.get("source", "")

        try:
            if vec_type == "PROCESS":
                pid = threat.get("pid")
                if pid:
                    self._nemesis.terminate_process(int(pid))
                    with self._lock:
                        self._status.auto_responses += 1
            elif vec_type in ("FILE", "METADATA"):
                src_path = Path(source) if source else None
                if src_path and src_path.exists():
                    self._nemesis.quarantine(src_path)
                    with self._lock:
                        self._status.auto_responses += 1
            elif vec_type == "NETWORK":
                # HUMAN_GATE — queue for operator approval, do NOT auto-execute
                result = self._nemesis.counter_telemetry(source, approved=False)
                if result.hitl_required:
                    with self._lock:
                        self._status.hitl_pending += 1
                    log.info(
                        "[SHADOW_VEIL] HITL queued for: %s — awaiting operator approval",
                        source,
                    )
        except Exception as exc:
            log.error("[SHADOW_VEIL] nemesis dispatch error: %s", exc)

    # ── Hermes integration ───────────────────────────────────────────────

    def _publish_hermes(self, report) -> None:
        if not self._hermes_enabled:
            return
        try:
            from control_plane.hermes_bridge import HermesBus
            bus = HermesBus()
            bus.publish("shadow.threats", {
                "source": "SHADOW_VEIL",
                "vector_count": len(report.vectors),
                "critical_count": report.critical_count,
                "is_clean": report.is_clean,
                "timestamp": report.timestamp,
                "vectors": [
                    {"type": v.vector_type, "source": v.source, "severity": v.severity}
                    for v in report.vectors[:20]  # cap payload size
                ],
            })
            with self._lock:
                self._status.hermes_ok = True
        except Exception as exc:
            log.debug("[SHADOW_VEIL] hermes publish failed: %s", exc)
            with self._lock:
                self._status.hermes_ok = False


# ── Singleton ─────────────────────────────────────────────────────────────────

_singleton: Optional[ShadowVeil] = None
_singleton_lock = threading.Lock()


def get_shadow_veil(repo_root: Optional[Path] = None) -> ShadowVeil:
    global _singleton
    with _singleton_lock:
        if _singleton is None:
            _singleton = ShadowVeil(repo_root=repo_root)
    return _singleton
