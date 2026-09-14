# SPDX-License-Identifier: MIT
"""
Tests for Arthurian Omni Forge Harmony Runes:
- //SYNC_OMNI_FORGE_DATABASES
- //IGNITE_SPEECH_AVATAR_UI
- //LOCK_BIFROST_mTLS
- //RENDER_3D_ADAPTIVE_WORKSPACE
"""

import pytest
from control_plane.runes.runic_router import normalize_rune, route_rune, RUNIC_COMMANDS


def test_harmony_runes_present_in_table():
    assert "//SYNC_OMNI_FORGE_DATABASES" in RUNIC_COMMANDS
    assert "//IGNITE_SPEECH_AVATAR_UI" in RUNIC_COMMANDS
    assert "//LOCK_BIFROST_mTLS" in RUNIC_COMMANDS
    assert "//RENDER_3D_ADAPTIVE_WORKSPACE" in RUNIC_COMMANDS


def test_harmony_runes_normalization():
    assert normalize_rune("//sync-omni-forge") == "//SYNC_OMNI_FORGE_DATABASES"
    assert normalize_rune("$sync-omni-forge") == "//SYNC_OMNI_FORGE_DATABASES"
    assert normalize_rune("//ignite-speech-avatar") == "//IGNITE_SPEECH_AVATAR_UI"
    assert normalize_rune("$ignite-speech-avatar") == "//IGNITE_SPEECH_AVATAR_UI"
    assert normalize_rune("//lock-bifrost-mtls") == "//LOCK_BIFROST_mTLS"
    assert normalize_rune("$lock-bifrost-mtls") == "//LOCK_BIFROST_mTLS"
    assert normalize_rune("//render-3d-workspace") == "//RENDER_3D_ADAPTIVE_WORKSPACE"
    assert normalize_rune("$render-3d-workspace") == "//RENDER_3D_ADAPTIVE_WORKSPACE"


def test_sync_omni_forge_databases_dispatch():
    res = route_rune("//SYNC_OMNI_FORGE_DATABASES", context={})
    assert res.queued is True
    assert res.metadata.get("status") == "SYNCED"
    assert res.metadata.get("action") == "sync_omni_forge_databases"
    assert "details" in res.metadata


def test_ignite_speech_avatar_ui_dispatch():
    res = route_rune("//IGNITE_SPEECH_AVATAR_UI", context={})
    assert res.queued is True
    assert res.metadata.get("status") == "IGNITED"
    assert res.metadata.get("duplex_latency_budget_ms") == 100


def test_lock_bifrost_mtls_dispatch():
    res = route_rune("//LOCK_BIFROST_mTLS", context={})
    assert res.queued is True
    assert res.metadata.get("status") == "LOCKED"
    assert res.metadata.get("perimeter") == "ZERO_TRUST_mTLS_LOCKED"


def test_render_3d_adaptive_workspace_dispatch():
    res = route_rune("//RENDER_3D_ADAPTIVE_WORKSPACE", context={})
    assert res.queued is True
    assert res.metadata.get("status") == "RENDERED"
    assert res.metadata.get("renderer") == "WebGPU_Zero_Copy_Pipeline"
