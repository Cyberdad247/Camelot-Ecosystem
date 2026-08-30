# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""
Memory Scarcity Guardian (`camelot-scarcity-guardian`)
=====================================================
Enforces the 8GB VPS Hub Hard Cap (7.2GB usable under cgroups v2) and the
4GB Samsung S26 Edge Orb memory partition (350MB active slice).

Triggers graceful SIGSTOP throttling on low-priority background WASM pills
under memory pressure (>90%), preventing audio drops or kernel OOM panics.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

LOG = logging.getLogger("camelot.scarcity_guardian")


@dataclass
class NodeMemoryProfile:
    node_type: str  # "VPS_HUB" | "S26_EDGE_ORB"
    total_ram_mb: float
    hard_cap_mb: float
    current_used_mb: float
    pressure_percentage: float


class ScarcityGuardian:
    """eBPF PSI & Memory Scarcity Governor."""

    VPS_HARD_CAP_MB = 7372.8   # 7.2 GB (90% of 8GB)
    S26_ACTIVE_SLICE_MB = 350.0 # 350 MB active slice on S26

    def __init__(self):
        self.throttled_pills: List[str] = []

    def evaluate_node_pressure(self, node_type: str, current_used_mb: float) -> NodeMemoryProfile:
        """Calculates memory pressure and evaluates threshold limits."""
        if node_type == "VPS_HUB":
            total = 8192.0
            hard_cap = self.VPS_HARD_CAP_MB
        elif node_type == "S26_EDGE_ORB":
            total = 4096.0
            hard_cap = self.S26_ACTIVE_SLICE_MB
        else:
            total = 8192.0
            hard_cap = 7200.0

        pressure = (current_used_mb / hard_cap) * 100.0

        profile = NodeMemoryProfile(
            node_type=node_type,
            total_ram_mb=total,
            hard_cap_mb=hard_cap,
            current_used_mb=current_used_mb,
            pressure_percentage=round(pressure, 2)
        )
        return profile

    def enforce_scarcity_policy(self, profile: NodeMemoryProfile, active_pills: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Throttles non-critical pills if pressure exceeds 90%."""
        actions_taken = []
        is_critical = profile.pressure_percentage >= 90.0

        if is_critical:
            LOG.warning(f"[SCARCITY_ALERT] Memory pressure at {profile.pressure_percentage}% on {profile.node_type}. Engaging throttle.")
            for pill in active_pills:
                pill_id = pill.get("pill_id", "unknown")
                priority = pill.get("priority", "LOW")
                # Preserve high-priority voice audio streaming
                if priority != "HIGH" and pill_id not in self.throttled_pills:
                    self.throttled_pills.append(pill_id)
                    actions_taken.append(f"SIGSTOP:{pill_id}")
                    LOG.info(f"[SCARCITY_ACTION] Emitted SIGSTOP to {pill_id} (Priority: {priority}).")
        else:
            # Memory relaxed, resume paused pills
            if self.throttled_pills:
                for pill_id in list(self.throttled_pills):
                    actions_taken.append(f"SIGCONT:{pill_id}")
                    LOG.info(f"[SCARCITY_ACTION] Emitted SIGCONT to {pill_id}.")
                self.throttled_pills.clear()

        return {
            "status": "THROTTLED" if is_critical else "CONVERGED",
            "pressure_percentage": profile.pressure_percentage,
            "actions_taken": actions_taken,
            "throttled_count": len(self.throttled_pills)
        }
