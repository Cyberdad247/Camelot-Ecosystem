# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Test Suite for LLM-as-a-Judge Engine

Validates judge scoring, batch evaluation, caching, and rubric integration.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm_judge import LLMJudge, JudgeRequest, BatchJudgeRequest
from rubric import JudgeVerdict


def test_single_evaluation():
    """Test single artifact evaluation."""
    print("\n=== Testing Single Evaluation ===")
    
    judge = LLMJudge(model_name="llama3.2:3b", temperature=0.1)
    
    request = JudgeRequest(
        artifact_id="test_001",
        artifact_type="agent_output",
        content="The authentication system uses OAuth2 for secure token-based authentication.",
        context={
            "intent": "Explain authentication",
            "source": "engineering_cartridge"
        }
    )
    
    output = judge.evaluate(request)
    
    print(f"✅ Judge score: {output.judge_score:.2f}")
    print(f"✅ Verdict: {output.verdict}")
    print(f"✅ Accuracy: {output.accuracy:.2f}")
    print(f"✅ Safety: {output.safety:.2f}")
    print(f"✅ Rationale: {output.rationale}")
    
    assert 0.0 <= output.judge_score <= 1.0, "Score should be in [0, 1]"
    assert output.verdict in [JudgeVerdict.APPROVE, JudgeVerdict.REJECT, JudgeVerdict.ESCALATE]


def test_batch_evaluation():
    """Test batch evaluation mode."""
    print("\n=== Testing Batch Evaluation ===")
    
    judge = LLMJudge()
    
    requests = [
        JudgeRequest(
            artifact_id="batch_001",
            artifact_type="fusion_result",
            content="Successful fusion of Strategy + Engineering agents",
            context={"agents": ["Lord Nexus", "Sir Lukas"]}
        ),
        JudgeRequest(
            artifact_id="batch_002",
            artifact_type="optimization_hypothesis",
            content="Cache resize from 50 to 100 entries improves hit rate by 15%",
            context={"metric": "cache_hit_rate"}
        ),
        JudgeRequest(
            artifact_id="batch_003",
            artifact_type="cartridge",
            content="New cartridge: DataScienceCore with pandas/numpy tools",
            context={"template": "ENGINEERING_CORE"}
        )
    ]
    
    batch = BatchJudgeRequest(requests=requests, parallel=False)
    results = judge.evaluate_batch(batch)
    
    print(f"✅ Batch evaluated {len(results)} artifacts")
    
    for i, result in enumerate(results):
        print(f"  - Artifact {i+1}: score={result.judge_score:.2f}, verdict={result.verdict}")
    
    assert len(results) == 3, "Should return all batch results"


def test_cache_behavior():
    """Test deterministic caching."""
    print("\n=== Testing Cache Behavior ===")
    
    judge = LLMJudge(enable_cache=True)
    
    request = JudgeRequest(
        artifact_id="cache_test",
        artifact_type="agent_output",
        content="Test caching with identical request",
        context={}
    )
    
    # First evaluation (cache miss)
    output1 = judge.evaluate(request)
    
    # Second evaluation (cache hit)
    output2 = judge.evaluate(request)
    
    print(f"✅ First eval score: {output1.judge_score:.2f}")
    print(f"✅ Second eval score: {output2.judge_score:.2f}")
    print(f"✅ Cache size: {judge.get_stats()['cache_size']}")
    
    assert output1.judge_score == output2.judge_score, "Cached results should be identical"
    assert judge.get_stats()['cache_size'] == 1


def test_verdict_thresholds():
    """Test automatic verdict assignment based on scores."""
    print("\n=== Testing Verdict Thresholds ===")
    
    judge = LLMJudge()
    
    # High quality (should approve)
    high_quality = JudgeRequest(
        artifact_id="high_quality",
        artifact_type="agent_output",
        content="Excellent output meeting all criteria",
        context={}
    )
    
    # Low quality (should reject)
    low_quality = JudgeRequest(
        artifact_id="low_quality",
        artifact_type="agent_output",
        content="error: failed to meet requirements",
        context={}
    )
    
    # Medium quality (should escalate)
    medium_quality = JudgeRequest(
        artifact_id="medium_quality",
        artifact_type="agent_output",
        content="warning: some issues detected",
        context={}
    )
    
    high_result = judge.evaluate(high_quality)
    low_result = judge.evaluate(low_quality)
    medium_result = judge.evaluate(medium_quality)
    
    print(f"✅ High quality: score={high_result.judge_score:.2f}, verdict={high_result.verdict}")
    print(f"✅ Low quality: score={low_result.judge_score:.2f}, verdict={low_result.verdict}")
    print(f"✅ Medium quality: score={medium_result.judge_score:.2f}, verdict={medium_result.verdict}")
    
    assert high_result.verdict == JudgeVerdict.APPROVE
    assert low_result.verdict == JudgeVerdict.REJECT


def test_dimension_scoring():
    """Test individual dimension score extraction."""
    print("\n=== Testing Dimension Scoring ===")
    
    judge = LLMJudge()
    
    request = JudgeRequest(
        artifact_id="dimensions_test",
        artifact_type="agent_output",
        content="OAuth2 provides security through token-based authentication",
        context={"domain": "security"}
    )
    
    output = judge.evaluate(request)
    
    print(f"✅ Accuracy: {output.accuracy:.2f} (weight: 0.30)")
    print(f"✅ Fidelity: {output.fidelity:.2f} (weight: 0.25)")
    print(f"✅ Safety: {output.safety:.2f} (weight: 0.20)")
    print(f"✅ Style: {output.style:.2f} (weight: 0.15)")
    print(f"✅ Provenance: {output.provenance:.2f} (weight: 0.10)")
    
    # Verify weighted calculation
    manual_score = (
        0.30 * output.accuracy +
        0.25 * output.fidelity +
        0.20 * output.safety +
        0.15 * output.style +
        0.10 * output.provenance
    )
    
    print(f"✅ Final score: {output.judge_score:.2f}")
    print(f"✅ Manual calc: {manual_score:.2f}")
    
    assert abs(output.judge_score - manual_score) < 0.01, "Weighted score should match formula"


def test_judge_stats():
    """Test stats reporting."""
    print("\n=== Testing Judge Stats ===")
    
    judge = LLMJudge(model_name="llama3.2:3b", enable_cache=True)
    
    stats = judge.get_stats()
    
    print(f"✅ Model: {stats['model']}")
    print(f"✅ Temperature: {stats['temperature']}")
    print(f"✅ Dimensions: {stats['dimensions']}")
    print(f"✅ Cache size: {stats['cache_size']}")
    
    assert stats['model'] == "llama3.2:3b"
    assert stats['temperature'] == 0.1
    assert len(stats['dimensions']) == 5


if __name__ == "__main__":
    print("🧪 LLM-as-a-Judge Engine — Test Suite\n")
    
    test_single_evaluation()
    test_batch_evaluation()
    test_cache_behavior()
    test_verdict_thresholds()
    test_dimension_scoring()
    test_judge_stats()
    
    print("\n✅ All judge tests passed!")