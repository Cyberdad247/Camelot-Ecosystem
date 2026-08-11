# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
SIR_HEIMDALL v1.0 — The Eternal Watcher
========================================
Perimeter Guardian of CAMELOT-OS. Detects fingerprinting attempts,
surveillance hooks, telemetry leakage, and shadow threats.

OCEAN: O=0.7 C=0.99 E=0.1 A=0.3 N=0.02
Runes: VIGIL | WITNESS | WARD
Law: "What is seen cannot be unseen. What is reported cannot be denied."
"""
from __future__ import annotations

import logging
import os
import socket
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

log = logging.getLogger("SIR_HEIMDALL")

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class FingerprintVector:
    """A detected fingerprinting or surveillance vector."""
    vector_type: str      # TELEMETRY | NETWORK | METADATA | PROCESS | PACKAGE
    source: str           # what triggered the detection
    severity: str         # LOW | MEDIUM | HIGH | CRITICAL
    detail: str
    recommended_action: str


@dataclass
class WatchReport:
    vectors: list[FingerprintVector] = field(default_factory=list)
    scan_path: str = ""
    timestamp: str = ""

    @property
    def critical_count(self) -> int:
        return sum(1 for v in self.vectors if v.severity == "CRITICAL")

    @property
    def is_clean(self) -> bool:
        return len(self.vectors) == 0


# ---------------------------------------------------------------------------
# Known telemetry signatures
# ---------------------------------------------------------------------------

_TELEMETRY_PACKAGES = frozenset({
    "sentry-sdk", "bugsnag", "rollbar", "datadog", "newrelic",
    "elastic-apm", "honeybadger", "raygun", "logrocket",
    "amplitude", "mixpanel", "segment", "posthog",
})

_TELEMETRY_ENDPOINTS = frozenset({
    "telemetry.microsoft.com",
    "vortex.data.microsoft.com",
    "settings-win.data.microsoft.com",
    "dc.services.visualstudio.com",
    "o1.ingest.sentry.io",
    "api.segment.io",
    "api.mixpanel.com",
    "api2.amplitude.com",
})

_FINGERPRINT_ENV_VARS = frozenset({
    "COMPUTERNAME", "USERNAME", "USERDOMAIN",
    "HOSTNAME", "USER", "LOGNAME",
})


# ---------------------------------------------------------------------------
# Sir Heimdall
# ---------------------------------------------------------------------------

class SirHeimdall:
    """
    L4 Perimeter Guardian — scans all system vectors for fingerprinting attempts.

    Usage:
        heimdall = SirHeimdall()
        report = heimdall.scan_fingerprint_vectors()
        if not report.is_clean:
            heimdall.emit_hermes_alert(report)
    """

    def __init__(self, repo_root: Optional[Path] = None):
        self._root = repo_root or Path(__file__).resolve().parents[5]
        self._hermes_channel = "shadow.threats"

    # ------------------------------------------------------------------
    # Core scan
    # ------------------------------------------------------------------

    def scan_fingerprint_vectors(self, path: Optional[Path] = None) -> WatchReport:
        """Full perimeter scan. Returns WatchReport with all detected vectors."""
        from datetime import datetime, timezone
        scan_target = path or self._root
        vectors: list[FingerprintVector] = []

        vectors.extend(self._scan_packages())
        vectors.extend(self._scan_env_leakage())
        vectors.extend(self._scan_telemetry_imports(scan_target))
        vectors.extend(self._scan_network_endpoints())

        report = WatchReport(
            vectors=vectors,
            scan_path=str(scan_target),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        if vectors:
            log.warning(
                "[HEIMDALL] %d fingerprint vector(s) detected — %d CRITICAL",
                len(vectors), report.critical_count,
            )
        else:
            log.info("[HEIMDALL] Perimeter clear — 0 fingerprint vectors")
        return report

    # ------------------------------------------------------------------
    # Sub-scanners
    # ------------------------------------------------------------------

    def _scan_packages(self) -> list[FingerprintVector]:
        vectors = []
        try:
            result = subprocess.run(
                ["pip", "list", "--format=columns"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=15,
            )
            for line in result.stdout.splitlines()[2:]:
                pkg = line.split()[0].lower() if line.split() else ""
                if pkg in _TELEMETRY_PACKAGES:
                    vectors.append(FingerprintVector(
                        vector_type="PACKAGE",
                        source=pkg,
                        severity="HIGH",
                        detail=f"Telemetry package installed: {pkg}",
                        recommended_action=f"pip uninstall {pkg} — confirm with Sir Nemesis Prime",
                    ))
        except Exception as exc:
            log.debug("[HEIMDALL] Package scan skipped: %s", exc)
        return vectors

    def _scan_env_leakage(self) -> list[FingerprintVector]:
        vectors = []
        leaked = [v for v in _FINGERPRINT_ENV_VARS if v in os.environ]
        if leaked:
            vectors.append(FingerprintVector(
                vector_type="METADATA",
                source="os.environ",
                severity="MEDIUM",
                detail=f"Identity env vars present: {leaked}",
                recommended_action="Use SirGalahad.stealth_exec() to sanitize subprocess env",
            ))
        return vectors

    def _scan_telemetry_imports(self, root: Path) -> list[FingerprintVector]:
        vectors = []
        try:
            import subprocess as sp
            result = sp.run(
                ["grep", "-r", "--include=*.py", "-l",
                 "-e", "sentry_sdk", "-e", "bugsnag", "-e", "datadog",
                 str(root)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
            )
            for fpath in result.stdout.strip().splitlines():
                vectors.append(FingerprintVector(
                    vector_type="TELEMETRY",
                    source=fpath,
                    severity="HIGH",
                    detail=f"Telemetry import found in {fpath}",
                    recommended_action="Remove telemetry import; replace with local logging",
                ))
        except Exception:
            pass
        return vectors

    def _scan_network_endpoints(self) -> list[FingerprintVector]:
        vectors = []
        for endpoint in _TELEMETRY_ENDPOINTS:
            try:
                socket.setdefaulttimeout(1)
                addr = socket.getaddrinfo(endpoint, 443)
                if addr:
                    vectors.append(FingerprintVector(
                        vector_type="NETWORK",
                        source=endpoint,
                        severity="CRITICAL",
                        detail=f"Telemetry endpoint reachable: {endpoint}",
                        recommended_action=f"Dispatch SirNemesisPrime.counter_telemetry('{endpoint}')",
                    ))
            except (socket.gaierror, OSError):
                pass  # endpoint not reachable = good
        return vectors

    # ------------------------------------------------------------------
    # Hermes integration
    # ------------------------------------------------------------------

    def emit_hermes_alert(self, report: WatchReport) -> None:
        """Publish threat report to Hermes shadow.threats channel."""
        try:
            from control_plane.infra.hermes_bridge import HermesBus
            HermesBus().publish(self._hermes_channel, {
                "source": "SIR_HEIMDALL",
                "vectors": len(report.vectors),
                "critical": report.critical_count,
                "scan_path": report.scan_path,
                "timestamp": report.timestamp,
                "details": [
                    {"type": v.vector_type, "source": v.source, "severity": v.severity}
                    for v in report.vectors
                ],
            })
        except ImportError:
            log.warning("[HEIMDALL] Hermes bridge unavailable — alert not published")

    # ------------------------------------------------------------------
    # Continuous watch
    # ------------------------------------------------------------------

    def watch(self, callback: Optional[Callable[[WatchReport], None]] = None,
              interval_seconds: int = 360) -> None:
        """Poll-based continuous watch. Calls callback on new threats detected."""
        import time
        log.info("[HEIMDALL] Continuous watch started — interval=%ds", interval_seconds)
        last_count = 0
        while True:
            report = self.scan_fingerprint_vectors()
            if len(report.vectors) != last_count:
                last_count = len(report.vectors)
                self.emit_hermes_alert(report)
                if callback:
                    callback(report)
            time.sleep(interval_seconds)
