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

    # Live connector value ("Verified Live" / Sovereign_Workspace). The roster
    # UUID 8c656cfa-... is reused across several knights and does not identify
    # this knight's notebook, so the connector — not the roster copy — is the
    # source of truth here.
    assert module.KNIGHT_NOTEBOOKS["SIR_CODEX"] == "05f1985d-e356-45d9-85b8-d101013a90b8"
    # Same treatment: the live connector, not the AGENTS.md roster copy, is the
    # authority for a knight's CloudBrain node id.
    assert module.KNIGHT_NOTEBOOKS["INVISIONED_MARKETING"] == "e6374819-50ce-41cf-b6b3-99924ca6ab90"
    assert "marketing" in module.NOTEBOOK_DOMAIN_TAGS["INVISIONED_MARKETING"]
