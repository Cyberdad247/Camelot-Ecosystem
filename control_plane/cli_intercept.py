"""CLI Intercept — Bridges camelot-cli to the MFOE Soul Router.

Every camelot-cli command passes through this intercept layer which:
1. Parses the intent from the command string
2. Scores it through the Soul Equation (S_omega = alpha*V + beta*M + gamma*P + delta*E)
3. Routes to the optimal Foundry Knight / engine
4. Dispatches execution to the appropriate backend (CLIProxyAPI, Ollama, or direct)

Usage:
    from control_plane.cli_intercept import CLIIntercept
    intercept = CLIIntercept()
    result = intercept.process("critique this architecture")
"""

from __future__ import annotations

import json
import os
import re
import sys
import asyncio
import argparse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from .soul_router import SoulRouter, RouteDecision, PRIVACY_KEYWORDS
from .main import ControlPlane, TaskPayload


CAMELOT_OS = Path(os.environ.get("CAMELOT_OS", Path.home() / "CAMELOT_OS"))
OMNIROUTE_CONFIG = CAMELOT_OS / "03_VAULT" / "training" / "configs" / "config" / "omniroute.json"


# ---------------------------------------------------------------------------
# Complexity Estimator
# ---------------------------------------------------------------------------

# Keywords that indicate high complexity (magnitude >= 0.7)
_HIGH_COMPLEXITY = frozenset({
    "architecture", "refactor", "migrate", "redesign", "multi-agent",
    "microservice", "deploy", "infrastructure", "pipeline", "orchestrat",
})

# Keywords that indicate low complexity (magnitude <= 0.3)
_LOW_COMPLEXITY = frozenset({
    "list", "status", "help", "version", "check", "show", "describe",
    "hello", "hi", "info",
})

# Keywords that indicate urgency (velocity >= 0.8)
_URGENT = frozenset({
    "hotfix", "urgent", "critical", "emergency", "fix now", "asap",
    "production", "p0", "incident",
})


def estimate_complexity(intent: str) -> float:
    """Estimate complexity score [0.0-1.0] from intent keywords."""
    lower = intent.lower()
    if any(kw in lower for kw in _HIGH_COMPLEXITY):
        return 0.8
    if any(kw in lower for kw in _LOW_COMPLEXITY):
        return 0.2
    # Word count heuristic: longer prompts tend to be more complex
    word_count = len(lower.split())
    if word_count > 50:
        return 0.7
    if word_count > 20:
        return 0.5
    return 0.4


def estimate_velocity(intent: str) -> float:
    """Estimate urgency score [0.0-1.0] from intent keywords."""
    lower = intent.lower()
    if any(kw in lower for kw in _URGENT):
        return 0.9
    return 0.5


def estimate_privacy(intent: str) -> float:
    """Estimate privacy score [0.0-1.0] from intent keywords."""
    lower = intent.lower()
    if any(kw in lower for kw in PRIVACY_KEYWORDS):
        return 0.95
    return 0.0


# ---------------------------------------------------------------------------
# Dispatch Result
# ---------------------------------------------------------------------------

@dataclass
class DispatchResult:
    """Result of intercepting and routing a CLI command."""
    route: RouteDecision
    engine_cmd: str
    model: str
    backend_url: str
    force_plan_mode: bool = False
    intercepted: bool = True


# ---------------------------------------------------------------------------
# CLI Intercept
# ---------------------------------------------------------------------------

class CLIIntercept:
    """Intercept layer between camelot-cli and the Foundry Council engines."""

    def __init__(self):
        self.router = SoulRouter()
        self._omniroute = self._load_omniroute()

    def _load_omniroute(self) -> dict:
        """Load omniroute.json for engine execution paths."""
        if OMNIROUTE_CONFIG.exists():
            return json.loads(OMNIROUTE_CONFIG.read_text(encoding="utf-8"))
        return {}

    def intercept(self, intent: str) -> DispatchResult:
        """Intercept a CLI command and route through the Soul Equation.

        Args:
            intent: Raw command/prompt string from camelot-cli.

        Returns:
            DispatchResult with the selected engine, model, and backend URL.
        """
        # Score the intent
        velocity = estimate_velocity(intent)
        magnitude = estimate_complexity(intent)
        privacy = estimate_privacy(intent)

        # Route through MFOE matrix
        decision = self.router.route(
            intent,
            velocity=velocity,
            magnitude=magnitude,
            privacy=privacy,
        )

        # Map decision to engine execution details
        engine_cmd, model, backend_url = self._resolve_engine(decision)

        # Check if complexity spike forces plan mode
        force_plan = magnitude >= 0.8

        return DispatchResult(
            route=decision,
            engine_cmd=engine_cmd,
            model=model,
            backend_url=backend_url,
            force_plan_mode=force_plan,
        )

    def _resolve_engine(self, decision: RouteDecision) -> tuple[str, str, str]:
        """Resolve a RouteDecision to concrete engine CLI command, model, and URL."""
        engines = self._omniroute.get("engines", {})
        upstream = self._omniroute.get("upstream", {})

        knight = decision.knight_id
        engine_name = decision.engine

        # Local engines (Open Coder / Sir Ghost) -> Ollama
        if engine_name in ("open_coder", "local_qwen"):
            engine_cfg = engines.get(engine_name, engines.get("open_coder", {}))
            model = engine_cfg.get("model", "qwen3:1.7b")
            host = engine_cfg.get("execution_path", "localhost:11434")
            url = f"http://{host}"
            return ("ollama", model, url)

        # Cloud engines -> CLIProxyAPI
        cliproxy = upstream.get("cliproxy", {})
        base_url = cliproxy.get("base_url", "http://127.0.0.1:8080/v1")

        if engine_name == "claude_code":
            return ("claude", "claude-opus-4-6", base_url)
        elif engine_name == "gemini_cli":
            return ("gemini", "gemini-2.5-pro", base_url)
        elif engine_name == "openai_codex":
            return ("codex", "gpt-5.3-codex", base_url)
        elif engine_name == "open_source":
            return ("ollama", "qwen3:8b", "http://127.0.0.1:11434")

        # Fallback
        return ("claude", "claude-sonnet-4-6", base_url)

    def format_route_log(self, result: DispatchResult) -> str:
        """Format a human-readable route log line."""
        r = result.route
        lines = [
            f"[INTERCEPT] {r.knight_id} via {result.engine_cmd}",
            f"  Model: {result.model} @ {result.backend_url}",
            f"  Score: S_omega={r.score:.4f} (W={r.weight})",
            f"  Tensor: V={r.tensor.velocity} M={r.tensor.magnitude} P={r.tensor.privacy}",
            f"  Reason: {r.reason}",
        ]
        if result.force_plan_mode:
            lines.append("  [GATE] COMPLEXITY_SPIKE: Plan Mode enforced before execution")
        if r.privacy_override:
            lines.append("  [SHIELD] PRIVACY_OVERRIDE: Routed to air-gapped local engine")
        return "\n".join(lines)


async def _run_cloudbrain_action(args: argparse.Namespace) -> dict[str, Any]:
    cp = ControlPlane()
    if args.cloudbrain_command == "status":
        task = TaskPayload(intent="cloudbrain status", constraints=[])
        return (await cp.process_task(task)).model_dump()
    if args.cloudbrain_command == "sync":
        task = TaskPayload(
            intent="cloud brain sync",
            parameters={
                "notebook_id": args.notebook_id,
                "note_title": args.note_title,
                "extra_summary": args.summary,
            },
            constraints=[],
        )
        return (await cp.process_task(task)).model_dump()
    if args.cloudbrain_command == "memory":
        task = TaskPayload(
            intent="memory recall",
            parameters={"agent_id": args.agent_id},
            constraints=[f"privacy={args.privacy}"],
        )
        return (await cp.process_task(task)).model_dump()
    if args.cloudbrain_command == "research":
        task = TaskPayload(
            intent="research investigate objective",
            parameters={
                "objective": args.objective,
                "agent_id": args.agent_id,
                "constraints": list(args.constraint or []),
            },
            constraints=[f"privacy={args.privacy}", *(args.constraint or [])],
        )
        return (await cp.process_task(task)).model_dump()
    raise ValueError(f"Unsupported cloudbrain command: {args.cloudbrain_command}")


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Camelot canonical CLI intercept")
    sub = parser.add_subparsers(dest="command")

    route_parser = sub.add_parser("route", help="Route an intent through the Soul Router")
    route_parser.add_argument("intent", nargs="+")

    cloudbrain = sub.add_parser("cloudbrain", help="Invoke cloudbrain and research actions")
    cloudbrain_sub = cloudbrain.add_subparsers(dest="cloudbrain_command", required=True)

    cloudbrain_sub.add_parser("status", help="Show cloudbrain status")
    sync = cloudbrain_sub.add_parser("sync", help="Sync local Camelot state into the canonical Cloud Brain notebook")
    sync.add_argument("--notebook-id", default="")
    sync.add_argument("--note-title", default="")
    sync.add_argument("--summary", default="")

    memory = cloudbrain_sub.add_parser("memory", help="Recall cloudbrain memory")
    memory.add_argument("--agent-id", default="merlin")
    memory.add_argument("--privacy", type=float, default=0.0)

    research = cloudbrain_sub.add_parser("research", help="Invoke the research agency")
    research.add_argument("objective")
    research.add_argument("--agent-id", default="lady_apis")
    research.add_argument("--privacy", type=float, default=0.0)
    research.add_argument("--constraint", action="append")

    return parser


def main() -> int:
    parser = _build_arg_parser()
    args = parser.parse_args()

    if args.command == "route":
        intercept = CLIIntercept()
        result = intercept.intercept(" ".join(args.intent))
        print(intercept.format_route_log(result))
        return 0

    if args.command == "cloudbrain":
        print(json.dumps(asyncio.run(_run_cloudbrain_action(args)), indent=2))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
