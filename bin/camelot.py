# SPDX-License-Identifier: MIT

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
    camelot status [--json|--quick]  Probe all services via boot sequencer (fast snapshot path)
    camelot boot [--quick|--full|--json|--snapshot|--skip a,b]  Full //BOOT via awaken
    camelot dev [--scope pwa|bifrost|vault|voice|all]  Rapid scoped test+typecheck loop
    camelot hermes             Show VPS Hermes_Prime + Bifrost bridge status
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

import argparse
import json
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

_WRAPPER_SUBCOMMANDS = {"configure", "config", "status", "boot", "dev", "hermes", "vps-hermes", "install", "build", "update", "warp", "shell-setup", "keys", "cockpit", "completion", "moto", "s26", "excalibur", "tmux", "vps-tmux", "s2s", "voice-s2s", "omni-s2s", "observatory", "glass", "compendium", "rpg", "cua", "computer-use", "reya-cua", "reya", "magsafe", "magsafe-audio", "magsafe-bridge"}


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


def _cmd_status(argv: list[str] | None = None) -> None:
    """Probe all services via the boot sequencer (single source of truth)."""
    argv = argv or []
    use_json = "--json" in argv
    use_snapshot = "--snapshot" in argv or "--quick" in argv
    try:
        from control_plane.infra import boot_sequence as _bs
        home = _bs._detect_home()
        if use_snapshot and hasattr(_bs, "try_snapshot_boot"):
            snap = _bs.try_snapshot_boot(home)
            if snap is not None:
                if use_json:
                    print(json.dumps(snap, indent=2))
                else:
                    s = snap.get("_summary", {})
                    print(f"AWAKEN (snapshot) {s.get('required_ok', '?')}/{s.get('required_total', '?')} required green")
                return
        results = _bs.run_boot(home, quick=True)
        if use_json:
            print(json.dumps(results, indent=2))
        else:
            green = sum(1 for k, v in results.items() if not k.startswith("_") and v["ok"])
            total = sum(1 for k in results if not k.startswith("_"))
            print(f"AWAKEN {green}/{total} phases in {results.get('_total_ms', '?')}ms")
        return
    except Exception as exc:
        print(f"[yellow]sequencer status failed ({exc}); falling back to configure status[/yellow]")
    from bin.camelot_configure import show_status
    show_status()


def _cmd_boot(argv: list[str]) -> None:
    """Full //BOOT via bin/awaken.py argument forwarding.

    Usage: camelot boot [--quick|--full] [--json] [--status] [--snapshot] [--skip a,b] [--no-hud]
    """
    import subprocess
    script = _REPO / "bin" / "awaken.py"
    cmd = [sys.executable, str(script)]
    # Default to status+snapshot fast path when no flags given
    if len(argv) == 0:
        cmd += ["--status", "--snapshot"]
    else:
        cmd += argv
    raise SystemExit(subprocess.run(cmd).returncode)


def _cmd_dev(argv: list[str]) -> None:
    """Rapid scoped test+typecheck loop (Windows-safe, no make/curl).

    Usage: camelot dev [--scope pwa|bifrost|vault|voice|all]
    """
    import subprocess
    scope = "all"
    for i, a in enumerate(argv):
        if a == "--scope" and i + 1 < len(argv):
            scope = argv[i + 1].lower()
    NPM = "npm.cmd" if sys.platform == "win32" else "npm"
    jobs: list[list[str]] = []
    if scope in ("vault", "all"):
        jobs.append([NPM, "run", "test:vault"])
    if scope in ("bifrost", "all"):
        jobs.append([NPM, "run", "test:bifrost"])
    if scope in ("voice", "all"):
        jobs.append([NPM, "run", "test:voice"])
    if scope in ("pwa", "all"):
        jobs.append([NPM, "--prefix", "apps/pwa", "run", "typecheck"])
    if not jobs:
        print(f"Unknown scope '{scope}'. Use pwa|bifrost|vault|voice|all", file=sys.stderr)
        raise SystemExit(2)
    for cmd in jobs:
        print(f"+ {' '.join(cmd)}")
        rc = subprocess.run(cmd, cwd=str(_REPO)).returncode
        if rc != 0:
            raise SystemExit(rc)


def _cmd_hermes(argv: list[str]) -> None:
    parser = argparse.ArgumentParser(
        prog="camelot hermes",
        description="Show VPS Hermes_Prime and Bifrost bridge status.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument(
        "--probe-live",
        dest="probe_live",
        action="store_true",
        default=False,
        help="Run read-only TCP probes against VPS bridge ports",
    )
    parser.add_argument(
        "--no-probe",
        dest="probe_live",
        action="store_false",
        help="Skip live probes and show configured contract only",
    )
    args = parser.parse_args(argv)

    from control_plane.infra.vps_hermes_prime import (
        format_vps_hermes_prime_status,
        summarize_vps_hermes_prime,
    )

    status = summarize_vps_hermes_prime(root=_REPO, probe_live=args.probe_live)
    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print(format_vps_hermes_prime_status(status))


def _cmd_moto(argv: list[str]) -> None:
    """Launch native scrcpy mirror for Motorola Moto G Power 5G."""
    import subprocess
    scrcpy_bin = Path(r"C:\Users\vizio\AppData\Local\CamelotTools\scrcpy\scrcpy.exe")
    if not scrcpy_bin.exists():
        scrcpy_bin = Path("scrcpy")
    cmd = [str(scrcpy_bin), "-s", "ZY22L3K36P", "--window-title", "Camelot-OS | Motorola Moto G Power 5G"] + argv
    print(f"🚀 [MOTO_MIRROR] Launching Motorola Moto G Power 5G Mirror...")
    subprocess.Popen(cmd)


def _cmd_s26(argv: list[str]) -> None:
    """Launch native scrcpy mirror for Samsung Galaxy S26 Ultra (Excalibur)."""
    import subprocess
    scrcpy_bin = Path(r"C:\Users\vizio\AppData\Local\CamelotTools\scrcpy\scrcpy.exe")
    if not scrcpy_bin.exists():
        scrcpy_bin = Path("scrcpy")
    cmd = [str(scrcpy_bin), "-s", "R3GL2009ZCH", "--window-title", "Camelot-OS | Excalibur S26 Ultra"] + argv
    print(f"🚀 [EXCALIBUR_MIRROR] Launching Excalibur S26 Ultra Mirror...")
    subprocess.Popen(cmd)


def _cmd_qtscrcpy(argv: list[str]) -> None:
    """Launch QtScrcpy GUI Orchestrator for multi-device Android management."""
    import subprocess
    qtscrcpy_dir = Path(r"C:\Users\vizio\AppData\Local\CamelotTools\QtScrcpy-v4.1.1\QtScrcpy-win-x64-v4.1.1")
    qtscrcpy_bin = qtscrcpy_dir / "QtScrcpy.exe"
    if not qtscrcpy_bin.exists():
        print(f"❌ [QTSCRCPY] QtScrcpy binary not found at {qtscrcpy_bin}", file=sys.stderr)
        return
    print(f"🚀 [QTSCRCPY] Launching QtScrcpy GUI Orchestrator...")
    subprocess.Popen([str(qtscrcpy_bin)] + argv, cwd=str(qtscrcpy_dir))


def _cmd_tmux(argv: list[str]) -> None:
    """Connect to VPS Hub Tmux Multiplexer Bus."""
    import subprocess
    key = Path.home() / ".ssh" / "camelot_oci_ed25519"
    cmd = ["ssh", "-i", str(key), "-o", "StrictHostKeyChecking=no", "-t", "root@100.110.180.18", "tmux a -t camelot-bus || tmux new-session -s camelot-bus"]
    print("⚡ [VPS_TMUX] Connecting to VPS Hub Tmux Bus (root@100.110.180.18)...")
    subprocess.run(cmd)


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
    from control_plane.camelot_cli import main as control_main

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
    _SUBCMDS = "configure config status boot dev hermes vps-hermes moto s26 qtscrcpy tmux vps-tmux install build update warp shell-setup keys cockpit completion"
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


def _cmd_s2s(argv: list[str]) -> None:
    """Omni Speech-to-Speech (S2S) CLI with RadixAttention prefix caching and Agora RTC.

    Usage: camelot s2s ["prompt text"] [--knight id] [--channel name] [--chunked] [--turns n] [--json] [--stats]
    """
    import argparse
    import math
    import struct
    parser = argparse.ArgumentParser(prog="camelot s2s", description="Camelot Omni S2S Engine CLI")
    parser.add_argument("query", nargs="*", default=[], help="Prompt text for S2S turn")
    parser.add_argument("--knight", "-k", default="reya_companion", help="Channeled Knight persona")
    parser.add_argument("--channel", "-c", default="camelot_omni_s2s", help="Agora RTC SD-RTN channel")
    parser.add_argument("--chunked", action="store_true", help="Simulate 100ms chunked prefill & speculative overlap")
    parser.add_argument("--turns", "-t", type=int, default=1, help="Number of turns to simulate")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--stats", action="store_true", help="Display Radix cache and Agora RTC stats")
    parsed = parser.parse_args(argv)

    s2s_dir = _REPO / "02_FORGE" / "assimilation" / "omni_s2s"
    if str(s2s_dir) not in sys.path:
        sys.path.insert(0, str(s2s_dir))
    from omni_s2s_engine import get_omni_s2s_engine

    engine = get_omni_s2s_engine()

    if parsed.stats:
        stats = {
            "radix_cache": engine.radix_cache.get_stats(),
            "agora_rtc": engine.agora_bridge.get_stats(),
            "turn_counter": engine.turn_counter,
        }
        if parsed.json:
            print(json.dumps(stats, indent=2))
        else:
            print("=== OMNI S2S SYSTEM STATUS ===")
            print(f"Channel:     {stats['agora_rtc']['channel']} (Connected: {stats['agora_rtc']['connected']})")
            print(f"SHM Slab:    {stats['agora_rtc']['shm_slab']}")
            print(f"Radix Cache: {stats['radix_cache']['cached_tokens']}/{stats['radix_cache']['max_tokens']} tokens")
            print(f"Cache Hits:  {stats['radix_cache']['hits']} (Rate: {stats['radix_cache']['hit_rate_pct']}%)")
            print(f"TTFT Saved:  {stats['radix_cache']['estimated_ttft_saving_ms']} ms")
            print(f"Total Turns: {engine.turn_counter}")
        return

    prompt_text = " ".join(parsed.query) if parsed.query else "Status check on fortress systems"
    samples = [int(1500 * math.sin(2 * math.pi * 220 * i / 16000)) for i in range(8000)]
    pcm_bytes = struct.pack(f"<{len(samples)}h", *samples)

    results = []
    for turn_idx in range(parsed.turns):
        turn_prompt = prompt_text if parsed.turns == 1 else f"{prompt_text} (turn {turn_idx + 1})"
        if parsed.chunked:
            chunks = [pcm_bytes[i:i + 3200] for i in range(0, len(pcm_bytes), 3200)]
            res = engine.process_chunked_speech_turn(
                chunks,
                transcript_hint=turn_prompt,
                knight_id=parsed.knight,
                enable_speculative_decode=True,
            )
        else:
            res = engine.process_speech_turn(
                pcm_bytes,
                transcript_hint=turn_prompt,
                knight_id=parsed.knight,
            )
        results.append(res.to_dict())

    if parsed.json:
        print(json.dumps(results if len(results) > 1 else results[0], indent=2))
    else:
        for r in results:
            print(f"\n[S2S] OMNI S2S TURN {r['turn_index']}  //  Knight: {r['active_knight']}")
            print(f"  Input:       {r['input_text']}")
            print(f"  Response:    {r['response_text']}")
            print(f"  TTFA:        {r['estimated_ttfa_ms']} ms")
            print(f"  Radix Cache: {r['radix_cache_hit_rate']}% hit rate ({r['radix_cache_hit_tokens']}/{r['radix_total_tokens']} tokens)")
            if r.get("is_chunked_prefill"):
                print(f"  Prefill:     100ms Chunked ({r['chunk_count']} chunks, {r['speculative_overlap_ms']}ms speculative overlap)")
            print(f"  Transport:   Agora SD-RTN ({r['channel_name']})")


def _cmd_observatory(argv: list[str]) -> None:
    """Project Speculum: The Glass Observatory & Living Compendium CLI.

    Usage: camelot observatory [--glass|--rpg|--transcripts|--evals|--compendium|--json]
    """
    import argparse
    parser = argparse.ArgumentParser(prog="camelot observatory", description="Camelot Glass Observatory & Living Compendium")
    parser.add_argument("--glass", action="store_true", help="Display full read-only Glass Wall HUD")
    parser.add_argument("--rpg", action="store_true", help="Display Sovereign RPG leaderboard and mastery stats")
    parser.add_argument("--transcripts", action="store_true", help="Display recent conversational transcripts")
    parser.add_argument("--evals", action="store_true", help="Display autonomous implementation evaluation grades")
    parser.add_argument("--compendium", action="store_true", help="Print the Living Compendium markdown directly")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parsed = parser.parse_args(argv)

    from control_plane.observatory.glass_observatory import get_glass_observatory
    obs = get_glass_observatory()

    if parsed.compendium:
        print(obs.get_compendium_markdown())
        return

    view_type = "all"
    if parsed.rpg:
        view_type = "rpg"
    elif parsed.transcripts:
        view_type = "transcripts"
    elif parsed.evals:
        view_type = "evaluations"

    data = obs.get_glass_wall_view(view_type)

    if parsed.json:
        print(json.dumps(data, indent=2))
        return

    print("=" * 72)
    print("  [GLASS WALL] THE IMPENETRABLE SOVEREIGN OBSERVATORY")
    print("  Status: LOCKED READ-ONLY (WORM) // Zero Hotpath Contention")
    print(f"  Compendium: {data['compendium_path']}")
    print("=" * 72)

    if "leaderboard" in data:
        print("\n[SOVEREIGN TENANT XP LEADERBOARD]:")
        for t in data["leaderboard"]["tenants"]:
            print(f"  - {t['tenant_id']:<15} {t['title']:<22} Lvl {t['sovereign_level']:<3} ({t['xp']:,} XP, {t['xp_to_next']:,} to next) [{t['dialogue_turns']} turns]")
        print("\n[ROUND TABLE KNIGHT MASTERY]:")
        for k in data["leaderboard"]["knights"]:
            ach = f" [{', '.join(k['achievements'])}]" if k['achievements'] else ""
            print(f"  - {k['knight_id']:<18} {k['title']:<24} Lvl {k['level']:<3} ({k['xp']:,} XP) [Turns: {k['turns_transcribed']}, Evals: {k['tasks_evaluated']}]{ach}")

    if "transcripts" in data:
        print("\n[RECENT CONVERSATIONAL TRANSCRIPTS]:")
        if not data["transcripts"]:
            print("  (No transcripts captured yet)")
        for tr in data["transcripts"][-5:]:
            print(f"  [{tr['turn_id']}] {tr['tenant_id']} -> {tr['knight_id']} (+{tr['xp_awarded']} XP | TTFA: {tr['ttfa_ms']}ms)")
            print(f"    Prompt:   \"{tr['user_prompt']}\"")
            print(f"    Response: \"{tr['knight_response']}\"")

    if "evaluations" in data:
        print("\n[AUTONOMOUS IMPLEMENTATION EVALUATIONS]:")
        if not data["evaluations"]:
            print("  (No evaluations recorded yet)")
        for ev in data["evaluations"][-5:]:
            print(f"  [{ev['eval_id']}] {ev['knight_id']} -> Rank [{ev['grade']}: {ev['score']}/100] (+{ev['xp_awarded']} XP)")
            print(f"    Task:     {ev['task_description']}")
            print(f"    Verdict:  {ev['rationale']}")


def _cmd_cua(argv: list[str]) -> None:
    """Universal Sovereign Computer-Use Agent (CUA) CLI via REYA Fabric.

    Usage:
        camelot cua status [--json]
        camelot cua click <X> <Y> [--button left|right] [--clicks 1|2] [--device desktop|mobile] [--json]
        camelot cua move <X> <Y> [--device desktop|mobile] [--json]
        camelot cua drag <X1> <Y1> <X2> <Y2> [--device desktop|mobile] [--json]
        camelot cua type <TEXT> [--delay-ms 10] [--json]
        camelot cua key <KEY> [--json]
        camelot cua hotkey <KEYS...> [--json]
        camelot cua capture [--device desktop|mobile] [--json]
        camelot cua diff <HASH1> <HASH2> [--json]
    """
    import argparse
    parser = argparse.ArgumentParser(prog="camelot cua", description="Camelot-OS Universal Sovereign CUA Engine (trycua/cua assimilation)")
    sub = parser.add_subparsers(dest="action", help="CUA sub-command")

    p_status = sub.add_parser("status", help="Get CUA engine & REYA fabric status")
    p_status.add_argument("--json", action="store_true", help="Output JSON")

    p_click = sub.add_parser("click", help="Click normalized coordinates [0.0, 1.0]")
    p_click.add_argument("x", type=float, help="Normalized X in [0.0, 1.0]")
    p_click.add_argument("y", type=float, help="Normalized Y in [0.0, 1.0]")
    p_click.add_argument("--button", default="left", choices=["left", "right", "middle"])
    p_click.add_argument("--clicks", type=int, default=1)
    p_click.add_argument("--device", default="desktop", choices=["desktop", "desktop_4k", "mobile_s26_ultra", "mobile_moto_g"])
    p_click.add_argument("--json", action="store_true")

    p_move = sub.add_parser("move", help="Move mouse to normalized coordinates")
    p_move.add_argument("x", type=float)
    p_move.add_argument("y", type=float)
    p_move.add_argument("--device", default="desktop")
    p_move.add_argument("--json", action="store_true")

    p_drag = sub.add_parser("drag", help="Drag and drop from start to end")
    p_drag.add_argument("x1", type=float)
    p_drag.add_argument("y1", type=float)
    p_drag.add_argument("x2", type=float)
    p_drag.add_argument("y2", type=float)
    p_drag.add_argument("--button", default="left")
    p_drag.add_argument("--device", default="desktop")
    p_drag.add_argument("--json", action="store_true")

    p_type = sub.add_parser("type", help="Type text sequence")
    p_type.add_argument("text", type=str)
    p_type.add_argument("--delay-ms", type=int, default=10)
    p_type.add_argument("--json", action="store_true")

    p_key = sub.add_parser("key", help="Press single key")
    p_key.add_argument("key", type=str)
    p_key.add_argument("--json", action="store_true")

    p_hotkey = sub.add_parser("hotkey", help="Execute hotkey combo")
    p_hotkey.add_argument("keys", nargs="+", type=str)
    p_hotkey.add_argument("--json", action="store_true")

    p_capture = sub.add_parser("capture", help="Capture viewport frame hash")
    p_capture.add_argument("--device", default="desktop")
    p_capture.add_argument("--json", action="store_true")

    p_diff = sub.add_parser("diff", help="Verify screen state diff")
    p_diff.add_argument("hash1", type=str)
    p_diff.add_argument("hash2", type=str)
    p_diff.add_argument("--json", action="store_true")

    parsed = parser.parse_args(argv)

    import importlib.util
    from pathlib import Path
    _fab_path = Path(__file__).resolve().parent.parent / "02_FORGE" / "assimilation" / "reya" / "reya_fabric_layer.py"
    _spec = importlib.util.spec_from_file_location("reya_fabric_layer", str(_fab_path))
    _mod = importlib.util.module_from_spec(_spec)
    sys.modules["reya_fabric_layer"] = _mod
    _spec.loader.exec_module(_mod)

    fabric = _mod.get_reya_fabric()

    if not parsed.action or parsed.action == "status":
        status = fabric.get_status()
        if getattr(parsed, "json", False):
            print(json.dumps(status, indent=2))
        else:
            print("=" * 68)
            print("  [CUA] UNIVERSAL SOVEREIGN COMPUTER-USE AGENT (REYA FABRIC)")
            print(f"  Active Knight:   {status['active_name']} ({status['active_knight']})")
            print(f"  Driver Attached: {status['cua_driver_attached']}")
            print(f"  Viewport:        {status['cua_viewport']}")
            print(f"  Memory Ceiling:  {status['cgroups_memory_max_mb']} MB (Rule 7)")
            print(f"  Status:          {status['status']}")
            print("=" * 68)
        return

    action_map = {
        "click": ("cua_mouse_click", {"norm_x": getattr(parsed, "x", 0.5), "norm_y": getattr(parsed, "y", 0.5), "button": getattr(parsed, "button", "left"), "clicks": getattr(parsed, "clicks", 1)}),
        "move": ("cua_mouse_move", {"norm_x": getattr(parsed, "x", 0.5), "norm_y": getattr(parsed, "y", 0.5)}),
        "drag": ("cua_mouse_drag", {"start_x": getattr(parsed, "x1", 0.0), "start_y": getattr(parsed, "y1", 0.0), "end_x": getattr(parsed, "x2", 0.5), "end_y": getattr(parsed, "y2", 0.5), "button": getattr(parsed, "button", "left")}),
        "type": ("cua_keyboard_type", {"text": getattr(parsed, "text", ""), "delay_ms": getattr(parsed, "delay_ms", 10)}),
        "key": ("cua_key_press", {"key": getattr(parsed, "key", "Return")}),
        "hotkey": ("cua_hotkey", {"keys": getattr(parsed, "keys", ["ctrl", "c"])}),
        "capture": ("cua_screen_capture", {}),
        "diff": ("cua_screen_diff_verify", {"pre_hash": getattr(parsed, "hash1", ""), "post_hash": getattr(parsed, "hash2", "")}),
    }

    if parsed.action in action_map:
        act_type, params = action_map[parsed.action]
        res = fabric.execute_fabric_action(act_type, params)
        if getattr(parsed, "json", False):
            print(json.dumps(res, indent=2))
        else:
            c_exec = res.get("result", {}).get("cua_driver_execution", {})
            print(f"[CUA] Action '{act_type}' Executed Successfully by [{res['speaking_name']}]")
            if "physical_coords" in c_exec:
                print(f"  Normalized:  {c_exec['normalized_coords']} -> Physical: {c_exec['physical_coords']} ({c_exec['device']})")
            elif "start_physical" in c_exec:
                print(f"  Drag:        {c_exec['start_physical']} -> {c_exec['end_physical']} ({c_exec['device']})")
            elif "char_count" in c_exec:
                print(f"  Typed:       {c_exec['char_count']} chars (preview: {c_exec['masked_preview']})")
            elif "state_hash" in c_exec:
                print(f"  Captured:    Frame Hash: {c_exec['state_hash']} ({c_exec['viewport']['width']}x{c_exec['viewport']['height']})")
            elif "state_changed" in c_exec:
                print(f"  Diff:        Changed={c_exec['state_changed']}, Delta={c_exec['delta_pct']}, Verified={c_exec['verified']}")
            print(f"  Latency:     {c_exec.get('latency_ms', 0)} ms")


def _cmd_reya(argv: list[str]) -> None:
    """REYA Universal Knight Fabric Layer & Kinetic Handshake CLI.

    Usage:
        camelot reya status [--json]
        camelot reya handshake [--knight <id>] [--grant|--revoke|--status] [--json]
        camelot reya switch <knight_id> [--json]
        camelot reya reset [--json]
    """
    import argparse
    parser = argparse.ArgumentParser(prog="camelot reya", description="Camelot-OS REYA Universal Kinetic Fabric Layer")
    sub = parser.add_subparsers(dest="action", help="REYA sub-command")

    p_status = sub.add_parser("status", help="Display REYA fabric and active Knight status")
    p_status.add_argument("--json", action="store_true")

    p_hsk = sub.add_parser("handshake", help="Manage Knight kinetic handshake clearance")
    p_hsk.add_argument("--knight", type=str, default=None, help="Knight ID to inspect or manage")
    p_hsk.add_argument("--grant", action="store_true", help="Grant explicit user allowance for kinetic access")
    p_hsk.add_argument("--revoke", action="store_true", help="Revoke active kinetic handshake lease")
    p_hsk.add_argument("--json", action="store_true")

    p_switch = sub.add_parser("switch", help="Switch active vocal persona to Knight")
    p_switch.add_argument("knight_id", type=str, help="Target Knight ID or alias")
    p_switch.add_argument("--json", action="store_true")

    p_reset = sub.add_parser("reset", help="Reset REYA to default companion persona")
    p_reset.add_argument("--json", action="store_true")

    parsed = parser.parse_args(argv)

    import importlib.util
    from pathlib import Path
    _fab_path = Path(__file__).resolve().parent.parent / "02_FORGE" / "assimilation" / "reya" / "reya_fabric_layer.py"
    _spec = importlib.util.spec_from_file_location("reya_fabric_layer", str(_fab_path))
    _mod = importlib.util.module_from_spec(_spec)
    sys.modules["reya_fabric_layer"] = _mod
    _spec.loader.exec_module(_mod)

    fabric = _mod.get_reya_fabric()

    if not parsed.action or parsed.action == "status":
        status = fabric.get_status()
        if getattr(parsed, "json", False):
            print(json.dumps(status, indent=2))
        else:
            print("=" * 68)
            print("  [REYA] UNIVERSAL KNIGHT KINETIC FABRIC & SENSORY INGRESS")
            print(f"  Active Persona:  {status['active_name']} ({status['active_knight']})")
            print(f"  Voice Engine:    {status['active_engine']}")
            print(f"  CUA Driver:      Attached={status['cua_driver_attached']} ({status['cua_viewport']})")
            print(f"  Handshake:       Active={status['handshake_active']} (ID: {status['handshake_id']})")
            print(f"  Memory Ceiling:  {status['cgroups_memory_max_mb']} MB (Rule 7)")
            print(f"  Available:       {len(status['available_knights'])} Knights")
            print("=" * 68)
        return

    if parsed.action == "switch":
        res = fabric.switch_knight(parsed.knight_id)
        if getattr(parsed, "json", False):
            print(json.dumps(res, indent=2))
        else:
            print(f"[REYA] Channeled Knight Persona: {res['display_name']} ({res['active_knight_id']})")
            print(f"  Spoken Greeting: \"{res['greeting_spoken']}\"")
            print(f"  Voice Engine:    {res['voice_engine']}")
        return

    if parsed.action == "reset":
        res = fabric.switch_knight("reya_companion")
        if getattr(parsed, "json", False):
            print(json.dumps(res, indent=2))
        else:
            print("[REYA] Reset to Default Companion Persona: REYA (The Sovereign Companion)")
        return

    if parsed.action == "handshake":
        target_k = parsed.knight or fabric.active_knight_id
        gate = fabric.handshake_gate
        if not gate:
            print("[ERROR] Handshake gate not loaded.")
            return

        if parsed.grant:
            lease = fabric.grant_kinetic_handshake(target_k)
            if getattr(parsed, "json", False):
                print(json.dumps(lease.to_dict(), indent=2))
            else:
                print(f"[REYA HANDSHAKE] GRANTED user allowance for Knight [{target_k}]")
                print(f"  Handshake ID: {lease.handshake_id}")
                print(f"  Autonomy:     {lease.autonomy_tier.value}")
                print(f"  Allowed:      {', '.join(lease.allowed_actions[:3])}...")
            return

        if parsed.revoke:
            ok = fabric.revoke_kinetic_handshake(target_k)
            if getattr(parsed, "json", False):
                print(json.dumps({"revoked": ok, "knight": target_k}, indent=2))
            else:
                print(f"[REYA HANDSHAKE] Revoked kinetic access for Knight [{target_k}]")
            return

        # Default: inspect handshake and autonomy evaluation
        autonomy_tier, level, rationale = gate.evaluate_knight_autonomy(target_k)
        active_l = gate.get_active_lease(target_k)
        res_info = {
            "knight_id": target_k,
            "autonomy_tier": autonomy_tier.value,
            "level": level,
            "rationale": rationale,
            "active_handshake": active_l.to_dict() if active_l else None,
        }
        if getattr(parsed, "json", False):
            print(json.dumps(res_info, indent=2))
        else:
            print("=" * 68)
            print(f"  [REYA HANDSHAKE PROTOCOL] Knight: {target_k}")
            print(f"  Autonomy Tier:  {autonomy_tier.value}")
            print(f"  Mastery Level:  Level {level}")
            print(f"  Rationale:      {rationale}")
            print(f"  Active Lease:   {active_l.handshake_id if active_l else 'None (Approval Required)'}")
            print("=" * 68)


def _cmd_magsafe(argv: list[str]) -> None:
    """MagSafe Ambient Voice Recorder & Kinetic Action Item Dispatcher CLI.

    Usage:
        camelot magsafe status [--json]
        camelot magsafe ingest <file> [--knight <id>] [--tenant <name>] [--dispatch] [--json]
    """
    import argparse
    import importlib.util
    parser = argparse.ArgumentParser(
        prog="camelot magsafe",
        description="MagSafe Voice Recorder Audio Processor & Kinetic Action Item Dispatcher",
    )
    sub = parser.add_subparsers(dest="action", help="MagSafe sub-command")

    p_status = sub.add_parser("status", help="Display MagSafe Audio Sentinel & Glass Observatory bridge status")
    p_status.add_argument("--json", action="store_true", help="Output JSON")

    p_ingest = sub.add_parser("ingest", help="Ingest audio recording / transcript and dispatch kinetic tasks")
    p_ingest.add_argument("file", type=str, help="Audio file path (.m4a, .wav, .opus, .pcm, .txt)")
    p_ingest.add_argument("--knight", "-k", type=str, default="SIR_HELIOS", help="Attributed Knight ID")
    p_ingest.add_argument("--tenant", "-t", type=str, default="Vizion Sky", help="Attributed Sovereign Tenant")
    p_ingest.add_argument("--dispatch", "-d", action="store_true", help="Auto-dispatch extracted action items through REYA")
    p_ingest.add_argument("--json", action="store_true", help="Output JSON result")

    parsed = parser.parse_args(argv)

    bridge_path = _REPO / "02_FORGE" / "assimilation" / "magsafe" / "magsafe_audio_bridge.py"
    if not bridge_path.exists():
        print(f"Error: MagSafe audio bridge not found at {bridge_path}", file=sys.stderr)
        sys.exit(1)

    spec = importlib.util.spec_from_file_location("magsafe_audio_bridge", str(bridge_path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["magsafe_audio_bridge"] = mod
    spec.loader.exec_module(mod)

    bridge = mod.get_magsafe_audio_bridge()

    if parsed.action == "status" or parsed.action is None:
        status_info = {
            "status": "ARMED_AND_ACTIVE",
            "memory_ceiling_mb": bridge.cgroups_memory_max_mb,
            "recorded_sessions": len(bridge.get_sessions()),
            "glass_observatory_tap": "ACTIVE" if mod.get_glass_observatory is not None else "INACTIVE",
            "reya_fabric_layer": "ACTIVE" if mod.get_reya_fabric is not None else "INACTIVE",
            "handshake_gate": "ACTIVE" if mod.get_handshake_gate is not None else "INACTIVE",
        }
        if getattr(parsed, "json", False):
            print(json.dumps(status_info, indent=2))
        else:
            print("=" * 72)
            print("  [MAGSAFE AUDIO SENTINEL & KINETIC ACTION DISPATCHER]")
            print(f"  Status: {status_info['status']} (MemoryMax: {status_info['memory_ceiling_mb']}MB)")
            print(f"  Recorded Sessions:     {status_info['recorded_sessions']}")
            print(f"  Glass Observatory Tap: {status_info['glass_observatory_tap']}")
            print(f"  REYA Fabric Layer:     {status_info['reya_fabric_layer']}")
            print(f"  Handshake Gate:        {status_info['handshake_gate']}")
            print("=" * 72)
        return

    if parsed.action == "ingest":
        res = bridge.process_audio_file(
            audio_file_path=parsed.file,
            target_knight=parsed.knight,
            tenant_id=parsed.tenant,
            auto_dispatch=parsed.dispatch,
        )
        if getattr(parsed, "json", False):
            print(json.dumps(res.to_dict(), indent=2))
        else:
            print(f"\n[MAGSAFE INGEST] Session {res.session_id} Complete")
            print(f"  Audio Source:   {res.audio_path} ({res.duration_seconds}s)")
            print(f"  Observatory:    Turn {res.observatory_turn_id} (+{res.tenant_xp_awarded} XP)")
            print(f"  Action Items:   {len(res.action_items)} extracted")
            for idx, it in enumerate(res.action_items, 1):
                disp_str = "DISPATCHED" if it.dispatched else "BLOCKED/PENDING"
                print(f"    [{idx}] {it.title} ({it.action_type}) -> {it.target_knight} [{disp_str}]")
            print(f"\n{res.summary}")
        return


def _cmd_freellmapi(argv: list[str]) -> None:
    """FreeLLMAPI Zero-Cost Gateway CLI.

    Usage:
        camelot freellmapi status [--json]
        camelot freellmapi models [--json]
        camelot freellmapi chat --prompt <TEXT> [--model auto] [--system <TEXT>] [--json]
    """
    import argparse
    import importlib.util

    bridge_path = Path(__file__).resolve().parent.parent / "02_FORGE" / "assimilation" / "freellmapi" / "freellmapi_bridge.py"
    spec = importlib.util.spec_from_file_location("freellmapi_bridge", str(bridge_path))
    if not spec or not spec.loader:
        print("[ERROR] Could not load freellmapi_bridge.py")
        return
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    bridge = mod.get_freellmapi_bridge()

    parser = argparse.ArgumentParser(prog="camelot freellmapi", description="FreeLLMAPI Zero-Cost Universal Gateway")
    sub = parser.add_subparsers(dest="action", help="Action")

    p_status = sub.add_parser("status", help="Check gateway status")
    p_status.add_argument("--json", action="store_true")

    p_models = sub.add_parser("models", help="List available free models")
    p_models.add_argument("--json", action="store_true")

    p_chat = sub.add_parser("chat", help="Execute chat completion")
    p_chat.add_argument("--prompt", "-p", required=True, help="User prompt to process")
    p_chat.add_argument("--model", "-m", default="auto", help="Target model alias")
    p_chat.add_argument("--system", "-s", default="You are a helpful sovereign intelligence assistant in Camelot-OS.", help="System prompt")
    p_chat.add_argument("--knight", "-k", default="SIR_HELIOS", help="Calling Knight")
    p_chat.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)

    if args.action in (None, "status"):
        alive, msg = bridge.is_alive()
        data = {
            "status": "ONLINE" if alive else "STANDBY",
            "base_url": bridge.base_url,
            "gateway_message": msg,
            "observatory_tap": "ENABLED" if bridge.enable_observatory_tap else "DISABLED",
            "curated_model_count": len(mod.FREE_MODEL_CATALOG),
        }
        if getattr(args, "json", False):
            print(json.dumps(data, indent=2))
        else:
            print("=" * 64)
            print("  [FREELLMAPI] ZERO-COST UNIVERSAL POOLED GATEWAY")
            print(f"  Status:       {data['status']} ({data['gateway_message']})")
            print(f"  Endpoint:     {data['base_url']}")
            print(f"  Observatory:  {data['observatory_tap']} (+35 XP / turn)")
            print(f"  Catalog:      {data['curated_model_count']} curated free tiers")
            print("=" * 64)
        return

    if args.action == "models":
        models = bridge.list_models()
        if args.json:
            print(json.dumps(models, indent=2))
        else:
            print("=" * 64)
            print(f"  [FREELLMAPI] CURATED / DETECTED MODELS ({len(models)} Total)")
            print("=" * 64)
            for m in models:
                mid = m.get("id", "unknown")
                prov = m.get("provider", "pooled")
                tier = m.get("tier", "free")
                desc = m.get("desc", "")
                print(f"  - {mid:<22} [{prov:<20}] ({tier}) {desc}")
        return

    if args.action == "chat":
        try:
            resp = bridge.chat_completion(
                prompt=args.prompt,
                system_prompt=args.system,
                model=args.model,
                calling_knight=args.knight,
            )
            if args.json:
                print(json.dumps(resp.to_dict(), indent=2))
            else:
                print("=" * 64)
                print(f"  [FREELLMAPI] RESPONSE (Model: {resp.model_used} | Provider: {resp.provider})")
                print(f"  Latency: {resp.duration_ms}ms | Tokens: {resp.total_tokens} | Fallback: {resp.is_fallback}")
                print("=" * 64)
                print(f"\n{resp.content}\n")
        except mod.SecretSanitizationViolation as e:
            print(f"[SECURITY FENCE REJECTED]: {e}")
        except Exception as e:
            print(f"[ERROR]: {e}")
        return


def _cmd_omniroute(argv: list[str]) -> None:
    """OmniRoute & 9Router-Go Gateway CLI.

    Usage:
        camelot omniroute status [--json]
        camelot omniroute compress --text <TEXT> [--mode rtk_caveman] [--json]
        camelot omniroute route --prompt <TEXT> [--strategy auto] [--json]
    """
    import argparse
    import importlib.util

    bridge_path = Path(__file__).resolve().parent.parent / "02_FORGE" / "assimilation" / "omniroute" / "omniroute_bridge.py"
    spec = importlib.util.spec_from_file_location("omniroute_bridge", str(bridge_path))
    if not spec or not spec.loader:
        print("[ERROR] Could not load omniroute_bridge.py")
        return
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    bridge = mod.get_omniroute_bridge()

    parser = argparse.ArgumentParser(prog="camelot omniroute", description="OmniRoute 359-Provider Gateway & 9Router-Go Accelerator")
    sub = parser.add_subparsers(dest="action", help="Action")

    p_status = sub.add_parser("status", help="Probe gateways and active strategies")
    p_status.add_argument("--json", action="store_true")

    p_comp = sub.add_parser("compress", help="Compress prompt using RTK + Caveman heuristics")
    p_comp.add_argument("--text", "-t", required=True, help="Text to compress")
    p_comp.add_argument("--mode", "-m", default="rtk_caveman", choices=["rtk", "caveman", "rtk_caveman"])
    p_comp.add_argument("--json", action="store_true")

    p_route = sub.add_parser("route", help="Route prompt through OmniRoute")
    p_route.add_argument("--prompt", "-p", required=True, help="Prompt to route")
    p_route.add_argument("--strategy", "-s", default="auto", help="Strategy (auto, auto/coding, auto/fast, auto/offline, voice/low-latency)")
    p_route.add_argument("--knight", "-k", default="SIR_HELIOS", help="Calling Knight")
    p_route.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)

    if args.action in (None, "status"):
        gateways = bridge.check_gateways()
        if getattr(args, "json", False):
            print(json.dumps(gateways, indent=2))
        else:
            print("=" * 68)
            print("  [OMNIROUTE & 9ROUTER-GO] UNIVERSAL ACCELERATION GATEWAY")
            print(f"  OmniRoute (:20128):  {gateways['omniroute']['status']} ({gateways['omniroute']['url']})")
            print(f"  9Router-Go (:3002):  {gateways['9router_go']['status']} ({gateways['9router_go']['url']}) [{gateways['9router_go']['peak_rps_rating']}, {gateways['9router_go']['target_ram']}]")
            print(f"  Compression Engine:  {gateways['compression_engine']} (~89% average reduction)")
            print(f"  Active Strategies:   {gateways['active_strategies_count']} strategies")
            print("=" * 68)
        return

    if args.action == "compress":
        res = mod.RTKCavemanCompressor.compress(args.text, mode=args.mode)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print("=" * 68)
            print(f"  [RTK + CAVEMAN COMPRESSOR] {res['original_tokens']} -> {res['compressed_tokens']} Tokens (-{res['saved_percent']}%)")
            print("=" * 68)
            print(f"\nOriginal ({res['original_tokens']} tokens):\n{res['original_text']}\n")
            print(f"Compressed ({res['compressed_tokens']} tokens):\n{res['compressed_text']}\n")
        return

    if args.action == "route":
        resp = bridge.route_request(prompt=args.prompt, strategy=args.strategy, calling_knight=args.knight)
        if args.json:
            print(json.dumps(resp.to_dict(), indent=2))
        else:
            print("=" * 68)
            print(f"  [OMNIROUTE RESPONSE] Strategy: {resp.strategy_used} | Provider: {resp.provider}")
            print(f"  Tokens: {resp.original_tokens} -> {resp.compressed_tokens} (-{resp.saved_percent}%) | Latency: {resp.duration_ms}ms")
            print("=" * 68)
            print(f"\n{resp.content}\n")
        return


def _cmd_bitrouter(argv: list[str]) -> None:
    """BitRouter Anti-Tokenmaxxing Agent Guardrails CLI.

    Usage:
        camelot bitrouter eval --loop <ID> --task <TASK> [--steps N] [--tokens N] [--cost F] [--json]
    """
    import argparse
    import importlib.util

    bridge_path = Path(__file__).resolve().parent.parent / "02_FORGE" / "assimilation" / "bitrouter" / "bitrouter_guardrails.py"
    spec = importlib.util.spec_from_file_location("bitrouter_guardrails", str(bridge_path))
    if not spec or not spec.loader:
        print("[ERROR] Could not load bitrouter_guardrails.py")
        return
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    engine = mod.get_bitrouter_engine()

    parser = argparse.ArgumentParser(prog="camelot bitrouter", description="BitRouter Anti-Tokenmaxxing Agent Guardrails")
    sub = parser.add_subparsers(dest="action", help="Action")

    p_eval = sub.add_parser("eval", help="Evaluate agent step and tighten model tier")
    p_eval.add_argument("--loop", "-l", default="default_loop", help="Loop identifier")
    p_eval.add_argument("--task", "-t", default="Execute agentic task", help="Task description")
    p_eval.add_argument("--knight", "-k", default="SIR_CODEX", help="Calling Knight")
    p_eval.add_argument("--tokens", type=int, default=1500, help="Added tokens in step")
    p_eval.add_argument("--cost", type=float, default=0.015, help="Added cost in USD")
    p_eval.add_argument("--type", default="tool_call", choices=["tool_call", "file_read", "subagent_hop", "retry"])
    p_eval.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)

    if args.action in (None, "eval"):
        state = engine.start_or_update_loop(
            loop_id=args.loop,
            task=args.task,
            knight_id=args.knight,
            added_tokens=args.tokens,
            added_cost=args.cost,
            step_type=args.type,
        )
        if getattr(args, "json", False):
            print(json.dumps(state.to_dict(), indent=2))
        else:
            print("=" * 68)
            print("  [BITROUTER] ANTI-TOKENMAXXING AGENT GUARDRAILS")
            print(f"  Loop ID:          {state.loop_id} (Iteration #{state.iteration})")
            print(f"  Calling Knight:   {state.calling_knight}")
            print(f"  Recommended Tier: {state.recommended_model.upper()}")
            print(f"  Circuit Breaker:  {'TRIPPED [HALT]' if state.circuit_breaker_tripped else 'CLEAR [OK]'}")
            print(f"  Tokens Consumed:  {state.total_tokens:,} tokens | Cost: ${state.estimated_cost_usd:.4f}")
            print(f"  Rationale:        {state.rationale}")
            print("=" * 68)
        return


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
    if first in ("omniroute", "9router", "nine-router"):
        _cmd_omniroute(args[1:])
        return

    if first in ("bitrouter", "guardrails", "tokenmax"):
        _cmd_bitrouter(args[1:])
        return

    if first in ("freellmapi", "zero-cost", "freellm"):
        _cmd_freellmapi(args[1:])
        return

    if first in ("magsafe", "magsafe-audio", "magsafe-bridge"):
        _cmd_magsafe(args[1:])
        return

    if first == "reya":
        _cmd_reya(args[1:])
        return
    if first in ("cua", "computer-use", "reya-cua"):
        _cmd_cua(args[1:])
        return

    if first in ("observatory", "glass", "compendium", "rpg"):
        _cmd_observatory(args[1:])
        return

    if first in ("s2s", "voice-s2s", "omni-s2s"):
        _cmd_s2s(args[1:])
        return

    if first == "configure" or first == "config":
        verbose = "--verbose" in args or "-v" in args
        _cmd_configure(verbose=verbose)
        return

    if first == "status":
        _cmd_status(args[1:])
        return

    if first == "boot":
        _cmd_boot(args[1:])
        return

    if first == "dev":
        _cmd_dev(args[1:])
        return

    if first in ("hermes", "vps-hermes"):
        _cmd_hermes(args[1:])
        return

    if first in ("moto", "motorola"):
        _cmd_moto(args[1:])
        return

    if first in ("s26", "excalibur"):
        _cmd_s26(args[1:])
        return

    if first in ("qtscrcpy", "qrscrcpy", "qt"):
        _cmd_qtscrcpy(args[1:])
        return

    if first in ("tmux", "vps-tmux"):
        _cmd_tmux(args[1:])
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
        from control_plane.camelot_cli import main as control_main
        raise SystemExit(control_main())

    _cmd_warp()


if __name__ == "__main__":
    main()
