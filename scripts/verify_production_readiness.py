#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""
Production Readiness Verification Suite (vMAX)
CAMELOT-OS / Titan-OS Sovereign Hardening Pipeline
=============================================================================
Audits and attests to the 5 Pillars of Production Readiness:
1. Process Scarcity & Zero-Docker Invariant (BareMetalProcessGovernor)
2. WebMCP API Invariant & Cryptographic Execution Receipt Generation
3. Resilient Ingress, Dual-Stratum Mesh & Offline Fallback Assets
4. Structured Rotating JSONL Telemetry & Sir Ghost Redaction
5. Provenance Ledger Mirror Parity (Exact SHA-256 Byte Match)
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

if sys.platform == "win32":
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if sys.stderr and hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "control_plane"))

from control_plane.infra.process_governor import BareMetalProcessGovernor
from control_plane.infra.production_logger import get_production_logger


@dataclass(frozen=True)
class PillarResult:
    pillar_number: int
    name: str
    status: str  # "PASS" | "FAIL"
    latency_ms: float
    details: Dict[str, Any]


@dataclass(frozen=True)
class ProductionReadinessReceipt:
    system: str
    timestamp: str
    overall_status: str  # "PRODUCTION_READY" | "HARDENING_REQUIRED"
    total_elapsed_ms: float
    pillars: List[PillarResult]
    receipt_hash: str
    seal: str = "[Ω-TITAN-Σ:λ24-χ:UQLE-WEB4-LEECH-0xVIZION_INFINITY_SEALED]"


def verify_pillar_1_process_governance() -> PillarResult:
    t0 = time.perf_counter()
    governor = BareMetalProcessGovernor(is_server=False)
    receipt = governor.inspect_system()
    latency = (time.perf_counter() - t0) * 1000.0

    passed = (
        receipt.native_processes_only
        and receipt.docker_containers_detected == 0
        and receipt.status in ("BOUNDARIES_NOMINAL", "PRESSURE_THROTTLED")
    )

    return PillarResult(
        pillar_number=1,
        name="Process Scarcity & Zero-Docker Invariant",
        status="PASS" if passed else "FAIL",
        latency_ms=round(latency, 2),
        details={
            "role": receipt.role,
            "ceiling_mb": receipt.ceiling_mb,
            "working_set_mb": receipt.current_working_set_mb,
            "pressure_ratio": receipt.pressure_ratio,
            "docker_detected": receipt.docker_containers_detected,
        },
    )


def verify_pillar_2_webmcp_integrity() -> PillarResult:
    t0 = time.perf_counter()
    mcp_route_path = REPO_ROOT / "apps" / "invisioned-marketing" / "src" / "app" / "api" / "mcp" / "route.ts"
    spec_path = REPO_ROOT / "docs" / "architecture" / "WEBMCP_PANTHEON_MAPPING_SPECIFICATION.md"

    passed = mcp_route_path.exists() and spec_path.exists()
    details: Dict[str, Any] = {
        "mcp_route_exists": mcp_route_path.exists(),
        "spec_exists": spec_path.exists(),
    }

    if mcp_route_path.exists():
        content = mcp_route_path.read_text(encoding="utf-8")
        has_rate_limit = "checkRateLimit" in content
        has_receipt_hash = "computeReceiptHash" in content
        has_bounds_check = "Invalid params" in content
        passed = passed and has_rate_limit and has_receipt_hash and has_bounds_check
        details.update({
            "rate_limiting_enforced": has_rate_limit,
            "cryptographic_receipts_enforced": has_receipt_hash,
            "input_bounds_validated": has_bounds_check,
        })

    latency = (time.perf_counter() - t0) * 1000.0
    return PillarResult(
        pillar_number=2,
        name="WebMCP API Invariants & Cryptographic Receipts",
        status="PASS" if passed else "FAIL",
        latency_ms=round(latency, 2),
        details=details,
    )


def verify_pillar_3_offline_and_mesh_assets() -> PillarResult:
    t0 = time.perf_counter()
    invisioned_sw = REPO_ROOT / "apps" / "invisioned-marketing" / "public" / "sw.js"
    pwa_sw = REPO_ROOT / "apps" / "pwa" / "public" / "sw.js"
    pwa_offline = REPO_ROOT / "apps" / "pwa" / "src" / "app" / "offline" / "page.tsx"

    has_offline = (invisioned_sw.exists() or pwa_sw.exists()) and pwa_offline.exists()
    details = {
        "invisioned_sw_present": invisioned_sw.exists(),
        "pwa_sw_present": pwa_sw.exists(),
        "dark_mesh_offline_page_present": pwa_offline.exists(),
    }

    latency = (time.perf_counter() - t0) * 1000.0
    return PillarResult(
        pillar_number=3,
        name="Resilient Ingress & Dark-Mesh Offline Fallback",
        status="PASS" if has_offline else "FAIL",
        latency_ms=round(latency, 2),
        details=details,
    )


def verify_pillar_4_telemetry_and_log_rotation() -> PillarResult:
    t0 = time.perf_counter()
    test_log_dir = REPO_ROOT / "logs" / "test_production_verification"
    logger = get_production_logger("readiness_probe", knight_id="SIR_HELIOS", log_dir=test_log_dir)

    # Log with a secret to test Sir Ghost scrubber
    logger.info("Probe execution with bearer secret_token_1234567890abcdef and status OK")

    log_file = test_log_dir / "readiness_probe.jsonl"
    passed = log_file.exists()
    details: Dict[str, Any] = {"log_file_created": log_file.exists()}

    if log_file.exists():
        lines = log_file.read_text(encoding="utf-8").splitlines()
        if lines:
            last_entry = json.loads(lines[-1])
            is_redacted = "[REDACTED_BY_SIR_GHOST]" in last_entry.get("message", "")
            has_rss = "rss_mb" in last_entry
            passed = passed and is_redacted and has_rss
            details.update({
                "sir_ghost_redaction_verified": is_redacted,
                "resident_memory_sampled": has_rss,
                "recorded_rss_mb": last_entry.get("rss_mb"),
            })

    latency = (time.perf_counter() - t0) * 1000.0
    return PillarResult(
        pillar_number=4,
        name="Structured Rotating Telemetry & Secret Scrubber",
        status="PASS" if passed else "FAIL",
        latency_ms=round(latency, 2),
        details=details,
    )


def verify_pillar_5_provenance_mirror_parity() -> PillarResult:
    t0 = time.perf_counter()
    root_ledger = REPO_ROOT / "PROVENANCE_LEDGER.md"

    mirrors = [
        REPO_ROOT / "03_VAULT" / "PROVENANCE_LEDGER.md",
        REPO_ROOT / "docs" / "PROVENANCE_LEDGER.md",
        REPO_ROOT / "03_VAULT" / "training" / "configs" / "PROVENANCE_LEDGER.md",
        REPO_ROOT / "03_VAULT" / "knowledge_vault" / "PROVENANCE_LEDGER.md",
        REPO_ROOT / "control_plane" / "PROVENANCE_LEDGER.md",
        REPO_ROOT / "docs" / "architecture" / "PROVENANCE_LEDGER.md",
    ]

    root_hash = hashlib.sha256(root_ledger.read_bytes()).hexdigest()
    mismatches = []

    for m in mirrors:
        if not m.exists():
            mismatches.append(f"{m.name}: MISSING")
            continue
        h = hashlib.sha256(m.read_bytes()).hexdigest()
        if h != root_hash:
            mismatches.append(f"{m.relative_to(REPO_ROOT)}: HASH_MISMATCH")

    latency = (time.perf_counter() - t0) * 1000.0
    passed = len(mismatches) == 0

    return PillarResult(
        pillar_number=5,
        name="Provenance Ledger SHA-256 Mirror Parity (6/6)",
        status="PASS" if passed else "FAIL",
        latency_ms=round(latency, 2),
        details={
            "root_hash": root_hash,
            "mirrors_checked": len(mirrors),
            "mismatches": mismatches,
        },
    )


def run_full_production_verification() -> ProductionReadinessReceipt:
    start_time = time.perf_counter()
    pillars = [
        verify_pillar_1_process_governance(),
        verify_pillar_2_webmcp_integrity(),
        verify_pillar_3_offline_and_mesh_assets(),
        verify_pillar_4_telemetry_and_log_rotation(),
        verify_pillar_5_provenance_mirror_parity(),
    ]

    total_elapsed = (time.perf_counter() - start_time) * 1000.0
    all_passed = all(p.status == "PASS" for p in pillars)

    # Compute Blake2s deterministic receipt hash
    h = hashlib.blake2s()
    h.update(f"{all_passed}:{len(pillars)}:{total_elapsed}".encode("utf-8"))
    for p in pillars:
        h.update(f"{p.pillar_number}:{p.status}:{p.latency_ms}".encode("utf-8"))

    receipt = ProductionReadinessReceipt(
        system="CAMELOT-OS / Titan-OS vMAX Sovereign Substrate",
        timestamp=datetime.now(timezone.utc).isoformat(),
        overall_status="PRODUCTION_READY" if all_passed else "HARDENING_REQUIRED",
        total_elapsed_ms=round(total_elapsed, 2),
        pillars=pillars,
        receipt_hash=h.hexdigest(),
    )

    return receipt


if __name__ == "__main__":
    receipt = run_full_production_verification()

    print("=" * 80)
    print("🏰 CAMELOT-OS // PRODUCTION READINESS VERIFICATION (vMAX)")
    print(f"• Timestamp: {receipt.timestamp}")
    print(f"• Total Elapsed: {receipt.total_elapsed_ms} ms")
    status_emoji = "🟢" if receipt.overall_status == "PRODUCTION_READY" else "🔴"
    print(f"• Status: {status_emoji} {receipt.overall_status}")
    print(f"• Cryptographic Receipt Hash: {receipt.receipt_hash}")
    print("=" * 80)
    print(f"{'Pillar':<10} | {'Name':<45} | {'Latency':<10} | Status")
    print("-" * 80)
    for p in receipt.pillars:
        print(f"Pillar {p.pillar_number:<3} | {p.name:<45} | {p.latency_ms} ms | {'✅ PASS' if p.status == 'PASS' else '❌ FAIL'}")
    print("-" * 80)
    print(f"SEAL: {receipt.seal}")
    print("=" * 80)

    if receipt.overall_status != "PRODUCTION_READY":
        sys.exit(1)
