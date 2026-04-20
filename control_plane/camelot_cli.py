"""User-facing Camelot-OS CLI modeled after prompt-first AI CLIs."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
import time
from typing import Any

from colorama import Fore, Style, just_fix_windows_console

from .cli_intercept import CLIIntercept
from .cloudbrain_sync import sync_after_event
from .config_manager import ConfigManager, OperatorProfile
from .provenance import ProvenanceManager, VerificationRun
from .ledger_sync import append_provenance_entry, ledger_status, sync_to_kernel
from .main import ControlPlane, TaskPayload


just_fix_windows_console()


STREAM_DELAY = float(os.getenv("CAMELOT_OS_STREAM_DELAY", "0.004"))
PROGRESS_DELAY = float(os.getenv("CAMELOT_OS_PROGRESS_DELAY", "0.12"))


# ---------------------------------------------------------------------------
# Anya's Ethereal Compiler (Phase 1 Upgrade)
# ---------------------------------------------------------------------------

class AnyaCompiler:
    """Ethereal Compiler (Layer 7) implementing Triple-QFT Protocol."""

    def __init__(self):
        self.anchor_tokens = {
            "build", "refactor", "create", "deploy", "audit", "fix", 
            "scaffold", "status", "sync", "research", "blueprint", "precise"
        }

    def renormalize(self, intent: str) -> str:
        """Strip conversational noise and irrelevant operators (Phase: Physics)."""
        fillers = {
            "please", "can you", "i need to", "help me", "i want to", 
            "would like to", "could you", "make sure to"
        }
        clean = intent.lower()
        for filler in fillers:
            clean = clean.replace(filler, "")
        
        # Remove extra punctuation and whitespace
        clean = re.sub(r'[^\w\s]', '', clean)
        return " ".join(clean.split())

    def quantize(self, intent: str) -> list[str]:
        """Identify Anchor Tokens for context compression (Phase: Engineering)."""
        words = set(intent.lower().split())
        found = words.intersection(self.anchor_tokens)
        return sorted(list(found))

    def pedagogy(self, intent: str) -> bool:
        """Check if the intent is ambiguous and needs clarification (Phase: Pedagogy)."""
        clean = self.renormalize(intent)
        words = clean.split()
        # Heuristic: < 2 words is usually ambiguous for a system command
        if len(words) < 2 and not any(w in self.anchor_tokens for w in words):
            return True
        return False

    def compile(self, raw_intent: str) -> tuple[str, float]:
        """Compile raw intent and return Titan Prompt + Confidence Scalar."""
        clean = self.renormalize(raw_intent)
        anchors = self.quantize(clean)
        
        # Calculate confidence scalar based on anchor presence
        score = 1.0 if anchors else 0.5
        if len(clean.split()) < 3 and not anchors:
            score = 0.3
            
        if not anchors:
            return clean, score
            
        # Format as a high-density Titan Prompt glyph
        prompt = f"⌖ Titan_Prompt | Intent: {clean} | ⌘ Anchors: {', '.join(anchors)}"
        return prompt, score


def _color(text: str, tone: str) -> str:
    palette = {
        "title": Fore.CYAN + Style.BRIGHT,
        "ok": Fore.GREEN + Style.BRIGHT,
        "warn": Fore.YELLOW + Style.BRIGHT,
        "err": Fore.RED + Style.BRIGHT,
        "info": Fore.CYAN,
        "dim": Style.DIM,
        "accent": Fore.MAGENTA + Style.BRIGHT,
        "score": Fore.BLUE + Style.BRIGHT,
    }
    return f"{palette.get(tone, '')}{text}{Style.RESET_ALL}"


def _check_iron_gate(intent: str, *, file_count: int = 0, size_delta_mb: float = 0.0) -> bool:
    """Enforce Titanium Laws: HITL Iron Gate v1.1 with Impact Brief."""
    dangerous_keywords = {"delete", "rm", "remove", "wipe", "purge", "format", "exec", "shell"}
    intent_lower = intent.lower()

    is_dangerous = any(k in intent_lower for k in dangerous_keywords)
    is_generative = any(k in intent_lower for k in {"build", "refactor", "fix", "scaffold", "implement"})

    if is_dangerous or is_generative or file_count > 3:
        _stream_print("\n[HITL_GATE] High-risk kinetic action detected.", tone="warn")
        _stream_print(f"Action: {intent}", tone="dim")
        
        # Display Impact Brief
        brief = f"◬ Impact_Brief | Files: {file_count or 'N/A'} | Delta: {size_delta_mb or 'Unknown'} MB"
        _stream_print(brief, tone="info")

        try:
            prompt_text = _color("[HITL_APPROVAL] Proceed with Kinetic Execution? {👤✅} [y/N]: ", "warn")
            choice = input(prompt_text).strip().lower()
            return choice == "y"
        except (EOFError, KeyboardInterrupt):
            return False

    return True


def _stream_print(text: str, *, tone: str | None = None, newline: bool = True) -> None:
    rendered = _color(text, tone) if tone else text
    if not sys.stdout.isatty() or STREAM_DELAY <= 0:
        print(rendered, end="\n" if newline else "", flush=True)
        return

    for char in rendered:
        print(char, end="", flush=True)
        if char not in {"\n", "\r"}:
            time.sleep(STREAM_DELAY)
    if newline:
        print("", flush=True)


def _progress(label: str, detail: str, *, tone: str = "dim") -> None:
    _stream_print(f"[{label}] {detail}", tone=tone)


def _print_json(payload: Any) -> None:
    print(json.dumps(payload, indent=2))


def _pretty_render(payload: Any) -> str:
    if isinstance(payload, dict) and "payload" in payload and isinstance(payload["payload"], dict):
        inner = payload["payload"]
        lines = [
            f"status: {inner.get('status', 'UNKNOWN')}",
            f"task: {inner.get('task', '-')}",
        ]
        if "service" in inner:
            lines.append(f"service: {inner['service']}")
        if "source" in inner:
            lines.append(f"source: {inner['source']}")
        if "reason" in inner:
            lines.append(f"reason: {inner['reason']}")
        result = inner.get("result")
        if isinstance(result, dict):
            if "message" in result and "latency_ms" in result:
                lines.append(f"message: {result['message']}")
                lines.append(f"latency_ms: {result['latency_ms']}")
            if "note_title" in result:
                lines.append(f"note_title: {result['note_title']}")
            if "note_id" in result:
                lines.append(f"note_id: {result['note_id']}")
            if "action" in result:
                lines.append(f"action: {result['action']}")
            if "content_chars" in result:
                lines.append(f"content_chars: {result['content_chars']}")
            if "generated_utc" in result:
                lines.append(f"generated_utc: {result['generated_utc']}")
            if "brief" in result:
                lines.append("")
                lines.append(str(result["brief"]))
            if "status" in result and "brief" not in result:
                lines.append(f"health: {result['status']}")
            if "supports_browser_isolation" in result and isinstance(result["supports_browser_isolation"], list):
                lines.append(f"browser_isolation: {', '.join(result['supports_browser_isolation'])}")
            if "principles" in result and isinstance(result["principles"], list):
                lines.append("")
                lines.append("principles:")
                lines.extend(f"- {item}" for item in result["principles"][:5])
            if "architecture_stack" in result and isinstance(result["architecture_stack"], list):
                lines.append("stack:")
                lines.extend(f"- {item}" for item in result["architecture_stack"][:5])
            if "execution_phases" in result and isinstance(result["execution_phases"], list):
                lines.append("phases:")
                for phase in result["execution_phases"][:4]:
                    lines.append(
                        f"- {phase.get('phase')}: {phase.get('goal')} ({phase.get('duration_days')}d, {phase.get('cost_profile')})"
                    )
            if "compute_tiers" in result and isinstance(result["compute_tiers"], list):
                lines.append(f"compute_tiers: {', '.join(result['compute_tiers'])}")
            if "aspects" in result and isinstance(result["aspects"], list):
                lines.append(f"aspects: {', '.join(result['aspects'])}")
            if "compute_tier" in result:
                lines.append(f"compute_tier: {result['compute_tier']}")
            if "browser_isolation" in result and not isinstance(result["browser_isolation"], list):
                lines.append(f"browser_isolation: {result['browser_isolation']}")
            if "aspect" in result:
                lines.append(f"aspect: {result['aspect']}")
            if "cartridge" in result:
                lines.append(f"cartridge: {result['cartridge']}")
            if "memory_count" in result:
                lines.append(f"memory_count: {result['memory_count']}")
            if "assigned_knights" in result:
                lines.append(f"knights: {', '.join(result['assigned_knights'])}")
            if "command_surface" in result:
                lines.append(f"command: {result['command_surface']}")
            if "swarm_capacity" in result and isinstance(result["swarm_capacity"], dict):
                lines.append(
                    f"safe_swarm_units: {result['swarm_capacity'].get('safe_swarm_units')}"
                )
                lines.append(
                    f"max_parallel_browser_sessions: {result['swarm_capacity'].get('max_parallel_browser_sessions')}"
                )
            if "nano_knight_llm_map" in result and isinstance(result["nano_knight_llm_map"], list):
                lines.append("nano_knights:")
                for item in result["nano_knight_llm_map"][:4]:
                    lines.append(
                        f"- {item.get('knight_id')}: {item.get('engine')} / {item.get('model')}"
                    )
        return "\n".join(lines)

    if isinstance(payload, dict) and {"task_id", "phase", "sub_tasks"}.issubset(payload.keys()):
        lines = [
            f"task_id: {payload.get('task_id')}",
            f"phase: {payload.get('phase')}",
            f"sub_tasks: {len(payload.get('sub_tasks', []))}",
        ]
        critique = payload.get("critique")
        if critique:
            lines.append(f"critique_passed: {critique.get('passed')}")
            lines.append(f"critique_confidence: {critique.get('confidence')}")
        return "\n".join(lines)

    return json.dumps(payload, indent=2)


def _emit(payload: Any, *, json_mode: bool = False, title: str | None = None) -> None:
    if json_mode:
        _print_json(payload)
        return

    if title:
        _stream_print(title, tone="title")
    _stream_print(_pretty_render(payload), tone="info")


async def _run_task(
    intent: str,
    *,
    agent_id: str | None = None,
    constraints: list[str] | None = None,
    objective: str | None = None,
    extra_parameters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    # Phase 1: Anya's Ethereal Compilation (Triple-QFT)
    compiler = AnyaCompiler()
    if compiler.pedagogy(intent):
        _stream_print("Anya [PEDAGOGY]: Intent is ambiguous. Renormalizing...", tone="warn")

    titan_prompt, confidence = compiler.compile(intent)
    _stream_print(f"Anya [COMPILE]: {titan_prompt} | ⚡ Confidence: {confidence*100:.0f}%", tone="dim")

    if confidence < 0.5:
        _stream_print("Anya [PEDAGOGY]: Intent clarity is low. Scaling to 1M token context for verification.", tone="warn")

    # Use renormalized intent for routing logic
    intent = compiler.renormalize(intent)

    # Phase 4: Iron Gate (High-risk check)
    if not _check_iron_gate(intent):
        return {"status": "CANCELLED", "reason": "HITL_GATE refused"}

    cp = ControlPlane()
    parameters: dict[str, Any] = dict(extra_parameters or {})
    if agent_id:
        parameters["agent_id"] = agent_id
    if objective:
        parameters["objective"] = objective
    task = TaskPayload(
        intent=intent,
        parameters=parameters,
        constraints=constraints or [],
    )
    return (await cp.process_task(task)).model_dump()


async def _run_sarda(
    intent: str,
    *,
    execute: bool,
    context: str = "",
    privacy: float = 0.0,
    timeout: int = 120,
) -> dict[str, Any]:
    if execute:
        # Phase 4: Iron Gate (High-risk check)
        if not _check_iron_gate(intent):
            return {"status": "CANCELLED", "reason": "HITL_GATE refused"}

    cp = ControlPlane()
    if execute:
        result = cp.sarda_execute(intent, context=context, privacy=privacy, timeout=timeout)
    else:
        result = cp.sarda_plan(intent, privacy=privacy)
    return json.loads(result.to_json())


def _stream_task_progress(
    intent: str,
    *,
    objective: str | None = None,
    constraints: list[str] | None = None,
) -> None:
    lower = intent.lower()
    _progress("analyze", f"intent: {intent}")

    if any(word in lower for word in {"cloudbrain", "notebook", "memory status"}):
        _progress("route", "cloudbrain status path", tone="info")
        time.sleep(PROGRESS_DELAY)
        _progress("fetch", "loading cloudbrain topology", tone="info")
        return

    if any(word in lower for word in {"memory", "context", "recall"}):
        _progress("route", "long-term memory path", tone="info")
        time.sleep(PROGRESS_DELAY)
        _progress("fetch", "querying Appwrite-backed memory", tone="info")
        return

    if any(word in lower for word in {"research", "deep dive", "deep-dive", "investigate"}):
        _progress("route", "research agency path", tone="info")
        time.sleep(PROGRESS_DELAY)
        _progress("scout", f"objective: {objective or intent}", tone="info")
        time.sleep(PROGRESS_DELAY)
        if constraints:
            _progress("guard", f"constraints: {', '.join(constraints)}", tone="warn")
        tier = next((c.split("=", 1)[1] for c in (constraints or []) if c.startswith("compute_tier=")), None)
        if tier:
            _progress("tier", f"compute tier: {tier}", tone="accent")
        _progress("synthesize", "assembling agency brief", tone="info")
        return

    if any(word in lower for word in {"northstar", "war room", "brainstorm"}):
        _progress("route", "northstar war-room path", tone="info")
        time.sleep(PROGRESS_DELAY)
        _progress("align", f"objective: {objective or intent}", tone="info")
        time.sleep(PROGRESS_DELAY)
        if constraints:
            _progress("guard", f"constraints: {', '.join(constraints)}", tone="warn")
        tier = next((c.split("=", 1)[1] for c in (constraints or []) if c.startswith("compute_tier=")), None)
        if tier:
            _progress("tier", f"compute tier: {tier}", tone="accent")
        aspect = next((c.split("=", 1)[1] for c in (constraints or []) if c.startswith("aspect=")), None)
        if aspect:
            _progress("aspect", f"mission aspect: {aspect}", tone="accent")
        _progress("chimera", "running 3-round audit topology", tone="info")
        return

    if any(word in lower for word in {"blueprint", "resource constrained", "development blueprint"}):
        _progress("route", "development blueprint path", tone="info")
        time.sleep(PROGRESS_DELAY)
        _progress("scope", f"objective: {objective or intent}", tone="info")
        time.sleep(PROGRESS_DELAY)
        if constraints:
            _progress("guard", f"constraints: {', '.join(constraints)}", tone="warn")
        tier = next((c.split("=", 1)[1] for c in (constraints or []) if c.startswith("compute_tier=")), None)
        if tier:
            _progress("tier", f"default tier: {tier}", tone="accent")
        _progress("shape", "optimizing phased delivery for constrained resources", tone="info")
        return

    if any(word in lower for word in {"precise mode", "nano-knight", "nano knight", "swarm"}):
        _progress("route", "precise-mode swarm path", tone="info")
        time.sleep(PROGRESS_DELAY)
        _progress("forge", f"objective: {objective or intent}", tone="info")
        time.sleep(PROGRESS_DELAY)
        if constraints:
            _progress("guard", f"constraints: {', '.join(constraints)}", tone="warn")
        tier = next((c.split("=", 1)[1] for c in (constraints or []) if c.startswith("compute_tier=")), None)
        if tier:
            _progress("tier", f"compute tier: {tier}", tone="accent")
        _progress("symmetry", "matching Nano-Knights to omniroute LLM lanes", tone="info")
        _progress("capacity", "computing safe ephemeral swarm capacity", tone="info")
        return

    _progress("route", "control-plane task path", tone="info")
    time.sleep(PROGRESS_DELAY)
    _progress("execute", "delegating to control plane", tone="info")


def _stream_sarda_progress(
    intent: str,
    *,
    execute: bool,
    context: str = "",
    privacy: float = 0.0,
) -> None:
    _progress("analyze", f"sarda intent: {intent}")
    _progress("map", "decomposing into sub-tasks (Merlin)", tone="info")
    time.sleep(PROGRESS_DELAY)

    # Phase 3: Swarm Zoology (Metal Execution)
    _progress("swarm", "deploying 150-token Nano-Knights", tone="accent")
    _progress("formica", "Ants: parallel file rewriting [Δ]", tone="dim")
    _progress("pongid", "Gorillas: API heavy-lifting", tone="dim")
    _progress("castor", "Beavers: WASM/Docker isolation [▩]", tone="dim")
    time.sleep(PROGRESS_DELAY)

    if any(term in intent.lower() for term in {"research", "deep dive", "deep-dive", "investigate"}):
        _progress("research", "augmenting with research agency context", tone="info")
        time.sleep(PROGRESS_DELAY)
    if execute:
        _progress("dispatch", "sending tasks to routed engines", tone="info")
        time.sleep(PROGRESS_DELAY)
        _progress("reduce", "merging outputs (Lukas)", tone="info")
        time.sleep(PROGRESS_DELAY)
        _progress("critique", "running final validation (Sir Sentinel)", tone="info")
    else:
        _progress("plan", "previewing routes without execution", tone="info")


def _interactive_shell(json_mode: bool = False) -> int:
    banner = [
        "Camelot-OS",
        "Prompt-first interface for routing, cloudbrain, and SARDA workflows.",
        "Commands: /help, /route <intent>, /status, /memory <agent>, /research <objective>, /northstar <objective>, /blueprint <objective>, /precise <objective>, /ledger-status, /sarda <intent>, /exit",
    ]
    if not json_mode:
        _stream_print(banner[0], tone="title")
        _stream_print(banner[1], tone="dim")
        _stream_print(banner[2], tone="dim")

    while True:
        try:
            raw = input(_color("Camelot-OS> ", "accent")).strip()
        except EOFError:
            return 0
        except KeyboardInterrupt:
            print()
            return 0

        if not raw:
            continue
        if raw in {"/exit", "exit", "quit"}:
            return 0
        if raw == "/help":
            if not json_mode:
                _stream_print(banner[-1], tone="dim")
            continue

        try:
            if raw.startswith("/gui") or raw.upper() == "//GUI":
                # Launch the Textual TUI
                _stream_print("Launching Obsidian Spire Cockpit v2.0...", tone="ok")
                from .tui_app import SovereignApp
                app = SovereignApp()
                app.run()
                continue

            if raw.startswith("/route "):
                intercept = CLIIntercept()
                result = intercept.intercept(raw[len("/route ") :].strip())
                output = {
                    "knight_id": result.route.knight_id,
                    "engine": result.engine_cmd,
                    "model": result.model,
                    "backend_url": result.backend_url,
                    "reason": result.route.reason,
                }
                if json_mode:
                    _print_json(output)
                else:
                    _stream_print(intercept.format_route_log(result), tone="info")
                continue

            if raw == "/status":
                if not json_mode:
                    _stream_task_progress("cloudbrain status")
                output = asyncio.run(_run_task("cloudbrain status"))
                _emit(output, json_mode=json_mode, title="Cloudbrain Status")
                continue

            if raw == "/research-health":
                output = asyncio.run(_run_task("research health"))
                _emit(output, json_mode=json_mode, title="Research Agency Health")
                continue

            if raw.startswith("/memory "):
                agent_id = raw[len("/memory ") :].strip()
                if not json_mode:
                    _stream_task_progress("memory recall", constraints=["privacy=0.0"])
                output = asyncio.run(
                    _run_task("memory recall", agent_id=agent_id, constraints=["privacy=0.0"])
                )
                _emit(output, json_mode=json_mode, title=f"Memory Recall: {agent_id}")
                continue

            if raw.startswith("/research "):
                objective = raw[len("/research ") :].strip()
                if not json_mode:
                    _stream_task_progress(
                        "research investigate objective",
                        objective=objective,
                        constraints=["privacy=0.0", "compute_tier=hybrid"],
                    )
                output = asyncio.run(
                    _run_task(
                        "research investigate objective",
                        agent_id="lady_apis",
                        objective=objective,
                        constraints=["privacy=0.0", "compute_tier=hybrid"],
                    )
                )
                _emit(output, json_mode=json_mode, title="Research Agency")
                continue

            if raw.startswith("/northstar "):
                objective = raw[len("/northstar ") :].strip()
                constraints = ["privacy=0.0", "compute_tier=apex", "aspect=research"]
                if not json_mode:
                    _stream_task_progress(
                        "northstar war room objective",
                        objective=objective,
                        constraints=constraints,
                    )
                output = asyncio.run(
                    _run_task(
                        "northstar war room objective",
                        agent_id="northstar",
                        objective=objective,
                        constraints=constraints,
                        extra_parameters={
                            "aspect": "research",
                            "compute_tier": "apex",
                            "cartridge": "COGNITIVE",
                            "browser_isolation": "team",
                            "multilogin_enabled": True,
                        },
                    )
                )
                _emit(output, json_mode=json_mode, title="Northstar War Room")
                continue

            if raw.startswith("/blueprint "):
                objective = raw[len("/blueprint ") :].strip()
                constraints = ["compute_tier=kinetic", "budget_mode=lean"]
                if not json_mode:
                    _stream_task_progress(
                        "development blueprint objective",
                        objective=objective,
                        constraints=constraints,
                    )
                output = asyncio.run(
                    _run_task(
                        "development blueprint objective",
                        objective=objective,
                        constraints=constraints,
                        extra_parameters={
                            "compute_tier": "kinetic",
                            "budget_mode": "lean",
                            "team_size": 1,
                            "horizon_days": 30,
                            "prioritize_local_first": True,
                            "multilogin_enabled": True,
                        },
                    )
                )
                _emit(output, json_mode=json_mode, title="Development Blueprint")
                continue

            if raw.startswith("/precise "):
                objective = raw[len("/precise ") :].strip()
                constraints = ["compute_tier=hybrid", "browser_isolation=agency"]
                if not json_mode:
                    _stream_task_progress(
                        "precise mode objective",
                        objective=objective,
                        constraints=constraints,
                    )
                output = asyncio.run(
                    _run_task(
                        "precise mode objective",
                        objective=objective,
                        constraints=constraints,
                        extra_parameters={
                            "compute_tier": "hybrid",
                            "browser_isolation": "agency",
                            "residential_proxy_enabled": True,
                            "stealth_enabled": True,
                            "ephemeral_sessions": True,
                            "operator_count": 1,
                            "memory_gb": 8,
                        },
                    )
                )
                _emit(output, json_mode=json_mode, title="Precise Mode")
                continue

            if raw.startswith("/sarda "):
                intent = raw[len("/sarda ") :].strip()
                if not json_mode:
                    _stream_sarda_progress(intent, execute=False)
                output = asyncio.run(_run_sarda(intent, execute=False))
                _emit(output, json_mode=json_mode, title="SARDA Plan")
                continue

            if raw == "/ledger-status":
                output = ledger_status()
                _emit(output, json_mode=json_mode, title="Ledger Status")
                continue

            if not json_mode:
                _stream_task_progress(raw)
            output = asyncio.run(_run_task(raw))
            _emit(output, json_mode=json_mode, title="Camelot-OS")
        except Exception as exc:
            if json_mode:
                _print_json({"success": False, "error": str(exc)})
            else:
                _stream_print(f"error: {exc}", tone="err")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="Camelot-OS",
        description="Camelot-OS prompt-first CLI for routing, cloudbrain, and SARDA.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--profile", help="Use a specific operator profile")

    sub = parser.add_subparsers(dest="command")

    chat_parser = sub.add_parser("chat", help="Start interactive mode")
    chat_parser.add_argument("--json", action="store_true", help="Emit JSON output")

    route_parser = sub.add_parser("route", help="Show routing decision for an intent")
    route_parser.add_argument("intent", nargs="+")

    ledger = sub.add_parser("ledger", help="Update and sync repository-side ledgers")
    ledger_sub = ledger.add_subparsers(dest="ledger_command", required=True)
    ledger_sub.add_parser("status", help="Show repository ledger status")
    ledger_sync = ledger_sub.add_parser("sync", help="Sync ledger state to the local kernel")
    ledger_sync.add_argument(
        "--intent",
        default="Sync repository ledger state to UKG_Vault",
        help="Sync intent to send to the local kernel",
    )
    ledger_update = ledger_sub.add_parser("update", help="Append a provenance ledger entry")
    ledger_update.add_argument("--title", required=True)
    ledger_update.add_argument("--actor", default="SIR_BORIS (Codex / GPT-5)")
    ledger_update.add_argument("--tag", default="[Omega_SYNC]")
    ledger_update.add_argument("--scope", action="append", required=True)
    ledger_update.add_argument("--verification", action="append", required=True)

    cloudbrain = sub.add_parser("cloudbrain", help="Invoke cloudbrain services")
    cloud_sub = cloudbrain.add_subparsers(dest="cloudbrain_command", required=True)
    cloud_sub.add_parser("status", help="Show cloudbrain status")
    cloud_sync = cloud_sub.add_parser("sync", help="Sync local Camelot state into the canonical Cloud Brain notebook")
    cloud_sync.add_argument("--notebook-id", default="")
    cloud_sync.add_argument("--note-title", default="")
    cloud_sync.add_argument("--summary", default="")
    cloud_sub.add_parser("research-health", help="Show research agency health")
    cloud_sub.add_parser("northstar-health", help="Show Northstar war-room health")
    cloud_sub.add_parser("blueprint-health", help="Show development blueprint health")
    cloud_sub.add_parser("precise-health", help="Show precise-mode swarm health")

    memory = cloud_sub.add_parser("memory", help="Recall long-term memory")
    memory.add_argument("--agent-id", default="merlin")
    memory.add_argument("--privacy", type=float, default=0.0)

    research = cloud_sub.add_parser("research", help="Invoke research agency")
    research.add_argument("objective")
    research.add_argument("--agent-id", default="lady_apis")
    research.add_argument("--privacy", type=float, default=0.0)
    research.add_argument("--tier", choices=("kinetic", "hybrid", "apex"), default="hybrid")
    research.add_argument("--allow-remote-sensitive", action="store_true")

    northstar = cloud_sub.add_parser("northstar", help="Run Northstar war-room planning")
    northstar.add_argument("objective")
    northstar.add_argument(
        "--aspect",
        choices=("research", "architecture", "audit", "operations", "growth"),
        default="research",
    )
    northstar.add_argument("--agent-id", default="northstar")
    northstar.add_argument("--privacy", type=float, default=0.0)
    northstar.add_argument("--tier", choices=("kinetic", "hybrid", "apex"), default="apex")
    northstar.add_argument(
        "--cartridge",
        choices=("ANT", "BEAVER", "HAWK", "SPIDER", "COGNITIVE", "ORACLE"),
        default="COGNITIVE",
    )
    northstar.add_argument(
        "--browser-isolation",
        choices=("stealth", "team", "agency"),
        default="team",
    )
    northstar.add_argument("--disable-multilogin", action="store_true")

    blueprint = cloud_sub.add_parser("blueprint", help="Generate efficient development blueprint")
    blueprint.add_argument("objective")
    blueprint.add_argument("--tier", choices=("kinetic", "hybrid", "apex"), default="kinetic")
    blueprint.add_argument("--budget-mode", choices=("lean", "balanced", "aggressive"), default="lean")
    blueprint.add_argument("--team-size", type=int, default=1)
    blueprint.add_argument("--horizon-days", type=int, default=30)
    blueprint.add_argument("--disable-multilogin", action="store_true")

    precise = cloud_sub.add_parser("precise", help="Plan precise-mode Nano-Knight browser swarm")
    precise.add_argument("objective")
    precise.add_argument("--tier", choices=("kinetic", "hybrid", "apex"), default=None)
    precise.add_argument("--browser-isolation", choices=("stealth", "team", "agency"), default=None)
    precise.add_argument("--operator-count", type=int, default=1)
    precise.add_argument("--memory-gb", type=int, default=8)
    precise.add_argument("--enable-residential-proxy", action="store_true", help="Enable residential proxy (Direct by default)")
    precise.add_argument("--enable-stealth", action="store_true", help="Enable stealth injection")
    precise.add_argument("--ephemeral-sessions", action="store_true", help="Use ephemeral sessions (Persistent by default)")

    sarda = sub.add_parser("sarda", help="Plan or execute SARDA")
    sarda.add_argument("intent")
    sarda.add_argument("--execute", action="store_true")
    sarda.add_argument("--context", default="")
    sarda.add_argument("--privacy", type=float, default=0.0)
    sarda.add_argument("--timeout", type=int, default=120)

    return parser


def main() -> int:
    known_commands = {"chat", "route", "cloudbrain", "sarda", "ledger"}
    argv = sys.argv[1:]

    if argv and not argv[0].startswith("-") and argv[0] not in known_commands:
        json_mode = False
        prompt_parts = argv
        if "--json" in argv:
            json_mode = True
            prompt_parts = [part for part in argv if part != "--json"]
        if not json_mode:
            _stream_task_progress(" ".join(prompt_parts))
        output = asyncio.run(_run_task(" ".join(prompt_parts)))
        _log_run(output)
        _emit(output, json_mode=json_mode, title="Camelot-OS")
        return 0

    parser = _build_parser()
    args = parser.parse_args(argv)

    # Task A6: Persisted operator config
    config_mgr = ConfigManager()
    profile = config_mgr.get_profile(args.profile)
    
    # Task E3: Verification Ledger
    prov_mgr = ProvenanceManager()

    def _log_run(results: dict[str, Any], success: bool = True):
        run = VerificationRun(
            run_id=f"run_{int(time.time())}",
            operator=args.profile or "default",
            command=" ".join(argv),
            results=results,
            success=success
        )
        prov_mgr.log_verification(run)
        payload = results.get("payload", {}) if isinstance(results, dict) else {}
        service = payload.get("service")
        if success and service != "notebooklm_sync" and "cloudbrain sync" not in run.command.lower():
            event = sync_after_event(
                event_type="verification_run",
                command=run.command,
                results=results,
            )
            if isinstance(results, dict):
                results.setdefault("cloudbrain_sync", event)

    if args.command == "chat":
        return _interactive_shell(json_mode=args.json)

    if args.command == "route":
        intercept = CLIIntercept()
        result = intercept.intercept(" ".join(args.intent))
        if args.json:
            _print_json(
                {
                    "knight_id": result.route.knight_id,
                    "engine": result.engine_cmd,
                    "model": result.model,
                    "backend_url": result.backend_url,
                    "reason": result.route.reason,
                }
            )
        else:
            _stream_print(intercept.format_route_log(result), tone="info")
        return 0

    if args.command == "ledger":
        if args.ledger_command == "status":
            output = ledger_status()
        elif args.ledger_command == "update":
            output = append_provenance_entry(
                title=args.title,
                actor=args.actor,
                scope=list(args.scope),
                verification=list(args.verification),
                tag=args.tag,
            )
            output["cloudbrain_sync"] = sync_after_event(
                event_type="ledger_update",
                command=f"ledger update {args.title}",
                results=output,
            )
        else:
            if not args.json:
                _progress("sync", "sending ledger sync intent to local kernel", tone="info")
            output = asyncio.run(sync_to_kernel(args.intent))
        _log_run(output)
        _emit(output, json_mode=args.json, title="Ledger")
        return 0

    if args.command == "cloudbrain":
        if not args.json:
            if args.cloudbrain_command == "status":
                _stream_task_progress("cloudbrain status")
            elif args.cloudbrain_command == "sync":
                _stream_task_progress("cloud brain sync")
            elif args.cloudbrain_command == "research-health":
                _stream_task_progress("research health")
            elif args.cloudbrain_command == "northstar-health":
                _stream_task_progress("northstar health")
            elif args.cloudbrain_command == "blueprint-health":
                _stream_task_progress("development blueprint health")
            elif args.cloudbrain_command == "precise-health":
                _stream_task_progress("precise mode health")
            elif args.cloudbrain_command == "memory":
                _stream_task_progress(
                    "memory recall",
                    constraints=[f"privacy={args.privacy}"],
                )
            elif args.cloudbrain_command == "northstar":
                constraints = [
                    f"privacy={args.privacy}",
                    f"compute_tier={args.tier}",
                    f"aspect={args.aspect}",
                ]
                _stream_task_progress(
                    "northstar war room objective",
                    objective=args.objective,
                    constraints=constraints,
                )
            elif args.cloudbrain_command == "blueprint":
                constraints = [
                    f"compute_tier={args.tier}",
                    f"budget_mode={args.budget_mode}",
                ]
                _stream_task_progress(
                    "development blueprint objective",
                    objective=args.objective,
                    constraints=constraints,
                )
            elif args.cloudbrain_command == "precise":
                constraints = [
                    f"compute_tier={args.tier}",
                    f"browser_isolation={args.browser_isolation}",
                ]
                _stream_task_progress(
                    "precise mode objective",
                    objective=args.objective,
                    constraints=constraints,
                )
            else:
                constraints = [f"privacy={args.privacy}", f"compute_tier={args.tier}"]
                if args.allow_remote_sensitive:
                    constraints.append("allow_remote_sensitive")
                _stream_task_progress(
                    "research investigate objective",
                    objective=args.objective,
                    constraints=constraints,
                )
        if args.cloudbrain_command == "status":
            output = asyncio.run(_run_task("cloudbrain status"))
        elif args.cloudbrain_command == "sync":
            extra_parameters: dict[str, Any] = {}
            if args.notebook_id:
                extra_parameters["notebook_id"] = args.notebook_id
            if args.note_title:
                extra_parameters["note_title"] = args.note_title
            if args.summary:
                extra_parameters["extra_summary"] = args.summary
            output = asyncio.run(
                _run_task(
                    "cloud brain sync",
                    extra_parameters=extra_parameters,
                )
            )
        elif args.cloudbrain_command == "research-health":
            output = asyncio.run(_run_task("research health"))
        elif args.cloudbrain_command == "northstar-health":
            output = asyncio.run(_run_task("northstar health"))
        elif args.cloudbrain_command == "blueprint-health":
            output = asyncio.run(_run_task("development blueprint health"))
        elif args.cloudbrain_command == "precise-health":
            output = asyncio.run(_run_task("precise mode health"))
        elif args.cloudbrain_command == "memory":
            output = asyncio.run(
                _run_task(
                    "memory recall",
                    agent_id=args.agent_id,
                    constraints=[f"privacy={args.privacy}"],
                )
            )
        elif args.cloudbrain_command == "northstar":
            constraints = [
                f"privacy={args.privacy}",
                f"compute_tier={args.tier}",
                f"aspect={args.aspect}",
            ]
            output = asyncio.run(
                _run_task(
                    "northstar war room objective",
                    agent_id=args.agent_id,
                    objective=args.objective,
                    constraints=constraints,
                    extra_parameters={
                        "aspect": args.aspect,
                        "compute_tier": args.tier,
                        "cartridge": args.cartridge,
                        "browser_isolation": args.browser_isolation,
                        "multilogin_enabled": not args.disable_multilogin,
                    },
                )
            )
        elif args.cloudbrain_command == "blueprint":
            constraints = [
                f"compute_tier={args.tier}",
                f"budget_mode={args.budget_mode}",
            ]
            output = asyncio.run(
                _run_task(
                    "development blueprint objective",
                    objective=args.objective,
                    constraints=constraints,
                    extra_parameters={
                        "compute_tier": args.tier,
                        "budget_mode": args.budget_mode,
                        "team_size": args.team_size,
                        "horizon_days": args.horizon_days,
                        "prioritize_local_first": True,
                        "multilogin_enabled": not args.disable_multilogin,
                    },
                )
            )
        elif args.cloudbrain_command == "precise":
            # Apply profile defaults if flags are not provided
            tier = args.tier or profile.compute_tier
            isolation = args.browser_isolation or profile.browser_isolation
            
            constraints = [
                f"compute_tier={tier}",
                f"browser_isolation={isolation}",
            ]
            output = asyncio.run(
                _run_task(
                    "precise mode objective",
                    objective=args.objective,
                    constraints=constraints,
                    extra_parameters={
                        "compute_tier": tier,
                        "browser_isolation": isolation,
                        "residential_proxy_enabled": args.enable_residential_proxy or profile.residential_proxy,
                        "stealth_enabled": args.enable_stealth or profile.stealth,
                        "ephemeral_sessions": args.ephemeral_sessions or profile.ephemeral_sessions,
                        "operator_count": args.operator_count,
                        "memory_gb": args.memory_gb,
                    },
                )
            )
        else:
            constraints = [f"privacy={args.privacy}", f"compute_tier={args.tier}"]
            if args.allow_remote_sensitive:
                constraints.append("allow_remote_sensitive")
            output = asyncio.run(
                _run_task(
                    "research investigate objective",
                    agent_id=args.agent_id,
                    objective=args.objective,
                    constraints=constraints,
                )
            )
        _log_run(output)
        _emit(output, json_mode=args.json, title="Cloudbrain")
        return 0

    if args.command == "sarda":
        if not args.json:
            _stream_sarda_progress(
                args.intent,
                execute=args.execute,
                context=args.context,
                privacy=args.privacy,
            )
        output = asyncio.run(
            _run_sarda(
                args.intent,
                execute=args.execute,
                context=args.context,
                privacy=args.privacy,
                timeout=args.timeout,
            )
        )
        _log_run(output)
        _emit(output, json_mode=args.json, title="SARDA")
        return 0

    return _interactive_shell(json_mode=args.json)


if __name__ == "__main__":
    raise SystemExit(main())
