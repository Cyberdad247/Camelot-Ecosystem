# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""
CLARITY_CORE v1.0.0 — SQUIRE UMA_SENTRY
======================================
Unified Memory Architecture (UMA) Sentinel & Cross-Node Workload Offloader.
Exploits asymmetric memory distribution across the Camelot-OS fleet:
  - Cybertronia Host: 8,192 MB RAM (constrained, ~80% utilization)
  - Excalibur S26 Ultra: 12,288 MB LPDDR5X RAM (~6.3 GB unallocated headroom)
  - Sovereign VPS Hub: 8,192 MB RAM (~4.1 GB headroom)
Under Global Law 03, offloads memory-intensive tasks across the Excalibur mesh
under FOUNDRY_BACKGROUND mode, shielding Cybertronia's 4 GB node ceiling.
"""

from __future__ import annotations

import logging
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from squires.pagekeeper import SquirePageKeeper
from squires.tokenpress import SquireTokenPress

LOG = logging.getLogger("SquireUMASentry")


@dataclass
class FleetMemoryBalance:
    timestamp: str
    cybertronia_used_mb: float
    cybertronia_total_mb: float
    cybertronia_util_pct: float
    excalibur_free_mb: float
    excalibur_total_mb: float
    vps_free_mb: float
    vps_total_mb: float
    offload_recommended: bool
    rationale: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OffloadPlan:
    task_id: str
    action: str
    target_node: str
    target_mode: str
    estimated_ram_mb: float
    compression_enabled: bool
    approved: bool
    status: str
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SquireUMASentry:
    """Manages cross-node memory telemetry and coordinates workload offloading to Excalibur."""

    def __init__(self, home: Optional[Path] = None, pressure_threshold_pct: float = 78.0) -> None:
        self.home = home or _ROOT
        self.pressure_threshold_pct = pressure_threshold_pct
        self.pagekeeper = SquirePageKeeper()
        self.tokenpress = SquireTokenPress()

    def get_fleet_memory_balance(self) -> FleetMemoryBalance:
        """Polls memory state across Cybertronia, Excalibur (S26 Ultra), and VPS."""
        tot_mb, free_mb, used_mb, util_pct = self.pagekeeper.get_system_memory()

        # Telemetry read from cached snapshots if available
        s26_free_mb = 6290.0
        s26_total_mb = 12288.0
        vps_free_mb = 4100.0
        vps_total_mb = 8192.0

        mobile_state = self.home / "03_VAULT" / "runtime_state" / "excalibur_mobile_state.json"
        if mobile_state.exists():
            try:
                import json
                st = json.loads(mobile_state.read_text(encoding="utf-8"))
                used = float(st.get("ram_usage_mb", 3584.0))
                s26_free_mb = round(max(500.0, s26_total_mb - used), 1)
            except Exception:
                pass

        offload = util_pct >= self.pressure_threshold_pct and s26_free_mb > 2048.0
        rationale = (
            f"Cybertronia RAM at {util_pct}% (>= {self.pressure_threshold_pct}%). "
            f"Excalibur S26 Ultra has {s26_free_mb:,.0f} MB free LPDDR5X headroom."
            if offload
            else f"Cybertronia RAM stable ({util_pct}%). Local execution favored."
        )

        return FleetMemoryBalance(
            timestamp=datetime.now(timezone.utc).isoformat(),
            cybertronia_used_mb=used_mb,
            cybertronia_total_mb=tot_mb,
            cybertronia_util_pct=util_pct,
            excalibur_free_mb=s26_free_mb,
            excalibur_total_mb=s26_total_mb,
            vps_free_mb=vps_free_mb,
            vps_total_mb=vps_total_mb,
            offload_recommended=offload,
            rationale=rationale,
        )

    def plan_offload(
        self,
        task_id: str,
        action: str,
        target_module: str,
        payload: Dict[str, Any],
        estimated_ram_mb: float = 500.0,
    ) -> OffloadPlan:
        """Determines if a task should execute locally or offload to Excalibur."""
        balance = self.get_fleet_memory_balance()

        compressed_blob = self.tokenpress.compress_payload(payload)
        metrics = self.tokenpress.get_metrics(payload, compressed_blob)

        # Offload decision
        if balance.offload_recommended or estimated_ram_mb >= 750.0:
            target_node = "EXCALIBUR_S26_ULTRA"
            target_mode = "FOUNDRY_BACKGROUND"
            approved = True
            status = "OFFLOAD_APPROVED"
        else:
            target_node = "CYBERTRONIA_LOCAL"
            target_mode = "DIRECT"
            approved = False
            status = "EXECUTE_LOCAL"

        return OffloadPlan(
            task_id=task_id,
            action=action,
            target_node=target_node,
            target_mode=target_mode,
            estimated_ram_mb=estimated_ram_mb,
            compression_enabled=True,
            approved=approved,
            status=status,
            metrics={
                "payload_compression": metrics,
                "fleet_balance": balance.to_dict(),
            },
        )

    def dispatch_offload(
        self,
        task_id: str,
        action: str,
        target_module: str,
        payload: Dict[str, Any],
        estimated_ram_mb: float = 500.0,
    ) -> Dict[str, Any]:
        """Executes offload via ExcaliburMobileDispatcher or local fallback."""
        plan = self.plan_offload(task_id, action, target_module, payload, estimated_ram_mb)

        if plan.target_node == "EXCALIBUR_S26_ULTRA":
            try:
                from control_plane.dispatch.excalibur_mobile_dispatcher import (
                    ExcaliburMobileDispatcher,
                    MobileTaskRequest,
                    OperationalMode,
                )

                dispatcher = ExcaliburMobileDispatcher(home=self.home)
                req = MobileTaskRequest(
                    task_id=task_id,
                    action=action,
                    target_module=target_module,
                    payload=payload,
                    mode=OperationalMode.FOUNDRY_BACKGROUND,
                )
                res = dispatcher.dispatch_task(req)
                return {
                    "task_id": task_id,
                    "status": "OFFLOADED_SUCCESS",
                    "execution_node": res.execution_node,
                    "ram_usage_mb": res.ram_usage_mb,
                    "gpu_accelerated": res.gpu_accelerated,
                    "plan": plan.to_dict(),
                }
            except Exception as exc:
                LOG.warning(f"[UMA_SENTRY] Offload dispatch fallback: {exc}")
                return {
                    "task_id": task_id,
                    "status": "LOCAL_FALLBACK_AFTER_ERROR",
                    "execution_node": "CYBERTRONIA_LOCAL",
                    "error": str(exc),
                    "plan": plan.to_dict(),
                }

        return {
            "task_id": task_id,
            "status": "LOCAL_EXECUTION",
            "execution_node": "CYBERTRONIA_LOCAL",
            "plan": plan.to_dict(),
        }
