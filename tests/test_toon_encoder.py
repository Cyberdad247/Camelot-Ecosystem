from __future__ import annotations

import json

from control_plane.runes.toon_encoder import TOONv2Diff, compute_dict_diff


def test_compute_dict_diff():
    previous = {
        "ui": {
            "theme": "dark",
            "sidebar_open": True,
            "coords": {"x": 100, "y": 200}
        },
        "system": {
            "status": "online"
        }
    }
    
    current = {
        "ui": {
            "theme": "dark",
            "sidebar_open": False,  # changed
            "coords": {"x": 100, "y": 250}  # changed y
        },
        "system": {
            "status": "online"  # unchanged
        }
    }
    
    diff = compute_dict_diff(current, previous)
    
    assert "system" not in diff
    assert "ui" in diff
    assert diff["ui"] == {
        "sidebar_open": False,
        "coords": {"y": 250}
    }


def test_toon_v2_diff_serialization():
    previous = {"theme": "light"}
    current = {"theme": "dark", "sidebar": True}
    
    serialized = TOONv2Diff.serialize_diff(current, previous)
    data = json.loads(serialized)
    
    assert data["type"] == "TOON_v2_diff"
    assert data["diff"] == {"theme": "dark", "sidebar": True}
    assert "checksum" in data
    assert len(data["checksum"]) == 8
