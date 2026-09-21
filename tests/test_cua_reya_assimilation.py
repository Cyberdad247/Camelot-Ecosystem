# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""Tests for CUA (Computer-Use Agent) & REYA Fabric Assimilation.
==============================================================
Validates:
1. Coordinate normalization and denormalization across Desktop and Mobile viewports.
2. CUA action primitives (click, move, drag, scroll, type, key, hotkey).
3. Screen capture and state diff verification.
4. S1 fast reflex macro chain execution.
5. Sir Sentinel capability lease protection (bounds, red zones, action limits).
6. REYA Fabric layer integration with dynamic Knight voice interchange.
7. Runic router //CUA dispatch.
"""

from __future__ import annotations

import pytest
from pathlib import Path
import sys

import importlib.util

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Load cua_driver_bridge
_cua_path = REPO_ROOT / "02_FORGE" / "assimilation" / "cua" / "cua_driver_bridge.py"
_cua_spec = importlib.util.spec_from_file_location("cua_driver_bridge", str(_cua_path))
assert _cua_spec is not None and _cua_spec.loader is not None
_cua_mod = importlib.util.module_from_spec(_cua_spec)
sys.modules["cua_driver_bridge"] = _cua_mod
_cua_spec.loader.exec_module(_cua_mod)

CuaDriverBridge = _cua_mod.CuaDriverBridge
DeviceViewport = _cua_mod.DeviceViewport
SentinelLease = _cua_mod.SentinelLease
SentinelViolationError = _cua_mod.SentinelViolationError
STANDARD_VIEWPORTS = _cua_mod.STANDARD_VIEWPORTS
get_cua_driver = _cua_mod.get_cua_driver

# Load reya_fabric_layer
_reya_path = REPO_ROOT / "02_FORGE" / "assimilation" / "reya" / "reya_fabric_layer.py"
_reya_spec = importlib.util.spec_from_file_location("reya_fabric_layer", str(_reya_path))
assert _reya_spec is not None and _reya_spec.loader is not None
_reya_mod = importlib.util.module_from_spec(_reya_spec)
sys.modules["reya_fabric_layer"] = _reya_mod
_reya_spec.loader.exec_module(_reya_mod)

ReyaUniversalFabric = _reya_mod.ReyaUniversalFabric
get_reya_fabric = _reya_mod.get_reya_fabric

from control_plane.runes.runic_router import route_rune


class TestCuaDriverBridge:
    def test_viewport_coordinate_resolution(self):
        driver = CuaDriverBridge(default_device="desktop")
        # 1920x1080
        px, py = driver.denormalize_coordinate(0.5, 0.5)
        assert px == 960
        assert py == 540

        nx, ny = driver.normalize_coordinate(960, 540)
        assert pytest.approx(nx, 0.001) == 0.5
        assert pytest.approx(ny, 0.001) == 0.5

        # S26 Ultra (1440x3120)
        s26_vp = STANDARD_VIEWPORTS["mobile_s26_ultra"]
        driver.set_viewport(s26_vp)
        spx, spy = driver.denormalize_coordinate(0.5, 0.5)
        assert spx == 720
        assert spy == 1560

    def test_mouse_primitives(self):
        driver = CuaDriverBridge(default_device="desktop", simulated=True)
        # Click
        clk = driver.mouse_click(0.2, 0.8, button="left", clicks=1)
        assert clk["status"] == "SUCCESS"
        assert clk["physical_coords"] == (384, 864)

        # Move
        mv = driver.mouse_move(0.1, 0.9)
        assert mv["status"] == "SUCCESS"
        assert mv["physical_coords"] == (192, 972)

        # Drag
        drg = driver.mouse_drag(0.1, 0.1, 0.5, 0.5)
        assert drg["status"] == "SUCCESS"
        assert drg["start_physical"] == (192, 108)
        assert drg["end_physical"] == (960, 540)

        # Scroll
        sc = driver.mouse_scroll(dx=0, dy=-240)
        assert sc["status"] == "SUCCESS"
        assert sc["dy"] == -240

    def test_keyboard_primitives(self):
        driver = CuaDriverBridge(default_device="desktop", simulated=True)
        # Type
        kb = driver.keyboard_type("test_secret", delay_ms=5)
        assert kb["status"] == "SUCCESS"
        assert kb["char_count"] == 11
        assert "***" in kb["masked_preview"]

        # Key press
        kp = driver.key_press("Return")
        assert kp["status"] == "SUCCESS"
        assert kp["key"] == "Return"

        # Hotkey
        hk = driver.hotkey(["ctrl", "shift", "p"])
        assert hk["status"] == "SUCCESS"
        assert hk["keys"] == ["ctrl", "shift", "p"]

    def test_screen_capture_and_diff(self):
        driver = CuaDriverBridge(default_device="desktop", simulated=True)
        cap1 = driver.screen_capture()
        assert cap1["status"] == "SUCCESS"
        assert "state_hash" in cap1

        cap2 = driver.screen_capture()
        assert cap2["status"] == "SUCCESS"

        # Diff verification
        diff = driver.screen_diff_verify(cap1["state_hash"], cap2["state_hash"])
        assert diff["status"] == "SUCCESS"
        assert "verified" in diff

    def test_s1_macro_chain_execution(self):
        driver = CuaDriverBridge(default_device="desktop", simulated=True)
        actions = [
            {"type": "click", "norm_x": 0.5, "norm_y": 0.5},
            {"type": "type", "text": "echo hello", "delay_ms": 2},
            {"type": "key_press", "key": "Return"},
        ]
        chain_res = driver.execute_s1_chain(actions)
        assert chain_res["status"] == "SUCCESS"
        assert chain_res["total_steps"] == 3
        assert len(chain_res["executed_steps"]) == 3
        # Sub-50ms check for rapid S1 reflex actions
        assert chain_res["average_step_ms"] < 50.0


class TestSentinelCapabilityLease:
    def test_lease_allows_valid_coordinate(self):
        lease = SentinelLease(
            lease_id="test_lease_1",
            target_device="desktop",
            allowed_rect=(0.1, 0.1, 0.9, 0.9),
            red_zones=[(0.4, 0.4, 0.6, 0.6)],
            max_actions=10,
        )
        # Coordinate inside allowed_rect and outside red_zone
        lease.validate_coordinate(0.2, 0.2)
        lease.increment()
        assert lease.actions_executed == 1

    def test_lease_blocks_out_of_bounds(self):
        lease = SentinelLease(
            lease_id="test_lease_2",
            target_device="desktop",
            allowed_rect=(0.2, 0.2, 0.8, 0.8),
        )
        with pytest.raises(SentinelViolationError, match="outside allowed bounding rect"):
            lease.validate_coordinate(0.1, 0.5)

    def test_lease_blocks_red_zone(self):
        lease = SentinelLease(
            lease_id="test_lease_3",
            target_device="desktop",
            red_zones=[(0.45, 0.45, 0.55, 0.55)],
        )
        with pytest.raises(SentinelViolationError, match="RED ZONE"):
            lease.validate_coordinate(0.5, 0.5)

    def test_lease_exhaustion(self):
        lease = SentinelLease(
            lease_id="test_lease_4",
            target_device="desktop",
            max_actions=1,
        )
        lease.increment()
        with pytest.raises(SentinelViolationError, match="exceeded max actions limit"):
            lease.validate_coordinate(0.5, 0.5)


class TestReyaUniversalFabricCua:
    def test_fabric_status_reports_cua_driver(self):
        fabric = ReyaUniversalFabric()
        status = fabric.get_status()
        assert status["cua_driver_attached"] is True
        assert status["cua_viewport"] == "cybertronia_desktop"
        assert status["status"] == "FABRIC_READY"

    def test_fabric_executes_cua_click_under_persona(self):
        fabric = ReyaUniversalFabric()
        res = fabric.execute_fabric_action(
            "cua_mouse_click",
            {"norm_x": 0.4, "norm_y": 0.6, "button": "left"},
        )
        assert res["status"] == "SUCCESS"
        assert res["speaking_name"] == "REYA (The Sovereign Companion)"
        assert "cua_driver_execution" in res["result"]
        c_exec = res["result"]["cua_driver_execution"]
        assert c_exec["physical_coords"] == (768, 648)

    def test_fabric_voice_interchange_channels_knight_for_cua(self):
        fabric = ReyaUniversalFabric()
        # Voice switch to Sir Boris
        switch_res = fabric.switch_knight("boris")
        assert switch_res["active_knight_id"] == "sir_boris"
        assert switch_res["display_name"] == "Sir Boris"

        # Execute CUA type action as Sir Boris (user approved)
        res = fabric.execute_fabric_action(
            "cua_keyboard_type",
            {"text": "pnpm build", "delay_ms": 5, "user_approved": True},
        )
        assert res["status"] == "SUCCESS"
        assert res["speaking_name"] == "Sir Boris"
        assert res["channeled_knight"] == "sir_boris"
        c_exec = res["result"]["cua_driver_execution"]
        assert c_exec["char_count"] == 10

    def test_fabric_sentinel_lease_enforcement(self):
        fabric = ReyaUniversalFabric()
        # Create strict lease with red zone
        fabric.create_sentinel_lease(
            target_device="desktop",
            allowed_rect=(0.0, 0.0, 1.0, 1.0),
            red_zones=[(0.9, 0.9, 1.0, 1.0)],  # Red zone in bottom-right corner
        )

        # Action in safe zone succeeds
        res_ok = fabric.execute_fabric_action(
            "cua_mouse_click",
            {"norm_x": 0.2, "norm_y": 0.2},
        )
        assert res_ok["status"] == "SUCCESS"

        # Action hitting red zone fails with SentinelViolationError
        with pytest.raises(SentinelViolationError, match="RED ZONE"):
            fabric.execute_fabric_action(
                "cua_mouse_click",
                {"norm_x": 0.95, "norm_y": 0.95},
            )


class TestRunicRouterCua:
    def test_route_rune_cua_click(self):
        res = route_rune("//CUA", "click 0.25 0.75")
        assert res.rune == "//CUA"
        assert res.knight == "sir_codex"
        assert res.metadata["status"] == "CUA_ACTION_EXECUTED"
        c_res = res.metadata["result"]["result"]["cua_driver_execution"]
        assert tuple(c_res["physical_coords"]) == (480, 810)

    def test_route_rune_cua_type(self):
        res = route_rune("//cua", "type cargo check")
        assert res.rune == "//CUA"
        assert res.metadata["status"] == "CUA_ACTION_EXECUTED"
        c_res = res.metadata["result"]["result"]["cua_driver_execution"]
        assert c_res["char_count"] == 11
