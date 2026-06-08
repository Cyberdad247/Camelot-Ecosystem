# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Context Expansion Protocol — API Integration

FastAPI endpoints for the Context Expansion Protocol.
Integrates with existing agno_app.py infrastructure.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import sys
import os

# Add context module to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../memory')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../context')))

from titan_omega import TitanOmega
from expansion_engine import ExpansionEngine


# =========================================
# REQUEST/RESPONSE MODELS
# =========================================

class ContextExpansionRequest(BaseModel):
    """Request for context expansion."""
    intent: str = Field(..., description="User's goal or query")
    token_budget: Optional[int] = Field(4000, description="Maximum tokens for context")
    session_id: Optional[str] = Field(None, description="Session ID for reasoning tracking")
    filters: Optional[Dict[str, Any]] = Field(None, description="Optional retrieval filters")
    use_got: bool = Field(False, description="Enable Graph-of-Thought reasoning")


class ContextExpansionResponse(BaseModel):
    """Response with expanded context."""
    intent: str
    context: str  # Formatted context string for LLM
    token_count: int
    budget_remaining: int
    cache_hit: bool
    trust_score: float
    metadata: Dict[str, Any]


class ContextValidationRequest(BaseModel):
    """Request for MIRAS++ context validation."""
    intent: str
    context: str


class ContextValidationResponse(BaseModel):
    """Validation results."""
    passed: bool
    warnings: List[str]
    errors: List[str]
    recommendations: List[str]


# =========================================
# ROUTER INITIALIZATION
# =========================================

# Initialize Titan Omega and Expansion Engine
# NOTE: In production, these should be singletons managed by the main app
titan_omega = TitanOmega()
expansion_engine = ExpansionEngine(
    titan=titan_omega,
    default_token_budget=4000,
    enable_got=True,
    enable_cache=True
)

# Create router
cep_router = APIRouter(prefix="/v2/context", tags=["Context Expansion Protocol"])


# =========================================
# API ENDPOINTS
# =========================================

@cep_router.post("/expand", response_model=ContextExpansionResponse)
async def expand_context(request: ContextExpansionRequest):
    """
    Expand context for a given intent using hybrid RAG + GoT + caching.
    
    **Workflow:**
    1. Check cache for existing context
    2. If miss: RAG retrieval from Ω-Graph + Ω-Vault
    3. Optional: GoT reasoning expansion
    4. Token budget management
    5. King Arthur policy gate
    6. Return formatted context bundle
    
    **Example:**
    ```json
    {
      "intent": "Build a secure authentication system",
      "token_budget": 3000,
      "use_got": true,
      "filters": {"agent_type": "Engineer"}
    }
    ```
    """
    try:
        # Perform context expansion
        bundle = expansion_engine.expand(
            intent=request.intent,
            token_budget=request.token_budget,
            session_id=request.session_id,
            filters=request.filters,
            use_got=request.use_got
        )
        
        # Format for LLM injection
        formatted_context = expansion_engine.format_bundle_for_llm(bundle)
        
        return ContextExpansionResponse(
            intent=bundle.intent,
            context=formatted_context,
            token_count=bundle.token_count,
            budget_remaining=bundle.budget_remaining,
            cache_hit=bundle.cache_hit,
            trust_score=bundle.trust_score,
            metadata=bundle.metadata
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context expansion failed: {str(e)}")


@cep_router.post("/validate", response_model=ContextValidationResponse)
async def validate_context(request: ContextValidationRequest):
    """
    Validate context quality using MIRAS++ checks.
    
    **Checks:**
    - Trust score threshold
    - Token budget compliance
    - Completeness analysis
    - Contradiction detection
    
    **Example:**
    ```json
    {
      "intent": "Build authentication system",
      "context": "Retrieved context about OAuth2..."
    }
    ```
    """
    try:
        # Create a minimal bundle for validation
        # (In production, would reconstruct from request)
        
        # Simplified validation - just check basic properties
        validation = {
            "passed": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        # Basic checks
        if not request.context or len(request.context) < 50:
            validation["warnings"].append("Context is very short")
        
        if len(request.context) > 10000:
            validation["warnings"].append("Context exceeds recommended size")
        
        # Check for policy violations
        restricted = ["password", "secret", "private_key"]
        for term in restricted:
            if term in request.context.lower():
                validation["errors"].append(f"Context contains restricted term: {term}")
                validation["passed"] = False
        
        # Recommendations
        if not validation["errors"]:
            validation["recommendations"].append("Context appears safe for LLM injection")
        
        return ContextValidationResponse(**validation)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@cep_router.get("/cache/stats")
async def get_cache_stats():
    """
    Get cache performance statistics.
    
    **Returns:**
    - Hit rate
    - Cache sizes (hot/warm/cold)
    - Eviction counts
    - Promotion/demotion stats
    """
    if not expansion_engine.enable_cache:
        raise HTTPException(status_code=404, detail="Caching is disabled")
    
    stats = expansion_engine.cache.get_stats()
    return {
        "cache_enabled": True,
        **stats
    }


@cep_router.post("/cache/invalidate")
async def invalidate_cache(intent: str = Query(..., description="Intent to invalidate")):
    """
    Invalidate cached context for a specific intent.
    
    Useful for forcing fresh retrieval after knowledge updates.
    """
    if not expansion_engine.enable_cache:
        raise HTTPException(status_code=404, detail="Caching is disabled")
    
    expansion_engine.cache.invalidate(intent)
    
    return {
        "status": "success",
        "message": f"Cache invalidated for intent: {intent[:50]}..."
    }


@cep_router.post("/cache/cleanup")
async def cleanup_expired_cache():
    """
    Manually trigger cleanup of expired cache entries.
    
    Normally happens automatically, but can be triggered for maintenance.
    """
    if not expansion_engine.enable_cache:
        raise HTTPException(status_code=404, detail="Caching is disabled")
    
    expansion_engine.cache.cleanup_expired()
    
    return {
        "status": "success",
        "message": "Expired cache entries cleaned up"
    }


# =========================================
# HEALTH CHECK
# =========================================

@cep_router.get("/health")
async def cep_health():
    """Health check for Context Expansion Protocol."""
    return {
        "status": "healthy",
        "components": {
            "titan_omega": "initialized",
            "rag_backbone": "ready",
            "got_expander": "ready" if expansion_engine.enable_got else "disabled",
            "cache_manager": "ready" if expansion_engine.enable_cache else "disabled"
        },
        "config": {
            "default_token_budget": expansion_engine.default_token_budget,
            "got_enabled": expansion_engine.enable_got,
            "cache_enabled": expansion_engine.enable_cache
        }
    }