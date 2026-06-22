from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from control_plane import runic_router
from control_plane import camelot_cli
from control_plane.system_triage import (
    CheckResult,
    TriageOptions,
    aggregate_verdict,
    run_system_triage,
)


def _check(
    name: str,
    *,
    status: str = "PASS",
    required: bool = True,
    classification: str = "confirmed",
) -> CheckResult:
    return CheckResult(
        name=name,
        stage="rapid",
        status=status,
        required=required,
        classification=classification,
        summary=name,
    )


def test_required_failure_blocks_but_optional_failure_only_degrades() -> None:
    assert aggregate_verdict([_check("boot", status="FAIL")]) == "BLOCKED"
    assert (
        aggregate_verdict([_check("boot"), _check("dashboard", status="FAIL", required=False)])
        == "DEGRADED"
    )


def test_aspirational_claim_never_blocks_release() -> None:
    verdict = aggregate_verdict(
        [_check("boot"), _check("myrddin", status="FAIL", classification="aspirational")]
    )

    assert verdict == "DEGRADED"


def test_unverified_required_check_produces_unverified_verdict() -> None:
    assert aggregate_verdict([_check("cloudbrain", status="UNVERIFIED")]) == "UNVERIFIED"


def test_deep_stage_is_skipped_after_rapid_blocker_unless_forced(tmp_path: Path) -> None:
    calls: list[str] = []

    def rapid(_context):
        calls.append("rapid")
        return _check("rapid", status="FAIL")

    def deep(_context):
        calls.append("deep")
        return _check("deep")

    result = run_system_triage(
        tmp_path,
        options=TriageOptions(mode="auto", write_reports=False),
        rapid_checks=[rapid],
        deep_checks=[deep],
    )
    assert calls == ["rapid"]
    assert result.deep_skipped is True

    calls.clear()
    run_system_triage(
        tmp_path,
        options=TriageOptions(mode="deep", force_deep=True, write_reports=False),
        rapid_checks=[rapid],
        deep_checks=[deep],
    )
    assert calls == ["rapid", "deep"]


def test_reports_are_written_as_json_and_markdown(tmp_path: Path) -> None:
    result = run_system_triage(
        tmp_path,
        options=TriageOptions(mode="rapid", timestamp="20260620T120000Z"),
        rapid_checks=[lambda _context: _check("source-of-truth")],
        deep_checks=[],
    )

    assert result.json_report is not None
    assert result.markdown_report is not None
    payload = json.loads(result.json_report.read_text(encoding="utf-8"))
    markdown = result.markdown_report.read_text(encoding="utf-8")
    assert payload["verdict"] == "GREEN"
    assert payload["checks"][0]["name"] == "source-of-truth"
    assert payload["json_report"] == str(result.json_report)
    assert payload["markdown_report"] == str(result.markdown_report)
    assert "# CAMELOT-OS System Triage" in markdown
    assert "source-of-truth" in markdown


def test_rune_routes_to_read_only_triage_command(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(runic_router, "QUEUE_FILE", tmp_path / "harness_queue.jsonl")
    monkeypatch.setattr(runic_router, "HydrationManager", None)

    result = runic_router.detect_and_route("//TRIAGE --rapid --json")

    assert result is not None
    assert result.knight == "sir_codex"
    assert result.metadata["canonical_command"] == "camelot triage --rapid --json"
    assert result.metadata["read_only"] is True


def test_cli_parser_accepts_triage_modes() -> None:
    parser = camelot_cli._build_parser()

    args = parser.parse_args(["triage", "--deep", "--force-deep", "--json"])

    assert args.command == "triage"
    assert args.deep is True
    assert args.force_deep is True
    assert args.triage_json is True


def test_cli_returns_triage_exit_code_and_json(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    triage_result = run_system_triage(
        tmp_path,
        options=TriageOptions(mode="rapid", write_reports=False),
        rapid_checks=[lambda _context: _check("boot", status="FAIL")],
        deep_checks=[],
    )
    monkeypatch.setattr(camelot_cli, "run_system_triage", lambda *_args, **_kwargs: triage_result)
    monkeypatch.setattr(sys, "argv", ["camelot", "triage", "--rapid", "--json"])

    exit_code = camelot_cli.main()

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 2
    assert output["verdict"] == "BLOCKED"


def test_kernel_banner_does_not_pollute_machine_readable_stdout() -> None:
    completed = subprocess.run(
        [sys.executable, "-c", "import importlib; importlib.import_module('01_KERNEL')"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    assert completed.returncode == 0
    assert completed.stdout == ""
    assert "Antigravity Safe I/O Active" in completed.stderr
