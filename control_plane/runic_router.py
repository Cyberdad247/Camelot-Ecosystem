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
import re
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

CAMELOT_HOME = Path(__file__).parent.parent
QUEUE_FILE   = CAMELOT_HOME / "logs" / "harness_queue.jsonl"

# ---------------------------------------------------------------------------
# Rune tables
# ---------------------------------------------------------------------------

# 11 Runic Commands — sovereign execution runes
RUNIC_COMMANDS: dict[str, dict[str, Any]] = {
    "//BOOT": {
        "knight": "sir_boris",
        "description": "6-phase awaken boot sequence",
        "mode": "FORGE",
        "priority": 1,
        "handler": "_handle_boot",
    },
    "//FORGE": {
        "knight": "sir_forge",
        "description": "Kinetic build + compile directive",
        "mode": "KINETIC",
        "priority": 2,
        "handler": "_handle_forge",
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
    "//FLEET": {
        "knight": "sir_boris",
        "description": "Map-Reduce swarm deployment across terminals",
        "mode": "SWARM",
        "priority": 2,
        "handler": "_handle_fleet",
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

def _queue_task(knight: str, directive: str, priority: int = 2) -> tuple[str, Optional[str]]:
    task_id = f"rune-{uuid.uuid4().hex[:8]}"
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

def _handle_forge(param: str, context: dict) -> dict:
    return {"action": "kinetic build", "param": param or "default target"}

def _handle_swarm(param: str, context: dict) -> dict:
    return {"action": "srdl_map_reduce", "param": param, "bio_swarm": "Formica+Pongid+Castor"}

def _handle_plan(param: str, context: dict) -> dict:
    return {"action": "tot_planning", "output": "Plan.json", "param": param}

def _handle_heal(param: str, context: dict) -> dict:
    return {"action": "piv_self_heal", "target": param or "auto-diagnose"}

def _handle_fleet(param: str, context: dict) -> dict:
    return {"action": "map_reduce_deploy", "terminals": "all live", "param": param}

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


_HANDLERS = {
    "_handle_boot": _handle_boot,
    "_handle_forge": _handle_forge,
    "_handle_swarm": _handle_swarm,
    "_handle_plan": _handle_plan,
    "_handle_heal": _handle_heal,
    "_handle_fleet": _handle_fleet,
    "_handle_genesis": _handle_genesis,
    "_handle_assimilate": _handle_assimilate,
    "_handle_scavenge": _handle_scavenge,
    "_handle_defense_init": _handle_defense_init,
    "_handle_vocal": _handle_vocal,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_RUNE_RE = re.compile(r"^(//\w+|Omega_\w+)\s*(.*)?$", re.IGNORECASE)


def parse_rune(text: str) -> Optional[tuple[str, str]]:
    """Extract (rune, param) from text. Returns None if no rune found."""
    for line in text.strip().splitlines():
        m = _RUNE_RE.match(line.strip())
        if m:
            rune = m.group(1)
            param = (m.group(2) or "").strip()
            # Normalize case for Omega runes
            for key in OMEGA_RUNES:
                if rune.lower() == key.lower():
                    return key, param
            # Normalize case for runic commands
            upper = rune.upper()
            if upper == "//VOCAL":
                upper = "//vocal"
            if upper in RUNIC_COMMANDS or rune in RUNIC_COMMANDS:
                return (upper if upper in RUNIC_COMMANDS else rune), param
    return None


def route_rune(rune: str, param: str = "", context: Optional[dict] = None) -> RuneResult:
    """Route a rune to the correct knight and queue the task."""
    context = context or {}

    # Runic command
    if rune in RUNIC_COMMANDS:
        cfg = RUNIC_COMMANDS[rune]
        handler_fn = _HANDLERS.get(cfg["handler"])
        metadata = handler_fn(param, context) if handler_fn else {"action": rune}
        directive = f"{rune} {param}".strip() if param else rune
        task_id, err = _queue_task(cfg["knight"], directive, cfg.get("priority", 2))
        return RuneResult(
            rune=rune,
            knight=cfg["knight"],
            directive=directive,
            mode=cfg.get("mode", "FORGE"),
            task_id=task_id,
            queued=err is None,
            queue_error=err,
            metadata=metadata,
        )

    # Omega rune
    if rune in OMEGA_RUNES:
        cfg = OMEGA_RUNES[rune]
        directive = f"{rune} {param}".strip() if param else rune
        task_id, err = _queue_task(cfg["knight"], directive, priority=2)
        return RuneResult(
            rune=rune,
            knight=cfg["knight"],
            directive=directive,
            mode="ORACLE",
            task_id=task_id,
            queued=err is None,
            queue_error=err,
            metadata={"description": cfg["description"]},
        )

    # Unknown rune — escalate to sir_boris
    task_id, err = _queue_task("sir_boris", f"UNKNOWN_RUNE: {rune} {param}", priority=3)
    return RuneResult(
        rune=rune,
        knight="sir_boris",
        directive=f"UNKNOWN_RUNE: {rune}",
        mode="FORGE",
        task_id=task_id,
        queued=err is None,
        queue_error=err,
        metadata={"warning": f"Rune '{rune}' not in dispatch table — escalated to SIR_BORIS"},
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
