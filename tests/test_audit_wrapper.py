import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "01_KERNEL"))
import iron_gate.security.audit_wrapper as audit_wrapper  # noqa: E402


def test_run_trivy_scan_success(capsys):
    """Test successful trivy scan with no critical vulnerabilities."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "No issues found"

    with patch("subprocess.run", return_value=mock_result) as mock_run:
        audit_wrapper.run_trivy_scan("/fake/dir")

        mock_run.assert_called_once_with(
            ["trivy", "fs", "--severity", "HIGH,CRITICAL", "/fake/dir"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        captured = capsys.readouterr()
        assert "✅ [VERITAS] Scan Complete. No critical vulnerabilities found." in captured.out
        assert "No issues found" in captured.out


def test_run_trivy_scan_failure_or_issues(capsys):
    """Test trivy scan returning vulnerabilities or failing execution."""
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stdout = "Critical vulnerabilities found"
    mock_result.stderr = "Some error output"

    with patch("subprocess.run", return_value=mock_result) as mock_run:
        audit_wrapper.run_trivy_scan("/fake/dir")

        mock_run.assert_called_once()

        captured = capsys.readouterr()
        assert "⚠️ [VERITAS] Scan found potential issues or failed." in captured.out
        assert "Critical vulnerabilities found" in captured.out
        assert "Some error output" in captured.out


def test_run_trivy_scan_not_found(capsys):
    """Test when trivy is not installed (FileNotFoundError)."""
    with patch("subprocess.run", side_effect=FileNotFoundError("No such file or directory: 'trivy'")) as mock_run:
        audit_wrapper.run_trivy_scan("/fake/dir")

        mock_run.assert_called_once()

        captured = capsys.readouterr()
        assert "❌ [VERITAS] Trivy not found in PATH." in captured.out
        assert "Suggested command: docker run --rm -v" in captured.out
