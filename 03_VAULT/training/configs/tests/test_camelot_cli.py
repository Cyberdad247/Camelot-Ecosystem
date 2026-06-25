"""Tests for the main camelot CLI module."""
import os
import sys
import subprocess

CAMELOT_PY = os.path.join(os.path.dirname(__file__), "..", "camelot.py")


def test_cli_help():
    result = subprocess.run([sys.executable, CAMELOT_PY, "--help"],
                          capture_output=True, text=True, timeout=10)
    assert result.returncode == 0
    assert "camelot" in result.stdout.lower()


def test_cli_knights():
    result = subprocess.run([sys.executable, CAMELOT_PY, "knights"],
                          capture_output=True, text=True, timeout=10)
    assert result.returncode == 0


def test_cli_stats():
    result = subprocess.run([sys.executable, CAMELOT_PY, "stats"],
                          capture_output=True, text=True, timeout=10)
    assert result.returncode == 0


def test_cli_history():
    result = subprocess.run([sys.executable, CAMELOT_PY, "history"],
                          capture_output=True, text=True, timeout=10)
    assert result.returncode == 0


def test_cli_bridge():
    result = subprocess.run([sys.executable, CAMELOT_PY, "bridge"],
                          capture_output=True, text=True, timeout=30)
    assert result.returncode == 0


def test_cli_exec():
    result = subprocess.run([sys.executable, CAMELOT_PY, "exec", "build a test"],
                          capture_output=True, text=True, timeout=30)
    assert result.returncode == 0


def test_sanitize_input():
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from camelot import _sanitize_input
    # Strips null bytes
    assert "\x00" not in _sanitize_input("hello\x00world")
    # Truncates long input
    assert len(_sanitize_input("x" * 5000)) == 2000
    # Preserves newlines and tabs
    assert "\n" in _sanitize_input("line1\nline2")
    assert "\t" in _sanitize_input("col1\tcol2")
