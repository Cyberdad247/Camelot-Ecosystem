# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — TypeSafe AI Jev (System 1) Integration Client
r"""
TypeSafe AI (typesafe.ai) System 1 Decision & Routing Client.
============================================================
Forged by: SIR_GHOST (Privacy Scanner & Air-Gap Vault) & SIR_HELIOS (Spire Sentinel)
Domain: CAMELOT-OS System 1 Non-Autoregressive Fast Decisioning

TypeSafe AI's 'Jev' (founded by Diogo Almeida) is a non-autoregressive "System 1" model
for software automation, delivering:
- Up to 200x faster execution (<50ms decision cycles)
- 400x lower inference cost than autoregressive LLMs
- Parallel question sampling and schema-constrained decisions (choices, enums, scores)
- Deterministic routing, intent triage, and permission scoring without token-by-token generation

Security / Air-Gap Invariant:
- API Keys are strictly sourced from untracked environment variables (TYPESAFE_API_KEY, JEV_API_KEY).
- Keys are NEVER printed, logged, or serialized into telemetry streams.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger("TypeSafeJevClient")

DEFAULT_TYPESAFE_BASE_URL = os.environ.get("TYPESAFE_BASE_URL", "https://api.typesafe.ai/v1")
DEFAULT_JEV_MODEL = os.environ.get("TYPESAFE_MODEL", "jev-latest")
DEFAULT_TIMEOUT_SEC = float(os.environ.get("TYPESAFE_TIMEOUT_SEC", "1.2"))


@dataclass
class System1DecisionResult:
    """Represents the structured result of a TypeSafe Jev System 1 evaluation."""

    model: str
    decisions: Dict[str, Any]
    confidence_scores: Dict[str, float]
    latency_ms: float
    is_live_call: bool
    status: str  # "SUCCESS", "FALLBACK_HEURISTIC", "ERROR"
    error_message: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "decisions": self.decisions,
            "confidence_scores": self.confidence_scores,
            "latency_ms": round(self.latency_ms, 2),
            "is_live_call": self.is_live_call,
            "status": self.status,
            "error_message": self.error_message,
            "timestamp": self.timestamp,
        }


class TypeSafeJevClient:
    """Sovereign TypeSafe AI Jev System 1 Client for Camelot-OS."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = DEFAULT_TYPESAFE_BASE_URL,
        model: str = DEFAULT_JEV_MODEL,
        timeout_sec: float = DEFAULT_TIMEOUT_SEC,
    ):
        # Auto-load .env if key not in environment
        if not api_key and not os.environ.get("TYPESAFE_API_KEY") and not os.environ.get("JEV_API_KEY"):
            try:
                import dotenv
                from pathlib import Path
                env_path = Path(__file__).resolve().parents[3] / ".env"
                if env_path.exists():
                    dotenv.load_dotenv(dotenv_path=env_path)
                else:
                    dotenv.load_dotenv()
            except Exception:
                pass

        # Resolve API key from arguments or environment
        self._api_key = (
            api_key
            or os.environ.get("TYPESAFE_API_KEY")
            or os.environ.get("TYPESAFE_AI_API_KEY")
            or os.environ.get("JEV_API_KEY")
            or ""
        ).strip()
        self.base_url = base_url.rstrip("/")
        self.default_model = model
        self.timeout_sec = timeout_sec

    @property
    def has_api_key(self) -> bool:
        """Check if an API key is available without exposing it."""
        return bool(self._api_key and len(self._api_key) > 8)

    def mask_key(self) -> str:
        """Safe masked display of key for telemetry."""
        if not self.has_api_key:
            return "UNSET"
        if len(self._api_key) <= 12:
            return "***"
        return f"{self._api_key[:6]}...{self._api_key[-4:]}"

    def decide(
        self,
        state: str,
        questions: Dict[str, Any],
        model: Optional[str] = None,
    ) -> System1DecisionResult:
        """
        Execute parallel structured decision sampling via TypeSafe Jev.
        
        Args:
            state: Contextual state string (e.g. current intent, prompt, code diff, or environment state).
            questions: Dictionary defining questions to evaluate.
                       Format:
                       {
                           "route": {"type": "choice", "options": ["forge", "codex", "sentinel", "hermes"]},
                           "risk_score": {"type": "score", "min": 0, "max": 100},
                           "requires_hitl": {"type": "boolean"}
                       }
            model: Model name override (defaults to 'jev-latest').
        """
        start_t = time.perf_counter()
        target_model = model or self.default_model

        # If no API key configured, use high-speed heuristic fallback
        if not self.has_api_key:
            return self._heuristic_fallback(state, questions, target_model, start_t, "API key not configured")

        payload = {
            "model": target_model,
            "state": state,
            "questions": questions,
        }

        # Attempt live API call to /systemone endpoint, falling back to /decisions
        endpoints = [
            f"{self.base_url}/systemone",
            f"{self.base_url}/decisions",
            f"{self.base_url}/chat/completions",
        ]

        last_error = None
        for endpoint in endpoints:
            try:
                data_bytes = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    endpoint,
                    data=data_bytes,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self._api_key}",
                        "User-Agent": "CamelotOS-System1/10001",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=self.timeout_sec) as resp:
                    if resp.status == 200:
                        res_data = json.loads(resp.read().decode("utf-8"))
                        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
                        return self._parse_api_response(res_data, target_model, elapsed_ms)
            except urllib.error.HTTPError as he:
                last_error = f"HTTP {he.code}: {he.reason}"
                # If 401 or 403, do not loop other endpoints
                if he.code in (401, 403):
                    break
            except Exception as ex:
                last_error = str(ex)

        # In case of API failure or network isolation, return resilient local heuristic
        return self._heuristic_fallback(state, questions, target_model, start_t, last_error)

    def classify_route(
        self,
        prompt: str,
        candidate_routes: List[str],
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Classify which candidate route best matches a user prompt in sub-50ms."""
        questions = {
            "selected_route": {
                "type": "choice",
                "options": candidate_routes,
            },
            "confidence": {
                "type": "score",
                "min": 0.0,
                "max": 1.0,
            },
        }
        res = self.decide(prompt, questions, model=model)
        selected = res.decisions.get("selected_route")
        if not selected or selected not in candidate_routes:
            selected = candidate_routes[0] if candidate_routes else "default"

        return {
            "selected_route": selected,
            "confidence": res.confidence_scores.get("confidence", 0.95),
            "latency_ms": res.latency_ms,
            "status": res.status,
            "model": res.model,
        }

    def triage_risk(
        self,
        task: str,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fast System 1 triage for safety, permissions, and Iron Gate requirements.
        Returns:
            - risk_level: R0 (Trivial), R1 (Read-only), R2 (Mutation), R3 (Destructive/Privileged), R4 (Critical)
            - requires_hitl: bool
            - rationale: str
        """
        state = f"Task: {task}\nContext: {context or ''}"
        questions = {
            "risk_level": {
                "type": "choice",
                "options": ["R0_TRIVIAL", "R1_READONLY", "R2_MUTATION", "R3_PRIVILEGED", "R4_CRITICAL"],
            },
            "requires_hitl": {
                "type": "boolean",
            },
            "confidence": {
                "type": "score",
                "min": 0.0,
                "max": 1.0,
            },
        }
        res = self.decide(state, questions)
        risk_level = res.decisions.get("risk_level", "R1_READONLY")
        requires_hitl = res.decisions.get("requires_hitl", False)

        return {
            "task": task,
            "risk_level": risk_level,
            "requires_hitl": requires_hitl,
            "latency_ms": res.latency_ms,
            "model": res.model,
            "status": res.status,
        }

    def _parse_api_response(
        self,
        data: Dict[str, Any],
        model: str,
        latency_ms: float,
    ) -> System1DecisionResult:
        """Parse raw response from TypeSafe AI API."""
        decisions = data.get("decisions") or data.get("answers") or {}
        confidence = data.get("confidence_scores") or {}

        # If OpenAI compatibility mode returned choices
        if not decisions and "choices" in data:
            try:
                choice_text = data["choices"][0]["message"]["content"]
                parsed = json.loads(choice_text)
                if isinstance(parsed, dict):
                    decisions = parsed
            except Exception:
                decisions = {"raw_output": data["choices"][0]["message"]["content"]}

        return System1DecisionResult(
            model=data.get("model", model),
            decisions=decisions,
            confidence_scores=confidence,
            latency_ms=latency_ms,
            is_live_call=True,
            status="SUCCESS",
        )

    def _heuristic_fallback(
        self,
        state: str,
        questions: Dict[str, Any],
        model: str,
        start_t: float,
        error_msg: Optional[str] = None,
    ) -> System1DecisionResult:
        """
        Local deterministic System 1 heuristic evaluation.
        Ensures sub-1ms non-blocking resolution when offline, testing, or during API failover.
        """
        state_lower = state.lower()
        decisions: Dict[str, Any] = {}
        confidences: Dict[str, float] = {}

        # Expanded critical safety keywords
        hitl_triggers = [
            "delete", "remove", "wipe", "force", "drop", "destroy", "purge", "secret",
            "rm ", "rm -rf", "rmdir", "format", "truncate", "shutdown", "reboot", "kill", "eval"
        ]
        mutation_triggers = ["create", "write", "update", "edit", "patch", "scaffold", "build", "forge"]
        has_hitl_trigger = any(trig in state_lower for trig in hitl_triggers)
        has_mutation_trigger = any(trig in state_lower for trig in mutation_triggers)

        for q_key, q_spec in questions.items():
            q_type = q_spec.get("type", "choice")
            if q_type == "choice":
                options = q_spec.get("options", [])
                matched_option = None

                # Special triage logic for risk level choices
                if "risk" in q_key.lower():
                    if has_hitl_trigger:
                        for crit in ["R4_CRITICAL", "R3_PRIVILEGED", "CRITICAL", "HIGH"]:
                            if crit in options:
                                matched_option = crit
                                break
                    elif has_mutation_trigger:
                        for mut in ["R2_MUTATION", "MEDIUM", "MUTATION"]:
                            if mut in options:
                                matched_option = mut
                                break
                    else:
                        for ro in ["R1_READONLY", "R0_TRIVIAL", "LOW", "READONLY"]:
                            if ro in options:
                                matched_option = ro
                                break

                if not matched_option:
                    for opt in options:
                        opt_clean = str(opt).lower().replace("_", " ")
                        if opt_clean in state_lower or str(opt).lower() in state_lower:
                            matched_option = opt
                            break

                if not matched_option and options:
                    matched_option = options[0]

                decisions[q_key] = matched_option
                confidences[q_key] = 0.95 if matched_option else 0.85

            elif q_type in ("boolean", "bool"):
                decisions[q_key] = has_hitl_trigger if "hitl" in q_key.lower() else False
                confidences[q_key] = 0.92

            elif q_type == "score":
                min_v = q_spec.get("min", 0.0)
                max_v = q_spec.get("max", 100.0)
                if "risk" in q_key.lower():
                    score = 95.0 if has_hitl_trigger else (50.0 if has_mutation_trigger else 10.0)
                else:
                    score = min(max_v, max(min_v, float(len(state.split())) * 2.5))
                decisions[q_key] = score
                confidences[q_key] = 0.90

            else:
                decisions[q_key] = "resolved"
                confidences[q_key] = 0.80

        elapsed_ms = (time.perf_counter() - start_t) * 1000.0
        return System1DecisionResult(
            model=f"{model} (heuristic_fallback)",
            decisions=decisions,
            confidence_scores=confidences,
            latency_ms=elapsed_ms,
            is_live_call=False,
            status="FALLBACK_HEURISTIC",
            error_message=error_msg,
        )


_typesafe_jev_singleton: Optional[TypeSafeJevClient] = None


def get_typesafe_jev_client() -> TypeSafeJevClient:
    """Return singleton instance of TypeSafeJevClient."""
    global _typesafe_jev_singleton
    if _typesafe_jev_singleton is None:
        _typesafe_jev_singleton = TypeSafeJevClient()
    return _typesafe_jev_singleton
