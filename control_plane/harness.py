"""Sovereign Harness — 24/7 Agentic Daemon
CAMELOT Apex OS persistent background runtime.

Responsibilities:
  - Watchdog loop: probes 5 boot phases every 30s, auto-restarts dead services
  - Memory sync loop: Integration Brain sync_state to both tiers every 5min
  - Ledger loop: appends activity digest to PROVENANCE_LEDGER every 10min
  - Task queue: processes submitted tasks from logs/harness_queue.jsonl
  - Knight cells: spawn/apoptosis per cellular protocol (complexity>10, 7d idle, >5% error)
  - OpenClaw loop: dynamic health triage every 5min, auto-queues remediation tasks

Usage:
    python -m control_plane.harness            # run forever
    python -m control_plane.harness --status   # print status and exit
    python -m control_plane.harness --once     # run one cycle and exit

IPC:
    Append a JSON line to logs/harness_queue.jsonl to submit a task:
    {"id":"t1","knight":"sir_mnemo","directive":"synthesize X","priority":1}

PID file: logs/harness.pid
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── Paths ────────────────────────────────────────────────────────────────────

CAMELOT_HOME = Path(os.environ.get("CAMELOT_OS_HOME", Path.home() / "CAMELOT_OS")).resolve()
CONFIGS_DIR  = CAMELOT_HOME / "03_VAULT" / "training" / "configs"
LOGS_DIR     = CAMELOT_HOME / "logs"
PID_FILE     = LOGS_DIR / "harness.pid"
QUEUE_FILE   = LOGS_DIR / "harness_queue.jsonl"
LEDGER_FILE  = CAMELOT_HOME / "PROVENANCE_LEDGER.md"

# Ensure logs dir exists
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Add configs dir to path for knight imports
if str(CONFIGS_DIR) not in sys.path:
    sys.path.insert(0, str(CONFIGS_DIR))

# ── Intervals ────────────────────────────────────────────────────────────────

WATCHDOG_INTERVAL_S    = 30
MEMORY_SYNC_INTERVAL_S = 300   # 5 min
LEDGER_INTERVAL_S      = 600   # 10 min
TASK_POLL_INTERVAL_S   = 2
ARCHIVIST_INTERVAL_S   = 3600   # 1 hr — Lord Archivist GEP scan
GIDEON_INTERVAL_S      = 21600  # 6 hr — Sir Gideon //SCORPION pass
GIDEON_REPORT_FILE     = LOGS_DIR / "gideon_report.json"
TOON_V2_INTERVAL_S     = 21600  # 6 hr — TOON_v2 delta sync to Cloud Brain
WATCHDOG_RESTART_COOLDOWN_S = 60   # base cooldown; doubles on each consecutive failure (exp backoff)
WATCHDOG_RESTART_MAX_COOLDOWN_S = 600  # cap at 10 min per service

# Services the watchdog can auto-restart (soft, non-critical)
_SOFT_SERVICE_CMDS: dict[str, list] = {}  # populated lazily after HOME is resolved

# ── Boot phase probes (mirrors hud.py logic without Rich) ────────────────────

BOOT_PROBES: list[tuple[str, str, int]] = [
    ("CLIProxy",        "127.0.0.1", 8080),
    ("KineticEdge",     "127.0.0.1", 3001),
    ("Qdrant",          "127.0.0.1", 6333),   # overridden to cloud HTTPS when QDRANT_URL is set
    ("Saltare",         "127.0.0.1", 8085),
    ("Holotable",       "127.0.0.1", 3000),
    ("OmniVoice",       "127.0.0.1", 3002),
    ("KittenTTS",       "127.0.0.1", 8300),
    ("SirOctavian",     "127.0.0.1", 8400),
    ("Redis",           "127.0.0.1", 6379),
]


# ── Data classes ─────────────────────────────────────────────────────────────

@dataclass
class HarnessTask:
    id:        str
    knight:    str
    directive: str
    priority:  int   = 1   # lower = higher priority
    submitted: str   = field(default_factory=lambda: _utcnow())
    retries:   int   = 0


@dataclass
class KnightCell:
    knight_id:   str
    spawned_at:  float = field(default_factory=time.time)
    task_count:  int   = 0
    error_count: int   = 0
    last_active: float = field(default_factory=time.time)

    @property
    def error_rate(self) -> float:
        if self.task_count == 0:
            return 0.0
        return self.error_count / self.task_count

    @property
    def idle_days(self) -> float:
        return (time.time() - self.last_active) / 86400


@dataclass
class HarnessStatus:
    pid:        int
    uptime_s:   float
    tasks_done: int
    tasks_fail: int
    cells:      dict[str, dict]
    probes:     dict[str, bool]
    last_sync:  str
    last_ledger: str


# ── Helpers ──────────────────────────────────────────────────────────────────

def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


async def _probe_port(host: str, port: int, timeout: float = 1.5) -> bool:
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=timeout
        )
        writer.close()
        await writer.wait_closed()
        return True
    except Exception:
        return False


def _append_ledger(entry: str) -> None:
    try:
        with open(LEDGER_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n{entry}")
    except Exception:
        pass


# ── Sovereign Harness ────────────────────────────────────────────────────────

class SovereignHarness:
    def __init__(self):
        self._start     = time.time()
        self._running   = True
        self._cells:    dict[str, KnightCell] = {}
        self._done      = 0
        self._fail      = 0
        self._last_sync   = "never"
        self._last_ledger = "never"
        self._probe_cache: dict[str, bool] = {}
        self._restart_ts: dict[str, float] = {}    # service → last restart epoch
        self._restart_count: dict[str, int] = {}  # consecutive failures per service
        self._prev_dark: set[str] = set()         # dark set from previous watchdog tick

    # ── Watchdog ──────────────────────────────────────────────────────────────

    def _soft_service_cmd(self, name: str) -> list[str] | None:
        """Return the restart command for a soft service, or None if not restartable."""
        venv_py = CAMELOT_HOME / ".venv" / "Scripts" / "python.exe"
        py = str(venv_py) if venv_py.exists() else sys.executable
        qdrant_exe = Path.home() / "bin" / "qdrant.exe"
        qdrant_cfg = CAMELOT_HOME / "data" / "qdrant" / "config.yaml"
        saltare_exe = CAMELOT_HOME / "kinetic_edge" / "saltare" / "saltare_gateway.exe"
        saltare_cfg = CAMELOT_HOME / "01_KERNEL" / "EXCALIBUR" / "config" / "saltare.toml"
        js = CAMELOT_HOME / "02_FORGE" / "KINETIC_ARMORY" / "omnivoice-router" / "omnivoice-router.js"
        runner = LOGS_DIR / "_kitten_runner.py"
        oct_py = CAMELOT_HOME / "control_plane" / "sir_octavian.py"
        cmds = {
            "Qdrant":     [str(qdrant_exe), "--config-path", str(qdrant_cfg)]
                if qdrant_exe.exists() and qdrant_cfg.exists() else None,
            "Saltare":    [str(saltare_exe), "--config", str(saltare_cfg), "mcp", "http", "--port", "8085"]
                if saltare_exe.exists() and saltare_cfg.exists() else None,
            "OmniVoice":   ["node", str(js)] if js.exists() else None,
            "KittenTTS":   [py, str(runner)] if runner.exists() else None,
            "SirOctavian": [py, str(oct_py), "--serve"] if oct_py.exists() else None,
            "Redis":        (["redis-server.exe"] if Path(r"C:\Program Files\Redis\redis-server.exe").exists()
                             else (["redis-server"] if shutil.which("redis-server") else
                                   (["sc", "start", "Redis"] if sys.platform == "win32" else None))),
        }
        return cmds.get(name)

    async def _restart_soft_service(self, name: str) -> None:
        cmd = self._soft_service_cmd(name)
        if not cmd:
            _log(f"[WATCHDOG] No restart command for {name}")
            return
        try:
            import platform as _pl
            kwargs: dict = {"cwd": str(CAMELOT_HOME)}
            if _pl.system() == "Windows":
                kwargs["creationflags"] = (
                    getattr(subprocess, "DETACHED_PROCESS", 0x08)
                    | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x200)
                )
                kwargs["close_fds"] = True
            else:
                kwargs["start_new_session"] = True
            out = LOGS_DIR / f"{name.lower()}_restart.log"
            with out.open("ab") as fh:
                kwargs["stdout"] = fh
                kwargs["stderr"] = fh
                proc = subprocess.Popen(cmd, **kwargs)  # fh open while Popen duplicates handle
            self._restart_count[name] = 0  # reset backoff on successful launch
            _log(f"[WATCHDOG] RESTART {name} PID={proc.pid}")
        except Exception as e:
            self._restart_count[name] = self._restart_count.get(name, 0) + 1
            _log(f"[WATCHDOG] RESTART {name} FAILED (attempt {self._restart_count[name]}): {e}")

    def _cooldown_for(self, name: str) -> float:
        """Exponential backoff: base * 2^failures, capped at max."""
        failures = self._restart_count.get(name, 0)
        return min(WATCHDOG_RESTART_COOLDOWN_S * (2 ** failures), WATCHDOG_RESTART_MAX_COOLDOWN_S)

    async def _watchdog_loop(self) -> None:
        while self._running:
            results = await asyncio.gather(*[
                _probe_port(host, port)
                for _, host, port in BOOT_PROBES
            ])
            self._probe_cache = {
                name: ok for (name, _, _), ok in zip(BOOT_PROBES, results)
            }
            dark = {n for n, ok in self._probe_cache.items() if not ok}

            # Log recoveries (was dark last tick, now green)
            recovered = self._prev_dark - dark
            for name in recovered:
                self._restart_count[name] = 0
                _log(f"[WATCHDOG] RECOVERED: {name} is GREEN")

            if dark:
                _log(f"[WATCHDOG] DARK: {', '.join(sorted(dark))}")
                now = time.time()
                for name in dark:
                    cooldown = self._cooldown_for(name)
                    if now - self._restart_ts.get(name, 0) >= cooldown:
                        self._restart_ts[name] = now
                        asyncio.create_task(self._restart_soft_service(name))
            else:
                _log("[WATCHDOG] All probes green")

            self._prev_dark = dark
            await asyncio.sleep(WATCHDOG_INTERVAL_S)

    # ── Memory sync ───────────────────────────────────────────────────────────

    async def _memory_sync_loop(self) -> None:
        await asyncio.sleep(10)   # let boot settle
        while self._running:
            try:
                from integration_brain import async_store
                result = await async_store(
                    title="Harness Heartbeat Sync",
                    content=self._build_sync_content(),
                    tier="both",
                )
                self._last_sync = _utcnow()
                lt_status = result.get("long_term", {})
                st_status = result.get("short_term", {})
                if not isinstance(st_status, dict):
                    st_status = {"action": str(st_status)[:120]}
                if not isinstance(lt_status, dict):
                    lt_status = {"status": str(lt_status)[:120]}
                _log(f"[MEMORY_SYNC] ST={st_status.get('action','?')} LT={lt_status.get('status','?')}")
            except Exception as e:
                _log(f"[MEMORY_SYNC] ERROR: {type(e).__name__}: {e}")
            await asyncio.sleep(MEMORY_SYNC_INTERVAL_S)

    def _build_sync_content(self) -> str:
        uptime = round(time.time() - self._start)
        probe_lines = "\n".join(
            f"  {n}: {'✅' if ok else '⬛'}"
            for n, ok in self._probe_cache.items()
        )
        cell_lines = "\n".join(
            f"  {cid}: tasks={c.task_count} errors={c.error_count} idle={c.idle_days:.1f}d"
            for cid, c in self._cells.items()
        )
        return (
            f"# Sovereign Harness Sync — {_utcnow()}\n"
            f"uptime: {uptime}s | done: {self._done} | fail: {self._fail}\n\n"
            f"## Boot Probes\n{probe_lines or '  (none yet)'}\n\n"
            f"## Knight Cells\n{cell_lines or '  (none active)'}\n"
        )

    # ── Ledger loop ───────────────────────────────────────────────────────────

    async def _ledger_loop(self) -> None:
        await asyncio.sleep(60)   # first entry after 1min
        entry_num = 900           # harness ledger entries start at 900
        while self._running:
            uptime = round(time.time() - self._start)
            probes_green = sum(self._probe_cache.values())
            probes_total = len(BOOT_PROBES)
            entry = (
                f"| {entry_num} | **Harness Heartbeat** | SovereignHarness | "
                f"⚡ LIVE | uptime={uptime}s tasks={self._done} fail={self._fail} "
                f"probes={probes_green}/{probes_total} cells={len(self._cells)} |"
            )
            _append_ledger(entry)
            self._last_ledger = _utcnow()
            entry_num += 1
            await asyncio.sleep(LEDGER_INTERVAL_S)

    # ── Lord Archivist GEP scan ───────────────────────────────────────────────

    async def _archivist_loop(self) -> None:
        """Loop 6 — GEP scan every 1hr. Writes learnings.md, XP, skill gaps."""
        await asyncio.sleep(120)  # let system settle before first scan
        while self._running:
            try:
                try:
                    from .lord_archivist import run_gep_scan
                except ImportError:
                    from control_plane.lord_archivist import run_gep_scan
                report = run_gep_scan()
                gaps = len(report.skill_gaps)
                patterns = len(report.fail_patterns)
                xp_count = len(report.xp_entries)
                _log(
                    f"[LORD_ARCHIVIST] GEP scan done — "
                    f"skills={len(report.skill_audits)} gaps={gaps} "
                    f"patterns={patterns} xp={xp_count} ({report.duration_ms:.0f}ms)"
                )
                if gaps:
                    _log(f"[LORD_ARCHIVIST] SKILL_GAPS: {report.skill_gaps}")
                if patterns:
                    _log(f"[LORD_ARCHIVIST] FAIL_PATTERNS: {[p.error_type for p in report.fail_patterns]}")
            except Exception as e:
                _log(f"[LORD_ARCHIVIST] GEP scan error: {type(e).__name__}: {e}")
            await asyncio.sleep(ARCHIVIST_INTERVAL_S)

    # ── Sir Gideon //SCORPION loop ────────────────────────────────────────────

    async def _gideon_loop(self) -> None:
        """Loop 7 — SCORPION Shatterpoint audit every 6h. Writes gideon_report.json."""
        await asyncio.sleep(300)  # 5 min after boot — let P0-P3 fully settle
        while self._running:
            try:
                from knights.sir_gideon import run_scorpion
                report = run_scorpion()
                _log(
                    f"[SIR_GIDEON] //SCORPION — score={report.gideon_risk_score} "
                    f"pass={report.passed} ({report.duration_ms:.0f}ms)"
                )
                if not report.passed:
                    criticals = [r.shatterpoint for r in report.shatterpoints if r.status == "CRITICAL"]
                    _log(f"[SIR_GIDEON] ALERT — CRITICAL: {criticals} — Iron Gate HITL required")
                # Write JSON report for HUD / external consumers
                report_data = {
                    "timestamp": _utcnow(),
                    "gideon_risk_score": report.gideon_risk_score,
                    "passed": report.passed,
                    "summary": report.summary,
                    "shatterpoints": [
                        {
                            "sp": r.shatterpoint,
                            "status": r.status,
                            "weight": r.weight,
                            "evidence_count": len(r.evidence),
                        }
                        for r in report.shatterpoints
                    ],
                }
                GIDEON_REPORT_FILE.write_text(
                    json.dumps(report_data, indent=2), encoding="utf-8"
                )
            except Exception as e:
                _log(f"[SIR_GIDEON] SCORPION error: {type(e).__name__}: {e}")
            await asyncio.sleep(GIDEON_INTERVAL_S)

    # ── OpenClaw health triage ────────────────────────────────────────────────

    async def _openclaw_loop(self) -> None:
        """Loop 9 — dynamic health triage every 5min. Auto-queues remediations."""
        await asyncio.sleep(180)
        while self._running:
            try:
                try:
                    from .openclaw import run_openclaw_triage
                except ImportError:
                    from control_plane.openclaw import run_openclaw_triage
                report = run_openclaw_triage(probe_cache=self._probe_cache)
                _log(
                    f"[OPENCLAW] {report['status']} — "
                    f"{report['checks_ok']}/{report['checks_total']} OK "
                    f"| auto_healed={report['auto_healed']}"
                    + (f" | CRITICAL: {report['critical_items']}" if report.get("critical_items") else "")
                )
                if report.get("hitl_required"):
                    _log("[OPENCLAW] HITL REQUIRED — see logs/openclaw_hitl_required.md")
            except Exception as e:
                _log(f"[OPENCLAW] error: {type(e).__name__}: {e}")
            await asyncio.sleep(300)

    # ── TOON_v2 delta cron ────────────────────────────────────────────────────

    async def _toon_v2_loop(self) -> None:
        """Loop 8 — push ledger delta to Cloud Brain every 6h."""
        await asyncio.sleep(900)  # 15 min after boot — let Cloud Brain auth settle
        toon_py = CAMELOT_HOME / "scripts" / "toon_v2_delta.py"
        while self._running:
            if toon_py.exists():
                try:
                    env = {**os.environ, "CAMELOT_OS_HOME": str(CAMELOT_HOME)}
                    proc = await asyncio.create_subprocess_exec(
                        sys.executable, str(toon_py),
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        env=env,
                    )
                    _, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)
                    if proc.returncode == 0:
                        _log(f"[TOON_V2] Delta sync OK (exit=0)")
                    else:
                        err = (stderr or b"").decode(errors="replace").strip()[-200:]
                        _log(f"[TOON_V2] Delta sync exit={proc.returncode}: {err}")
                except asyncio.TimeoutError:
                    _log("[TOON_V2] Delta sync timed out after 120s")
                except Exception as e:
                    _log(f"[TOON_V2] Delta sync error: {type(e).__name__}: {e}")
            else:
                _log("[TOON_V2] toon_v2_delta.py not found — skipping")
            await asyncio.sleep(TOON_V2_INTERVAL_S)

    # ── Switchboard monitor ───────────────────────────────────────────────────

    async def _switchboard_loop(self) -> None:
        """Probe all terminals every 60s. Flag dark terminals. Suggest reroutes."""
        await asyncio.sleep(15)   # let boot settle
        while self._running:
            try:
                try:
                    from .switchboard import probe_all, summary
                except ImportError:
                    from control_plane.switchboard import probe_all, summary
                await probe_all()
                s = summary()
                dark = [k for k, v in s.items() if v == "dark"]
                live = sum(1 for v in s.values() if v in ("live", "assumed_live"))
                _log(f"[SWITCHBOARD] {live}/{len(s)} live" + (f" | DARK: {dark}" if dark else ""))
                if len(dark) >= 2:
                    _log(f"[WATCHDOG] ALERT: {len(dark)} terminals dark — escalating to SIR_BORIS")
            except Exception as e:
                _log(f"[SWITCHBOARD] probe error: {type(e).__name__}: {e}")
            await asyncio.sleep(60)

    # ── Task queue ────────────────────────────────────────────────────────────

    async def _task_loop(self) -> None:
        processed: set[str] = self._queue_ids()
        while self._running:
            tasks = self._read_queue(processed)
            for task in sorted(tasks, key=lambda t: t.priority):
                asyncio.create_task(self._dispatch(task))
                processed.add(task.id)
            await asyncio.sleep(TASK_POLL_INTERVAL_S)

    def _queue_ids(self) -> set[str]:
        ids: set[str] = set()
        if not QUEUE_FILE.exists():
            return ids
        try:
            lines = QUEUE_FILE.read_text(encoding="utf-8").splitlines()
        except Exception:
            return ids
        for line in lines:
            try:
                data = json.loads(line.strip())
                tid = data.get("id")
                if tid:
                    ids.add(str(tid))
            except Exception:
                pass
        return ids

    def _read_queue(self, processed: set[str]) -> list[HarnessTask]:
        tasks: list[HarnessTask] = []
        if not QUEUE_FILE.exists():
            return tasks
        try:
            lines = QUEUE_FILE.read_text(encoding="utf-8").splitlines()
        except Exception:
            return tasks
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                tid = data.get("id", "")
                if tid and tid not in processed:
                    tasks.append(HarnessTask(**{k: data[k] for k in HarnessTask.__dataclass_fields__ if k in data}))
            except Exception:
                pass
        return tasks

    async def _dispatch(self, task: HarnessTask) -> None:
        cell = self._cells.setdefault(task.knight, KnightCell(knight_id=task.knight))
        cell.task_count += 1
        cell.last_active = time.time()
        _log(f"[DISPATCH] {task.knight} ← {task.directive[:60]}")
        try:
            result = await self._run_knight(task)
            self._done += 1
            _log(f"[DONE] {task.id} → {str(result)[:80]}")
        except Exception as e:
            self._fail += 1
            cell.error_count += 1
            _log(f"[FAIL] {task.id} {type(e).__name__}: {e}")
            # Cellular apoptosis: >5% error rate
            if cell.error_rate > 0.05 and cell.task_count >= 10:
                _log(f"[APOPTOSIS] {task.knight} error_rate={cell.error_rate:.1%} — cell pruned")
                del self._cells[task.knight]

    async def _run_knight(self, task: HarnessTask) -> Any:
        knight_id = task.knight.lower().replace("sir_", "").replace("-", "_")

        # SIR_MNEMO — memory routing
        if knight_id == "mnemo":
            from knights.mnemo import route_query
            route = route_query(task.directive)
            return {"tier": route.tier, "reasons": route.score.reasons}

        # Integration Brain synthesis
        if knight_id in ("integration_brain", "cloud_brain", "lady_apis"):
            from integration_brain import async_synthesize
            return await async_synthesize(task.directive)

        # Lord Archivist — GEP scan on demand
        if knight_id in ("lord_archivist", "archivist"):
            try:
                from .lord_archivist import run_gep_scan
            except ImportError:
                from control_plane.lord_archivist import run_gep_scan
            report = run_gep_scan()
            return {"gaps": report.skill_gaps, "patterns": len(report.fail_patterns), "xp": len(report.xp_entries)}

        # Sir Gideon — //SCORPION forensic audit
        if knight_id in ("sir_gideon", "gideon") or task.directive.startswith("//SCORPION"):
            from knights.sir_gideon import SirGideon
            return SirGideon().execute(task.directive)

        # Contract build — compile and smoke-test the portable Camelot runtime.
        if task.directive.upper().startswith("//CONTRACT"):
            script = CAMELOT_HOME / "scripts" / "build_portable.py"
            if not script.exists():
                return {"status": "failed", "error": f"missing build script: {script}"}
            env = os.environ.copy()
            env.setdefault("PYTHONIOENCODING", "utf-8")
            proc = await asyncio.to_thread(
                subprocess.run,
                [sys.executable, str(script), "--test"],
                cwd=str(CAMELOT_HOME),
                env=env,
                capture_output=True,
                text=True,
                timeout=180,
            )
            output = (proc.stdout or "") + (proc.stderr or "")
            return {
                "status": "built" if proc.returncode == 0 else "failed",
                "returncode": proc.returncode,
                "binary": str(CAMELOT_HOME / "dist" / "camelot.exe"),
                "summary": output[-500:],
            }

        # Cybertron Dawning - OS map audit, Lady M sync, and project isolation.
        if task.directive.upper().startswith("//DAWNING"):
            if knight_id != "forge":
                return {
                    "rune": "//DAWNING",
                    "status": "accepted_no_requeue",
                    "reason": f"routed to {task.knight}; direct dawning execution skipped",
                }
            script = CAMELOT_HOME / "scripts" / "cybertron_dawning.py"
            if not script.exists():
                return {"status": "failed", "error": f"missing dawning script: {script}"}
            try:
                from .runic_router import parse_rune
            except ImportError:
                from control_plane.runic_router import parse_rune
            parsed = parse_rune(task.directive)
            project_name = parsed[1] if parsed else "default_nexus"
            env = os.environ.copy()
            env.setdefault("PYTHONIOENCODING", "utf-8")
            proc = await asyncio.to_thread(
                subprocess.run,
                [sys.executable, str(script), project_name or "default_nexus"],
                cwd=str(CAMELOT_HOME),
                env=env,
                capture_output=True,
                text=True,
                timeout=120,
            )
            output = (proc.stdout or "") + (proc.stderr or "")
            return {
                "status": "dawning_complete" if proc.returncode == 0 else "failed",
                "returncode": proc.returncode,
                "project": project_name or "default_nexus",
                "state": str(CAMELOT_HOME / "03_VAULT" / "runtime_state" / "cybertron_dawning_latest.json"),
                "summary": output[-800:],
            }

        # Runic command dispatch
        if task.directive.startswith("//") or task.directive.startswith("Omega_"):
            try:
                from .runic_router import parse_rune
            except ImportError:
                from control_plane.runic_router import parse_rune
            parsed = parse_rune(task.directive)
            if parsed:
                rune, param = parsed
                return {"rune": rune, "param": param, "status": "accepted_no_requeue"}

        # Generic — log and return
        return {"status": "dispatched", "knight": task.knight, "directive": task.directive}

    # ── Status ───────────────────────────────────────────────────────────────

    def status(self) -> HarnessStatus:
        return HarnessStatus(
            pid=os.getpid(),
            uptime_s=round(time.time() - self._start, 1),
            tasks_done=self._done,
            tasks_fail=self._fail,
            cells={cid: asdict(c) for cid, c in self._cells.items()},
            probes=dict(self._probe_cache),
            last_sync=self._last_sync,
            last_ledger=self._last_ledger,
        )

    # ── Main run ─────────────────────────────────────────────────────────────

    async def run(self, once: bool = False) -> None:
        _log(f"[HARNESS] Sovereign Harness online PID={os.getpid()}")
        PID_FILE.write_text(str(os.getpid()), encoding="utf-8")

        if once:
            await asyncio.gather(self._watchdog_loop.__wrapped__(self) if hasattr(self._watchdog_loop, '__wrapped__') else asyncio.sleep(0))
            # single watchdog cycle
            results = await asyncio.gather(*[_probe_port(h, p) for _, h, p in BOOT_PROBES])
            self._probe_cache = {n: ok for (n, _, _), ok in zip(BOOT_PROBES, results)}
            print(json.dumps(asdict(self.status()), indent=2))
            return

        loops = [
            self._watchdog_loop(),
            self._memory_sync_loop(),
            self._ledger_loop(),
            self._task_loop(),
            self._switchboard_loop(),
            self._archivist_loop(),
            self._gideon_loop(),
            self._toon_v2_loop(),
            self._openclaw_loop(),
        ]

        def _shutdown(sig, frame):
            _log(f"[HARNESS] Signal {sig} received — shutting down")
            self._running = False
            try:
                PID_FILE.unlink(missing_ok=True)
            except Exception:
                pass

        signal.signal(signal.SIGINT,  _shutdown)
        signal.signal(signal.SIGTERM, _shutdown)

        await asyncio.gather(*loops, return_exceptions=True)
        PID_FILE.unlink(missing_ok=True)
        _log("[HARNESS] Sovereign Harness offline")


# ── Logging ──────────────────────────────────────────────────────────────────

_LOG_MAX_BYTES = 10 * 1024 * 1024   # 10 MB per file
_LOG_BACKUP_COUNT = 3               # keep harness.log.1 / .2 / .3


def _rotate_log(log_path: Path) -> None:
    """Roll harness.log → .1 → .2 → .3, drop .3 if present."""
    for i in range(_LOG_BACKUP_COUNT, 0, -1):
        src = log_path.with_suffix(f".log.{i - 1}") if i > 1 else log_path
        dst = log_path.with_name(log_path.name + f".{i}")
        if src.exists():
            src.replace(dst)


def _log(msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        log_path = LOGS_DIR / "harness.log"
        if log_path.exists() and log_path.stat().st_size >= _LOG_MAX_BYTES:
            _rotate_log(log_path)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


# ── hud.py boot hook ─────────────────────────────────────────────────────────

def boot_harness(home: Path | None = None) -> tuple[bool, str]:
    """Called by awaken Phase 6. Spawns harness as detached background process."""
    import subprocess, platform
    home = home or CAMELOT_HOME
    script = home / "control_plane" / "harness.py"
    if not script.exists():
        return False, "harness.py not found"

    # Check if already running
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            os.kill(pid, 0)  # check alive
            return True, f"Sovereign Harness already running PID={pid}"
        except (ProcessLookupError, ValueError):
            PID_FILE.unlink(missing_ok=True)

    py = sys.executable
    kwargs: dict = {"cwd": str(home)}
    if platform.system() == "Windows":
        kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE
    else:
        kwargs["start_new_session"] = True

    proc = subprocess.Popen([py, str(script)], **kwargs)
    time.sleep(1.0)
    if proc.poll() is not None:
        return False, f"Harness exited immediately (code {proc.returncode})"
    return True, f"Sovereign Harness spawned PID={proc.pid}"


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(prog="harness", description="CAMELOT Sovereign Harness")
    ap.add_argument("--status", action="store_true", help="Print status JSON and exit")
    ap.add_argument("--once",   action="store_true", help="Run one watchdog cycle and exit")
    args = ap.parse_args()

    harness = SovereignHarness()

    if args.status:
        if PID_FILE.exists():
            try:
                pid = int(PID_FILE.read_text().strip())
                print(json.dumps({"running": True, "pid": pid}))
            except Exception:
                print(json.dumps({"running": False}))
        else:
            print(json.dumps({"running": False}))
        return

    asyncio.run(harness.run(once=args.once))


if __name__ == "__main__":
    main()
