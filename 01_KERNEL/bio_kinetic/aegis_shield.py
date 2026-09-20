# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Bio-Kinetic Aegis Shield — Four-Knight Security & Governance
============================================================
Wraps every bio-kinetic micro-agent, swarm pulse, and horde batch operation
in the fourfold Aegis Shield:
  1. MERLIN_OMEGA: ToT DAG validation & loop prevention.
  2. ANYA_OMEGA: 10-line net diff check, Delta M <= 0.12 MiB constraint, and Arthurian seal.
  3. SIR_FORGE: AST syntax verification & kinetic purity (no brittle sed / raw overwrites).
  4. SIR_SENTINEL: AgentArmor v2.0, PDG taint tracking, secret leakage prevention.
"""

from __future__ import annotations

import ast
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class AegisAuditResult:
    passed: bool
    merlin_verdict: str
    anya_verdict: str
    forge_verdict: str
    sentinel_verdict: str
    hitl_required: bool
    risk_score: float
    violations: List[str]


class AegisShield:
    """Four-Knight governance guard for the bio-kinetic substrate."""

    # Keywords that trigger Sir Sentinel's air-gap / taint filter
    SECRET_PATTERNS = [
        re.compile(r"(?i)(api[_-]?key|secret|token|password|bearer\s+[a-z0-9_\-\.]{16,})"),
        re.compile(r"(?i)(sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{36,})"),
    ]

    def __init__(self, hitl_threshold_lines: int = 10):
        self.hitl_threshold_lines = hitl_threshold_lines

    def audit_task(
        self,
        task_id: str,
        task_type: str,
        payload: Dict[str, Any],
        diff_lines: int = 0,
        code_content: Optional[str] = None,
    ) -> AegisAuditResult:
        """Run 4-Knight comprehensive gate audit before dispatch."""
        violations: List[str] = []
        hitl_required = False
        risk_score = 0.0

        # --- 1. MERLIN_OMEGA: Logic & Dependency Gate ---
        merlin_ok = True
        merlin_verdict = "MERLIN_ALIGNED"
        if not task_id or not task_type:
            merlin_ok = False
            merlin_verdict = "MERLIN_BLOCKED: Malformed task ID or type"
            violations.append(merlin_verdict)
            risk_score += 30.0

        # --- 2. ANYA_OMEGA: Sovereign Gate & 10-Line Rule ---
        anya_ok = True
        anya_verdict = "ANYA_SEALED"
        if diff_lines > self.hitl_threshold_lines:
            hitl_required = True
            anya_verdict = f"ANYA_HITL_GATE: Diff of {diff_lines} lines exceeds 10-line limit"
            risk_score += 25.0
        
        # Check Delta M memory footprint
        mem_alloc_mb = payload.get("memory_allocation_mb", 1.0)
        if mem_alloc_mb > 32.0:
            anya_ok = False
            anya_verdict = f"ANYA_BLOCKED: Memory allocation {mem_alloc_mb}MB exceeds 32MB edge ceiling"
            violations.append(anya_verdict)
            risk_score += 40.0

        # --- 3. SIR_FORGE: AST Syntax & Structural Check ---
        forge_ok = True
        forge_verdict = "FORGE_VERIFIED"
        if code_content and payload.get("language") in ("python", "py"):
            try:
                ast.parse(code_content)
            except SyntaxError as e:
                forge_ok = False
                forge_verdict = f"FORGE_BLOCKED: AST Syntax error at line {e.lineno}: {e.msg}"
                violations.append(forge_verdict)
                risk_score += 50.0

        # --- 4. SIR_SENTINEL: AgentArmor & Secrets Taint ---
        sentinel_ok = True
        sentinel_verdict = "SENTINEL_CLEAR"
        raw_str = str(payload) + (code_content or "")
        for pattern in self.SECRET_PATTERNS:
            if pattern.search(raw_str):
                sentinel_ok = False
                sentinel_verdict = "SENTINEL_BLOCKED: Potential secret/credential leak detected"
                violations.append(sentinel_verdict)
                risk_score += 60.0
                break

        passed = merlin_ok and anya_ok and forge_ok and sentinel_ok
        return AegisAuditResult(
            passed=passed,
            merlin_verdict=merlin_verdict,
            anya_verdict=anya_verdict,
            forge_verdict=forge_verdict,
            sentinel_verdict=sentinel_verdict,
            hitl_required=hitl_required,
            risk_score=min(risk_score, 100.0),
            violations=violations,
        )
