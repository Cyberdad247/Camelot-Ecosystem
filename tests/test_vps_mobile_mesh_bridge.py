# SPDX-License-Identifier: MIT

from control_plane.dispatch.vps_mobile_mesh_bridge import is_mesh_request_authorized


def test_mesh_bridge_rejects_missing_or_wrong_token(monkeypatch):
    monkeypatch.setenv("MESH_BRIDGE_TOKEN", "fixture-mesh-token")

    assert is_mesh_request_authorized({}) is False
    assert is_mesh_request_authorized({"x-camelot-token": "wrong"}) is False
    assert is_mesh_request_authorized({"x-camelot-token": "fixture-mesh-token"}) is True
