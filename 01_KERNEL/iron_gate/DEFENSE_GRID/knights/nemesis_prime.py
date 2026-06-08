# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
SIR_NEMESIS_PRIME v1.0 — The Reckoning
========================================
Active Defense Executor. Receives Heimdall threat signals.
Executes targeted neutralization: process termination, quarantine, counter-telemetry.

OCEAN: O=0.5 C=1.0 E=0.2 A=0.1 N=0.03
Runes: STRIKE | CONTAIN | NULLIFY
Law: "Every threat answered is a lesson taught. Every lesson taught is a fortress built."

Iron Gate compliance:
  - quarantine(): AUTO (moves file only)
  - terminate_process(): AUTO (local PID only)
  - counter_telemetry(): HUMAN_GATE (writes /etc/hosts or Windows hosts file)
"""
from __future__ import annotations

import logging
import os
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

log = logging.getLogger("SIR_NEMESIS_PRIME")

_HOSTS_PATH_WINDOWS = Path("C:/Windows/System32/drivers/etc/hosts")
_HOSTS_PATH_UNIX = Path("/etc/hosts")


@dataclass
class NeutralizeResult:
    action: str
    target: str
    success: bool
    detail: str
    hitl_required: bool = False
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class SirNemesisPrime:
    """
    L4 Active Defense Executor.

    Usage:
        nemesis = SirNemesisPrime()
        result = nemesis.quarantine("/path/to/suspicious_file.exe")
        result = nemesis.terminate_process(1234)
        result = nemesis.counter_telemetry("telemetry.evil.com")  # HUMAN_GATE
    """

    def __init__(self, quarantine_dir: Optional[Path] = None):
        self._quarantine = quarantine_dir or (
            Path(__file__).resolve().parents[5] / "CAMELOT_DefenseGrid_Quarantine"
        )
        self._quarantine.mkdir(parents=True, exist_ok=True)
        self._ledger_path = self._quarantine / "nemesis_actions.jsonl"

    # ------------------------------------------------------------------
    # AUTO actions
    # ------------------------------------------------------------------

    def quarantine(self, path: str | Path) -> NeutralizeResult:
        """Move suspicious file to quarantine directory. AUTO — no HITL required."""
        src = Path(path)
        if not src.exists():
            return NeutralizeResult(
                action="QUARANTINE", target=str(src),
                success=False, detail="File not found",
            )

        dest = self._quarantine / src.name
        # Avoid collision
        if dest.exists():
            dest = self._quarantine / f"{src.stem}_{int(datetime.now().timestamp())}{src.suffix}"

        try:
            shutil.move(str(src), str(dest))
            detail = f"Moved {src} → {dest}"
            log.warning("[NEMESIS_PRIME] QUARANTINE: %s", detail)
            result = NeutralizeResult(
                action="QUARANTINE", target=str(src), success=True, detail=detail,
            )
        except (OSError, shutil.Error) as exc:
            detail = f"Move failed: {exc}"
            log.error("[NEMESIS_PRIME] QUARANTINE FAILED: %s", detail)
            result = NeutralizeResult(
                action="QUARANTINE", target=str(src), success=False, detail=detail,
            )

        self._log_action(result)
        self._emit_hermes(result)
        return result

    def terminate_process(self, pid: int) -> NeutralizeResult:
        """Terminate a process by PID. AUTO — local PID only."""
        try:
            import psutil
            proc = psutil.Process(pid)
            name = proc.name()
            proc.terminate()
            detail = f"Terminated PID {pid} ({name})"
            log.warning("[NEMESIS_PRIME] TERMINATE: %s", detail)
            result = NeutralizeResult(
                action="TERMINATE", target=f"pid:{pid}", success=True, detail=detail,
            )
        except ImportError:
            # Fallback without psutil
            import signal
            try:
                os.kill(pid, signal.SIGTERM)
                detail = f"Sent SIGTERM to PID {pid}"
                result = NeutralizeResult(
                    action="TERMINATE", target=f"pid:{pid}", success=True, detail=detail,
                )
            except ProcessLookupError:
                result = NeutralizeResult(
                    action="TERMINATE", target=f"pid:{pid}",
                    success=False, detail=f"PID {pid} not found",
                )
        except Exception as exc:
            result = NeutralizeResult(
                action="TERMINATE", target=f"pid:{pid}",
                success=False, detail=str(exc),
            )

        self._log_action(result)
        self._emit_hermes(result)
        return result

    # ------------------------------------------------------------------
    # HUMAN_GATE actions
    # ------------------------------------------------------------------

    def counter_telemetry(self, endpoint: str,
                           approved: bool = False) -> NeutralizeResult:
        """Block telemetry endpoint via hosts file amendment.

        REQUIRES approved=True (HUMAN_GATE). Never auto-executes.
        Without approval, returns hitl_required=True NeutralizeResult.
        """
        if not approved:
            log.info(
                "[NEMESIS_PRIME] counter_telemetry('%s') — awaiting HUMAN_GATE approval",
                endpoint,
            )
            result = NeutralizeResult(
                action="COUNTER_TELEMETRY",
                target=endpoint,
                success=False,
                detail="HUMAN_GATE required — call with approved=True after operator sign-off",
                hitl_required=True,
            )
            self._log_action(result)
            self._emit_hermes(result)
            return result

        hosts_path = (
            _HOSTS_PATH_WINDOWS if _HOSTS_PATH_WINDOWS.exists() else _HOSTS_PATH_UNIX
        )
        block_entry = f"0.0.0.0 {endpoint}  # NEMESIS_PRIME block\n"
        try:
            current = hosts_path.read_text(encoding="utf-8", errors="replace")
            if endpoint in current:
                detail = f"{endpoint} already blocked in {hosts_path}"
                success = True
            else:
                with open(hosts_path, "a", encoding="utf-8") as f:
                    f.write(block_entry)
                detail = f"Blocked {endpoint} in {hosts_path}"
                success = True
            log.warning("[NEMESIS_PRIME] COUNTER_TELEMETRY: %s", detail)
        except PermissionError:
            detail = f"Permission denied writing to {hosts_path} — run as admin"
            success = False
            log.error("[NEMESIS_PRIME] %s", detail)
        except OSError as exc:
            detail = str(exc)
            success = False

        result = NeutralizeResult(
            action="COUNTER_TELEMETRY", target=endpoint,
            success=success, detail=detail,
        )
        self._log_action(result)
        self._emit_hermes(result)
        return result

    def respond_to_threat(self, threat: dict) -> list[NeutralizeResult]:
        """Dispatch appropriate response to a Heimdall FingerprintVector threat dict."""
        results = []
        vector_type = threat.get("type", "")
        source = threat.get("source", "")

        if vector_type == "NETWORK":
            results.append(self.counter_telemetry(source, approved=False))
        elif vector_type in ("PACKAGE", "TELEMETRY"):
            log.warning("[NEMESIS_PRIME] Package threat — recommend: pip uninstall %s", source)
        elif vector_type == "PROCESS":
            pid = threat.get("pid")
            if pid:
                results.append(self.terminate_process(int(pid)))
        elif vector_type == "METADATA":
            log.info("[NEMESIS_PRIME] Metadata threat — Sir Galahad stealth_exec recommended")

        return results

    # ------------------------------------------------------------------
    # Logging + Hermes
    # ------------------------------------------------------------------

    def _log_action(self, result: NeutralizeResult) -> None:
        import json
        try:
            with open(self._ledger_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "action": result.action,
                    "target": result.target,
                    "success": result.success,
                    "detail": result.detail,
                    "hitl_required": result.hitl_required,
                    "timestamp": result.timestamp,
                }) + "\n")
        except OSError:
            pass

    def _emit_hermes(self, result: NeutralizeResult) -> None:
        try:
            from control_plane.hermes_bridge import HermesBus
            HermesBus().publish("iron_gate.alerts", {
                "source": "SIR_NEMESIS_PRIME",
                "action": result.action,
                "target": result.target,
                "success": result.success,
                "hitl_required": result.hitl_required,
                "timestamp": result.timestamp,
            })
        except ImportError:
            pass
