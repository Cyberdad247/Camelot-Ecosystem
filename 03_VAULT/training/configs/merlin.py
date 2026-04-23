"""Merlin Omega - Knight Router and Risk Assessment.

Routes compiled intents to the appropriate knight.
Integrates with CAMELOT_OS kernel when available:
  - Zenith Scanner for hostile pattern detection
  - Warden for zero-trust permission verification
  - Iron Gate for HITL approval on critical actions
  - MGV Engine for complexity analysis
Falls back to local pattern matching when kernel is unavailable.
"""

import re

KNIGHT_MAP = {
    "PLAN": "Sir Systema",
    "CREATE": "Sir Forge",
    "RESEARCH": "Lady Apis",
    "DESIGN": "Lady Muse",
    "SECURE": "Sir Zenith",
    "AUDIT": "Sir Sentinel",
    "DEBUG": "Sir Debug",
    "EVOLVE": "Agenteer",
}

KNIGHT_MODULES = {
    "Sir Systema": "architect",
    "Sir Forge": "coder",
    "Lady Apis": "researcher",
    "Lady Muse": "creative",
    "Sir Zenith": "warden",
    "Sir Sentinel": "sentinel",
    "Sir Debug": "debug",
    "Agenteer": "agenteer",
}

# Local fallback risk patterns (word-boundary regex)
LOCAL_RISK_PATTERNS = [
    r"\bdelete\b", r"\bremove\b", r"\bdrop\b", r"\bdestroy\b", r"\bformat\b",
    r"rm\s+-rf", r"\bsudo\b", r"chmod\s+777", r"\bprod\b", r"\bproduction\b",
    r"\bdeploy\b", r"push\s+--force", r"reset\s+--hard",
]


def assess_risk(directive: str) -> dict:
    """Evaluate directive risk level.

    Uses CAMELOT_OS Zenith Scanner + Warden when available,
    falls back to local regex matching.
    """
    try:
        from bridge import assess_risk_bridged
        return assess_risk_bridged(directive)
    except ImportError:
        pass

    # Local fallback
    text = directive.lower()
    triggers = [p for p in LOCAL_RISK_PATTERNS if re.search(p, text)]
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


def route(compiled_intent: dict) -> dict:
    """Route a compiled intent to the appropriate knight.

    Enriches routing with MGV complexity analysis when kernel is available.
    """
    intent = compiled_intent["intent"]
    knight = KNIGHT_MAP.get(intent, "Sir Forge")
    module = KNIGHT_MODULES.get(knight, "coder")
    risk = assess_risk(compiled_intent["directive"])

    # Enrich with MGV analysis if available
    mgv_analysis = None
    try:
        from bridge import mgv_validate
        mgv_analysis = mgv_validate(compiled_intent["directive"])
    except ImportError:
        pass

    return {
        "knight": knight,
        "module": module,
        "risk": risk,
        "intent": compiled_intent,
        "mgv": mgv_analysis,
    }


def verify_registry():
    """Check that KNIGHT_MAP and KNIGHT_MODULES are consistent."""
    errors = []
    for intent, knight in KNIGHT_MAP.items():
        if knight not in KNIGHT_MODULES:
            errors.append(f"Knight '{knight}' (intent={intent}) missing from KNIGHT_MODULES")
    return errors
