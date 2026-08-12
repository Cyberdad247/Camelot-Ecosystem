# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Cartridge Manifest Schema and Templates

Based on Project Chimera specifications for the Dynamic Cartridge Fabrication Engine.
"""

from typing import Dict, List
from pydantic import BaseModel, Field
from datetime import datetime


# =========================================
# CARTRIDGE MANIFEST SCHEMA
# =========================================

class ResourceBudget(BaseModel):
    """Resource constraints for cartridge execution."""
    max_tokens: int = Field(default=25000, description="Maximum token budget")
    max_memory_mb: int = Field(default=512, description="Maximum memory in MB")
    max_latency_ms: int = Field(default=600, description="Maximum latency in milliseconds")


class GovernancePolicy(BaseModel):
    """Governance rules for cartridge operations."""
    HITL_required: bool = Field(default=False, description="Requires human-in-the-loop approval")
    allowed_tools: List[str] = Field(default_factory=list, description="Whitelisted tools")
    denied_operations: List[str] = Field(default_factory=list, description="Blacklisted operations")


class CartridgeHooks(BaseModel):
    """Lifecycle hooks for cartridge management."""
    on_load: List[str] = Field(default_factory=list, description="Scripts to run on load")
    on_unload: List[str] = Field(default_factory=list, description="Scripts to run on unload")
    health_check: List[str] = Field(default_factory=list, description="Health check scripts")


class CartridgeEmbeddings(BaseModel):
    """Pre-computed embeddings for static content."""
    static_docs: List[str] = Field(default_factory=list, description="Document IDs")
    symbolic_snippets: List[str] = Field(default_factory=list, description="Symbolect snippet IDs")


class CartridgeManifest(BaseModel):
    """
    Complete cartridge manifest for the Cartridge Matrix (CMX).
    Defines agents, tools, protocols, capabilities, and governance.
    """
    cartridge_id: str = Field(..., description="Unique cartridge identifier")
    version: str = Field(default="1.0.0", description="Semantic version")
    description: str = Field(..., description="Human-readable description")
    agents: List[str] = Field(default_factory=list, description="Agent IDs included")
    tools: List[str] = Field(default_factory=list, description="Tool IDs included")
    protocols: List[str] = Field(default_factory=list, description="Protocol IDs included")
    
    # Manifests sub-object
    capabilities: List[str] = Field(default_factory=list, description="Capability tags")
    resource_budget: ResourceBudget = Field(default_factory=ResourceBudget)
    risk_profile: str = Field(default="low", description="Risk level (low/medium/high)")
    governance: GovernancePolicy = Field(default_factory=GovernancePolicy)
    
    # Lifecycle
    hooks: CartridgeHooks = Field(default_factory=CartridgeHooks)
    
    # Pre-computed data
    embeddings: CartridgeEmbeddings = Field(default_factory=CartridgeEmbeddings)
    
    # Provenance
    signature: str = Field(..., description="SHA-256 signature")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(default="ChimeraKernel", description="Creator agent")


# =========================================
# JIT TOOL ADAPTER SCHEMA
# =========================================

class APIMethod(BaseModel):
    """Definition for a single API method."""
    method: str = Field(..., description="HTTP method (GET/POST/PUT/DELETE)")
    params: List[str] = Field(default_factory=list, description="Required parameters")
    response_map: Dict[str, str] = Field(default_factory=dict, description="JSONPath mappings")


class SandboxConstraints(BaseModel):
    """Sandbox execution limits for JIT tools."""
    timeout_ms: int = Field(default=1500, description="Timeout in milliseconds")
    max_calls_per_minute: int = Field(default=20, description="Rate limit")


class JITToolAdapter(BaseModel):
    """
    Just-in-Time tool adapter for external API integration.
    Compiled dynamically during cartridge fabrication.
    """
    adapter_id: str = Field(..., description="Unique adapter ID")
    type: str = Field(default="api_wrapper", description="Adapter type")
    endpoint: str = Field(..., description="Base API endpoint URL")
    auth: str = Field(..., description="Authentication (e.g., 'env:API_KEY')")
    methods: Dict[str, APIMethod] = Field(default_factory=dict, description="Available methods")
    sandbox_constraints: SandboxConstraints = Field(default_factory=SandboxConstraints)


# =========================================
# CARTRIDGE TEMPLATE EXAMPLES
# =========================================

# Strategy Cartridge Template (Lord Nexus, Sir Lancelot)
STRATEGY_CARTRIDGE_TEMPLATE = {
    "cartridge_id": "STRATEGY_CORE",
    "description": "Strategy and planning cartridge",
    "agents": ["Lord_Nexus", "Sir_Lancelot"],
    "tools": ["QERE", "MIND_MODULES"],
    "protocols": ["MIRAS++"],
    "capabilities": ["planning", "architecture", "strategic_thinking"],
    "risk_profile": "low"
}

# Engineering Cartridge Template (Sir Lukas, Sir Hydron)
ENGINEERING_CARTRIDGE_TEMPLATE = {
    "cartridge_id": "ENGINEERING_CORE",
    "description": "Engineering and implementation cartridge",
    "agents": ["Sir_Lukas", "Sir_Hydron", "Sir_Syntax"],
    "tools": ["CodeGen", "SecurityScan", "SyntaxChecker"],
    "protocols": ["TDD", "CodeReview"],
    "capabilities": ["backend", "frontend", "cli", "testing"],
    "risk_profile": "medium"
}

# Creative Cartridge Template (Vizion Wealth, Dame Sparkle)
CREATIVE_CARTRIDGE_TEMPLATE = {
    "cartridge_id": "CREATIVE_CORE",
    "description": "Creative content generation cartridge",
    "agents": ["Vizion_Wealth", "Dame_Sparkle", "Sir_Visage"],
    "tools": ["LCE_4.0", "SBE_1.5", "ImageGen"],
    "protocols": ["StyleBlending"],
    "capabilities": ["copywriting", "visual_design", "audio"],
    "risk_profile": "low"
}

# Operations Cartridge Template (Sir Myrmidon, Sir Nova)
OPERATIONS_CARTRIDGE_TEMPLATE = {
    "cartridge_id": "OPERATIONS_CORE",
    "description": "Operations and research cartridge",
    "agents": ["Sir_Myrmidon", "Sir_Nova", "Sir_Percival"],
    "tools": ["ACO_SWARM", "WebCrawler", "KG_Builder"],
    "protocols": ["ResearchProtocol"],
    "capabilities": ["research", "knowledge_graph", "swarm_intelligence"],
    "risk_profile": "medium"
}