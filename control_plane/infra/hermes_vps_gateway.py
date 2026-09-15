# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Camelot-OS — Hermes VPS Gateway & Remote Control
=================================================
Connects Camelot-OS local agents to the remote NousResearch Hermes Agent running
on VPS Hub KVM563 (162.35.107.134 / 100.110.180.18).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import webbrowser
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

VPS_HOST = os.environ.get("CAMELOT_VPS_HOST", "162.35.107.134")
VPS_TAILSCALE_IP = os.environ.get("CAMELOT_VPS_TS_IP", "100.110.180.18")
VPS_USER = "root"

DASHBOARD_URL = f"http://{VPS_HOST}/"
DASHBOARD_TS_URL = f"http://{VPS_TAILSCALE_IP}/"
OPENAI_GATEWAY_URL = f"http://{VPS_HOST}/api/v1"
OPENAI_GATEWAY_TS_URL = f"http://{VPS_TAILSCALE_IP}/api/v1"


def get_hermes_endpoints() -> Dict[str, str]:
    return {
        "dashboard_public": DASHBOARD_URL,
        "dashboard_tailscale": DASHBOARD_TS_URL,
        "api_gateway_public": OPENAI_GATEWAY_URL,
        "api_gateway_tailscale": OPENAI_GATEWAY_TS_URL,
        "ssh_target": f"{VPS_USER}@{VPS_HOST}",
        "container_name": "hermes",
    }


def open_hermes_dashboard(use_tailscale: bool = False) -> str:
    url = DASHBOARD_TS_URL if use_tailscale else DASHBOARD_URL
    webbrowser.open(url)
    return url


def run_hermes_cli(args: List[str] | str, timeout: int = 30) -> Dict[str, Any]:
    """Execute a Hermes CLI command inside the VPS Docker container."""
    if isinstance(args, list):
        cmd_str = " ".join(args)
    else:
        cmd_str = str(args).strip()

    remote_cmd = f"docker exec -i hermes hermes {cmd_str}"
    ssh_cmd = [
        "ssh",
        "-o", "BatchMode=yes",
        "-o", "ConnectTimeout=8",
        f"{VPS_USER}@{VPS_HOST}",
        remote_cmd,
    ]

    try:
        proc = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        return {
            "status": "SUCCESS" if proc.returncode == 0 else "ERROR",
            "returncode": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
            "command": remote_cmd,
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "TIMEOUT",
            "returncode": -1,
            "stdout": "",
            "stderr": f"Command timed out after {timeout} seconds",
            "command": remote_cmd,
        }
    except Exception as exc:
        return {
            "status": "EXCEPTION",
            "returncode": -1,
            "stdout": "",
            "stderr": str(exc),
            "command": remote_cmd,
        }


def get_hermes_status() -> Dict[str, Any]:
    """Retrieve live status of Hermes on the VPS."""
    version_res = run_hermes_cli(["--version"], timeout=8)
    config_res = run_hermes_cli(["config", "get", "model"], timeout=8)
    sessions_res = run_hermes_cli(["sessions", "list"], timeout=8)

    return {
        "status": "ONLINE" if version_res["status"] == "SUCCESS" else "DEGRADED",
        "endpoints": get_hermes_endpoints(),
        "version": version_res.get("stdout", ""),
        "model_config": config_res.get("stdout", ""),
        "recent_sessions": sessions_res.get("stdout", ""),
    }


if __name__ == "__main__":
    if "--status" in sys.argv:
        print(json.dumps(get_hermes_status(), indent=2))
    elif "--dashboard" in sys.argv:
        u = open_hermes_dashboard()
        print(f"Opened dashboard at {u}")
    elif len(sys.argv) > 1:
        args_to_run = [a for a in sys.argv[1:] if not a.startswith("--")]
        res = run_hermes_cli(args_to_run)
        print(res.get("stdout") or res.get("stderr"))
    else:
        print(json.dumps(get_hermes_status(), indent=2))
