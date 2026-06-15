# -*- coding: utf-8 -*-
"""
Runic Router — CAMELOT Command Dispatch
=========================================
P1-C. Routes all 11 runic commands + 29 Omega runes.

Entry point: route_rune(rune_str, context) -> RuneResult
Called by: anya_gate._stage_compile (detects // prefix) + camelot_cli

Rune parsing:
  //FORGE param  → intent_type=FORGE, dispatch to sir_boris with param
  Omega_SYNC     → omega dispatch table

Integration: appends to harness_queue.jsonl for async execution.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import sys
import threading
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from control_plane.taxonomy import PRIVACY_KEYWORDS

try:
    from importlib import import_module
    hydration = import_module("01_KERNEL.memory.hydration_manager")
    HydrationManager = hydration.HydrationManager
except ImportError:
    HydrationManager = None

CAMELOT_HOME = Path(__file__).parent.parent
QUEUE_FILE   = CAMELOT_HOME / "logs" / "harness_queue.jsonl"

# Rate-limit guard for _queue_task — kills runaway producers that fire the same
# (knight, directive) thousands of times per second. Tunable via env:
#   CAMELOT_ROUTER_DEDUP_WINDOW_SEC (default 10) — sliding window in seconds
#   CAMELOT_ROUTER_DEDUP_MAX        (default 5)  — max identical submits per window
#   CAMELOT_ROUTER_DEDUP_DISABLE=1               — bypass the guard entirely
_DEDUP_WINDOW_SEC = float(os.environ.get("CAMELOT_ROUTER_DEDUP_WINDOW_SEC", "10"))
_DEDUP_MAX        = int(os.environ.get("CAMELOT_ROUTER_DEDUP_MAX", "5"))
_DEDUP_DISABLED   = os.environ.get("CAMELOT_ROUTER_DEDUP_DISABLE") == "1"
_dedup_lock      = threading.Lock()
_dedup_state: dict[tuple[str, str], deque[float]] = defaultdict(deque)

# ---------------------------------------------------------------------------
# Rune tables
# ---------------------------------------------------------------------------

# 11 Runic Commands — sovereign execution runes

RUNIC_COMMANDS: dict[str, dict[str, Any]] = {
    "//FLEET": {
        "knight": "sir_boris",
        "description": "Stateful Graph-based Swarm Dispatch",
        "mode": "AGENTIC",
        "priority": 1,
        "handler": "_handle_fleet",
    },
    "//BOOT": {
        "knight": "sir_boris",
        "description": "6-phase awaken boot sequence",
        "mode": "FORGE",
        "priority": 1,
        "handler": "_handle_boot",
    },
    "//DAWNING": {
        "knight": "sir_forge",
        "description": "Global wake-up, OS map audit, Lady M sync, and project isolation",
        "mode": "FORGE",
        "priority": 1,
        "handler": "_handle_dawning",
    },
    "//FORGE": {
        "knight": "sir_forge",
        "description": "Kinetic build + compile directive",
        "mode": "KINETIC",
        "priority": 2,
        "handler": "_handle_forge",
    },
    "//CODEX": {
        "knight": "sir_codex",
        "description": "High-velocity implementation and rapid prototyping",
        "mode": "KINETIC",
        "priority": 2,
        "handler": "_handle_codex",
    },
    "//CONTRACT": {
        "knight": "sir_forge",
        "description": "Compile Camelot into a portable runtime package",
        "mode": "KINETIC",
        "priority": 2,
        "handler": "_handle_contract",
    },
    "//CLAW": {
        "knight": "sir_boris",
        "description": "Guarded Claw Suite manifest for Shopify headless AI forger workflows",
        "mode": "ORACLE",
        "priority": 2,
        "handler": "_handle_claw",
        "hydrate": False,
    },
    "//SWARM": {
        "knight": "sir_boris",
        "description": "Full hive parallel debug/optimize vote",
        "mode": "SWARM",
        "priority": 2,
        "handler": "_handle_swarm",
    },
    "//PLAN": {
        "knight": "merlin_omega",
        "description": "ToT strategic planning — outputs Plan.json",
        "mode": "ORACLE",
        "priority": 3,
        "handler": "_handle_plan",
    },
    "//HEAL": {
        "knight": "sir_debug",
        "description": "PIV self-healing — diagnose and repair",
        "mode": "FORGE",
        "priority": 2,
        "handler": "_handle_heal",
    },
    "//GENESIS": {
        "knight": "sir_boris",
        "description": "Bootstrap new project from BriefingScript template",
        "mode": "FORGE",
        "priority": 3,
        "handler": "_handle_genesis",
    },
    "//ASSIMILATE": {
        "knight": "sir_helio",
        "description": "Cloud Brain scour + CLAUDE.md enhancement",
        "mode": "ORACLE",
        "priority": 3,
        "handler": "_handle_assimilate",
    },
    "//SCAVENGE": {
        "knight": "lady_apis",
        "description": "Forage external sources for context and artifacts",
        "mode": "ORACLE",
        "priority": 3,
        "handler": "_handle_scavenge",
    },
    "//DEFENSE_INIT": {
        "knight": "sir_sentinel",
        "description": "Agent-Armor v2.0 + PDG taint initialization",
        "mode": "SENTINEL",
        "priority": 1,
        "handler": "_handle_defense_init",
    },
    "//vocal": {
        "knight": "sir_sonus",
        "description": "Voice AI pipeline — 3-phase Oracle/Veritas/Lazarus",
        "mode": "ORACLE",
        "priority": 2,
        "handler": "_handle_vocal",
    },
    "//SCAN": {
        "knight": "squire_colony",
        "description": "CLARITY_CORE squire colony codebase scan",
        "mode": "SENTINEL",
        "priority": 2,
        "handler": "_handle_scan",
    },
    "//STATUS": {
        "knight": "sir_boris",
        "description": "Live system status + port probes",
        "mode": "ORACLE",
        "priority": 1,
        "handler": "_handle_status",
    },
    "//THINK": {
        "knight": "merlin_omega",
        "description": "Deep reasoning via GoT/ToT chain",
        "mode": "ORACLE",
        "priority": 3,
        "handler": "_handle_think",
    },
    "//NANO_SWARM_EXPAND": {
        "knight": "sir_boris",
        "description": "6-phase UKG_NANO_SWARM_V1000 expansion: SAT-gate → CvRDT mesh → Ouroboros seed → Aegis bind → AST audit → Anya seal",
        "mode": "SWARM",
        "priority": 1,
        "handler": "_handle_nano_swarm_expand",
    },
    "//BIFROST_LOCK": {
        "knight": "sir_heimdall",
        "description": "Emergency Bifrost perimeter lockdown",
        "mode": "SENTINEL",
        "priority": 1,
        "handler": "_handle_bifrost_lock",
    },
    "//SCAN_VECTORS": {
        "knight": "sir_heimdall",
        "description": "Deep 4-vector fingerprint scan",
        "mode": "SENTINEL",
        "priority": 2,
        "handler": "_handle_scan_vectors",
    },
}

# 29 Omega Runes — system-level operations
OMEGA_RUNES: dict[str, dict[str, Any]] = {
    "Omega_SYNC":       {"knight": "sir_mnemo",    "description": "Dual-tier memory sync (ST+LT)"},
    "Omega_PURGE":      {"knight": "sir_forge",    "description": "Targeted purge with Iron Gate"},
    "Omega_STATUS":     {"knight": "sir_boris",    "description": "Full system status report"},
    "Omega_KINETIC":    {"knight": "lukas_omega",  "description": "Kinetic Edge binary operations"},
    "Omega_ACTUATE":    {"knight": "sir_boris",    "description": "Singularity Engine activation"},
    "Omega_REFORGE":    {"knight": "sir_forge",    "description": "Full module recompile + hotswap"},
    "Omega_AUDIT":      {"knight": "sir_sentinel", "description": "Full security audit cycle"},
    "Omega_THINK":      {"knight": "merlin_omega", "description": "Deep GoT/DoT reasoning chain"},
    "Omega_GLYPH":      {"knight": "merlin_omega", "description": "NPE TCoT formal verification"},
    "Omega_COMPRESS":   {"knight": "merlin_omega", "description": "SAC->CCF->QFT compression"},
    "Omega_SHIELD":     {"knight": "sir_sentinel", "description": "Agent-Armor PDG taint shield"},
    "Omega_KERNEL":     {"knight": "sir_boris",    "description": "Kernel-level OS operations"},
    "Omega_ORACLE":     {"knight": "merlin_omega", "description": "Oracle Hypervisor broadcast"},
    "Omega_ANYA":       {"knight": "anya_omega",   "description": "APEE v6.5 pipeline audit"},
    "Omega_BESTIARY":   {"knight": "sir_boris",    "description": "Bio-Swarm zoology report"},
    "Omega_VOICE":      {"knight": "sir_sonus",    "description": "Voice pipeline diagnostics"},
    "Omega_VISION":     {"knight": "sir_visage",   "description": "Media/image pipeline ops"},
    "Omega_COMPILE":    {"knight": "lukas_omega",  "description": "Rust/Go compilation trigger"},
    "Omega_EVOLVE":     {"knight": "lord_archivist", "description": "GEP scan + XP evolution cycle"},
    "Omega_RESEARCH":   {"knight": "lady_apis",    "description": "BASHR research loop"},
    "Omega_CLEAN":      {"knight": "sir_forge",    "description": "Cache + orphan cleanup"},
    "Omega_PERSONA":    {"knight": "sir_alex",     "description": "Persona evolution binding"},
    "Omega_SILENCE":    {"knight": "sir_sentinel", "description": "Emergency lockdown protocol"},
    "Omega_PROMETHEUS": {"knight": "sir_helio",    "description": "Cloud burst + Modal GPU"},
    "Omega_ARCHETYPE":  {"knight": "sir_alex",     "description": "Archetype pattern synthesis"},
    "Omega_GRAPH":      {"knight": "merlin_omega", "description": "UKG graph traversal + query"},
    "Omega_GATEWAY":    {"knight": "sir_link",     "description": "Switchboard gateway diagnostics"},
    "Omega_STACK":      {"knight": "sir_boris",    "description": "Full stack topology report"},
    "Omega_SCORPION":   {"knight": "sir_gideon",   "description": "Forensic GIDEON_RISK_MATRIX audit"},
    "Omega_CODEX":      {"knight": "sir_codex",    "description": "Direct SIR_CODEX execution lane"},
    "Omega_BIFROST":    {"knight": "sir_heimdall", "description": "Bifrost Sentinel operations"},
}


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class RuneResult:
    rune: str
    knight: str
    directive: str
    mode: str
    task_id: str
    queued: bool
    queue_error: Optional[str]
    metadata: dict


# ---------------------------------------------------------------------------
# Handler functions
# ---------------------------------------------------------------------------

def _rate_limit_check(knight: str, directive: str) -> Optional[str]:
    """Return an error string if (knight, directive) has been submitted more than
    _DEDUP_MAX times in the last _DEDUP_WINDOW_SEC seconds. None = allow."""
    if _DEDUP_DISABLED:
        return None
    key = (knight, directive)
    now = time.monotonic()
    cutoff = now - _DEDUP_WINDOW_SEC
    with _dedup_lock:
        dq = _dedup_state[key]
        while dq and dq[0] < cutoff:
            dq.popleft()
        if len(dq) >= _DEDUP_MAX:
            return (
                f"rate_limited: {_DEDUP_MAX}+ identical submits in "
                f"{_DEDUP_WINDOW_SEC:.0f}s window for ({knight}, {directive[:60]!r})"
            )
        dq.append(now)
    return None


def _queue_task(knight: str, directive: str, priority: int = 2) -> tuple[str, Optional[str]]:
    task_id = f"rune-{uuid.uuid4().hex[:8]}"
    rl_err = _rate_limit_check(knight, directive)
    if rl_err:
        return task_id, rl_err
    entry = {
        "id": task_id,
        "knight": knight,
        "directive": directive,
        "priority": priority,
        "submitted": datetime.now(timezone.utc).isoformat(),
    }
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(QUEUE_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        return task_id, None
    except Exception as e:
        return task_id, str(e)


def _handle_boot(param: str, context: dict) -> dict:
    return {"action": "awaken 6-phase boot", "detail": "run: python bin/awaken.py"}

def _handle_dawning(param: str, context: dict) -> dict:
    project_name = param or "default_nexus"
    quoted_project = json.dumps(project_name)
    return {
        "action": "cybertron_dawning",
        "lead_bio_knight": "lukas_forge",
        "project": project_name,
        "detail": f"run: python scripts/cybertron_dawning.py {quoted_project}",
    }

def _handle_forge(param: str, context: dict) -> dict:
    return {"action": "kinetic build", "param": param or "default target"}

def _handle_codex(param: str, context: dict) -> dict:
    return {"action": "codex_velocity_execution", "param": param or "default target"}

def _handle_contract(param: str, context: dict) -> dict:
    brief = param or "portable Camelot runtime package"
    return {
        "action": "portable_contract_build",
        "brief": brief,
        "output": "dist/camelot.exe",
        "detail": "run: python scripts/build_portable.py --test",
    }

def _handle_claw(param: str, context: dict) -> dict:
    from control_plane.claw_suite import route_claw_suite

    return route_claw_suite(param, context)

def _handle_swarm(param: str, context: dict) -> dict:
    return {"action": "srdl_map_reduce", "param": param, "bio_swarm": "Formica+Pongid+Castor"}

def _handle_plan(param: str, context: dict) -> dict:
    return {"action": "tot_planning", "output": "Plan.json", "param": param}

def _handle_heal(param: str, context: dict) -> dict:
    return {"action": "piv_self_heal", "target": param or "auto-diagnose"}

def _handle_fleet(param: str, context: dict) -> dict:
    """Route //FLEET via importlib to avoid 01_KERNEL naming restriction."""
    import importlib.util
    repo_root = Path(__file__).resolve().parent.parent
    module_path = repo_root / "01_KERNEL" / "swarm" / "graph_orchestrator.py"
    if module_path.exists():
        spec = importlib.util.spec_from_file_location("graph_orchestrator", module_path)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            try:
                sys.modules[spec.name] = mod
                spec.loader.exec_module(mod)
                orchestrator = mod.GraphOrchestrator()
                final_state = orchestrator.run(param or "Auto-Evolution Directive")
                return {
                    "action": "swarm_graph_execution",
                    "directive": param,
                    "status": final_state.get("validation_results", {}).get("status", "unknown"),
                }
            except Exception as e:
                return {"action": "fleet_dispatch", "error": str(e)}
    return {"action": "fleet_dispatch", "detail": "GraphOrchestrator not available", "param": param}

def _handle_genesis(param: str, context: dict) -> dict:
    return {"action": "project_bootstrap", "template": "BriefingScript", "name": param}

def _handle_assimilate(param: str, context: dict) -> dict:
    return {"action": "omega_assimilate", "source": "cloud_brain_scour", "target": "CLAUDE.md"}

def _handle_scavenge(param: str, context: dict) -> dict:
    return {"action": "bashr_forage", "target": param or "external corpus"}

def _handle_defense_init(param: str, context: dict) -> dict:
    return {"action": "agent_armor_v2", "pdg_rules": 4, "blocked_patterns": 8}

def _handle_vocal(param: str, context: dict) -> dict:
    return {"action": "vocal_pipeline", "phases": ["Oracle", "Veritas", "Lazarus"], "param": param}

def _handle_scan(param: str, context: dict) -> dict:
    return {"action": "squires_colony_triage", "path": param or ".", "detail": "run: python -m squires.colony triage"}

def _handle_status(param: str, context: dict) -> dict:
    return {"action": "system_status", "detail": "run: python -m control_plane.harness --status"}

def _handle_think(param: str, context: dict) -> dict:
    return {"action": "got_reasoning", "param": param, "knight": "merlin_omega"}

def _handle_bifrost_lock(param: str, context: dict) -> dict:
    return {"action": "bifrost_lockdown", "status": "AIR_GAPPED"}

def _handle_scan_vectors(param: str, context: dict) -> dict:
    return {"action": "4_vector_scan", "target": param or "project_root"}

def _handle_nano_swarm_expand(param: str, context: dict) -> dict:
    """Execute the 6-phase NANO_SWARM_EXPAND protocol via importlib."""
    import importlib.util
    script = CAMELOT_HOME / "scripts" / "nano_swarm_expand.py"
    if script.exists():
        spec = importlib.util.spec_from_file_location("nano_swarm_expand", script)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            try:
                sys.modules[spec.name] = mod
                spec.loader.exec_module(mod)
                tokens = shlex.split(param or "", posix=False)
                if tokens and tokens[0].lower() == "supervise":
                    action = tokens[1].lower() if len(tokens) > 1 else "status"
                    node_arg = None
                    for idx, token in enumerate(tokens):
                        if token == "--node" and idx + 1 < len(tokens):
                            node_arg = tokens[idx + 1]
                    from control_plane.nano_swarm_runtime import supervise_nodes

                    result = supervise_nodes(action, node_name=node_arg)
                    return {
                        "action": "nano_swarm_supervise",
                        "supervise": True,
                        **result,
                    }
                if tokens and tokens[0].lower() == "expand":
                    tokens = tokens[1:]
                node = "Node_A_Frontend"
                manifest_path = CAMELOT_HOME / "03_VAULT" / "runtime_state" / "ukg_nano_omega_glyph_v1000_omni_codex.json"
                report_dir = None
                rollback_path = None
                source_dir = None
                for idx, token in enumerate(tokens):
                    if token == "--node" and idx + 1 < len(tokens):
                        node = tokens[idx + 1]
                    elif token == "--manifest" and idx + 1 < len(tokens):
                        manifest_path = Path(tokens[idx + 1])
                    elif token == "--report-dir" and idx + 1 < len(tokens):
                        report_dir = Path(tokens[idx + 1])
                    elif token == "--rollback-path" and idx + 1 < len(tokens):
                        rollback_path = Path(tokens[idx + 1])
                    elif token == "--source-dir" and idx + 1 < len(tokens):
                        source_dir = Path(tokens[idx + 1])
                if "--verify-all" in tokens:
                    result = mod.verify_all_generated_nodes()
                    return {
                        "action": "nano_swarm_expand",
                        "verify_all": True,
                        **result,
                    }
                if "--checkpoint" in tokens:
                    result = mod.create_checkpoint(manifest_path=manifest_path)
                    return {
                        "action": "nano_swarm_expand",
                        "checkpoint": True,
                        **result,
                    }
                if "--formal-gate" in tokens:
                    result = mod.evaluate_formal_claims_gate()
                    return {
                        "action": "nano_swarm_expand",
                        "formal_gate": True,
                        **result,
                    }
                if "--bifrost-preflight" in tokens:
                    result = mod.bifrost_sidecar_preflight()
                    return {
                        "action": "nano_swarm_expand",
                        "bifrost_preflight": True,
                        **result,
                    }
                if "--runtime-status" in tokens:
                    from control_plane.nano_swarm_runtime import write_runtime_status

                    result = write_runtime_status()
                    return {
                        "action": "nano_swarm_expand",
                        "runtime_status": True,
                        **result,
                    }
                if "--rollback" in tokens:
                    result = mod.rollback_generated_node(node, rollback_path=rollback_path)
                    return {
                        "action": "nano_swarm_expand",
                        "rollback": True,
                        **result,
                    }
                if "--promote" in tokens:
                    kwargs = {"node_name": node}
                    if source_dir is not None:
                        kwargs["source_dir"] = source_dir
                    result = mod.promote_generated_node(**kwargs)
                    return {
                        "action": "nano_swarm_expand",
                        "promote": True,
                        **result,
                    }
                if "--evidence" in tokens:
                    kwargs = {"manifest_path": manifest_path}
                    if report_dir is not None:
                        kwargs["report_dir"] = report_dir
                    result = mod.write_evidence_report(**kwargs)
                    return {
                        "action": "nano_swarm_expand",
                        "evidence": True,
                        **result,
                    }
                if "--dry-run" in tokens:
                    result = mod.dry_run_expand(node_name=node, manifest_path=manifest_path)
                    return {
                        "action": "nano_swarm_expand",
                        "dry_run": True,
                        **result,
                    }
                if "--generate" in tokens:
                    result = mod.generate_node_artifact(node_name=node, manifest_path=manifest_path)
                    return {
                        "action": "nano_swarm_expand",
                        "generate": True,
                        **result,
                    }
                if "--source" in tokens:
                    result = mod.generate_node_source(node_name=node, manifest_path=manifest_path)
                    return {
                        "action": "nano_swarm_expand",
                        "source": True,
                        **result,
                    }
                exit_code = mod.run_expansion()
                return {
                    "action": "nano_swarm_expand",
                    "status": "CRYSTALLIZED" if exit_code == 0 else "BLOCKED",
                    "exit_code": exit_code,
                }
            except Exception as e:
                return {"action": "nano_swarm_expand", "error": str(e)}
    return {"action": "nano_swarm_expand", "detail": "script not found", "path": str(script)}


_HANDLERS = {
    "_handle_boot": _handle_boot,
    "_handle_dawning": _handle_dawning,
    "_handle_forge": _handle_forge,
    "_handle_codex": _handle_codex,
    "_handle_contract": _handle_contract,
    "_handle_claw": _handle_claw,
    "_handle_swarm": _handle_swarm,
    "_handle_plan": _handle_plan,
    "_handle_heal": _handle_heal,
    "_handle_fleet": _handle_fleet,
    "_handle_genesis": _handle_genesis,
    "_handle_assimilate": _handle_assimilate,
    "_handle_scavenge": _handle_scavenge,
    "_handle_defense_init": _handle_defense_init,
    "_handle_vocal": _handle_vocal,
    "_handle_scan": _handle_scan,
    "_handle_status": _handle_status,
    "_handle_think": _handle_think,
    "_handle_bifrost_lock": _handle_bifrost_lock,
    "_handle_scan_vectors": _handle_scan_vectors,
    "_handle_nano_swarm_expand": _handle_nano_swarm_expand,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_RUNE_RE = re.compile(r"^(//[\w-]+|Omega_\w+)\s*(.*)?$", re.IGNORECASE)
_RUNE_ALIASES: dict[str, str] = {
    "omega_codex": "Omega_CODEX",
    "//nano-swarm": "//NANO_SWARM_EXPAND",
    "//nanoswarm": "//NANO_SWARM_EXPAND",
    "//nano": "//NANO_SWARM_EXPAND",
}


def normalize_rune(rune: str) -> str:
    """Normalize rune aliases/casing to canonical dispatch keys."""
    raw = (rune or "").strip()
    if not raw:
        return raw

    alias = _RUNE_ALIASES.get(raw.lower())
    if alias:
        return alias

    for key in OMEGA_RUNES:
        if raw.lower() == key.lower():
            return key

    upper = raw.upper()
    if upper == "//VOCAL":
        return "//vocal"
    if upper in RUNIC_COMMANDS:
        return upper
    if raw in RUNIC_COMMANDS:
        return raw
    return raw


def parse_rune(text: str) -> Optional[tuple[str, str]]:
    """Extract (rune, param) from text. Returns None if no rune found."""
    for line in text.strip().splitlines():
        m = _RUNE_RE.match(line.strip())
        if m:
            rune = normalize_rune(m.group(1))
            param = (m.group(2) or "").strip()
            if rune in OMEGA_RUNES or rune in RUNIC_COMMANDS:
                return rune, param
    return None


def route_rune(rune: str, param: str = "", context: Optional[dict] = None) -> RuneResult:
    """Route a rune to the correct knight and queue the task."""
    rune = normalize_rune(rune)
    context = context or {}

    # Check for Privacy Shield Override
    combined_text = f"{rune} {param}".lower()
    is_privacy_override = any(kw in combined_text for kw in PRIVACY_KEYWORDS)

    # Runic command
    if rune in RUNIC_COMMANDS:
        cfg = RUNIC_COMMANDS[rune]
        knight = "sir_ghost" if is_privacy_override else cfg["knight"]
        handler_fn = _HANDLERS.get(cfg["handler"])
        metadata = handler_fn(param, context) if handler_fn else {"action": rune}
        directive = f"{rune} {param}".strip() if param else rune

        if HydrationManager and cfg.get("hydrate", True):
            mgr = HydrationManager(knight_id=knight)
            complexity = 9 if cfg.get("priority", 2) <= 1 else 5
            mgr.store_tissue(intent=directive, content=metadata, complexity=complexity, tier="L2" if complexity >= 8 else "L1")
            hydration = mgr.hydrate_context(intent=directive, complexity=complexity)
            if hydration.get("L2") and not "yielded no results" in str(hydration.get("L2")):
                directive += f"\n\n[CLOUD_BRAIN_CONTEXT]: {hydration.get('L2')}"

        if is_privacy_override:
            metadata["privacy_override"] = True
            metadata["original_knight"] = cfg["knight"]

        task_id, err = _queue_task(knight, directive, cfg.get("priority", 2))
        return RuneResult(
            rune=rune,
            knight=knight,
            directive=directive,
            mode="SENTINEL" if is_privacy_override else cfg.get("mode", "FORGE"),
            task_id=task_id,
            queued=err is None,
            queue_error=err,
            metadata=metadata,
        )

    # Omega rune
    if rune in OMEGA_RUNES:
        cfg = OMEGA_RUNES[rune]
        knight = "sir_ghost" if is_privacy_override else cfg["knight"]
        directive = f"{rune} {param}".strip() if param else rune
        metadata = {"description": cfg["description"]}

        if HydrationManager:
            mgr = HydrationManager(knight_id=knight)
            mgr.store_tissue(intent=directive, content=cfg["description"], complexity=9, tier="L2")
            hydration = mgr.hydrate_context(intent=directive, complexity=9)
            if hydration.get("L2") and not "yielded no results" in str(hydration.get("L2")):
                directive += f"\n\n[CLOUD_BRAIN_CONTEXT]: {hydration.get('L2')}"

        if is_privacy_override:
            metadata["privacy_override"] = True
            metadata["original_knight"] = cfg["knight"]

        task_id, err = _queue_task(knight, directive, priority=2)
        return RuneResult(
            rune=rune,
            knight=knight,
            directive=directive,
            mode="SENTINEL" if is_privacy_override else "ORACLE",
            task_id=task_id,
            queued=err is None,
            queue_error=err,
            metadata=metadata,
        )

    # Unknown rune — escalate to sir_boris or sir_ghost
    knight = "sir_ghost" if is_privacy_override else "sir_boris"
    directive = f"UNKNOWN_RUNE: {rune} {param}"
    metadata = {"warning": f"Rune '{rune}' not in dispatch table — escalated"}
    
    if is_privacy_override:
        metadata["privacy_override"] = True

    if HydrationManager:
        mgr = HydrationManager(knight_id=knight)
        mgr.store_tissue(intent=directive, content="Unknown Rune Escalation", complexity=5, tier="L1")
    task_id, err = _queue_task(knight, directive, priority=3)
    return RuneResult(
        rune=rune,
        knight=knight,
        directive=f"UNKNOWN_RUNE: {rune}",
        mode="SENTINEL" if is_privacy_override else "FORGE",
        task_id=task_id,
        queued=err is None,
        queue_error=err,
        metadata=metadata,
    )


def detect_and_route(text: str, context: Optional[dict] = None) -> Optional[RuneResult]:
    """Parse text for rune prefix and route if found. Returns None if no rune."""
    parsed = parse_rune(text)
    if parsed is None:
        return None
    rune, param = parsed
    return route_rune(rune, param, context)


def list_runes() -> dict[str, list[str]]:
    """Return all available runes grouped by type."""
    return {
        "runic_commands": list(RUNIC_COMMANDS.keys()),
        "omega_runes": list(OMEGA_RUNES.keys()),
    }


# ---------------------------------------------------------------------------
# CLI entry (python -m control_plane.runic_router [--rune X] [--task Y])
# ---------------------------------------------------------------------------

def _cli_main() -> None:
    import argparse
    import sys

    ap = argparse.ArgumentParser(
        prog="python -m control_plane.runic_router",
        description="CAMELOT-OS Runic Dispatch",
    )
    ap.add_argument("--rune", help="Rune name (e.g. FORGE, //BOOT, Omega_SYNC)")
    ap.add_argument("--task", default="", help="Task parameter passed to the handler")
    ap.add_argument("--detect", metavar="TEXT", help="Parse free-form text for a rune prefix")
    ap.add_argument("--list", action="store_true", help="List all available runes")
    args = ap.parse_args()

    if args.list:
        runes = list_runes()
        print("=== Runic Commands ===")
        for r in runes["runic_commands"]:
            print(f"  {r}")
        print("\n=== Omega Runes ===")
        for r in runes["omega_runes"]:
            print(f"  {r}")
        return

    if args.detect:
        result = detect_and_route(args.detect)
        if result is None:
            print(json.dumps({"error": "No rune detected in input"}))
            sys.exit(1)
    elif args.rune:
        raw_rune = args.rune if (args.rune.startswith("//") or args.rune.startswith("Omega_")) else f"//{args.rune.upper()}"
        rune = normalize_rune(raw_rune)
        result = route_rune(rune, args.task)
    else:
        ap.print_help()
        return

    print(json.dumps({
        "rune": result.rune,
        "knight": result.knight,
        "directive": result.directive,
        "mode": result.mode,
        "task_id": result.task_id,
        "queued": result.queued,
        "metadata": result.metadata,
    }, indent=2))


if __name__ == "__main__":
    _cli_main()
