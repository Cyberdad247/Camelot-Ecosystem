# Copyright (c) 2026 CAMELOT-OS. All rights reserved.
# -*- coding: utf-8 -*-
"""
PHASE 4: OLLAMA INTEGRATION TEST
Quick test to verify Ollama integration with Camelot OS.
"""
import sys
from pathlib import Path

# Add paths
vault_path = Path(__file__).parent.parent / "03_VAULT"
sys.path.insert(0, str(vault_path))

from ollama_client import OllamaClient

def main():
    """Test Ollama integration."""
    print("[TEST] Initializing Ollama Client...")
    client = OllamaClient()
    
    print("[TEST] Listing available models...")
    models = client.list_models()
    print(f"[OK] Found {len(models)} models:")
    for model in models:
        print(f"  - {model['name']}")
    
    # Use the smallest model for testing
    test_model = "llama3.2:1b"
    print(f"\n[TEST] Generating with {test_model}...")
    
    try:
        response = client.generate(
            model=test_model,
            prompt="What is the Law of Locality? Answer in one sentence.",
            system="You are a helpful AI assistant. Be concise.",
            max_tokens=50
        )
        
        print(f"\n[SUCCESS] Response:")
        print(response.get("response", "No response"))
        print(f"\n[TEST] Integration test PASSED!")
        
    except Exception as e:
        print(f"\n[ERROR] Integration test FAILED: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
