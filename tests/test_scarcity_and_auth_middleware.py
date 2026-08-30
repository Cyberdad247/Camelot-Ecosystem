# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.

import hashlib
import pytest
from datetime import datetime, timezone
from control_plane.infra.lease_auth_middleware import LeaseAuthMiddleware
from control_plane.infra.scarcity_guardian import ScarcityGuardian


def test_lease_auth_middleware_valid_and_tampered():
    middleware = LeaseAuthMiddleware(tenant_id="tenant_sovereign_001")
    
    lease_id = "lease_test_123"
    scope = "gmail.read"
    risk = "R4"
    now = datetime.now(timezone.utc)
    expires_at = datetime.fromtimestamp(now.timestamp() + 300, tz=timezone.utc).isoformat()
    
    # Valid Signature
    raw_msg = f"{lease_id}:tenant_sovereign_001:{scope}:{risk}:{expires_at}"
    valid_sig = hashlib.sha256(raw_msg.encode("utf-8")).hexdigest()
    
    assert middleware.verify_lease_header(lease_id, scope, risk, expires_at, valid_sig) is True
    
    # Tampered Signature
    assert middleware.verify_lease_header(lease_id, scope, risk, expires_at, "bad_sig_999") is False
    
    # Expired Lease
    expired_at = datetime.fromtimestamp(now.timestamp() - 300, tz=timezone.utc).isoformat()
    raw_expired = f"{lease_id}:tenant_sovereign_001:{scope}:{risk}:{expired_at}"
    exp_sig = hashlib.sha256(raw_expired.encode("utf-8")).hexdigest()
    assert middleware.verify_lease_header(lease_id, scope, risk, expired_at, exp_sig) is False


def test_scarcity_guardian_pressure_and_throttling():
    guardian = ScarcityGuardian()
    
    # 1. VPS Hub Normal State (5.0GB / 7.2GB cap = ~67%)
    profile_vps_normal = guardian.evaluate_node_pressure("VPS_HUB", current_used_mb=5000.0)
    assert profile_vps_normal.pressure_percentage < 90.0
    
    pills = [
        {"pill_id": "pill_audio_streamer", "priority": "HIGH"},
        {"pill_id": "pill_background_scraper", "priority": "LOW"},
        {"pill_id": "pill_heavy_indexer", "priority": "MEDIUM"}
    ]
    res_normal = guardian.enforce_scarcity_policy(profile_vps_normal, pills)
    assert res_normal["status"] == "CONVERGED"
    assert len(res_normal["actions_taken"]) == 0
    
    # 2. VPS Hub Pressure State (6.9GB / 7.2GB cap = ~93.5%)
    profile_vps_pressure = guardian.evaluate_node_pressure("VPS_HUB", current_used_mb=6900.0)
    assert profile_vps_pressure.pressure_percentage >= 90.0
    
    res_pressure = guardian.enforce_scarcity_policy(profile_vps_pressure, pills)
    assert res_pressure["status"] == "THROTTLED"
    # Audio streamer (HIGH priority) preserved, others throttled
    assert "SIGSTOP:pill_background_scraper" in res_pressure["actions_taken"]
    assert "SIGSTOP:pill_heavy_indexer" in res_pressure["actions_taken"]
    assert "SIGSTOP:pill_audio_streamer" not in res_pressure["actions_taken"]
    
    # 3. S26 Edge Orb Normal vs Slice Pressure (350MB active slice)
    profile_s26_normal = guardian.evaluate_node_pressure("S26_EDGE_ORB", current_used_mb=200.0)
    assert profile_s26_normal.pressure_percentage < 90.0
    
    profile_s26_spike = guardian.evaluate_node_pressure("S26_EDGE_ORB", current_used_mb=330.0)
    assert profile_s26_spike.pressure_percentage >= 90.0
