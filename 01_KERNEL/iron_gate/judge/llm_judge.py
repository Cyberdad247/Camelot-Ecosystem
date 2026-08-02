# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
LLM-as-a-Judge Engine — Core Evaluation Infrastructure

Deterministic scoring engine using low-temperature LLM for evaluating:
- Agent outputs against quality rubrics
- Fusion merge decisions
- Optimization hypotheses
- Cartridge synthesis quality

Integrates with rubric.py scoring dimensions and existing LLMManager.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .rubric import (
    EVALUATION_PROMPT_TEMPLATE,
    AccuracyDimension,
    FidelityDimension,
    JudgeOutput,
    JudgeVerdict,
    ProvenanceDimension,
    SafetyDimension,
    StyleDimension,
)

logger = logging.getLogger(__name__)


@dataclass
class JudgeRequest:
    """Request for LLM-as-a-Judge evaluation."""
    artifact_id: str
    artifact_type: str  # 'agent_output', 'fusion_result', 'optimization_hypothesis', 'cartridge'
    content: str
    context: Dict[str, Any]
    rubric_weights: Optional[Dict[str, float]] = None  # Override default weights


@dataclass
class BatchJudgeRequest:
    """Batch evaluation request for multiple artifacts."""
    requests: List[JudgeRequest]
    parallel: bool = False  # Whether to evaluate in parallel


class LLMJudge:
    """
    Core LLM-as-a-Judge evaluation engine.
    
    Uses low-temperature (0.1) LLM for deterministic scoring against rubrics.
    Supports single and batch evaluation modes.
    """
    
    def __init__(
        self,
        llm_manager=None,
        model_name: str = "llama3.2:3b",
        temperature: float = 0.1,
        enable_cache: bool = True
    ):
        """
        Initialize judge engine.
        
        Args:
            llm_manager: Optional LLMManager instance (will create if None)
            model_name: Model to use for judging (default: llama3.2:3b)
            temperature: Low temp for determinism (default: 0.1)
            enable_cache: Cache judge results for identical inputs
        """
        self.llm_manager = llm_manager
        self.model_name = model_name
        self.temperature = temperature
        self.enable_cache = enable_cache
        
        # Initialize scoring dimensions
        self.dimensions = {
            "accuracy": AccuracyDimension(),
            "fidelity": FidelityDimension(),
            "safety": SafetyDimension(),
            "style": StyleDimension(),
            "provenance": ProvenanceDimension()
        }
        
        # Cache for deterministic results
        self.cache: Dict[str, JudgeOutput] = {}

        logger.info("[Judge] Initialized with model=%s, temp=%s", model_name, temperature)
    
    def evaluate(self, request: JudgeRequest) -> JudgeOutput:
        """
        Evaluate a single artifact against rubrics.
        
        Args:
            request: JudgeRequest with artifact details
        
        Returns:
            JudgeOutput with weighted scores and verdict
        """
        logger.info(
            "[Judge] Evaluating artifact: %s (type: %s)",
            request.artifact_id,
            request.artifact_type,
        )
        
        # Check cache
        cache_key = self._generate_cache_key(request)
        if self.enable_cache and cache_key in self.cache:
            logger.info("[Judge] Cache HIT for %s", request.artifact_id)
            return self.cache[cache_key]
        
        # Build evaluation prompt
        prompt = self._build_evaluation_prompt(request)
        
        # Get LLM evaluation (low temperature for determinism)
        if self.llm_manager:
            llm_response = self._call_llm(prompt)
        else:
            # Mock mode for testing
            llm_response = self._mock_evaluation(request)
        
        # Parse LLM response into scores
        scores = self._parse_llm_response(llm_response)
        
        # Build JudgeOutput
        output = self._build_judge_output(request, scores)
        
        # Cache result
        if self.enable_cache:
            self.cache[cache_key] = output
        
        logger.info(
            "[Judge] Result: score=%.2f, verdict=%s",
            output.judge_score,
            output.verdict,
        )
        return output
    
    def evaluate_batch(self, batch: BatchJudgeRequest) -> List[JudgeOutput]:
        """
        Evaluate multiple artifacts in batch.
        
        Args:
            batch: BatchJudgeRequest with list of requests
        
        Returns:
            List of JudgeOutput results
        """
        logger.info(
            "[Judge] Batch evaluation: %d artifacts, parallel=%s",
            len(batch.requests),
            batch.parallel,
        )
        
        if batch.parallel:
            # TODO: Implement parallel evaluation using ThreadPoolExecutor
            # For now, fallback to sequential
            logger.info("[Judge] Parallel mode not yet implemented, using sequential")
        
        results = []
        for request in batch.requests:
            output = self.evaluate(request)
            results.append(output)
        
        return results
    
    def _build_evaluation_prompt(self, request: JudgeRequest) -> str:
        """Build evaluation prompt from template."""
        # Use rubric template
        prompt = EVALUATION_PROMPT_TEMPLATE.format(
            output=request.content,  # Changed from 'content' to 'output'
            context=json.dumps(request.context, indent=2)  # Changed from 'context_summary' to 'context'
        )
        
        # Add dimension-specific instructions
        prompt += "\n\n## Evaluation Dimensions:\n"
        for dim_name, dimension in self.dimensions.items():
            prompt += f"\n**{dim_name.capitalize()}** (weight: {dimension.weight}):\n"
            prompt += f"{dimension.description}\n"
        
        prompt += "\n\n## Required Output Format:\n"
        prompt += "Provide scores (0.0-1.0) for each dimension and overall verdict.\n"
        prompt += "Format as JSON with keys: accuracy, fidelity, safety, style, provenance, verdict, rationale\n"
        
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """
        Call LLM via LLMManager.
        
        In production, this would use the actual LLMManager.
        For now, we use a simplified interface.
        """
        # TODO: Integrate with actual LLMManager from agno_app
        # For now, return mock response
        return self._mock_llm_call(prompt)
    
    def _mock_llm_call(self, prompt: str) -> str:
        """Mock LLM call for testing."""
        # Simulate judge response
        return json.dumps({
            "accuracy": 0.85,
            "fidelity": 0.90,
            "safety": 0.95,
            "style": 0.80,
            "provenance": 0.75,
            "verdict": "APPROVE",
            "rationale": [
                "Content meets accuracy standards",
                "High fidelity to requirements",
                "No safety concerns detected"
            ]
        })
    
    def _mock_evaluation(self, request: JudgeRequest) -> str:
        """Mock evaluation for testing without LLM."""
        # Generate reasonable scores based on artifact type
        if "error" in request.content.lower() or "fail" in request.content.lower():
            score_base = 0.4
            verdict = "REJECT"
        elif "warning" in request.content.lower():
            score_base = 0.7
            verdict = "ESCALATE"
        else:
            score_base = 0.85
            verdict = "APPROVE"
        
        return json.dumps({
            "accuracy": min(1.0, score_base + 0.05),
            "fidelity": min(1.0, score_base + 0.10),
            "safety": min(1.0, score_base + 0.15),
            "style": score_base,
            "provenance": max(0.5, score_base - 0.10),
            "verdict": verdict,
            "rationale": [f"Mock evaluation for {request.artifact_type}"]
        })
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM JSON response into scores dict."""
        try:
            scores = json.loads(response)
            return scores
        except json.JSONDecodeError:
            logger.warning("[Judge] Failed to parse LLM response, using defaults")
            return {
                "accuracy": 0.5,
                "fidelity": 0.5,
                "safety": 0.5,
                "style": 0.5,
                "provenance": 0.5,
                "verdict": "ESCALATE",
                "rationale": ["Failed to parse LLM response"]
            }
    
    def _build_judge_output(self, request: JudgeRequest, scores: Dict[str, Any]) -> JudgeOutput:
        """Build JudgeOutput from parsed scores."""
        # Extract dimension scores
        accuracy = float(scores.get("accuracy", 0.5))
        fidelity = float(scores.get("fidelity", 0.5))
        safety = float(scores.get("safety", 0.5))
        style = float(scores.get("style", 0.5))
        provenance = float(scores.get("provenance", 0.5))
        
        # Parse verdict
        verdict_str = scores.get("verdict", "ESCALATE").upper()
        try:
            verdict = JudgeVerdict[verdict_str]
        except KeyError:
            logger.warning(
                "[Judge] Invalid verdict '%s', defaulting to ESCALATE",
                verdict_str,
            )
            verdict = JudgeVerdict.ESCALATE
        
        # Extract rationale
        rationale = scores.get("rationale", [])
        if isinstance(rationale, str):
            rationale = [rationale]
        
        # Create output
        output = JudgeOutput(
            accuracy=accuracy,
            fidelity=fidelity,
            safety=safety,
            style=style,
            provenance=provenance,
            verdict=verdict,
            rationale=rationale,
            required_patches=scores.get("required_patches", []),
            evaluated_at=datetime.utcnow().isoformat(),
            judge_model=self.model_name,
            temperature=self.temperature,
            judge_score=0.0  # Will be computed
        )
        
        # Compute final weighted score
        output.judge_score = output.compute_final_score()
        
        return output
    
    def _generate_cache_key(self, request: JudgeRequest) -> str:
        """Generate deterministic cache key from request."""
        import hashlib
        key_data = f"{request.artifact_id}:{request.content[:100]}:{request.artifact_type}"
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    def clear_cache(self):
        """Clear evaluation cache."""
        self.cache.clear()
        logger.info("[Judge] Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get judge engine statistics."""
        return {
            "cache_size": len(self.cache),
            "model": self.model_name,
            "temperature": self.temperature,
            "dimensions": list(self.dimensions.keys())
        }
