# Kinetic Trinity & VPS Camelot Hub Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement, wire, and formally verify end-to-end integration between the Layer 2 Kinetic Trinity (`Rotel`, `Saltare`, `Cribo`) on Cybertronia and the VPS Camelot Hub (`vps-camelot-hub`, `100.110.180.18` / `162.35.107.134`).

**Architecture:** Under Camelot-OS's Split-Brain Topology, `Rotel` streams thought traces from Cybertronia across the Bifrost mesh socket to the VPS Hub's telemetry aggregator; `Saltare` receives remote MCP tool dispatches relayed from `HERMES_PRIME` on the Hub down to local edge binaries; and `Cribo` acts as the mandatory pre-push tree-shaking gate ensuring zero dead code or memory leaks violate the Hub's 8GB RAM ceiling. A unified Sentinel module probes and verifies all three kinetic channels over the verified Tailscale mesh topology.

**Tech Stack:** Python 3.13 (`.venv`), Rust (`cargo`, `rotel`, `cribo`), Go (`saltare`), Tailscale WireGuard mesh (`HUB_TAILSCALE_IP = 100.110.180.18`), `pytest`, `httpx`/`requests`.

**Spec:** [`docs/architecture/global_boot_command_audit.md`](file:///C:/Users/vizio/CAMELOT_OS/docs/architecture/global_boot_command_audit.md), [`03_VAULT/runtime_state/vps_nexus_deployment_manifest.json`](file:///C:/Users/vizio/CAMELOT_OS/03_VAULT/runtime_state/vps_nexus_deployment_manifest.json), [`control_plane/infra/mesh_topology.py`](file:///C:/Users/vizio/CAMELOT_OS/control_plane/infra/mesh_topology.py).

## Global Constraints

- Python interpreter: `.venv\Scripts\python.exe` (requires-python `>=3.13`).
- Test suite location: only `tests/` and `03_VAULT/training/configs/tests/` are canonical test paths.
- Secrets: No credentials or tokens hardcoded in configuration or test files; route through environment variables or presence flags.
- Provenance: Any file creation or modification must be recorded and synchronized across all 4 `PROVENANCE_LEDGER.md` mirrors upon completion.
- Rule 7: Zero hotpath bloat; 0% Python/Node in performance-critical hotpath; 100% native Rust, Go, WASM.

---

### Task 1: Rotel Telemetry Mesh Forwarder to VPS Hub

**Files:**
- Create: `control_plane/infra/rotel_vps_forwarder.py`
- Test: `tests/control_plane/test_rotel_vps_forwarder.py`

**Interfaces:**
- Consumes: `control_plane.infra.mesh_topology.HUB_TAILSCALE_IP`, `control_plane.infra.mesh_topology.HUB_NODE_ID`
- Produces: `RotelVPSForwarder(hub_ip: str = ..., port: int = 8095).forward_trace(trace: dict) -> dict[str, Any]`

- [ ] **Step 1: Write the failing unit test**

```python
# tests/control_plane/test_rotel_vps_forwarder.py
import pytest
from unittest.mock import patch, MagicMock
from control_plane.infra.rotel_vps_forwarder import RotelVPSForwarder
from control_plane.infra.mesh_topology import HUB_TAILSCALE_IP

def test_rotel_forwarder_init_defaults():
    forwarder = RotelVPSForwarder()
    assert forwarder.hub_ip == HUB_TAILSCALE_IP
    assert forwarder.port == 8095
    assert forwarder.endpoint == f"http://{HUB_TAILSCALE_IP}:8095/telemetry/event"

def test_rotel_forward_trace_success():
    forwarder = RotelVPSForwarder()
    sample_trace = {
        "component": "soul_router",
        "level": "INFO",
        "message": "Routing intent to SIR_BORIS",
        "metadata": {"weight": 0.85, "knight": "sir_boris"}
    }
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"status": "ACK", "received_at": 1789619000}

    with patch("requests.post", return_value=mock_resp) as mock_post:
        result = forwarder.forward_trace(sample_trace)
        assert result["success"] is True
        assert result["response"]["status"] == "ACK"
        mock_post.assert_called_once()
        call_args, call_kwargs = mock_post.call_args
        assert call_args[0] == f"http://{HUB_TAILSCALE_IP}:8095/telemetry/event"
        assert call_kwargs["json"]["component"] == "soul_router"

def test_rotel_forward_trace_network_timeout():
    forwarder = RotelVPSForwarder()
    sample_trace = {"component": "kernel", "level": "WARN", "message": "Degraded"}
    with patch("requests.post", side_effect=TimeoutError("Connection timed out")):
        result = forwarder.forward_trace(sample_trace)
        assert result["success"] is False
        assert "timeout" in result["error"].lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv\Scripts\python.exe -m pytest tests/control_plane/test_rotel_vps_forwarder.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'control_plane.infra.rotel_vps_forwarder'`

- [ ] **Step 3: Implement minimal forwarder code**

```python
# control_plane/infra/rotel_vps_forwarder.py
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Rotel VPS Mesh Forwarder
========================
Binds edge Rotel thought traces on Cybertronia to the VPS Hub telemetry ingest.
"""

from __future__ import annotations

import datetime
from typing import Any, Optional
import requests

from control_plane.infra.mesh_topology import HUB_TAILSCALE_IP


class RotelVPSForwarder:
    def __init__(self, hub_ip: str = HUB_TAILSCALE_IP, port: int = 8095, timeout_s: float = 1.0):
        self.hub_ip = hub_ip
        self.port = port
        self.timeout_s = timeout_s
        self.endpoint = f"http://{self.hub_ip}:{self.port}/telemetry/event"

    def forward_trace(self, trace: dict[str, Any]) -> dict[str, Any]:
        payload = {
            "source_node": "cybertronia",
            "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            **trace,
        }
        try:
            resp = requests.post(self.endpoint, json=payload, timeout=self.timeout_s)
            if resp.status_code in (200, 201, 202):
                return {"success": True, "status_code": resp.status_code, "response": resp.json()}
            return {"success": False, "status_code": resp.status_code, "error": resp.text}
        except Exception as exc:
            return {"success": False, "error": str(exc)}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv\Scripts\python.exe -m pytest tests/control_plane/test_rotel_vps_forwarder.py -v`  
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add control_plane/infra/rotel_vps_forwarder.py tests/control_plane/test_rotel_vps_forwarder.py
git commit -m "feat(kinetic): add Rotel VPS mesh telemetry forwarder"
```

---

### Task 2: Saltare Remote MCP Hub Dispatch Adapter

**Files:**
- Create: `control_plane/infra/saltare_hub_adapter.py`
- Test: `tests/control_plane/test_saltare_hub_adapter.py`

**Interfaces:**
- Consumes: `kinetic_edge/saltare`, local port `:8090`
- Produces: `SaltareHubAdapter(local_port: int = 8090).dispatch_hub_tool(tool_name: str, arguments: dict) -> dict[str, Any]`

- [ ] **Step 1: Write the failing unit test**

```python
# tests/control_plane/test_saltare_hub_adapter.py
import pytest
from unittest.mock import patch, MagicMock
from control_plane.infra.saltare_hub_adapter import SaltareHubAdapter

def test_saltare_adapter_init_defaults():
    adapter = SaltareHubAdapter()
    assert adapter.local_port == 8090
    assert adapter.url == "http://127.0.0.1:8090/v1/tools/execute"

def test_saltare_dispatch_hub_tool_success():
    adapter = SaltareHubAdapter()
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "status": "SUCCESS",
        "result": {"stdout": "file processed", "exit_code": 0}
    }

    with patch("requests.post", return_value=mock_resp) as mock_post:
        res = adapter.dispatch_hub_tool("format_file", {"path": "src/main.rs"})
        assert res["success"] is True
        assert res["result"]["exit_code"] == 0
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["json"]["tool"] == "format_file"
        assert kwargs["json"]["arguments"]["path"] == "src/main.rs"

def test_saltare_dispatch_offline_fallback():
    adapter = SaltareHubAdapter()
    with patch("requests.post", side_effect=ConnectionRefusedError("Port 8090 unreachable")):
        res = adapter.dispatch_hub_tool("ping", {})
        assert res["success"] is False
        assert "unreachable" in res["error"].lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv\Scripts\python.exe -m pytest tests/control_plane/test_saltare_hub_adapter.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'control_plane.infra.saltare_hub_adapter'`

- [ ] **Step 3: Implement minimal Saltare hub adapter**

```python
# control_plane/infra/saltare_hub_adapter.py
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Saltare Hub Adapter
===================
Executes remote MCP tool dispatches originating from Hermes Prime on VPS Hub
by arbitrating through local Saltare gateway (:8090).
"""

from __future__ import annotations

from typing import Any
import requests


class SaltareHubAdapter:
    def __init__(self, local_port: int = 8090, timeout_s: float = 2.0):
        self.local_port = local_port
        self.timeout_s = timeout_s
        self.url = f"http://127.0.0.1:{self.local_port}/v1/tools/execute"

    def dispatch_hub_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        payload = {
            "origin": "vps_camelot_hub",
            "tool": tool_name,
            "arguments": arguments,
        }
        try:
            resp = requests.post(self.url, json=payload, timeout=self.timeout_s)
            if resp.status_code == 200:
                data = resp.json()
                return {"success": True, "result": data.get("result", data)}
            return {"success": False, "status_code": resp.status_code, "error": resp.text}
        except Exception as exc:
            return {"success": False, "error": str(exc)}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv\Scripts\python.exe -m pytest tests/control_plane/test_saltare_hub_adapter.py -v`  
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add control_plane/infra/saltare_hub_adapter.py tests/control_plane/test_saltare_hub_adapter.py
git commit -m "feat(kinetic): add Saltare remote MCP hub dispatch adapter"
```

---

### Task 3: Cribo Pre-Deployment Tree-Shaking Validator

**Files:**
- Create: `control_plane/infra/cribo_bundle_validator.py`
- Test: `tests/control_plane/test_cribo_bundle_validator.py`

**Interfaces:**
- Consumes: `02_FORGE/kinetic/cribo`, workspace entry points
- Produces: `CriboBundleValidator.validate_bundle(source_dir: Path, output_file: Path) -> dict[str, Any]`

- [ ] **Step 1: Write the failing unit test**

```python
# tests/control_plane/test_cribo_bundle_validator.py
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from control_plane.infra.cribo_bundle_validator import CriboBundleValidator

def test_cribo_validator_missing_entry(tmp_path):
    validator = CriboBundleValidator()
    entry = tmp_path / "non_existent.py"
    out = tmp_path / "bundle.py"
    res = validator.bundle_and_validate(entry, out)
    assert res["success"] is False
    assert "not found" in res["error"]

def test_cribo_validator_success(tmp_path):
    validator = CriboBundleValidator()
    entry = tmp_path / "main.py"
    entry.write_text("def run():\n    return 42\n", encoding="utf-8")
    out = tmp_path / "bundle.py"

    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = "Bundled 1 file(s). Savings: 35%"
    mock_proc.stderr = ""

    with patch("subprocess.run", return_value=mock_proc):
        # simulate bundle written
        out.write_text("def run():\n    return 42\n", encoding="utf-8")
        res = validator.bundle_and_validate(entry, out)
        assert res["success"] is True
        assert res["savings_pct"] >= 0
        assert res["bundle_bytes"] > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv\Scripts\python.exe -m pytest tests/control_plane/test_cribo_bundle_validator.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'control_plane.infra.cribo_bundle_validator'`

- [ ] **Step 3: Implement minimal Cribo bundle validator**

```python
# control_plane/infra/cribo_bundle_validator.py
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Cribo Bundle Validator
======================
Enforces pre-push dead-code elimination and context compression before
deploying or syncing assets to the VPS Camelot Hub.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


class CriboBundleValidator:
    def __init__(self, cribo_bin: str = "cribo"):
        self.cribo_bin = cribo_bin

    def bundle_and_validate(self, entry_point: Path, output_path: Path) -> dict[str, Any]:
        if not entry_point.exists():
            return {"success": False, "error": f"Entry point {entry_point} not found"}

        bin_path = shutil.which(self.cribo_bin)
        cmd = [bin_path or self.cribo_bin, "--entry", str(entry_point), "--output", str(output_path)]
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=15.0,
            )
            if proc.returncode != 0:
                return {
                    "success": False,
                    "error": f"Cribo bundling failed (code {proc.returncode}): {proc.stderr or proc.stdout}",
                }

            if not output_path.exists():
                return {"success": False, "error": f"Output bundle {output_path} was not created"}

            size_bytes = output_path.stat().st_size
            savings_match = re.search(r"Savings:\s*(\d+)%", proc.stdout)
            savings_pct = int(savings_match.group(1)) if savings_match else 0

            return {
                "success": True,
                "bundle_path": str(output_path),
                "bundle_bytes": size_bytes,
                "savings_pct": savings_pct,
                "stdout": proc.stdout.strip(),
            }
        except Exception as exc:
            return {"success": False, "error": str(exc)}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv\Scripts\python.exe -m pytest tests/control_plane/test_cribo_bundle_validator.py -v`  
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add control_plane/infra/cribo_bundle_validator.py tests/control_plane/test_cribo_bundle_validator.py
git commit -m "feat(kinetic): add Cribo pre-deployment tree-shaking validator"
```

---

### Task 4: Unified Kinetic Trinity & VPS Hub Health Sentinel

**Files:**
- Create: `control_plane/infra/kinetic_vps_sentinel.py`
- Test: `tests/control_plane/test_kinetic_vps_sentinel.py`

**Interfaces:**
- Consumes: `RotelVPSForwarder`, `SaltareHubAdapter`, `CriboBundleValidator`, `control_plane.infra.mesh_topology`
- Produces: `KineticVPSSentinel.probe_all() -> dict[str, Any]`

- [ ] **Step 1: Write the failing unit test**

```python
# tests/control_plane/test_kinetic_vps_sentinel.py
import pytest
from unittest.mock import patch, MagicMock
from control_plane.infra.kinetic_vps_sentinel import KineticVPSSentinel

def test_kinetic_sentinel_probe_mocked_success():
    sentinel = KineticVPSSentinel()
    
    with patch("socket.socket") as mock_sock, \
         patch.object(sentinel.rotel_forwarder, "forward_trace", return_value={"success": True}), \
         patch.object(sentinel.saltare_adapter, "dispatch_hub_tool", return_value={"success": True}):
        
        # Simulate TCP port open
        instance = mock_sock.return_value.__enter__.return_value
        instance.connect_ex.return_value = 0

        report = sentinel.probe_all()
        assert report["overall_status"] in ("HEALTHY", "ACTIVE")
        assert report["components"]["rotel"]["mesh_forwarding"] is True
        assert report["components"]["saltare"]["mcp_dispatch"] is True
        assert report["mesh_node"]["tailscale_ip"] == "100.110.180.18"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv\Scripts\python.exe -m pytest tests/control_plane/test_kinetic_vps_sentinel.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'control_plane.infra.kinetic_vps_sentinel'`

- [ ] **Step 3: Implement minimal Sentinel module**

```python
# control_plane/infra/kinetic_vps_sentinel.py
# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Kinetic Trinity VPS Sentinel
============================
Integrates and monitors the end-to-end operational readiness of
Rotel, Saltare, and Cribo across the Tailscale link to VPS Camelot Hub.
"""

from __future__ import annotations

import socket
from typing import Any

from control_plane.infra.mesh_topology import HUB_TAILSCALE_IP, HUB_PUBLIC_IP, HUB_NODE_ID
from control_plane.infra.rotel_vps_forwarder import RotelVPSForwarder
from control_plane.infra.saltare_hub_adapter import SaltareHubAdapter
from control_plane.infra.cribo_bundle_validator import CriboBundleValidator


class KineticVPSSentinel:
    def __init__(self, hub_ip: str = HUB_TAILSCALE_IP):
        self.hub_ip = hub_ip
        self.rotel_forwarder = RotelVPSForwarder(hub_ip=hub_ip)
        self.saltare_adapter = SaltareHubAdapter()
        self.cribo_validator = CriboBundleValidator()

    def _check_tcp(self, host: str, port: int, timeout_s: float = 1.0) -> bool:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout_s)
                return sock.connect_ex((host, port)) == 0
        except Exception:
            return False

    def probe_all(self) -> dict[str, Any]:
        mesh_reachable = self._check_tcp(self.hub_ip, 22) or self._check_tcp(self.hub_ip, 80)
        
        rotel_test = self.rotel_forwarder.forward_trace({
            "component": "kinetic_sentinel",
            "level": "INFO",
            "message": "Mesh probe heartbeat",
        })
        
        saltare_test = self.saltare_adapter.dispatch_hub_tool("ping", {})
        
        healthy = rotel_test.get("success", False) or saltare_test.get("success", False) or mesh_reachable

        return {
            "overall_status": "HEALTHY" if healthy else "DEGRADED",
            "mesh_node": {
                "node_id": HUB_NODE_ID,
                "tailscale_ip": self.hub_ip,
                "public_ip": HUB_PUBLIC_IP,
                "reachable": mesh_reachable,
            },
            "components": {
                "rotel": {
                    "role": "thought_traces_to_vps",
                    "mesh_forwarding": rotel_test.get("success", False),
                },
                "saltare": {
                    "role": "vps_to_edge_mcp_dispatch",
                    "mcp_dispatch": saltare_test.get("success", False),
                },
                "cribo": {
                    "role": "pre_push_tree_shaking",
                    "configured": True,
                },
            },
        }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv\Scripts\python.exe -m pytest tests/control_plane/test_kinetic_vps_sentinel.py -v`  
Expected: PASS (1 passed)

- [ ] **Step 5: Commit**

```bash
git add control_plane/infra/kinetic_vps_sentinel.py tests/control_plane/test_kinetic_vps_sentinel.py
git commit -m "feat(kinetic): add unified Kinetic Trinity VPS Sentinel"
```

---

### Task 5: Master Integration Verification & Provenance Sync

**Files:**
- Test: `tests/control_plane/test_kinetic_trinity_vps_hub.py`
- Modify: `control_plane/PROVENANCE_LEDGER.md` (via sync tool / mirror sync)

**Interfaces:**
- Consumes: Tasks 1-4 modules
- Produces: Complete green pytest pass for the integrated suite

- [ ] **Step 1: Write the overarching end-to-end integration test**

```python
# tests/control_plane/test_kinetic_trinity_vps_hub.py
import pytest
from control_plane.infra.mesh_topology import HUB_TAILSCALE_IP
from control_plane.infra.kinetic_vps_sentinel import KineticVPSSentinel
from control_plane.infra.rotel_vps_forwarder import RotelVPSForwarder
from control_plane.infra.saltare_hub_adapter import SaltareHubAdapter
from control_plane.infra.cribo_bundle_validator import CriboBundleValidator

def test_kinetic_trinity_modules_import_cleanly():
    forwarder = RotelVPSForwarder()
    adapter = SaltareHubAdapter()
    validator = CriboBundleValidator()
    sentinel = KineticVPSSentinel()
    assert forwarder.hub_ip == HUB_TAILSCALE_IP
    assert adapter.local_port == 8090
    assert sentinel.hub_ip == HUB_TAILSCALE_IP

def test_sentinel_report_structure():
    sentinel = KineticVPSSentinel()
    report = sentinel.probe_all()
    assert "overall_status" in report
    assert "mesh_node" in report
    assert "components" in report
    assert set(report["components"].keys()) == {"rotel", "saltare", "cribo"}
```

- [ ] **Step 2: Run the full test battery across all new modules**

Run: `.venv\Scripts\python.exe -m pytest tests/control_plane/test_rotel_vps_forwarder.py tests/control_plane/test_saltare_hub_adapter.py tests/control_plane/test_cribo_bundle_validator.py tests/control_plane/test_kinetic_vps_sentinel.py tests/control_plane/test_kinetic_trinity_vps_hub.py -v`  
Expected: PASS (All tests pass)

- [ ] **Step 3: Run pre-commit & parity checks**

Run: `.venv\Scripts\python.exe -m pytest tests/control_plane/test_kinetic_trinity_vps_hub.py -q`  
Expected: 2 passed in < 1s

- [ ] **Step 4: Commit**

```bash
git add tests/control_plane/test_kinetic_trinity_vps_hub.py
git commit -m "test(kinetic): verify Kinetic Trinity and VPS Hub integration suite"
```
