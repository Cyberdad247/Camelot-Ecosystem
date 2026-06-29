import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

def test_intent_retention_classification():
    from control_plane.cli_intercept import estimate_retention_class
    
    # SCHEMA_STATIC: System-level, high recompute cost, high frequency
    assert estimate_retention_class("//BOOT") == "SCHEMA_STATIC"
    assert estimate_retention_class("//SCAN .") == "SCHEMA_STATIC"
    assert estimate_retention_class("Omega_AUDIT") == "SCHEMA_STATIC"
    
    # SESSION_STATE: Mission-specific, medium duration
    assert estimate_retention_class("//FORGE add login button") == "SESSION_STATE"
    assert estimate_retention_class("//PLAN architecture update") == "SESSION_STATE"
    
    # ONE_OFF: Low priority, ephemeral
    assert estimate_retention_class("hello") == "ONE_OFF"
    assert estimate_retention_class("what time is it?") == "ONE_OFF"
    assert estimate_retention_class("random question about space") == "ONE_OFF"
