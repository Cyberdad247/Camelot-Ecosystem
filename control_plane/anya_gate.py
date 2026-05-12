# -*- coding: utf-8 -*-
"""
Anya_Omega — APEE v6.5 Sovereign Gate
======================================
ANYA_IS_THE_GATE. Titanium Law #11.

Every intent enters through this pipeline. Every output exits through it.
No knight receives a raw prompt. No response returns unvalidated.

Pipeline: PARSE -> ENRICH -> COMPILE -> ROUTE -> VALIDATE
"""

from __future__ import annotations

import os
import re
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).parent.parent

# ---------------------------------------------------------------------------
# Stage output dataclasses
# ---------------------------------------------------------------------------

@dataclass
class ParseResult:
    intent_type: str          # BUILD | RESEARCH | AUDIT | ROUTE | QUERY | FORGE | HEAL
    raw: str
    entities: list[str]
    constraints: list[str]
    complexity: float         # 0.0-1.0
    privacy: float            # 0.0-1.0
    velocity: float           # 0.0-1.0 (urgency)
    ambiguity_stripped: str   # cleaned intent with noise removed


@dataclass
class EnrichResult:
    domain: str               # go/binary | python/api | security | voice | infra | research
    cartridge_hint: str       # matching cartridge name
    ukg_refs: list[str]       # UKG node IDs relevant to intent
    context_tags: list[str]   # active service endpoints, personas
    magnitude: float          # derived from complexity + domain weight


@dataclass
class TitanPrompt:
    directive: str            # the compiled dense machine directive
    target_layer: str         # L1-L7
    execution_mode: str       # KINETIC | SWARM | ORACLE | FORGE | SENTINEL
    constraints_encoded: list[str]


@dataclass
class ValidationResult:
    passed: bool
    issues: list[str]
    iron_gate: str            # CLEARED | HITL_REQUIRED | BLOCKED
    net_lines_estimate: int
    requires_briefing: bool


@dataclass
class APEEResult:
    """Full APEE v6.5 pipeline result — the compiled artifact from Anya's gate."""
    raw_intent: str
    parse: ParseResult
    enrich: EnrichResult
    titan: TitanPrompt
    route_knight: str
    route_engine: str
    route_score: float
    route_reason: str
    validation: ValidationResult
    pipeline_ms: float

    def render(self) -> str:
        """Returns the visible Anya pipeline block for display in responses."""
        sep = "─" * 54
        ig_color = "CLEARED" if self.validation.iron_gate == "CLEARED" else self.validation.iron_gate
        lines = [
            "",
            "🎭 ANYA_Omega — APEE v6.5 COMPILATION",
            sep,
            f"PARSE    | type={self.parse.intent_type}  complexity={self.parse.complexity:.2f}"
            f"  privacy={self.parse.privacy:.2f}",
            f"         | entities={self.parse.entities}",
            f"ENRICH   | domain={self.enrich.domain}  cartridge={self.enrich.cartridge_hint}"
            f"  magnitude={self.enrich.magnitude:.2f}",
            f"         | tags={self.enrich.context_tags}",
            f"COMPILE  | \"{self.titan.directive[:72]}\"",
            f"         | layer={self.titan.target_layer}  mode={self.titan.execution_mode}",
            f"ROUTE    | -> {self.route_knight.upper()} (W={self.route_score:.2f})",
            f"         | {self.route_reason}",
            f"VALIDATE | Iron Gate: {ig_color}  "
            f"briefing={'REQUIRED' if self.validation.requires_briefing else 'OK'}",
        ]
        if self.validation.issues:
            lines.append(f"         | issues={self.validation.issues}")
        lines += [sep, f"         pipeline: {self.pipeline_ms:.0f}ms", ""]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# APEE v6.5 Stage Implementations
# ---------------------------------------------------------------------------

_NOISE_PATTERNS = re.compile(
    r"\b(please|kindly|could you|can you|just|simply|basically|like|you know|"
    r"i think|maybe|perhaps|would you|hey|yo|boss)\b",
    re.IGNORECASE,
)

_INTENT_TYPE_MAP: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\b(build|compile|create|make|write|scaffold|forge|generate)\b", re.I), "BUILD"),
    (re.compile(r"\b(research|find|search|look up|investigate|analyze|analyse)\b", re.I), "RESEARCH"),
    (re.compile(r"\b(audit|review|security|scan|check|verify|validate)\b", re.I), "AUDIT"),
    (re.compile(r"\b(route|dispatch|send|assign|delegate)\b", re.I), "ROUTE"),
    (re.compile(r"\b(heal|fix|debug|repair|patch|resolve)\b", re.I), "HEAL"),
    (re.compile(r"\b(delete|remove|purge|clean|drop)\b", re.I), "FORGE"),
    (re.compile(r"\b(deploy|launch|start|boot|awaken|run)\b", re.I), "FORGE"),
]

_DOMAIN_MAP: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\b(go|golang|bubbletea|binary|compile|exe)\b", re.I), "go/binary"),
    (re.compile(r"\b(rust|cargo|axum|mcp)\b", re.I), "rust/kinetic"),
    (re.compile(r"\b(python|fastapi|pydantic|gradio|pip)\b", re.I), "python/api"),
    (re.compile(r"\b(security|audit|cve|vuln|sentinel|armor)\b", re.I), "security"),
    (re.compile(r"\b(voice|audio|tts|livekit|sonus)\b", re.I), "voice/media"),
    (re.compile(r"\b(next|react|node|typescript|ui|dashboard|web)\b", re.I), "web/ui"),
    (re.compile(r"\b(infra|docker|deploy|cloud|modal|k8s)\b", re.I), "infra/cloud"),
    (re.compile(r"\b(research|search|notebook|ukg|context)\b", re.I), "research"),
]

_CARTRIDGE_MAP: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\b(cognitive|reasoning|critical thinking|tradeoff|decision)\b", re.I), "cognitive"),
    (re.compile(r"\b(bridge|handoff|terminal|ui)\b", re.I), "bridge"),
    (re.compile(r"\b(go|rust|binary|compile|kinetic)\b", re.I), "rust-kinetic"),
    (re.compile(r"\b(next|react|typescript|web|ui)\b", re.I), "nextjs"),
    (re.compile(r"\b(python|fastapi|api|pydantic)\b", re.I), "python-api"),
    (re.compile(r"\b(security|audit|cve|scan)\b", re.I), "security"),
    (re.compile(r"\b(voice|audio|livekit)\b", re.I), "voice-media"),
    (re.compile(r"\b(swarm|colony|agent|dispatch)\b", re.I), "swarm-colony"),
    (re.compile(r"\b(reason|think|plan|analyze)\b", re.I), "reasoning"),
]

_ENTITY_PATTERN = re.compile(
    r"\b([A-Z][a-zA-Z0-9_\-]{2,}|:\d{4,5}|sir_\w+|anya|merlin|lukas|"
    r"saltare|excalibur|holotable|vizion|loom\s*#?\d+)\b",
    re.IGNORECASE,
)

_PRIVACY_KEYWORDS = frozenset({"secret", "private", "credential", "key", "password", "local", "air-gapped"})
_HIGH_COMPLEXITY = frozenset({"swarm", "colony", "multi-agent", "refactor", "migrate", "architecture", "full stack"})


def _stage_parse(raw: str) -> ParseResult:
    cleaned = _NOISE_PATTERNS.sub("", raw).strip()
    cleaned = re.sub(r"\s{2,}", " ", cleaned)

    intent_type = "QUERY"
    for pattern, itype in _INTENT_TYPE_MAP:
        if pattern.search(cleaned):
            intent_type = itype
            break

    entities = list(dict.fromkeys(
        e.strip() for e in _ENTITY_PATTERN.findall(cleaned) if len(e.strip()) > 2
    ))[:8]

    constraints = []
    if re.search(r"\b(max|limit|ceiling|under|less than|<)\s*\d+", cleaned, re.I):
        constraints.append("has_numerical_constraint")
    if re.search(r"\b(only|never|always|must|shall)\b", cleaned, re.I):
        constraints.append("has_hard_constraint")
    if re.search(r"\b(today|now|urgent|immediately|asap)\b", cleaned, re.I):
        constraints.append("velocity_high")

    privacy = 0.9 if any(kw in cleaned.lower() for kw in _PRIVACY_KEYWORDS) else 0.0
    complexity = min(1.0, 0.3 + 0.1 * len(entities) + (0.3 if any(kw in cleaned.lower() for kw in _HIGH_COMPLEXITY) else 0.0))
    velocity = 0.8 if "velocity_high" in constraints else 0.5

    return ParseResult(
        intent_type=intent_type,
        raw=raw,
        entities=entities,
        constraints=constraints,
        complexity=complexity,
        privacy=privacy,
        velocity=velocity,
        ambiguity_stripped=cleaned,
    )


def _stage_enrich(parse: ParseResult) -> EnrichResult:
    domain = "general"
    for pattern, d in _DOMAIN_MAP:
        if pattern.search(parse.ambiguity_stripped):
            domain = d
            break

    cartridge = "reasoning"
    for pattern, c in _CARTRIDGE_MAP:
        if pattern.search(parse.ambiguity_stripped):
            cartridge = c
            break

    # Light UKG probe — look for matching node files without loading full graph
    ukg_refs: list[str] = []
    ukg_dir = ROOT / "03_VAULT" / "training" / "configs" / "memory"
    if ukg_dir.exists():
        for node_file in list(ukg_dir.glob("*.json"))[:3]:
            ukg_refs.append(node_file.stem)

    context_tags: list[str] = []
    for svc, port in [("saltare", 8085), ("excalibur", 8000), ("holotable", 3000)]:
        import socket
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.15):
                context_tags.append(f"{svc}:{port}:ONLINE")
        except OSError:
            context_tags.append(f"{svc}:{port}:OFFLINE")

    magnitude = min(1.0, parse.complexity + (0.1 if len(context_tags) > 2 else 0.0))

    return EnrichResult(
        domain=domain,
        cartridge_hint=cartridge,
        ukg_refs=ukg_refs,
        context_tags=context_tags,
        magnitude=magnitude,
    )


def _stage_compile(parse: ParseResult, enrich: EnrichResult) -> TitanPrompt:
    # Strip filler, compress to imperative dense directive
    directive = parse.ambiguity_stripped
    # Remove trailing punctuation softness
    directive = re.sub(r"[.!?]+$", "", directive).strip()
    # Title-case imperative if starts with verb pattern
    if parse.intent_type in ("BUILD", "FORGE", "HEAL", "AUDIT"):
        directive = directive[0].upper() + directive[1:] if directive else directive

    layer_map = {
        "BUILD": "L2", "FORGE": "L2", "HEAL": "L3",
        "AUDIT": "L6", "ROUTE": "L5", "RESEARCH": "L4", "QUERY": "L7",
    }
    mode_map = {
        "go/binary": "KINETIC", "rust/kinetic": "KINETIC",
        "python/api": "FORGE", "security": "SENTINEL",
        "voice/media": "ORACLE", "web/ui": "FORGE",
        "infra/cloud": "SWARM", "research": "ORACLE", "general": "FORGE",
    }

    return TitanPrompt(
        directive=directive,
        target_layer=layer_map.get(parse.intent_type, "L3"),
        execution_mode=mode_map.get(enrich.domain, "FORGE"),
        constraints_encoded=parse.constraints,
    )


def _stage_route(parse: ParseResult, enrich: EnrichResult) -> tuple[str, str, float, str]:
    try:
        from .soul_router import SoulRouter
        router = SoulRouter()
        decision = router.route(
            parse.ambiguity_stripped,
            velocity=parse.velocity,
            magnitude=enrich.magnitude,
            privacy=parse.privacy,
        )
        return decision.knight_id, decision.engine, decision.weight, decision.reason
    except Exception as e:
        return "sir_boris", "claude_code", 0.85, f"FALLBACK: soul_router unavailable ({e})"


def _stage_validate(
    parse: ParseResult,
    titan: TitanPrompt,
    enrich: EnrichResult,
    knight_id: str = "sir_boris",
) -> ValidationResult:
    issues: list[str] = []
    iron_gate = "CLEARED"

    # Iron Gate HITL triggers
    net_lines_estimate = max(10, int(parse.complexity * 80))
    requires_briefing = len(parse.entities) > 5 or parse.complexity > 0.7

    if net_lines_estimate > 50 or parse.complexity > 0.8:
        iron_gate = "HITL_REQUIRED"
        issues.append(f"complexity={parse.complexity:.2f} exceeds threshold — BriefingScript required")

    if parse.privacy >= 0.8 and titan.execution_mode != "KINETIC":
        issues.append("privacy flag raised — verify air-gapped routing")

    if not titan.directive.strip():
        issues.append("directive is empty after compilation")
        iron_gate = "BLOCKED"

    # SP-01 RBAC ACL check (Shatterpoint remediation)
    try:
        from .rbac_matrix import RBACMatrix
        rbac = RBACMatrix()
        rbac_ok, rbac_issues = rbac.check(
            knight_id, titan.execution_mode, enrich.domain, parse.complexity
        )
        if not rbac_ok:
            iron_gate = "BLOCKED"
            issues.extend(rbac_issues)
        elif rbac_issues:
            issues.extend(rbac_issues)
            if iron_gate == "CLEARED":
                iron_gate = "HITL_REQUIRED"
    except Exception as rbac_err:
        issues.append(f"RBAC matrix unavailable ({rbac_err}) — defaulting to HITL_REQUIRED")
        if iron_gate == "CLEARED":
            iron_gate = "HITL_REQUIRED"

    passed = iron_gate != "BLOCKED"

    return ValidationResult(
        passed=passed,
        issues=issues,
        iron_gate=iron_gate,
        net_lines_estimate=net_lines_estimate,
        requires_briefing=requires_briefing,
    )


# ---------------------------------------------------------------------------
# AnyaGate — the sovereign entry/exit point
# ---------------------------------------------------------------------------

class AnyaGate:
    """
    ANYA_IS_THE_GATE — Titanium Law #11.

    Usage:
        gate = AnyaGate()
        result = gate.process("build a BubbleTea dashboard in Go")
        print(result.render())        # visible pipeline block
        # then execute against result.titan.directive
        # then call gate.validate_output(response_text) before returning to user
    """

    def process(self, raw_intent: str) -> APEEResult:
        t0 = time.perf_counter()

        parse   = _stage_parse(raw_intent)
        enrich  = _stage_enrich(parse)
        titan   = _stage_compile(parse, enrich)
        knight, engine, weight, reason = _stage_route(parse, enrich)
        validation = _stage_validate(parse, titan, enrich, knight_id=knight)

        ms = (time.perf_counter() - t0) * 1000

        return APEEResult(
            raw_intent=raw_intent,
            parse=parse,
            enrich=enrich,
            titan=titan,
            route_knight=knight,
            route_engine=engine,
            route_score=weight,
            route_reason=reason,
            validation=validation,
            pipeline_ms=ms,
        )

    def validate_output(self, response: str) -> tuple[bool, list[str]]:
        """Exit gate — validate a response before it leaves the system."""
        issues: list[str] = []
        if not response or not response.strip():
            issues.append("empty response — blocked at exit gate")
            return False, issues
        if len(response) < 10:
            issues.append("response suspiciously short")
        if re.search(r"\b(i don't know|i cannot|i'm not sure)\b", response, re.I):
            issues.append("response contains uncertainty markers — consider Merlin escalation")
        return len(issues) == 0, issues


class AnyaCompiler:
    """Ethereal Compiler (Layer 7) implementing Triple-QFT Protocol."""

    def __init__(self):
        self.anchor_tokens = {
            "build", "refactor", "create", "deploy", "audit", "fix",
            "scaffold", "status", "sync", "research", "blueprint", "precise",
            "ctx7"
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
