"""
CLARITY_CORE v1.0.0 — Squire Colony CLI
Usage: python -m squires.colony [scan|index|ghost|vector|triage|status|graph] [path] [options]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

# Ensure UTF-8 on Windows consoles (prevents cp1252 codec errors with emoji)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── Rich (optional — graceful fallback) ──────────────────────────────────────
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    _RICH = True
except ImportError:
    _RICH = False


def _console() -> "Console | None":
    # legacy_windows=False uses ANSI instead of Win32 API (avoids double-write on PS5.1)
    return Console(legacy_windows=False) if _RICH else None


def _print(msg: str, style: str = "") -> None:
    if _RICH:
        c = _console()
        c.print(f"[{style}]{msg}[/{style}]" if style else msg)
    else:
        print(msg)


# ── Sub-commands ─────────────────────────────────────────────────────────────

def cmd_scan(root: Path, args: argparse.Namespace) -> None:
    from .scan import scan
    console = _console()
    records = list(scan(root))

    if _RICH:
        table = Table(title=f"SCAN — {root}", show_lines=False)
        table.add_column("File", style="cyan", max_width=60)
        table.add_column("Ext", style="green", width=8)
        table.add_column("Lines", justify="right", width=8)
        table.add_column("Size", justify="right", width=10)
        table.add_column("SHA", width=14)
        for rec in records[:200]:
            table.add_row(
                rec.rel,
                rec.ext,
                str(rec.lines),
                f"{rec.size:,}",
                rec.sha256,
            )
        if len(records) > 200:
            table.add_row(f"... {len(records) - 200} more files", "", "", "", "")
        console.print(table)
        console.print(f"\n[bold]Total:[/bold] {len(records)} files")
    else:
        for rec in records:
            print(f"{rec.rel:60} {rec.ext:8} {rec.lines:6} lines")
        print(f"\nTotal: {len(records)} files")


def cmd_index(root: Path, args: argparse.Namespace) -> None:
    from .index import build_index
    from .scan import scan

    t0 = time.perf_counter()
    _print("🔍 Scanning...", "dim")
    records = list(scan(root))
    _print(f"📚 Indexing {len(records)} files...", "dim")
    idx = build_index(iter(records))
    elapsed = time.perf_counter() - t0

    out_dir = root if root.is_dir() else root.parent
    out = out_dir / ".colony" / "index.json"
    idx.save(out)

    if _RICH:
        console = _console()
        console.print(Panel.fit(
            f"[bold green]Index built in {elapsed:.2f}s[/bold green]\n"
            f"Files: {idx.stats['total_files']:,}  |  "
            f"Symbols: {idx.stats['total_symbols']:,}  |  "
            f"Lines: {idx.stats['total_lines']:,}\n"
            f"Saved: [cyan]{out}[/cyan]",
            title="INDEX squire",
        ))
    else:
        print(f"Index built in {elapsed:.2f}s")
        print(f"Files: {idx.stats['total_files']}, Symbols: {idx.stats['total_symbols']}")
        print(f"Saved: {out}")


def cmd_ghost(root: Path, args: argparse.Namespace) -> None:
    from .ghost import triage
    from .scan import scan

    _print("👻 GHOST scanning for secrets/TODOs...", "dim")
    records = list(scan(root))
    report = triage(iter(records))
    summary = report.summary()

    if _RICH:
        console = _console()
        table = Table(title="GHOST Triage Report", show_lines=True)
        table.add_column("Severity", width=10)
        table.add_column("Kind", width=18)
        table.add_column("File", style="cyan", max_width=50)
        table.add_column("Line", justify="right", width=6)
        table.add_column("Detail", max_width=60)

        color = {"critical": "red", "warning": "yellow", "info": "dim"}
        for flag in report.flags:
            c = color.get(flag.severity, "white")
            table.add_row(
                f"[{c}]{flag.severity.upper()}[/{c}]",
                flag.kind,
                flag.file,
                str(flag.line) if flag.line else "-",
                flag.detail,
            )

        console.print(table)
        console.print(f"\n[bold]Summary:[/bold] {summary}")
    else:
        for flag in report.flags:
            print(f"[{flag.severity.upper()}] {flag.kind} {flag.file}:{flag.line} - {flag.detail}")
        print(f"\nSummary: {summary}")

    # CI mode: non-zero exit when critical flags exist (GHOST itself is
    # read-only — no HITL gate involved, unlike triage's report write).
    if getattr(args, "fail_on_critical", False) and report.critical:
        _print(
            f"❌ {len(report.critical)} critical flag(s) — failing (CI)",
            "red",
        )
        sys.exit(2)


def cmd_vector(root: Path, args: argparse.Namespace) -> None:
    from .scan import scan
    from .vector import build_corpus

    query = " ".join(args.query) if args.query else ""
    if not query:
        _print("Usage: colony vector <path> --query <search terms>", "red")
        sys.exit(1)

    _print(f"🔎 Building corpus and searching: '{query}'", "dim")
    records = list(scan(root))
    corpus = build_corpus(iter(records))
    results = corpus.search(query, top_k=args.top_k)

    if _RICH:
        console = _console()
        table = Table(title=f"Vector Search: '{query}'", show_lines=True)
        table.add_column("Rank", width=5)
        table.add_column("Score", width=8)
        table.add_column("File", style="cyan", max_width=50)
        table.add_column("Snippet", max_width=60)
        for i, match in enumerate(results, 1):
            table.add_row(str(i), str(match.score), match.file, match.snippet)
        console.print(table)
    else:
        for i, match in enumerate(results, 1):
            print(f"{i:2}. [{match.score:.4f}] {match.file}")
            print(f"    {match.snippet}")


def cmd_triage(root: Path, args: argparse.Namespace) -> None:
    from .ghost import triage as ghost_triage
    from .index import build_index
    from .judge import judge
    from .mason import build_report
    from .scan import scan
    from .sentinel import HITLBlocked, gate, soft_gate
    from .sweep import sweep

    _print("\n⚔️  CLARITY_CORE — Full Pipeline Triage", "bold")
    _print("Pipeline: SCAN → INDEX → GHOST → SWEEP → JUDGE → SENTINEL → MASON\n", "dim")

    t0 = time.perf_counter()

    # SCAN
    _print("📡 SCAN...", "dim")
    records = list(scan(root))
    _print(f"   {len(records)} files found", "dim")

    # INDEX
    _print("📚 INDEX...", "dim")
    idx = build_index(iter(records))

    # GHOST
    _print("👻 GHOST...", "dim")
    ghost_report = ghost_triage(iter(records))

    # SWEEP
    _print("🧹 SWEEP...", "dim")
    sweep_report = sweep(iter(records))

    # JUDGE
    _print("⚖️  JUDGE...", "dim")
    verdict = judge(ghost_report, sweep_report, idx)

    # SENTINEL gate
    if verdict.requires_hitl and not args.auto_approve:
        try:
            gate(verdict, action_label="write colony_report.md", auto_approve=False)
        except HITLBlocked as e:
            _print(f"\n🛑 {e}", "red")
            sys.exit(1)
    else:
        soft_gate(verdict)

    # MASON
    _print("\n🧱 MASON — writing report...", "dim")
    out = build_report(root, idx, ghost_report, sweep_report, verdict)

    elapsed = time.perf_counter() - t0

    if _RICH:
        risk_color = "red" if verdict.risk_label == "CRITICAL" else "yellow" if verdict.risk_label in ("HIGH", "MEDIUM") else "green"
        _console().print(Panel.fit(
            f"[bold green]Triage complete in {elapsed:.2f}s[/bold green]\n"
            f"Risk: [{risk_color}]{verdict.risk_label}[/{risk_color}] ({verdict.risk_score:.1f}/100)\n"
            f"Report: [cyan]{out}[/cyan]",
            title="CLARITY_CORE v1.0.0",
        ))
    else:
        print(f"\n✅ Triage complete in {elapsed:.2f}s")
        print(f"Risk: {verdict.risk_label} ({verdict.risk_score:.1f}/100)")
        print(f"Report: {out}")


def cmd_status(root: Path, args: argparse.Namespace) -> None:
    base_dir = root if root.is_dir() else root.parent
    colony_dir = base_dir / ".colony"
    index_file = colony_dir / "index.json"
    report_file = base_dir / "colony_report.md"

    if _RICH:
        console = _console()
        table = Table(title="Squire Colony Status", show_header=False, box=None)
        table.add_column("Key", style="bold", width=22)
        table.add_column("Value")

        def row(k, v, style=""):
            table.add_row(k, f"[{style}]{v}[/{style}]" if style else str(v))

        row("Root", str(root))
        row("Index", str(index_file), "green" if index_file.exists() else "red")
        row("Report", str(report_file), "green" if report_file.exists() else "dim")
        graft_manifest = base_dir / "graft" / "manifest.json"
        row(
            "Graft graph",
            str(graft_manifest),
            "green" if graft_manifest.exists() else "dim",
        )

        if index_file.exists():
            try:
                data = json.loads(index_file.read_text(encoding="utf-8"))
                stats = data.get("stats", {})
                row("Files indexed", f"{stats.get('total_files', '?'):,}")
                row("Symbols", f"{stats.get('total_symbols', '?'):,}")
                row("Lines", f"{stats.get('total_lines', '?'):,}")
            except Exception:
                row("Index", "corrupted", "red")

        try:
            from .pagekeeper import SquirePageKeeper
            pk = SquirePageKeeper()
            audit = pk.audit()
            status_color = "green" if audit.node_compliant else "red"
            row("PageKeeper RAM", f"{audit.used_physical_mb:,.0f}/{audit.total_physical_mb:,.0f} MB ({audit.utilization_pct}%)", status_color)
            row("Node Compliance", f"Ceiling {audit.node_ceiling_mb:.0f} MB — {'PASS' if audit.node_compliant else 'WARN'}", status_color)
        except Exception:
            pass

        console.print(table)
    else:
        print(f"Root:   {root}")
        print(f"Index:  {'✅' if index_file.exists() else '❌'} {index_file}")
        print(f"Report: {'✅' if report_file.exists() else '—'} {report_file}")
        graft_manifest = base_dir / "graft" / "manifest.json"
        print(f"Graft:  {'✅' if graft_manifest.exists() else '—'} {graft_manifest}")
        try:
            from .pagekeeper import SquirePageKeeper
            pk = SquirePageKeeper()
            audit = pk.audit()
            print(f"RAM:    {'✅' if audit.node_compliant else '⚠️'} {audit.used_physical_mb:,.0f}/{audit.total_physical_mb:,.0f} MB ({audit.utilization_pct}%) [Node Ceiling: {audit.node_ceiling_mb:.0f} MB]")
        except Exception:
            pass


def cmd_graph(root: Path, args: argparse.Namespace) -> None:
    """Read-only graft context-graph query — `map` by default, `ask` with --query."""
    graft = shutil.which("graft")
    if not graft:
        _print("❌ graft CLI not found on PATH — npm install -g @nanonets/graft", "red")
        sys.exit(1)
    if args.query:
        argv = ["ask", " ".join(args.query), "--source"]
    else:
        argv = ["map"]
    base = root if root.is_dir() else root.parent
    _print(f"🔗 graft {' '.join(argv)}", "dim")
    rc = subprocess.run([graft, *argv], cwd=str(base)).returncode
    if rc:
        sys.exit(rc)


def cmd_conform(root: Path, args: argparse.Namespace) -> None:
    """Hardware-accelerated filesystem reconciliation & deduplication via conform.exe."""
    conform_bin = Path(os.environ.get("CONFORM_BIN", Path.home() / "tools" / "conform" / "target" / "release" / "conform.exe"))
    if not conform_bin.exists():
        conform_bin = Path.home() / "tools" / "conform" / "target" / "debug" / "conform.exe"

    if not conform_bin.exists():
        _print(f"❌ conform.exe binary not found at {conform_bin} — run 'cargo build --release' in tools/conform", "red")
        sys.exit(1)

    subcmd = "dedupe" if getattr(args, "dedupe", False) else "scan"
    cmd = [str(conform_bin), subcmd, str(root)]
    if getattr(args, "dry_run", False) and subcmd == "dedupe":
        cmd.append("--dry-run")
    if getattr(args, "min_size", None) and subcmd == "dedupe":
        cmd.extend(["--min-size", str(args.min_size)])

    _print(f"⚡ Delegating to Conform engine: {' '.join(cmd)}", "dim")
    rc = subprocess.run(cmd).returncode
    if rc == 0 and getattr(args, "dedupe", False) and not getattr(args, "dry_run", False):
        try:
            from control_plane.infra.conform_xp_hook import award_xp_for_conform
            award_xp_for_conform("sir_forge", "A", 100, f"Colony Conform deduplication on {root.name}", apply=True)
        except Exception:
            pass
    if rc:
        sys.exit(rc)


def cmd_pagekeeper(root: Path, args: argparse.Namespace) -> None:
    """Autonomous working set balancing and memory governance."""
    from .pagekeeper import SquirePageKeeper
    threshold = getattr(args, "threshold", 80.0) or 80.0
    execute_trim = getattr(args, "trim", False)
    keeper = SquirePageKeeper(pressure_threshold_pct=threshold)

    audit = keeper.govern(force_trim=execute_trim) if execute_trim else keeper.audit()

    if getattr(args, "json", False):
        print(json.dumps(audit.to_dict(), indent=2))
        return

    if _RICH:
        console = _console()
        table = Table(title="Squire PageKeeper — Memory Governance", show_header=False, box=None)
        table.add_column("Metric", style="bold", width=25)
        table.add_column("Value")

        def r(k, v, s=""):
            table.add_row(k, f"[{s}]{v}[/{s}]" if s else str(v))

        r("Physical Total", f"{audit.total_physical_mb:,.1f} MB")
        r("Physical Free", f"{audit.free_physical_mb:,.1f} MB", "green")
        r("Physical Used", f"{audit.used_physical_mb:,.1f} MB ({audit.utilization_pct}%)")
        r("Current Process", f"{audit.process_working_set_mb:,.1f} MB")
        r("Node Ceiling (4GB)", f"{audit.node_ceiling_mb:,.1f} MB", "green" if audit.node_compliant else "red")
        r("Pressure Detected", f"{audit.pressure_detected}", "yellow" if audit.pressure_detected else "green")
        r("Action Taken", audit.action_taken, "cyan")
        if audit.reclaimed_mb > 0:
            r("Reclaimed RAM", f"+{audit.reclaimed_mb:,.1f} MB", "bold green")
        console.print(table)
    else:
        print(f"RAM Total:     {audit.total_physical_mb:,.1f} MB")
        print(f"RAM Free:      {audit.free_physical_mb:,.1f} MB")
        print(f"RAM Used:      {audit.used_physical_mb:,.1f} MB ({audit.utilization_pct}%)")
        print(f"Process RAM:   {audit.process_working_set_mb:,.1f} MB")
        print(f"Node Ceiling:  {audit.node_ceiling_mb:,.1f} MB ({'COMPLIANT' if audit.node_compliant else 'OVER_LIMIT'})")
        print(f"Action:        {audit.action_taken}")
        if audit.reclaimed_mb > 0:
            print(f"Reclaimed:     +{audit.reclaimed_mb:,.1f} MB")


def cmd_tokenpress(root: Path, args: argparse.Namespace) -> None:
    """Inter-agent payload and Symbolect compression benchmark."""
    from .tokenpress import SquireTokenPress
    press = SquireTokenPress()

    sample = (
        "All commands must pass ANYA_IS_THE_GATE on CYBERTRONIA before writing to PROVENANCE_LEDGER.md. "
        "MERLIN_OMEGA coordinates with SIR_HELIOS and SIR_LUCAS over TAILSCALE_MESH on Samsung Galaxy S26 Ultra."
    )
    if args.query:
        sample = " ".join(args.query)

    blob = press.compress_payload(sample)
    metrics = press.get_metrics(sample, blob)
    sym_compressed = press.compress_symbolect(sample)

    if getattr(args, "json", False):
        res = {
            "metrics": metrics,
            "symbolect": sym_compressed,
            "sample_len": len(sample),
            "blob_len": len(blob),
        }
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return

    if _RICH:
        console = _console()
        table = Table(title="Squire TokenPress — Payload & Symbolect Compression", show_header=False, box=None)
        table.add_column("Property", style="bold", width=22)
        table.add_column("Value")
        table.add_row("Algorithm", metrics["algorithm"])
        table.add_row("Original Size", f"{metrics['original_bytes']} bytes")
        table.add_row("Compressed Size", f"{metrics['compressed_bytes']} bytes", "green")
        table.add_row("Compression Ratio", metrics["ratio"], "cyan")
        table.add_row("RAM Savings", f"{metrics['savings_pct']}%", "bold green")
        table.add_row("Symbolect Encoded", sym_compressed[:80] + "..." if len(sym_compressed) > 80 else sym_compressed, "magenta")
        console.print(table)
    else:
        print(f"Algorithm:    {metrics['algorithm']}")
        print(f"Original:     {metrics['original_bytes']} bytes")
        print(f"Compressed:   {metrics['compressed_bytes']} bytes")
        print(f"Ratio:        {metrics['ratio']}")
        print(f"Savings:      {metrics['savings_pct']}%")
        print(f"Symbolect:    {sym_compressed}")


# ── Cron helpers ─────────────────────────────────────────────────────────────

def _parse_schedule(s: str) -> int:
    """Convert '6h', '30m', or raw seconds string to int seconds."""
    s = s.strip().lower()
    if s.endswith("h"):
        return int(s[:-1]) * 3600
    if s.endswith("m"):
        return int(s[:-1]) * 60
    return int(s)


def _inject_forge_directives(root: Path, ghost_report, verdict) -> int:
    """Write CRITICAL ghost findings as forge directives into the harness queue."""
    import uuid
    from datetime import datetime, timezone

    queue_file = root / "logs" / "harness_queue.jsonl"
    queue_file.parent.mkdir(parents=True, exist_ok=True)
    injected = 0
    for flag in ghost_report.flags:
        if flag.severity != "critical":
            continue
        task_id = f"colony-{uuid.uuid4().hex[:8]}"
        directive = (
            f"COLONY CRIT: {flag.kind} found in {flag.file} line {flag.line}. "
            f"Detail: {flag.detail}. Risk score: {verdict.risk_score:.0f}/100. "
            f"Investigate and remediate immediately."
        )
        entry = json.dumps({
            "id": task_id,
            "knight": "sir_sentinel",
            "directive": directive,
            "priority": 1,
            "submitted": datetime.now(timezone.utc).isoformat(),
            "source": "colony_cron",
        })
        with open(queue_file, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
        injected += 1
    return injected


def _cron_scan_and_inject(root: Path, auto_approve: bool) -> dict:
    """Full triage pipeline for cron mode; injects CRITICAL findings into harness queue."""
    from .ghost import triage as ghost_triage
    from .index import build_index
    from .judge import judge
    from .scan import scan
    from .sweep import sweep

    records = list(scan(root))
    idx = build_index(iter(records))
    ghost_report = ghost_triage(iter(records))
    sweep_report = sweep(iter(records))
    verdict = judge(ghost_report, sweep_report, idx)
    injected = _inject_forge_directives(root, ghost_report, verdict)
    return {
        "files": len(records),
        "risk_label": verdict.risk_label,
        "risk_score": verdict.risk_score,
        "critical_flags": sum(1 for f in ghost_report.flags if f.severity == "critical"),
        "injected": injected,
    }


# ── Main ─────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="colony",
        description="CLARITY_CORE v1.0.0 — Squire Colony codebase intelligence",
    )
    parser.add_argument(
        "command",
        choices=["scan", "index", "ghost", "vector", "triage", "status", "graph", "conform", "pagekeeper", "tokenpress"],
        help="Squire pipeline stage to run",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Root directory to analyze (default: current dir)",
    )
    parser.add_argument("--query", nargs="+", help="Search query (vector: keywords; graph: graft ask; tokenpress: text to compress)")
    parser.add_argument("--top-k", type=int, default=10, help="Number of vector results (default: 10)")
    parser.add_argument("--auto-approve", action="store_true", help="Skip SENTINEL HITL gate (CI mode)")
    parser.add_argument("--fail-on-critical", action="store_true",
                        help="ghost: exit 2 when critical flags found (CI secret gate)")
    parser.add_argument("--schedule", metavar="INTERVAL", default="",
                        help="Cron mode for triage: repeat on interval e.g. '6h', '30m', '3600'")
    parser.add_argument("--dedupe", action="store_true", help="conform: execute atomic hardlink deduplication")
    parser.add_argument("--dry-run", action="store_true", help="conform: simulate deduplication without linking")
    parser.add_argument("--min-size", type=int, default=1, help="conform: minimum file size in bytes for dedupe")
    parser.add_argument("--trim", action="store_true", help="pagekeeper: execute working set trim")
    parser.add_argument("--threshold", type=float, default=80.0, help="pagekeeper: RAM utilization pressure threshold pct")
    parser.add_argument("--json", action="store_true", help="output machine-readable JSON")

    args = parser.parse_args(argv)
    root = Path(args.path).resolve()

    if not root.exists():
        _print(f"❌ Path not found: {root}", "red")
        sys.exit(1)

    dispatch = {
        "scan":       cmd_scan,
        "index":      cmd_index,
        "ghost":      cmd_ghost,
        "vector":     cmd_vector,
        "triage":     cmd_triage,
        "status":     cmd_status,
        "graph":      cmd_graph,
        "conform":    cmd_conform,
        "pagekeeper": cmd_pagekeeper,
        "tokenpress": cmd_tokenpress,
    }

    if args.schedule and args.command == "triage":
        try:
            interval = _parse_schedule(args.schedule)
        except ValueError:
            _print(f"❌ Invalid --schedule '{args.schedule}' — use e.g. '6h', '30m', '3600'", "red")
            sys.exit(1)
        _print(f"\n⏰  Colony cron mode — interval={args.schedule} ({interval}s) path={root}", "bold")
        cycle = 0
        while True:
            cycle += 1
            _print(f"\n🔄  Cycle #{cycle}  [{time.strftime('%H:%M:%S')}]", "dim")
            try:
                stats = _cron_scan_and_inject(root, args.auto_approve)
                style = "yellow" if stats["critical_flags"] else "dim"
                _print(
                    f"  files={stats['files']}  risk={stats['risk_label']}({stats['risk_score']:.0f})"
                    f"  critical={stats['critical_flags']}  injected={stats['injected']}",
                    style,
                )
            except Exception as e:
                _print(f"  ⚠️   Scan error: {e}", "yellow")
            _print(f"  💤  Next scan in {args.schedule}…", "dim")
            time.sleep(interval)
    else:
        dispatch[args.command](root, args)


if __name__ == "__main__":
    main()
