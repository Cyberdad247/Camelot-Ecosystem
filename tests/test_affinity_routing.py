import pytest
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

def test_affinity_key_consistency():
    from control_plane.cli_intercept import generate_affinity_key
    # Identical structural prompts should yield the same affinity key
    prompt1 = "Summarize this file: C:/path/a.py"
    prompt2 = "Summarize this file: C:/path/b.py"
    
    key1 = generate_affinity_key(prompt1)
    key2 = generate_affinity_key(prompt2)
    assert key1 == key2

def test_affinity_key_different():
    from control_plane.cli_intercept import generate_affinity_key
    # Different structural intents should yield different keys
    key1 = generate_affinity_key("//BOOT")
    key2 = generate_affinity_key("//SCAN .")
    assert key1 != key2

def test_affinity_key_uuid_abstraction():
    from control_plane.cli_intercept import generate_affinity_key
    p1 = "Audit session: 8c656cfa-a189-409e-a72d-07692a47f17e"
    p2 = "Audit session: bcaadfdd-1654-487d-9c4c-111f7dea120e"
    assert generate_affinity_key(p1) == generate_affinity_key(p2)
