"""tests/test_camelot_ide_mcp_server.py — Iron-Gate-friendly tests for the
VS Code-targeted MCP server at ``bin/camelot_ide_mcp.py``.

Verifies:
  1. Tool names comply with the MCP spec regex ``^[a-zA-Z0-9_-]+$``
     (NO slashes, NO colons — Anthropic and VS Code both reject those).
  2. Each tool's ``inputSchema.type`` is ``"object"``.
  3. The path-traversal jail rejects escapes outside the workspace and
     accepts valid subpaths.
  4. The NO_RICH constant is the literal ``"1"`` so subprocess captures
     stay plain-text (otherwise Rich markup corrupts the JSON-RPC stream).
  5. ``_invoke_portable`` uses argv-list mode (no ``shell=True``).

All assertions are pure stdlib; the MCP SDK (``mcp>=1.26.0``) is imported
lazily inside ``bin.camelot_ide_mcp.main`` so it is not required at test
collection time.
"""
from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

import pytest

MCP_TOOL_NAME_RE = re.compile(r"^[a-zA-Z0-9_-]+$")


# ── 1+2: tool schemas ─────────────────────────────────────────────


def test_mcp_tool_names_match_spec():
    """Every registered tool name must satisfy the MCP regex (no slashes)."""
    from bin.camelot_ide_mcp import TOOLS

    assert TOOLS, "TOOLS list is empty"
    for t in TOOLS:
        assert MCP_TOOL_NAME_RE.match(t["name"]), (
            f"Tool name {t['name']!r} violates MCP regex ^"
            "[a-zA-Z0-9_-]+$"
        )
        assert "/" not in t["name"], f"Tool name {t['name']!r} contains a slash"


def test_mcp_tool_schemas_have_object_inputschema():
    """Every tool must declare ``inputSchema.type == 'object'``."""
    from bin.camelot_ide_mcp import TOOLS

    for t in TOOLS:
        assert "inputSchema" in t, f"Tool {t['name']!r} missing inputSchema"
        assert t["inputSchema"]["type"] == "object", (
            f"Tool {t['name']!r} inputSchema.type != object"
        )


def test_mcp_tools_count_is_four():
    """Surface should mirror the 4 portable CLI subcommands exactly."""
    from bin.camelot_ide_mcp import TOOLS

    assert len(TOOLS) == 4
    expected = {
        "camelot_omniroute",
        "camelot_knight",
        "camelot_mcp",
        "camelot_cartridge",
    }
    assert {t["name"] for t in TOOLS} == expected


# ── 3: path-traversal jail ────────────────────────────────────────


def test_jail_rejects_relative_escape(tmp_path):
    """``../../etc`` must be rejected."""
    from bin.camelot_ide_mcp import _jail_target

    with pytest.raises(ValueError, match="(?i)escap"):
        _jail_target("../../etc/passwd", tmp_path)


def test_jail_rejects_parent_relative_escape(tmp_path):
    """``../bar`` (single dotdot) must be rejected."""
    from bin.camelot_ide_mcp import _jail_target

    with pytest.raises(ValueError, match="(?i)escap"):
        _jail_target("../bar", tmp_path)


def test_jail_accepts_subpath(tmp_path):
    """A target inside the workspace is accepted and absolutized."""
    from bin.camelot_ide_mcp import _jail_target

    result = _jail_target("projects/foo", tmp_path)
    assert result.startswith(str(tmp_path.resolve()))


def test_jail_accepts_absolute_subpath(tmp_path):
    """An absolute path that lives inside the workspace is accepted."""
    from bin.camelot_ide_mcp import _jail_target

    inside = (tmp_path / "deep" / "nested").resolve()
    inside.parent.mkdir(parents=True, exist_ok=True)
    result = _jail_target(str(inside), tmp_path)
    assert Path(result).resolve() == inside


def test_jail_rejects_absolute_outside(tmp_path):
    """An absolute path outside the workspace is rejected."""
    from bin.camelot_ide_mcp import _jail_target

    outside = Path(tempfile.gettempdir()).resolve() / "totally_unrelated_camelot_jail_test"
    with pytest.raises(ValueError, match="(?i)escap"):
        _jail_target(str(outside), tmp_path)


def test_jail_rejects_empty_target(tmp_path):
    """An empty target string is rejected (defends against accidental ninja-edit)."""
    from bin.camelot_ide_mcp import _jail_target

    with pytest.raises(ValueError, match="(?i)empty"):
        _jail_target("", tmp_path)


# ── 4: NO_RICH constant ───────────────────────────────────────────


def test_no_rich_constant_is_one():
    """NO_RICH must be '1' so subprocess captures are plain text."""
    from bin.camelot_ide_mcp import NO_RICH_ENV

    assert NO_RICH_ENV == "1"


# ── 5: argv-list invocation (no shell) ────────────────────────────


def test_invoke_portable_uses_argv_list_mode(monkeypatch):
    """``_invoke_portable`` must call ``create_subprocess_exec`` with NO shell kwarg.

    The MCP SDK already enforces ``shell=False``, but we verify our wrapper
    doesn't smuggle a shell=True through ``**kwargs`` either.
    """
    import asyncio

    import bin.camelot_ide_mcp as mod

    captured: dict = {}

    class _Stub:
        returncode = 0

        async def communicate(self):
            return (b"stub-output\n", b"")

    async def _fake_exec(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return _Stub()

    monkeypatch.setattr(asyncio, "create_subprocess_exec", _fake_exec)
    out = asyncio.run(
        mod._invoke_portable(["omniroute", "--list"])
    )
    assert out == "stub-output\n"
    assert "shell" not in captured["kwargs"], (
        "argv-list mode must not pass shell=True"
    )
    # First positional arg must be the interpreter.
    assert captured["args"][0] == sys.executable


def test_invoke_portable_sets_no_rich_env(monkeypatch):
    """Subprocess env must include NO_RICH=1 + PYTHONUTF8=1."""
    import asyncio

    import bin.camelot_ide_mcp as mod

    captured: dict = {}

    class _Stub:
        returncode = 0

        async def communicate(self):
            return (b"", b"")

    async def _fake_exec(*args, **kwargs):
        captured["kwargs"] = kwargs
        return _Stub()

    monkeypatch.setattr(asyncio, "create_subprocess_exec", _fake_exec)
    asyncio.run(mod._invoke_portable(["mcp"]))
    env = captured["kwargs"].get("env", {})
    assert env.get("NO_RICH") == "1"
    assert env.get("PYTHONUTF8") == "1"


# ── 6: self-test entry point ──


def test_self_test_passes_when_invoked_from_commandline(tmp_path, monkeypatch):
    """``python bin/camelot_ide_mcp.py --self-test`` must exit 0."""
    import subprocess

    cmd = [
        sys.executable,
        str(Path(__file__).resolve().parent.parent / "bin" / "camelot_ide_mcp.py"),
        "--self-test",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, (
        f"self-test exited {result.returncode}: {result.stderr}"
    )
    assert "[OK] all 4 tools valid" in result.stderr
