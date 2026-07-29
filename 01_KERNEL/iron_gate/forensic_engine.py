# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import json
import re
from datetime import datetime
from pathlib import Path


class ForensicEngine:
    """
    Track GAMMA: Forensic Sovereign Upgrade (L6 Governance).
    Scans PROVENANCE_LEDGER.md for historical scars, but logs passive checks
    to runtime state so read-only commands do not mutate provenance.
    """

    def __init__(self, ledger_path: str = "C:/Users/vizio/CAMELOT_OS/PROVENANCE_LEDGER.md"):
        self.ledger_path = Path(ledger_path)
        self.scars = []
        self._index_scars()

    def _index_scars(self):
        """Index historical failures and security incidents from the ledger."""
        if not self.ledger_path.exists():
            return

        scar_keywords = [
            r"REMEDIATION",
            r"PATCH",
            r"ROLLBACK",
            r"VULNERABILITY",
            r"RCE",
            r"BLOCK",
            r"FIX",
            r"FAILED",
            r"CRASH",
            r"PURGED",
        ]
        pattern = re.compile("|".join(scar_keywords), re.IGNORECASE)

        try:
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                for line in f:
                    if pattern.search(line):
                        self.scars.append(line.strip())
        except Exception as e:
            print(f"[FORENSIC_ENGINE] Error reading ledger: {e}")

    def analyze_impact(self, module_path: str, intent: str) -> dict:
        """
        Analyze risk score from historical module path and intent type.
        Returns: { 'risk_score': float, 'alerts': list[str] }
        """
        risk_score = 0.0
        alerts = []

        module_path_norm = module_path.replace("\\", "/").lower()
        module_name = Path(module_path).name.lower()
        intent_lower = intent.lower()

        relevant_scars = []
        intent_words = [w for w in re.split(r"\W+", intent_lower) if len(w) > 3]
        for scar in self.scars:
            scar_lower = scar.lower().replace("\\", "/")
            module_match = module_name in scar_lower or module_path_norm in scar_lower
            intent_match = any(word in scar_lower for word in intent_words)
            if module_match or intent_match:
                relevant_scars.append(scar)

        if relevant_scars:
            risk_score = min(0.1 * len(relevant_scars), 1.0)
            combined_scars = " ".join(relevant_scars).upper()
            if "RCE" in combined_scars or "VULNERABILITY" in combined_scars:
                risk_score = max(risk_score, 0.8)
                alerts.append("Historical Security Critical (RCE/Vulnerability) detected in context.")
            if any(kw in combined_scars for kw in ["PATCH", "FIX", "REMEDIATION", "FAILED"]):
                alerts.append(f"Module has {len(relevant_scars)} recent remediation/failure entries.")

        return {
            "risk_score": round(risk_score, 2),
            "alerts": alerts,
            "relevant_count": len(relevant_scars),
        }

    def log_check(self, module_path: str, intent: str, result: dict):
        """Log passive forensic checks to runtime state, not provenance."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
        runtime_log = self.ledger_path.parent / "03_VAULT" / "runtime_state" / "forensic_checks.jsonl"
        event = {
            "timestamp_utc": timestamp,
            "module_path": module_path,
            "intent": intent,
            "risk_score": result.get("risk_score", 0.0),
            "alerts": result.get("alerts", []),
            "relevant_count": result.get("relevant_count", 0),
        }
        try:
            runtime_log.parent.mkdir(parents=True, exist_ok=True)
            with open(runtime_log, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
        except Exception as e:
            print(f"[FORENSIC_ENGINE] Failed to log runtime check: {e}")


if __name__ == "__main__":
    engine = ForensicEngine()
    impact = engine.analyze_impact("security/warden.py", "Update firewall rules")
    print(f"Impact Analysis: {impact}")
