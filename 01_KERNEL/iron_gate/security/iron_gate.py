# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import json
import os
import secrets
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

LEDGER_PATH = Path(__file__).resolve().parent.parent.parent / "PROVENANCE_LEDGER.md"
HITL_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "hitl_gate.json"


class IronGateWarden:
    """
    Sentinel's Iron Gate: manages high-risk action approvals.
    """

    def __init__(self):
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}
        self.config = self._load_gate_config()

    def _load_gate_config(self) -> Dict[str, Any]:
        try:
            with open(HITL_CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            # Safe default: require confirmation and keep lockdown off.
            return {
                "requires_confirmation": True,
                "confirmation_env_var": "CAMELOT_HITL_CONFIRM_TOKEN",
                "confirmation_token": "",
                "allow_plain_signature_fallback": False,
                "default_ttl_seconds": 60,
                "lockdown_mode": False,
            }

    def _now(self) -> datetime:
        return datetime.utcnow()

    def _is_expired(self, requested_at: str, ttl_seconds: int) -> bool:
        try:
            issued = datetime.fromisoformat(requested_at)
        except ValueError:
            return True
        return self._now() > issued + timedelta(seconds=max(1, ttl_seconds))

    def _expected_confirmation(self) -> str:
        env_var = self.config.get("confirmation_env_var", "")
        env_val = os.getenv(env_var, "").strip() if env_var else ""
        if env_val:
            return env_val

        fallback_allowed = bool(self.config.get("allow_plain_signature_fallback", False))
        static_token = str(self.config.get("confirmation_token", "")).strip()
        if fallback_allowed and static_token:
            return static_token
        return ""

    def request_approval(self, action: Dict[str, Any]) -> str:
        action_id = str(uuid.uuid4())
        ttl_default = int(self.config.get("default_ttl_seconds", 60))
        ttl_seconds = int(action.get("ttlSeconds", ttl_default))
        self.pending_approvals[action_id] = {
            "action": action,
            "status": "PENDING",
            "requested_at": self._now().isoformat(),
            "ttl": max(1, ttl_seconds),
        }
        print(f"[IRON_GATE] Approval Requested: {action_id} (Risk: {action.get('riskLevel')})")
        return action_id

    def verify_response(self, action_id: str, approved: bool, signature: str) -> bool:
        if self.config.get("lockdown_mode", False):
            print("[IRON_GATE] LOCKDOWN_MODE_ACTIVE")
            return False

        if action_id not in self.pending_approvals:
            print(f"[IRON_GATE] ACTION_NOT_FOUND: {action_id}")
            return False

        action_data = self.pending_approvals[action_id]
        if action_data.get("status") != "PENDING":
            print(f"[IRON_GATE] ACTION_ALREADY_FINALIZED: {action_id}")
            return action_data.get("status") == "APPROVED"

        if self._is_expired(action_data["requested_at"], int(action_data.get("ttl", 60))):
            action_data["status"] = "EXPIRED"
            print(f"[IRON_GATE] ACTION_EXPIRED: {action_id}")
            self.log_to_ledger(action_id, "EXPIRED", "NONE")
            return False

        if not approved:
            action_data["status"] = "REJECTED"
            print(f"[IRON_GATE] ACTION_REJECTED: {action_id}")
            self.log_to_ledger(action_id, "REJECTED", "NONE")
            return False

        requires_confirmation = bool(self.config.get("requires_confirmation", True))
        if requires_confirmation:
            expected = self._expected_confirmation()
            presented = (signature or "").strip()
            if not expected:
                action_data["status"] = "REJECTED"
                print(f"[IRON_GATE] CONFIRMATION_MISCONFIGURED: {action_id}")
                self.log_to_ledger(action_id, "REJECTED", "MISSING_EXPECTED_TOKEN")
                return False
            if not secrets.compare_digest(presented, expected):
                action_data["status"] = "REJECTED"
                print(f"[IRON_GATE] INVALID_CONFIRMATION: {action_id}")
                self.log_to_ledger(action_id, "REJECTED", "BAD_SIGNATURE")
                return False

        action_data["status"] = "APPROVED"
        action_data["signed_at"] = self._now().isoformat()
        print(f"[IRON_GATE] ACTION_APPROVED: {action_id}")
        self.log_to_ledger(action_id, "APPROVED", "CONFIRMED")
        return True

    def log_to_ledger(self, action_id: str, status: str, signature: str):
        try:
            action_data = self.pending_approvals.get(action_id, {})
            summary = action_data.get("action", {}).get("summary", "Unknown Action")
            risk = action_data.get("action", {}).get("riskLevel", "UNKNOWN")
            date_str = self._now().strftime("%Y-%m-%d")
            v_id = f"vIG.{action_id[:4]}"
            sig_preview = (signature or "NONE")[:16]

            new_row = (
                f"| {date_str} | {v_id:<7} | **Iron Gate** | "
                f"**GATE_{status}**: {summary} (Risk:{risk}, Sig:{sig_preview}) | Sentinel |\n"
            )

            with open(LEDGER_PATH, "a", encoding="utf-8") as f:
                f.write(new_row)
            print(f"[IRON_GATE] Ledger updated for {action_id}")
        except Exception as e:
            print(f"[IRON_GATE] LEDGER_UPDATE_FAILED: {e}")

    def get_action(self, action_id: str) -> Dict[str, Any]:
        return self.pending_approvals.get(action_id, {})


iron_gate = IronGateWarden()