# SPDX-License-Identifier: MIT

from __future__ import annotations

from control_plane.versioning import VersionInfo, get_dynamic_version


def test_get_dynamic_version_returns_version_info() -> None:
    version = get_dynamic_version()
    assert isinstance(version, VersionInfo)
    assert version.label.startswith("dynamic-") or version.source == "env"

