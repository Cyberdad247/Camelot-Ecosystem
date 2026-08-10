"""tests/test_camelot_portable_subcommands.py — coverage for the v1000 IDE/CLI
subcommands added to ``bin/camelot_portable.py``.

The four handlers (``cmd_omniroute``, ``cmd_knight``, ``cmd_mcp``,
``cmd_cartridge``) are exported by the module and can be exercised
directly with synthetic argparse.Namespace objects + a tiny console
shim.  This keeps the tests fast and avoids pulling Rich into the test
scope.
"""
from __future__ import annotations

import sys
from pathlib import Path

from bin.camelot_portable import (
    cmd_cartridge,
    cmd_knight,
    cmd_mcp,
    cmd_omniroute,
)
from tests._fixtures import CapturingConsole, make_args

# ── omniroute ─────────────────────────────────────────────────────────────────


def test_omniroute_list_prints_models_table():
    console = CapturingConsole()
    rc = cmd_omniroute(make_args(omniroute_list=True), console)
    assert rc == 0
    # At least one line was rendered
    assert console.lines


def test_omniroute_route_routes_to_a_knight():
    console = CapturingConsole()
    rc = cmd_omniroute(
        make_args(route="scaffold a hello-world Rust project"), console
    )
    # The keyword router maps {scaffold, code, build, ...} -> sir_forge.
    assert rc == 0
    assert any("Routed knight" in line for line in console.lines)
    assert any("sir_" in line for line in console.lines)


def test_omniroute_select_degrades_when_control_plane_unavailable(monkeypatch):
    """In the portable frozen binary, control_plane import fails; handler must
    degrade cleanly with rc=1 and a friendly message — not raise."""
    # PEP 451: pinning ``sys.modules[name] = None`` causes
    # ``from name import x`` to raise ``ModuleNotFoundError`` immediately,
    # which simulates frozen-binary unavailability without poisoning
    # ``sys.path`` (the handler defensively re-roots via ``sys.path.insert``).
    monkeypatch.setitem(sys.modules, "control_plane.omniroute_policies", None)
    console = CapturingConsole()
    rc = cmd_omniroute(
        make_args(select="scaffold a hello-world Rust project"), console
    )
    assert rc == 1
    assert any("unavailable" in line for line in console.lines)


def test_omniroute_no_args_returns_2():
    console = CapturingConsole()
    rc = cmd_omniroute(make_args(), console)
    # Missing subaction prints usage hint + rc=2
    assert rc == 2


# ── knight ────────────────────────────────────────────────────────────────────


def test_knight_list_prints_models_table():
    console = CapturingConsole()
    rc = cmd_knight(make_args(knight_list=True), console)
    assert rc == 0
    assert console.lines


def test_knight_invoke_unknown_knight_returns_1():
    console = CapturingConsole()
    rc = cmd_knight(
        make_args(invoke="sir_does_not_exist", prompt="hello"), console
    )
    assert rc == 1


def test_knight_invoke_without_prompt_returns_2():
    console = CapturingConsole()
    rc = cmd_knight(make_args(invoke="sir_codex", prompt=None), console)
    assert rc == 2


# ── mcp ──────────────────────────────────────────────────────────────────────


def test_mcp_default_lists_servers_without_panic(monkeypatch):
    """mcp with no flags must default to --list behaviour."""
    import bin.camelot_portable as mod

    monkeypatch.setattr(
        mod,
        "_MCP_CONFIG_PATHS",
        [Path("/nonexistent/a.json"), Path("/nonexistent/b.json")],
    )
    console = CapturingConsole()
    rc = cmd_mcp(make_args(), console)
    assert rc == 0


def test_mcp_explicit_list_flag_matches_default(monkeypatch):
    """``mcp --list`` must produce the same output as ``mcp`` with no flag,
    so the default behaviour is discoverable via argparse --help. Mirrors
    the V4000 cmd_cartridge pattern where the default mode is the docs
    first entry.
    """
    import bin.camelot_portable as mod

    monkeypatch.setattr(
        mod,
        "_MCP_CONFIG_PATHS",
        [Path("/nonexistent/a.json"), Path("/nonexistent/b.json")],
    )
    ## Capture the default-evoke run (no flags at all)
    console_default = CapturingConsole()
    rc_default = cmd_mcp(make_args(), console_default)
    ## Capture the explicit --list evoke run
    console_list = CapturingConsole()
    rc_list = cmd_mcp(make_args(mcp_list=True), console_list)
    ## Both paths return 0 and render identical lines (including the empty-config message)
    assert rc_default == 0
    assert rc_list == 0
    import re
    def sanitize_lines(lines: list[str]) -> list[str]:
        return [re.sub(r"0x[0-9a-fA-F]+", "0xXXXXXX", line) for line in lines]

    assert sanitize_lines(console_default.lines) == sanitize_lines(console_list.lines), (
        f"explicit --list should match no-flag behaviour:\n"
        f"  default={console_default.lines}\n  --list={console_list.lines}"
    )


def test_mcp_describe_unknown_server_returns_1(monkeypatch):
    import bin.camelot_portable as mod

    monkeypatch.setattr(mod, "_MCP_CONFIG_PATHS", [])
    console = CapturingConsole()
    rc = cmd_mcp(make_args(mcp_describe="ghost_server"), console)
    assert rc == 1


def test_mcp_ping_unknown_server_returns_1(monkeypatch):
    import bin.camelot_portable as mod

    monkeypatch.setattr(mod, "_MCP_CONFIG_PATHS", [])
    console = CapturingConsole()
    rc = cmd_mcp(make_args(ping="ghost_server"), console)
    assert rc == 1


def test_mcp_describe_known_server_returns_0(tmp_path, monkeypatch):
    """Inject a fake MCP config; describe should find it and print."""
    import bin.camelot_portable as mod

    cfg_path = tmp_path / "mcp_servers.json"
    cfg_path.write_text(
        '{"mcpServers": {"fake_server": {"command": "echo", "args": ["hi"]}}}',
        encoding="utf-8",
    )
    monkeypatch.setattr(
        mod, "_MCP_CONFIG_PATHS", [cfg_path]
    )
    console = CapturingConsole()
    rc = cmd_mcp(make_args(mcp_describe="fake_server"), console)
    assert rc == 0
    # The JSON dump should be in the captured output
    assert any("fake_server" in line or "echo" in line for line in console.lines)


# ── cartridge ─────────────────────────────────────────────────────────────────


def test_cartridge_default_lists_v4000_stages():
    """cartridge with no flags must default to --list behaviour."""
    console = CapturingConsole()
    rc = cmd_cartridge(make_args(), console)
    assert rc == 0


def test_cartridge_emit_creates_trio(tmp_path):
    console = CapturingConsole()
    rc = cmd_cartridge(make_args(emit="myproj", target=str(tmp_path / "myproj")), console)
    assert rc == 0
    target = tmp_path / "myproj"
    for fname in ("blueprint.md", "task.md", "verification.md"):
        assert (target / fname).exists()
        text = (target / fname).read_text(encoding="utf-8")
        assert "myproj" in text
        assert len(text.strip()) > 50  # non-trivial scaffold body


def test_cartridge_emit_no_target_defaults_to_projects(tmp_path, monkeypatch):
    """When --target is omitted, emit goes to ./projects/STAGE relative to cwd."""
    monkeypatch.chdir(tmp_path)
    console = CapturingConsole()
    rc = cmd_cartridge(make_args(emit="myproj"), console)
    assert rc == 0
    assert (tmp_path / "projects" / "myproj" / "blueprint.md").exists()


# ── cartridge emit preflight guard ────────────────────────────────────────────


def test_cartridge_emit_proceeds_when_existing_trio_is_default_unmodified(tmp_path):
    """A trio whose bytes equal the freshly-emitted default scaffold is
    treated as 'unmodified default' and may be overwritten without
    ``--force``. Covers the common case of re-running ``--emit`` against a
    still-pristine scaffold.
    """
    from bin.camelot_portable import _default_scaffold_body
    target = tmp_path / "myproj"
    target.mkdir()
    for fname in ("blueprint.md", "task.md", "verification.md"):
        (target / fname).write_text(
            _default_scaffold_body(fname, "myproj"), encoding="utf-8"
        )
    console = CapturingConsole()
    rc = cmd_cartridge(make_args(emit="myproj", target=str(target)), console)
    assert rc == 0
    for fname in ("blueprint.md", "task.md", "verification.md"):
        assert (target / fname).exists()


def test_cartridge_emit_proceeds_when_target_disagrees_with_stage(tmp_path):
    """Regression: when ``--emit X`` is paired with ``--target /path/Y`` the
    preflight must key the byte-equality check against ``Y`` (i.e.
    ``target.name`` — the directory the trio materialises under), NOT ``X``
    (``args.emit``). The write path has always used ``target.name``; before
    this fix the preflight used ``args.emit`` and any explicit
    ``--target`` diverging from ``--emit`` spuriously refused an
    otherwise-untouched re-emit. """
    from bin.camelot_portable import _default_scaffold_body
    target = tmp_path / "renamed_on_disk"
    target.mkdir()
    for fname in ("blueprint.md", "task.md", "verification.md"):
        (target / fname).write_text(
            _default_scaffold_body(fname, "renamed_on_disk"), encoding="utf-8"
        )
    console = CapturingConsole()
    rc = cmd_cartridge(
        make_args(emit="original_stage_name", target=str(target)), console
    )
    assert rc == 0, "re-emit must proceed without --force when bytes match target.name"


def test_cartridge_emit_refuses_when_existing_trio_is_user_modified(tmp_path):
    """A trio whose bytes depart from the default scaffold triggers the
    refuse-without-``--force`` branch. The file is left untouched (mtime
    AND content unchanged).
    """
    target = tmp_path / "myproj"
    target.mkdir()
    protected_content = (
        "# Blueprint — myproj\n\n"
        "## Status\n\n"
        "USER-OWNED CONTENT — must not be silently clobbered by an emit "
        "without --force. Includes deliberate long-form rationale.\n"
    )
    protected_path = target / "blueprint.md"
    protected_path.write_text(protected_content, encoding="utf-8")
    pre_mtime = protected_path.stat().st_mtime
    pre_size = protected_path.stat().st_size
    console = CapturingConsole()
    rc = cmd_cartridge(make_args(emit="myproj", target=str(target)), console)
    assert rc == 1
    # The preflight must print the explanatory "refusing" token so MCP / VS
    # Code consumers can surface the hint.
    assert any("refusing without --force" in line for line in console.lines)
    # File content unchanged.
    assert protected_path.read_text(encoding="utf-8") == protected_content
    assert protected_path.stat().st_mtime == pre_mtime
    assert protected_path.stat().st_size == pre_size


def test_cartridge_emit_force_overrides_modified_trio(tmp_path):
    """``--force`` proceeds even when the existing trio is user-modified."""
    target = tmp_path / "myproj"
    target.mkdir()
    protected_content = "# Blueprint — myproj\n\n## Status\n\nUSER-OWNED CONTENT\n"
    (target / "blueprint.md").write_text(protected_content, encoding="utf-8")
    console = CapturingConsole()
    rc = cmd_cartridge(
        make_args(emit="myproj", target=str(target), cartridge_force=True),
        console,
    )
    assert rc == 0
    # After force, the trio is rewritten to the default scaffold body.
    assert "USER-OWNED CONTENT" not in (
        target / "blueprint.md"
    ).read_text(encoding="utf-8")


def test_cartridge_emit_refuses_when_partial_trio_has_user_data(tmp_path):
    """Even with 1 of 3 trio files present + non-default, refuse without
    ``--force``. The other 2 files might still be auto-created on a
    ``--force`` run, but the partial combo still constitutes user work."""
    target = tmp_path / "myproj"
    target.mkdir()
    user_blueprint = target / "blueprint.md"
    user_blueprint.write_text(
        "# Blueprint — myproj\n\n## My Notes\n\nreal work\n",
        encoding="utf-8",
    )
    pre_mtime = user_blueprint.stat().st_mtime
    console = CapturingConsole()
    rc = cmd_cartridge(make_args(emit="myproj", target=str(target)), console)
    assert rc == 1
    assert user_blueprint.stat().st_mtime == pre_mtime
    assert "real work" in user_blueprint.read_text(encoding="utf-8")


def test_cartridge_emit_proceeds_when_existing_trio_is_empty_stub(tmp_path):
    """A 0-byte trio file is treated as a stub the user wants filled;
    overwrites proceed without ``--force``."""
    target = tmp_path / "myproj"
    target.mkdir()
    for fname in ("blueprint.md", "task.md", "verification.md"):
        (target / fname).write_text("", encoding="utf-8")
    console = CapturingConsole()
    rc = cmd_cartridge(make_args(emit="myproj", target=str(target)), console)
    assert rc == 0
    for fname in ("blueprint.md", "task.md", "verification.md"):
        assert (target / fname).stat().st_size > 0


# ── cartridge --list frozen-mode early-out ─────────────────────────────────────


def test_cmd_cartridge_list_prints_frozen_mode_hint_when_pyinstaller(monkeypatch):
    """In PyInstaller frozen mode (``sys._MEIPASS`` is set), the V4000
    stages lookup silently no-ops because ``_REPO`` is a stale dev path.
    Print a clear hint instead so users know this is intentional, not a
    bug, and tell them exactly how to enable V4000 stages in the bundle
    (add the dir to ``camelot.spec``'s ``datas`` list).
    """
    monkeypatch.setattr(sys, "_MEIPASS", "/tmp/fake_meipass", raising=False)
    console = CapturingConsole()
    args = make_args()  # emit=None triggers the --list path
    rc = cmd_cartridge(args, console)
    assert rc == 0
    # The hint must be in the captured output so frozen-mode users see it
    # instead of silence.
    assert any("not bundled in portable binary" in line for line in console.lines), (
        f"Expected frozen-mode hint, got: {console.lines}"
    )
    # The hint must tell the user exactly how to opt in.
    assert any("camelot.spec" in line and "datas" in line for line in console.lines), (
        f"Expected hint to mention camelot.spec datas, got: {console.lines}"
    )


def test_cmd_cartridge_list_skips_frozen_hint_in_dev_mode(monkeypatch):
    """Counter-test: the frozen-mode hint must NOT fire in dev mode
    (i.e. when ``sys._MEIPASS`` is absent). The opposite scan also
    verifies the dev-mode listing is real, so the hasattr gate didn't
    accidentally swallow it for operators with a populated
    ``02_FORGE/cartridge/digital_factory_v4000_ascended/`` tree.
    """
    # Explicitly ensure no _MEIPASS attribute in this test process.
    monkeypatch.delattr(sys, "_MEIPASS", raising=False)
    console = CapturingConsole()
    args = make_args()
    rc = cmd_cartridge(args, console)
    assert rc == 0
    # Frozen-mode hint must NOT appear in dev mode.
    assert not any("not bundled in portable binary" in line for line in console.lines), (
        f"Frozen-mode hint should not fire in dev mode, got: {console.lines}"
    )
    # Positive listing assertion: the V4000 stages section MUST appear in
    # dev mode so a populated repo actually shows its stages. The repo
    # ships 02_FORGE/cartridge/digital_factory_v4000_ascended/ populated
    # with stage subdirs that the listing iterates.
    assert any("V4000 stages" in line for line in console.lines), (
        f"Dev-mode listing should print V4000 stages heading, got: {console.lines}"
    )


# ── mcp --chain: saltare provider fallback table ───────────────────────────────


def test_mcp_chain_returns_0_with_table_when_saltare_declared(tmp_path, monkeypatch):
    """``--chain`` surfaces the saltare provider chain sorted by priority — proves
    the entry-2 (mcp_config.json) load-bearing metadata is now visible to
    the operator, not only internal.
    """
    import io

    from rich.console import Console

    import bin.camelot_portable as mod

    # Three providers given in non-priority order to prove the table
    # sorts by the ``priority`` field (not insertion order).
    cfg_path = tmp_path / "mcp_config.json"
    cfg_path.write_text(
        '{"saltare": {"port": 8080, "fallback_chain": ['
        '{"provider": "ollama", "priority": 3, "note": "local sovereignty"}, '
        '{"provider": "cerebras", "priority": 1, "note": "wafer-scale"}, '
        '{"provider": "openrouter", "priority": 2, "note": "cloud fallback"}'
        ']}}',
        encoding="utf-8",
    )
    monkeypatch.setattr(mod, "_MCP_CONFIG_PATHS", [cfg_path])

    # Real Rich Console with StringIO so the Table renders to text the
    # test can assert against. The minimal ``CapturingConsole`` shim
    # converts Table objects to ``repr(...)``, losing row contents.
    buf = io.StringIO()
    console = Console(file=buf, force_terminal=False, width=200)
    rc = cmd_mcp(make_args(mcp_chain=True), console)
    assert rc == 0

    output = buf.getvalue()
    assert "Source" in output, f"Expected Source annotation, got:\n{output}"
    # Priority-sorted output: cerebras (1) -> openrouter (2) -> ollama (3).
    cerebras_pos = output.find("cerebras")
    openrouter_pos = output.find("openrouter")
    ollama_pos = output.find("ollama")
    assert cerebras_pos != -1 and openrouter_pos != -1 and ollama_pos != -1, (
        f"Expected all 3 providers in output, got:\n{output}"
    )
    assert cerebras_pos < openrouter_pos < ollama_pos, (
        f"Expected cerebras < openrouter < ollama (sorted by priority), got:\n{output}"
    )


def test_mcp_chain_returns_1_when_no_saltare_declared_in_dev_mode(monkeypatch):
    """``--chain`` returns 1 + a friendly hint when no MCP config declares a
    ``saltare`` block in dev mode (no ``_MEIPASS``). Counter-test so the
    helper's empty-result branch is exercised and doesn't accidentally
    print an empty table silently.
    """
    import bin.camelot_portable as mod

    monkeypatch.setattr(mod, "_MCP_CONFIG_PATHS", [])
    # Force dev-mode path so the test is robust against a CI harness that
    # happens to set ``sys._MEIPASS`` for unrelated reasons.
    monkeypatch.delattr(sys, "_MEIPASS", raising=False)
    console = CapturingConsole()
    rc = cmd_mcp(make_args(mcp_chain=True), console)
    assert rc == 1
    assert any("No saltare chain" in line for line in console.lines), (
        f"Expected missing-chain hint, got: {console.lines}"
    )


def test_mcp_chain_returns_0_with_frozen_mode_hint_when_pyinstaller(monkeypatch):
    """In PyInstaller frozen mode + no bundled saltare config, return 0
    with a parallel hint telling the user exactly which path to add to
    ``camelot.spec`` datas — mirrors the V4000 cmd_cartridge pattern.
    """
    import bin.camelot_portable as mod

    monkeypatch.setattr(mod, "_MCP_CONFIG_PATHS", [Path("/nonexistent/a.json")])
    monkeypatch.setattr(sys, "_MEIPASS", "/tmp/fake_meipass", raising=False)
    console = CapturingConsole()
    rc = cmd_mcp(make_args(mcp_chain=True), console)
    # Informational exit (matches V4000 cmd_cartridge frozen-mode early-out).
    assert rc == 0
    # The hint must mention camelot.spec datas so users know how to opt in.
    assert any("not bundled" in line for line in console.lines), (
        f"Expected frozen-mode hint, got: {console.lines}"
    )
    assert any(
        "camelot.spec" in line and "datas" in line for line in console.lines
    ), f"Expected camelot.spec datas hint, got: {console.lines}"
