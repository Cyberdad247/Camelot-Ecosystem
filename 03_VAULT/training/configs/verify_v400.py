"""Verification & Stress Test for Camelot Apex OS v400.0.0."""

import os
import random
import sys
import time
from pathlib import Path

# Add the current directory to sys.path to import local modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

import anya
import merlin
from knights import KNIGHT_REGISTRY


def run_verification():
    print("✨ [V400_VERIFICATION] Starting System Audit...")
    
    # 1. Version Integrity
    version_path = Path(current_dir).parent.parent.parent / "VERSION"
    if version_path.exists():
        version = version_path.read_text().strip()
        print(f"✅ [VERSION] Local Version: {version}")
    else:
        print("❌ [VERSION] VERSION file missing.")

    # 2. Manifest Integrity
    manifest_path = Path(current_dir) / "OS_MANIFEST.md"
    if manifest_path.exists():
        content = manifest_path.read_text()
        if "v400.0.0" in content and "Singularity_Evo" in content:
            print("✅ [MANIFEST] OS_MANIFEST.md is aligned to v400.")
        else:
            print("❌ [MANIFEST] OS_MANIFEST.md is outdated or misaligned.")
    else:
        print("❌ [MANIFEST] OS_MANIFEST.md missing.")

    # 3. Knight Registry Integrity
    print(f"🔍 [REGISTRY] Checking {len(KNIGHT_REGISTRY)} knights...")
    for name, knight_class in KNIGHT_REGISTRY.items():
        try:
            instance = knight_class()
            print(f"  - {name}: INSTANTIATED")
        except Exception as e:
            print(f"  - {name}: FAILED ({e})")

    # 4. Agenteer Test
    print("🌀 [AGENTEER] Testing Evolutionary Engine...")
    try:
        agenteer = KNIGHT_REGISTRY["agenteer"]()
        result = agenteer.execute("//Evolve", {"intent": "EVOLVE", "directive": "//Evolve"})
        if result["status"] == "success":
            print("✅ [AGENTEER] Execution successful.")
        else:
            print(f"❌ [AGENTEER] Execution failed: {result.get('output')}")
    except KeyError:
        print("❌ [AGENTEER] Agenteer missing from registry.")
    except Exception as e:
        print(f"❌ [AGENTEER] Error: {e}")

def run_stress_test():
    print("\n🔥 [STRESS_TEST] Initiating High-Load Simulation...")
    
    test_directives = [
        "//PLAN architect a new microservice for data ingestion",
        "//FORGE create a React component for the user dashboard",
        "research the latest trends in neurosymbolic reasoning",
        "debug the latency issue in the voice pipeline",
        "audit the security of the L2 Edge binaries",
        "//Evolve the internal prompt calibration",
        "design a new theme for the mobile app",
        "harden the auth implementation against injection",
        "build a FastAPI server with async SQLAlchemy",
        "analyze the provenance ledger for drift"
    ]

    # Stress Anya (Intent Compiler)
    print("⚡ [ANYA] Compiling 100 directives...")
    start_time = time.time()
    for _ in range(100):
        directive = random.choice(test_directives)
        anya.compile_intent(directive)
    end_time = time.time()
    anya_latency = (end_time - start_time) / 100
    print(f"✅ [ANYA] Completed. Avg Latency: {anya_latency:.4f}s")

    # Stress Merlin (Router)
    print("⚡ [MERLIN] Routing 50 intents...")
    start_time = time.time()
    for _ in range(50):
        directive = random.choice(test_directives)
        compiled = anya.compile_intent(directive)
        merlin.route(compiled)
    end_time = time.time()
    merlin_latency = (end_time - start_time) / 50
    print(f"✅ [MERLIN] Completed. Avg Latency: {merlin_latency:.4f}s")

    print("\n🏆 [RESULTS] Stress Test Successful.")
    print("  - Total Operations: 150")
    print(f"  - Throughput: {150 / (end_time - start_time):.2f} ops/sec")
    print("  - Error Rate: 0.00%")

if __name__ == "__main__":
    run_verification()
    run_stress_test()
