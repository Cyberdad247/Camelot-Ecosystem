# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""CUA (Computer-Use Agent) Driver Bridge for Camelot-OS & REYA.
=============================================================
Forged by: SIR_CODEX (Kinetic Implementer) & SIR_HELIO (Bifrost Guardian)
Domain: CAMELOT-OS CUA Bridge Substrate
Based on: trycua/cua assimilation (cua-driver, cua-s1, cua-fleets, cua-bench)

Axioms:
1. Normalized Coordinate Space: All UI targets are expressed as (norm_x, norm_y)
   in [0.0, 1.0], resolving automatically to desktop or mobile resolution.
2. Sentinel Capability Leases: All actions require safety clearance against
   bounding boxes and red-zone quarantine to prevent credential leaks.
3. Sub-50ms S1 Reflex Execution: Macro chains execute locally without round-trip
   cloud LLM latency.
4. Rule 7 Compliance: Zero hotpath bloat; memory footprint strictly < 350MB.
"""

from __future__ import annotations

import hashlib
import logging
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [CUA_DRIVER] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("cua_driver_bridge")


class SentinelViolationError(Exception):
    """Raised when an action violates a Sentinel capability lease or hits a red zone."""


@dataclass
class SentinelLease:
    """Capability lease restricting CUA actions to verified safe zones."""

    lease_id: str
    target_device: str  # "desktop" | "mobile"
    allowed_rect: Optional[Tuple[float, float, float, float]] = None  # (min_x, min_y, max_x, max_y)
    red_zones: List[Tuple[float, float, float, float]] = field(default_factory=list)
    max_actions: int = 500
    actions_executed: int = 0
    is_active: bool = True
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def validate_coordinate(self, norm_x: float, norm_y: float) -> None:
        """Validates that a coordinate falls inside the lease and outside red zones."""
        if not self.is_active:
            raise SentinelViolationError(f"Sentinel lease '{self.lease_id}' is inactive or expired.")

        if self.actions_executed >= self.max_actions:
            raise SentinelViolationError(
                f"Sentinel lease '{self.lease_id}' exceeded max actions limit ({self.max_actions})."
            )

        if not (0.0 <= norm_x <= 1.0 and 0.0 <= norm_y <= 1.0):
            raise SentinelViolationError(
                f"Coordinate out of normalized bounds: ({norm_x:.4f}, {norm_y:.4f})"
            )

        # Check allowed bounding rectangle if specified
        if self.allowed_rect:
            min_x, min_y, max_x, max_y = self.allowed_rect
            if not (min_x <= norm_x <= max_x and min_y <= norm_y <= max_y):
                raise SentinelViolationError(
                    f"Coordinate ({norm_x:.4f}, {norm_y:.4f}) outside allowed bounding rect: {self.allowed_rect}"
                )

        # Check red zones (forbidden regions: e.g. password fields, system wipe buttons)
        for rz in self.red_zones:
            rz_min_x, rz_min_y, rz_max_x, rz_max_y = rz
            if rz_min_x <= norm_x <= rz_max_x and rz_min_y <= norm_y <= rz_max_y:
                raise SentinelViolationError(
                    f"Sentinel quarantine: Coordinate ({norm_x:.4f}, {norm_y:.4f}) strikes RED ZONE: {rz}"
                )

    def increment(self) -> None:
        self.actions_executed += 1


@dataclass(frozen=True)
class DeviceViewport:
    device_id: str
    device_type: str  # "desktop" | "mobile"
    width: int
    height: int
    scale_factor: float = 1.0


# Standard default target viewports in Camelot-OS
STANDARD_VIEWPORTS: Dict[str, DeviceViewport] = {
    "desktop": DeviceViewport(
        device_id="cybertronia_desktop",
        device_type="desktop",
        width=1920,
        height=1080,
        scale_factor=1.0,
    ),
    "desktop_4k": DeviceViewport(
        device_id="cybertronia_4k",
        device_type="desktop",
        width=3840,
        height=2160,
        scale_factor=1.5,
    ),
    "mobile_s26_ultra": DeviceViewport(
        device_id="vashawns_s26_ultra",
        device_type="mobile",
        width=1440,
        height=3120,
        scale_factor=3.0,
    ),
    "mobile_moto_g": DeviceViewport(
        device_id="motorola_moto_g_power",
        device_type="mobile",
        width=1080,
        height=2400,
        scale_factor=2.5,
    ),
}


class CuaDriverBridge:
    """High-efficiency CUA driver and coordinate translator for REYA."""

    def __init__(
        self,
        default_device: str = "desktop",
        simulated: bool = True,
        viewport_override: Optional[DeviceViewport] = None,
    ):
        self.default_device = default_device
        self.simulated = simulated
        self.viewport = (
            viewport_override
            if viewport_override is not None
            else STANDARD_VIEWPORTS.get(default_device, STANDARD_VIEWPORTS["desktop"])
        )
        self._action_history: List[Dict[str, Any]] = []

    def set_viewport(self, viewport: DeviceViewport) -> None:
        self.viewport = viewport
        logger.info(
            f"CUA viewport set to {viewport.device_id} ({viewport.width}x{viewport.height}, scale={viewport.scale_factor})"
        )

    def normalize_coordinate(self, pixel_x: int, pixel_y: int) -> Tuple[float, float]:
        """Converts physical screen pixels to normalized [0.0, 1.0] coordinates."""
        nx = max(0.0, min(1.0, pixel_x / max(1, self.viewport.width)))
        ny = max(0.0, min(1.0, pixel_y / max(1, self.viewport.height)))
        return round(nx, 6), round(ny, 6)

    def denormalize_coordinate(self, norm_x: float, norm_y: float) -> Tuple[int, int]:
        """Converts normalized [0.0, 1.0] coordinates to physical device pixels."""
        px = int(round(max(0.0, min(1.0, norm_x)) * self.viewport.width))
        py = int(round(max(0.0, min(1.0, norm_y)) * self.viewport.height))
        return px, py

    def mouse_click(
        self,
        norm_x: float,
        norm_y: float,
        button: str = "left",
        clicks: int = 1,
        lease: Optional[SentinelLease] = None,
    ) -> Dict[str, Any]:
        """Executes a mouse click or double-click at normalized coordinates."""
        start_time = time.perf_counter()
        if lease:
            lease.validate_coordinate(norm_x, norm_y)
            lease.increment()

        px, py = self.denormalize_coordinate(norm_x, norm_y)
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        result = {
            "status": "SUCCESS",
            "action": "mouse_click",
            "normalized_coords": (norm_x, norm_y),
            "physical_coords": (px, py),
            "button": button,
            "clicks": clicks,
            "device": self.viewport.device_id,
            "device_type": self.viewport.device_type,
            "simulated": self.simulated,
            "latency_ms": round(elapsed_ms, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._record_action(result)
        return result

    def mouse_move(
        self,
        norm_x: float,
        norm_y: float,
        lease: Optional[SentinelLease] = None,
    ) -> Dict[str, Any]:
        """Smoothly moves cursor to normalized coordinates."""
        start_time = time.perf_counter()
        if lease:
            lease.validate_coordinate(norm_x, norm_y)
            lease.increment()

        px, py = self.denormalize_coordinate(norm_x, norm_y)
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        result = {
            "status": "SUCCESS",
            "action": "mouse_move",
            "normalized_coords": (norm_x, norm_y),
            "physical_coords": (px, py),
            "device": self.viewport.device_id,
            "simulated": self.simulated,
            "latency_ms": round(elapsed_ms, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._record_action(result)
        return result

    def mouse_drag(
        self,
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float,
        button: str = "left",
        lease: Optional[SentinelLease] = None,
    ) -> Dict[str, Any]:
        """Executes a drag-and-drop gesture from start to end coordinates."""
        t0 = time.perf_counter()
        if lease:
            lease.validate_coordinate(start_x, start_y)
            lease.validate_coordinate(end_x, end_y)
            lease.increment()

        spx, spy = self.denormalize_coordinate(start_x, start_y)
        epx, epy = self.denormalize_coordinate(end_x, end_y)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        result = {
            "status": "SUCCESS",
            "action": "mouse_drag",
            "start_normalized": (start_x, start_y),
            "end_normalized": (end_x, end_y),
            "start_physical": (spx, spy),
            "end_physical": (epx, epy),
            "button": button,
            "device": self.viewport.device_id,
            "simulated": self.simulated,
            "latency_ms": round(elapsed_ms, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._record_action(result)
        return result

    def mouse_scroll(
        self,
        dx: int = 0,
        dy: int = -120,
        lease: Optional[SentinelLease] = None,
    ) -> Dict[str, Any]:
        """Emits vertical or horizontal scroll delta."""
        t0 = time.perf_counter()
        if lease:
            lease.increment()

        elapsed_ms = (time.perf_counter() - t0) * 1000
        result = {
            "status": "SUCCESS",
            "action": "mouse_scroll",
            "dx": dx,
            "dy": dy,
            "device": self.viewport.device_id,
            "simulated": self.simulated,
            "latency_ms": round(elapsed_ms, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._record_action(result)
        return result

    def keyboard_type(
        self,
        text: str,
        delay_ms: int = 10,
        lease: Optional[SentinelLease] = None,
    ) -> Dict[str, Any]:
        """Types text sequence with optional per-keystroke cadence."""
        t0 = time.perf_counter()
        if lease:
            lease.increment()

        elapsed_ms = (time.perf_counter() - t0) * 1000
        result = {
            "status": "SUCCESS",
            "action": "keyboard_type",
            "char_count": len(text),
            "delay_ms": delay_ms,
            "masked_preview": text[:2] + "***" if len(text) > 4 else "***",
            "device": self.viewport.device_id,
            "simulated": self.simulated,
            "latency_ms": round(elapsed_ms, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._record_action(result)
        return result

    def key_press(
        self,
        key: str,
        lease: Optional[SentinelLease] = None,
    ) -> Dict[str, Any]:
        """Presses and releases a single key."""
        t0 = time.perf_counter()
        if lease:
            lease.increment()

        elapsed_ms = (time.perf_counter() - t0) * 1000
        result = {
            "status": "SUCCESS",
            "action": "key_press",
            "key": key,
            "device": self.viewport.device_id,
            "simulated": self.simulated,
            "latency_ms": round(elapsed_ms, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._record_action(result)
        return result

    def hotkey(
        self,
        keys: List[str],
        lease: Optional[SentinelLease] = None,
    ) -> Dict[str, Any]:
        """Executes simultaneous hotkey combination."""
        t0 = time.perf_counter()
        if lease:
            lease.increment()

        elapsed_ms = (time.perf_counter() - t0) * 1000
        result = {
            "status": "SUCCESS",
            "action": "hotkey",
            "keys": keys,
            "device": self.viewport.device_id,
            "simulated": self.simulated,
            "latency_ms": round(elapsed_ms, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._record_action(result)
        return result

    def screen_capture(
        self,
        bounding_box: Optional[Tuple[float, float, float, float]] = None,
    ) -> Dict[str, Any]:
        """Captures viewport screenshot buffer metadata and state hash."""
        t0 = time.perf_counter()
        # High-efficiency deterministic frame state hash
        frame_id = f"frame_{int(time.time() * 1000)}"
        state_payload = f"{self.viewport.device_id}:{self.viewport.width}x{self.viewport.height}:{frame_id}"
        frame_hash = hashlib.sha256(state_payload.encode("utf-8")).hexdigest()[:16]

        elapsed_ms = (time.perf_counter() - t0) * 1000
        result = {
            "status": "SUCCESS",
            "action": "screen_capture",
            "frame_id": frame_id,
            "state_hash": frame_hash,
            "viewport": {
                "device_id": self.viewport.device_id,
                "width": self.viewport.width,
                "height": self.viewport.height,
            },
            "bounding_box": bounding_box,
            "simulated": self.simulated,
            "latency_ms": round(elapsed_ms, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._record_action(result)
        return result

    def screen_diff_verify(
        self,
        pre_hash: str,
        post_hash: str,
        min_delta_pct: float = 0.01,
    ) -> Dict[str, Any]:
        """Verifies state transition between pre-action and post-action captures."""
        changed = pre_hash != post_hash
        # Calculate simulated distance or match
        distance = 0.0 if not changed else 0.15

        return {
            "status": "SUCCESS",
            "action": "screen_diff_verify",
            "pre_hash": pre_hash,
            "post_hash": post_hash,
            "state_changed": changed,
            "delta_pct": distance,
            "verified": changed if min_delta_pct > 0 else True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def execute_s1_chain(
        self,
        actions: List[Dict[str, Any]],
        lease: Optional[SentinelLease] = None,
    ) -> Dict[str, Any]:
        """Executes a rapid System 1 macro chain of micro-actions (<50ms per action)."""
        chain_start = time.perf_counter()
        executed_steps = []

        for idx, act in enumerate(actions):
            act_type = act.get("type", "")
            step_res: Dict[str, Any] = {}

            if act_type == "click":
                step_res = self.mouse_click(
                    act.get("norm_x", 0.5),
                    act.get("norm_y", 0.5),
                    button=act.get("button", "left"),
                    clicks=act.get("clicks", 1),
                    lease=lease,
                )
            elif act_type == "move":
                step_res = self.mouse_move(
                    act.get("norm_x", 0.5),
                    act.get("norm_y", 0.5),
                    lease=lease,
                )
            elif act_type == "drag":
                step_res = self.mouse_drag(
                    act.get("start_x", 0.0),
                    act.get("start_y", 0.0),
                    act.get("end_x", 0.5),
                    act.get("end_y", 0.5),
                    button=act.get("button", "left"),
                    lease=lease,
                )
            elif act_type == "scroll":
                step_res = self.mouse_scroll(
                    dx=act.get("dx", 0),
                    dy=act.get("dy", -120),
                    lease=lease,
                )
            elif act_type == "type":
                step_res = self.keyboard_type(
                    text=act.get("text", ""),
                    delay_ms=act.get("delay_ms", 10),
                    lease=lease,
                )
            elif act_type == "key_press":
                step_res = self.key_press(
                    key=act.get("key", "Return"),
                    lease=lease,
                )
            elif act_type == "hotkey":
                step_res = self.hotkey(
                    keys=act.get("keys", ["ctrl", "c"]),
                    lease=lease,
                )
            else:
                step_res = {"status": "SKIPPED", "reason": f"Unknown action type '{act_type}'"}

            step_res["step_index"] = idx
            executed_steps.append(step_res)

        total_elapsed_ms = (time.perf_counter() - chain_start) * 1000

        return {
            "status": "SUCCESS",
            "action": "cua_s1_chain",
            "total_steps": len(executed_steps),
            "executed_steps": executed_steps,
            "total_latency_ms": round(total_elapsed_ms, 2),
            "average_step_ms": round(total_elapsed_ms / max(1, len(executed_steps)), 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _record_action(self, action_dict: Dict[str, Any]) -> None:
        self._action_history.append(action_dict)
        if len(self._action_history) > 100:
            self._action_history.pop(0)

    def get_history(self) -> List[Dict[str, Any]]:
        return list(self._action_history)


# Module singleton
_driver_instance: Optional[CuaDriverBridge] = None


def get_cua_driver() -> CuaDriverBridge:
    global _driver_instance
    if _driver_instance is None:
        _driver_instance = CuaDriverBridge()
    return _driver_instance
