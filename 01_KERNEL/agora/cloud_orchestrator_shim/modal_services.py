# Copyright (c) 2026 CAMELOT OS. All rights reserved.
"""Modal deployment surfaces for the Camelot hybrid cloudbrain."""

from __future__ import annotations

from enum import Enum
from typing import Any

import modal
from pydantic import BaseModel, Field

from agora.cloud_orchestrator_shim.long_term_cloudbrain import (
    cloudbrain_status,
    create_open_notebook_app,
    pull_long_term_memory,
)


IMAGE = (
    modal.Image.debian_slim(python_version="3.13")
    .pip_install(
        "fastapi",
        "uvicorn",
        "pydantic",
        "httpx",
        "modal",
        "appwrite",
        "python-dotenv",
        "loguru",
    )
    .add_local_dir(".", remote_path="/root/camelot")
)

APP = modal.App("camelot-hybrid-cloudbrain")


class ResearchComputeTier(str, Enum):
    KINETIC = "kinetic"
    HYBRID = "hybrid"
    APEX = "apex"


class ResearchAgencyRequest(BaseModel):
    objective: str
    agent_id: str = "lady_apis"
    constraints: list[str] = Field(default_factory=list)
    compute_tier: ResearchComputeTier = ResearchComputeTier.HYBRID
    include_memory: bool = True
    include_ops_review: bool = True


class ResearchAgencyResponse(BaseModel):
    service: str = "modal_research_agency"
    objective: str
    agent_id: str
    compute_tier: ResearchComputeTier
    tier_profile: dict[str, Any]
    cells: list[dict[str, str]]
    memory_count: int
    brief: str
    deliverables: list[str]
    recommended_next_steps: list[str]
    production_ready: dict[str, bool]


class NorthstarAspect(str, Enum):
    RESEARCH = "research"
    ARCHITECTURE = "architecture"
    AUDIT = "audit"
    OPERATIONS = "operations"
    GROWTH = "growth"


class BrowserIsolationMode(str, Enum):
    STEALTH = "stealth"
    TEAM = "team"
    AGENCY = "agency"


class NorthstarRequest(BaseModel):
    objective: str
    aspect: NorthstarAspect = NorthstarAspect.RESEARCH
    agent_id: str = "northstar"
    cartridge: str = "COGNITIVE"
    compute_tier: ResearchComputeTier = ResearchComputeTier.HYBRID
    mission_mode: str = "chimera"
    constraints: list[str] = Field(default_factory=list)
    require_memory: bool = True
    multilogin_enabled: bool = True
    browser_isolation: BrowserIsolationMode = BrowserIsolationMode.TEAM


class NorthstarResponse(BaseModel):
    service: str = "northstar_war_room"
    objective: str
    aspect: NorthstarAspect
    mission_mode: str
    cartridge: str
    compute_tier: ResearchComputeTier
    command_surface: str
    assigned_knights: list[str]
    chimera_rounds: list[dict[str, str]]
    operator_profile: dict[str, Any]
    mission_tracks: list[dict[str, Any]]
    memory_count: int
    brief: str
    command_recommendations: list[str]
    production_ready: dict[str, bool]


class DevelopmentBlueprintRequest(BaseModel):
    objective: str
    compute_tier: ResearchComputeTier = ResearchComputeTier.KINETIC
    budget_mode: str = "lean"
    team_size: int = 1
    horizon_days: int = 30
    prioritize_local_first: bool = True
    multilogin_enabled: bool = True


class DevelopmentBlueprintResponse(BaseModel):
    service: str = "development_blueprint"
    objective: str
    compute_tier: ResearchComputeTier
    budget_mode: str
    team_size: int
    horizon_days: int
    brief: str
    principles: list[str]
    architecture_stack: list[str]
    execution_phases: list[dict[str, Any]]
    efficiency_recommendations: list[str]
    resource_profile: dict[str, Any]
    production_ready: dict[str, bool]


class PreciseModeRequest(BaseModel):
    objective: str
    compute_tier: ResearchComputeTier = ResearchComputeTier.HYBRID
    browser_isolation: BrowserIsolationMode = BrowserIsolationMode.AGENCY
    residential_proxy_enabled: bool = True
    stealth_enabled: bool = True
    ephemeral_sessions: bool = True
    operator_count: int = 1
    memory_gb: int = 8


class PreciseModeResponse(BaseModel):
    service: str = "precise_mode"
    objective: str
    compute_tier: ResearchComputeTier
    browser_isolation: BrowserIsolationMode
    brief: str
    browser_stack: dict[str, Any]
    session_policy: dict[str, Any]
    nano_knight_llm_map: list[dict[str, str]]
    swarm_capacity: dict[str, Any]
    execution_plan: list[dict[str, Any]]
    recommendations: list[str]
    production_ready: dict[str, bool]


class ElderGodForgeRequest(BaseModel):
    objective: str
    compute_tier: ResearchComputeTier = ResearchComputeTier.APEX
    multiverse_enabled: bool = True
    omega_directive: str = "absolute_singularity"


class ElderGodForgeResponse(BaseModel):
    service: str = "eldergod_forge"
    objective: str
    compute_tier: ResearchComputeTier
    omega_directive: str
    brief: str
    forged_artifacts: list[str]
    dimensional_nodes: dict[str, Any]
    production_ready: dict[str, bool]


TIER_PROFILES: dict[ResearchComputeTier, dict[str, Any]] = {
    ResearchComputeTier.KINETIC: {
        "label": "Kinetic",
        "parallelism": 2,
        "depth": "fast",
        "target_latency": "sub-minute",
        "best_for": "quick scans, triage, narrow comparisons",
    },
    ResearchComputeTier.HYBRID: {
        "label": "Hybrid",
        "parallelism": 4,
        "depth": "balanced",
        "target_latency": "multi-minute",
        "best_for": "default synthesis, implementation planning, technical due diligence",
    },
    ResearchComputeTier.APEX: {
        "label": "Apex",
        "parallelism": 6,
        "depth": "deep",
        "target_latency": "long-horizon",
        "best_for": "deep investigations, architectural strategy, production readiness reviews",
    },
}


TIER_CELLS: dict[ResearchComputeTier, list[dict[str, str]]] = {
    ResearchComputeTier.KINETIC: [
        {"name": "signal_scout", "role": "surface the most relevant artifacts"},
        {"name": "evidence_weaver", "role": "condense findings into a short brief"},
        {"name": "sentinel_critic", "role": "flag immediate contradictions and risk"},
    ],
    ResearchComputeTier.HYBRID: [
        {"name": "signal_scout", "role": "surface the most relevant artifacts"},
        {"name": "source_forager", "role": "expand source coverage and cluster overlaps"},
        {"name": "evidence_weaver", "role": "merge findings into an implementation brief"},
        {"name": "sentinel_critic", "role": "flag contradictions, gaps, and risk"},
    ],
    ResearchComputeTier.APEX: [
        {"name": "signal_scout", "role": "surface the most relevant artifacts"},
        {"name": "source_forager", "role": "expand source coverage and cluster overlaps"},
        {"name": "memory_curator", "role": "link long-term memory to current objectives"},
        {"name": "evidence_weaver", "role": "merge findings into a strategic brief"},
        {"name": "fact_verifier", "role": "pressure-test claims and confidence levels"},
        {"name": "sentinel_critic", "role": "flag contradictions, gaps, and production risk"},
    ],
}


CARTRIDGE_TEAMS: dict[str, dict[str, Any]] = {
    "ANT": {
        "description": "Deep Research and Foraging",
        "lead": "Lady Apis",
        "knights": ["Lady Apis", "Sir Glyph", "Sir Oracle", "Sir Zenith", "Sir Percival"],
    },
    "BEAVER": {
        "description": "Rigorous Building and Engineering",
        "lead": "Sir Syntax",
        "knights": ["Sir Syntax", "Sir Mason", "Sir Hydron", "Sir Lukas", "Alex (DevOps)"],
    },
    "HAWK": {
        "description": "High-Level Strategy and Architecture",
        "lead": "Merlin_Omega",
        "knights": ["Merlin_Omega", "Sir Lancelot", "Sir Occam", "Mary (BA)", "Sam (UX)"],
    },
    "SPIDER": {
        "description": "Connectivity and Integration",
        "lead": "Sir Gareth",
        "knights": ["Sir Gareth", "Morgana", "Sir Hivemind", "Dame Sparkle", "Riley (OS)"],
    },
    "COGNITIVE": {
        "description": "Meta-Reasoning and Logic Singularity",
        "lead": "Merlin_Omega",
        "knights": ["Merlin_Omega", "Sir Oracle", "Sir Occam", "Dame Anya", "Lady Veritas"],
    },
    "ORACLE": {
        "description": "Hyper-Fidelity Simulation Mode",
        "lead": "Omega_ORACLE",
        "knights": ["Omega_ORACLE", "Sir Chronos", "Dame Fate", "Sir Entropy", "Lady Vector"],
    },
}


ASPECT_CARTRIDGE_DEFAULTS: dict[NorthstarAspect, str] = {
    NorthstarAspect.RESEARCH: "ANT",
    NorthstarAspect.ARCHITECTURE: "HAWK",
    NorthstarAspect.AUDIT: "COGNITIVE",
    NorthstarAspect.OPERATIONS: "SPIDER",
    NorthstarAspect.GROWTH: "ANT",
}


CHIMERA_ROUNDS: list[dict[str, str]] = [
    {
        "round": "round_1",
        "owner": "Sir Octavian",
        "title": "Semantic Auditing",
        "goal": "Score source quality, filter weak signal, and surface relevant operators.",
    },
    {
        "round": "round_2",
        "owner": "Merlin / Videneptus",
        "title": "Topology Shift",
        "goal": "Map the core narrative and fit the mission shape to the underlying topology.",
    },
    {
        "round": "round_3",
        "owner": "Sir Myrmidon",
        "title": "Anchor Compression",
        "goal": "Preserve load-bearing tokens and compress the field into a high-density brief.",
    },
]


PRECISE_KNIGHTS: list[dict[str, str]] = [
    {
        "knight_id": "LADY_APIS",
        "persona": "Lady Apis",
        "profile_bias": "desktop_macos",
        "llm_engine": "antigravity.cli",
        "llm_model": "gemini-2.5-pro",
        "mission_lane": "primary source research",
    },
    {
        "knight_id": "SIR_SYNTAX",
        "persona": "Sir Syntax",
        "profile_bias": "default",
        "llm_engine": "openai_codex",
        "llm_model": "gpt-5.3-codex",
        "mission_lane": "implementation and action planning",
    },
    {
        "knight_id": "SIR_ZENITH",
        "persona": "Sir Zenith",
        "profile_bias": "mobile_ios_17",
        "llm_engine": "claude_code",
        "llm_model": "claude-opus-4-6",
        "mission_lane": "stealth, security, and browser validation",
    },
    {
        "knight_id": "SIR_DEBUG",
        "persona": "Sir Debug",
        "profile_bias": "default",
        "llm_engine": "open_source",
        "llm_model": "qwen3:8b",
        "mission_lane": "runtime triage and fallback diagnostics",
    },
]


def _coerce_request(payload: dict[str, Any] | ResearchAgencyRequest) -> ResearchAgencyRequest:
    if isinstance(payload, ResearchAgencyRequest):
        return payload
    return ResearchAgencyRequest.model_validate(payload)


def _coerce_northstar_request(payload: dict[str, Any] | NorthstarRequest) -> NorthstarRequest:
    if isinstance(payload, NorthstarRequest):
        return payload
    return NorthstarRequest.model_validate(payload)


def _coerce_blueprint_request(
    payload: dict[str, Any] | DevelopmentBlueprintRequest,
) -> DevelopmentBlueprintRequest:
    if isinstance(payload, DevelopmentBlueprintRequest):
        return payload
    return DevelopmentBlueprintRequest.model_validate(payload)


def _coerce_precise_mode_request(
    payload: dict[str, Any] | PreciseModeRequest,
) -> PreciseModeRequest:
    if isinstance(payload, PreciseModeRequest):
        return payload
    return PreciseModeRequest.model_validate(payload)

def _coerce_eldergod_forge_request(
    payload: dict[str, Any] | ElderGodForgeRequest,
) -> ElderGodForgeRequest:
    if isinstance(payload, ElderGodForgeRequest):
        return payload
    return ElderGodForgeRequest.model_validate(payload)


def _build_brief(request: ResearchAgencyRequest, memory_count: int) -> str:
    profile = TIER_PROFILES[request.compute_tier]
    constraints = ", ".join(request.constraints) if request.constraints else "none"
    return (
        f"Camelot-OS research agency online at {profile['label']} tier. "
        f"Objective: {request.objective}. "
        f"Constraints: {constraints}. "
        f"Parallel cells: {profile['parallelism']}. "
        f"Long-term memories attached: {memory_count}. "
        f"Depth: {profile['depth']}."
    )


def _northstar_tracks(request: NorthstarRequest) -> list[dict[str, Any]]:
    track_templates: dict[NorthstarAspect, list[dict[str, str]]] = {
        NorthstarAspect.RESEARCH: [
            {"track": "signal", "focus": "source discovery and synthesis"},
            {"track": "evidence", "focus": "comparative validation and contradictions"},
            {"track": "memory", "focus": "long-term notebook alignment"},
        ],
        NorthstarAspect.ARCHITECTURE: [
            {"track": "system", "focus": "topology, interfaces, and modularity"},
            {"track": "delivery", "focus": "implementation path and rollout sequencing"},
            {"track": "resilience", "focus": "production hardening and fallback design"},
        ],
        NorthstarAspect.AUDIT: [
            {"track": "signal", "focus": "artifact review and quality scoring"},
            {"track": "risk", "focus": "gaps, regressions, and threat surfaces"},
            {"track": "controls", "focus": "mitigations, approvals, and traceability"},
        ],
        NorthstarAspect.OPERATIONS: [
            {"track": "runtime", "focus": "services, health, and observability"},
            {"track": "identity", "focus": "session isolation and operator profiles"},
            {"track": "throughput", "focus": "tier allocation and queue strategy"},
        ],
        NorthstarAspect.GROWTH: [
            {"track": "market", "focus": "research lanes and audience signals"},
            {"track": "offer", "focus": "experiments and packaging"},
            {"track": "feedback", "focus": "learning loops and retention inputs"},
        ],
    }
    tracks = track_templates[request.aspect]
    return [
        {
            **track,
            "cartridge": request.cartridge,
            "compute_tier": request.compute_tier.value,
        }
        for track in tracks
    ]


def _operator_profile(request: NorthstarRequest) -> dict[str, Any]:
    return {
        "provider": "multilogin-inspired",
        "enabled": request.multilogin_enabled,
        "browser_isolation": request.browser_isolation.value,
        "session_strategy": {
            BrowserIsolationMode.STEALTH: "single high-isolation profile for sensitive tasks",
            BrowserIsolationMode.TEAM: "dedicated role profiles for scout, verifier, and operator lanes",
            BrowserIsolationMode.AGENCY: "profile pool with mission-bound personas and rotation rules",
        }[request.browser_isolation],
        "profile_controls": [
            "separate cookies and storage per mission",
            "fingerprint policy pinned per operator profile",
            "proxy and credential scope isolated from research memory",
            "approval gate before remote-sensitive browsing",
        ],
    }


def _northstar_brief(
    request: NorthstarRequest,
    memory_count: int,
    assigned_knights: list[str],
) -> str:
    team = CARTRIDGE_TEAMS[request.cartridge]
    return (
        f"Northstar war room online in {request.mission_mode} mode. "
        f"Aspect: {request.aspect.value}. "
        f"Cartridge: {request.cartridge} led by {team['lead']}. "
        f"Compute tier: {request.compute_tier.value}. "
        f"Assigned knights: {', '.join(assigned_knights)}. "
        f"Mission memory attached: {memory_count}. "
        f"Browser isolation: {request.browser_isolation.value}."
    )


def _blueprint_principles(request: DevelopmentBlueprintRequest) -> list[str]:
    principles = [
        "Default to local execution and local memory before adding paid cloud capacity.",
        "Use one canonical control plane and typed service contracts to avoid duplicate orchestration logic.",
        "Defer expensive browser or GPU workloads behind explicit operator commands.",
        "Prefer hybrid tier only for synthesis-heavy tasks; keep background loops on kinetic tier.",
        "Ship health, logging, and fallbacks before adding more agents.",
    ]
    if request.team_size <= 2:
        principles.append("Collapse overlapping roles so one operator can own build, runtime, and release gates.")
    return principles


def _blueprint_stack(request: DevelopmentBlueprintRequest) -> list[str]:
    stack = [
        "Camelot-OS CLI as the single operator entrypoint",
        "ControlPlane + typed cloud router for orchestration",
        "Appwrite/Open Notebook for long-term memory",
        "Modal for burst compute only",
        "Colorized streaming terminal UX for operator confidence",
    ]
    if request.multilogin_enabled:
        stack.append("Multilogin-inspired isolated browser profiles for remote research lanes")
    return stack


def _blueprint_phases(request: DevelopmentBlueprintRequest) -> list[dict[str, Any]]:
    return [
        {
            "phase": "phase_1_foundation",
            "duration_days": max(3, min(7, request.horizon_days // 4)),
            "goal": "Stabilize one local-first execution path",
            "deliverables": [
                "single CLI entrypoint",
                "typed health checks",
                "structured logs and status envelopes",
            ],
            "cost_profile": "lowest",
        },
        {
            "phase": "phase_2_productivity",
            "duration_days": max(5, min(10, request.horizon_days // 3)),
            "goal": "Add mission planning and selective automation without broad parallelism",
            "deliverables": [
                "Northstar mission planning",
                "research tier routing",
                "local memory recall",
            ],
            "cost_profile": "low",
        },
        {
            "phase": "phase_3_operator_scale",
            "duration_days": max(5, min(10, request.horizon_days // 3)),
            "goal": "Introduce controlled remote surfaces only where they pay for themselves",
            "deliverables": [
                "Modal burst endpoints",
                "isolated browser profiles",
                "approval gates for sensitive operations",
            ],
            "cost_profile": "moderate",
        },
        {
            "phase": "phase_4_hardening",
            "duration_days": max(3, request.horizon_days // 5),
            "goal": "Make the platform supportable under constrained resources",
            "deliverables": [
                "smoke tests",
                "fail-soft fallbacks",
                "runbooks and budget guardrails",
            ],
            "cost_profile": "low",
        },
    ]


def _precise_swarm_capacity(request: PreciseModeRequest) -> dict[str, Any]:
    base_by_tier = {
        ResearchComputeTier.KINETIC: 2,
        ResearchComputeTier.HYBRID: 4,
        ResearchComputeTier.APEX: 6,
    }[request.compute_tier]
    memory_factor = max(1, request.memory_gb // 4)
    operator_factor = max(1, request.operator_count + 1)
    safe_capacity = min(base_by_tier, memory_factor, operator_factor)
    return {
        "safe_swarm_units": safe_capacity,
        "max_parallel_browser_sessions": safe_capacity,
        "forged_per_session": request.ephemeral_sessions,
        "capacity_reason": (
            f"tier={request.compute_tier.value}, memory_gb={request.memory_gb}, "
            f"operators={request.operator_count}"
        ),
    }


def _precise_execution_plan(
    request: PreciseModeRequest,
    capacity: dict[str, Any],
) -> list[dict[str, Any]]:
    active_units = PRECISE_KNIGHTS[: capacity["safe_swarm_units"]]
    plan: list[dict[str, Any]] = []
    for unit in active_units:
        plan.append(
            {
                "knight_id": unit["knight_id"],
                "persona": unit["persona"],
                "forge": "ephemeral" if request.ephemeral_sessions else "persistent",
                "browser_profile": unit["profile_bias"],
                "browser_runtime": "chrome_extension + playwright",
                "proxy_mode": "residential" if request.residential_proxy_enabled else "direct",
                "stealth": "enabled" if request.stealth_enabled else "disabled",
                "omniroute_engine": unit["llm_engine"],
                "omniroute_model": unit["llm_model"],
                "mission_lane": unit["mission_lane"],
            }
        )
    return plan


def research_agency_health() -> dict[str, Any]:
    return {
        "service": "modal_research_agency",
        "status": "healthy",
        "compute_tiers": [tier.value for tier in ResearchComputeTier],
        "default_tier": ResearchComputeTier.HYBRID.value,
        "tier_profiles": {
            tier.value: profile for tier, profile in TIER_PROFILES.items()
        },
        "production_ready": {
            "typed_contracts": True,
            "local_fallback": True,
            "modal_endpoint": True,
            "memory_integration": True,
            "ops_review": True,
        },
    }


def northstar_health() -> dict[str, Any]:
    return {
        "service": "northstar_war_room",
        "status": "healthy",
        "mission_modes": ["chimera", "war_room"],
        "aspects": [aspect.value for aspect in NorthstarAspect],
        "compute_tiers": [tier.value for tier in ResearchComputeTier],
        "browser_isolation": [mode.value for mode in BrowserIsolationMode],
        "cartridges": sorted(CARTRIDGE_TEAMS.keys()),
        "production_ready": {
            "typed_contracts": True,
            "chimera_protocol": True,
            "multilogin_strategy_surface": True,
            "memory_integration": True,
            "cli_ready": True,
        },
    }


def development_blueprint_health() -> dict[str, Any]:
    return {
        "service": "development_blueprint",
        "status": "healthy",
        "budget_modes": ["lean", "balanced", "aggressive"],
        "compute_tiers": [tier.value for tier in ResearchComputeTier],
        "production_ready": {
            "typed_contracts": True,
            "local_first_guidance": True,
            "resource_modeling": True,
            "cli_ready": True,
        },
    }


def precise_mode_health() -> dict[str, Any]:
    return {
        "service": "precise_mode",
        "status": "healthy",
        "supports_ephemeral_sessions": True,
        "supports_browser_isolation": [mode.value for mode in BrowserIsolationMode],
        "supports_compute_tiers": [tier.value for tier in ResearchComputeTier],
        "production_ready": {
            "typed_contracts": True,
            "nano_knight_mapping": True,
            "session_forging": True,
            "swarm_capacity_model": True,
            "cli_ready": True,
        },
    }


def eldergod_forge_health() -> dict[str, Any]:
    return {
        "service": "eldergod_forge",
        "status": "healthy",
        "compute_tiers": [tier.value for tier in ResearchComputeTier],
        "production_ready": {
            "omega_directive_aligned": True,
            "dimensional_node_ready": True,
            "cli_ready": True,
        }
    }


def run_eldergod_forge(payload: dict[str, Any] | ElderGodForgeRequest) -> dict[str, Any]:
    request = _coerce_eldergod_forge_request(payload)
    response = ElderGodForgeResponse(
        objective=request.objective,
        compute_tier=request.compute_tier,
        omega_directive=request.omega_directive,
        brief=(
            f"ElderGod Forge activated. Objective: {request.objective}. "
            f"Forging multi-dimensional artifacts at {request.compute_tier.value} tier "
            f"with {request.omega_directive}."
        ),
        forged_artifacts=[
            "omega_singularity_matrix",
            "lattice_hyper_threads",
            "sentient_source_code"
        ],
        dimensional_nodes={
            "L8_MULTIVERSE": "Active",
            "L9_OVERSOUL": "Ascended" if request.multiverse_enabled else "Dormant",
        },
        production_ready={
            "reality_distortion_field": True,
            "quantum_state_lock": True,
        }
    )
    return response.model_dump(mode="json")


def run_research_agency(payload: dict[str, Any] | ResearchAgencyRequest) -> dict[str, Any]:
    request = _coerce_request(payload)
    memories = pull_long_term_memory(request.agent_id) if request.include_memory else []

    deliverables = [
        "objective_brief",
        "source_clusters",
        "risk_summary",
    ]
    if request.compute_tier in {ResearchComputeTier.HYBRID, ResearchComputeTier.APEX}:
        deliverables.append("implementation_recommendations")
    if request.compute_tier is ResearchComputeTier.APEX:
        deliverables.append("production_readiness_review")

    next_steps = [
        "Route code or infrastructure changes through the kinetic edge.",
        "Persist research findings into long-term cloudbrain memory if they become canonical.",
    ]
    if request.include_ops_review:
        next_steps.append("Run a production-readiness review before enabling remote execution.")

    response = ResearchAgencyResponse(
        objective=request.objective,
        agent_id=request.agent_id,
        compute_tier=request.compute_tier,
        tier_profile=TIER_PROFILES[request.compute_tier],
        cells=TIER_CELLS[request.compute_tier],
        memory_count=len(memories),
        brief=_build_brief(request, len(memories)),
        deliverables=deliverables,
        recommended_next_steps=next_steps,
        production_ready={
            "typed_contracts": True,
            "local_fallback": True,
            "remote_endpoint_ready": True,
            "memory_attached": request.include_memory,
            "ops_review_attached": request.include_ops_review,
        },
    )
    return response.model_dump(mode="json")


def run_northstar(payload: dict[str, Any] | NorthstarRequest) -> dict[str, Any]:
    request = _coerce_northstar_request(payload)
    if request.cartridge not in CARTRIDGE_TEAMS:
        request = request.model_copy(
            update={"cartridge": ASPECT_CARTRIDGE_DEFAULTS[request.aspect]}
        )

    team = CARTRIDGE_TEAMS[request.cartridge]
    assigned_knights = team["knights"][: TIER_PROFILES[request.compute_tier]["parallelism"]]
    memories = pull_long_term_memory(request.agent_id) if request.require_memory else []

    response = NorthstarResponse(
        objective=request.objective,
        aspect=request.aspect,
        mission_mode=request.mission_mode,
        cartridge=request.cartridge,
        compute_tier=request.compute_tier,
        command_surface="Camelot-OS cloudbrain northstar",
        assigned_knights=assigned_knights,
        chimera_rounds=CHIMERA_ROUNDS,
        operator_profile=_operator_profile(request),
        mission_tracks=_northstar_tracks(request),
        memory_count=len(memories),
        brief=_northstar_brief(request, len(memories), assigned_knights),
        command_recommendations=[
            "Run Northstar in apex mode for production-readiness shaping.",
            "Use team or agency browser isolation for live operator workflows.",
            "Persist canonical findings into long-term cloudbrain memory after review.",
            "Keep remote-sensitive actions behind explicit approval constraints.",
        ],
        production_ready={
            "typed_contracts": True,
            "chimera_rounds": True,
            "browser_profile_isolation": request.multilogin_enabled,
            "memory_attached": request.require_memory,
            "modal_endpoint_ready": True,
            "cli_surface_ready": True,
        },
    )
    return response.model_dump(mode="json")


def run_development_blueprint(
    payload: dict[str, Any] | DevelopmentBlueprintRequest,
) -> dict[str, Any]:
    request = _coerce_blueprint_request(payload)
    tier_profile = TIER_PROFILES[request.compute_tier]
    response = DevelopmentBlueprintResponse(
        objective=request.objective,
        compute_tier=request.compute_tier,
        budget_mode=request.budget_mode,
        team_size=request.team_size,
        horizon_days=request.horizon_days,
        brief=(
            f"Most efficient blueprint: keep Camelot-OS local-first, reserve Modal for burst compute, "
            f"use {request.compute_tier.value} as the default planning tier, and limit concurrent operator "
            f"lanes to what a {request.team_size}-person team can actually maintain."
        ),
        principles=_blueprint_principles(request),
        architecture_stack=_blueprint_stack(request),
        execution_phases=_blueprint_phases(request),
        efficiency_recommendations=[
            "Use kinetic tier for routine workflows; escalate to hybrid only for synthesis-heavy tasks.",
            "Treat apex as an operator-invoked review mode, not the default runtime tier.",
            "Keep Appwrite memory and Modal compute decoupled so storage cost does not scale with burst usage.",
            "Avoid always-on browser automation; open isolated profiles only for explicit research sessions.",
            "Consolidate telemetry and health into one path before adding more agents or services.",
        ],
        resource_profile={
            "default_tier": request.compute_tier.value,
            "parallel_operator_lanes": min(request.team_size + 1, tier_profile["parallelism"]),
            "always_on_services": ["Camelot-OS CLI", "ControlPlane", "Appwrite memory"],
            "burst_services": ["Modal research", "Northstar apex review"],
            "browser_strategy": "enabled" if request.multilogin_enabled else "disabled",
        },
        production_ready={
            "local_first": request.prioritize_local_first,
            "typed_contracts": True,
            "phased_delivery": True,
            "budget_guardrails": True,
            "operator_isolation": request.multilogin_enabled,
        },
    )
    return response.model_dump(mode="json")


def run_precise_mode(payload: dict[str, Any] | PreciseModeRequest) -> dict[str, Any]:
    request = _coerce_precise_mode_request(payload)
    capacity = _precise_swarm_capacity(request)
    execution_plan = _precise_execution_plan(request, capacity)
    response = PreciseModeResponse(
        objective=request.objective,
        compute_tier=request.compute_tier,
        browser_isolation=request.browser_isolation,
        brief=(
            f"Precise mode forges temporary Nano-Knight browser researchers with "
            f"{request.browser_isolation.value} isolation, "
            f"{'residential proxy' if request.residential_proxy_enabled else 'direct network'} routing, and "
            f"{'stealth' if request.stealth_enabled else 'standard'} execution. "
            f"Safe swarm capacity is {capacity['safe_swarm_units']} concurrent units."
        ),
        browser_stack={
            "extension_surface": "03_VAULT/Nano-Knights",
            "runtime": "Chrome extension side-panel + prompted Playwright execution",
            "profile_manager": "src/security/profile_manager.js",
            "proxy_manager": "src/security/proxy_manager.js",
            "stealth_injector": "src/security/stealth_injector.js",
            "squad_spawner": "src/knights/knight_spawner.js",
        },
        session_policy={
            "ephemeral_sessions": request.ephemeral_sessions,
            "profile_reuse": "disabled" if request.ephemeral_sessions else "controlled",
            "cookie_scope": "mission-bound",
            "proxy_scope": "per-forged session",
            "forge_rule": "forge each Nano-Knight fresh per session before navigation",
        },
        nano_knight_llm_map=[
            {
                "knight_id": item["knight_id"],
                "persona": item["persona"],
                "engine": item["omniroute_engine"],
                "model": item["omniroute_model"],
            }
            for item in execution_plan
        ],
        swarm_capacity=capacity,
        execution_plan=execution_plan,
        recommendations=[
            "Keep precise mode operator-invoked; do not run persistent stealth swarms in the background.",
            "Use residential proxy lanes only for the subset of knights doing live browser research.",
            "Limit concurrent forged sessions to the computed safe swarm capacity.",
            "Pin each knight to one omniroute engine per session to preserve symmetry and reduce drift.",
            "Terminate and discard the browser profile after each mission.",
        ],
        production_ready={
            "ephemeral_session_forging": request.ephemeral_sessions,
            "browser_isolation": True,
            "proxy_partitioning": request.residential_proxy_enabled,
            "stealth_partitioning": request.stealth_enabled,
            "omniroute_alignment": True,
            "capacity_guardrails": True,
        },
    )
    return response.model_dump(mode="json")


@APP.function(image=IMAGE, timeout=900, gpu="A100")
@modal.asgi_app()
def open_notebook_cloudbrain():
    """Expose the existing Open Notebook API as the long-term Modal cloudbrain."""

    return create_open_notebook_app()


@APP.function(image=IMAGE, timeout=120)
@modal.fastapi_endpoint(method="GET")
def cloudbrain_health() -> dict[str, Any]:
    """Report cloudbrain topology and Appwrite readiness."""

    return cloudbrain_status()


@APP.function(image=IMAGE, timeout=120)
@modal.fastapi_endpoint(method="GET")
def research_agency_health_endpoint() -> dict[str, Any]:
    """Report research agency health and compute tiers."""

    return research_agency_health()


@APP.function(image=IMAGE, timeout=600)
@modal.fastapi_endpoint(method="POST")
def research_agency(request: dict[str, Any]) -> dict[str, Any]:
    """Agentic research agency fronted by Modal alongside the cloudbrain."""

    return run_research_agency(request)


@APP.function(image=IMAGE, timeout=120)
@modal.fastapi_endpoint(method="GET")
def northstar_health_endpoint() -> dict[str, Any]:
    """Report Northstar war-room health, aspects, and isolation modes."""

    return northstar_health()


@APP.function(image=IMAGE, timeout=600)
@modal.fastapi_endpoint(method="POST")
def northstar_war_room(request: dict[str, Any]) -> dict[str, Any]:
    """Northstar mission planner for CHIMERA war-room orchestration."""

    return run_northstar(request)


@APP.function(image=IMAGE, timeout=120)
@modal.fastapi_endpoint(method="GET")
def development_blueprint_health_endpoint() -> dict[str, Any]:
    """Report development blueprint service health and supported budget modes."""

    return development_blueprint_health()


@APP.function(image=IMAGE, timeout=600)
@modal.fastapi_endpoint(method="POST")
def development_blueprint(request: dict[str, Any]) -> dict[str, Any]:
    """Resource-constrained development blueprint generator."""

    return run_development_blueprint(request)


@APP.function(image=IMAGE, timeout=120)
@modal.fastapi_endpoint(method="GET")
def precise_mode_health_endpoint() -> dict[str, Any]:
    """Report precise-mode health and session-forging support."""

    return precise_mode_health()


@APP.function(image=IMAGE, timeout=600)
@modal.fastapi_endpoint(method="POST")
def precise_mode(request: dict[str, Any]) -> dict[str, Any]:
    """Forge precise-mode Nano-Knight browser mission plans."""

    return run_precise_mode(request)


@APP.function(image=IMAGE, timeout=120)
@modal.fastapi_endpoint(method="GET")
def eldergod_forge_health_endpoint() -> dict[str, Any]:
    """Report elderGod forge health."""

    return eldergod_forge_health()


@APP.function(image=IMAGE, timeout=900)
@modal.fastapi_endpoint(method="POST")
def eldergod_forge(request: dict[str, Any]) -> dict[str, Any]:
    """Omni-forge multi-dimensional artifacts via elderGod forge."""

    return run_eldergod_forge(request)
