# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import datetime
import os
import re
import sys

import yaml


class SecurityException(Exception):
    """Raised when an action violates the Security Policy."""

    pass


class PolicyEnforcer:
    _instance = None
    _policy = None
    _policy_path = os.path.join(os.path.dirname(__file__), "policy.yaml")
    _listeners = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PolicyEnforcer, cls).__new__(cls)
            cls._instance._load_policy()
            # Register the God Eye
            sys.addaudithook(cls._instance._audit_hook)
        return cls._instance

    def _load_policy(self):
        try:
            with open(self._policy_path, "r") as f:
                self._policy = yaml.safe_load(f)
                print(f"[ENFORCER] Policy v{self._policy.get('version')} Loaded.")
        except Exception as e:
            print(f"[ENFORCER] (FAIL) Failed to load policy: {e}")
            self._policy = {"permissions": {"file_system": {"deny": [{"path": "*", "ops": ["ALL"]}]}}}

    def add_listener(self, callback):
        """Register a callback to receive live audit events."""
        self._listeners.append(callback)

    def _broadcast(self, event_type, target, status, details=""):
        """Send event to all listeners (e.g., WebSockets)."""
        event = {
            "id": str(datetime.datetime.now().timestamp()),
            "type": event_type,
            "target": str(target),
            "status": status,
            "time": datetime.datetime.now().strftime("%H:%M:%S"),
            "details": details,
        }
        for listener in self._listeners:
            try:
                listener(event)
            except Exception:
                pass  # Don't let listener crash the kernel

    def _audit_hook(self, event: str, args: tuple):
        """
        PEP 578 Audit Hook. Intercepts low-level interpreter events.
        """
        try:
            if event == "open":
                path = args[0]
                if isinstance(path, str):
                    # Filter out noise (reading own source code, pycache)
                    if "__pycache__" in path or path.endswith(".py") or "node_modules" in path:
                        return

                    # Check Logic (Monitor Mode - We log but don't abort yet to avoid crashes)
                    # Real enforcement happens in explicit check_permission calls for now
                    self._broadcast("FS_ACCESS", path, "MONITORED")

            elif event == "socket.connect":
                addr = args[1] if len(args) > 1 else args[0]
                if isinstance(addr, (tuple, list)) and len(addr) >= 2:
                    host, port = addr[0], addr[1]
                    self._broadcast("NET_EGRESS", f"{host}:{port}", "MONITORED")

            elif event == "subprocess.Popen":
                cmd = args[0]
                self._broadcast("EXEC_PROCESS", str(cmd), "MONITORED")

        except Exception as e:
            # Audit hooks must never fail, or they crash the process
            print(f"[AUDIT ERROR] {e}")

    def check_permission(self, agent_id: str, resource_type: str, action: str, target: str) -> bool:
        """
        Validates an action against the loaded policy.
        """
        perms = self._policy.get("permissions", {}).get(resource_type, {})

        # Check DENY
        for rule in perms.get("deny", []):
            if self._matches(target, rule["path"]) and (action in rule["ops"] or "ALL" in rule["ops"]):
                self._broadcast(f"{action}_BLOCKED", target, "BLOCKED", "Explicit Deny Rule")
                raise SecurityException(f"ACCESS DENIED: {action} on {target} is explicitly forbidden.")

        # Check ALLOW
        allowed = False
        for rule in perms.get("allow", []):
            if self._matches(target, rule["path"]) and (action in rule["ops"] or "ALL" in rule["ops"]):
                allowed = True
                break

        if not allowed:
            self._broadcast(f"{action}_DENIED", target, "BLOCKED", "Implicit Deny")
            raise SecurityException(f"ACCESS DENIED: {action} on {target} is not explicitly allowed.")

        self._broadcast(f"{action}_ALLOWED", target, "ALLOWED")
        return True

    def _matches(self, target: str, pattern: str) -> bool:
        """Simple glob matching for paths."""
        target = target.replace("\\", "/")
        pattern = pattern.replace("\\", "/")
        try:
            regex = "^" + re.escape(pattern).replace("\\*", ".*") + "$"
            flags = re.IGNORECASE if os.name == "nt" else 0
            return bool(re.match(regex, target, flags=flags))
        except:
            return False


# Singleton accessor
enforcer = PolicyEnforcer()