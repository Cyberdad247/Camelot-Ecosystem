# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""Sir Helios's autonomous NotebookLM connection guard.

NotebookLM is the dynamic main source feeding the tri-brain consumers:

1. **Local hydration L2** — ``HydrationManager`` CloudBrain bursts.
2. **WorldTree tissue mirror** — per-knight open-notebook local tissues.
3. **Hub CloudBrain broker** — ``cloudbrain://notebooklm/<workspace>/<notebook>``
   retrieval leases against the Cybertronia broker (:3015).

One stale session breaks all three silently (empty bursts, unmirrored tissue,
rejected leases). This guard lets Sir Helios verify the connection
autonomously: session-file forensics, SDK presence, and a bounded live probe.

Secret discipline: reports carry cookie NAMES, counts, and expiries only.
Cookie VALUES never enter logs, tissue, or return payloads.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_CAMELOT_ROOT = Path(__file__).resolve().parent.parent.parent

# Candidate session paths (mirrors vfs/notebooklm_client.py lookup order).
SESSION_CANDIDATES: List[Path] = [
    Path.home() / ".notebooklm" / "profiles" / "default" / "storage_state.json",
    Path.home() / ".notebooklm" / "storage_state.json",
    Path(r"C:\Users\vizio\.notebooklm\storage_state.json"),
]

LIVE_PROBE_TIMEOUT_S = 20.0
HELIOS_TISSUE_KNIGHT = "SIR_HELIO"  # hydration-canonical Helios id


def _ensure_sys_path() -> None:
    for extra in (_CAMELOT_ROOT, _CAMELOT_ROOT / "01_KERNEL", _CAMELOT_ROOT / "vfs"):
        if str(extra) not in sys.path:
            sys.path.insert(0, str(extra))


def find_session_file() -> Optional[Path]:
    """First existing NotebookLM storage_state.json, or None."""
    for candidate in SESSION_CANDIDATES:
        if candidate.is_file():
            return candidate
    return None


def inspect_session(path: Optional[Path] = None) -> Dict[str, Any]:
    """Forensic session-file inspection. Metadata only — values never leave this function."""
    target = path or find_session_file()
    if target is None:
        return {"found": False, "remediation": ".venv\\Scripts\\notebooklm login"}
    try:
        stat = target.stat()
    except OSError as exc:
        return {"found": False, "path": str(target), "error": "unreadable: %s" % exc,
                "remediation": ".venv\\Scripts\\notebooklm login"}
    report: Dict[str, Any] = {
        "found": True,
        "path": str(target),
        "bytes": stat.st_size,
        "age_hours": round((time.time() - stat.st_mtime) / 3600, 1),
    }
    try:
        state = json.loads(target.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        report["valid_json"] = False
        report["error"] = "unparseable: %s" % exc
        return report
    report["valid_json"] = True
    cookies = state.get("cookies", [])
    now = time.time()
    expired = 0
    names = []
    session_names = []
    for cookie in cookies:
        name = str(cookie.get("name", ""))
        names.append(name)
        expires = cookie.get("expires", -1)
        try:
            is_expired = float(expires) <= now
        except (TypeError, ValueError):
            is_expired = True  # session cookies without expiry are treated as suspect
        if is_expired:
            expired += 1
        if cookie.get("domain") == "notebooklm.google.com" and name in ("OSID", "__Secure-OSID", "SID", "__Secure-1PSID"):
            session_names.append(name)
    report["cookie_count"] = len(cookies)
    report["expired_cookies"] = expired
    report["cookie_names"] = sorted(set(names))
    report["notebooklm_session_cookies"] = sorted(set(session_names))
    if expired and len(cookies):
        report["remediation"] = ".venv\\Scripts\\notebooklm login"
    return report


def sdk_available() -> bool:
    """Is the real notebooklm-py SDK importable (acquisition layer present)?"""
    try:
        _ensure_sys_path()
        from notebooklm_client import NOTEBOOKLM_AVAILABLE  # noqa: PLC0415

        return bool(NOTEBOOKLM_AVAILABLE)
    except Exception:  # noqa: BLE001
        return False


def live_probe(timeout_s: float = LIVE_PROBE_TIMEOUT_S) -> Dict[str, Any]:
    """Bounded live probe: list notebooks. Read-only; never raises."""
    try:
        _ensure_sys_path()
        from notebooklm_client import list_notebooks  # noqa: PLC0415
    except Exception as exc:  # noqa: BLE001
        return {"live": False, "error": "client import failed: %s" % exc}
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(list_notebooks)
        try:
            notebooks = future.result(timeout=timeout_s)
        except Exception as exc:  # noqa: BLE001 — timeout, auth, network
            return {"live": False, "error": "%s: %s" % (type(exc).__name__, exc)}
    notebooks = notebooks or []
    return {"live": True, "notebook_count": len(notebooks)}


def tri_brain_consumers() -> Dict[str, Any]:
    """Static wiring map of the three NotebookLM consumers (no I/O)."""
    return {
        "L2_hydration": {
            "reader": "01_KERNEL/memory/hydration_manager.py HydrationManager.query_notebook",
            "needs": "live session",
        },
        "worldtree_tissue": {
            "reader": "01_KERNEL/memory/cloudbrain_connector.py _sync_open_notebook_local",
            "needs": "knight notebook registry (works offline for local mirror)",
        },
        "hub_broker": {
            "reader": "cloudbrain://notebooklm/<workspace>/<notebook> lease vs Cybertronia :3015",
            "needs": "live session + Sentinel cloudbrain:retrieve lease",
        },
    }


def _mirror_helios_tissue(status: str, summary: Dict[str, Any]) -> bool:
    """Record the verification outcome in Helios tissue (metadata only, local)."""
    try:
        _ensure_sys_path()
        from memory.cloudbrain_connector import CloudBrainConnector  # noqa: PLC0415

        cb = CloudBrainConnector(knight_id=HELIOS_TISSUE_KNIGHT)
        cb._sync_open_notebook_local(
            "notebooklm_link",
            "Helios NotebookLM link verification: %s" % status,
            json.dumps(summary, indent=2),
        )
        return True
    except Exception:  # noqa: BLE001
        return False


def verify(live: bool = True, mirror_tissue: bool = True) -> Dict[str, Any]:
    """Autonomous connection verification. Returns a JSON-safe status report."""
    session = inspect_session()
    sdk = sdk_available()
    probe: Dict[str, Any] = {"live": False, "skipped": True}
    if live and session.get("found") and session.get("valid_json") and sdk:
        probe = live_probe()
    if probe.get("live"):
        status = "CONNECTED"
    elif session.get("found") and session.get("valid_json") and sdk:
        status = "DEGRADED"
    else:
        status = "OFFLINE"
    summary = {
        "stale_session_file": bool(session.get("found")) and session.get("expired_cookies", 0) > 0,
        "sdk_present": sdk,
        "live_verified": bool(probe.get("live")),
    }
    report = {
        "action": "helios_notebooklm_verify",
        "status": status,
        "knight": "SIR_HELIOS",
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "session": session,
        "sdk_available": sdk,
        "probe": probe,
        "summary": summary,
        "tri_brain_consumers": tri_brain_consumers(),
        "remediation": session.get("remediation", ".venv\\Scripts\\notebooklm login") if status != "CONNECTED" else "",
    }
    if mirror_tissue:
        report["tissue_mirrored"] = _mirror_helios_tissue(status, summary)
    return report


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Sir Helios autonomous NotebookLM link verification")
    parser.add_argument("--offline", action="store_true", help="Skip the live probe (session-file forensics only)")
    parser.add_argument("--no-mirror", action="store_true", help="Do not mirror the outcome to Helios tissue")
    args = parser.parse_args(argv)
    report = verify(live=not args.offline, mirror_tissue=not args.no_mirror)
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "CONNECTED" else 1


if __name__ == "__main__":
    sys.exit(main())
