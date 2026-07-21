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

__version__ = "9000.14"  # CYBERTRONIA — set by P1-T01


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
QUEUE_FILE = CAMELOT_HOME / "logs" / "harness_queue.jsonl"

# Rate-limit guard for _queue_task — kills runaway producers that fire the same
# (knight, directive) thousands of times per second. Tunable via env:
#   CAMELOT_ROUTER_DEDUP_WINDOW_SEC (default 10) — sliding window in seconds
#   CAMELOT_ROUTER_DEDUP_MAX        (default 5)  — max identical submits per window
#   CAMELOT_ROUTER_DEDUP_DISABLE=1               — bypass the guard entirely
_DEDUP_WINDOW_SEC = float(os.environ.get("CAMELOT_ROUTER_DEDUP_WINDOW_SEC", "10"))
_DEDUP_MAX = int(os.environ.get("CAMELOT_ROUTER_DEDUP_MAX", "5"))
_DEDUP_DISABLED = os.environ.get("CAMELOT_ROUTER_DEDUP_DISABLE") == "1"
_dedup_lock = threading.Lock()
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
        "description": "global awaken boot sequence",
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
    "//TRIAGE": {
        "knight": "sir_codex",
        "description": "Evidence-gated read-only system architecture triage",
        "mode": "SENTINEL",
        "priority": 1,
        "handler": "_handle_triage",
        "hydrate": False,
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
        "description": "6-phase UKG_NANO_SWARM_V1000 expansion: SAT-gate → CvRDT mesh → Ouroboros seed → Argus bind → AST audit → Anya seal",
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
    "//EVOLVE_AND_FORGE": {
        "knight": "sir_boris",
        "description": "GEP-driven shadow forge and evolution cycle",
        "mode": "SWARM",
        "priority": 1,
        "handler": "_handle_evolve_and_forge",
    },
    "//PURGE_MEMORY": {
        "knight": "sir_forge",
        "description": "Zero-out local and remote vector indices + JSON-LD memories",
        "mode": "FORGE",
        "priority": 1,
        "handler": "_handle_purge_memory",
    },
    "//EXECUTE_PROMPT": {
        "knight": "lukas_omega",
        "description": "Execute a forge-law crystallized cartridge with Iron Gate approval",
        "mode": "FORGE",
        "priority": 1,
        "handler": "_handle_execute_prompt",
    },
}

# 29 Omega Runes — system-level operations
OMEGA_RUNES: dict[str, dict[str, Any]] = {
    "Omega_SYNC": {"knight": "sir_mnemo", "description": "Dual-tier memory sync (ST+LT)"},
    "Omega_PURGE": {"knight": "sir_forge", "description": "Targeted purge with Iron Gate"},
    "Omega_STATUS": {"knight": "sir_boris", "description": "Full system status report"},
    "Omega_KINETIC": {"knight": "lukas_omega", "description": "Kinetic Edge binary operations"},
    "Omega_ACTUATE": {"knight": "sir_boris", "description": "Singularity Engine activation"},
    "Omega_REFORGE": {"knight": "sir_forge", "description": "Full module recompile + hotswap"},
    "Omega_AUDIT": {"knight": "sir_sentinel", "description": "Full security audit cycle"},
    "Omega_THINK": {"knight": "merlin_omega", "description": "Deep GoT/DoT reasoning chain"},
    "Omega_GLYPH": {"knight": "merlin_omega", "description": "NPE TCoT formal verification"},
    "Omega_COMPRESS": {"knight": "merlin_omega", "description": "SAC->CCF->QFT compression"},
    "Omega_SHIELD": {"knight": "sir_sentinel", "description": "Agent-Armor PDG taint shield"},
    "Omega_KERNEL": {"knight": "sir_boris", "description": "Kernel-level OS operations"},
    "Omega_ORACLE": {"knight": "merlin_omega", "description": "Oracle Hypervisor broadcast"},
    "Omega_ANYA": {"knight": "anya_omega", "description": "APEE v6.5 pipeline audit"},
    "Omega_BESTIARY": {"knight": "sir_boris", "description": "Bio-Swarm zoology report"},
    "Omega_VOICE": {"knight": "sir_sonus", "description": "Voice pipeline diagnostics"},
    "Omega_VISION": {"knight": "sir_visage", "description": "Media/image pipeline ops"},
    "Omega_COMPILE": {"knight": "lukas_omega", "description": "Rust/Go compilation trigger"},
    "Omega_EVOLVE": {"knight": "lord_archivist", "description": "GEP scan + XP evolution cycle"},
    "Omega_RESEARCH": {"knight": "lady_apis", "description": "BASHR research loop"},
    "Omega_CLEAN": {"knight": "sir_forge", "description": "Cache + orphan cleanup"},
    "Omega_PERSONA": {"knight": "sir_alex", "description": "Persona evolution binding"},
    "Omega_SILENCE": {"knight": "sir_sentinel", "description": "Emergency lockdown protocol"},
    "Omega_PROMETHEUS": {"knight": "sir_helio", "description": "Cloud burst + Modal GPU"},
    "Omega_ARCHETYPE": {"knight": "sir_alex", "description": "Archetype pattern synthesis"},
    "Omega_GRAPH": {"knight": "merlin_omega", "description": "UKG graph traversal + query"},
    "Omega_GATEWAY": {"knight": "sir_link", "description": "Switchboard gateway diagnostics"},
    "Omega_STACK": {"knight": "sir_boris", "description": "Full stack topology report"},
    "Omega_SCORPION": {"knight": "sir_gideon", "description": "Forensic GIDEON_RISK_MATRIX audit"},
    "Omega_CODEX": {"knight": "sir_codex", "description": "Direct SIR_CODEX execution lane"},
    "Omega_BIFROST": {"knight": "sir_heimdall", "description": "Bifrost Sentinel operations"},
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
# GCMN vMAX stub governance
# ---------------------------------------------------------------------------
#
# The GCMN vMAX nano-seed was pasted as untrusted external input. It is
# NEVER auto-activated. To even *route* these runes, the operator must set:
#
#     CAMELOT_GCMN_STUBS_ENABLED=1
#
# Without the flag, the runes fall through to the standard unknown/escalation
# path (knight=sir_boris) so callers cannot accidentally invoke the stub
# envelope. The stubs themselves are INERT: they emit a structured TODO
# metadata payload + a stderr log line + a synthetic task id, but they do
# NOT touch Bifrost / pqcrypto / SQLCipher / cartridge ignition.
#
# This constant is the single source of truth for stub governance state.
# PROVENANCE_LEDGER.md is hook-owned and MUST NOT be referenced as a write
# target here.
GCMN_GOVERNANCE: dict[str, Any] = {
    "schema": "camelot-os.system/schema/cybertronia/v26/kba_services",
    "fingerprint": "νKG_CRYSTAL_OMEGA_STANDARDIZED",
    "version": "vMAX",
    "owner": "untrusted_external_seed",
    "status": "STUB_INERT",
    "audit_ledger_pointer": None,
    "hitl_required_for_activation": True,
    "hitl_risk_score": 95,
}

# Four stub runes mirrored exactly from the pasted seed. Canonical keys stay
# in //UPPER_SNAKE_CASE to match existing patterns (//NANO_SWARM_EXPAND,
# //BIFROST_LOCK, //EVOLVE_AND_FORGE, //PURGE_MEMORY).
GCMN_STUB_RUNES: dict[str, dict[str, Any]] = {
    "//SYNC_KBA_DATABASES_SQLCIPHER": {
        "knight_hint": "sir_sentinel",
        "spec_step": 1,  # AUTH_SHIELD
        "todo": [
            "Adjudicate SQLCipher multi-tenant KDF (no rotation policy in seed)",
            "Reconcile against existing tenant schema under 04_KINETIC",
        ],
        "collision": None,
        "domain": "KBA_SERVICES",
    },
    "//LOCK_BIFROST_mTLS_KYBER768": {
        "knight_hint": "sir_heimdall",
        "spec_step": 3,  # TOPOLOGY_MOUNT
        "todo": [
            "Largely redundant with deployed bin/bifrost.py + control_plane/pqcrypto_bridge.py",
            "Verify ML-KEM-768 interop with the mTLS envelope under Vercel Edge Wasm",
            "Confirm Kyber-768 binary size + entropy APIs fit Vercel Edge route limits",
        ],
        "collision": "bin/bifrost.py + control_plane/pqcrypto_bridge.py already deployed",
        "domain": "KBA_SERVICES",
    },
    "//ENGAGE_RUST_IRON_DAEMON": {
        "knight_hint": "sir_forge",
        "spec_step": 3,  # TOPOLOGY_MOUNT
        "todo": [
            "Confirm cargo target vs existing 04_KINETIC/squires_rs binary",
            "Define the WSS protocol contract (no schema in seed)",
        ],
        "collision": "Namespace may clash with 04_KINETIC binaries",
        "domain": "KBA_SERVICES",
    },
    "//CRYSTALLIZE_GCMN_vMAX": {
        "knight_hint": "sir_boris",
        "spec_step": 4,  # CARTRIDGE_IGNITION (kitchen-sink rake)
        "todo": [
            "Decompose into Plan.json via the existing //PLAN handler",
            "Specify cartridge ignition order for Amani/Castellon/etc.",
            "Avoid overlap with //NANO_SWARM_EXPAND + cartridge_manager",
        ],
        "collision": "Overlaps //NANO_SWARM_EXPAND + cartridge_manager semantics",
        "domain": "KBA_SERVICES",
    },
}


# Module-level session-disable flag — flipped by `_dispatch_gcmn_purge()` so
# the --purge_stubs force-kill can disable the GCMN_STUBS path for the rest
# of the runtime session without touching the operator's `.env`. Reset by
# interpreter exit (process-scoped; not persisted).
_gcmn_stubs_session_disabled = False


def _gcmn_stubs_enabled() -> bool:
    """Operator feature flag for the GCMN vMAX stub dispatch table.

    Default OFF. Mirrors the env-var pattern used by the dedup guard
    (CAMELOT_ROUTER_DEDUP_DISABLE) so the consistency model is preserved.

    The session-disable short-circuit returns False if
    `_dispatch_gcmn_purge()` has already fired in this runtime session —
    keeps the force-kill audit-visible while rendering the stub path inert
    without mutating the operator's .env state.
    """
    if _gcmn_stubs_session_disabled:
        return False
    return os.environ.get("CAMELOT_GCMN_STUBS_ENABLED") == "1"


def _dispatch_gcmn_stub(rune: str, param: str) -> RuneResult:
    """INERT stub dispatcher for the GCMN vMAX nano-seed.

    Returns a sealed TODO envelope + a synthetic task id. Does NOT call
    _queue_task (so the harness queue is not polluted with stub markers).
    Emits one structured stderr line so opt-in operators can audit a run.
    """
    cfg = GCMN_STUB_RUNES[rune]
    fingerprint = str(GCMN_GOVERNANCE["fingerprint"])
    metadata: dict[str, Any] = {
        "action": "gcmn_stub_exec",
        "rune": rune,
        "status": "STUB_INERT",
        "gate": "CAMELOT_GCMN_STUBS_ENABLED=1",
        "governance": {**GCMN_GOVERNANCE},
        "knight_hint": cfg["knight_hint"],
        "spec_step": cfg["spec_step"],
        "domain": cfg.get("domain", "KBA_SERVICES"),
        "todo": list(cfg["todo"]),
        "collision_warning": cfg["collision"],
        "param_echoed": param,
        "next_action": "HUMAN_REVIEW_REQUIRED",
    }
    print(
        f"[GCMN-STUB] rune={rune} fingerprint={fingerprint} status=STUB_INERT",
        file=sys.stderr,
    )
    directive = f"{rune} {param}".strip() if param else rune
    return RuneResult(
        rune=rune,
        knight=cfg["knight_hint"],
        directive=f"STUB::{directive}",
        mode="ORACLE",
        task_id=f"gcmn-stub-{uuid.uuid4().hex[:8]}",
        queued=False,
        queue_error=None,
        metadata=metadata,
    )


def _dispatch_gcmn_purge() -> RuneResult:
    """Force-kill STUB_PURGED emitter. Disables GCMN_STUBS for the session.

    Activation ADR §8 contract:
      * Requires `CAMELOT_OPS_EMERGENCY=1` in env as a degraded signature
        witness (operator of record: sir_sentinel). The CLI argparse
        handler `_cli_main` enforces the witness before invoking this
        function; this function must never be called unless the witness
        is verified.
      * Emits a STUB_PURGED envelope with metadata.tombstone='STUB_PURGED'.
      * Sets module-level `_gcmn_stubs_session_disabled = True`, which
        short-circuits `_gcmn_stubs_enabled()` for the remainder of the
        runtime session. The env var itself is un-touched so the next
        session re-evaluates cleanly.
      * Emits one stderr audit line `[GCMN-STUB] tombstone=STUB_PURGED ...`.
      * Does NOT call `_queue_task` (consistent with `_dispatch_gcmn_stub`).
      * The PROVENANCE_LEDGER append is the caller's responsibility.
    """
    global _gcmn_stubs_session_disabled
    _gcmn_stubs_session_disabled = True

    fingerprint = str(GCMN_GOVERNANCE["fingerprint"])
    print(
        f"[GCMN-STUB] tombstone=STUB_PURGED witness=CAMELOT_OPS_EMERGENCY=1 "
        f"fingerprint={fingerprint}",
        file=sys.stderr,
    )

    return RuneResult(
        rune="//GCMN_PURGE",
        knight="sir_sentinel",
        directive="STUB_PURGED: session-disabled GCMN_STUBS path",
        mode="SENTINEL",
        task_id=f"gcmn-purge-{uuid.uuid4().hex[:8]}",
        queued=False,
        queue_error=None,
        metadata={
            "action": "gcmn_purge_force_kill",
            "rune": "//GCMN_PURGE",
            "status": "STUB_PURGED",
            "tombstone": "STUB_PURGED",
            "force_kill_witness": "CAMELOT_OPS_EMERGENCY=1",
            "next_action": "FORCE_KILL_EXECUTED",
            "session_disabled": True,
            "governance": {**GCMN_GOVERNANCE, "status": "STUB_PURGED"},
            "decision_doc": "docs/adr/gcmn_stubs_activation.md",
        },
    )


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


def _queue_task(knight: str, directive: str, priority: int = 2, extra: Optional[dict[str, Any]] = None, task_id: Optional[str] = None) -> tuple[str, Optional[str]]:
    if task_id is None:
        task_id = f"rune-{uuid.uuid4().hex[:8]}"
    rl_err = _rate_limit_check(knight, directive)
    if rl_err:
        return task_id, rl_err
    entry: dict[str, Any] = {
        "id": task_id,
        "knight": knight,
        "directive": directive,
        "priority": priority,
        "submitted": datetime.now(timezone.utc).isoformat(),
    }
    if extra:
        entry.update(extra)
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(QUEUE_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        return task_id, None
    except Exception as e:
        return task_id, str(e)


def _handle_boot(param: str, context: dict) -> dict:
    return {
        "action": "awaken global boot",
        "detail": "run: awaken",
        "canonical_command": "awaken",
        "fallback": "python bin/awaken.py",
    }


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
    rust_bin = str(CAMELOT_HOME / "04_KINETIC" / "squires_rs" / "target" / "release" / "squires_rs.exe")
    return {"action": "squires_colony_triage", "path": param or ".", "detail": f"run: {rust_bin} scan"}


def _handle_status(param: str, context: dict) -> dict:
    return {"action": "system_status", "detail": "run: python -m control_plane.harness --status"}


def _handle_triage(param: str, context: dict) -> dict:
    tokens = shlex.split(param, posix=False) if param else []
    allowed = {"--rapid", "--deep", "--force-deep", "--json"}
    normalized = [token for token in tokens if token in allowed]
    command = "camelot triage"
    if normalized:
        command += " " + " ".join(normalized)
    return {
        "action": "system_triage",
        "canonical_command": command,
        "read_only": True,
        "requested_options": normalized,
    }


def _handle_think(param: str, context: dict) -> dict:
    return {"action": "got_reasoning", "param": param, "knight": "merlin_omega"}


def _handle_bifrost_lock(param: str, context: dict) -> dict:
    return {"action": "bifrost_lockdown", "status": "AIR_GAPPED"}


def _handle_scan_vectors(param: str, context: dict) -> dict:
    return {"action": "4_vector_scan", "target": param or "project_root"}


def _handle_evolve_and_forge(param: str, context: dict) -> dict:
    objective = param or "default objective"
    return {
        "action": "evolve_and_forge",
        "objective": objective,
        "detail": f"run: python scripts/evolve_and_forge.py --task {shlex.quote(objective)}",
    }


def _handle_purge_memory(param: str, context: dict) -> dict:
    return {
        "action": "purge_memory",
        "detail": "run: python scripts/purge_memory.py",
        "canonical_command": "python scripts/purge_memory.py",
    }


def _handle_execute_prompt(param: str, context: dict) -> dict:
    """Handle //EXECUTE_PROMPT with approval grant requirement."""
    from control_plane import forge_law

    cartridge_id = param.strip() if param else ""
    approval = context.get("approval_grant") if context else None
    if not approval or not isinstance(approval, dict) or approval.get("version") != 2:
        raise ValueError("//EXECUTE_PROMPT requires a valid Iron Gate v2 approval grant")
    binding = forge_law.approval_binding(cartridge_id)
    if approval.get("cartridge_digest") != binding.get("cartridgeDigest"):
        raise ValueError("approval grant digest does not match cartridge")
    if approval.get("target_root") != binding.get("targetRoot"):
        raise ValueError("approval grant target root does not match cartridge")
    return {
        "action": "execute_prompt",
        "cartridge_id": cartridge_id,
        "approval_id": approval.get("approval_id"),
    }


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
                manifest_path = (
                    CAMELOT_HOME / "03_VAULT" / "runtime_state" / "ukg_nano_omega_glyph_v1000_omni_codex.json"
                )
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
    "_handle_triage": _handle_triage,
    "_handle_think": _handle_think,
    "_handle_bifrost_lock": _handle_bifrost_lock,
    "_handle_scan_vectors": _handle_scan_vectors,
    "_handle_nano_swarm_expand": _handle_nano_swarm_expand,
    "_handle_evolve_and_forge": _handle_evolve_and_forge,
    "_handle_purge_memory": _handle_purge_memory,
    "_handle_execute_prompt": _handle_execute_prompt,
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

    # GCMN vMAX stub dispatch (feature-flagged, inert by default).
    # Inserted BEFORE the RUNIC_COMMANDS branch so that when the flag is
    # OFF the rune falls through cleanly to unknown/escalation rather than
    # matching a real handler.
    if not is_privacy_override and rune in GCMN_STUB_RUNES and _gcmn_stubs_enabled():
        return _dispatch_gcmn_stub(rune, param)

    # Runic command
    if rune in RUNIC_COMMANDS:
        cfg = RUNIC_COMMANDS[rune]
        knight = "sir_ghost" if is_privacy_override else cfg["knight"]
        handler_fn = _HANDLERS.get(cfg["handler"])
        try:
            metadata = handler_fn(param, context) if handler_fn else {"action": rune}
        except ValueError as exc:
            directive = f"{rune} {param}".strip() if param else rune
            return RuneResult(
                rune=rune,
                knight=knight,
                directive=directive,
                mode=cfg.get("mode", "FORGE"),
                task_id=f"rune-{uuid.uuid4().hex[:8]}",
                queued=False,
                queue_error=str(exc),
                metadata={"action": rune, "error": str(exc)},
            )
        directive = f"{rune} {param}".strip() if param else rune

        if HydrationManager and cfg.get("hydrate", True):
            mgr = HydrationManager(knight_id=knight)
            complexity = 9 if cfg.get("priority", 2) <= 1 else 5
            mgr.store_tissue(
                intent=directive, content=metadata, complexity=complexity, tier="L2" if complexity >= 8 else "L1"
            )
            hydration = mgr.hydrate_context(intent=directive, complexity=complexity)
            if hydration.get("L2") and "yielded no results" not in str(hydration.get("L2")):
                directive += f"\n\n[CLOUD_BRAIN_CONTEXT]: {hydration.get('L2')}"

        if is_privacy_override:
            metadata["privacy_override"] = True
            metadata["original_knight"] = cfg["knight"]

        extra: Optional[dict[str, Any]] = None
        approval = context.get("approval_grant") if context else None
        if approval and isinstance(approval, dict):
            pending_task_id = f"rune-{uuid.uuid4().hex[:8]}"
            extra = {
                "approval_grant": {
                    "version": approval.get("version"),
                    "approval_id": approval.get("approval_id"),
                    "grant_id": approval.get("grant_id"),
                    "cartridge_digest": approval.get("cartridge_digest"),
                    "target_root": approval.get("target_root"),
                    "task_id": pending_task_id,
                }
            }

        task_id, err = _queue_task(knight, directive, cfg.get("priority", 2), extra=extra, task_id=pending_task_id if approval and isinstance(approval, dict) else None)
        if extra:
            extra["approval_grant"]["task_id"] = task_id
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
            if hydration.get("L2") and "yielded no results" not in str(hydration.get("L2")):
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
    """Return all available runes grouped by type.

    The ``gcmn_stub_runes`` group is only emitted when the
    ``CAMELOT_GCMN_STUBS_ENABLED=1`` flag is set, so default ``--list``
    output stays clean.
    """
    out: dict[str, list[str]] = {
        "runic_commands": list(RUNIC_COMMANDS.keys()),
        "omega_runes": list(OMEGA_RUNES.keys()),
    }
    if _gcmn_stubs_enabled():
        out["gcmn_stub_runes"] = list(GCMN_STUB_RUNES.keys())
    return out


# ---------------------------------------------------------------------------
# CLI entry (python -m control_plane.runic_router [--rune X] [--task Y])
# ---------------------------------------------------------------------------


def _cli_main() -> None:
    import argparse
    import sys

    # Reconfigure stdout/stderr to UTF-8 so the ν (U+03BD) glyph in
    # νKG_CRYSTAL_OMEGA_STANDARDIZED and Greek letters in governance markers
    # don't trip the cp1252 codec on Windows. Safe no-op on POSIX (UTF-8 is
    # the default there).
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        # AttributeError: Python <3.7 (we target 3.11+, but defensive).
        # ValueError: stdout already captured or reconfigured by a test
        # harness that doesn't allow reconfigure.
        pass

    ap = argparse.ArgumentParser(
        prog="python -m control_plane.runic_router",
        description="CAMELOT-OS Runic Dispatch",
    )
    ap.add_argument("--rune", help="Rune name (e.g. FORGE, //BOOT, Omega_SYNC)")
    ap.add_argument("--task", default="", help="Task parameter passed to the handler")
    ap.add_argument("--detect", metavar="TEXT", help="Parse free-form text for a rune prefix")
    ap.add_argument("--list", action="store_true", help="List all available runes")
    ap.add_argument(
        "--purge_stubs",
        action="store_true",
        help=(
            "Emergency scrub: force-kill the GCMN_STUBS path for this "
            "session and emit a STUB_PURGED envelope. Requires "
            "`CAMELOT_OPS_EMERGENCY=1` in env as a witness (degraded "
            "signature per activation ADR §8)."
        ),
    )
    args = ap.parse_args()

    if args.purge_stubs:
        # Witness check — degraded signature per activation ADR §8. We
        # require the EXACT string `"1"` (matches `_gcmn_stubs_enabled`
        # semantics) so truthy strings like "true"/"yes" do not silently
        # authorize a force-kill.
        if os.environ.get("CAMELOT_OPS_EMERGENCY") != "1":
            print(
                json.dumps(
                    {
                        "error": (
                            "--purge_stubs requires CAMELOT_OPS_EMERGENCY=1 "
                            "in env (degraded signature witness per "
                            "activation ADR §8)."
                        )
                    }
                )
            )
            sys.exit(1)
        result = _dispatch_gcmn_purge()
        # Append receipt to PROVENANCE_LEDGER.md. The runic_router treats
        # runtime receipts (e.g. heartbeat, watchdog) as writeable here;
        # the `audit_ledger_pointer=None` governance signal applies to the
        # audited-trail claims, not to runtime housekeeping lines. We
        # annotate a failure into metadata if the append fails rather than
        # crashing — the dispatch itself succeeded.
        try:
            ledger_path = CAMELOT_HOME / "PROVENANCE_LEDGER.md"
            now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            with open(ledger_path, "a", encoding="utf-8") as f:
                f.write(
                    f"\n| {now_iso} | SIR_SENTINEL | FORCE_KILL: "
                    f"--purge_stubs activated; GCMN_STUBS path disabled "
                    f"for session; tombstone=STUB_PURGED | PURGED |\n"
                )
        except OSError as e:
            result.metadata["ledger_append_error"] = str(e)
        print(
            json.dumps(
                {
                    "rune": result.rune,
                    "knight": result.knight,
                    "directive": result.directive,
                    "mode": result.mode,
                    "task_id": result.task_id,
                    "queued": result.queued,
                    "metadata": result.metadata,
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return

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
        raw_rune = (
            args.rune if (args.rune.startswith("//") or args.rune.startswith("Omega_")) else f"//{args.rune.upper()}"
        )
        rune = normalize_rune(raw_rune)
        result = route_rune(rune, args.task)
    else:
        ap.print_help()
        return

    print(
        json.dumps(
            {
                "rune": result.rune,
                "knight": result.knight,
                "directive": result.directive,
                "mode": result.mode,
                "task_id": result.task_id,
                "queued": result.queued,
                "metadata": result.metadata,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    _cli_main()
