import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

def test_dualmap_slo_escape():
    from control_plane.soul_router import SoulRouter
    router = SoulRouter()
    router.slo_threshold_ms = 100.0 # Aggressive SLO for test

    # Simulate high latency for Sir Helio AND Sir Sentinel
    for knight in ["sir_helio", "sir_sentinel"]:
        for _ in range(5):
            router.record_ttft(knight, 500.0)

    # Route an intent that normally targets sir_helio or sir_sentinel
    intent = "1m_context audit"
    decision = router.route(intent)

    # Should escape both and fall back to Tensor Scoring or Sir Boris
    assert decision.knight_id not in ["sir_helio", "sir_sentinel"]
    assert "DUALMAP_ESCAPE" in decision.reason
    print(f"SLO Escape Verified: {decision.knight_id} selected instead of slow knights.")
def test_linear_tier_slo_escape():
    from control_plane.soul_router import SoulRouter
    router = SoulRouter()
    router.slo_threshold_ms = 100.0
    
    # Simulate high latency for Ouroboros
    for _ in range(5):
        router.record_ttft("sir_ouroboros", 500.0)
        
    # Intent with high linear_need
    intent = "infinite_context reasoning"
    decision = router.route(intent, linear_need=0.9)
    
    # Should escape sir_ouroboros
    assert decision.knight_id != "sir_ouroboros"
    assert "DUALMAP_ESCAPE" in decision.reason
    print("Linear Tier SLO Escape Verified.")
