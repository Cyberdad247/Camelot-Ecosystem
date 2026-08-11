"""
camelot — CAMELOT-OS Global Command (WARP_GATE v1.0.0)
=======================================================
The primary sovereign CLI. Equivalent to `claude`, `gemini`, or `codex` but
routes through OmniRoute to the optimal Camelot-OS knight with full constitution
context injected every session.

Sub-commands:
    camelot [warp]             Boot into Camelot-OS REPL (default)
    camelot cockpit            Warp-first shell overlay helpers
    camelot configure          Run auto-configuration engine
    camelot status             Probe all services + show health matrix
    camelot install            First-time setup guide
    camelot build              Build portable binary (PyInstaller)
    camelot completion SHELL   Print shell completion script (bash/zsh/fish/powershell)

Global flags (forwarded to warp):
    --knight / -k  <id>   Force specific knight
    --no-context / -n     Skip CLAUDE.md injection (raw LLM)
    --system / -s  <file> Override system prompt from file
    --verbose / -v        Show routing + context token details
    --version / -V        Print version and exit
"""

from __future__ import annotations

import sys
from pathlib import Path

# When frozen as a PyInstaller binary, _MEIPASS holds embedded assets.
# When running from source, fall back to repo root.
_FROZEN = hasattr(sys, "_MEIPASS")
_ASSET_ROOT = Path(sys._MEIPASS) if _FROZEN else None  # type: ignore[attr-defined]
_REPO = Path(__file__).resolve().parent.parent if not _FROZEN else Path(sys._MEIPASS)  # type: ignore[attr-defined]

if not _FROZEN:
    sys.path.insert(0, str(_REPO))

__version__ = "400.1.0"
_WARP_GATE  = "1.0.0"

_WRAPPER_SUBCOMMANDS = {"configure", "config", "status", "install", "build", "update", "warp", "shell-setup", "keys", "cockpit", "completion"}


def _banner() -> None:
    from rich.console import Console
    from rich.panel import Panel
    Console().print(Panel(
        f"[bold yellow]CAMELOT-OS[/bold yellow] v{__version__}  //  "
        f"[bold]WARP_GATE[/bold] v{_WARP_GATE}\n"
        "[dim]Type [bold]camelot[/bold] to warp in  ·  "
        "[bold]camelot configure[/bold] to auto-detect environment  ·  "
        "[bold]camelot status[/bold] to probe services[/dim]",
        border_style="yellow",
    ))


def _cmd_warp() -> None:
    """Default: boot into Camelot-OS REPL."""
    if _FROZEN:
        # In portable binary: use self-contained REPL (no control_plane deps)
        from camelot_portable import main as portable_main  # type: ignore
        portable_main()
    else:
        from bin.knight_session import main as ks_main
        ks_main()


def _cmd_configure(verbose: bool = False) -> None:
    from bin.camelot_configure import run_configure
    run_configure(verbose=verbose)


def _cmd_status() -> None:
    from bin.camelot_configure import show_status
    show_status()


def _cmd_install() -> None:
    from rich.console import Console
    from rich.panel import Panel
    console = Console()
    console.print(Panel(
        "[bold yellow]⚔  CAMELOT-OS Install Guide[/bold yellow]\n\n"
        "[bold]Option 1 — pip (recommended)[/bold]\n"
        "  pip install -e .\n\n"
        "[bold]Option 2 — Already installed (this session)[/bold]\n"
        "  camelot configure   ← run auto-detection now\n\n"
        "[bold]Option 3 — Windows PowerShell installer[/bold]\n"
        "  .\\scripts\\install.ps1\n\n"
        "[bold]Option 4 — Linux/Mac shell installer[/bold]\n"
        "  bash scripts/install.sh\n\n"
        "[bold]After install:[/bold]\n"
        "  camelot configure   ← auto-detects CLIProxy, Ollama, API keys\n"
        "  camelot             ← warp into Camelot-OS",
        border_style="yellow",
    ))


def _cmd_build() -> None:
    from rich.console import Console
    console = Console()
    build_script = _REPO / "scripts" / "build_portable.py"
    if not build_script.exists():
        console.print(
            "[yellow]scripts/build_portable.py not yet created — "
            "see WARP_GATE Phase 2 (T-36→T-41)[/yellow]"
        )
        return
    import subprocess
    subprocess.run([sys.executable, str(build_script)], check=True)


def _cmd_shell_setup(argv: list[str]) -> None:
    if _FROZEN:
        # In portable binary, shell-setup module is bundled
        try:
            from camelot_shell_setup import main as ss_main  # type: ignore
            ss_main(argv)
            return
        except ImportError:
            pass
    from bin.camelot_shell_setup import main as ss_main
    ss_main(argv)


def _cmd_keys(argv: list[str]) -> None:
    if _FROZEN:
        try:
            from camelot_keys import main as keys_main  # type: ignore
            keys_main(argv)
            return
        except ImportError:
            pass
    from bin.camelot_keys import main as keys_main
    keys_main(argv)


def _cmd_update() -> None:
    from rich.console import Console
    console = Console()
    console.print("[dim]Pulling latest CLAUDE.md + cartridges from git...[/dim]")
    import subprocess
    try:
        result = subprocess.run(
            ["git", "pull", "--ff-only"],
            cwd=str(_REPO), capture_output=True, text=True, timeout=30
        )
        console.print(result.stdout or result.stderr)
    except Exception as e:
        console.print(f"[red]Update failed: {e}[/red]")


def _cmd_cockpit() -> None:
    from control_plane.runes.camelot_cli import main as control_main

    raise SystemExit(control_main())


def _cmd_completion(shell: str = "bash", install: bool = False) -> None:
    """Print shell completion script for the given shell.

    Supported shells: bash, zsh, fish, powershell
    Usage:
        eval "$(camelot completion bash)"     # activate in current shell
        camelot completion bash > /etc/bash_completion.d/camelot
    """
    _KNIGHTS = " ".join([
        "sir_boris", "sir_alex", "sir_sentinel", "sir_mnemo", "sir_codex",
        "sir_helio", "sir_link", "sir_liberte", "sir_forge", "sir_ghost",
        "sir_forge_master", "sir_gideon", "sir_octavian", "lady_apis",
    ])
    _SUBCMDS = "configure config status install build update warp shell-setup keys cockpit completion"
    _TIERS   = "T0 T1 T2 T3"

    shell = shell.lower().strip()

    if shell in ("bash", "zsh"):
        # Try to emit the bundled completion file first
        _comp_file = Path(__file__).resolve().parent / "camelot_completion_bash.sh"
        if _comp_file.exists():
            print(_comp_file.read_text(encoding="utf-8"))
            return
        # Inline fallback
        print(f'''\
# CAMELOT-OS {shell} completion (inline fallback)
_camelot_complete() {{
  local cur prev
  cur="${{COMP_WORDS[COMP_CWORD]}}"
  prev="${{COMP_WORDS[COMP_CWORD-1]}}"
  case "$prev" in
    --knight|-k) COMPREPLY=( $(compgen -W "{_KNIGHTS}" -- "$cur") ); return ;;
    --tier)      COMPREPLY=( $(compgen -W "{_TIERS}" -- "$cur") ); return ;;
    --system|-s) COMPREPLY=( $(compgen -f -- "$cur") ); return ;;
    completion)  COMPREPLY=( $(compgen -W "bash zsh fish powershell" -- "$cur") ); return ;;
  esac
  if [[ ${{COMP_CWORD}} -eq 1 ]]; then
    COMPREPLY=( $(compgen -W "{_SUBCMDS} --knight --no-context --system --verbose --version" -- "$cur") )
  fi
}}
complete -F _camelot_complete camelot
complete -F _camelot_complete ai
''')

    elif shell == "fish":
        print(f'''\
# CAMELOT-OS fish completion
# Save to: ~/.config/fish/completions/camelot.fish
set -l _knights {_KNIGHTS}
set -l _subcmds  {_SUBCMDS}

complete -c camelot -f
complete -c camelot -n '__fish_use_subcommand' -a "$_subcmds"
complete -c camelot -s k -l knight -xa "$_knights" -d 'Force specific knight'
complete -c camelot -s n -l no-context -d 'Skip CLAUDE.md injection'
complete -c camelot -s s -l system   -r -d 'Override system prompt from file'
complete -c camelot -s v -l verbose  -d 'Show routing details'
complete -c camelot -s V -l version  -d 'Print version and exit'
complete -c camelot -n '__fish_seen_subcommand_from completion' -xa 'bash zsh fish powershell'
''')

    elif shell in ("powershell", "ps", "pwsh"):
        print(f'''\
# CAMELOT-OS PowerShell completion
# Add to $PROFILE:  camelot completion powershell | Out-String | Invoke-Expression
Register-ArgumentCompleter -Native -CommandName @('camelot','ai') -ScriptBlock {{
  param($wordToComplete, $commandAst, $cursorPosition)
  $knights = @({",".join(f"'{k}'" for k in _KNIGHTS.split())})
  $subcmds = @({",".join(f"'{s}'" for s in _SUBCMDS.split())})
  $tiers   = @('T0','T1','T2','T3')
  $tokens  = $commandAst.CommandElements
  $prev    = if ($tokens.Count -ge 2) {{ $tokens[$tokens.Count - 2].Value }} else {{ '' }}
  switch ($prev) {{
    {{$_ -in '--knight','-k'}} {{ $knights | Where-Object {{ $_ -like "$wordToComplete*" }} | ForEach-Object {{ [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_) }}; return }}
    '--tier'                  {{ $tiers   | Where-Object {{ $_ -like "$wordToComplete*" }} | ForEach-Object {{ [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_) }}; return }}
    'completion'              {{ @('bash','zsh','fish','powershell') | Where-Object {{ $_ -like "$wordToComplete*" }} | ForEach-Object {{ [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_) }}; return }}
  }}
  $subcmds + @('--knight','--no-context','--system','--verbose','--version') |
    Where-Object {{ $_ -like "$wordToComplete*" }} |
    ForEach-Object {{ [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_) }}
}}
''')

    else:
        print(f"Unknown shell '{shell}'. Supported: bash, zsh, fish, powershell", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    args = sys.argv[1:]

    # Version check (before anything else)
    if any(a in ("--version", "-V") for a in args):
        print(f"CAMELOT-OS v{__version__} // WARP_GATE v{_WARP_GATE}")
        return

    # No args → warp (show banner too)
    if not args:
        _cmd_warp()
        return

    first = args[0].lstrip("-").lower() if not args[0].startswith("-") else ""

    # Route sub-commands
    if first == "configure" or first == "config":
        verbose = "--verbose" in args or "-v" in args
        _cmd_configure(verbose=verbose)
        return

    if first == "status":
        _cmd_status()
        return

    if first == "install":
        _cmd_install()
        return

    if first == "build":
        _cmd_build()
        return

    if first == "update":
        _cmd_update()
        return

    if first == "warp":
        sys.argv = [sys.argv[0]] + [a for a in sys.argv[1:] if a != "warp"]
        _cmd_warp()
        return

    if first in ("shell-setup", "shellsetup", "shell_setup"):
        _cmd_shell_setup(args[1:])
        return

    if first == "keys":
        _cmd_keys(args[1:])
        return

    if first == "cockpit":
        _cmd_cockpit()
        return

    if first == "completion":
        shell = args[1] if len(args) > 1 else "bash"
        install = "--install" in args
        _cmd_completion(shell=shell, install=install)
        return

    # Anything else (flags, --knight, etc.) → forward to warp
    if first and not first.startswith("-"):
        from control_plane.runes.camelot_cli import main as control_main
        raise SystemExit(control_main())

    _cmd_warp()


if __name__ == "__main__":
    main()
