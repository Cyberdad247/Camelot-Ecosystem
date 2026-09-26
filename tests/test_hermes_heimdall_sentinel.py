# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Unit tests for HERMES_PRIME & PALADIN_HEIMDALL Sentinel Integration.
"""
from __future__ import annotations

from control_plane.infra.hermes_heimdall_sentinel import HermesHeimdallSentinel

def test_paladin_heimdall_perimeter_audit(tmp_path):
    sentinel = HermesHeimdallSentinel(workspace_root=str(tmp_path))
    audit = sentinel.audit_bifrost_perimeter()
    assert audit.paladin_verdict == "HEIMDALL_PERIMETER_LOCKED"
    assert ":3001 (Express/WS)" in audit.ports_verified
    assert ":8095 (Mobile Bridge)" in audit.ports_verified
    assert audit.active_governor == "HERMES_PRIME + PALADIN_HEIMDALL"

def test_paladin_heimdall_blocks_dangerous_network_diff(tmp_path):
    sentinel = HermesHeimdallSentinel(workspace_root=str(tmp_path))
    diff = "expose express listener on 0.0.0.0 for public access"
    result = sentinel.verify_patch_as_paladin(description="Public exposure", diff=diff)
    assert not result["safe"]
    assert result["verdict"] == "HEIMDALL_Z3_BLOCK"
    assert len(result["violated"]) > 0

def test_paladin_heimdall_allows_benign_patch(tmp_path):
    sentinel = HermesHeimdallSentinel(workspace_root=str(tmp_path))
    result = sentinel.verify_patch_as_paladin(
        description="Optimize WebSocket buffer latency",
        diff="const BUFFER_SIZE = 4096;"
    )
    assert result["safe"]
    assert "PASS" in result["verdict"]
