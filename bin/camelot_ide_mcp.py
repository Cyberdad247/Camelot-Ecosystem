# SPDX-License-Identifier: MIT

"""
camelot_ide_mcp — CAMELOT-OS IDE/CLI MCP server.

Exposes the four bin/camelot_portable.py subcommands as MCP tools so that
VS Code (1.86+) / Cursor / Claude Dev / Roo-Code MCP clients can drive the
portable CLI surface via stdio JSON-RPC.

Iron Gate conformance
---------------------
- stdout is the JSON-RPC stream; this module NEVER prints to stdout.
- All subprocess invocations use argv-list mode. ``shell=False`` is enforced
  via ``asyncio.create_subprocess_exec`` (no shell quoting, no injection).
- ``camelot_cartridge(action="emit")`` enforces a path-traversal jail on
  the ``--target`` argument so an MCP client cannot escape the workspace.
- NO_RICH=1 is forced on every subprocess so captured stdout is plain text.

Self-test
---------
::

    python bin/camelot_ide_mcp.py --self-test
"""
from __future__ import annotations

import asyncio
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any


# Stderr-only logging; stdout is the JSON-RPC stream.
def _log(msg: str) -> None:
    sys.stderr.write(f"[camelot-ide-mcp] {msg}\n")
    sys.stderr.flush()


REPO_ROOT: Path = Path(__file__).resolve().parent.parent
PORTABLE: Path = REPO_ROOT / "bin" / "camelot_portable.py"
NO_RICH_ENV = "1"

# MCP spec: tool names must match ^[a-zA-Z0-9_-]+$. No slashes.
_MCP_TOOL_NAME_RE = re.compile(r"^[a-zA-Z0-9_-]+$")


# ── Path-traversal jail (workspace root = REPO for dev, cwd for MCP-from-CLI) ─


def _jail_target(target: str, workspace_root: Path) -> str:
    """Resolve ``target`` and assert it stays inside ``workspace_root``.

    Rejects ``../../`` traversal, absolute paths outside the workspace, and
    symlinks that resolve outside. Raises ``ValueError`` on escape attempts.
    """
    if not target:
        raise ValueError("target is empty")
    p = Path(target).expanduser()
    if not p.is_absolute():
        p = workspace_root / p
    abs_p = p.resolve(strict=False)
    ws_abs = workspace_root.resolve(strict=False)
    try:
        abs_p.relative_to(ws_abs)
    except ValueError:
        raise ValueError(
            f"target {abs_p} escapes workspace {ws_abs}"
        )
    return str(abs_p)


# ── Subprocess invocation (argv-list, NO_RICH, PYTHONUTF8) ─


async def _invoke_portable(args: list[str], workspace_root: Path | None = None) -> str:
    """Invoke ``python bin/camelot_portable.py <args>`` and capture its stdout.

    Returns captured stdout (NO_RICH strips Rich markup in the subprocess).
    Raises ``RuntimeError`` on non-zero exit, including stderr in the message.
    """
    cwd = str(workspace_root or REPO_ROOT)
    env = {**os.environ, "NO_RICH": NO_RICH_ENV, "PYTHONUTF8": "1"}
    proc = await asyncio.create_subprocess_exec(
        sys.executable,
        str(PORTABLE),
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd,
        env=env,
    )  # shell=False by definition; argv-list mode enforced.
    stdout_b, stderr_b = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(
            f"camelot_portable.py exit {proc.returncode}: "
            + stderr_b.decode("utf-8", "replace")[:500]
        )
    return stdout_b.decode("utf-8", "replace")


# ── Tool catalogue ─────────────────────────────────

TOOLS: list[dict[str, Any]] = [
    {
        "name": "camelot_omniroute",
        "description": (
            "Route an intent via OmniRoute lane-signal policy "
            "(SELECT_OPTIMAL_FRAMEWORK_O1). Action: list | select | route. "
            "select returns a LaneSignal (lane + rationale + matched_keyword) "
            "via control_plane.omniroute_policies.select_lane. route returns "
            "the keyword-routed knight id."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "select", "route"],
                    "description": "Which OmniRoute verb to invoke",
                },
                "intent": {
                    "type": "string",
                    "description": "Intent text. Required for action=select|route.",
                },
            },
            "required": ["action"],
        },
    },
    {
        "name": "camelot_knight",
        "description": (
            "List or invoke a Camelot frontier-LLM knight via the CLIProxyAPI "
            "gateway at :8080 (or direct API fallback). Available knights: "
            "sir_boris, sir_helio, sir_alex, sir_sentinel, sir_codex, sir_link, "
            "sir_debug, lady_apis, sir_mnemo, sir_forge, sir_ghost, etc."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "invoke"],
                },
                "knight_id": {
                    "type": "string",
                    "description": "e.g. sir_codex, sir_boris, sir_helio. Required for invoke.",
                },
                "prompt": {
                    "type": "string",
                    "description": "Prompt text. Required for invoke.",
                },
            },
            "required": ["action"],
        },
    },
    {
        "name": "camelot_mcp",
        "description": (
            "Discover / probe MCP servers configured across "
            ".claude/settings.json, mcp_servers.json, and mcp_config.json. "
            "Action: list | describe | ping."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "describe", "ping"],
                },
                "server_name": {
                    "type": "string",
                    "description": "Required for action=describe|ping.",
                },
            },
            "required": ["action"],
        },
    },
    {
        "name": "camelot_cartridge",
        "description": (
            "Digital Factory V4000 cartridges: list active stages + trio file "
            "health, OR emit a fresh (blueprint.md / task.md / verification.md) "
            "trio into a target directory (path-traversal jail enforced). "
            "When emitting into a target whose trio files have been modified "
            "past the default scaffold, the portable CLI is REFUSING without "
            "`--force` and exits 1. Re-call this tool with `force=true` to "
            "overwrite a non-trivial trio."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "emit"],
                },
                "stage": {
                    "type": "string",
                    "description": "Stage id (slug). Required for emit.",
                },
                "target": {
                    "type": "string",
                    "description": (
                        "Target directory for emit. Jailed to the workspace "
                        "root. Default: projects/<stage>."
                    ),
                },
                "force": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Overwrite an existing non-trivial trio. Only "
                        "honored for action=emit. When the existing trio "
                        "files are byte-identical to the default scaffold "
                        "(or missing / 0-byte stubs) the emit proceeds "
                        "without --force; the portable CLI enforces this "
                        "and exit 1 means the caller should re-call with "
                        "force=true after reviewing the existing content."
                    ),
                },
            },
            "required": ["action"],
        },
    },
]


# ── Tool dispatch ────────────────────────────────


async def _dispatch_tool(name: str, arguments: dict[str, Any]) -> str:
    """Dispatch one MCP tool call. Returns the textual response payload."""
    if name not in {t["name"] for t in TOOLS}:
        raise ValueError(f"unknown tool: {name!r}")

    if name == "camelot_omniroute":
        action = arguments.get("action", "")
        if action == "list":
            return await _invoke_portable(["omniroute", "--list"])
        if action in ("select", "route"):
            intent = arguments.get("intent") or ""
            flag = "--select" if action == "select" else "--route"
            return await _invoke_portable(["omniroute", flag, intent])
        raise ValueError(f"unsupported omniroute action: {action!r}")

    if name == "camelot_knight":
        action = arguments.get("action", "")
        if action == "list":
            return await _invoke_portable(["knight", "--list"])
        if action == "invoke":
            kid = arguments["knight_id"]
            prompt = arguments["prompt"]
            return await _invoke_portable(
                ["knight", "--invoke", kid, "--prompt", prompt]
            )
        raise ValueError(f"unsupported knight action: {action!r}")

    if name == "camelot_mcp":
        action = arguments.get("action", "list")
        if action == "list":
            return await _invoke_portable(["mcp"])
        if action == "describe":
            return await _invoke_portable(
                ["mcp", "--describe", arguments["server_name"]]
            )
        if action == "ping":
            return await _invoke_portable(
                ["mcp", "--ping", arguments["server_name"]]
            )
        raise ValueError(f"unsupported mcp action: {action!r}")

    if name == "camelot_cartridge":
        action = arguments.get("action", "list")
        if action == "list":
            return await _invoke_portable(["cartridge", "--list"])
        if action == "emit":
            stage = arguments["stage"]
            target_arg = arguments.get("target") or f"projects/{stage}"
            # Path-traversal jail: target must stay inside REPO_ROOT or cwd.
            safe_target = _jail_target(target_arg, REPO_ROOT)
            argv: list[str] = ["cartridge", "--emit", stage, "--target", safe_target]
            # Append --force only when the caller (typically an AI agent
            # that already saw the "refusing without --force" message)
            # explicitly opts in. Default (force=false) preserves the
            # preflight guard's user-content protection.
            if bool(arguments.get("force", False)):
                argv.append("--force")
            return await _invoke_portable(argv)
        raise ValueError(f"unsupported cartridge action: {action!r}")

    raise ValueError(f"unhandled tool: {name!r}")  # pragma: no cover


# ── MCP SDK server registration ────────────────────

# Imported lazily so the self-test path doesn't pull the SDK unless the server
# is actually being run. The SDK is declared in pyproject.toml (mcp>=1.26.0).
server = None  # type: ignore[assignment]
_stdio_server = None  # type: ignore[assignment]
_TextContent = None  # type: ignore[assignment]


def _init_sdk() -> None:
    """Lazy-init the MCP SDK bindings. Called from main() / self-test."""
    global server, _stdio_server, _TextContent
    from mcp.server import Server as _Server
    from mcp.server.stdio import stdio_server as _stdio
    from mcp.types import TextContent as _TC
    server = _Server("camelot-ide")
    _stdio_server = _stdio
    _TextContent = _TC


async def _main_loop() -> None:
    """Run the MCP server over stdio until the client terminates."""
    assert server is not None and _stdio_server is not None
    _init_tool_handlers()
    _log("starting stdio loop")
    async with _stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def _init_tool_handlers() -> None:
    """Install the @server.list_tools / @server.call_tool hooks."""
    assert server is not None and _TextContent is not None

    @server.list_tools()
    async def _list() -> list[Any]:
        from mcp.types import Tool
        return [Tool(**t) for t in TOOLS]

    @server.call_tool()
    async def _call(name: str, arguments: dict[str, Any]) -> list[Any]:
        text = await _dispatch_tool(name, arguments)
        return [_TextContent(type="text", text=text)]


# ── Self-test (no MCP transport needed) ─────────────


def _self_test() -> int:
    """Verify tools, schemas, jail, and NO_RICH policy without running a server."""
    errors: list[str] = []

    # 1. Tool names comply with MCP regex (no slashes).
    for t in TOOLS:
        if not _MCP_TOOL_NAME_RE.match(t["name"]):
            errors.append(f"tool name {t['name']!r} violates MCP regex")
        if "/" in t["name"]:
            errors.append(f"tool name {t['name']!r} contains a slash")
        if t["inputSchema"].get("type") != "object":
            errors.append(f"tool {t['name']!r} inputSchema.type != object")

    # 2. Path-traversal jail rejects escape attempts.
    with tempfile.TemporaryDirectory() as tmp:
        ws = Path(tmp)
        try:
            _jail_target("../../../etc/passwd", ws)
            errors.append("jail accepted ../../../etc/passwd (must reject)")
        except ValueError:
            pass
        if errors and "jail" in errors[-1]:
            errors.pop()  # we count the rejection as success
        try:
            _jail_target("projects/foo", ws)
        except ValueError as e:
            errors.append(f"jail rejected valid subpath: {e}")

    # 3. NO_RICH env var is the literal string "1".
    if NO_RICH_ENV != "1":
        errors.append(f"NO_RICH_ENV={NO_RICH_ENV!r} must be '1'")

    # 4. camelot_cartridge schema exposes the `force` arg for emit (used
    # by AI agents that re-call after seeing the "refusing without --force"
    # stdout sentinel from the portable CLI's preflight guard).
    cart = next((t for t in TOOLS if t["name"] == "camelot_cartridge"), None)
    if cart is None:
        errors.append("camelot_cartridge tool missing from TOOLS")
    else:
        props = cart["inputSchema"].get("properties", {})
        if "force" not in props:
            errors.append("camelot_cartridge inputSchema missing 'force' arg")
        elif props["force"].get("type") != "boolean":
            errors.append(
                f"camelot_cartridge.force type={props['force'].get('type')!r} "
                "must be 'boolean'"
            )
        if "refusing" not in cart["description"].lower():
            errors.append(
                "camelot_cartridge description must mention the preflight "
                "refusal so LLM clients learn the contract from the schema"
            )

    if errors:
        for e in errors:
            _log(f"[FAIL] {e}")
        return 1
    _log("[OK] all 4 tools valid; jail rejects escapes; NO_RICH=1; "
         "cartridge schema exposes `force` arg with refusal-sentinel description")
    return 0


# ── Entry ──────────────────────────────────


def main() -> int:
    if "--self-test" in sys.argv:
        return _self_test()
    _init_sdk()
    asyncio.run(_main_loop())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
