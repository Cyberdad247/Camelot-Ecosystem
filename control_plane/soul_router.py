"""Soul Router — MFOE Routing Matrix for Camelot Foundry Council.

Implements the Soul Equation: S_omega = alpha*V + beta*M + gamma*P + delta*E
Routes intents to the optimal Knight engine based on weighted tensor scoring.

Weight locks are mathematically enforced — W_orchestration=0.85 for Sir Boris
is a Titanium Law invariant, not a tunable parameter.
"""

from __future__ import annotations

import os
import sys
import importlib.util
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

try:
    import requests  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover - fallback path depends on local env
    requests = None
    import httpx

# Add KERNEL to path for telemetry import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    _TELEMETRY_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "01_KERNEL", "senses", "telemetry_client.py")
    )
    _TELEMETRY_SPEC = importlib.util.spec_from_file_location(
        "camelot_telemetry_client",
        _TELEMETRY_PATH,
    )
    if _TELEMETRY_SPEC is None or _TELEMETRY_SPEC.loader is None:
        raise ImportError(f"Unable to load telemetry client from {_TELEMETRY_PATH}")
    _TELEMETRY_MODULE = importlib.util.module_from_spec(_TELEMETRY_SPEC)
    _TELEMETRY_SPEC.loader.exec_module(_TELEMETRY_MODULE)
    RotelClient = _TELEMETRY_MODULE.RotelClient
    KINETIC_TOKEN = _TELEMETRY_MODULE.KINETIC_TOKEN
    logger = RotelClient("soul_router")
except Exception:
    # Fallback if kernel path is not resolved
    class DummyLogger:
        def info(self, *args, **kwargs): pass
    logger = DummyLogger()
    KINETIC_TOKEN = os.getenv("CAMELOT_KINETIC_TOKEN", "default-token")

SALTARE_URL = os.getenv("SALTARE_URL", "http://127.0.0.1:8080/api/v1/route")
# OmniRoute routing logic lives in cli_intercept.py — reads omniroute.json,
# resolves all cloud engines to upstream.cliproxy (CLIProxyAPI :8080).
# Port :20128 is not a standalone server; cli_intercept IS the OmniRoute layer.
CLIPROXY_URL = os.getenv("CLIPROXY_URL", "http://127.0.0.1:8080/v1")


# ---------------------------------------------------------------------------
# Foundry Council Engine Registry (Weight-Locked)
# ---------------------------------------------------------------------------

class EngineWeight(float, Enum):
    """Immutable weight locks per Titanium Law. DO NOT MODIFY."""
    W_ORCHESTRATION = 0.85   # Sir Boris  — Claude Code
    W_COGNITIVE     = 0.88   # Sir Alex  — Cognitive orchestration
    W_CONTEXT       = 0.90   # Sir Helio  — Gemini CLI
    W_VELOCITY      = 0.75   # Sir Codex  — OpenAI Codex
    W_PRIVACY       = 1.00   # Sir Ghost  — Local Qwen 3.5
    W_SOVEREIGNTY   = 0.80   # Sir Liberte — Open Source
    W_KINETIC       = 0.70   # Sir Forge  — Open Coder (local)
    W_BRIDGE        = 0.78   # Sir Link  — UI/bridge handoff coordination
    W_MEMORY        = 0.92   # Sir Mnemo — Integration Brain routing
    W_LINEAR        = 0.95   # Sir Ouroboros — Linear SSM (Infinite Context)


@dataclass(frozen=True)
class KnightEngine:
    """Immutable engine definition for a Foundry Council Knight."""
    knight_id: str
    engine: str
    weight: EngineWeight
    function: str
    privacy_level: float = 0.0  # 0.0 = cloud OK, 1.0 = air-gapped only


# The Foundry Council — frozen registry
FOUNDRY_COUNCIL: tuple[KnightEngine, ...] = (
    KnightEngine("sir_boris",   "claude_code",  EngineWeight.W_ORCHESTRATION,
                 "Architecture, Colony Command, 13-Agent Critique", privacy_level=0.3),
    KnightEngine("sir_alex",    "claude_code",  EngineWeight.W_COGNITIVE,
                 "Cognitive cartridge orchestration, decision framing, bridge governance", privacy_level=0.3),
    KnightEngine("sir_helio",   "gemini_cli",   EngineWeight.W_CONTEXT,
                 "1M+ token context mapping", privacy_level=0.2),
    KnightEngine("sir_codex",   "openai_codex", EngineWeight.W_VELOCITY,
                 "High-velocity code generation", privacy_level=0.2),
    KnightEngine("sir_forge",   "open_coder",   EngineWeight.W_KINETIC,
                 "L2 Kinetic Code Generation — local open-weight", privacy_level=0.7),
    KnightEngine("sir_link",    "gemini_cli",   EngineWeight.W_BRIDGE,
                 "Bridge coordination across UI, cloud brain, and local terminal", privacy_level=0.2),
    KnightEngine("sir_ghost",   "local_qwen",   EngineWeight.W_PRIVACY,
                 "Zero-Trust, air-gapped execution", privacy_level=1.0),
    KnightEngine("sir_liberte", "open_source",   EngineWeight.W_SOVEREIGNTY,
                 "Anti-vendor lock-in, sovereign execution", privacy_level=0.5),
    KnightEngine("sir_mnemo",   "integration_brain", EngineWeight.W_MEMORY,
                 "Memory routing — ST/LT/both tier scoring for Integration Brain", privacy_level=0.4),
    KnightEngine("sir_ouroboros", "ouroboros_ssm", EngineWeight.W_LINEAR,
                 "Linear Reasoning Tier — O(N) scaling for infinite context (Mamba-3)", privacy_level=0.1),
)

# Free provider pool — all routed through CLIProxyAPI :8080
OMNI_PROVIDER_MAP: dict[str, dict[str, str]] = {
    "kiro": {"model": "kr/claude-3-5-sonnet", "knight": "sir_boris"},
    "qoder": {"model": "if/deepseek-r1", "knight": "sir_syntax"},
    "groq": {"model": "groq/llama-3-70b", "knight": "sir_forge"},
    "cerebras": {"model": "cerebras/llama-3-1-70b", "knight": "sir_kronos"},
    "longcat": {"model": "lc/longcat-flash-lite", "knight": "sir_helio"},
}

# Special Knight Routing Overrides
KNIGHT_STRATEGY_OVERRIDE: dict[str, str] = {
    "sir_helio": "context-optimized",  # Force 1M+ token path
}

# Privacy override keywords — triggers immediate reroute to air-gapped engine
PRIVACY_KEYWORDS: frozenset[str] = frozenset({
    "secret", "local", "private", "credential", "key", "password",
})

_ENGINE_MAP = {e.knight_id: e for e in FOUNDRY_COUNCIL}


# ---------------------------------------------------------------------------
# Intent Tensor (VIDENEPTUS S4 Strategic)
# ---------------------------------------------------------------------------

@dataclass
class IntentTensor:
    """Multi-dimensional intent scoring vector.

    V = velocity     (urgency / time pressure)
    M = magnitude    (scope / complexity 0.0-1.0)
    P = privacy      (data sensitivity 0.0-1.0)
    E = environment  (execution weight from engine matrix)
    """
    velocity: float = 0.5
    magnitude: float = 0.5
    privacy: float = 0.0
    environment: float = 0.0

    def __post_init__(self):
        for attr in ("velocity", "magnitude", "privacy", "environment"):
            val = getattr(self, attr)
            if not 0.0 <= val <= 1.0:
                raise ValueError(f"{attr} must be in [0.0, 1.0], got {val}")


# Soul Equation coefficients (tuned by Merlin_Omega)
_ALPHA = 0.20   # velocity weight
_BETA  = 0.35   # magnitude weight
_GAMMA = 0.30   # privacy weight
_DELTA = 0.15   # environment weight


def soul_equation(tensor: IntentTensor) -> float:
    """S_omega = alpha*V + beta*M + gamma*P + delta*E"""
    return (
        _ALPHA * tensor.velocity
        + _BETA * tensor.magnitude
        + _GAMMA * tensor.privacy
        + _DELTA * tensor.environment
    )


# ---------------------------------------------------------------------------
# Keyword -> Knight mapping (mirrors control_plane/main.py KNIGHT_ROUTES)
# ---------------------------------------------------------------------------

KEYWORD_ROUTES: dict[str, str] = {
    "orchestration": "sir_boris",
    "architecture":  "sir_boris",
    "colony":        "sir_boris",
    "critique":      "sir_boris",
    "vocal":         "sir_boris",
    "cognitive":     "sir_alex",
    "reasoning":     "sir_alex",
    "critical":      "sir_alex",
    "decision":      "sir_alex",
    "bridge":        "sir_link",
    "handoff":       "sir_link",
    "terminal":      "sir_link",
    "ui":            "sir_link",
    "memory":        "sir_mnemo",
    "remember":      "sir_mnemo",
    "archive":       "sir_mnemo",
    "recall":        "sir_mnemo",
    "store":         "sir_mnemo",
    "synthesize":    "sir_mnemo",
    "persist":       "sir_mnemo",
    "technical":     "sir_forge",
    "scaffold":      "sir_forge",
    "code_gen":      "sir_forge",
    "security_review": "sir_sentinel",
    "audit":         "sir_sentinel",
    "financial":     "sir_valerian",
    "roi":           "sir_valerian",
    # SIR_CODEX — high-velocity code generation via CLIProxyAPI
    "velocity":      "sir_codex",
    "rapid_proto":   "sir_codex",
    "boilerplate":   "sir_codex",
    "prototype":     "sir_codex",
    # SIR_HELIO — 1M+ context mapping via Gemini CLI -> CLIProxyAPI
    "context_map":   "sir_helio",
    "full_repo":     "sir_helio",
    "1m_context":    "sir_helio",
    "cloud_burst":   "sir_helio",
    "ouroboros":     "sir_ouroboros",
    "mamba":         "sir_ouroboros",
    "linear_scaling": "sir_ouroboros",
    "infinite_context": "sir_ouroboros",
    # Browser Nano-Knights
    "browse":        "nano_apis",
    "//browse":      "nano_apis",
    "navigate":      "nano_apis",
    "scrape":        "nano_apis",
    "crawl":         "nano_apis",
    "browser_audit": "nano_sentinel",
    "browser_debug": "nano_debug",
    "browser_code":  "nano_syntax",
}


# ---------------------------------------------------------------------------
# Soul Router
# ---------------------------------------------------------------------------

@dataclass
class RouteDecision:
    """Result of a routing decision."""
    knight_id: str
    engine: str
    weight: float
    score: float
    tensor: IntentTensor
    reason: str
    privacy_override: bool = False


class SoulRouter:
    """MFOE Routing Matrix — routes intents to the optimal Foundry Knight.

    Privacy Override: If privacy >= 0.8, ALL traffic reroutes to Sir Ghost
    regardless of keyword match. This is a Titanium Law invariant.

    Complexity Spike: If magnitude >= 0.8, forces multi-agent plan output
    (VIDENEPTUS S4_Strategic tensor maxes out).
    """

    def __init__(self):
        self._engines = _ENGINE_MAP
        self._routes = KEYWORD_ROUTES

    def saltare_route(self, intent: str, velocity: float, magnitude: float, privacy: float) -> Optional[RouteDecision]:
        """Delegate routing to the Go-based Saltare gateway."""
        payload = {
            "intent": intent,
            "velocity": velocity,
            "magnitude": magnitude,
            "privacy": privacy
        }
        headers = {
            "X-API-Key": KINETIC_TOKEN
        }
        try:
            # Short timeout to maintain Kinetic Purity velocity
            if requests is not None:
                resp = requests.post(SALTARE_URL, json=payload, headers=headers, timeout=0.2)
                status_code = resp.status_code
                data = resp.json() if status_code == 200 else None
            else:
                with httpx.Client(timeout=0.2) as client:
                    resp = client.post(SALTARE_URL, json=payload, headers=headers)
                status_code = resp.status_code
                data = resp.json() if status_code == 200 else None
            if status_code == 200 and data is not None:
                t = data.get("tensor", {})
                return RouteDecision(
                    knight_id=data["knight_id"],
                    engine=data["engine"],
                    weight=data["weight"],
                    score=data["score"],
                    tensor=IntentTensor(
                        velocity=t.get("velocity", 0.0),
                        magnitude=t.get("magnitude", 0.0),
                        privacy=t.get("privacy", 0.0),
                        environment=t.get("environment", 0.0)
                    ),
                    reason=f"SALTARE_GO: {data['reason']}",
                    privacy_override=data.get("privacy_override", False)
                )
        except Exception:
            return None
        return None

    def route(
        self,
        intent: str,
        *,
        velocity: float = 0.5,
        magnitude: float = 0.5,
        privacy: float = 0.0,
        linear_need: float = 0.0,
        _apee_compiled: bool = False,
    ) -> RouteDecision:
        """Route an intent string to the optimal Knight.

        If called externally with raw intent, pass through AnyaGate first
        (unless _apee_compiled=True, indicating AnyaGate already preprocessed).
        Tries Saltare (Go) first, falls back to local Python logic.
        """
        # Titanium Law #11 — ANYA_IS_THE_GATE
        # AnyaGate calls route() internally with _apee_compiled=True to avoid recursion.
        # External callers receive a compiled intent; we honour it as-is.

        # 🚀 Try Saltare Ascension Route first
        decision = self.saltare_route(intent, velocity, magnitude, privacy)
        if decision:
            # 📡 Telemetry: Log the Saltare decision
            logger.info(
                f"ROUTE_DECISION: {decision.knight_id} selected via SALTARE",
                intent=intent[:100],
                knight=decision.knight_id,
                engine=decision.engine,
                source="saltare"
            )
            return decision

        # 🐢 Fallback to local Python logic
        intent_lower = intent.lower()

        # --- Switchboard: Sir Link availability check (cache-only, zero probe cost) ---
        try:
            _cp_dir = os.path.dirname(__file__)
            if _cp_dir not in sys.path:
                sys.path.insert(0, _cp_dir)
            from switchboard import route_sync as _sb_route_sync
            # If preferred knight is dark, let Sir Link negotiate fallback
            keyword_match = next((kn for kw, kn in self._routes.items() if kw in intent_lower), None)
            if keyword_match:
                terminal = _sb_route_sync(keyword_match)
                if terminal and terminal.id != keyword_match and terminal.status == "live":
                    logger.info(f"SWITCHBOARD: {keyword_match} dark → rerouted to {terminal.id}")
                    intent_lower = intent_lower.replace(keyword_match, terminal.id)
        except Exception:
            pass   # switchboard optional — never blocks routing

        # --- Privacy Override (Titanium Law) ---
        # Trigger 1: Explicit privacy score >= 0.8
        # Trigger 2: Intent contains privacy keywords (secret, local, private, etc.)
        keyword_privacy = any(kw in intent_lower for kw in PRIVACY_KEYWORDS)
        if privacy >= 0.8 or keyword_privacy:
            effective_privacy = max(privacy, 0.9 if keyword_privacy else privacy)
            ghost = self._engines["sir_ghost"]
            tensor = IntentTensor(velocity, magnitude, effective_privacy, float(ghost.weight))
            trigger = (
                f"keyword_match={[k for k in PRIVACY_KEYWORDS if k in intent_lower]}"
                if keyword_privacy else f"p={privacy}"
            )
            return RouteDecision(
                knight_id="sir_ghost",
                engine=ghost.engine,
                weight=float(ghost.weight),
                score=soul_equation(tensor),
                tensor=tensor,
                reason=f"PRIVACY_OVERRIDE: {trigger} -> Sir Ghost (air-gapped)",
                privacy_override=True,
            )

        # --- Linear Reasoning Tier (v1000) ---
        # Trigger: Explicit linear scaling need >= 0.8
        if linear_need >= 0.8:
            ouro = self._engines["sir_ouroboros"]
            tensor = IntentTensor(velocity, magnitude, privacy, float(ouro.weight))
            return RouteDecision(
                knight_id="sir_ouroboros",
                engine=ouro.engine,
                weight=float(ouro.weight),
                score=soul_equation(tensor),
                tensor=tensor,
                reason=f"LINEAR_TIER_TRIGGER: linear_need={linear_need} -> Sir Ouroboros (SSM)",
            )

        # --- Keyword matching ---
        matched_knight = None
        for keyword, knight_id in self._routes.items():
            if keyword in intent_lower:
                matched_knight = knight_id
                break

        # --- Tensor scoring across all eligible engines ---
        if matched_knight and matched_knight in self._engines:
            engine = self._engines[matched_knight]
            tensor = IntentTensor(velocity, magnitude, privacy, float(engine.weight))
            score = soul_equation(tensor)
            reason = f"KEYWORD_MATCH: '{keyword}' -> {matched_knight} (W={engine.weight})"
        else:
            # No keyword match — score all council engines, pick highest
            best_score = -1.0
            best_engine: Optional[KnightEngine] = None
            best_tensor: Optional[IntentTensor] = None

            for engine in FOUNDRY_COUNCIL:
                # Skip air-gapped engine for non-private intents
                if engine.privacy_level >= 0.8 and privacy < 0.3:
                    continue
                t = IntentTensor(velocity, magnitude, privacy, float(engine.weight))
                s = soul_equation(t)
                if s > best_score:
                    best_score = s
                    best_engine = engine
                    best_tensor = t

            if best_engine is None:
                # Fallback: Sir Boris always catches
                best_engine = self._engines["sir_boris"]
                best_tensor = IntentTensor(velocity, magnitude, privacy,
                                           float(best_engine.weight))
                best_score = soul_equation(best_tensor)

            matched_knight = best_engine.knight_id
            engine = best_engine
            tensor = best_tensor
            score = best_score
            reason = f"TENSOR_SCORED: S_omega={score:.4f} -> {matched_knight} (W={engine.weight})"

        # --- Complexity spike: force multi-agent plan ---
        if magnitude >= 0.8:
            reason += " | COMPLEXITY_SPIKE: c>=0.8, forcing multi-agent plan output"

        decision = RouteDecision(
            knight_id=matched_knight,
            engine=engine.engine,
            weight=float(engine.weight),
            score=score,
            tensor=tensor,
            reason=reason,
        )

        # 📡 Telemetry: Log the decision to Rotel
        logger.info(
            f"ROUTE_DECISION: {matched_knight} selected for intent",
            intent=intent[:100],
            knight=matched_knight,
            engine=engine.engine,
            score=score,
            reason=reason
        )

        return decision

    def get_engine(self, knight_id: str) -> Optional[KnightEngine]:
        """Lookup a knight engine by ID."""
        return self._engines.get(knight_id)

    def verify_weight_lock(self) -> bool:
        """Verify W_orchestration=0.85 invariant. Returns True if intact."""
        boris = self._engines.get("sir_boris")
        return boris is not None and float(boris.weight) == 0.85
