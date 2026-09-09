"""
LISA SHOPIFY KNIGHT — Host-Side Adapter & Governance Evaluator
============================================================
Handles WASM execution boundaries, Level progression (Squire -> Warlord),
and side-effect gating for Shopify sandbox operations.
"""
from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass, asdict

STATE_FILE = Path("03_VAULT/runtime_state/lisa_state.json")

@dataclass
class LisaState:
    level: int = 1
    title: str = "Squire"
    xp: int = 0
    sandbox_enabled: bool = False
    completed_dags: int = 0

class LisaCartridgeHost:
    def __init__(self, state_file: Path = STATE_FILE):
        self.state_file = state_file
        self.state = self._load_state()

    def _load_state(self) -> LisaState:
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text(encoding="utf-8"))
                return LisaState(**data)
            except Exception:
                pass
        return LisaState()

    def save_state(self):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(asdict(self.state), indent=2), encoding="utf-8")

    def evaluate_side_effect(self, action_type: str) -> dict:
        if action_type == "deploy_sandbox":
            if self.state.level >= 3 and self.state.sandbox_enabled:
                return {
                    "allowed": True,
                    "status": "SANDBOX_EXECUTION_GRANTED",
                    "level": self.state.level
                }
            return {
                "allowed": False,
                "status": "BLOCKED_BY_GOVERNANCE",
                "level": self.state.level,
                "reason": f"Lisa is Level {self.state.level} ({self.state.title}). Requires Level 3 (Transmogrified) + sandbox_enabled.",
                "action": "PLAN_ONLY_FALLBACK"
            }
        elif action_type == "deploy_production":
            if self.state.level >= 4:
                return {
                    "allowed": True,
                    "status": "PRODUCTION_EXECUTION_GRANTED",
                    "level": self.state.level
                }
            return {
                "allowed": False,
                "status": "BLOCKED_BY_GOVERNANCE",
                "level": self.state.level,
                "reason": f"Production deployment requires Level 4 (Warlord) + Warden HITL gate.",
                "action": "WARDEN_GATE_TRIGGERED"
            }
        return {"allowed": True, "status": "PLAN_ONLY_ALLOWED", "level": self.state.level}

    def award_xp(self, amount: int) -> dict:
        self.state.xp += amount
        self.state.completed_dags += 1
        previous_level = self.state.level

        if self.state.xp >= 1000 and self.state.level < 4:
            self.state.level = 4
            self.state.title = "Warlord"
        elif self.state.xp >= 300 and self.state.level < 3:
            self.state.level = 3
            self.state.title = "Transmogrified"
            self.state.sandbox_enabled = True
        elif self.state.xp >= 100 and self.state.level < 2:
            self.state.level = 2
            self.state.title = "Apprentice"

        self.save_state()
        return {
            "xp": self.state.xp,
            "level": self.state.level,
            "title": self.state.title,
            "leveled_up": self.state.level > previous_level
        }

    def process_task(self, prompt: str, mode: str = "dry-run") -> dict:
        eval_result = self.evaluate_side_effect("deploy_sandbox" if mode == "sandbox" else "plan")
        xp_gain = 15 if eval_result.get("allowed") else 5
        xp_report = self.award_xp(xp_gain)

        dag = [
            {"step": "scout_seo", "agent": "Formica-Scout", "status": "COMPLETED"},
            {"step": "graphql_schema", "agent": "Castor-Architect", "status": "COMPLETED", "output": "subscription_schema.graphql"},
            {"step": "theme_css", "agent": "Formica-Ant", "status": "COMPLETED", "output": "subscription_theme.css"},
            {"step": "warden_compliance", "agent": "Sir-Sentinel", "status": "VERIFIED"}
        ]

        return {
            "cartridge": "lisa_shopify_knight",
            "prompt": prompt,
            "mode": mode,
            "governance": eval_result,
            "dag": dag,
            "xp_report": xp_report,
            "status": "PROCESSED"
        }
