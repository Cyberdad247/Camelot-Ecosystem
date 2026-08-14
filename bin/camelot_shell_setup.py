# SPDX-License-Identifier: MIT

"""camelot shell-setup — Install tab completion for the current shell.

Detects the active shell and installs the appropriate completion script.

Usage:
    camelot shell-setup                    # auto-detect shell
    camelot shell-setup --shell powershell
    camelot shell-setup --shell bash
    camelot shell-setup --shell zsh
    camelot shell-setup --shell fish
    camelot shell-setup --print            # print script to stdout instead of installing
"""
from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def _detect_shell() -> str:
    """Detect the currently active shell."""
    # Explicit env override
    shell_env = os.environ.get("CAMELOT_SHELL", "")
    if shell_env:
        return shell_env.lower()

    # Windows → PowerShell by default unless SHELL is set
    if platform.system() == "Windows":
        ps_ver = os.environ.get("PSVersionTable", "") or os.environ.get("SHELL", "")
        if "bash" in ps_ver.lower():
            return "bash"
        if "zsh" in ps_ver.lower():
            return "zsh"
        return "powershell"

    # Unix — read $SHELL
    shell_path = os.environ.get("SHELL", "")
    if "fish" in shell_path:
        return "fish"
    if "zsh" in shell_path:
        return "zsh"
    if "bash" in shell_path:
        return "bash"
    return "bash"


def _repo_root() -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent.parent


def _completion_script(shell: str) -> Path:
    ext_map = {"bash": "bash", "zsh": "zsh", "fish": "fish", "powershell": "ps1"}
    ext = ext_map.get(shell, "bash")
    return _repo_root() / "completions" / f"camelot.{ext}"


def _powershell_cockpit_script() -> str:
    return r"""
# CAMELOT-OS Cockpit
if (-not $script:CamelotOriginalPrompt) {
    $script:CamelotOriginalPrompt = $function:prompt
}

function Get-CamelotCockpitHeader {
    try {
        $payload = camelot --json cockpit prompt 2>$null | ConvertFrom-Json
        if (-not $payload) { return $null }

        $health = if ($payload.stale) { "STALE" } elseif ($payload.services.state) { [string]$payload.services.state } else { "WARN" }
        $cpu = if ($null -ne $payload.system.cpu_percent) { "{0:N0}%" -f [double]$payload.system.cpu_percent } else { "n/a" }
        $ram = if ($null -ne $payload.system.memory_percent) { "{0:N0}%" -f [double]$payload.system.memory_percent } else { "n/a" }
        $queue = if ($payload.queue.pending -ge 0) { [string]$payload.queue.pending } else { "?" }
        $rune = if ($payload.last_command.rune) { [string]$payload.last_command.rune } else { "shell" }
        $knight = if ($payload.last_command.knight) { [string]$payload.last_command.knight } else { "idle" }
        $latency = if ($payload.last_command.latency_ms) { "{0:N0}ms" -f [double]$payload.last_command.latency_ms } else { "n/a" }
        $services = if ($payload.services.total -gt 0) { "{0}/{1}" -f @($payload.services.green, $payload.services.total) } else { "n/a" }
        $mode = if ($payload.mode) { [string]$payload.mode } else { "off" }
        $line = "[CAMELOT {0}] svc {1} cpu {2} ram {3} q {4} last {5} {6} {7} mode {8}" -f @(
            $health, $services, $cpu, $ram, $queue, $rune, $knight, $latency, $mode
        )
        if ($payload.memory_banner) {
            return @($line, [string]$payload.memory_banner)
        }
        return @($line)
    } catch {
        return @("[CAMELOT STALE] prompt unavailable")
    }
}

function Enter-CamelotCockpit {
    $env:CAMELOT_COCKPIT_MODE = 'on'
    camelot --json cockpit refresh | Out-Null
}

function Exit-CamelotCockpit {
    Remove-Item Env:CAMELOT_COCKPIT_MODE -ErrorAction SilentlyContinue
}

function Invoke-CamelotCockpitExec {
    param(
        [Parameter(Mandatory=$true, Position=0, ValueFromRemainingArguments=$true)]
        [string[]]$InputText
    )
    $joined = $InputText -join ' '
    camelot cockpit exec $joined
}

Set-Alias cockpit-on Enter-CamelotCockpit
Set-Alias cockpit-off Exit-CamelotCockpit
Set-Alias crune Invoke-CamelotCockpitExec

function prompt {
    if ($env:CAMELOT_COCKPIT_MODE -eq 'on') {
        $headerLines = Get-CamelotCockpitHeader
        if ($headerLines) {
            foreach ($line in $headerLines) {
                Write-Host $line -ForegroundColor Cyan
            }
        }
    }

    if ($script:CamelotOriginalPrompt) {
        return & $script:CamelotOriginalPrompt
    }
    return "PS $($executionContext.SessionState.Path.CurrentLocation)> "
}
"""


def _install_powershell(script: Path, console) -> None:
    # Prefer the PowerShell 7 profile in the local Documents folder (not OneDrive)
    candidates = [
        Path.home() / "Documents" / "PowerShell" / "profile.ps1",       # PS7 local
        Path.home() / "Documents" / "WindowsPowerShell" / "profile.ps1", # PS5 local
        Path.home() / "OneDrive" / "Documents" / "WindowsPowerShell" / "profile.ps1",
        Path.home() / "OneDrive" / "Documents" / "PowerShell" / "profile.ps1",
    ]

    profile_path = None
    # Try PS query first — but fall back gracefully
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "[System.Environment]::GetFolderPath('MyDocuments')"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            docs = Path(result.stdout.strip())
            candidates.insert(0, docs / "PowerShell" / "profile.ps1")
            candidates.insert(1, docs / "WindowsPowerShell" / "profile.ps1")
    except Exception:
        pass

    # Pick the first candidate whose parent is reachable
    for c in candidates:
        try:
            c.parent.mkdir(parents=True, exist_ok=True)
            if not c.exists():
                c.touch()
            profile_path = c
            break
        except (OSError, PermissionError):
            continue

    if not profile_path:
        profile_path = Path.home() / "Documents" / "PowerShell" / "profile.ps1"
        profile_path.parent.mkdir(parents=True, exist_ok=True)
        profile_path.touch()

    content = script.read_text(encoding="utf-8")
    cockpit_content = _powershell_cockpit_script()
    marker = "# CAMELOT-OS Completion"
    cockpit_marker = "# CAMELOT-OS Cockpit"

    profile_path.parent.mkdir(parents=True, exist_ok=True)
    if not profile_path.exists():
        profile_path.touch()

    existing = profile_path.read_text(encoding="utf-8") if profile_path.exists() else ""
    if marker not in existing:
        with profile_path.open("a", encoding="utf-8") as f:
            f.write(f"\n{marker}\n{content}\n")
        console.print(f"  [green][OK][/green] Appended completion to: {profile_path}")
    else:
        console.print(f"  [yellow][!!] Completion already in profile: {profile_path}[/yellow]")

    if cockpit_marker not in existing:
        with profile_path.open("a", encoding="utf-8") as f:
            f.write(f"\n{cockpit_content}\n")
        console.print(f"  [green][OK][/green] Appended cockpit prompt helpers to: {profile_path}")
    else:
        console.print(f"  [yellow][!!] Cockpit helpers already in profile: {profile_path}[/yellow]")

    console.print("  [dim]Restart PowerShell or run: . $PROFILE[/dim]")


def _install_bash(script: Path, console) -> None:
    rc = Path.home() / ".bashrc"
    marker = "# CAMELOT-OS Completion"

    existing = rc.read_text(encoding="utf-8") if rc.exists() else ""
    if marker in existing:
        console.print(f"  [yellow][!!] Completion already in {rc}[/yellow]")
        return

    with rc.open("a", encoding="utf-8") as f:
        f.write(f"\n{marker}\nsource \"{script}\"\n")

    console.print(f"  [green][OK][/green] Added to {rc}")
    console.print("  [dim]Run: source ~/.bashrc[/dim]")


def _install_zsh(script: Path, console) -> None:
    # Try fpath installation first (preferred)
    fpath_dir = Path.home() / ".zsh" / "completions"
    fpath_dir.mkdir(parents=True, exist_ok=True)
    dest = fpath_dir / "_camelot"
    shutil.copy2(str(script), str(dest))
    console.print(f"  [green][OK][/green] Copied completion to {dest}")

    zshrc = Path.home() / ".zshrc"
    marker = "# CAMELOT-OS Completion"
    existing = zshrc.read_text(encoding="utf-8") if zshrc.exists() else ""
    fpath_line = f'fpath=("{fpath_dir}" $fpath)'

    if marker not in existing:
        with zshrc.open("a", encoding="utf-8") as f:
            f.write(f"\n{marker}\n{fpath_line}\nautoload -Uz compinit && compinit\n")
        console.print(f"  [green][OK][/green] Updated {zshrc}")

    console.print("  [dim]Run: source ~/.zshrc[/dim]")


def _install_fish(script: Path, console) -> None:
    fish_completions = Path.home() / ".config" / "fish" / "completions"
    fish_completions.mkdir(parents=True, exist_ok=True)
    dest = fish_completions / "camelot.fish"
    shutil.copy2(str(script), str(dest))
    console.print(f"  [green][OK][/green] Copied to {dest}")
    console.print("  [dim]Fish completions load automatically on next shell start[/dim]")


def run_shell_setup(shell: str | None = None, print_only: bool = False) -> None:
    from rich.console import Console
    console = Console()

    detected = _detect_shell()
    active_shell = shell or detected

    console.print(
        f"\n  [bold yellow]CAMELOT-OS Shell Setup[/bold yellow] — "
        f"shell: [cyan]{active_shell}[/cyan]"
        + ("" if shell else " [dim](auto-detected)[/dim]")
    )

    script = _completion_script(active_shell)
    if not script.exists():
        console.print(f"  [red]Completion script not found: {script}[/red]")
        return

    if print_only:
        if active_shell == "powershell":
            console.print(script.read_text(encoding="utf-8"), markup=False)
            console.print(_powershell_cockpit_script(), markup=False)
        else:
            console.print(script.read_text(encoding="utf-8"), markup=False)
        return

    console.print(f"  [dim]Source: {script}[/dim]")

    if active_shell == "powershell":
        _install_powershell(script, console)
    elif active_shell == "bash":
        _install_bash(script, console)
    elif active_shell == "zsh":
        _install_zsh(script, console)
    elif active_shell == "fish":
        _install_fish(script, console)
    else:
        console.print(f"  [yellow]Unknown shell '{active_shell}' — printing script:[/yellow]")
        console.print(script.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> None:
    import argparse
    p = argparse.ArgumentParser(
        prog="camelot shell-setup",
        description="Install Camelot-OS tab completion for your shell"
    )
    p.add_argument(
        "--shell", choices=["bash", "zsh", "fish", "powershell"],
        help="Target shell (auto-detected if omitted)"
    )
    p.add_argument(
        "--print", dest="print_only", action="store_true",
        help="Print the completion script to stdout instead of installing"
    )
    args = p.parse_args(argv)
    run_shell_setup(shell=args.shell, print_only=args.print_only)


if __name__ == "__main__":
    main()
