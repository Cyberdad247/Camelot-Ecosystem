# SPDX-License-Identifier: MIT

"""TDD-first tests for `probes.exec.run` (slice #1 Task 2)."""
from control_plane.preflight.probes import exec as probe


def test_run_passes_through_exit_code_0():
    r = probe.run(["python", "-c", "print('hi')"], timeout_s=5)
    assert r.exit_code == 0
    assert "hi" in r.stdout_excerpt
    assert r.timed_out is False


def test_run_captures_nonzero_exit():
    r = probe.run(
        ["python", "-c", "import sys; sys.exit(7)"], timeout_s=5
    )
    assert r.exit_code == 7
    assert r.timed_out is False


def test_run_timeout_returns_timed_out_true():
    # 5s sleep with 1s timeout -> subprocess.TimeoutExpired surfaces here.
    r = probe.run(
        ["python", "-c", "import time; time.sleep(5)"], timeout_s=1
    )
    assert r.timed_out is True
    assert r.exit_code != 0  # killed process returns nonzero on POSIX;
                             # on Windows this may differ. See plan.
    assert r.duration_ms >= 1000


def test_run_caps_excerpts_at_4kib():
    big = "x" * 8000
    r = probe.run(
        ["python", "-c", f"print({big!r})"], timeout_s=5
    )
    # Excerpt must be capped at 4096 bytes; truncation marker added.
    encoded = r.stdout_excerpt.encode("utf-8")
    # Allow the truncation marker; the body bytes must be <= 4096.
    assert len(encoded) <= 4096 + len("\n…[truncated]\n".encode("utf-8"))
