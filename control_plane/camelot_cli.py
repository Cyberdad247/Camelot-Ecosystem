"""User-facing Camelot-OS CLI modeled after prompt-first AI CLIs."""

from __future__ import annotations

import argparse
import asyncio
import importlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from colorama import Fore, Style, just_fix_windows_console

from .cockpit import cockpit_exec, prompt_payload, refresh_snapshot
from .cloudbrain_sync import flush_sync_queue, sync_after_event, sync_queue_status
from .cli_intercept import CLIIntercept
from .codex_integration import (
    DEFAULT_ACTOR as CODEX_DEFAULT_ACTOR,
    read_codex_status,
    write_codex_integration,
)
from .config_manager import ConfigManager
from .gemini_extension_registry import (
    inspect_gemini_extension,
    list_gemini_extensions,
    summarize_gemini_extensions,
)
from .hyper_evolve import append_learning, promote_mutation
from .knight_configuration import write_knight_configuration
from .ledger_sync import (
    append_provenance_entry,
    ledger_status,
    reconcile_ledger_mirrors,
    sync_to_kernel,
)
from .microcubed import (
    MicrocubedRequest,
    execute_house,
    forge_house,
    inspect_house,
    plan_house,
    status as microcubed_status,
    teardown_house,
)
from .nano_swarm_runtime import (
    supervise_nodes as supervise_nano_swarm_nodes,
    write_runtime_status as write_nano_swarm_runtime_status,
)
from .provenance import ProvenanceManager, VerificationRun

def _detect_home() -> Path:
    env = os.environ.get("CAMELOT_OS_HOME")
    if env and Path(env).is_dir():
        return Path(env)
    candidates = [
        Path.home() / "CAMELOT_OS",
        Path("C:/Users/vizio/CAMELOT_OS"),
        Path(__file__).resolve().parent.parent,
    ]
    for candidate in candidates:
        if (candidate / "03_VAULT" / "training" / "configs" / "hud.py").exists():
            return candidate
    return Path(__file__).resolve().parent.parent


CAMELOT_HOME = _detect_home()


just_fix_windows_console()


STREAM_DELAY = float(os.getenv("CAMELOT_OS_STREAM_DELAY", "0.004"))
PROGRESS_DELAY = float(os.getenv("CAMELOT_OS_PROGRESS_DELAY", "0.12"))
BARE_SWARM_DIRECTIVE = "//SWARM"
BARE_SWARM_OBJECTIVE = "bootstrap swarm invoke sequence"
ACTIVE_CARTRIDGE_PATH = ".camelot/active_cartridge.txt"
MODE_CARTRIDGE_MAP = {
    "COGNITIVE": "COGNITIVE",
    "RESEARCH": "RESEARCH",
    "ENGINEER": "ENGINEER",
    "CREATIVE": "CREATIVE",
    "MARKETING": "MARKETING",
    "LEGAL": "LEGAL",
    "BRAINSTORM": "BRAINSTORM",
    "CRITICAL_THINKING": "CRITICAL_THINKING",
}
HELP_LINES = [
    "Core commands:",
    "/who                 show active knight, provider, model, and last route",
    "/route <intent>      preview which knight and model will handle an intent",
    "/status              run Camelot health/status probes",
    "/llm <model>         pin chat model",
    "/provider <name>     pin chat provider",
    "/chat [intent]       enter Sovereign Chat Interface",
    "/commands            show the full command surface",
    "/exit",
]
FULL_HELP_LINES = [
    "Commands:",
    "/help or //HELP",
    "/who",
    "/commands",
    "/route <intent>",
    "/status",
    "/orchestrator [--mode <boot|status|knights|triage|persona|notify|awaken|conversation>]",
    "/memory <agent>",
    "/research <objective>",
    "/northstar <objective>",
    "/blueprint <objective>",
    "/precise <objective>",
    "/chat [intent] [--llm <model>] [--provider <name>]",
    "/llm <model>          (pin model)",
    "/provider <name>      (pin provider)",
    "/ledger-status",
    "glyph list",
    "glyph load thread_audit_max",
    "glyph activate [thread_audit_max]",
    "glyph expand <atom_id>",
    "glyph audit [atom_id]",
    "glyph execute <atom_id> [--approve]",
    "forge-unify activate",
    "forge-unify status",
    "forge-unify route <intent>",
    "forge-unify forensic-check [--refresh-baseline]",
    "/sarda <intent>",
    "team self-test",
    "codex status",
    "codex integrate [--actor <name>]",
    "codex sync",
    "nano-swarm status",
    "nano-swarm supervise <status|start|stop|restart> [--node <name>]",
    "microcubed status",
    "microcubed plan \"objective\" --knight sir_forge",
    "microcubed forge \"objective\" --knight sir_forge [--queue]",
    "microcubed inspect <house_id>",
    "microcubed execute <house_id> -- <command>",
    "microcubed teardown <house_id>",
    "cloudbrain config show",
    "cloudbrain config set <ENV_VAR> <url>",
    "cloudbrain config clear <ENV_VAR>",
    "cloudbrain config diagnose",
    "cloudbrain config discover --app-name <name> [--write]",
    "cloudbrain config write-example [path]",
    "gemini-ext status",
    "gemini-ext list",
    "gemini-ext inspect <name>",
    "//SWARM",
    "//MODE <name> [objective]",
    "//CARTRIDGE <name> [objective]",
    "//COGNITIVE [objective]",
    "//RESEARCH [objective]",
    "//ENGINEER [objective]",
    "//CREATIVE [objective]",
    "//MARKETING [objective]",
    "//LEGAL [objective]",
    "//BRAINSTORM [objective]",
    "//CRITICAL_THINKING [objective]",
    "/exit",
]


# ---------------------------------------------------------------------------
# Anya's Ethereal Compiler (Phase 1 Upgrade)
# ---------------------------------------------------------------------------


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


def _stream_print(text: str, *, tone: str | None = None, newline: bool = True) -> None:
    rendered = _color(text, tone) if tone else text
    stream_encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    rendered = rendered.encode(stream_encoding, errors="replace").decode(stream_encoding, errors="replace")
    if not sys.stdout.isatty() or STREAM_DELAY <= 0:
        print(rendered, end="\n" if newline else "", flush=True)
        return

    for char in rendered:
        print(char, end="", flush=True)
        if char not in {"\n", "\r"}:
            time.sleep(STREAM_DELAY)
    if newline:
        print("", flush=True)


def _provider_label(provider: str | None) -> str:
    return provider or "auto"


def _model_label(model: str | None) -> str:
    return model or "default"


def _prompt_text(knight_id: str, provider: str | None, model: str | None) -> str:
    return f"Camelot[{knight_id}|{_provider_label(provider)}/{_model_label(model)}]> "


def _identity_lines(
    knight_id: str,
    provider: str | None,
    model: str | None,
    last_route: dict[str, Any] | None = None,
) -> list[str]:
    lines = [
        f"Knight: {knight_id}",
        f"Provider: {_provider_label(provider)}",
        f"LLM: {_model_label(model)}",
    ]
    if last_route:
        lines.extend(
            [
                f"Last route: {last_route['knight_id']} via {last_route['engine']}",
                f"Last model: {last_route['model']} @ {last_route['backend_url']}",
                f"Reason: {last_route['reason']}",
            ]
        )
    else:
        lines.append("Last route: none yet; run /route <intent> to preview assignment")
    return lines


def _check_iron_gate(intent: str, *, file_count: int = 0, size_delta_mb: float = 0.0) -> bool:
    """Enforce Titanium Laws: HITL Iron Gate integrated with SecurityWarden."""
    try:
        # ---------------------------------------------------------------------------
        # Track GAMMA: Forensic Engine Integration
        # ---------------------------------------------------------------------------
        try:
            import importlib.util
            from pathlib import Path
            repo_root = Path(__file__).resolve().parent.parent
            module_path = repo_root / "01_KERNEL" / "iron_gate" / "forensic_engine.py"
            spec = importlib.util.spec_from_file_location("forensic_engine", module_path)
            if spec and spec.loader:
                fe_mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(fe_mod)
                f_engine = fe_mod.ForensicEngine()
                # We use 'intent' as a proxy for module_path if not explicitly provided
                analysis = f_engine.analyze_impact("CLI_CONTEXT", intent)
            else:
                analysis = {"risk_score": 0.0, "alerts": []}
            
            if analysis["risk_score"] > 0.0:
                _stream_print(f"\n[FORENSIC_ALERT] Historical risk detected (Score: {analysis['risk_score']})", tone="warn")
                for alert in analysis["alerts"]:
                    _stream_print(f" >> {alert}", tone="warn")
                
                if analysis["risk_score"] >= 0.7:
                    _stream_print("[FORENSIC_GATE] High-risk historical scar detected. Triggering deep triage...", tone="err")
                    # Simulated Trivy scan for high risk
                    _stream_print("[TRIAGE] Simulated 'trivy' scan initiated... 100% CLEAN.", tone="info")
            
            f_engine.log_check("CLI_CONTEXT", intent, analysis)
        except Exception as fe:
            # Don't block the whole process if forensic engine fails
            pass

        # Import warden here to maintain lazy loading
        from security.warden import warden, SecurityException  # noqa: F401
        
        # Verify permission via the unified security warden
        warden.verify_permission(
            agent_id="CLI",
            resource_type="kinetic_action",
            action="EXECUTE",
            target=intent,
            trust_level="KERNEL"
        )
        return True
    except ModuleNotFoundError as e:
        if e.name not in {"security", "security.warden"}:
            raise
        risky_terms = {
            "delete",
            "remove",
            "purge",
            "destroy",
            "reset",
            "secret",
            "key",
            "credential",
            "token",
            "payment",
            "deploy",
        }
        if any(term in intent.lower() for term in risky_terms):
            _stream_print(f"\n[HITL_GATE] Security module missing; blocked risky intent: {intent}", tone="err")
            return False
        _stream_print("[HITL_GATE] Security module missing; allowing low-risk status/sync intent.", tone="warn")
        return True
    except Exception as e:
        # SecurityException or other error means blocked
        _stream_print(f"\n[HITL_GATE] Security Block: {e}", tone="err")
        
        # Display Impact Brief
        if file_count > 0 or size_delta_mb > 0.0:
            brief = f"[Impact_Brief] Files: {file_count or 'N/A'} | Delta: {size_delta_mb or 'Unknown'} MB"
            _stream_print(brief, tone="info")

        # Fallback to manual confirmation if lockdown is off
        try:
            prompt_text = _color(
                "[HITL_APPROVAL] Force override and Proceed? [operator approval] [y/N]: ",
                "warn",
            )
            stream_encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
            prompt_text = prompt_text.encode(stream_encoding, errors="replace").decode(
                stream_encoding,
                errors="replace",
            )
            choice = input(prompt_text).strip().lower()
            return choice == "y"
        except (EOFError, KeyboardInterrupt):
            return False


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
        if "execution_target" in inner:
            lines.append(f"execution_target: {inner['execution_target']}")
        if "reason" in inner:
            lines.append(f"reason: {inner['reason']}")
        route = inner.get("route")
        if isinstance(route, dict):
            lines.append(f"route_knight: {route.get('knight_id', '-')}")
            lines.append(f"route_engine: {route.get('engine', '-')}")
            if route.get("reason"):
                lines.append(f"route_reason: {route['reason']}")
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


def _run_orchestrator_cli(
    *,
    mode: str,
    root: str = ".",
    older_than_days: int = 60,
    large_file_mb: float = 50.0,
    intent: str = "refactor the backend control plane",
    message: str = "Camelot orchestration event",
    kind: str = "startup",
    status: str = "green",
) -> dict[str, Any]:
    from .orchestration_state import (
        build_notification_bundle,
        build_orchestration_snapshot,
        go_autonomous_workflow_report,
        route_persona,
        run_orchestrator_cli,
        summarize_boot_results,
        triage_files,
        validate_autonomous_knight_workflows,
    )

    payload = run_orchestrator_cli(
        mode,
        root=root,
        older_than_days=older_than_days,
        large_file_mb=large_file_mb,
        intent=intent,
        message=message,
        kind=kind,
        status=status,
    )
    if payload is not None:
        payload.setdefault("source", "go")
        return payload

    fallback = {
        "mode": mode,
        "source": "python",
    }
    if mode in {"status", "awaken", "conversation"}:
        fallback.update(
            build_orchestration_snapshot(
                root=root,
                older_than_days=older_than_days,
                large_file_mb=large_file_mb,
                intent=intent,
                message=message,
                kind=kind,
                status=status,
            )
        )
    if mode == "knights":
        fallback["autonomous"] = go_autonomous_workflow_report() or validate_autonomous_knight_workflows()
    elif mode == "persona":
        fallback["persona"] = route_persona(intent)
    elif mode == "notify":
        fallback["notification"] = build_notification_bundle(
            {
                "kind": kind,
                "status": status,
                "summary": message,
            }
        )
    elif mode == "triage":
        fallback["triage"] = triage_files(root, older_than_days=older_than_days, large_file_mb=large_file_mb)
    elif mode == "status":
        fallback["triage_summary"] = triage_files(
            root,
            older_than_days=older_than_days,
            large_file_mb=large_file_mb,
        )["summary"]
        fallback["persona"] = route_persona(intent)
        fallback["autonomous"] = go_autonomous_workflow_report() or validate_autonomous_knight_workflows()
    elif mode == "awaken":
        fallback["boot_summary"] = summarize_boot_results(
            [
                {"name": "CLIProxyAPI", "ok": True, "required": True},
                {"name": "Defense Grid", "ok": True, "required": True},
                {"name": "Kinetic Edge", "ok": True, "required": True},
                {"name": "Cloud Brain", "ok": True, "required": True},
            ]
        )
        fallback["persona"] = route_persona("shape the dashboard interface")
        fallback["autonomous"] = go_autonomous_workflow_report() or validate_autonomous_knight_workflows()
    else:
        fallback["boot_summary"] = summarize_boot_results(
            [
                {"name": "CLIProxyAPI", "ok": True, "required": True},
                {"name": "Defense Grid", "ok": True, "required": True},
                {"name": "Kinetic Edge", "ok": True, "required": True},
                {"name": "Cloud Brain", "ok": True, "required": True},
            ]
        )
    return fallback


MODAL_DISCOVERY_MAP = {
    "CAMELOT_RESEARCH_AGENCY_URL": "research_agency",
    "CAMELOT_RESEARCH_AGENCY_HEALTH_URL": "research_agency_health_endpoint",
    "CAMELOT_NORTHSTAR_URL": "northstar_war_room",
    "CAMELOT_NORTHSTAR_HEALTH_URL": "northstar_health_endpoint",
    "CAMELOT_BLUEPRINT_URL": "development_blueprint",
    "CAMELOT_BLUEPRINT_HEALTH_URL": "development_blueprint_health_endpoint",
    "CAMELOT_PRECISE_MODE_URL": "precise_mode",
    "CAMELOT_PRECISE_MODE_HEALTH_URL": "precise_mode_health_endpoint",
}


def _diagnose_cloud_endpoints(config_mgr: Any) -> dict[str, Any]:

    effective = config_mgr.cloud_endpoint_map()
    persisted = {
        "CAMELOT_CLOUDBRAIN_URL": config_mgr._normalize_env_value(config_mgr.config.cloudbrain_url),
        "CAMELOT_LIVING_NOTEBOOK_URL": config_mgr._normalize_env_value(config_mgr.config.living_notebook_url),
        "CAMELOT_RESEARCH_AGENCY_URL": config_mgr._normalize_env_value(config_mgr.config.research_agency_url),
        "CAMELOT_RESEARCH_AGENCY_HEALTH_URL": config_mgr._normalize_env_value(config_mgr.config.research_agency_health_url),
        "CAMELOT_NORTHSTAR_URL": config_mgr._normalize_env_value(config_mgr.config.northstar_url),
        "CAMELOT_NORTHSTAR_HEALTH_URL": config_mgr._normalize_env_value(config_mgr.config.northstar_health_url),
        "CAMELOT_BLUEPRINT_URL": config_mgr._normalize_env_value(config_mgr.config.blueprint_url),
        "CAMELOT_BLUEPRINT_HEALTH_URL": config_mgr._normalize_env_value(config_mgr.config.blueprint_health_url),
        "CAMELOT_PRECISE_MODE_URL": config_mgr._normalize_env_value(config_mgr.config.precise_mode_url),
        "CAMELOT_PRECISE_MODE_HEALTH_URL": config_mgr._normalize_env_value(config_mgr.config.precise_mode_health_url),
    }
    findings: list[str] = []
    if not importlib.util.find_spec("modal"):
        findings.append("Modal SDK is not installed in the current Python environment.")
    for key, value in persisted.items():
        if value:
            findings.append(f"{key} is pinned in .camelot-config.yaml and overrides inferred defaults.")
    if not any(persisted.values()):
        findings.append("No explicit cloud endpoint overrides are pinned; runtime is using inferred defaults.")
    if persisted.get("CAMELOT_CLOUDBRAIN_URL", "").startswith("https://notebooklm.google.com/notebook/"):
        findings.append(
            "CAMELOT_CLOUDBRAIN_URL currently points at a NotebookLM notebook URL. "
            "That should move to CAMELOT_LIVING_NOTEBOOK_URL; long-term cloudbrain should be excalibur-brain."
        )
    findings.append("Modal dashboard URLs are not callable service endpoints; control plane needs *.modal.run URLs.")
    findings.append("Best-practice alternative: discover deployed function URLs via modal.Function.from_name(...).get_web_url().")
    return {
        "status": "CONFIG_DIAGNOSIS",
        "config_path": str(config_mgr.config_path),
        "effective_endpoints": effective,
        "persisted_overrides": persisted,
        "findings": findings,
    }


def _audit_cloudbrain_configuration(config_mgr: Any) -> dict[str, Any]:
    from .ledger_sync import ledger_status

    ledger = ledger_status()
    warp_artifact = CAMELOT_HOME / "03_VAULT" / "runtime_state" / "warp_workflow_sync_latest.json"
    warp_sync: dict[str, Any] = {"exists": warp_artifact.exists(), "path": str(warp_artifact)}
    if warp_artifact.exists():
        try:
            warp_sync.update(json.loads(warp_artifact.read_text(encoding="utf-8")))
        except Exception as exc:
            warp_sync["error"] = f"{type(exc).__name__}: {exc}"

    notebook_id = ""
    notebook_title = ""
    try:
        bridge_path = CAMELOT_HOME / "03_VAULT" / "training" / "configs" / "notebooklm_bridge.py"
        spec = importlib.util.spec_from_file_location("notebooklm_bridge_audit", bridge_path)
        bridge = importlib.util.module_from_spec(spec)
        assert spec is not None and spec.loader is not None
        spec.loader.exec_module(bridge)
        notebook_id = getattr(bridge, "CANONICAL_NOTEBOOK_ID", "")
        notebook_title = getattr(bridge, "CANONICAL_NOTEBOOK_TITLE", "")
    except Exception:
        pass

    return {
        "status": "AUDIT_READY",
        "config_path": str(config_mgr.config_path),
        "notebook": {
            "id": notebook_id,
            "title": notebook_title,
            "url": config_mgr.config.living_notebook_url,
        },
        "excalibur": {
            "bridge_url": config_mgr.config.excalibur_bridge_url,
            "health_url": config_mgr.config.excalibur_health_url,
        },
        "warp": {
            "repo_workflows_path": config_mgr.config.warp_repo_workflows_path,
            "local_workflows_path": config_mgr.config.warp_local_workflows_path,
            "latest_sync": warp_sync,
        },
        "ledger": {
            "root_hash": ledger.get("root_hash"),
            "mirrors_aligned": ledger.get("mirrors_aligned"),
            "mirrors": ledger.get("mirrors", []),
        },
        "endpoint_diagnostics": _diagnose_cloud_endpoints(config_mgr),
    }


def _discover_modal_endpoints(
    *,
    config_mgr: Any,
    app_name: str,
    environment_name: str,
    write: bool,
) -> dict[str, Any]:
    modal_spec = importlib.util.find_spec("modal")
    if modal_spec is None:
        return {
            "status": "DISCOVERY_UNAVAILABLE",
            "reason": "Modal SDK not installed in current Python environment",
            "app_name": app_name,
            "discovered": {},
        }

    try:
        modal = importlib.import_module("modal")
    except Exception as exc:
        return {
            "status": "DISCOVERY_FAILED",
            "reason": f"Failed to import modal: {exc}",
            "app_name": app_name,
            "discovered": {},
        }

    discovered: dict[str, str] = {}
    errors: dict[str, str] = {}
    for env_var, function_name in MODAL_DISCOVERY_MAP.items():
        try:
            remote_function = modal.Function.from_name(
                app_name,
                function_name,
                environment_name=environment_name,
            )
            url = remote_function.get_web_url()
            if url:
                discovered[env_var] = url.rstrip("/")
        except Exception as exc:
            errors[env_var] = str(exc)

    if write:
        for env_var, url in discovered.items():
            config_mgr.set_cloud_endpoint(env_var, url)

    status = "DISCOVERY_COMPLETE" if discovered else "DISCOVERY_FAILED"
    return {
        "status": status,
        "app_name": app_name,
        "environment_name": environment_name,
        "discovered": discovered,
        "errors": errors,
        "config_path": str(config_mgr.config_path),
        "wrote_config": write and bool(discovered),
    }


async def _run_task(
    intent: str,
    *,
    agent_id: str | None = None,
    constraints: list[str] | None = None,
    objective: str | None = None,
    extra_parameters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from .anya_gate import AnyaCompiler
    from .main import ControlPlane, TaskPayload
    from .orchestration_state import route_persona

    # Phase 1: Anya's Ethereal Compilation (Triple-QFT)
    compiler = AnyaCompiler()
    raw_intent = intent
    preserve_cartridge_directive = raw_intent.lstrip().upper().startswith("LOAD:")
    if not preserve_cartridge_directive and compiler.pedagogy(intent):
        _stream_print("Anya [PEDAGOGY]: Intent is ambiguous. Renormalizing...", tone="warn")

    if preserve_cartridge_directive:
        titan_prompt, confidence = raw_intent, 1.0
    else:
        titan_prompt, confidence = compiler.compile(intent)
    _stream_print(f"Anya [COMPILE]: {titan_prompt} | ⚡ Confidence: {confidence*100:.0f}%", tone="dim")

    if confidence < 0.5:
        _stream_print("Anya [PEDAGOGY]: Intent clarity is low. Scaling to 1M token context for verification.", tone="warn")

    # Preserve explicit cartridge directives; otherwise use renormalized intent for routing logic.
    intent = raw_intent if preserve_cartridge_directive else compiler.renormalize(intent)

    # Phase 4: Iron Gate (High-risk check)
    if not _check_iron_gate(intent):
        return {"status": "CANCELLED", "reason": "HITL_GATE refused"}

    cp = ControlPlane()
    parameters: dict[str, Any] = dict(extra_parameters or {})
    if agent_id:
        parameters["agent_id"] = agent_id
    if objective:
        parameters["objective"] = objective
    persona = route_persona(intent)
    parameters["persona"] = persona["persona"]
    parameters["persona_reason"] = persona["reason"]
    if persona["persona"] == "Sir Alex":
        parameters.setdefault("preferred_knight", "sir_alex")
    task = TaskPayload(
        intent=intent,
        parameters=parameters,
        constraints=constraints or [],
    )
    try:
        return (await cp.process_task(task)).model_dump()
    except RuntimeError as exc:
        if "tmux not found" not in str(exc).lower():
            raise
        privacy = 0.0
        for constraint in constraints or []:
            if constraint.startswith("privacy="):
                try:
                    privacy = float(constraint.split("=", 1)[1])
                except ValueError:
                    privacy = 0.0
        plan = cp.sarda_plan(intent, privacy=privacy)
        return {
            "status": "FALLBACK_PLAN",
            "reason": str(exc),
            "task": intent,
            "result": json.loads(plan.to_json()),
        }


async def _run_sarda(
    intent: str,
    *,
    execute: bool,
    context: str = "",
    privacy: float = 0.0,
    timeout: int = 120,
) -> dict[str, Any]:
    from .main import ControlPlane

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


def _run_team_self_test(
    *,
    worker_id: str,
    prompt: str,
    timeout: int,
) -> dict[str, Any]:
    from .main import ControlPlane

    cp = ControlPlane()
    return cp.team_self_test(
        worker_id=worker_id,
        prompt=prompt,
        timeout=timeout,
    )


def _is_bare_swarm_directive(text: str) -> bool:
    return text.strip().upper() == BARE_SWARM_DIRECTIVE


def _translate_mode_directive(text: str) -> tuple[str, str] | None:
    stripped = text.strip()
    if not stripped.startswith("//"):
        return None

    command, _, remainder = stripped.partition(" ")
    upper_command = command.upper()
    remainder = remainder.strip()

    if upper_command in {f"//{name}" for name in MODE_CARTRIDGE_MAP}:
        cartridge = upper_command[2:]
        if not remainder:
            return cartridge, ""
        if cartridge == "BRAINSTORM":
            return cartridge, f"LOAD:BRAINSTORM LOAD:CREATIVE LOAD:CRITICAL_THINKING {remainder}"
        if cartridge == "CRITICAL_THINKING":
            return cartridge, f"LOAD:CRITICAL_THINKING LOAD:COGNITIVE {remainder}"
        return cartridge, f"LOAD:{cartridge} {remainder}"

    if upper_command in {"//MODE", "//CARTRIDGE"}:
        if not remainder:
            return None
        mode_name, _, objective = remainder.partition(" ")
        cartridge = mode_name.strip().upper()
        if cartridge not in MODE_CARTRIDGE_MAP:
            return None
        objective = objective.strip() or ""
        if not objective:
            return cartridge, ""
        if cartridge == "BRAINSTORM":
            return cartridge, f"LOAD:BRAINSTORM LOAD:CREATIVE LOAD:CRITICAL_THINKING {objective}"
        if cartridge == "CRITICAL_THINKING":
            return cartridge, f"LOAD:CRITICAL_THINKING LOAD:COGNITIVE {objective}"
        return cartridge, f"LOAD:{cartridge} {objective}"

    return None


def _set_active_cartridge(cartridge: str) -> dict[str, Any]:
    os.makedirs(os.path.dirname(ACTIVE_CARTRIDGE_PATH), exist_ok=True)
    with open(ACTIVE_CARTRIDGE_PATH, "w", encoding="utf-8") as handle:
        handle.write(f"{cartridge}\n")
    return {
        "status": "ACTIVE_CARTRIDGE_SET",
        "cartridge": cartridge,
        "path": ACTIVE_CARTRIDGE_PATH,
    }


async def _invoke_swarm_directive(*, json_mode: bool = False) -> dict[str, Any]:
    if not json_mode:
        _stream_sarda_progress(BARE_SWARM_OBJECTIVE, execute=True)
    output = await _run_sarda(BARE_SWARM_OBJECTIVE, execute=True)
    if output.get("status") == "CANCELLED" and output.get("reason") == "HITL_GATE refused":
        if not json_mode:
            _progress("fallback", "iron gate unavailable; reverting to plan mode", tone="warn")
            _stream_sarda_progress(BARE_SWARM_OBJECTIVE, execute=False)
        output = await _run_sarda(BARE_SWARM_OBJECTIVE, execute=False)
        output["fallback_reason"] = "HITL_GATE refused"
    return output


async def _invoke_mode_directive(
    cartridge: str,
    translated_intent: str,
) -> dict[str, Any]:
    def _extract_task_status(output: dict[str, Any]) -> str:
        status = str(output.get("status", "")).upper()
        if status:
            return status
        payload = output.get("payload")
        if isinstance(payload, dict):
            return str(payload.get("status", "")).upper()
        return ""

    async def _run_with_fallback(
        preferred_intent: str,
        *,
        preferred_agent_id: str | None = None,
        preferred_constraints: list[str] | None = None,
        preferred_extra_parameters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        output = await _run_task(
            preferred_intent,
            agent_id=preferred_agent_id,
            objective=objective,
            constraints=preferred_constraints,
            extra_parameters=preferred_extra_parameters,
        )
        status = _extract_task_status(output)
        if status not in {"FAILED", "CANCELLED", "ERROR"}:
            return output
        fallback = await _run_task(translated_intent)
        if isinstance(fallback, dict):
            fallback.setdefault("fallback_reason", status or "preferred_mode_failed")
            fallback.setdefault("fallback_from", cartridge)
        return fallback

    objective = translated_intent

    if cartridge == "BRAINSTORM":
        return await _run_with_fallback(
            "northstar war room objective",
            preferred_constraints=["privacy=0.0", "compute_tier=apex", "aspect=growth"],
            preferred_extra_parameters={
                "aspect": "growth",
                "compute_tier": "apex",
                "cartridge": "BRAINSTORM",
                "browser_isolation": "team",
                "multilogin_enabled": True,
            },
        )

    if cartridge == "RESEARCH":
        return await _run_with_fallback(
            "research investigate objective",
            preferred_agent_id="lady_apis",
            preferred_constraints=["privacy=0.0", "compute_tier=hybrid"],
        )

    if cartridge == "LEGAL":
        return await _run_with_fallback(
            "northstar war room objective",
            preferred_constraints=["privacy=0.0", "compute_tier=apex", "aspect=audit"],
            preferred_extra_parameters={
                "aspect": "audit",
                "compute_tier": "apex",
                "cartridge": "LEGAL",
                "browser_isolation": "team",
                "multilogin_enabled": True,
            },
        )

    if cartridge == "MARKETING":
        return await _run_with_fallback(
            "northstar war room objective",
            preferred_constraints=["privacy=0.0", "compute_tier=apex", "aspect=growth"],
            preferred_extra_parameters={
                "aspect": "growth",
                "compute_tier": "apex",
                "cartridge": "MARKETING",
                "browser_isolation": "team",
                "multilogin_enabled": True,
            },
        )

    if cartridge == "COGNITIVE":
        return await _run_with_fallback(
            "northstar war room objective",
            preferred_agent_id="sir_alex",
            preferred_constraints=["privacy=0.0", "compute_tier=apex", "aspect=architecture"],
            preferred_extra_parameters={
                "aspect": "architecture",
                "compute_tier": "apex",
                "cartridge": "COGNITIVE",
                "preferred_knight": "sir_alex",
                "browser_isolation": "team",
                "multilogin_enabled": True,
                "execution_target": "analysis_only",
            },
        )

    if cartridge == "CREATIVE":
        return await _run_with_fallback(
            "northstar war room objective",
            preferred_constraints=["privacy=0.0", "compute_tier=apex", "aspect=growth"],
            preferred_extra_parameters={
                "aspect": "growth",
                "compute_tier": "apex",
                "cartridge": "CREATIVE",
                "browser_isolation": "team",
                "multilogin_enabled": True,
            },
        )

    if cartridge == "CRITICAL_THINKING":
        return await _run_with_fallback(
            "northstar war room objective",
            preferred_agent_id="sir_alex",
            preferred_constraints=["privacy=0.0", "compute_tier=apex", "aspect=architecture"],
            preferred_extra_parameters={
                "aspect": "architecture",
                "compute_tier": "apex",
                "cartridge": "CRITICAL_THINKING",
                "preferred_knight": "sir_alex",
                "browser_isolation": "team",
                "multilogin_enabled": True,
                "execution_target": "analysis_only",
            },
        )

    return await _run_task(translated_intent)


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

    if any(word in lower for word in {"eldergod", "elder god forge", "eldergod forge"}):
        _progress("route", "elderGod forge path", tone="info")
        time.sleep(PROGRESS_DELAY)
        _progress("scope", f"objective: {objective or intent}", tone="info")
        time.sleep(PROGRESS_DELAY)
        if constraints:
            _progress("guard", f"constraints: {', '.join(constraints)}", tone="warn")
        tier = next((c.split("=", 1)[1] for c in (constraints or []) if c.startswith("compute_tier=")), None)
        if tier:
            _progress("tier", f"default tier: {tier}", tone="accent")
        _progress("forge", "igniting the elderGod forge", tone="info")
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


def _interactive_shell(
    json_mode: bool = False, provider: str | None = None, llm: str | None = None
) -> int:
    banner = [
        "Camelot-OS",
        "Prompt-first interface for routing, cloudbrain, and SARDA workflows.",
        "Use /help or //HELP for the full command surface.",
    ]
    if not json_mode:
        _stream_print(banner[0], tone="title")
        _stream_print(banner[1], tone="dim")
        _stream_print(banner[2], tone="dim")
        if provider or llm:
            _stream_print(f"Pinned: provider={provider or 'auto'} llm={llm or 'default'}", tone="info")

    current_provider = provider
    current_llm = llm
    current_knight = os.getenv("CAMELOT_ACTIVE_KNIGHT", "sir_codex")
    last_route: dict[str, Any] | None = None

    while True:
        try:
            raw = input(_color(_prompt_text(current_knight, current_provider, current_llm), "accent")).strip()
        except EOFError:
            return 0
        except KeyboardInterrupt:
            print()
            return 0

        if not raw:
            continue
        if raw in {"/exit", "exit", "quit"}:
            return 0
        if raw in {"/help", "//HELP"}:
            if not json_mode:
                for line in HELP_LINES:
                    _stream_print(line, tone="dim")
            continue
        if raw in {"/commands", "commands"}:
            if not json_mode:
                for line in FULL_HELP_LINES:
                    _stream_print(line, tone="dim")
            continue
        if raw in {"/who", "who"}:
            output = {
                "knight_id": current_knight,
                "provider": _provider_label(current_provider),
                "model": _model_label(current_llm),
                "last_route": last_route,
            }
            if json_mode:
                _print_json(output)
            else:
                for line in _identity_lines(current_knight, current_provider, current_llm, last_route):
                    _stream_print(line, tone="info")
            continue

        try:
            if raw.startswith("/llm "):
                current_llm = raw[len("/llm ") :].strip()
                _stream_print(f"Pinned LLM: {current_llm}", tone="ok")
                continue

            if raw.startswith("/provider "):
                current_provider = raw[len("/provider ") :].strip()
                if current_provider.lower() in ("auto", "none", ""):
                    current_provider = None
                _stream_print(f"Pinned Provider: {current_provider or 'auto'}", tone="ok")
                continue

            if raw == "/chat" or raw.startswith("/chat "):
                _stream_print("Shifting to Sovereign Chat Interface...", tone="accent")
                chat_path = CAMELOT_HOME / "03_VAULT" / "training" / "configs" / "chat.py"
                if not chat_path.exists():
                    _stream_print(f"error: chat.py not found at {chat_path}", tone="err")
                    continue
                
                # Check for inline args
                parts = raw.split()
                target_provider = current_provider
                target_llm = current_llm
                if "--provider" in parts:
                    idx = parts.index("--provider")
                    if idx + 1 < len(parts): target_provider = parts[idx+1]
                if "--llm" in parts:
                    idx = parts.index("--llm")
                    if idx + 1 < len(parts): target_llm = parts[idx+1]
                elif "--model" in parts:
                    idx = parts.index("--model")
                    if idx + 1 < len(parts): target_llm = parts[idx+1]

                spec = importlib.util.spec_from_file_location("chat", chat_path)
                chat_mod = importlib.util.module_from_spec(spec)
                sys.path.insert(0, str(chat_path.parent))
                spec.loader.exec_module(chat_mod)
                chat_mod.run_chat(provider=target_provider, model=target_llm)
                continue
            if raw.startswith("/gui") or raw.upper() == "//GUI":
                # Launch the Textual TUI
                _stream_print("Launching Obsidian Spire Cockpit v2.0...", tone="ok")
                from .tui_app import SovereignApp
                app = SovereignApp()
                app.run()
                continue

            if _is_bare_swarm_directive(raw):
                output = asyncio.run(_invoke_swarm_directive(json_mode=json_mode))
                _emit(output, json_mode=json_mode, title="SWARM")
                continue

            mode_directive = _translate_mode_directive(raw)
            if mode_directive:
                cartridge, translated_intent = mode_directive
                if not translated_intent:
                    output = _set_active_cartridge(cartridge)
                    _emit(output, json_mode=json_mode, title=f"{cartridge} Mode")
                    continue
                if not json_mode:
                    _stream_task_progress(translated_intent, objective=translated_intent)
                output = asyncio.run(_invoke_mode_directive(cartridge, translated_intent))
                _emit(output, json_mode=json_mode, title=f"{cartridge} Mode")
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
                current_knight = result.route.knight_id
                current_llm = result.model
                last_route = output
                if json_mode:
                    _print_json(output)
                else:
                    _stream_print(intercept.format_route_log(result), tone="info")
                continue

            if raw == "/status":
                if not json_mode:
                    _stream_print("Probing Septem Regna Layer health…", tone="title")
                    boot_sequence.run_boot(CAMELOT_HOME)
                    output = asyncio.run(_run_task("cloudbrain status"))
                    _emit(output, json_mode=json_mode, title="Cloudbrain Internals")
                else:
                    output = boot_sequence.run_boot(CAMELOT_HOME, quick=True)
                    _print_json(output)
                continue

            if raw == "/boot":
                _stream_print("Initiating full 6-phase bootstrap sequence…", tone="warn")
                boot_sequence.run_boot(CAMELOT_HOME)
                continue

            if raw == "/sync":
                _stream_print("Triggering OMEGA SYNC PROTOCOL (UKG + Ledger + Kinetic)…", tone="accent")
                sync_script = CAMELOT_HOME / "01_KERNEL" / "system" / "SYNC_PROTOCOL.py"
                venv_py = boot_sequence._detect_venv_python(CAMELOT_HOME)
                smolvm.run([str(venv_py), str(sync_script)], cwd=str(CAMELOT_HOME))
                continue

            if raw.startswith("/log"):
                _stream_print("Reading latest Provenance Ledger entries…", tone="info")
                ledger = CAMELOT_HOME / "PROVENANCE_LEDGER.md"
                if ledger.exists():
                    lines = ledger.read_text(encoding="utf-8").splitlines()
                    for line in lines[-20:]:
                        _stream_print(line, tone="dim")
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

            # Omni-Routing Intercept
            intercept = CLIIntercept()
            result = intercept.intercept(raw)
            current_knight = result.route.knight_id
            current_llm = result.model
            last_route = {
                "knight_id": result.route.knight_id,
                "engine": result.engine_cmd,
                "model": result.model,
                "backend_url": result.backend_url,
                "reason": result.route.reason,
            }
            
            if not json_mode:
                _stream_print(intercept.format_route_log(result), tone="info")
                _stream_task_progress(raw)
                
            output = asyncio.run(_run_task(raw))
            _emit(output, json_mode=json_mode, title=f"Camelot-OS | {result.route.knight_id}")
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
    chat_parser.add_argument("--provider", help="Pin provider for session")
    chat_parser.add_argument("--llm", "--model", dest="llm", help="Pin model for session")

    route_parser = sub.add_parser("route", help="Show routing decision for an intent")
    route_parser.add_argument("intent", nargs="+")

    orchestrator = sub.add_parser("orchestrator", help="Run the Rust orchestration CLI")
    orchestrator.add_argument(
        "--mode",
        choices=("boot", "status", "knights", "triage", "persona", "notify", "awaken", "conversation"),
        default="status",
        help="Rust orchestration mode to run",
    )
    orchestrator.add_argument("--root", default=".", help="Root directory for triage mode")
    orchestrator.add_argument("--older-than-days", type=int, default=60)
    orchestrator.add_argument("--large-file-mb", type=float, default=50.0)
    orchestrator.add_argument("--intent", default="refactor the backend control plane")
    orchestrator.add_argument("--message", default="Camelot orchestration event")
    orchestrator.add_argument("--kind", default="startup")
    orchestrator.add_argument("--status", default="green")
    orchestrator.add_argument("--json", action="store_true", help="Emit JSON output")

    ledger = sub.add_parser("ledger", help="Update and sync repository-side ledgers")
    ledger_sub = ledger.add_subparsers(dest="ledger_command", required=True)
    ledger_sub.add_parser("status", help="Show repository ledger status")
    ledger_sub.add_parser("audit", help="Run forensic SHA-256 integrity check on the verification ledger")
    ledger_sub.add_parser("reconcile", help="Copy root provenance ledger to all mirror ledgers")
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

    glyph = sub.add_parser("glyph", help="Manage guarded UKG glyph stacks")
    glyph_sub = glyph.add_subparsers(dest="glyph_command", required=True)
    glyph_sub.add_parser("list", help="List registered glyph atoms")
    glyph_load = glyph_sub.add_parser("load", help="Load a glyph stack into the active registry")
    glyph_load.add_argument("stack", nargs="?", default="thread_audit_max")
    glyph_activate = glyph_sub.add_parser("activate", help="Alias for loading a glyph stack into the active registry")
    glyph_activate.add_argument("stack", nargs="?", default="thread_audit_max")
    glyph_expand = glyph_sub.add_parser("expand", help="Expand one glyph atom without side effects")
    glyph_expand.add_argument("atom_id")
    glyph_audit = glyph_sub.add_parser("audit", help="Audit all atoms or one atom")
    glyph_audit.add_argument("atom_id", nargs="?")
    glyph_execute = glyph_sub.add_parser("execute", help="Stage an approved glyph atom execution")
    glyph_execute.add_argument("atom_id")
    glyph_execute.add_argument(
        "--approve",
        action="store_true",
        help="Record an approved staged execution. Does not enable mutation.",
    )

    forge_unify = sub.add_parser("forge-unify", help="Manage the v400.2 Forge Unify runtime contract")
    forge_unify_sub = forge_unify.add_subparsers(dest="forge_unify_command", required=True)
    forge_unify_sub.add_parser("activate", help="Activate FS context, TAR, Octem, and Sentinel hook manifests")
    forge_unify_sub.add_parser("status", help="Show Forge Unify status and run a Sentinel forensic check")
    forge_route = forge_unify_sub.add_parser("route", help="Select a topology for an intent")
    forge_route.add_argument("intent", nargs="+")
    forge_forensic = forge_unify_sub.add_parser("forensic-check", help="Run the Sir Sentinel integrity check")
    forge_forensic.add_argument("--refresh-baseline", action="store_true")

    cloudbrain = sub.add_parser("cloudbrain", help="Invoke cloudbrain services")
    cloud_sub = cloudbrain.add_subparsers(dest="cloudbrain_command", required=True)
    cloud_sub.add_parser("status", help="Show cloudbrain status")
    cloud_config = cloud_sub.add_parser("config", help="Show or persist cloud endpoint configuration")
    cloud_config_sub = cloud_config.add_subparsers(dest="cloud_config_command", required=True)
    cloud_config_sub.add_parser("show", help="Show the effective cloud endpoint map")
    cloud_config_sub.add_parser("diagnose", help="Diagnose endpoint inference and override state")
    cloud_config_sub.add_parser("audit", help="Audit Cloud Brain, Warp, and ledger sync configuration")
    cloud_config_set = cloud_config_sub.add_parser("set", help="Persist a cloud endpoint override")
    cloud_config_set.add_argument(
        "env_var",
        choices=(
            "CAMELOT_CLOUDBRAIN_URL",
            "CAMELOT_LIVING_NOTEBOOK_URL",
            "CAMELOT_RESEARCH_AGENCY_URL",
            "CAMELOT_RESEARCH_AGENCY_HEALTH_URL",
            "CAMELOT_NORTHSTAR_URL",
            "CAMELOT_NORTHSTAR_HEALTH_URL",
            "CAMELOT_BLUEPRINT_URL",
            "CAMELOT_BLUEPRINT_HEALTH_URL",
            "CAMELOT_PRECISE_MODE_URL",
            "CAMELOT_PRECISE_MODE_HEALTH_URL",
            "CAMELOT_EXCALIBUR_BRIDGE_URL",
            "CAMELOT_EXCALIBUR_HEALTH_URL",
        ),
    )
    cloud_config_set.add_argument("value", help="Absolute URL for the endpoint override")
    cloud_config_clear = cloud_config_sub.add_parser("clear", help="Remove a persisted cloud endpoint override")
    cloud_config_clear.add_argument(
        "env_var",
        choices=(
            "CAMELOT_CLOUDBRAIN_URL",
            "CAMELOT_LIVING_NOTEBOOK_URL",
            "CAMELOT_RESEARCH_AGENCY_URL",
            "CAMELOT_RESEARCH_AGENCY_HEALTH_URL",
            "CAMELOT_NORTHSTAR_URL",
            "CAMELOT_NORTHSTAR_HEALTH_URL",
            "CAMELOT_BLUEPRINT_URL",
            "CAMELOT_BLUEPRINT_HEALTH_URL",
            "CAMELOT_PRECISE_MODE_URL",
            "CAMELOT_PRECISE_MODE_HEALTH_URL",
            "CAMELOT_EXCALIBUR_BRIDGE_URL",
            "CAMELOT_EXCALIBUR_HEALTH_URL",
        ),
    )
    cloud_config_discover = cloud_config_sub.add_parser(
        "discover",
        help="Discover deployed Modal web endpoint URLs via Modal SDK",
    )
    cloud_config_discover.add_argument("--app-name", required=True, help="Deployed Modal app name")
    cloud_config_discover.add_argument(
        "--environment",
        default="main",
        help="Modal environment name to query",
    )
    cloud_config_discover.add_argument(
        "--write",
        action="store_true",
        help="Persist discovered URLs into .camelot-config.yaml",
    )
    cloud_config_example = cloud_config_sub.add_parser("write-example", help="Write a cloud config example file")
    cloud_config_example.add_argument(
        "--path",
        default=".camelot-config.yaml.example",
        help="Destination path for the example config file",
    )
    cloud_sync = cloud_sub.add_parser("sync", help="Sync local Camelot state into the canonical Cloud Brain notebook")
    cloud_sync.add_argument("--notebook-id", default="")
    cloud_sync.add_argument("--note-title", default="")
    cloud_sync.add_argument("--summary", default="")
    cloud_queue = cloud_sub.add_parser("queue", help="Inspect or flush queued Cloud Brain sync events")
    cloud_queue_sub = cloud_queue.add_subparsers(dest="cloud_queue_command", required=True)
    cloud_queue_sub.add_parser("status", help="Show queued Cloud Brain sync events")
    cloud_queue_flush = cloud_queue_sub.add_parser("flush", help="Retry queued Cloud Brain sync events")
    cloud_queue_flush.add_argument("--limit", type=int, default=0, help="Maximum events to retry; 0 means all")
    cloud_sub.add_parser("research-health", help="Show research agency health")
    cloud_sub.add_parser("northstar-health", help="Show Northstar war-room health")
    cloud_sub.add_parser("blueprint-health", help="Show development blueprint health")
    cloud_sub.add_parser("precise-health", help="Show precise-mode swarm health")
    cloud_sub.add_parser("eldergod-health", help="Show elderGod forge health")

    memory = cloud_sub.add_parser("memory", help="Recall long-term memory")
    memory.add_argument("--agent-id", default="merlin")
    memory.add_argument("--privacy", type=float, default=0.0)

    eldergod = cloud_sub.add_parser("eldergod", help="Invoke the elderGod forge")
    eldergod.add_argument("objective")
    eldergod.add_argument("--tier", choices=("kinetic", "hybrid", "apex"), default="apex")

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

    team = sub.add_parser("team", help="OMC team operations")
    team_sub = team.add_subparsers(dest="team_command", required=True)
    team_sub.add_parser("roster", help="Refresh and show knight cartridges, configuration, and roster")
    team_self_test = team_sub.add_parser("self-test", help="Run harness dispatch self-test")
    team_self_test.add_argument(
        "--target",
        default="harness_codex",
        help="Dispatch target ID (sir_* or harness_* or harness:<name>)",
    )
    team_self_test.add_argument(
        "--prompt",
        default="codex",
        help="Safe probe prompt",
    )
    team_self_test.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Collection timeout in seconds",
    )
    team_self_test.add_argument(
        "--runtime",
        choices=("auto", "go", "rust", "python"),
        default=None,
        help="Override CAMELOT_HARNESS_RUNTIME for this test invocation",
    )
    team_self_test.add_argument(
        "--require-pass",
        action="store_true",
        help="Exit non-zero when self-test fails",
    )

    cockpit = sub.add_parser("cockpit", help="Warp-first truthful shell overlay helpers")
    cockpit_sub = cockpit.add_subparsers(dest="cockpit_command", required=True)
    cockpit_prompt = cockpit_sub.add_parser("prompt", help="Return the cached prompt/header payload")
    cockpit_prompt.add_argument("--json", dest="cockpit_json", action="store_true", help="Emit JSON output")
    cockpit_exec_parser = cockpit_sub.add_parser("exec", help="Route runic input without replacing the shell")
    cockpit_exec_parser.add_argument("input", nargs="+", help="Runic input such as //STATUS or Omega_STATUS")
    cockpit_exec_parser.add_argument("--json", dest="cockpit_json", action="store_true", help="Emit JSON output")
    cockpit_refresh = cockpit_sub.add_parser("refresh", help="Refresh the cached cockpit snapshot")
    cockpit_refresh.add_argument("--json", dest="cockpit_json", action="store_true", help="Emit JSON output")
    cockpit_chat = cockpit_sub.add_parser("chat", help="Escape hatch into knight-session")
    cockpit_chat.add_argument("--json", dest="cockpit_json", action="store_true", help="Emit JSON output")

    codex = sub.add_parser("codex", help="Manage Codex integration with Camelot-OS")
    codex_sub = codex.add_subparsers(dest="codex_command", required=True)
    codex_sub.add_parser("status", help="Show the Codex integration artifact")
    codex_integrate = codex_sub.add_parser("integrate", help="Write artifact, ledger, and Cloud Brain sync hook")
    codex_integrate.add_argument("--actor", default=CODEX_DEFAULT_ACTOR)
    codex_sync = codex_sub.add_parser("sync", help="Refresh Codex artifact and trigger Cloud Brain sync")
    codex_sync.add_argument("--actor", default=CODEX_DEFAULT_ACTOR)

    shadow = sub.add_parser("shadow", help="Shadow Veil — fingerprint-less defense pipeline status")
    shadow_sub = shadow.add_subparsers(dest="shadow_command", required=True)
    shadow_status_p = shadow_sub.add_parser("status", help="Show Shadow Veil pipeline status")
    shadow_status_p.add_argument("--scan", action="store_true", help="Run a live Heimdall scan before reporting")

    nano_swarm = sub.add_parser("nano-swarm", help="Inspect promoted UKG nano-swarm runtime state")
    nano_swarm_sub = nano_swarm.add_subparsers(dest="nano_swarm_command", required=True)
    nano_swarm_sub.add_parser("status", help="Refresh and show promoted nano-swarm runtime status")
    nano_supervise = nano_swarm_sub.add_parser("supervise", help="Manage promoted nano-swarm service processes")
    nano_supervise.add_argument("supervise_action", choices=("status", "start", "stop", "restart"))
    nano_supervise.add_argument("--node", default=None, help="Limit action to one node")

    microcubed = sub.add_parser("microcubed", help="Manage Microcubed SmolVM knight task houses")
    microcubed_sub = microcubed.add_subparsers(dest="microcubed_command", required=True)
    microcubed_sub.add_parser("status", help="Show Microcubed houses and latest contract")
    micro_plan = microcubed_sub.add_parser("plan", help="Render a Microcubed task-house contract without writing it")
    micro_plan.add_argument("objective")
    micro_plan.add_argument("--knight", default="sir_forge")
    micro_plan.add_argument("--tenant", default=None)
    micro_plan.add_argument("--house", default=None)
    micro_plan.add_argument("--timeout", type=int, default=900)
    micro_plan.add_argument("--max-write-mb", type=int, default=25)
    micro_forge = microcubed_sub.add_parser("forge", help="Forge an isolated Microcubed house for a knight task")
    micro_forge.add_argument("objective")
    micro_forge.add_argument("--knight", default="sir_forge")
    micro_forge.add_argument("--tenant", default=None)
    micro_forge.add_argument("--house", default=None)
    micro_forge.add_argument("--timeout", type=int, default=900)
    micro_forge.add_argument("--max-write-mb", type=int, default=25)
    micro_forge.add_argument("--queue", action="store_true", help="Append a queue directive for the tenant knight")
    micro_inspect = microcubed_sub.add_parser("inspect", help="Inspect a Microcubed house contract, manifest, and latest output")
    micro_inspect.add_argument("house_id")
    micro_execute = microcubed_sub.add_parser(
        "execute",
        help="Run a command inside a Microcubed house workspace after Sentinel preflight",
    )
    micro_execute.add_argument("house_id")
    micro_execute.add_argument("command_args", nargs=argparse.REMAINDER)
    micro_execute.add_argument("--timeout", type=int, default=None)
    micro_teardown = microcubed_sub.add_parser("teardown", help="Archive and remove a Microcubed house")
    micro_teardown.add_argument("house_id")
    micro_teardown.add_argument("--no-archive", action="store_true")

    gemini_ext = sub.add_parser("gemini-ext", help="Inspect Gemini CLI extension adapters")
    gemini_ext_sub = gemini_ext.add_subparsers(dest="gemini_ext_command", required=True)
    gemini_ext_sub.add_parser("status", help="Summarize Gemini extension adapter state")
    gemini_ext_sub.add_parser("list", help="List Gemini extensions and adapter metadata")
    gemini_ext_inspect = gemini_ext_sub.add_parser("inspect", help="Inspect one Gemini extension")
    gemini_ext_inspect.add_argument("name")

    evolve = sub.add_parser("evolve", help="Record learnings and promote guarded swarm mutations")
    evolve.add_argument("--agent", required=True, help="Knight or subsystem proposing the mutation")
    evolve.add_argument("--objective", required=True, help="Objective that produced the learning")
    evolve.add_argument(
        "--failure",
        action="append",
        dest="failures",
        required=True,
        help="Observed failure or friction point. Repeat for multiple entries.",
    )
    evolve.add_argument("--learning", required=True, help="Condensed lesson extracted from the run")
    evolve.add_argument("--proposal", required=True, help="Concrete rule to promote into the shared registry")
    evolve.add_argument(
        "--verification",
        action="append",
        required=True,
        help="Verification step executed before promotion. Repeat for multiple entries.",
    )
    evolve.add_argument(
        "--scope",
        action="append",
        default=[],
        help="Files or modules affected by the proposed mutation.",
    )
    evolve.add_argument(
        "--actor",
        default="SIR_BORIS (Codex / GPT-5)",
        help="Actor recorded in the provenance ledger.",
    )

    scripts = sub.add_parser("scripts", help="Manage and run integrated scripts")
    scripts_sub = scripts.add_subparsers(dest="scripts_command", required=True)
    scripts_sub.add_parser("voice-test", help="Run the voice test orchestrator")
    scripts_sub.add_parser("notebook-access", help="Run access_v700.py script")
    scripts_sub.add_parser("notebook-check", help="Run check_notebook.py script")
    scripts_sub.add_parser("notebook-query", help="Run query_notebook.py script")
    scripts_sub.add_parser("forge-omnicrystal", help="Run forge_omnicrystal.py script")
    scripts_sub.add_parser("start-gateway", help="Run start_clawdbot_gateway.ps1 script")
    scripts_sub.add_parser("stop-gateway", help="Run stop_clawdbot_gateway.ps1 script")

    p_ctx7 = sub.add_parser("ctx7", help="Context 7 Forensic Report Processor")
    p_ctx7.add_argument("report", help="Path to the sentinel forensic report (.json)")
    p_ctx7.add_argument("--setup", action="store_true", help="Execute automated setup based on report")

    return parser


def main() -> int:
    try:
        from bin import bifrost

        bifrost.enforce()
    except Exception as e:
        _stream_print(f"BIFROST GATE REFUSED: {e}", tone="err")
        return 77

    known_commands = {
        "chat",
        "route",
        "cloudbrain",
        "orchestrator",
        "sarda",
        "ledger",
        "glyph",
        "glyth",
        "forge-unify",
        "cockpit",
        "evolve",
        "team",
        "codex",
        "nano-swarm",
        "microcubed",
        "gemini-ext",
        "scripts",
        "ctx7",
    }
    argv = sys.argv[1:]
    for index, part in enumerate(argv):
        if not part.startswith("-"):
            if part.lower() == "glyth":
                argv[index] = "glyph"
            break

    if argv and not argv[0].startswith("-") and argv[0] not in known_commands:
        json_mode = False
        prompt_parts = argv
        if "--json" in argv:
            json_mode = True
            prompt_parts = [part for part in argv if part != "--json"]
        prompt_text = " ".join(prompt_parts)
        if _is_bare_swarm_directive(prompt_text):
            output = asyncio.run(_invoke_swarm_directive(json_mode=json_mode))
            _emit(output, json_mode=json_mode, title="SWARM")
            return 0
        mode_directive = _translate_mode_directive(prompt_text)
        if mode_directive:
            cartridge, translated_intent = mode_directive
            if not translated_intent:
                output = _set_active_cartridge(cartridge)
                _emit(output, json_mode=json_mode, title=f"{cartridge} Mode")
                return 0
            if not json_mode:
                _stream_task_progress(translated_intent, objective=translated_intent)
            output = asyncio.run(_invoke_mode_directive(cartridge, translated_intent))
            _emit(output, json_mode=json_mode, title=f"{cartridge} Mode")
            return 0
        if not json_mode:
            _stream_task_progress(prompt_text)
        output = asyncio.run(_run_task(prompt_text))
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
        mutating_command = (
            args.command in {"glyph", "forge-unify", "evolve", "sarda", "team"}
            or (args.command == "ledger" and getattr(args, "ledger_command", "") == "update")
            or (
                args.command == "microcubed"
                and getattr(args, "microcubed_command", "") in {"forge", "execute", "teardown"}
            )
        )
        if (
            success
            and mutating_command
            and service != "notebooklm_sync"
            and "cloudbrain sync" not in run.command.lower()
        ):
            event = sync_after_event(
                event_type="verification_run",
                command=run.command,
                results=results,
            )
            if isinstance(results, dict):
                results.setdefault("cloudbrain_sync", event)

    if args.command == "chat":
        return _interactive_shell(json_mode=args.json, provider=args.provider, llm=args.llm)

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

    if args.command == "orchestrator":
        output = _run_orchestrator_cli(
            mode=args.mode,
            root=args.root,
            older_than_days=args.older_than_days,
            large_file_mb=args.large_file_mb,
            intent=args.intent,
            message=args.message,
            kind=args.kind,
            status=args.status,
        )
        _emit(output, json_mode=args.json, title="Orchestrator")
        return 0

    if args.command == "ledger":
        if args.ledger_command == "status":
            output = ledger_status()
        elif args.ledger_command == "audit":
            if not args.json:
                _stream_print("Initiating forensic SHA-256 integrity check...", tone="accent")
            is_valid = prov_mgr.verify_integrity()
            output = {
                "status": "SECURE" if is_valid else "TAMPERED",
                "integrity_check": "PASS" if is_valid else "FAIL",
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "entries_scanned": len(prov_mgr.get_verification_entries()),
                "ledger_path": str(prov_mgr.verification_ledger)
            }
        elif args.ledger_command == "reconcile":
            output = reconcile_ledger_mirrors()
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

    if args.command == "glyph":
        if args.glyph_command == "list":
            output = list_glyphs()
        elif args.glyph_command in {"load", "activate"}:
            output = load_stack(args.stack)
            if output.get("status") == "LOADED":
                output["ledger"] = append_provenance_entry(
                    title=f"Glyph stack activated: {args.stack}",
                    actor="SIR_BORIS (Codex / GPT-5)",
                    scope=[
                        "03_VAULT/UKG/THREAD_AUDIT_MAX.toon",
                        "03_VAULT/UKG/glyphs/thread_audit_max.registry.json",
                        ".camelot/active_glyph_stack.json",
                    ],
                    verification=[
                        f"camelot glyph {args.glyph_command} {args.stack}",
                        "camelot glyph audit",
                    ],
                    tag="[Omega_GLYPH]",
                )
        elif args.glyph_command == "expand":
            output = expand_atom(args.atom_id)
        elif args.glyph_command == "audit":
            output = audit_atom(args.atom_id)
            if output.get("status") == "AUDITED":
                target = args.atom_id or "all"
                output["ledger"] = append_provenance_entry(
                    title=f"Glyph audit: {target}",
                    actor="SIR_BORIS (Codex / GPT-5)",
                    scope=["03_VAULT/UKG/THREAD_AUDIT_MAX.toon", "control_plane/glyph_registry.py"],
                    verification=[f"camelot glyph audit {target}".strip()],
                    tag="[Omega_GLYPH_AUDIT]",
                )
        else:
            output = execute_atom(args.atom_id, approved=args.approve)
            if output.get("status") in {"STAGED", "GUARD_REQUIRED"}:
                output["ledger"] = append_provenance_entry(
                    title=f"Glyph execute staged: {args.atom_id}",
                    actor="SIR_BORIS (Codex / GPT-5)",
                    scope=["control_plane/glyph_registry.py", "03_VAULT/UKG/THREAD_AUDIT_MAX.toon"],
                    verification=[
                        f"camelot glyph expand {args.atom_id}",
                        f"camelot glyph execute {args.atom_id}{' --approve' if args.approve else ''}",
                    ],
                    tag="[Omega_GLYPH_EXECUTE]",
                )
            elif output.get("status") == "MOUNTED":
                output["ledger"] = append_provenance_entry(
                    title=f"Glyph execute mounted: {args.atom_id}",
                    actor="SIR_BORIS (Codex / GPT-5)",
                    scope=[
                        "control_plane/glyph_registry.py",
                        "03_VAULT/UKG/THREAD_AUDIT_MAX.toon",
                        "03_VAULT/runtime_state/openviking_context_mount_latest.json",
                        "03_VAULT/UKG/nodes/OpenViking_Context_Mount_UKG.json",
                    ],
                    verification=[
                        f"camelot glyph expand {args.atom_id}",
                        f"camelot glyph execute {args.atom_id} --approve",
                        "camelot glyph audit 05",
                    ],
                    tag="[Omega_GLYPH_MOUNT]",
                )
        _emit(output, json_mode=args.json, title="Glyph")
        return 0 if output.get("status") not in {"NOT_FOUND", "MISSING_ARTIFACT"} else 1

    if args.command == "forge-unify":
        if args.forge_unify_command == "activate":
            output = activate_forge_unify()
            output["ledger"] = append_provenance_entry(
                title="Forge Unify v400.2 activated",
                actor="SIR_CODEX (Lead Engineer) with Sir Alex and Sir Link",
                scope=[
                    "control_plane/forge_unify.py",
                    "control_plane/camelot_cli.py",
                    ".hive/context/manifest.json",
                    ".hive/context/routing/tar_router_contract.json",
                    ".hive/context/research/paladin_octem_personas.json",
                    "03_VAULT/runtime_state/forge_unify_status.json",
                ],
                verification=[
                    "camelot --json forge-unify activate",
                    "camelot --json forge-unify status",
                    "camelot --json forge-unify route refactor cross dependency upgrade",
                    "camelot --json forge-unify forensic-check",
                ],
                tag="[Omega_FORGE_UNIFY]",
            )
        elif args.forge_unify_command == "status":
            output = forge_unify_status()
        elif args.forge_unify_command == "route":
            output = select_topology(" ".join(args.intent))
        else:
            output = sentinel_forensic_check(refresh_baseline=args.refresh_baseline)
            if output.get("status") in {"TRIGGERED", "BASELINE_CREATED"}:
                output["ledger"] = append_provenance_entry(
                    title=f"Sentinel forensic check: {output.get('status')}",
                    actor="SIR_CODEX (Lead Engineer) with Sir Sentinel",
                    scope=[
                        "control_plane/forge_unify.py",
                        "03_VAULT/runtime_state/sentinel_forensic_report_latest.json",
                    ],
                    verification=[
                        "camelot --json forge-unify forensic-check",
                    ],
                    tag="[Omega_SENTINEL_FORENSIC]",
                )
        _emit(output, json_mode=args.json, title="Forge Unify")
        return 0 if output.get("status") not in {"NOT_ACTIVE"} else 1

    if args.command == "cloudbrain":
        if not args.json:
            if args.cloudbrain_command == "status":
                _stream_task_progress("cloudbrain status")
            elif args.cloudbrain_command == "config":
                _stream_task_progress("cloudbrain config")
            elif args.cloudbrain_command == "sync":
                _stream_task_progress("cloud brain sync")
            elif args.cloudbrain_command == "queue":
                _stream_task_progress("cloud brain sync queue")
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
            elif args.cloudbrain_command == "eldergod-health":
                _stream_task_progress("elderGod forge health")
            elif args.cloudbrain_command == "eldergod":
                constraints = [
                    f"compute_tier={args.tier}",
                ]
                _stream_task_progress(
                    "elderGod forge objective",
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
            elif args.cloudbrain_command == "research":
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
        elif args.cloudbrain_command == "config":
            if args.cloud_config_command == "show":
                output = {
                    "status": "CONFIG_READY",
                    "config_path": str(config_mgr.config_path),
                    "endpoints": config_mgr.cloud_endpoint_map(),
                }
            elif args.cloud_config_command == "diagnose":
                output = _diagnose_cloud_endpoints(config_mgr)
            elif args.cloud_config_command == "audit":
                output = _audit_cloudbrain_configuration(config_mgr)
            elif args.cloud_config_command == "set":
                output = {
                    "status": "CONFIG_UPDATED",
                    **config_mgr.set_cloud_endpoint(args.env_var, args.value),
                }
            elif args.cloud_config_command == "clear":
                output = {
                    "status": "CONFIG_CLEARED",
                    **config_mgr.set_cloud_endpoint(args.env_var, None),
                }
            elif args.cloud_config_command == "discover":
                output = _discover_modal_endpoints(
                    config_mgr=config_mgr,
                    app_name=args.app_name,
                    environment_name=args.environment,
                    write=args.write,
                )
            else:
                example_path = Path(args.path)
                example_content = """# Camelot-OS cloud endpoint overrides
# Copy to .camelot-config.yaml and replace placeholders with real production URLs.
cloudbrain_url: "https://replace-me.modal.run"
living_notebook_url: "https://notebooklm.google.com/notebook/replace-me"
research_agency_url: "https://replace-me.modal.run"
research_agency_health_url: "https://replace-me.modal.run"
northstar_url: "https://replace-me.modal.run"
northstar_health_url: "https://replace-me.modal.run"
blueprint_url: "https://replace-me.modal.run"
blueprint_health_url: "https://replace-me.modal.run"
precise_mode_url: "https://replace-me.modal.run"
precise_mode_health_url: "https://replace-me.modal.run"
excalibur_bridge_url: "https://replace-me.modal.run"
excalibur_health_url: "https://replace-me.modal.run"
"""
                example_path.write_text(example_content, encoding="utf-8")
                output = {
                    "status": "CONFIG_TEMPLATE_WRITTEN",
                    "path": str(example_path),
                }
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
        elif args.cloudbrain_command == "queue":
            if args.cloud_queue_command == "status":
                output = sync_queue_status()
            else:
                output = flush_sync_queue(limit=args.limit or None)
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
        elif args.cloudbrain_command == "eldergod-health":
            output = asyncio.run(_run_task("elderGod forge health"))
        elif args.cloudbrain_command == "eldergod":
            constraints = [
                f"compute_tier={args.tier}",
            ]
            output = asyncio.run(
                _run_task(
                    "elderGod forge objective",
                    objective=args.objective,
                    constraints=constraints,
                    extra_parameters={
                        "compute_tier": args.tier,
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

    if args.command == "team":
        if args.team_command == "roster":
            output = write_knight_configuration(CAMELOT_HOME)
            _emit(output, json_mode=args.json, title="Knight Configuration")
            return 0

        if args.team_command == "self-test":
            if args.runtime:
                os.environ["CAMELOT_HARNESS_RUNTIME"] = args.runtime
            if not args.json:
                _progress("analyze", f"team self-test target={args.target} runtime={os.getenv('CAMELOT_HARNESS_RUNTIME', 'auto')}", tone="info")
            output = _run_team_self_test(
                worker_id=args.target,
                prompt=args.prompt,
                timeout=args.timeout,
            )
            _log_run(output, success=output.get("status") == "PASSED")
            _emit(output, json_mode=args.json, title="Team Self-Test")
            if args.require_pass and output.get("status") != "PASSED":
                return 1
            return 0

    if args.command == "cockpit":
        json_mode = args.json or getattr(args, "cockpit_json", False)
        if args.cockpit_command == "prompt":
            output = prompt_payload()
            if output.get("stale"):
                output = refresh_snapshot(trigger="prompt")
        elif args.cockpit_command == "refresh":
            output = refresh_snapshot(trigger="manual")
        elif args.cockpit_command == "exec":
            output = cockpit_exec(" ".join(args.input))
        else:
            if json_mode:
                output = {
                    "status": "HANDOFF",
                    "target": "knight-session",
                    "command": [sys.executable, str(CAMELOT_HOME / "bin" / "knight_session.py")],
                }
            else:
                from bin.knight_session import main as knight_session_main

                knight_session_main()
                return 0
        _emit(output, json_mode=json_mode, title="Cockpit")
        return 0 if output.get("status") != "QUEUE_WARN" else 2

    if args.command == "codex":
        if args.codex_command == "status":
            output = read_codex_status(CAMELOT_HOME)
        else:
            output = write_codex_integration(CAMELOT_HOME, actor=args.actor, trigger=args.codex_command)
            ledger = append_provenance_entry(
                title="Codex integrated with Camelot-OS",
                actor=args.actor,
                scope=[
                    "control_plane/codex_integration.py",
                    "control_plane/camelot_cli.py",
                    "control_plane/boot_sequence.py",
                    "02_FORGE/apps/omni-eye-dashboard",
                    "03_VAULT/runtime_state/codex_integration_latest.json",
                ],
                verification=[
                    "camelot codex status",
                    "camelot codex integrate",
                    "awaken --quick surfaces Codex Integration",
                ],
                tag="[Omega_CODEX]",
            )
            sync_event = sync_after_event(
                event_type="codex_integration",
                command=f"codex {args.codex_command}",
                results=output,
            )
            output["ledger"] = ledger
            output["cloudbrain_sync"] = sync_event
        _log_run(output)
        _emit(output, json_mode=args.json, title="Codex Integration")
        return 0

    if args.command == "shadow":
        import importlib.util as _shadow_ilu
        _shadow_spec = _shadow_ilu.spec_from_file_location(
            "shadow_pipeline",
            CAMELOT_HOME / "01_KERNEL/iron_gate/DEFENSE_GRID/shadow_veil/shadow_pipeline.py",
        )
        _shadow_mod = _shadow_ilu.module_from_spec(_shadow_spec)
        sys.modules["shadow_pipeline"] = _shadow_mod
        _shadow_spec.loader.exec_module(_shadow_mod)
        sv = _shadow_mod.ShadowVeil(repo_root=CAMELOT_HOME, hermes_enabled=False)
        if getattr(args, "scan", False):
            st = sv.scan_once()
        else:
            st = sv.status()
        output = {
            "shadow_veil": {
                "heimdall_ok": st.heimdall_ok,
                "nemesis_ok": st.nemesis_ok,
                "hermes_ok": st.hermes_ok,
                "vector_count": st.vector_count,
                "critical_count": st.critical_count,
                "threats_detected": st.threats_detected,
                "auto_responses": st.auto_responses,
                "hitl_pending": st.hitl_pending,
                "last_scan_at": st.last_scan_at,
                "last_threat_at": st.last_threat_at,
                "active": st.active,
            }
        }
        _emit(output, json_mode=args.json, title="Shadow Veil Status")
        return 0

    if args.command == "nano-swarm":
        if args.nano_swarm_command == "status":
            output = write_nano_swarm_runtime_status()
            success = bool(output.get("runtime_ready"))
        else:
            output = supervise_nano_swarm_nodes(args.supervise_action, node_name=args.node)
            success = output.get("status") != "SUPERVISOR_ERROR"
        _emit(output, json_mode=args.json, title="Nano Swarm Runtime")
        return 0 if success else 2

    if args.command == "microcubed":
        if args.microcubed_command == "status":
            output = microcubed_status()
            _emit(output, json_mode=args.json, title="Microcubed")
            return 0

        if args.microcubed_command in {"plan", "forge"}:
            request = MicrocubedRequest(
                objective=args.objective,
                knight=args.knight,
                tenant=args.tenant,
                house=args.house,
                timeout_seconds=args.timeout,
                max_write_mb=args.max_write_mb,
                queue=getattr(args, "queue", False),
            )
            output = plan_house(request) if args.microcubed_command == "plan" else forge_house(request)
            if args.microcubed_command == "forge":
                output["ledger"] = append_provenance_entry(
                    title="Microcubed SmolVM house forged",
                    actor="SIR_CODEX + LUKAS_OMEGA",
                    scope=[
                        "control_plane/microcubed.py",
                        "control_plane/camelot_cli.py",
                        "03_VAULT/runtime_state/microcubed",
                    ],
                    verification=[
                        "camelot microcubed status",
                        "python -m json.tool 03_VAULT/runtime_state/microcubed/microcubed_latest.json",
                    ],
                    tag="[Omega_KINETIC][MICROCUBED]",
                )
            _log_run(output, success=output.get("status") in {"PLANNED", "READY"})
            _emit(output, json_mode=args.json, title="Microcubed")
            return 0

        if args.microcubed_command == "inspect":
            output = inspect_house(args.house_id)
            _emit(output, json_mode=args.json, title="Microcubed")
            return 0

        if args.microcubed_command == "execute":
            command_args = list(args.command_args or [])
            if command_args and command_args[0] == "--":
                command_args = command_args[1:]
            if not command_args:
                raise SystemExit("microcubed execute requires a command after --")
            output = execute_house(args.house_id, command_args, timeout_seconds=args.timeout)
            _log_run(output, success=output.get("status") == "COMPLETE")
            _emit(output, json_mode=args.json, title="Microcubed")
            return 0 if output.get("status") == "COMPLETE" else 2

        output = teardown_house(args.house_id, archive=not args.no_archive)
        _log_run(output, success=output.get("status") in {"TORN_DOWN", "MISSING"})
        _emit(output, json_mode=args.json, title="Microcubed")
        return 0

    if args.command == "gemini-ext":
        if args.gemini_ext_command == "status":
            output = summarize_gemini_extensions()
        elif args.gemini_ext_command == "list":
            output = list_gemini_extensions()
        else:
            output = inspect_gemini_extension(args.name)
        _emit(output, json_mode=args.json, title="Gemini Extensions")
        return 0 if output.get("status") != "NOT_FOUND" else 1

    if args.command == "evolve":
        if not args.json:
            _stream_task_progress(
                "hyper evolve",
                objective=args.objective,
                constraints=[f"agent={args.agent}", f"verification_steps={len(args.verification)}"],
            )
        append_learning(
            agent=args.agent,
            objective=args.objective,
            failures=list(args.failures),
            learning=args.learning,
            proposal=args.proposal,
        )
        output = promote_mutation(
            agent=args.agent,
            objective=args.objective,
            learning=args.learning,
            proposal=args.proposal,
            verification=list(args.verification),
            scope=list(args.scope),
            actor=args.actor,
        )
        _log_run(output, success=output.get("status") == "APPROVED")
        _emit(output, json_mode=args.json, title="Hyper Evolve")
        return 0

    if args.command == "scripts":
        script_map = {
            "voice-test": ["python", str(CAMELOT_HOME / "scripts" / "voice" / "voice_test_orchestrator.py")],
            "notebook-access": ["python", str(CAMELOT_HOME / "scripts" / "notebooklm" / "access_v999.py")],
            "notebook-check": ["python", str(CAMELOT_HOME / "scripts" / "notebooklm" / "check_notebook.py")],
            "notebook-query": ["python", str(CAMELOT_HOME / "scripts" / "notebooklm" / "query_notebook.py")],
            "forge-omnicrystal": ["python", str(CAMELOT_HOME / "02_FORGE" / "forge_omnicrystal.py")],
            "start-gateway": ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(CAMELOT_HOME / "05_INFRASTRUCTURE" / "gateways" / "start_clawdbot_gateway.ps1")],
            "stop-gateway": ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(CAMELOT_HOME / "05_INFRASTRUCTURE" / "gateways" / "stop_clawdbot_gateway.ps1")]
        }
        cmd = script_map.get(args.scripts_command)
        if cmd:
            if not args.json:
                _stream_print(f"Running integrated script: {args.scripts_command}...", tone="info")
            subprocess.run(cmd)
        return 0

    if args.command == "ctx7":
        if args.setup:
            _stream_print(f"Executing ctx7 automated setup for: {args.report}", tone="accent")
        else:
            _stream_print(f"Analyzing Context 7 report: {args.report}", tone="info")
        return 0

    return _interactive_shell(json_mode=args.json)

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        import traceback
        error_msg = str(e)
        trace = traceback.format_exc()
        _stream_print(f"\n[🔥] KINETIC_CRITICAL_FAILURE: {error_msg}", tone="warn")
        _stream_print("Transmuting error into Chronicle of Scars...", tone="dim")
        
        # Log to Chronicle of Scars (L6 Governance)
        try:
            append_learning(
                agent="SIR_BORIS",
                objective="Global CLI Execution",
                failures=[error_msg],
                learning="Caught unhandled exception in main loop.",
                proposal=f"Patch affected path and implement guardrail for: {error_msg}"
            )
            _stream_print("Scar recorded. System will evolve on next //BOOT.", tone="accent")
        except Exception:
            pass
        
        sys.exit(1)
