"""OMC Team CLI Worker — Spawns parallel Foundry Knight engines in tmux panes.

Sir Boris uses this to orchestrate parallel task execution across:
- Claude Code (Sir Boris)   — tmux pane 0 (controller)
- Gemini CLI (Sir Helio)    — tmux pane 1
- OpenAI Codex (Sir Codex)  — tmux pane 2

Each pane runs in an isolated tmux window under session 'camelot-foundry'.
Boris can dispatch tasks, collect results, and terminate panes.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


TMUX_SESSION = "camelot-foundry"
CAMELOT_OS = Path.home() / "CAMELOT_OS"


@dataclass
class WorkerPane:
    """A tmux pane running a Foundry Knight engine."""
    knight_id: str
    engine_cmd: str
    pane_index: int
    pid: Optional[int] = None
    status: str = "idle"  # idle | running | completed | failed


@dataclass
class OMCTeam:
    """Orchestrates parallel Foundry Council execution via tmux panes.

    Usage:
        team = OMCTeam()
        team.spawn_session()
        team.dispatch("sir_helio", "analyze this 500K token codebase")
        team.dispatch("sir_codex", "generate the CRUD endpoints")
        results = team.collect_all(timeout=120)
        team.teardown()
    """

    session: str = TMUX_SESSION
    workers: dict[str, WorkerPane] = field(default_factory=dict)
    results_dir: Path = field(default_factory=lambda: CAMELOT_OS / "logs" / "omc_team")

    # Engine CLI commands per knight
    ENGINE_COMMANDS: dict[str, str] = field(default_factory=lambda: {
        "sir_boris": str(CAMELOT_OS / "claude-ollama.cmd"),
        "sir_helio": "gemini",
        "sir_codex": "codex",
    })

    def __post_init__(self):
        self.results_dir.mkdir(parents=True, exist_ok=True)
        if not shutil.which("tmux"):
            raise RuntimeError(
                "tmux not found. Install via: sudo apt install tmux (Linux) "
                "or brew install tmux (macOS). On Windows use WSL."
            )

    def spawn_session(self) -> bool:
        """Create the tmux session with panes for each engine."""
        # Kill existing session if stale
        subprocess.run(
            ["tmux", "kill-session", "-t", self.session],
            capture_output=True,
        )

        # Create new session (detached) — pane 0 is Boris (controller)
        result = subprocess.run(
            ["tmux", "new-session", "-d", "-s", self.session, "-n", "foundry"],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            return False

        self.workers["sir_boris"] = WorkerPane(
            knight_id="sir_boris",
            engine_cmd=self.ENGINE_COMMANDS["sir_boris"],
            pane_index=0,
            status="idle",
        )

        # Split panes for Helio and Codex
        pane_idx = 1
        for knight_id in ("sir_helio", "sir_codex"):
            cmd = self.ENGINE_COMMANDS.get(knight_id)
            if not cmd or not shutil.which(cmd):
                continue

            subprocess.run(
                ["tmux", "split-window", "-t", f"{self.session}:foundry", "-h"],
                capture_output=True,
            )
            self.workers[knight_id] = WorkerPane(
                knight_id=knight_id,
                engine_cmd=cmd,
                pane_index=pane_idx,
                status="idle",
            )
            pane_idx += 1

        # Tile panes evenly
        subprocess.run(
            ["tmux", "select-layout", "-t", f"{self.session}:foundry", "tiled"],
            capture_output=True,
        )

        return True

    def dispatch(self, knight_id: str, prompt: str, agent_prompt: str = "") -> bool:
        """Send a task to a specific knight's tmux pane.

        Args:
            knight_id: Target knight (sir_boris, sir_helio, sir_codex).
            prompt: The task prompt to execute.
            agent_prompt: Optional agent persona override.

        Returns:
            True if dispatch succeeded.
        """
        worker = self.workers.get(knight_id)
        if not worker:
            return False

        # Build engine-specific CLI command
        result_file = self.results_dir / f"{knight_id}_{int(time.time())}.json"
        engine_cmd = worker.engine_cmd

        if knight_id == "sir_boris":
            # Claude Code: omc ask claude --agent-prompt sir_boris --prompt "..."
            shell_cmd = (
                f'{engine_cmd} --print '
                f'"{prompt}" '
                f'2>&1 | tee {result_file}'
            )
        elif knight_id == "sir_helio":
            # Gemini CLI
            shell_cmd = (
                f'{engine_cmd} '
                f'"{prompt}" '
                f'2>&1 | tee {result_file}'
            )
        elif knight_id == "sir_codex":
            # OpenAI Codex
            shell_cmd = (
                f'{engine_cmd} '
                f'"{prompt}" '
                f'2>&1 | tee {result_file}'
            )
        else:
            return False

        # Send keys to the tmux pane
        target = f"{self.session}:foundry.{worker.pane_index}"
        subprocess.run(
            ["tmux", "send-keys", "-t", target, shell_cmd, "Enter"],
            capture_output=True,
        )
        worker.status = "running"
        return True

    def collect(self, knight_id: str) -> Optional[str]:
        """Read the latest result file from a knight's output."""
        pattern = f"{knight_id}_*.json"
        files = sorted(self.results_dir.glob(pattern), reverse=True)
        if not files:
            return None
        return files[0].read_text(encoding="utf-8", errors="replace")

    def collect_all(self, timeout: int = 120) -> dict[str, Optional[str]]:
        """Wait for all running workers and collect results.

        Args:
            timeout: Max seconds to wait per worker.

        Returns:
            Dict of knight_id -> output string (or None if timed out).
        """
        results: dict[str, Optional[str]] = {}
        for knight_id, worker in self.workers.items():
            if worker.status != "running":
                results[knight_id] = None
                continue

            # Poll for result file
            deadline = time.time() + timeout
            output = None
            while time.time() < deadline:
                output = self.collect(knight_id)
                if output and len(output) > 10:
                    break
                time.sleep(2)

            worker.status = "completed" if output else "failed"
            results[knight_id] = output

        return results

    def terminate(self, knight_id: str) -> bool:
        """Send Ctrl-C to a specific knight's pane."""
        worker = self.workers.get(knight_id)
        if not worker:
            return False
        target = f"{self.session}:foundry.{worker.pane_index}"
        subprocess.run(
            ["tmux", "send-keys", "-t", target, "C-c", ""],
            capture_output=True,
        )
        worker.status = "idle"
        return True

    def teardown(self) -> bool:
        """Kill the entire tmux session."""
        result = subprocess.run(
            ["tmux", "kill-session", "-t", self.session],
            capture_output=True,
        )
        self.workers.clear()
        return result.returncode == 0

    def status(self) -> dict[str, str]:
        """Return status of all worker panes."""
        return {k: w.status for k, w in self.workers.items()}
