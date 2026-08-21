"""Tests for the session log module (control_plane.cli.session_log)."""

import json
import os
import time
from pathlib import Path

from control_plane.cli.session_log import (
    MAX_LOG_AGE_DAYS,
    MAX_LOG_FILES,
    MAX_FILE_SIZE_BYTES,
    TRUNCATE_KEEP_BYTES,
    _truncate_file,
    get_log_path,
    get_session_id,
    log_command_error,
    log_raw_entry,
    reset_session,
)


class TestSessionLogBasics:
    """Core session log mechanics."""

    def setup_method(self):
        """Reset session state before each test."""
        reset_session()

    def teardown_method(self):
        """Clean up any created log files."""
        path = get_log_path()
        if path and path.exists():
            path.unlink()

    def test_session_id_format(self):
        """Session IDs follow the expected naming pattern."""
        sid = get_session_id()
        assert sid.startswith("session_")
        parts = sid.split("_")
        assert len(parts) == 4  # session, date, time, pid

    def test_reset_session_returns_new_id(self):
        """reset_session() returns a fresh session ID."""
        sid1 = get_session_id()
        sid2 = reset_session()
        assert sid1 != sid2

    def test_log_creates_file(self):
        """Logging an error creates the JSONL file."""
        path = log_command_error("test_cmd", ValueError("boom"))
        assert path.exists()
        assert path.suffix == ".jsonl"

    def test_log_entry_is_valid_jsonl(self):
        """Each line in the log file is valid JSON."""
        log_command_error("cmd_a", RuntimeError("fail_a"))
        log_command_error("cmd_b", TypeError("fail_b"))
        path = get_log_path()
        lines = path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 2
        for line in lines:
            entry = json.loads(line)
            assert "ts" in entry
            assert "session_id" in entry
            assert "command" in entry
            assert "error_type" in entry
            assert "error_msg" in entry
            assert "traceback" in entry

    def test_log_entry_content(self):
        """Logged entries contain the correct error details."""
        exc = ValueError("bad value")
        entry_path = log_command_error("deploy", exc, context={"knight": "sir_codex"}, user_input="/deploy prod")
        line = Path(entry_path).read_text(encoding="utf-8").strip()
        entry = json.loads(line)
        assert entry["command"] == "deploy"
        assert entry["error_type"] == "ValueError"
        assert entry["error_msg"] == "bad value"
        assert entry["context"]["knight"] == "sir_codex"
        assert entry["user_input"] == "/deploy prod"
        assert "ValueError" in entry["traceback"]

    def test_log_raw_entry(self):
        """log_raw_entry writes arbitrary dicts."""
        log_raw_entry({"event": "test_event", "detail": "hello"})
        path = get_log_path()
        entry = json.loads(path.read_text(encoding="utf-8").strip())
        assert entry["event"] == "test_event"
        assert entry["detail"] == "hello"
        assert "ts" in entry
        assert "session_id" in entry

    def test_multiple_sessions_are_isolated(self):
        """Each session gets its own log file."""
        log_command_error("cmd1", ValueError("a"))
        path1 = get_log_path()

        reset_session()
        log_command_error("cmd2", ValueError("b"))
        path2 = get_log_path()

        assert path1 != path2
        assert path1.exists()
        assert path2.exists()

    def test_no_file_until_first_error(self):
        """No log file is created until an error occurs."""
        assert get_log_path() is None

    def test_context_and_user_input_are_optional(self):
        """Logging works without context or user_input."""
        log_command_error("bare_cmd", RuntimeError("oops"))
        path = get_log_path()
        entry = json.loads(path.read_text(encoding="utf-8").strip())
        assert "context" not in entry
        assert "user_input" not in entry


class TestSessionLogRotation:
    """Log rotation: count-based, age-based, and size-based."""

    def setup_method(self):
        reset_session()

    def teardown_method(self):
        path = get_log_path()
        if path and path.exists():
            path.unlink()

    def test_count_based_rotation(self):
        """More than MAX_LOG_FILES triggers deletion of oldest files."""
        import control_plane.cli.session_log as mod

        log_dir = mod._LOG_DIR
        log_dir.mkdir(parents=True, exist_ok=True)

        # Create MAX_LOG_FILES + 5 dummy session files
        dummy_paths = []
        for i in range(MAX_LOG_FILES + 5):
            p = log_dir / f"session_20260101_000000_{i}.jsonl"
            p.write_text(json.dumps({"i": i}) + "\n")
            dummy_paths.append(p)
            # Ensure different mtimes
            os.utime(p, (1_700_000_000 + i, 1_700_000_000 + i))

        # Trigger rotation via a new session write
        reset_session()
        log_command_error("rotation_test", ValueError("trigger"))

        remaining = list(log_dir.glob("session_*.jsonl"))
        # Should be at most MAX_LOG_FILES (the rotated-out ones deleted)
        assert len(remaining) <= MAX_LOG_FILES + 1  # +1 for the new session file

        # Clean up
        for p in remaining:
            p.unlink(missing_ok=True)

    def test_age_based_rotation(self):
        """Files older than MAX_LOG_AGE_DAYS are deleted."""
        import control_plane.cli.session_log as mod

        log_dir = mod._LOG_DIR
        log_dir.mkdir(parents=True, exist_ok=True)

        old_file = log_dir / "session_20200101_000000_999.jsonl"
        old_file.write_text("old\n")
        # Set mtime to 60 days ago
        old_time = time.time() - (MAX_LOG_AGE_DAYS + 30) * 86400
        os.utime(old_file, (old_time, old_time))

        reset_session()
        log_command_error("age_test", ValueError("trigger"))

        assert not old_file.exists()

        # Clean up
        path = get_log_path()
        if path and path.exists():
            path.unlink()

    def test_truncate_file(self):
        """_truncate_file keeps last TRUNCATE_KEEP_BYTES and adds marker."""
        import control_plane.cli.session_log as mod

        log_dir = mod._LOG_DIR
        log_dir.mkdir(parents=True, exist_ok=True)

        big_file = log_dir / "session_big.jsonl"
        content = "x" * (MAX_FILE_SIZE_BYTES + 1000)
        big_file.write_text(content)

        _truncate_file(big_file)

        size = big_file.stat().st_size
        # Should be marker + truncated content, well under original
        assert size < MAX_FILE_SIZE_BYTES
        # Should be roughly TRUNCATE_KEEP_BYTES + marker overhead
        assert size > TRUNCATE_KEEP_BYTES // 2

        with open(big_file, encoding="utf-8") as f:
            first_line = f.readline()
        marker = json.loads(first_line)
        assert marker["event"] == "truncated"
        assert marker["original_bytes"] > MAX_FILE_SIZE_BYTES

        big_file.unlink(missing_ok=True)

    def test_rotation_runs_once_per_session(self):
        """Rotation only runs once per session (not on every write)."""
        import control_plane.cli.session_log as mod

        # Ensure rotation flag is reset
        reset_session()
        assert mod._rotation_done is False

        log_command_error("first_write", ValueError("a"))
        assert mod._rotation_done is True

        # Second write should not re-trigger rotation
        # (we just verify the flag stays True)
        log_command_error("second_write", ValueError("b"))
        assert mod._rotation_done is True


class TestSessionLogIntegration:
    """Verify the shell's error boundaries write to the session log."""

    def setup_method(self):
        reset_session()

    def teardown_method(self):
        path = get_log_path()
        if path and path.exists():
            path.unlink()

    def test_run_command_logs_error(self):
        """_run_command logs errors to the session log."""
        from control_plane.cli.shell import _run_command

        def bad_fn():
            raise RuntimeError("intentional test error")

        _run_command("test_bad", bad_fn, json_mode=False)
        path = get_log_path()
        assert path is not None
        entry = json.loads(path.read_text(encoding="utf-8").strip())
        assert entry["command"] == "test_bad"
        assert entry["error_type"] == "RuntimeError"
        assert entry["error_msg"] == "intentional test error"

    def test_run_async_command_logs_error(self):
        """_run_async_command logs errors to the session log."""
        from control_plane.cli.shell import _run_async_command

        async def bad_coro():
            raise TypeError("async oops")

        _run_async_command("test_async_bad", bad_coro, json_mode=False)
        path = get_log_path()
        assert path is not None
        entry = json.loads(path.read_text(encoding="utf-8").strip())
        assert entry["command"] == "test_async_bad"
        assert entry["error_type"] == "TypeError"

    def test_run_command_success_does_not_create_log(self):
        """_run_command success does not write to the session log."""
        from control_plane.cli.shell import _run_command

        def good_fn():
            return {"ok": True}

        _run_command("test_good", good_fn, json_mode=False)
        # No log file should exist since no error occurred
        assert get_log_path() is None
