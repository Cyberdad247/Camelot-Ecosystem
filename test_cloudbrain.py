import sys

# Add root to sys.path so we can import 01_KERNEL
sys.path.insert(0, r"C:\Users\vizio\CAMELOT_OS")

import json

try:
    from notebooklmpy import NotebookLM
except ImportError:
    # Need to simulate if it's an MCP environment where the py wrapper isn't strictly available in the python env
    print("NotebookLM not available directly in Python script. Please check MCP instead.")
    
from importlib import import_module
hydration = import_module("01_KERNEL.memory.hydration_manager")
HydrationManager = hydration.HydrationManager

def test_pipeline():
    print("Testing Knight Cloud Brain Pipeline...")
    
    # 1. Initialize HydrationManager with SIR_ALEX
    mgr = HydrationManager(knight_id="SIR_ALEX")
    
    # 2. Store L2 context (should push to NotebookLM)
    intent = "test_l2_burst"
    content = {
        "status": "active",
        "description": "This is a test of the Knight -> Cloud Brain pipeline from SIR_ALEX.",
        "layer": "L2"
    }
    
    print(f"\nStoring L2 artifact for {intent}...")
    mgr.store_tissue(intent=intent, content=content, complexity=9, tier="L2")
    
    # 3. Hydrate L2 context (should query NotebookLM)
    print(f"\nHydrating context for {intent}...")
    result = mgr.hydrate_context(intent=intent, complexity=9)
    
    print("\nResult:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_pipeline()
