from __future__ import annotations

import os
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_camelot_control_plane_ledger_status_parses() -> None:
    result = subprocess.run(
        ["cmd", "/c", "camelot --json ledger status"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert '"ledger_path"' in result.stdout
    assert '"mirrors_aligned"' in result.stdout


def test_support_mutation_requires_operator_token(monkeypatch) -> None:
    from scripts.serve_anya_dashboard import SpaHandler

    monkeypatch.delenv("CAMELOT_DASHBOARD_OPERATOR_TOKEN", raising=False)
    handler = object.__new__(SpaHandler)
    handler.headers = {}
    sent: list[tuple[dict, int]] = []

    def fake_send_json(payload: dict, status: int = 200) -> None:
        sent.append((payload, status))

    handler._send_json = fake_send_json  # type: ignore[method-assign]

    assert handler._require_operator() is False
    assert sent == [({"status": "ERROR", "error": "operator token required"}, 403)]


def test_support_mutation_accepts_matching_operator_token(monkeypatch) -> None:
    from scripts.serve_anya_dashboard import SpaHandler

    monkeypatch.setenv("CAMELOT_DASHBOARD_OPERATOR_TOKEN", "test-token")
    handler = object.__new__(SpaHandler)
    handler.headers = {"X-Camelot-Operator-Token": "test-token"}

    assert handler._operator_authorized() is True
