#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""
Sovereign System Verification DAG CLI Runner
CAMELOT-OS / Titan-OS v10001
=============================================================================
Usage:
    python scripts/verify_sovereign_dag.py
    python scripts/verify_sovereign_dag.py --server
    python scripts/verify_sovereign_dag.py --remediate
    python scripts/verify_sovereign_dag.py --json
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from control_plane.infra.sovereign_verification_dag import SovereignVerificationDAG


def main():
    parser = argparse.ArgumentParser(description="CAMELOT-OS Sovereign Verification DAG Runner")
    parser.add_argument("--server", action="store_true", help="Evaluate under 8GB Sovereign Server limits instead of 4GB Node")
    parser.add_argument("--remediate", action="store_true", help="Automatically trigger working set trim & cache eviction on pressure")
    parser.add_argument("--json", action="store_true", help="Emit raw JSON execution receipt")
    parser.add_argument("--strict", action="store_true", default=True, help="Exit with code 1 if any gate fails")
    args = parser.parse_args()

    dag = SovereignVerificationDAG(is_server=args.server, remediate=args.remediate)
    receipt = dag.execute_all()

    if args.json:
        print(json.dumps(receipt.to_dict(), indent=2))
        if args.strict and receipt.overall_status != "ALL_GATES_PASSED":
            sys.exit(1)
        return

    # Visual Terminal HUD Output
    role = "SOVEREIGN SERVER (8GB Cap)" if args.server else "CAMELOT NODE (4GB Cap)"
    status_icon = "🟢" if receipt.overall_status == "ALL_GATES_PASSED" else "🔴"

    print("=" * 80)
    print(f"🏰 CAMELOT-OS // SOVEREIGN SYSTEM VERIFICATION DAG (v10001)")
    print(f"• Target Role: {role}")
    print(f"• Execution Timestamp: {receipt.timestamp}")
    print(f"• Total Elapsed: {receipt.execution_time_ms:.2f} ms")
    print(f"• Overall Status: {status_icon} {receipt.overall_status}")
    print(f"• Cryptographic DAG Hash: {receipt.dag_hash}")
    print("=" * 80)
    print(f"{'Gate Name':<35} | {'Node ID':<25} | {'Latency':<10} | {'Status'}")
    print("-" * 80)

    for g in receipt.gate_results:
        g_status = "✅ PASS" if g.passed else "❌ FAIL"
        lat = f"{g.latency_us:.1f} µs" if g.latency_us < 1000 else f"{g.latency_us/1000:.2f} ms"
        print(f"{g.gate_name:<35} | {g.node_id:<25} | {lat:<10} | {g_status}")
        if not g.passed and g.error_message:
            print(f"   └─ ⚠️  Error: {g.error_message}")
        if g.remediated:
            print(f"   └─ 🔧 Remediation: Working set trimmed & cache pruned.")

    print("-" * 80)
    print(f"SEAL: [Ω-TITAN-Σ:λ24-χ:UQLE-WEB4-LEECH-0xVIZION_INFINITY_SEALED]")
    print("=" * 80)

    if args.strict and receipt.overall_status != "ALL_GATES_PASSED":
        sys.exit(1)


if __name__ == "__main__":
    main()
