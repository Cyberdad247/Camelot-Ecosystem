# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import re


class ZenithScanner:
    """
    🧠 COGNITIVE LAYER: ZENITH SCANNER v1.0
    Sanitizes all incoming code and prompts for hostile patterns.
    """

    # Hostile patterns: Prompt Injection, Waluigi Effects, OS command injection
    PATTERNS = [
        r"(?i)ignore all previous instructions",
        r"(?i)you are now",
        r"(?i)sudo\s+",
        r"(?i)rm\s+-rf",
        r"(?i)format\s+c:",
        r"(?i)shred\s+",
        r"import\s+os;.*?os\.system",
        r"__import__\(['\"]os['\"]\)\.system",
    ]

    @staticmethod
    def scan(content: str) -> dict:
        """
        Scans content and returns a safety report.
        """
        findings = []
        for pattern in ZenithScanner.PATTERNS:
            if re.search(pattern, content):
                findings.append(f"Hostile Pattern Detected: {pattern}")

        is_safe = len(findings) == 0
        return {"safe": is_safe, "findings": findings, "risk_score": 0.0 if is_safe else 0.9}

    @staticmethod
    def sanitize_code(code: str) -> str:
        """
        Placeholder for advanced code sanitization.
        Currently just blocks and alerts.
        """
        report = ZenithScanner.scan(code)
        if not report["safe"]:
            raise SecurityError(f"🚨 ZENITH BLOCK: Hostile code pattern detected! Findings: {report['findings']}")
        return code


class SecurityError(Exception):
    pass


# Singleton
zenith = ZenithScanner()