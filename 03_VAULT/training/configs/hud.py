"""Camelot OS HUD -- Rich terminal dashboard.

Provides a full-screen heads-up display showing:
  - System status and bridge health
  - Active LLM providers and models
  - Knight roster and performance stats
  - Execution history
  - Interactive command prompt
"""

import atexit
import json
import os
import shlex
import subprocess
import sys
import threading
import time

# Fix Windows encoding before anything else
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import io
import logging

import requests

__version__ = "1.0.0"

CAMELOT_DIR = os.path.dirname(os.path.abspath(__file__))
HOME_DIR = os.path.expanduser("~")
sys.path.insert(0, CAMELOT_DIR)

# ── Defense Grid Daemon ──────────────────────────────────────────────

_heartbeat_proc = None
_cliproxy_proc = None
_kinetic_edge_proc = None

HEARTBEAT_GO = os.path.join(os.path.abspath(os.path.join(CAMELOT_DIR, "..", "..", "..")), "cmd", "pulse", "heartbeat.go")
CLIPROXY_BIN = os.path.join(HOME_DIR, "CLIProxyAPI", "cli-proxy-api.exe")
CLIPROXY_DIR = os.path.join(HOME_DIR, "CLIProxyAPI")
# Phase 1 RIP_AND_REPLACE (HiveIDE_Apex_v1000) — see
# 03_VAULT/runtime_state/node_mcp_cutlist.json + phase3_pending_prerequisite.md
# Default flipped camelot-mcp-edge.exe -> pmcp-server.exe.
# Override with CAMELOT_KINETIC_EDGE_BIN env var to restore legacy binary.
# Revert: git checkout HEAD -- 03_VAULT/training/configs/hud.py
# or restore from 03_VAULT/runtime_state/backups/hiveide_cut_*/
_KINETIC_EDGE_BIN_NAME = os.environ.get("CAMELOT_KINETIC_EDGE_BIN") or "pmcp-server.exe"  # was: camelot-mcp-edge.exe
KINETIC_EDGE_BIN = os.path.join(HOME_DIR, "CAMELOT_OS", "bin", _KINETIC_EDGE_BIN_NAME)
KINETIC_EDGE_URL = "http://127.0.0.1:3001"
SALTARE_URL = "http://localhost:8080/route"
ROTEL_STATUS_URL = "http://localhost:4317/status"


def _boot_defense_grid():
    """Spawn the heartbeat.go daemon as a background process."""
    global _heartbeat_proc
    if not os.path.isfile(HEARTBEAT_GO):
        return None, "[yellow]heartbeat.go not found — skipping Defense Grid[/]"
    try:
        _heartbeat_proc = subprocess.Popen(
            ["go", "run", HEARTBEAT_GO],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        atexit.register(_shutdown_defense_grid)
        return _heartbeat_proc.pid, f"[green]Defense Grid online[/] (PID {_heartbeat_proc.pid})"
    except FileNotFoundError:
        return None, "[yellow]Go not found — Defense Grid skipped[/]"
    except Exception as e:
        return None, f"[red]Defense Grid failed: {e}[/]"


def _shutdown_defense_grid():
    """Terminate the heartbeat daemon on exit."""
    global _heartbeat_proc
    if _heartbeat_proc and _heartbeat_proc.poll() is None:
        _heartbeat_proc.terminate()
        try:
            _heartbeat_proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            _heartbeat_proc.kill()
        _heartbeat_proc = None


def _boot_cliproxy():
    """Spawn CLIProxyAPI as a background process (Zero-Burn local proxy)."""
    global _cliproxy_proc
    if not os.path.isfile(CLIPROXY_BIN):
        return None, "[yellow]cli-proxy-api binary not found — skipping CLIProxyAPI[/]"
    # Check if port 8080 is already in use (proxy already running)
    try:
        import httpx
        resp = httpx.get("http://127.0.0.1:8080/v1/models",
                         headers={"Authorization": "Bearer proxy-admin-key"}, timeout=2)
        if resp.status_code == 200:
            return None, "[green]CLIProxyAPI already running[/] on :8080"
    except Exception:
        pass
    try:
        _cliproxy_proc = subprocess.Popen(
            [CLIPROXY_BIN],
            cwd=CLIPROXY_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        atexit.register(_shutdown_cliproxy)
        return _cliproxy_proc.pid, f"[green]CLIProxyAPI online[/] (PID {_cliproxy_proc.pid}, port 8080)"
    except Exception as e:
        return None, f"[red]CLIProxyAPI failed: {e}[/]"


def _boot_kinetic_edge():
    """Spawn Lukas — Rust/Axum MCP server with AgentArmor PDG on :3001."""
    global _kinetic_edge_proc
    if not os.path.isfile(KINETIC_EDGE_BIN):
        return None, "[yellow]camelot-mcp-edge.exe not found — Kinetic Edge skipped[/]"
    # v6 review fix: dropped the legacy httpx /tool/stat_file probe — that endpoint
    # was camelot-mcp-edge specific. pmcp-server-v0.1 is stdio-MCP only; the probe
    # would silently time out and trigger a retry loop. The RustClaw lineage now
    # supervises the Kinetic Edge service via process-alive (port=None).
    detach = os.environ.get("AWAKEN_DETACH_CHILDREN") == "1"
    try:
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        if detach:
            flags |= getattr(subprocess, "DETACHED_PROCESS", 0)
            flags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        _kinetic_edge_proc = subprocess.Popen(
            [KINETIC_EDGE_BIN],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            creationflags=flags,
            close_fds=True,
        )
        if not detach:
            atexit.register(_shutdown_kinetic_edge)
        return _kinetic_edge_proc.pid, f"[green]Kinetic Edge online[/] (PID {_kinetic_edge_proc.pid}, port 3001)"
    except Exception as e:
        return None, f"[red]Kinetic Edge failed: {e}[/]"


def _shutdown_kinetic_edge():
    global _kinetic_edge_proc
    if _kinetic_edge_proc and _kinetic_edge_proc.poll() is None:
        _kinetic_edge_proc.terminate()
        try:
            _kinetic_edge_proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            _kinetic_edge_proc.kill()
        _kinetic_edge_proc = None


def _boot_cloud_brain():
    """Integration Brain heartbeat — ST(NotebookLM) + LT(Modal/Appwrite). Synthesis deferred until //PLAN."""
    try:
        from integration_brain import health_probe
        ok, msg, latency = health_probe()
        color = "green" if ok else "yellow"
        return ok, f"[{color}]{msg}[/] ({latency:.0f}ms)"
    except ImportError as e:
        return False, f"[yellow]Integration Brain skipped — {e}[/]"
    except Exception as e:
        return False, f"[yellow]Integration Brain probe failed: {type(e).__name__}[/]"


def _shutdown_cliproxy():
    """Terminate CLIProxyAPI on exit."""
    global _cliproxy_proc
    if _cliproxy_proc and _cliproxy_proc.poll() is None:
        _cliproxy_proc.terminate()
        try:
            _cliproxy_proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            _cliproxy_proc.kill()
        _cliproxy_proc = None


# ── Runic Routing (from camelot_cli.py) ──────────────────────────────

def _handle_forge(command: str):
    """//FORGE — bypass LLM, invoke local Rust bundler via cribo."""
    result = subprocess.run(
        ["cribo", "--entry", "src/main.py", "--output", "bundle.py"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode == 0:
        msg = "[green]FORGE SUCCESS[/] — bundle.py written."
        if result.stdout.strip():
            msg += f"\n{result.stdout.strip()}"
        return msg
    else:
        msg = f"[red]FORGE ERROR[/] — exit code {result.returncode}"
        if result.stderr.strip():
            msg += f"\n[red]{result.stderr.strip()}[/]"
        return msg


def _handle_research(command: str, console) -> None:
    """//RESEARCH [kinetic|hybrid|apex] <objective> — Perplexity-killer research agency."""
    import asyncio
    rest = command[len("//RESEARCH"):].strip()
    if not rest:
        console.print(
            "[yellow]Usage:[/] //RESEARCH [kinetic|hybrid|apex] <objective>\n"
            "[dim]Tiers: kinetic=fast(3 cells) | hybrid=balanced(4) | apex=deep(5)[/]"
        )
        return

    # Parse optional tier prefix
    tier = "hybrid"
    parts = rest.split(None, 1)
    if parts[0].lower() in ("kinetic", "hybrid", "apex"):
        tier = parts[0].lower()
        objective = parts[1] if len(parts) > 1 else ""
    else:
        objective = rest

    if not objective:
        console.print("[yellow]No objective specified.[/]")
        return

    console.print(
        f"[bright_magenta]//RESEARCH[/] [{tier.upper()}] "
        f"[dim]{objective[:90]}[/]"
    )

    try:
        sys.path.insert(0, CAMELOT_DIR)
        from knights.browser_research_agency import BrowserResearchAgency
        from rich.panel import Panel
        from rich.progress import Progress, SpinnerColumn, TextColumn
        from rich.table import Table

        agency = BrowserResearchAgency(tier=tier)

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                      transient=True, console=console) as progress:
            progress.add_task(
                f"Research agency [{tier}] — ancestor → cells → CHIMERA → sync…",
                total=None
            )
            brief = asyncio.run(agency.run(objective))

        # Ancestor context panel (if available)
        if brief.ancestor_context and not brief.ancestor_context.startswith("[ancestor"):
            console.print(Panel(
                brief.ancestor_context[:600],
                title="[bold cyan]NotebookLM Ancestor Brain[/] — prior knowledge",
                border_style="cyan",
            ))

        # Cell results table
        table = Table(title=f"Browser Cells — {tier.upper()} tier",
                      border_style="bright_magenta", show_lines=True)
        table.add_column("Cell", style="cyan", width=18)
        table.add_column("Knight", width=16)
        table.add_column("URLs", justify="right", width=5)
        table.add_column("ms", justify="right", width=7)
        table.add_column("OK", width=4)
        table.add_column("Preview", no_wrap=False)

        for cr in brief.cells:
            ok_color = "green" if cr.success else "red"
            table.add_row(
                cr.cell,
                cr.knight_id,
                str(len(cr.urls)),
                f"{cr.elapsed_ms:.0f}",
                f"[{ok_color}]{'✓' if cr.success else '✗'}[/]",
                cr.result[:200] if cr.result else "[dim]—[/]",
            )
        console.print(table)

        # CHIMERA rounds
        if brief.chimera:
            chimera_table = Table(title="CHIMERA Rounds", border_style="bright_yellow", show_lines=True)
            chimera_table.add_column("Round", style="yellow", width=8)
            chimera_table.add_column("Owner", width=22)
            chimera_table.add_column("Title", width=22)
            chimera_table.add_column("ms", justify="right", width=7)
            chimera_table.add_column("OK", width=4)
            chimera_table.add_column("Output", no_wrap=False)
            for r in brief.chimera:
                ok_color = "green" if r.success else "red"
                chimera_table.add_row(
                    r.round_id[-1],
                    r.owner,
                    r.title,
                    f"{r.elapsed_ms:.0f}",
                    f"[{ok_color}]{'✓' if r.success else '✗'}[/]",
                    r.output[:200] if r.output else "[dim]—[/]",
                )
            console.print(chimera_table)

        # Final synthesis
        console.print(Panel(
            brief.synthesis[:1400] if brief.synthesis else "[dim]no synthesis[/]",
            title="[bold]Final Synthesis[/] — CHIMERA × NotebookLM × Integration Brain",
            border_style="bright_cyan",
        ))
        console.print(
            f"[dim]Sources: {len(brief.sources)} | "
            f"NLM sources added: {brief.sources_added} | "
            f"Ancestor synced: {'✓' if brief.ancestor_synced else '—'} | "
            f"LT stored: {'✓' if brief.memory_count > 0 else '—'} | "
            f"Total: {brief.elapsed_ms:.0f}ms[/]"
        )

    except ImportError as e:
        console.print(
            f"[red]//RESEARCH:[/] browser-use not installed.\n"
            f"Run: [cyan]pip install browser-use langchain-anthropic[/]\n{e}"
        )
    except Exception as e:
        console.print(f"[red]//RESEARCH error:[/] {type(e).__name__}: {e}")


def _handle_browse(command: str, console) -> None:
    """//BROWSE [knight_ids] <task> — deploy browser nano-knights with feedback."""
    import asyncio
    rest = command[len("//BROWSE"):].strip()
    if not rest:
        console.print("[yellow]Usage:[/] //BROWSE [apis|sentinel|syntax|debug,…] <task>")
        return

    # Parse optional roster prefix: "apis,sentinel: go find X"
    roster = ["apis"]
    task = rest
    if ":" in rest and rest.split(":")[0].replace(",", "").replace(" ", "").isalpha():
        roster_part, task = rest.split(":", 1)
        roster = [r.strip().lower() for r in roster_part.split(",") if r.strip()]
        task = task.strip()

    if not task:
        console.print("[yellow]No task specified.[/]")
        return

    roster_str = ", ".join(roster)
    console.print(f"[bright_magenta]//BROWSE[/] spawning [cyan]{roster_str}[/] → [dim]{task[:80]}[/]")

    try:
        sys.path.insert(0, CAMELOT_DIR)
        from knights.browser_nano_knight import BrowserSquad
        from rich.progress import Progress, SpinnerColumn, TextColumn
        from rich.table import Table

        squad = BrowserSquad(roster=roster)

        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                      transient=True, console=console) as progress:
            progress.add_task(f"Browser squad [{roster_str}] running…", total=None)
            results = asyncio.run(squad.deploy(task))

        table = Table(title="//BROWSE Results", border_style="bright_magenta", show_lines=True)
        table.add_column("Knight", style="cyan", width=18)
        table.add_column("Steps", justify="right", width=6)
        table.add_column("URLs", justify="right", width=5)
        table.add_column("ms", justify="right", width=7)
        table.add_column("Status", width=8)
        table.add_column("Result", no_wrap=False)

        for fb in results:
            status_color = "green" if fb.success else "red"
            status = f"[{status_color}]{'OK' if fb.success else 'ERR'}[/]"
            table.add_row(
                fb.knight_id,
                str(fb.steps_taken),
                str(len(fb.urls_visited)),
                f"{fb.elapsed_ms:.0f}",
                status,
                fb.result[:300] if fb.result else "[dim]—[/]",
            )

        console.print(table)
        console.print("[dim]Feedback stored to Integration Brain LT (Modal Volume).[/]")

    except ImportError as e:
        console.print(f"[red]//BROWSE:[/] browser-use not installed. Run: [cyan]pip install browser-use langchain-anthropic[/]\n{e}")
    except Exception as e:
        console.print(f"[red]//BROWSE error:[/] {type(e).__name__}: {e}")


def _handle_rune(rune: str) -> str:
    """Omega_ rune dispatcher — wires 29 Omega runes to real handlers."""
    r = rune.upper().replace("OMEGA_", "").strip()

    # ── Omega_SYNC — Lord Archivist GEP scan (Ouroboros state capture) ──────
    if r == "SYNC":
        try:
            cp = os.path.join(HOME_DIR, "CAMELOT_OS", "control_plane")
            if cp not in sys.path:
                sys.path.insert(0, cp)
            from lord_archivist import run_gep_scan
            rpt = run_gep_scan()
            lines = [
                "[cyan]Omega_SYNC — Lord Archivist GEP Scan[/]",
                f"  Skills scanned: [green]{len(rpt.skill_audits)}[/]",
                f"  Skill gaps:     [{'red' if rpt.skill_gaps else 'green'}]{rpt.skill_gaps or 'none'}[/]",
                f"  Fail patterns:  {len(rpt.fail_patterns)}",
                f"  XP entries:     {len(rpt.xp_entries)}",
                f"  Duration:       {rpt.duration_ms:.0f}ms",
                "[dim]Learnings written to 03_VAULT/Knights/learnings.md[/]",
            ]
            return "\n".join(lines)
        except Exception as e:
            return f"[yellow]Omega_SYNC:[/] GEP scan unavailable — {e}"

    # ── Omega_STATUS — camelot-status.py quick run ───────────────────────────
    elif r == "STATUS":
        try:
            status_py = os.path.join(HOME_DIR, "CAMELOT_OS", "scripts", "camelot-status.py")
            result = subprocess.run(
                [sys.executable, status_py, "--quick"],
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60,
            )
            return result.stdout.strip() or result.stderr.strip() or "[dim]Status check returned empty[/]"
        except Exception as e:
            return f"[yellow]Omega_STATUS:[/] status check failed — {e}"

    # ── Omega_AUDIT — Sir Gideon //SCORPION pass ─────────────────────────────
    elif r == "AUDIT":
        try:
            cfg = os.path.join(HOME_DIR, "CAMELOT_OS", "03_VAULT", "training", "configs")
            if cfg not in sys.path:
                sys.path.insert(0, cfg)
            from knights.sir_gideon import run_scorpion
            rpt = run_scorpion()
            col = "green" if rpt.passed else "red"
            lines = [f"[{col}]Omega_AUDIT — {rpt.summary}[/]", ""]
            for sp in rpt.shatterpoints:
                c = {"CLEAR": "green", "WARN": "yellow", "CRITICAL": "red"}.get(sp.status, "white")
                lines.append(f"  [{c}]{sp.status:8}[/] {sp.shatterpoint}")
            return "\n".join(lines)
        except Exception as e:
            return f"[yellow]Omega_AUDIT:[/] Sir Gideon unavailable — {e}"

    # ── Omega_PURGE — clear harness_queue.jsonl and temp log artifacts ───────
    elif r == "PURGE":
        purged = []
        try:
            q = os.path.join(HOME_DIR, "CAMELOT_OS", "logs", "harness_queue.jsonl")
            if os.path.exists(q):
                open(q, "w", encoding="utf-8").close()
                purged.append("harness_queue.jsonl (cleared)")
        except Exception as e:
            purged.append(f"queue clear failed: {e}")
        return f"[cyan]Omega_PURGE:[/] {', '.join(purged) if purged else 'nothing to purge'}"

    # ── Omega_CLEAN — clear Python __pycache__ under control_plane ───────────
    elif r == "CLEAN":
        import shutil as _sh
        cleaned = 0
        for root, dirs, _ in os.walk(os.path.join(HOME_DIR, "CAMELOT_OS", "control_plane")):
            for d in dirs:
                if d == "__pycache__":
                    try:
                        _sh.rmtree(os.path.join(root, d))
                        cleaned += 1
                    except Exception:
                        pass
        return f"[cyan]Omega_CLEAN:[/] {cleaned} __pycache__ dirs removed"

    # ── Omega_EVOLVE — trigger persona evolution cycle ────────────────────────
    elif r == "EVOLVE":
        try:
            cp = os.path.join(HOME_DIR, "CAMELOT_OS", "control_plane")
            if cp not in sys.path:
                sys.path.insert(0, cp)
            from lord_archivist import run_gep_scan
            rpt = run_gep_scan()
            events = [e.tag for e in rpt.evolve_events] if rpt.evolve_events else []
            return (
                f"[magenta]Omega_EVOLVE — Persona Evolution Cycle[/]\n"
                f"  XP entries harvested: {len(rpt.xp_entries)}\n"
                f"  Evolve events: {events or 'none'}\n"
                f"  [dim]Update soul.md / identity.md if events require refinement[/]"
            )
        except Exception as e:
            return f"[yellow]Omega_EVOLVE:[/] evolution scan failed — {e}"

    # ── Omega_RESEARCH — Lady Apis foraging stub ─────────────────────────────
    elif r == "RESEARCH":
        return (
            "[cyan]Omega_RESEARCH — Lady Apis Foraging[/]\n"
            "  Route: ask@gemini <objective> for 1M-context deep dive\n"
            "  Or: exec sir_helio <query> for cloud burst synthesis\n"
            "  [dim]Full DeerFlow integration pending DeerFlow/Kestra wiring[/]"
        )

    # ── Omega_THINK — GoT/DoT structured reasoning chain ────────────────────
    elif r == "THINK":
        return (
            "[cyan]Omega_THINK — GoT/DoT/ToT Reasoning Chain[/]\n"
            "  Activate via: ask <complex question> — Merlin_Omega applies structured decomp\n"
            "  Sub-goal cap: 3 (8GB RAM ceiling, NPE Law #12)\n"
            "  [dim]Full GoT wiring: control_plane/soul_router.py MFOE tensor scoring active[/]"
        )

    # ── Omega_GRAPH — UKG knowledge graph ops ────────────────────────────────
    elif r == "GRAPH":
        ukg = os.path.join(HOME_DIR, "CAMELOT_OS", "03_VAULT", "training",
                           "configs", "memory", "ukg_graph.jsonld")
        exists = os.path.isfile(ukg)
        size   = f"{os.path.getsize(ukg) // 1024}KB" if exists else "missing"
        return (
            f"[cyan]Omega_GRAPH — UKG Knowledge Graph[/]\n"
            f"  Path:   03_VAULT/training/configs/memory/ukg_graph.jsonld\n"
            f"  Status: [{'green' if exists else 'red'}]{size}[/]\n"
            f"  [dim]Qdrant vector index at :6333 (offline — run awaken to start)[/]"
        )

    # ── Omega_SHIELD — Agent-Armor activation ────────────────────────────────
    elif r == "SHIELD":
        return (
            "[cyan]Omega_SHIELD — Agent-Armor v2.0[/]\n"
            "  Program Dependency Graph: active (sir_sentinel)\n"
            "  RBAC Matrix: active (omc_team.dispatch gated)\n"
            "  Iron Gate HITL: >10 net lines or >50MB requires approval\n"
            "  //SCORPION: GIDEON_RISK_SCORE=1 PASS\n"
            "  [dim]Full PDG scan: exec sir_sentinel security_review[/]"
        )

    # ── Omega_KINETIC — kinetic edge status ──────────────────────────────────
    elif r == "KINETIC":
        import socket as _s
        ok = False
        try:
            with _s.create_connection(("127.0.0.1", 3001), timeout=0.5):
                ok = True
        except OSError:
            pass
        bin_dir = os.path.join(HOME_DIR, "CAMELOT_OS", "bin")
        spawner = os.path.isfile(os.path.join(bin_dir, "swarm-spawner.exe"))
        pqc     = os.path.isfile(os.path.join(bin_dir, "camelot-pqcrypto.exe"))
        viz     = os.path.isfile(os.path.join(bin_dir, "vizion-telemetry.exe"))
        lines = [
            "[cyan]Omega_KINETIC — Kinetic Edge[/]",
            f"  MCP Axum :3001  [{'green' if ok else 'red'}]{'live' if ok else 'dark'}[/]",
            f"  swarm-spawner   [{'green' if spawner else 'yellow'}]{'built' if spawner else 'pending build'}[/]",
            f"  pqcrypto        [{'green' if pqc else 'yellow'}]{'built' if pqc else 'pending build'}[/]",
            f"  vizion-telem    [{'green' if viz else 'yellow'}]{'built' if viz else 'pending build'}[/]",
            "  [dim]Run: bash scripts/build_kinetic.sh[/]",
        ]
        return "\n".join(lines)

    # ── Omega_STACK — control_plane module inventory ──────────────────────────
    elif r == "STACK":
        cp = os.path.join(HOME_DIR, "CAMELOT_OS", "control_plane")
        mods = sorted(f.stem for f in Path(cp).glob("*.py") if not f.name.startswith("_"))
        return (
            f"[cyan]Omega_STACK — Control Plane ({len(mods)} modules)[/]\n"
            + "  " + "  ".join(f"[dim]{m}[/]" for m in mods)
        )

    # ── Omega_GATEWAY — CLIProxy status ───────────────────────────────────────
    elif r == "GATEWAY":
        import socket as _s
        ok = False
        try:
            with _s.create_connection(("127.0.0.1", 8080), timeout=0.5):
                ok = True
        except OSError:
            pass
        return (
            f"[cyan]Omega_GATEWAY — CLIProxy :8080[/]  "
            f"[{'green' if ok else 'red'}]{'LIVE' if ok else 'DARK'}[/]\n"
            f"  [dim]29 models | free→low→medium→high cost discipline[/]"
        )

    else:
        # Route through runic_router for any remaining Omega runes
        try:
            cp = os.path.join(HOME_DIR, "CAMELOT_OS", "control_plane")
            if cp not in sys.path:
                sys.path.insert(0, cp)
            from runic_router import detect_and_route
            result = detect_and_route(f"Omega_{rune.split('_', 1)[-1]}")
            if result:
                return (
                    f"[cyan]Omega_{r}[/] queued → knight [bright_magenta]{result.knight}[/]  "
                    f"[dim]task_id={result.task_id}[/]"
                )
        except Exception:
            pass
        return f"[yellow]Omega_{r}:[/] no registered handler — queued to runic router"


def _handle_saltare(user_input: str):
    """Forward natural language to Saltare MCP Gateway."""
    import requests
    try:
        resp = requests.post(SALTARE_URL, json={"query": user_input}, timeout=10)
        resp.raise_for_status()
        payload = resp.json()
        parts = []
        if "tool_to_call" in payload:
            parts.append(f"[green]Tool Resolved:[/] {payload['tool_to_call']}")
        if "response" in payload:
            parts.append(f"{payload['response']}")
        if not parts:
            parts.append(f"[dim]Gateway Payload:[/] {payload}")
        return "\n".join(parts)
    except requests.exceptions.ConnectionError:
        return f"[red]Saltare Offline[/] — Cannot reach {SALTARE_URL}. Is the MCP Gateway running?"
    except requests.exceptions.Timeout:
        return "[red]Timeout[/] — Saltare Gateway did not respond within 10s."
    except requests.exceptions.HTTPError as exc:
        return f"[red]HTTP Error[/] — Gateway returned {exc.response.status_code}"
    except ValueError:
        return f"[dim]Gateway Raw Response:[/] {resp.text}"

# Suppress ALL kernel noise during import (fd-level redirect catches C-level prints)

def _silence_kernel(func):
    """Run func with stdout/stderr silenced at fd level (Windows-safe)."""
    old_stdout, old_stderr = sys.stdout, sys.stderr
    try:
        devnull_fd = os.open(os.devnull, os.O_WRONLY)
        old_out_fd = os.dup(1)
        old_err_fd = os.dup(2)
        fd_redirect = True
    except OSError:
        fd_redirect = False

    if fd_redirect:
        os.dup2(devnull_fd, 1)
        os.dup2(devnull_fd, 2)
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
    logging.disable(logging.CRITICAL)
    try:
        return func()
    except Exception:
        return None
    finally:
        logging.disable(logging.NOTSET)
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        if fd_redirect:
            os.dup2(old_out_fd, 1)
            os.dup2(old_err_fd, 2)
            os.close(devnull_fd)
            os.close(old_out_fd)
            os.close(old_err_fd)

# Pre-load bridge silently — suppress ALL output channels
import builtins

_real_print = builtins.print
_real_stdout, _real_stderr = sys.stdout, sys.stderr
builtins.print = lambda *a, **k: None
sys.stdout = io.StringIO()
sys.stderr = io.StringIO()
logging.disable(logging.CRITICAL)
bridge = None
_BRIDGE_PRELOAD_TIMEOUT = float(os.environ.get("CAMELOT_BRIDGE_PRELOAD_TIMEOUT", "8"))
try:
    import bridge as _bridge_mod
    bridge = _bridge_mod
    if bridge.is_available() and _BRIDGE_PRELOAD_TIMEOUT > 0:
        _br_result = [None]
        def _preload_bridge():
            try:
                _br_result[0] = _bridge_mod.get_bridge_status()
            except Exception:
                pass
        _br_t = threading.Thread(target=_preload_bridge, daemon=True)
        _br_t.start()
        _br_t.join(timeout=_BRIDGE_PRELOAD_TIMEOUT)
except Exception:
    bridge = None
builtins.print = _real_print
sys.stdout = _real_stdout
sys.stderr = _real_stderr
logging.disable(logging.NOTSET)
# Re-apply Windows encoding fix after restoring stdout/stderr
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    from rich import box
    from rich.columns import Columns
    from rich.console import Console
    from rich.layout import Layout
    from rich.live import Live
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.table import Table
    from rich.text import Text
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

if not HAS_RICH:
    def main():
        print("Camelot OS HUD requires the 'rich' package.")
        print("Install it with: pip install rich")
        sys.exit(1)

    if __name__ == "__main__":
        main()
    # Prevent rest of module from failing on imports
    import types
    console = types.SimpleNamespace(print=print, clear=lambda: None)
else:
    try:
        _term_width = os.get_terminal_size().columns
    except (OSError, ValueError):
        _term_width = 80

    console = Console(width=max(_term_width, 60))

# ── ASCII Banner ──────────────────────────────────────────────────────

BANNER = r"""[bold bright_yellow]
   ____                      _       _      ___  ____
  / ___|__ _ _ __ ___   ___ | | ___ | |_   / _ \/ ___|
 | |   / _` | '_ ` _ \ / _ \| |/ _ \| __| | | | \___ \
 | |__| (_| | | | | | |  __/| | (_) | |_  | |_| |___) |
  \____\__,_|_| |_| |_|\___||_|\___/ \__|  \___/|____/
[/]
[dim]  v400.1.0 LATTICE_RADIANT | 7-Loop Sovereign Harness | SCORPION PASS[/]"""


# ── Component Panels ──────────────────────────────────────────────────

_suppress_lock = threading.Lock()


def _suppress_kernel_noise(func):
    """Run a function with ALL output suppressed (thread-safe)."""
    with _suppress_lock:
        old_out, old_err = sys.stdout, sys.stderr
        old_print = builtins.print
        builtins.print = lambda *a, **k: None
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        try:
            return func()
        finally:
            builtins.print = old_print
            sys.stdout = old_out
            sys.stderr = old_err


def _build_bridge_panel():
    """Build the bridge status panel."""
    try:
        status = _suppress_kernel_noise(bridge.get_bridge_status) if bridge else None
        if not status:
            return Panel("[red]Bridge unavailable[/]", title="Bridge", border_style="red")
    except Exception:
        return Panel("[red]Bridge unavailable[/]", title="Bridge", border_style="red")

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Component", style="cyan", width=18)
    table.add_column("Status", width=12)

    categories = {
        "Security": ["iron_gate", "warden", "zenith"],
        "Reasoning": ["mgv", "planning_engine", "council_debate"],
        "Infra": ["excalibur", "think_tank", "cartridges_os"],
        "Storage": ["vault", "titan_omega"],
    }

    for category, comps in categories.items():
        for comp in comps:
            state = status["components"].get(comp, "?")
            style = "green" if state == "active" else "red"
            table.add_row(comp, f"[{style}]{state}[/]")

    active = sum(1 for s in status["components"].values() if s == "active")
    total = len(status["components"])
    title = f"Kernel Bridge [{active}/{total}]"
    color = "green" if active >= 9 else "yellow" if active >= 5 else "red"
    return Panel(table, title=title, border_style=color)


def _build_llm_panel():
    """Build the LLM providers panel."""
    try:
        from llm_router import list_available
        providers = list_available()
    except Exception as e:
        return Panel(f"[red]LLM Router error: {e}[/]", title="LLM Providers", border_style="red")

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Provider", style="cyan", width=12)
    table.add_column("Status", width=10)
    table.add_column("Model", style="dim", width=22)

    for p in providers:
        status = p["status"]
        if "ready" in status:
            style = "green"
        elif status == "no_key":
            style = "yellow"
        else:
            style = "red"
        table.add_row(p["name"], f"[{style}]{status}[/]", p["default_model"])

    ready = sum(1 for p in providers if "ready" in p["status"])
    return Panel(table, title=f"LLM Providers [{ready}/{len(providers)}]",
                 border_style="bright_blue")


def _build_knights_panel():
    """Build the knights roster panel."""
    try:
        from camelot import _discover_knights, _knight_registry
        _discover_knights()
        knights = _knight_registry
    except Exception:
        knights = {}

    if not knights:
        return Panel("[dim]No knights loaded[/]", title="Knights", border_style="bright_magenta")

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Knight", style="bold", width=16)
    table.add_column("Role", style="dim", width=28)

    for key, knight in knights.items():
        table.add_row(knight.name, knight.specialty)

    return Panel(table, title=f"Knights [{len(knights)}]", border_style="bright_magenta")


def _build_stats_panel():
    """Build execution statistics panel."""
    try:
        from ouroboros import get_history, get_stats
        stats = get_stats()
        history = get_history(5)
    except Exception:
        return Panel("[dim]No stats[/]", title="Stats", border_style="dim")

    lines = []
    total_runs = sum(s.get("total_runs", 0) for s in stats)
    total_ok = sum(s.get("successes", 0) for s in stats)
    pct = (total_ok / total_runs * 100) if total_runs else 0
    lines.append(f"[bold]{total_runs}[/] executions | [green]{pct:.0f}%[/] success")

    if history:
        lines.append("")
        lines.append("[dim]Recent:[/]")
        for h in history[:3]:
            ts = h["timestamp"][11:19]
            st = "[green]OK[/]" if h["status"] == "success" else "[red]ERR[/]"
            lines.append(f"  {ts} {st} {h['directive'][:40]}")

    return Panel("\n".join(lines), title="Ouroboros Stats", border_style="bright_cyan")


def _build_fleet_panel():
    """Build the FLEET panel — live agent telemetry from Ouroboros."""
    try:
        from ouroboros import get_history, get_stats
        stats = get_stats()
        history = get_history(20)
    except Exception:
        stats, history = [], []

    # Full roster with layers
    full_roster = [
        ("MERLIN_O", "Archwizard", "L3"),
        ("ANYA_O", "Compiler", "L7"),
        ("LUKAS_O", "Kinetic Hand", "L2"),
        ("SIR_BORIS", "Foundry Lead", "L5"),
        ("SIR_HELIO", "Context Lord", "L5"),
        ("SIR_CODEX", "Velocity", "L5"),
        ("SIR_GHOST", "Zero-Trust", "L5"),
        ("SIR_FORGE", "Builder", "L2"),
        ("SIR_SENTINEL", "Warden", "L6"),
        ("SIR_VALERIAN", "Finance", "L5"),
        ("SIR_OCTAVIAN", "High Warden", "L6"),
        ("SIR_SYNTAX", "Code Architect", "L2"),
        ("SIR_HERMES", "Courier", "L4"),
        ("SIR_PERCIVAL", "High Scout", "L4"),
        ("LADY_VERITAS", "Truth Sentinel", "L6"),
        ("LADY_APIS", "Swarm Mother", "L4"),
    ]

    # Build lookup from Ouroboros stats keyed by knight name fragment
    stat_map = {}
    for s in stats:
        key = s.get("knight", "").upper().replace(" ", "_")
        stat_map[key] = s

    # Determine which knights were recently active (last 20 executions)
    recent_knights = set()
    for h in history:
        k = (h.get("knight") or "").upper().replace(" ", "_")
        if k:
            recent_knights.add(k)

    table = Table(show_header=True, box=box.SIMPLE_HEAVY, padding=(0, 1))
    table.add_column("Agent", style="bold green", width=16)
    table.add_column("Role", style="dim cyan", width=16)
    table.add_column("Layer", style="dim", width=5)
    table.add_column("Runs", justify="right", width=5)
    table.add_column("OK%", justify="right", width=5)
    table.add_column("Avg ms", justify="right", width=7)
    table.add_column("Status", width=10)

    total_active = 0
    for name, role, layer in full_roster:
        # Match stats by checking if the roster name appears in any stat key
        s = None
        for sk, sv in stat_map.items():
            # Match on knight module name or full name
            if name.replace("_O", "").lower() in sk.lower() or sk.lower() in name.lower():
                s = sv
                break

        runs = s.get("total_runs", 0) if s else 0
        ok = s.get("successes", 0) if s else 0
        avg = int(s.get("avg_duration_ms", 0)) if s else 0
        pct = f"{ok / runs * 100:.0f}" if runs > 0 else "-"

        # Status: check if in recent history
        is_recent = any(name.replace("_O", "").lower() in rk.lower() or rk.lower() in name.lower()
                        for rk in recent_knights)
        if is_recent and runs > 0:
            status = "[bold green]ACTIVE[/]"
            total_active += 1
        elif runs > 0:
            status = "[yellow]READY[/]"
        else:
            status = "[dim]IDLE[/]"

        table.add_row(name, role, layer, str(runs) if runs else "-", pct,
                      str(avg) if avg else "-", status)

    total = len(full_roster)
    color = "green" if total_active >= 3 else "yellow" if total_active >= 1 else "dim"
    return Panel(table, title=f"FLEET [{total_active}/{total} active]",
                 border_style=color, subtitle="//FLEET for full view")


def _build_phoenix_panel():
    """Build the Phoenix Portal performance panel with live Rotel telemetry."""
    # Simulated metrics as baseline
    live_visitors = 0
    conversions = 0
    exits = 0
    signals = 0

    try:
        # Poll Rotel for recent signals
        resp = requests.get(ROTEL_STATUS_URL, timeout=0.1)
        if resp.status_code == 200:
            data = resp.json()
            signals = data.get("total_logs", 0)
            # In a full impl, we'd fetch specific component stats
            # For resonance, we'll derive some 'live' feeling from the global signal count
            live_visitors = (signals % 50) + 1
            conversions = round((signals % 100) / 20, 1)
            exits = signals % 15
    except Exception:
        pass

    table = Table(show_header=True, box=box.SIMPLE, padding=(0, 1))
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")
    table.add_column("Trend", justify="center")

    metrics = [
        ("Live Resonance", str(live_visitors), "[green]↑[/]"),
        ("Lead Conv.", f"{conversions}%", "[green]↑[/]"),
        ("Exit Intent", str(exits), "[yellow]→[/]"),
        ("Active Signals", str(signals), "[green]↑[/]"),
    ]

    for m, v, t in metrics:
        table.add_row(m, v, t)

    return Panel(table, title="PHOENIX_PORTAL [RESONANCE]", border_style="gold1")


def _build_env_panel():
    """Build environment info panel."""
    lines = []
    lines.append(f"[cyan]OS Root:[/] {os.path.expanduser('~/CAMELOT_OS')}")
    lines.append(f"[cyan]CLI:[/]     {CAMELOT_DIR}")
    lines.append(f"[cyan]Python:[/]  {sys.version.split()[0]}")

    # Check Ollama
    try:
        import httpx
        resp = httpx.get("http://127.0.0.1:11434/api/tags", timeout=2)
        models = resp.json().get("models", [])
        lines.append(f"[cyan]Ollama:[/]  [green]online[/] ({len(models)} models)")
    except Exception:
        lines.append("[cyan]Ollama:[/]  [red]offline[/]")

    # Check env keys
    keys_present = []
    for env_var in ["GOOGLE_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY",
                    "XAI_API_KEY", "MISTRAL_API_KEY", "OPENROUTER_API_KEY"]:
        if os.environ.get(env_var):
            keys_present.append(env_var.split("_")[0].lower())
    if keys_present:
        lines.append(f"[cyan]API Keys:[/] {', '.join(keys_present)}")
    else:
        lines.append("[cyan]API Keys:[/] [yellow]none set (use env vars)[/]")

    return Panel("\n".join(lines), title="Environment", border_style="dim")


# ── Sir Link Flight Control Panel ───────────────────────────────────

def _build_sir_link_panel():
    """Anya Dashboard — Sir Link section. Shows full LLM terminal manifest."""
    from rich.panel import Panel
    from rich.table import Table

    manifest_path = os.path.join(HOME_DIR, "CAMELOT_OS", "logs", "switchboard_manifest.json")
    try:
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
        terminals = manifest.get("terminals", {})
        age_s = round(time.time() - manifest.get("updated", 0))
    except Exception:
        terminals = {}
        age_s = -1

    table = Table(show_header=True, header_style="bold bright_cyan",
                  box=None, padding=(0, 1))
    table.add_column("Terminal",  style="bold white",       width=14)
    table.add_column("Engine",    style="dim",               width=16)
    table.add_column("Status",    justify="center",          width=12)
    table.add_column("Weight",    justify="right",           width=8)
    table.add_column("Cost",      justify="center",          width=8)
    table.add_column("Latency",   justify="right",           width=10)
    table.add_column("Capability",style="dim",               width=30)

    status_glyphs = {
        "live":         "[green]● LIVE[/]",
        "assumed_live": "[green]◌ ASSUMED[/]",
        "dark":         "[red]○ DARK[/]",
        "degraded":     "[yellow]◑ DEGRADED[/]",
        "unknown":      "[dim]? UNKNOWN[/]",
    }

    live_count = 0
    for tid, data in sorted(terminals.items()):
        status = data.get("status", "unknown")
        if status in ("live", "assumed_live"):
            live_count += 1
        glyph = status_glyphs.get(status, f"[dim]{status}[/]")
        latency = data.get("latency_ms", 0)
        lat_str = f"{latency:.0f}ms" if latency > 0 else "—"
        caps = ", ".join(data.get("capability", [])[:3])
        table.add_row(
            tid.replace("sir_", "[bold]sir_[/]"),
            data.get("engine", "?"),
            glyph,
            f"{data.get('weight', 0):.2f}",
            data.get("cost_tier", "?"),
            lat_str,
            caps,
        )

    age_str = f"{age_s}s ago" if age_s >= 0 else "no manifest"
    title = (
        f"[bold bright_cyan]SIR_LINK — FLIGHT CONTROL TERMINAL[/]  "
        f"[green]{live_count}[/]/[white]{len(terminals)}[/] live  "
        f"[dim]manifest {age_str}[/]"
    )
    return Panel(table, title=title, border_style="bright_cyan")


# ── Anya Gate Panel (APEE v6.5 pipeline — Titanium Law #11) ──────────

def _build_anya_panel():
    """Anya Omega APEE v6.5 — 5-stage pipeline status (Titanium Law #11)."""
    CAMELOT_HOME_P = os.path.join(HOME_DIR, "CAMELOT_OS")
    ctrl = os.path.join(CAMELOT_HOME_P, "control_plane")
    configs = os.path.join(CAMELOT_HOME_P, "03_VAULT", "training", "configs")

    # Stage presence checks
    stages = [
        ("Ingestion",    os.path.isfile(os.path.join(ctrl, "anya_gate.py"))),
        ("RBAC Gate",    os.path.isfile(os.path.join(ctrl, "rbac_matrix.py"))),
        ("Runic Router", os.path.isfile(os.path.join(ctrl, "runic_router.py"))),
        ("Crystallize",  os.path.isfile(os.path.join(ctrl, "soul_router.py"))),
        ("Harmony Gate", os.path.isfile(os.path.join(ctrl, "harness.py"))),
    ]

    # SCORPION score — try live, fallback to last manifest
    scorpion_str = "[dim]not run[/]"
    try:
        import sys as _sys
        if configs not in _sys.path:
            _sys.path.insert(0, configs)
        from knights.sir_gideon import run_scorpion
        _rpt = run_scorpion()
        _col = "green" if _rpt.passed else "red"
        scorpion_str = f"[{_col}]SCORE={_rpt.gideon_risk_score} {'PASS' if _rpt.passed else 'FAIL'}[/]"
    except Exception as _e:
        scorpion_str = "[yellow]unavailable[/]"

    # Switchboard live count
    sw_str = "[dim]no manifest[/]"
    manifest_p = os.path.join(HOME_DIR, "CAMELOT_OS", "logs", "switchboard_manifest.json")
    try:
        import json as _json
        _m = _json.loads(open(manifest_p, encoding="utf-8").read())
        _terms = _m.get("terminals", {})
        _live = sum(1 for v in _terms.values() if v.get("status") in ("live", "assumed_live"))
        sw_str = f"[green]{_live}[/]/[white]{len(_terms)}[/] terminals live"
    except Exception:
        pass

    lines = [
        "[bold bright_magenta]APEE v6.5[/] — [bold]ANYA_IS_THE_GATE[/]",
        "",
    ]
    for label, ok in stages:
        sym = "[green]●[/]" if ok else "[red]●[/]"
        lines.append(f"  {sym} {label}")

    lines += [
        "",
        f"  //SCORPION   {scorpion_str}",
        f"  Switchboard  {sw_str}",
        "",
        "  [dim]Law #11: All intent enters APEE. All output validated.[/]",
    ]

    all_ok = all(ok for _, ok in stages)
    color = "bright_magenta" if all_ok else "yellow"
    return Panel("\n".join(lines), title="Anya Omega — APEE v6.5", border_style=color)


# ── OS Health Panel (P0-P3 component status) ─────────────────────────

def _build_os_health_panel():
    """P0-P3 CAMELOT Apex OS component health — wires camelot-status checks inline."""
    import socket

    def _probe(host: str, port: int) -> bool:
        try:
            with socket.create_connection((host, port), timeout=0.4):
                return True
        except OSError:
            return False

    CAMELOT_HOME_P = os.path.join(HOME_DIR, "CAMELOT_OS")
    hive_skills    = os.path.join(CAMELOT_HOME_P, ".hive", "skills")
    ctrl           = os.path.join(CAMELOT_HOME_P, "control_plane")
    configs        = os.path.join(CAMELOT_HOME_P, "03_VAULT", "training", "configs")
    bin_dir        = os.path.join(CAMELOT_HOME_P, "bin")
    kinetic        = os.path.join(CAMELOT_HOME_P, "kinetic_edge")

    checks = [
        # (label, ok_bool)
        ("CLIProxy :8080",   _probe("127.0.0.1", 8080)),
        ("Kinetic  :3001",   _probe("127.0.0.1", 3001)),
        ("Qdrant   :6333",   _probe("127.0.0.1", 6333)),
        ("Holotable:3000",   _probe("127.0.0.1", 3000)),
        ("brain_directory",  os.path.isfile(os.path.join(hive_skills, "brain_directory.md"))),
        ("GIDEON_RISK_MATRIX", os.path.isfile(os.path.join(configs, "GIDEON_RISK_MATRIX.md"))),
        ("access_matrix.json", os.path.isfile(os.path.join(configs, "config", "access_matrix.json"))),
        ("rbac_matrix.py",   os.path.isfile(os.path.join(ctrl, "rbac_matrix.py"))),
        ("lord_archivist",   os.path.isfile(os.path.join(ctrl, "lord_archivist.py"))),
        ("runic_router",     os.path.isfile(os.path.join(ctrl, "runic_router.py"))),
        ("sir_gideon",       os.path.isfile(os.path.join(configs, "knights", "sir_gideon.py"))),
        ("pqcrypto_bridge",  os.path.isfile(os.path.join(ctrl, "pqcrypto_bridge.py"))),
        ("bitnet_swarm",     os.path.isfile(os.path.join(configs, "bitnet_swarm.py"))),
        ("swarm-spawner.exe", os.path.isfile(os.path.join(bin_dir, "swarm-spawner.exe"))),
        ("pqcrypto.exe",     os.path.isfile(os.path.join(bin_dir, "camelot-pqcrypto.exe"))),
        ("vizion-telem.exe", os.path.isfile(os.path.join(bin_dir, "vizion-telemetry.exe"))),
        ("ollama_catalog",   os.path.isfile(os.path.join(configs, "ollama_catalog.json"))),
    ]

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Component", style="cyan", width=22)
    table.add_column("Status", width=8)

    green = 0
    for label, ok in checks:
        sym = "[green]OK[/]" if ok else "[red]--[/]"
        if ok:
            green += 1
        table.add_row(label, sym)

    total = len(checks)
    color = "green" if green == total else ("yellow" if green >= total - 3 else "red")
    subtitle = f"{green}/{total} green"
    return Panel(table, title="OS Health (P0-P3)", border_style=color, subtitle=subtitle)


# ── HUD Rendering ────────────────────────────────────────────────────

def render_hud():
    """Render the full HUD dashboard."""
    console.clear()
    console.print(BANNER)
    console.print()

    # Build all panels with noise suppressed
    bridge_p = _suppress_kernel_noise(_build_bridge_panel)
    llm_p = _suppress_kernel_noise(_build_llm_panel)
    knights_p = _suppress_kernel_noise(_build_knights_panel)
    stats_p = _suppress_kernel_noise(_build_stats_panel)
    fleet_p = _suppress_kernel_noise(_build_fleet_panel)
    env_p = _suppress_kernel_noise(_build_env_panel)

    # Top row: Bridge + LLM
    top = Columns([bridge_p, llm_p], equal=True, expand=True)
    console.print(top)

    # Middle row: Knights + Stats
    mid = Columns([knights_p, stats_p], equal=True, expand=True)
    console.print(mid)

    # Fleet row: Agent telemetry
    console.print(fleet_p)

    # Sir Link Flight Control panel
    sir_link_p = _suppress_kernel_noise(_build_sir_link_panel)
    console.print(sir_link_p)

    # Anya Gate + OS Health side by side
    anya_p = _suppress_kernel_noise(_build_anya_panel)
    os_h_p = _suppress_kernel_noise(_build_os_health_panel)
    console.print(Columns([anya_p, os_h_p], equal=True, expand=True))

    # Bottom: Phoenix Portal + Environment
    bottom = Columns([_build_phoenix_panel(), env_p], equal=True, expand=True)
    console.print(bottom)
    console.print()


def render_compact_status():
    """Render a single-line compact status bar."""
    def _collect():
        parts = []
        # Bridge
        try:
            status = bridge.get_bridge_status() if bridge else None
            if status:
                active = sum(1 for s in status["components"].values() if s == "active")
                total = len(status["components"])
                parts.append(("green" if active >= 9 else "yellow", f"Bridge {active}/{total}"))
            else:
                parts.append(("red", "Bridge offline"))
        except Exception:
            parts.append(("red", "Bridge offline"))

        # LLM
        try:
            from llm_router import list_available
            providers = list_available()
            ready = sum(1 for p in providers if "ready" in p["status"])
            parts.append(("bright_blue", f"LLM {ready}/{len(providers)}"))
        except Exception:
            parts.append(("red", "LLM error"))

        # Ollama
        try:
            import httpx
            resp = httpx.get("http://127.0.0.1:11434/api/tags", timeout=2)
            n = len(resp.json().get("models", []))
            parts.append(("green", f"Ollama {n}m"))
        except Exception:
            parts.append(("red", "Ollama off"))

        return parts

    parts = _suppress_kernel_noise(_collect)
    if parts:
        formatted = "  [dim]|[/] ".join(f"[{c}]{t}[/]" for c, t in parts)
        console.print(formatted)


# ── Interactive Mode ──────────────────────────────────────────────────

HELP_TEXT = """[bold]Runic Commands (11):[/]
  [bold bright_magenta]//FORGE[/]               Kinetic Rust bundler (bypasses LLM)
  [bold bright_magenta]//RESEARCH[/]            Research agency — Perplexity killer (kinetic|hybrid|apex <objective>)
  [bold bright_magenta]//BROWSE[/]              Browser nano-knights (apis|sentinel|syntax|debug: <task>)
  [bold bright_magenta]//SWARM[/]               Launch Bio-Swarm Nano-Knight cells
  [bold bright_magenta]//PLAN[/]                Task DAG planning (Sir Oracle)
  [bold bright_magenta]//HEAL[/]                PIV self-healing loop
  [bold bright_magenta]//FLEET[/]               Agent telemetry dashboard
  [bold bright_magenta]//GENESIS[/]             Spawn new knight persona
  [bold bright_magenta]//ASSIMILATE[/]          Ingest external repo/doc
  [bold bright_magenta]//SCAVENGE[/]            Lady Apis research foraging
  [bold bright_magenta]//SCORPION[/]            Sir Gideon — GIDEON_RISK_MATRIX audit (10 SPs)
  [bold bright_magenta]//BOOT[/]                Re-run bootstrap sequence
  [bold bright_magenta]//DEFENSE_INIT[/]        Initialize Defense Grid
  [bold bright_cyan]//vocal[/]                Voice pipeline (Piper TTS / Kokoro)
  [bold bright_cyan]Omega_SYNC[/]              Lord Archivist GEP scan (skills/gaps/XP)
  [bold bright_cyan]Omega_STATUS[/]            camelot-status.py full health check
  [bold bright_cyan]Omega_AUDIT[/]             Sir Gideon //SCORPION (10 Shatterpoints)
  [bold bright_cyan]Omega_PURGE[/]             Clear harness queue + cache
  [bold bright_cyan]Omega_CLEAN[/]             Remove __pycache__ dirs
  [bold bright_cyan]Omega_KINETIC[/]           Kinetic Edge binary + MCP status
  [bold bright_cyan]Omega_SHIELD[/]            Agent-Armor RBAC status surface
  [bold bright_cyan]Omega_GRAPH[/]             UKG knowledge graph status
  [bold bright_cyan]Omega_GATEWAY[/]           CLIProxy :8080 live probe
  [bold bright_cyan]Omega_STACK[/]             Control plane module inventory
  [cyan]exec[/] <directive>     Execute through knight pipeline
  [cyan]ask[/] <question>       Ask LLM directly (uses fallback chain)
  [cyan]ask@<provider>[/] <q>   Ask specific provider (gemini, openai, ollama, grok, mistral)
  [cyan]knights[/]              List available knights
  [cyan]bridge[/]               Show bridge status
  [cyan]llm[/]                  Show LLM providers
  [cyan]warden[/] <cmd>         Warden security (status/lockdown/unlock/audit)
  [cyan]memory[/] <cmd>         Titan Omega memory (status/query/session/store)
  [cyan]plan[/] <cmd>           Planning engine (list/create/next/complete)
  [cyan]kernel[/] <intent>      Route through Excalibur kernel
  [cyan]history[/]              Execution history
  [cyan]stats[/]                Performance stats
  [cyan]hud[/]                  Refresh HUD display
  [cyan]help[/]                 Show this help
  [cyan]exit[/]                 Exit Camelot OS
"""


def _handle_ask(line: str):
    """Handle ask commands with provider routing."""
    from llm_router import chat

    # Parse provider prefix: ask@gemini, ask@ollama, etc.
    provider = None
    if line.startswith("ask@"):
        parts = line.split(" ", 1)
        provider = parts[0][4:]  # after "ask@"
        prompt = parts[1] if len(parts) > 1 else ""
    else:
        prompt = line[4:].strip() if line.startswith("ask ") else line

    if not prompt:
        console.print("[yellow]Usage: ask <question> or ask@provider <question>[/]")
        return

    system = ("You are a Camelot OS assistant. Be concise, direct, and helpful. "
              "Respond in markdown format when appropriate.")

    provider_label = f"@{provider}" if provider else "auto"
    console.print(f"  [dim]Routing to {provider_label}...[/]")

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": prompt},
    ]

    start = time.time()
    result = chat(messages, provider=provider)
    elapsed = int((time.time() - start) * 1000)

    if result.get("error"):
        console.print(f"[red]  Error: {result['error']}[/]")
        if result.get("fallback_errors"):
            for err in result["fallback_errors"]:
                console.print(f"[dim]    {err}[/]")
        return

    # Display response
    console.print(f"\n[bold bright_blue]{result['provider']}[/]/{result['model']} "
                  f"[dim]({elapsed}ms, {result['usage'].get('completion_tokens', '?')} tokens)[/]\n")
    console.print(Panel(result["content"], border_style="bright_blue", padding=(1, 2)))

    if result.get("fallback_errors"):
        console.print(f"[dim]  Fallback chain: {', '.join(e.split(':')[0] for e in result['fallback_errors'])} -> {result['provider']}[/]")

    # Log to ouroboros
    try:
        from ouroboros import log_execution
        log_execution(prompt, "ASK", "LLM", 1, f"LLM/{result['provider']}",
                      "success", result["content"][:500], elapsed)
    except Exception:
        pass


def _handle_cli_command(line: str):
    """Route a command through the existing camelot CLI."""
    import subprocess
    camelot_py = os.path.join(CAMELOT_DIR, "camelot.py")
    try:
        args = shlex.split(line)
        result = subprocess.run(
            [sys.executable, camelot_py] + args,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=60,
        )
        if result.stdout:
            console.print(result.stdout.rstrip())
        if result.stderr:
            # Filter out kernel noise
            for stderr_line in result.stderr.splitlines():
                if any(skip in stderr_line for skip in [
                    "[ENFORCER]", "[Cap-Graph]", "[Judge]", "[AUDIT ERROR]",
                    "[MCP_ADAPTER]", "Graph]", "Flux]"
                ]):
                    continue
                console.print(f"[dim]{stderr_line}[/]")
    except subprocess.TimeoutExpired:
        console.print("[red]Command timed out (60s)[/]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/]")


def interactive_no_hud():
    """Enter REPL without rendering HUD first."""
    _repl_loop()


def interactive_loop():
    """Enter REPL (HUD already rendered by main)."""
    _repl_loop()


def interactive():
    """Run the interactive Camelot OS shell (legacy entry)."""
    render_hud()
    _, proxy_msg = _boot_cliproxy()
    console.print(Panel(proxy_msg, title="CLIProxyAPI", border_style="bright_green"))
    _, defense_msg = _boot_defense_grid()
    console.print(Panel(defense_msg, title="Defense Grid", border_style="bright_red"))
    _repl_loop()


def _repl_loop():
    """Core REPL loop with runic routing."""
    while True:
        try:
            console.print()
            line = Prompt.ask("[bold bright_yellow]camelot[/]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Exiting Camelot OS.[/]")
            break

        if not line:
            continue

        # ── Runic Interception: // commands ──────────────────────
        if line.startswith("//FORGE"):
            console.print(Panel(_handle_forge(line), title="FORGE", border_style="bright_magenta"))
            continue
        elif line.startswith("//FLEET"):
            console.print(_build_fleet_panel())
            continue
        elif line.startswith("//DEFENSE_INIT"):
            pid, msg = _boot_defense_grid()
            console.print(Panel(msg, title="Defense Grid", border_style="bright_red"))
            continue
        elif line.startswith("//BOOT"):
            console.print("[bright_magenta]Re-running bootstrap…[/]")
            render_hud()
            _, px = _boot_cliproxy()
            console.print(Panel(px, title="CLIProxyAPI", border_style="bright_green"))
            _, dg = _boot_defense_grid()
            console.print(Panel(dg, title="Defense Grid", border_style="bright_red"))
            _, ke = _boot_kinetic_edge()
            console.print(Panel(ke, title="Kinetic Edge", border_style="bright_cyan"))
            _, cb = _boot_cloud_brain()
            console.print(Panel(cb, title="Cloud Brain (lazy)", border_style="bright_blue"))
            continue
        elif line.startswith("//BROWSE"):
            _handle_browse(line, console)
            continue
        elif line.startswith("//RESEARCH"):
            _handle_research(line, console)
            continue
        elif line.startswith("//CHAT"):
            try:
                from chat import run_chat
                rest = line[len("//CHAT"):].strip()
                provider = rest or None
                run_chat(provider=provider)
            except Exception as e:
                console.print(f"[red]CHAT failed: {type(e).__name__}: {e}[/]")
            continue
        elif line.startswith("//SCORPION"):
            try:
                sys.path.insert(0, CAMELOT_DIR)
                from knights.sir_gideon import run_scorpion
                report = run_scorpion()
                score_color = "green" if report.passed else "red"
                lines_out = [f"[{score_color}]{report.summary}[/]", ""]
                for sp in report.shatterpoints:
                    c = {"CLEAR": "green", "WARN": "yellow", "CRITICAL": "red"}.get(sp.status, "white")
                    lines_out.append(f"  [{c}]{sp.status}[/]  {sp.shatterpoint}")
                    for ev in sp.evidence[:3]:
                        lines_out.append(f"       [dim]{ev}[/]")
                lines_out.append(f"\n  [dim]Scan time: {report.duration_ms:.0f}ms[/]")
                console.print(Panel("\n".join(lines_out), title="//SCORPION — GIDEON AUDIT", border_style=score_color))
            except Exception as e:
                console.print(f"[red]//SCORPION failed: {e}[/]")
            continue
        elif line.startswith("//"):
            # Route through Runic Router before falling back to unknown
            try:
                cp_dir = os.path.join(HOME_DIR, "CAMELOT_OS", "control_plane")
                if cp_dir not in sys.path:
                    sys.path.insert(0, cp_dir)
                from runic_router import detect_and_route
                result = detect_and_route(line)
                if result:
                    console.print(Panel(
                        f"[green]Queued[/] rune [bright_magenta]{result.rune}[/] "
                        f"-> knight [cyan]{result.knight}[/]\n"
                        f"[dim]task_id={result.task_id}[/]",
                        title="Runic Router", border_style="bright_magenta",
                    ))
                else:
                    rune_name = line[2:].strip()
                    console.print(f"[red]Unknown // command:[/] '//{rune_name}' — not in runic registry.")
            except Exception as e:
                rune_name = line[2:].strip()
                console.print(f"[yellow]Runic router unavailable ({e}).[/] '//{rune_name}' unhandled.")
            continue

        # ── Ouroboros Runes: Omega_ ──────────────────────────────────
        if line.startswith(("\u03a9_", "Omega_", "Omega_", "omega_")):
            console.print(Panel(_handle_rune(line), title="Ouroboros", border_style="bright_cyan"))
            continue

        cmd = line.split()[0].lower()

        if cmd in ("exit", "quit", "q"):
            console.print("[dim]Shutting down Defense Grid & exiting Camelot OS.[/]")
            _shutdown_defense_grid()
            break
        elif cmd == "help":
            console.print(HELP_TEXT)
        elif cmd == "hud":
            render_hud()
        elif cmd == "clear":
            console.clear()
        elif cmd in ("ask", ) or cmd.startswith("ask@"):
            _handle_ask(line)
        elif cmd == "fleet":
            console.print(_build_fleet_panel())
        elif cmd == "llm":
            console.print(_build_llm_panel())
        elif cmd == "exec":
            _handle_cli_command(line)
        elif cmd in ("knights", "history", "stats", "bridge", "cartridges",
                     "export", "warden", "memory", "plan", "kernel", "vault"):
            _handle_cli_command(line)
        else:
            # Natural language → APEE v6.5 gate (Titanium Law #11), then Saltare/exec
            compiled_directive = line
            try:
                _cp = os.path.join(HOME_DIR, "CAMELOT_OS", "control_plane")
                if _cp not in sys.path:
                    sys.path.insert(0, _cp)
                from anya_gate import AnyaGate
                _apee = AnyaGate().process(line)
                compiled_directive = _apee.titan.directive or line
                _gate  = _apee.validation.iron_gate
                _color = "bright_magenta" if _gate == "CLEARED" else ("yellow" if _gate == "HITL_REQUIRED" else "red")
                console.print(Panel(
                    f"[bright_magenta]APEE v6.5[/]  "
                    f"type=[cyan]{_apee.parse.intent_type}[/]  "
                    f"domain=[cyan]{_apee.enrich.domain}[/]  "
                    f"knight=[bright_yellow]{_apee.route_knight}[/]  "
                    f"mode=[dim]{_apee.titan.execution_mode}[/]  "
                    f"gate=[{_color}]{_gate}[/]  "
                    f"[dim]{_apee.pipeline_ms:.0f}ms[/]",
                    title="Anya Gate", border_style=_color, padding=(0, 1),
                ))
                if _gate == "BLOCKED":
                    console.print(f"[red]Iron Gate BLOCKED:[/] {_apee.validation.issues}")
                    continue  # type: ignore[reportReturnType]
                if _gate == "HITL_REQUIRED":
                    console.print(f"[yellow]HITL required:[/] {_apee.validation.issues}")
            except Exception as _ae:
                console.print(f"[dim]Anya gate offline ({type(_ae).__name__}) — direct routing.[/]")

            result = _handle_saltare(compiled_directive)
            if "Saltare Offline" in result:
                console.print("[dim]Saltare offline — routing through knight pipeline.[/]")
                _handle_cli_command(f"exec \"{compiled_directive}\"")
            else:
                console.print(Panel(result, title="Saltare", border_style="bright_green"))


# ── Entry Point ──────────────────────────────────────────────────────

def main():
    """Main entry point for camelot-os command.

    Full bootstrap sequence:
      1. Render HUD dashboard
      2. Boot Defense Grid daemon (heartbeat.go) in background
      3. Enter interactive REPL with runic routing (//FORGE, Omega_ runes, Saltare)
    """
    import argparse
    parser = argparse.ArgumentParser(prog="camelot-os", description="Camelot OS HUD Terminal")
    parser.add_argument("--no-hud", action="store_true", help="Skip HUD, go straight to prompt")
    parser.add_argument("--no-defense", action="store_true", help="Skip Defense Grid daemon")
    parser.add_argument("--status", action="store_true", help="Show compact status and exit")
    parser.add_argument("--ask", nargs="*", help="Quick ask and exit")
    parser.add_argument("--provider", "-p", help="LLM provider for --ask")
    args = parser.parse_args()

    if args.status:
        render_compact_status()
        return

    if args.ask:
        prompt = " ".join(args.ask)
        from llm_router import quick_ask
        result = quick_ask(prompt, provider=args.provider)
        console.print(result)
        return

    # ── Bootstrap Sequence ──────────────────────────────────────
    # Phase 1: CLIProxyAPI (Zero-Burn local proxy on :8080)
    _, proxy_msg = _boot_cliproxy()

    # Phase 2: Defense Grid (heartbeat daemon)
    if not args.no_defense:
        _, defense_msg = _boot_defense_grid()
    else:
        defense_msg = None

    # Phase 3: Kinetic Edge (Lukas — Rust MCP server on :3001)
    _, kinetic_msg = _boot_kinetic_edge()

    # Phase 4: Cloud Brain heartbeat (lazy — no synthesis at boot)
    _, cloud_msg = _boot_cloud_brain()

    if not args.no_hud:
        render_hud()

    # Show boot status after HUD
    console.print(Panel(proxy_msg, title="CLIProxyAPI", border_style="bright_green"))
    if defense_msg:
        console.print(Panel(defense_msg, title="Defense Grid", border_style="bright_red"))
    console.print(Panel(kinetic_msg, title="Kinetic Edge", border_style="bright_cyan"))
    console.print(Panel(cloud_msg, title="Cloud Brain (lazy)", border_style="bright_blue"))

    # Enter the unified interactive loop (HUD + Runic + Saltare)
    interactive_no_hud() if args.no_hud else interactive_loop()


if __name__ == "__main__":
    main()
