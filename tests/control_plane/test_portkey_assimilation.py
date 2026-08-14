# SPDX-License-Identifier: MIT

from __future__ import annotations

from control_plane.portkey_assimilation import LOCAL_GATEWAY_URL, load_portkey_runtime_config


def test_portkey_runtime_config_defaults_to_hosted_gateway() -> None:
    config = load_portkey_runtime_config()
    gateway_config = config.gateway_config()

    assert config.base_url.endswith("/v1")
    assert gateway_config["retry"]["attempts"] == 3
    assert gateway_config["metadata"]["system"] == "camelot-os"


def test_portkey_runtime_config_can_target_local_gateway() -> None:
    config = load_portkey_runtime_config(local_gateway=True)
    assert config.base_url == LOCAL_GATEWAY_URL

