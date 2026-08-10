"""Bridge Module -- connects the CLI frontend to the CAMELOT_OS kernel.

Provides graceful fallback: if CAMELOT_OS is available, uses the real
kernel components (Iron Gate, Warden, MGV, Agora, cartridges, memory,
planning, orchestration). Falls back to local implementations when
kernel is unavailable.
"""

import contextlib
import io
import json
import logging
import os
import sys
import threading
from pathlib import Path
from typing import Optional

__version__ = "1.0.0"

logger = logging.getLogger("camelot.bridge")

# ── Fix Windows encoding before any kernel imports ────────────────────
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# ── Discovery ────────────────────────────────────────────────────────

CAMELOT_OS_ROOT = Path(os.environ.get(
    "CAMELOT_OS_ROOT",
    os.environ.get("CAMELOT_OS_HOME", os.path.expanduser("~/CAMELOT_OS"))
))
logger.info("Bridge Root: %s", CAMELOT_OS_ROOT)
KERNEL_DIR = CAMELOT_OS_ROOT / "01_KERNEL"
VAULT_DIR = CAMELOT_OS_ROOT / "03_VAULT"
FORGE_DIR = CAMELOT_OS_ROOT / "02_FORGE"
LEDGER_PATH = CAMELOT_OS_ROOT / "PROVENANCE_LEDGER.md"

_os_available = KERNEL_DIR.is_dir()
_components = {}
_components_lock = threading.Lock()
IMPORT_TIMEOUT = 45  # seconds — prevents hanging on bad kernel modules


class _TitanFluxFallback:
    """Minimal in-memory flux store when Titan Omega dependencies are missing."""

    def __init__(self):
        self._events: dict[str, list[str]] = {}

    def store_event(self, session_id: str, content: str):
        self._events.setdefault(session_id, []).append(content)

    def get_session_events(self, session_id: str) -> list[str]:
        return list(self._events.get(session_id, []))


class _TitanGraphFallback:
    """Minimal graph-like store for bridge callers."""

    def __init__(self):
        self._nodes: list[dict] = []

    def add_node(self, node_data: dict) -> str:
        node_id = str(node_data.get("node_id") or node_data.get("id") or f"node_{len(self._nodes)+1}")
        payload = dict(node_data)
        payload.setdefault("node_id", node_id)
        self._nodes.append(payload)
        return node_id

    def query(self, pattern: dict) -> list[dict]:
        results = []
        for node in self._nodes:
            if all(node.get(key) == value for key, value in pattern.items()):
                results.append(dict(node))
        return results


def _build_titan_fallback() -> dict:
    logger.warning("Titan Omega unavailable; using degraded in-memory fallback")
    return {"graph": _TitanGraphFallback(), "flux": _TitanFluxFallback(), "degraded": True}


def _local_excalibur_process_intent(intent: str) -> dict:
    """Fallback intent router when the full Excalibur kernel cannot load."""
    lower = intent.lower()
    if any(term in lower for term in ("status", "health", "report")):
        action = "SYSTEM_HEALTH_CHECK"
        target = "Merlin_Omega"
        priority = "LOW"
    elif any(term in lower for term in ("research", "search", "find", "who is")):
        action = "DISPATCH_RESEARCH_AGENT"
        target = "Morgana_Swarm"
        priority = "MEDIUM"
    elif any(term in lower for term in ("deploy", "build", "run", "execute")):
        action = "INITIATE_KINETIC_SEQUENCE"
        target = "Sir_Lukas"
        priority = "HIGH"
    else:
        action = "GENERIC_PROCESS"
        target = "UKG_Vault"
        priority = "MEDIUM"
    return {
        "action": action,
        "target": target,
        "priority": priority,
        "payload": intent,
        "source": "bridge_fallback",
    }


def _add_kernel_to_path():
    """Add CAMELOT_OS paths so kernel modules are importable."""
    paths_to_add = [
        str(CAMELOT_OS_ROOT),
        str(KERNEL_DIR / "titan"),
        str(KERNEL_DIR),
        str(KERNEL_DIR / "iron_gate"),
        str(KERNEL_DIR / "merlin"),
        str(KERNEL_DIR / "agora"),
        str(KERNEL_DIR / "forge"),
        str(KERNEL_DIR / "senses"),
        str(KERNEL_DIR / "EXCALIBUR"),
    ]
    for p in paths_to_add:
        if p not in sys.path:
            sys.path.insert(0, p)


def is_available() -> bool:
    """Check if CAMELOT_OS kernel is reachable."""
    return _os_available


# ── Lazy Component Loading ───────────────────────────────────────────

def _load_component(name: str):
    """Lazy-load a kernel component with error isolation and thread safety."""
    with _components_lock:
        if name in _components:
            return _components[name]

        if not _os_available:
            _components[name] = None
            return None

        _add_kernel_to_path()
        return _load_component_inner(name)


def _load_component_inner(name: str):
    """Inner loader with timeout — called under lock."""
    result = [None]
    error = [None]

    def _do_import():
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                result[0] = _import_component(name)
        except Exception as e:
            error[0] = e

    t = threading.Thread(target=_do_import, daemon=True)
    t.start()
    t.join(timeout=IMPORT_TIMEOUT)
    if t.is_alive():
        logger.warning("Import of %s timed out after %ds", name, IMPORT_TIMEOUT)
        _components[name] = None
        return None
    if error[0]:
        logger.warning("Failed to load %s: %s", name, error[0])
        _components[name] = None
        return None
    _components[name] = result[0]
    if result[0] is not None:
        logger.info("%s loaded from CAMELOT_OS", name)
    return result[0]


def _import_component(name: str):
    """Actually import a kernel component. May run in a background thread."""
    if name == "iron_gate":
        from iron_gate.security.iron_gate import iron_gate
        return iron_gate

    elif name == "warden":
        from iron_gate.security.warden import warden
        return warden

    elif name == "zenith":
        from iron_gate.security.zenith_scanner import zenith
        return zenith

    elif name == "mgv":
        from reasoning.core import MGVEngine
        return MGVEngine(debug=False)

    elif name == "cartridges_os":
        cart_path = KERNEL_DIR / "EXCALIBUR" / "config" / "cartridges.json"
        if cart_path.exists():
            with open(cart_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    elif name == "vault":
        sys.path.insert(0, str(VAULT_DIR))
        try:
            from vault_manager import VaultManager
            return VaultManager
        except FileNotFoundError:
            logger.warning("Vault Manager not initialized (no master key)")
            return None

    elif name == "titan_omega":
        try:
            from titan.memory.titan_omega import TitanOmega
            stack = TitanOmega.graft(tier="alpha_omega", mode="production", persist="all")
            return {
                "graph": stack.graph,
                "vault": stack.vault,
                "flux": stack.flux,
                "config": stack.config,
                "stack": stack
            }
        except Exception as e:
            import traceback
            logger.warning("Titan Omega import failed: %s\n%s", e, traceback.format_exc())
            return _build_titan_fallback()

    elif name == "planning_engine":
        from reasoning.planning_engine import PlanningEngine
        return PlanningEngine()

    elif name == "excalibur":
        try:
            from EXCALIBUR.core.excalibur import process_intent
            return process_intent
        except Exception as e:
            logger.warning("Excalibur import failed: %s; using local fallback", e)
            return _local_excalibur_process_intent

    elif name == "think_tank":
        from agora.orchestration.think_tank import ThinkTankOrchestrator
        return ThinkTankOrchestrator()

    elif name == "council_debate":
        from reasoning.council_debate import CouncilDebate
        return CouncilDebate

    return None


# ── Public API ───────────────────────────────────────────────────────

def get_iron_gate():
    return _load_component("iron_gate")


def get_warden():
    return _load_component("warden")


def get_zenith():
    return _load_component("zenith")


def get_mgv():
    return _load_component("mgv")


def get_os_cartridges() -> dict:
    return _load_component("cartridges_os") or {}


def get_vault_class():
    return _load_component("vault")


def get_titan_omega() -> Optional[dict]:
    """Get Titan Omega memory system (graph + flux)."""
    return _load_component("titan_omega")


def get_planning_engine():
    """Get the kernel planning engine."""
    return _load_component("planning_engine")


def get_excalibur():
    """Get the Excalibur process_intent function."""
    return _load_component("excalibur")


def get_think_tank():
    """Get the Think Tank orchestrator."""
    return _load_component("think_tank")


def get_council_debate():
    """Get the Council Debate class."""
    return _load_component("council_debate")


# ── Risk Assessment (bridged) ───────────────────────────────────────

def assess_risk_bridged(directive: str) -> dict:
    """Use Zenith Scanner if available, otherwise fall back to local merlin."""
    zenith = get_zenith()
    if zenith:
        scan = zenith.scan(directive)
        if not scan["safe"]:
            return {
                "level": "CRITICAL",
                "triggers": scan["findings"],
                "requires_approval": True,
                "source": "zenith",
            }

    # Warden check is informational only — policy.yaml may not have
    # CLI directives in its allow list, so we don't gate on it.
    # The Zenith scan above catches hostile patterns.

    # Fall back to local regex matching (inlined to avoid circular import)
    import re
    local_patterns = [
        r"\bdelete\b", r"\bremove\b", r"\bdrop\b", r"\bdestroy\b", r"\bformat\b",
        r"rm\s+-rf", r"\bsudo\b", r"chmod\s+777", r"\bprod\b", r"\bproduction\b",
        r"\bdeploy\b", r"push\s+--force", r"reset\s+--hard",
    ]
    text = directive.lower()
    triggers = [p for p in local_patterns if re.search(p, text)]
    level = "LOW"
    if len(triggers) >= 2:
        level = "CRITICAL"
    elif len(triggers) == 1:
        level = "HIGH"
    return {
        "level": level,
        "triggers": triggers,
        "requires_approval": level in ("HIGH", "CRITICAL"),
        "source": "local",
    }


# ── MGV Validation (bridged) ────────────────────────────────────────

def mgv_validate(directive: str) -> dict:
    """Run MGV monitor on a directive if kernel available."""
    mgv = get_mgv()
    if mgv:
        return mgv.monitor(directive)
    return {"complexity": "UNKNOWN", "risk_level": "UNKNOWN", "requires_reasoning": False}


# ── Iron Gate Approval (bridged) ────────────────────────────────────

def iron_gate_approve(action_summary: str, risk_level: str) -> bool:
    """Request Iron Gate approval for high-risk actions."""
    gate = get_iron_gate()
    if gate:
        action_id = gate.request_approval({
            "summary": action_summary,
            "riskLevel": risk_level,
            "source": "camelot_cli",
        })
        # In CLI mode, prompt user directly
        try:
            confirm = input(f"    [IRON GATE] Approve action {action_id[:8]}? (y/N): ").strip().lower()
        except EOFError:
            # Non-interactive — deny by default
            gate.verify_response(action_id, False, "")
            return False
        if confirm == "y":
            sig = os.environ.get("CAMELOT_HITL_CONFIRM_TOKEN", "CLI_APPROVED")
            return gate.verify_response(action_id, True, sig)
        else:
            gate.verify_response(action_id, False, "")
            return False
    return True  # No gate = allow


# ── Provenance Ledger (bridged) ──────────────────────────────────────

def log_provenance(entity: str, event: str, status: str = "SUCCESS"):
    """Write to the real CAMELOT_OS provenance ledger."""
    if not LEDGER_PATH.exists():
        return
    try:
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        entry = f"| {timestamp} | {entity} | {event} | {status} |\n"
        with open(LEDGER_PATH, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception as e:
        logger.warning("Provenance ledger write failed: %s", e)


# ── Memory (bridged) ─────────────────────────────────────────────────

def memory_store(entity: str, event: str, session_id: str = "cli"):
    """Store an event in Titan Omega ephemeral flux memory."""
    omega = get_titan_omega()
    if omega and omega.get("flux"):
        content = f"[{entity}] {event}"
        omega["flux"].store_event(session_id, content)
        return True
    return False


def memory_query(pattern: dict) -> list:
    """Query the Titan Omega knowledge graph."""
    omega = get_titan_omega()
    if omega and omega.get("graph"):
        return omega["graph"].query(pattern)
    return []


def memory_add_node(node_data: dict) -> Optional[str]:
    """Add a node to the Titan Omega knowledge graph."""
    omega = get_titan_omega()
    if omega and omega.get("graph"):
        return omega["graph"].add_node(node_data)
    return None


def memory_get_session(session_id: str = "cli") -> list:
    """Get events from the current session's flux memory."""
    omega = get_titan_omega()
    if omega and omega.get("flux"):
        return omega["flux"].get_session_events(session_id)
    return []


# ── Planning (bridged) ───────────────────────────────────────────────

def create_plan(objective: str, tasks: list) -> Optional[dict]:
    """Create a plan via the kernel planning engine."""
    engine = get_planning_engine()
    if engine:
        return engine.create_plan(objective, tasks)
    return None


def get_next_action(plan_id: str) -> Optional[dict]:
    """Get next action from an active plan."""
    engine = get_planning_engine()
    if engine:
        return engine.get_next_action(plan_id)
    return None


def complete_task(plan_id: str, task_id: str) -> bool:
    """Mark a task as complete in a plan."""
    engine = get_planning_engine()
    if engine:
        return engine.complete_task(plan_id, task_id)
    return False


def export_plan(plan_id: str) -> Optional[dict]:
    """Export a plan as structured data."""
    engine = get_planning_engine()
    if engine:
        return engine.export_plan(plan_id)
    return None


# ── Excalibur (bridged) ──────────────────────────────────────────────

def kernel_process_intent(intent: str) -> dict:
    """Route an intent through the Excalibur kernel."""
    process_fn = get_excalibur()
    if process_fn:
        return process_fn(intent)
    return {"status": "unavailable", "message": "Excalibur kernel not loaded"}


# ── Warden Commands (bridged) ────────────────────────────────────────

def warden_command(cmd: str) -> str:
    """Execute a warden command (status, lockdown, unlock, audit)."""
    warden = get_warden()
    if not warden:
        return "Warden not available (CAMELOT_OS kernel not connected)"

    if cmd == "status":
        s = warden.get_status()
        lines = [
            f"  Lockdown: {'ACTIVE' if s.get('lockdown_mode') else 'inactive'}",
            f"  Recent Events: {s.get('recent_events', 0)}",
        ]
        return "\n".join(lines)
    elif cmd == "lockdown":
        warden.engage_lockdown()
        return "  Warden lockdown ENGAGED."
    elif cmd == "unlock":
        warden.disengage_lockdown()
        return "  Warden lockdown disengaged."
    elif cmd == "audit":
        log = warden.get_audit_log(20)
        if not log:
            return "  No security events recorded."
        lines = []
        for entry in log:
            lines.append(f"  [{entry.get('timestamp', '?')[:19]}] "
                         f"{entry.get('action', '?')} - {entry.get('result', '?')}")
        return "\n".join(lines)
    elif cmd.startswith("spotlight "):
        content = cmd[len("spotlight "):]
        return f"  Wrapped: {warden.spotlight(content)}"
    else:
        return "  Commands: status, lockdown, unlock, audit, spotlight <text>"


# ── Status ───────────────────────────────────────────────────────────

ALL_COMPONENTS = [
    "iron_gate", "warden", "zenith", "mgv", "cartridges_os", "vault",
    "titan_omega", "planning_engine", "excalibur", "think_tank", "council_debate",
]


def get_bridge_status() -> dict:
    """Return status of all bridged components."""
    status = {
        "os_available": _os_available,
        "os_root": str(CAMELOT_OS_ROOT),
        "components": {},
    }
    for c in ALL_COMPONENTS:
        loaded = _load_component(c)
        status["components"][c] = "active" if loaded else "unavailable"
    return status
