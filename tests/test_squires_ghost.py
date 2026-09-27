"""Unit tests for GHOST squire false-positive hardening + CI fail-on-critical."""
from __future__ import annotations

from pathlib import Path

import pytest

from squires import colony
from squires.ghost import _is_readable_constant, triage
from squires.scan import scan

# 35-char body after the AIza prefix (google_api_key pattern), deliberately
# free of mock markers (no 'test'/'0000'/'1234'/'abcdef' substrings).
GOOGLE_KEY = "AIza" + "Ab9" * 11 + "Ab"
# Opaque 31-char blob — passes generic_token but fails the readable-constant cap.
OPAQUE_TOKEN = "kR7mQ2xZ9pL4wN8vT6yB3sD5fH1jG"


def _triage(tmp_path: Path, name: str, content: str):
    (tmp_path / name).write_text(content, encoding="utf-8")
    return triage(iter(scan(tmp_path)))


def test_your_private_key_placeholder_is_mock(tmp_path):
    report = _triage(
        tmp_path,
        "service_account.json",
        '{"private_key": "-----BEGIN PRIVATE KEY-----\\nYOUR_PRIVATE_KEY\\n-----END PRIVATE KEY-----\\n"}',
    )
    assert not report.critical, "YOUR_PRIVATE_KEY placeholder must not be critical"
    assert any(f.kind == "mock_secret" for f in report.flags)


def test_template_path_content_is_mock(tmp_path):
    # JS-style unquoted key so the generic_token pattern actually matches.
    report = _triage(tmp_path, "config.example.json", f'apiKey: "{OPAQUE_TOKEN}"')
    assert not report.critical, "example/template files are public by contract"
    assert any(f.kind == "mock_secret" for f in report.flags)


def test_real_google_api_key_is_critical(tmp_path):
    report = _triage(tmp_path, "app_config.py", f'API_KEY = "{GOOGLE_KEY}"\n')
    assert any(
        f.kind == "secret" and "google_api_key" in f.detail for f in report.critical
    ), "real AIza key must be flagged critical"


def test_opaque_token_is_critical(tmp_path):
    report = _triage(tmp_path, "app_config.py", f'api_key = "{OPAQUE_TOKEN}"\n')
    assert any(f.kind == "secret" and f.severity == "critical" for f in report.flags)


def test_readable_constant_downgraded_not_dropped(tmp_path):
    report = _triage(
        tmp_path,
        "approval-states.yaml",
        'requires_override_token: "CAMELOT_DASHBOARD_OPERATOR_TOKEN"\n',
    )
    assert not report.critical, "env-var names are not credentials"
    flags = [f for f in report.flags if f.kind == "token_constant"]
    assert flags and flags[0].severity == "warning", "constant stays visible as warning"


def test_single_line_pem_marker_pair_is_mock(tmp_path):
    report = _triage(
        tmp_path,
        "protocol.rs",
        'if !pem.contains("-----BEGIN PRIVATE KEY-----") || !pem.contains("-----END PRIVATE KEY-----") {\n',
    )
    assert not report.critical, "BEGIN+END on one line is a validation check, not key material"


def test_multiline_pem_private_key_is_critical(tmp_path):
    report = _triage(
        tmp_path,
        "leaked.key.txt",
        "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSj\n-----END PRIVATE KEY-----\n",
    )
    assert any(f.kind == "secret" and "private_key" in f.detail for f in report.critical)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("CAMELOT_DASHBOARD_OPERATOR_TOKEN", True),
        ("1000-EXCALIBUR-A", True),
        ("operator_request_signature_verified", True),
        ("camelot-kinetic-v300-auth-token", True),
        (OPAQUE_TOKEN, False),
        ("aB3xK9pQ7zLmN4rT8vWcY2sD5fH6jG1q", False),
    ],
)
def test_is_readable_constant(value, expected):
    assert _is_readable_constant(value) is expected


def _run_ghost(args: list[str]) -> int:
    colony._RICH = False
    try:
        colony.main(["ghost", *args])
    except SystemExit as e:
        return int(e.code or 0)
    return 0


def test_fail_on_critical_exits_2(tmp_path):
    (tmp_path / "app_config.py").write_text(f'api_key = "{OPAQUE_TOKEN}"\n', encoding="utf-8")
    assert _run_ghost([str(tmp_path), "--fail-on-critical"]) == 2


def test_fail_on_critical_clean_exits_0(tmp_path):
    (tmp_path / "app.py").write_text("value = 1\n", encoding="utf-8")
    assert _run_ghost([str(tmp_path), "--fail-on-critical"]) == 0


def test_default_ghost_exit_0_even_with_criticals(tmp_path):
    (tmp_path / "app_config.py").write_text(f'api_key = "{OPAQUE_TOKEN}"\n', encoding="utf-8")
    assert _run_ghost([str(tmp_path)]) == 0
