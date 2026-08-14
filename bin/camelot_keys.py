# SPDX-License-Identifier: MIT

"""camelot keys — Secure API key management via system keyring.

Keys are stored in the OS keyring (Windows Credential Manager, macOS Keychain,
Linux Secret Service). The config.json NEVER stores actual key values — only
boolean presence flags. This module is the single source of truth for keys.

Usage:
    camelot keys set anthropic    # prompt for key, store in keyring
    camelot keys get anthropic    # retrieve and print (masked)
    camelot keys delete anthropic # remove from keyring
    camelot keys list             # show which keys are stored (masked)
    camelot keys export-env       # print export statements for current shell session
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

_SERVICE = "camelot-os"

_KNOWN_KEYS = {
    "anthropic":  ("ANTHROPIC_API_KEY",  "Anthropic Claude API key"),
    "google":     ("GOOGLE_API_KEY",     "Google Gemini API key"),
    "openai":     ("OPENAI_API_KEY",     "OpenAI API key"),
    "cliproxy":   ("CLIPROXY_API_KEY",   "CLIProxy OAuth key (proxy-admin-key)"),
    "groq":       ("GROQ_API_KEY",       "Groq API key"),
    "cerebras":   ("CEREBRAS_API_KEY",   "Cerebras API key"),
}


def _get_keyring():
    try:
        import keyring
        return keyring
    except ImportError:
        return None


def _mask(value: str) -> str:
    if len(value) <= 8:
        return "***"
    return value[:4] + "..." + value[-4:]


def cmd_set(key_name: str, value: Optional[str] = None) -> None:
    from rich.console import Console
    from rich.prompt import Prompt
    console = Console()

    kr = _get_keyring()
    if not kr:
        console.print("[red]keyring not installed. Run: pip install keyring[/red]")
        sys.exit(1)

    info = _KNOWN_KEYS.get(key_name.lower())
    if not info:
        console.print(f"[yellow]Unknown key '{key_name}'. Known: {', '.join(_KNOWN_KEYS)}[/yellow]")
        console.print("[dim]Storing anyway as custom key...[/dim]")
        env_var = key_name.upper()
        description = f"Custom key: {key_name}"
    else:
        env_var, description = info

    if not value:
        value = Prompt.ask(f"  Enter {description}", password=True)

    if not value.strip():
        console.print("[red]Empty key — aborted.[/red]")
        return

    kr.set_password(_SERVICE, key_name.lower(), value.strip())
    console.print(f"  [green][OK][/green] Stored {key_name} in system keyring ({_mask(value.strip())})")
    console.print(f"  [dim]Also sets env var {env_var} for this process[/dim]")
    os.environ[env_var] = value.strip()

    _update_config_flag(key_name.lower(), present=True)


def cmd_get(key_name: str) -> None:
    from rich.console import Console
    console = Console()

    kr = _get_keyring()
    if not kr:
        console.print("[red]keyring not installed.[/red]")
        return

    value = kr.get_password(_SERVICE, key_name.lower())
    if value:
        console.print(f"  [green]{key_name}[/green]: {_mask(value)}")
    else:
        # Fallback to env var
        info = _KNOWN_KEYS.get(key_name.lower())
        env_val = os.environ.get(info[0], "") if info else ""
        if env_val:
            console.print(f"  [yellow]{key_name}[/yellow]: {_mask(env_val)} [dim](env var only, not in keyring)[/dim]")
        else:
            console.print(f"  [red]{key_name}[/red]: not found")


def cmd_delete(key_name: str) -> None:
    from rich.console import Console
    console = Console()

    kr = _get_keyring()
    if not kr:
        console.print("[red]keyring not installed.[/red]")
        return

    try:
        kr.delete_password(_SERVICE, key_name.lower())
        console.print(f"  [green][OK][/green] Deleted {key_name} from keyring")
        _update_config_flag(key_name.lower(), present=False)
    except Exception:
        console.print(f"  [yellow]{key_name} not found in keyring[/yellow]")


def cmd_list() -> None:
    from rich.console import Console
    from rich.table import Table
    console = Console()

    kr = _get_keyring()

    table = Table(title="Camelot-OS API Keys", border_style="yellow")
    table.add_column("Key", style="bold")
    table.add_column("Env Var")
    table.add_column("Keyring")
    table.add_column("Env")
    table.add_column("Value (masked)")

    for name, (env_var, desc) in _KNOWN_KEYS.items():
        kr_val = kr.get_password(_SERVICE, name) if kr else None
        env_val = os.environ.get(env_var, "")
        active_val = kr_val or env_val

        kr_status  = "[green]yes[/green]" if kr_val  else "[dim]no[/dim]"
        env_status = "[green]yes[/green]" if env_val else "[dim]no[/dim]"
        masked = _mask(active_val) if active_val else "[dim]—[/dim]"

        table.add_row(name, env_var, kr_status, env_status, masked)

    console.print(table)
    console.print(
        "\n  [dim]Use [bold]camelot keys set <name>[/bold] to store a key securely.[/dim]"
    )


def cmd_export_env(shell: str = "auto") -> None:
    """Print export/Set-Item statements to inject keys into current shell session."""
    from rich.console import Console
    console = Console()

    kr = _get_keyring()
    lines = []

    for name, (env_var, _) in _KNOWN_KEYS.items():
        value = (kr.get_password(_SERVICE, name) if kr else None) or os.environ.get(env_var, "")
        if not value:
            continue

        if shell in ("powershell", "ps", "auto") and sys.platform == "win32":
            lines.append(f'$env:{env_var} = "{value}"')
        else:
            lines.append(f'export {env_var}="{value}"')

    if lines:
        console.print("\n".join(lines))
    else:
        console.print("[yellow]No keys found in keyring.[/yellow]")


def load_keys_to_env() -> dict[str, bool]:
    """Called at REPL startup — inject keyring keys into os.environ. Returns presence flags."""
    kr = _get_keyring()
    flags: dict[str, bool] = {}

    for name, (env_var, _) in _KNOWN_KEYS.items():
        # Don't overwrite already-set env vars
        if os.environ.get(env_var):
            flags[name] = True
            continue
        if kr:
            value = kr.get_password(_SERVICE, name)
            if value:
                os.environ[env_var] = value
                flags[name] = True
                continue
        flags[name] = False

    return flags


def _update_config_flag(key_name: str, present: bool) -> None:
    """Update config.json boolean flag (never writes actual key value)."""
    import json
    config_path = Path.home() / ".camelot" / "config.json"
    if not config_path.exists():
        return
    try:
        cfg = json.loads(config_path.read_text())
        if "keys" not in cfg:
            cfg["keys"] = {}
        cfg["keys"][key_name] = present
        config_path.write_text(json.dumps(cfg, indent=2))
    except Exception:
        pass


def main(argv: list[str] | None = None) -> None:
    import argparse
    p = argparse.ArgumentParser(prog="camelot keys", description="Manage API keys in system keyring")
    sub = p.add_subparsers(dest="action")

    s = sub.add_parser("set",    help="Store a key in the keyring")
    s.add_argument("key",        help="Key name (anthropic, google, openai, ...)")
    s.add_argument("value",      nargs="?", help="Key value (prompted if omitted)")

    g = sub.add_parser("get",    help="Show a stored key (masked)")
    g.add_argument("key")

    d = sub.add_parser("delete", help="Remove a key from the keyring")
    d.add_argument("key")

    sub.add_parser("list",       help="List all known keys and their status")

    e = sub.add_parser("export-env", help="Print shell export statements for all stored keys")
    e.add_argument("--shell", choices=["bash", "zsh", "fish", "powershell"], default="auto")

    args = p.parse_args(argv)

    if args.action == "set":
        cmd_set(args.key, getattr(args, "value", None))
    elif args.action == "get":
        cmd_get(args.key)
    elif args.action == "delete":
        cmd_delete(args.key)
    elif args.action == "list":
        cmd_list()
    elif args.action == "export-env":
        cmd_export_env(args.shell)
    else:
        cmd_list()


if __name__ == "__main__":
    main()
