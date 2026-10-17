#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""
Master Production DAG CLI Deployment Runner
CAMELOT-OS / Titan-OS vMAX
=============================================================================
Usage:
    python scripts/deploy_production_dag.py
    python scripts/deploy_production_dag.py --server
    python scripts/deploy_production_dag.py --diff-lines 5
    python scripts/deploy_production_dag.py --diff-lines 25 --operator-token "AUTH_TOKEN_XYZ"
    python scripts/deploy_production_dag.py --json
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from control_plane.infra.master_production_dag import MasterProductionDAG


def main():
    parser = argparse.ArgumentParser(description="CAMELOT-OS Master Production DAG Deployment Engine")
    parser.add_argument("--server", action="store_true", help="Deploy under 8GB Sovereign Server profile instead of 4GB Node")
    parser.add_argument("--diff-lines", type=int, default=4, help="Number of code lines modified (Iron Gate 2 checks <=10 limit)")
    parser.add_argument("--operator-token", type=str, default=None, help="HITL operator authorization token for diffs > 10 lines")
    parser.add_argument("--dry-run", action="store_true", help="Simulate pipeline without committing disk mutations")
    parser.add_argument("--json", action="store_true", help="Emit raw JSON execution receipt")
    parser.add_argument("--strict", action="store_true", default=True, help="Exit with code 1 if any phase fails")
    args = parser.parse_args()

    engine = MasterProductionDAG(is_server=args.server, operator_token=args.operator_token)
    receipt = engine.execute_full_pipeline(staged_diff_lines=args.diff_lines, dry_run=args.dry_run)

    if args.json:
        print(json.dumps(receipt.to_dict(), indent=2))
        if args.strict and receipt.overall_status != "PRODUCTION_DEPLOY_ACTIVE":
            sys.exit(1)
        return

    # Visual HUD Output
    role = "SOVEREIGN SERVER (8GB Hard Ceiling)" if args.server else "EDGE NODE (4GB Hard Ceiling)"
    status_icon = "🟢" if receipt.overall_status == "PRODUCTION_DEPLOY_ACTIVE" else "🔴"

    print("=" * 82)
    print(f"🏰 CAMELOT-OS // MASTER PRODUCTION DAG ENGINE (vMAX)")
    print(f"• Deployment Target: {role}")
    print(f"• Execution Timestamp: {receipt.timestamp}")
    print(f"• Total Latency: {receipt.total_latency_ms:.2f} ms")
    print(f"• Pipeline Status: {status_icon} {receipt.overall_status}")
    print(f"• Cryptographic Seal: {receipt.cryptographic_seal}")
    print("=" * 82)
    print(f"{'Phase ID':<24} | {'Phase Name':<40} | {'Latency':<8} | {'Status'}")
    print("-" * 82)

    for p in receipt.phases:
        p_status = "✅ PASS" if p.passed else "❌ FAIL"
        lat_str = f"{p.latency_ms:.1f}ms"
        print(f"{p.phase_id:<24} | {p.phase_name:<40} | {lat_str:<8} | {p_status}")
        if not p.passed and p.error_message:
            print(f"   └─ ⚠️  Error: {p.error_message}")

    print("-" * 82)
    print("SEAL: [Ω-TITAN-Σ:λ24-χ:UQLE-WEB4-LEECH-0xVIZION_INFINITY_SEALED]")
    print("=" * 82)

    if args.strict and receipt.overall_status != "PRODUCTION_DEPLOY_ACTIVE":
        sys.exit(1)


if __name__ == "__main__":
    main()
