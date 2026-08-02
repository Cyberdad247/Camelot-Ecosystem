# Camelot-OS VS Code Extension

Thin shell-out to `bin/camelot_portable.py` from VS Code (`^1.86.0`). The extension doesn't reimplement any logic; it forwards subcommand invocations over a stdio child-process with an argv-list (no shell quoting), and surfaces the response in VS Code's Output channel.

## Commands

| Command | Title | Description |
|---------|-------|-------------|
| `camelot.omniroute` | _Camelot: OmniRoute lane (intake intent)_ | Prompt for intent, run `omniroute --select`, surface the LaneSignal in the **Camelot OmniRoute** output channel. |
| `camelot.knight` | _Camelot: Knight invoke (one-shot frontier LLM)_ | Prompt for knight id + prompt, run `knight --invoke ID --prompt TEXT`, stream the response to the **Camelot Knight [id]** output channel. |
| `camelot.mcp` | _Camelot: MCP server inventory_ | Run `mcp`, surface the table in the **Camelot MCP** output channel. |
| `camelot.cartridge` | _Camelot: Cartridge emit (V4000 trio)_ | Prompt for stage name + target dir, run `cartridge --emit STAGE --target DIR`, refresh the Files Explorer. |

## Composition

- **Tasks**: `.vscode/tasks.json` (workspace-level) exposes the same verbs as Task labels.
- **Snippets**: `.vscode/snippets/camelot.code-snippets` (workspace-level) exposes per-knight + runic dispatch headers + an Iron-Gate-friendly degrade-test scaffold.
- **MCP client**: `.vscode/mcp.json` (VS Code 1.97+ standalone format) registers `bin/camelot_ide_mcp.py` for VS Code's MCP client, Cursor, Claude Dev, and Roo-Code. **The extension manifest itself does NOT register an MCP server** — MCP discovery is workspace-level via `.vscode/mcp.json`, not via `contributes.mcpServerDefinitionProviders`.
- **Status bar**: A `$(zap) Camelot: <knight>` indicator surfaces the active default knight.

## Format compatibility

- The extension commands + status bar work in VS Code `^1.86.0`.
- `.vscode/mcp.json` requires VS Code `1.97.0+` (standalone MCP client config). For older VS Code, add the MCP server to your `settings.json` `mcp.servers` block manually.

## Iron-Gate posture

- **Argv-list spawn** — every subprocess uses `child_process.spawn(python, [portable, ...args], { shell: false })`. No shell quoting, no injection surface.
- **NO_RICH=1 forced** — subprocess captures stay plain-text; Rich markup doesn't leak into Output channels.
- **UTF-8 output stream forced** — `bin/camelot_portable.py::_console_factory()` wraps `sys.stdout.buffer` in a UTF-8 `TextIOWrapper` under NO_RICH=1 so non-cp1252 chars (Greek ``Ω``, CJK, emoji) survive capture cleanly.
- **PYTHONUTF8=1 forced** — Python interpreter-level UTF-8 default for the subprocess.
- **Path-traversal jail** — `bin/camelot_ide_mcp.py::_jail_target` jails the `--target` argument of `cartridge --emit` so MCP clients can't escape the workspace. The extension forwards user input verbatim; if you intend to bind untrusted `--target` paths, route through the MCP client.

## Configuration

| Key | Default | Description |
|-----|---------|-------------|
| `camelot.pythonPath` | `python` | Python interpreter (3.13+) for the portable CLI + MCP server. |
| `camelot.defaultKnight` | `sir_helio` | Knight surfaced on the status bar. |

## Build / install

```bash
cd extensions/camelot-vscode
npm install
npm run build        # tsc -> out/extension.js
npm run package      # vsce package -> camelot-1000.0.0.vsix
code --install-extension camelot-1000.0.0.vsix
```

## Activation events

- `onCommand:camelot.omniroute|knight|mcp|cartridge` — eagerly registers the commands you invoke.
- `workspaceContains:CLAUDE.md` — auto-activates in Camelot-OS workspaces.
- `workspaceContains:omniroute.json` — auto-activates in workspaces where OmniRoute is configured.
