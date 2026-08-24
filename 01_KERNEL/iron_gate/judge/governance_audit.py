# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import sys
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    failures: list[str] = []

    authoritative_files = [
        "AGENTS.md",
        "docs/LAWS/TITANIUM_LAWS.md",
        "docs/LAWS/CONSTITUTION.md",
        "docs/ARCH/INSTRUCTION_GOVERNANCE.md",
        "01_KERNEL/config/CAMELOT_APEX_SYSTEM_PROMPT.md",
        "01_KERNEL/memory/UKG_CORE.toon",
        "01_KERNEL/config/hitl_gate.json",
        "01_KERNEL/security/iron_gate.py",
    ]
    for rel in authoritative_files:
        if not (root / rel).exists():
            failures.append(f"Missing required governance file: {rel}")

    agents_path = root / "AGENTS.md"
    ukg_path = root / "01_KERNEL/memory/UKG_CORE.toon"
    hitl_config_path = root / "01_KERNEL/config/hitl_gate.json"
    iron_gate_path = root / "01_KERNEL/security/iron_gate.py"
    laws_path = root / "docs/LAWS/TITANIUM_LAWS.md"
    apex_prompt_path = root / "01_KERNEL/config/CAMELOT_APEX_SYSTEM_PROMPT.md"

    if agents_path.exists():
        agents = read_text(agents_path)
        expected_agent_refs = [
            "docs/LAWS/TITANIUM_LAWS.md",
            "docs/EMPIRE_MAP.md",
            "docs/LAWS/CONSTITUTION.md",
            "01_KERNEL/security/policy.yaml",
        ]
        for ref in expected_agent_refs:
            if ref not in agents:
                failures.append(f"AGENTS.md missing expected reference: {ref}")
            elif not (root / ref).exists():
                failures.append(f"AGENTS.md reference does not exist: {ref}")

        banned_refs = [
            "docs/TITANIUM_LAWS.md",
            "docs/SECURITY_WARDEN_SPEC.md",
            "src.tools.antigravity",
        ]
        for ref in banned_refs:
            if ref in agents:
                failures.append(f"AGENTS.md contains deprecated/stale reference: {ref}")

    if ukg_path.exists():
        ukg = read_text(ukg_path)
        if "No_HITL" in ukg:
            failures.append("UKG policy contains No_HITL, conflicts with governance HITL requirement")
        if "Require_HITL" not in ukg:
            failures.append("UKG policy missing Require_HITL rule")
        if "LOCK | HITL:true" not in ukg:
            failures.append("UKG lock state must enforce HITL:true")

    if laws_path.exists():
        laws = read_text(laws_path)
        if "Human-in-the-Loop" not in laws and "HITL" not in laws:
            failures.append("Titanium laws missing HITL requirement language")

    if apex_prompt_path.exists():
        apex = read_text(apex_prompt_path)
        if "Human-in-the-Loop" not in apex and "HITL REQUIRED" not in apex:
            failures.append("CAMELOT_APEX_SYSTEM_PROMPT missing HITL requirement language")

    if hitl_config_path.exists():
        try:
            cfg = json.loads(read_text(hitl_config_path))
        except json.JSONDecodeError as exc:
            failures.append(f"Invalid JSON in hitl_gate.json: {exc}")
            cfg = {}

        if not cfg.get("requires_confirmation", False):
            failures.append("hitl_gate.json must require confirmation")
        if not isinstance(cfg.get("confirmation_env_var"), str) or not cfg.get("confirmation_env_var"):
            failures.append("hitl_gate.json must define non-empty confirmation_env_var")
        if cfg.get("allow_plain_signature_fallback", True):
            failures.append("hitl_gate.json must disable allow_plain_signature_fallback in CI")
        if int(cfg.get("default_ttl_seconds", 0)) <= 0:
            failures.append("hitl_gate.json must define positive default_ttl_seconds")

    if iron_gate_path.exists():
        gate = read_text(iron_gate_path)
        required_snippets = [
            "HITL_CONFIG_PATH",
            "os.getenv",
            "secrets.compare_digest",
            "_is_expired(",
            "CONFIRMATION_MISCONFIGURED",
            "INVALID_CONFIRMATION",
        ]
        for snippet in required_snippets:
            if snippet not in gate:
                failures.append(f"iron_gate.py missing required enforcement: {snippet}")

    if failures:
        print("Instruction governance checks failed:")
        for item in failures:
            print(f"- {item}")
        return 1

    print("Instruction governance checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
