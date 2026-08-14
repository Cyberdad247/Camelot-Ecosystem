# SPDX-License-Identifier: MIT

from __future__ import annotations

import importlib.util
from pathlib import Path


def test_sir_codex_has_cloudbrain_mapping() -> None:
    path = Path("01_KERNEL/memory/cloudbrain_connector.py")
    spec = importlib.util.spec_from_file_location("cloudbrain_connector_test", path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    assert module.KNIGHT_NOTEBOOKS["SIR_CODEX"] == "8c656cfa-a189-409e-a72d-07692a47f17e"
