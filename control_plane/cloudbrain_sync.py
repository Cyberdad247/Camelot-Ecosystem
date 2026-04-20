"""Best-effort Cloud Brain sync hooks for local Camelot state changes."""

from __future__ import annotations

import asyncio
import importlib.util
import os
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_notebooklm_bridge():
    bridge_path = REPO_ROOT / "03_VAULT" / "training" / "configs" / "notebooklm_bridge.py"
    spec = importlib.util.spec_from_file_location("notebooklm_bridge", bridge_path)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(f"Unable to load notebooklm bridge at {bridge_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("notebooklm_bridge", module)
    spec.loader.exec_module(module)
    return module


def _summarize_results(results: dict[str, Any], *, limit: int = 4000) -> str:
    text = str(results)
    if len(text) > limit:
        return text[:limit].rstrip() + " ...[truncated]"
    return text


def sync_after_event(
    *,
    event_type: str,
    command: str,
    results: dict[str, Any],
    enabled: bool = True,
) -> dict[str, Any]:
    """Best-effort sync of local state after a structural event.

    Never raises. Failures are returned to the caller for optional display/logging.
    """
    if not enabled:
        return {"triggered": False, "reason": "disabled"}

    try:
        os.environ.setdefault("CAMELOT_OS_HOME", str(REPO_ROOT))
        bridge = _load_notebooklm_bridge()
        summary = "\n".join(
            [
                f"Auto-sync trigger: {event_type}",
                f"Command: {command}",
                "Result summary:",
                _summarize_results(results),
            ]
        )
        payload = asyncio.run(bridge.async_sync_state(extra_summary=summary))
        return {"triggered": True, "result": payload}
    except Exception as exc:  # pragma: no cover - defensive, environment-dependent
        return {"triggered": True, "error": f"{type(exc).__name__}: {exc}"}
