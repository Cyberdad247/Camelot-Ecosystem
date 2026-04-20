# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Cartridge Sandbox (Node 3.5)

Provides an isolated execution environment for agent cartridges.
Enforces resource budgets, tool whitelisting, and governance policies.
"""

import os
import time
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

from .cartridge_schemas import CartridgeManifest, GovernancePolicy, ResourceBudget

@dataclass
class SandboxSession:
    """State of a single cartridge execution session."""
    cartridge_id: str
    start_time: float = field(default_factory=time.time)
    token_usage: int = 0
    memory_peak_mb: float = 0.0
    calls_made: int = 0
    logs: List[str] = field(default_factory=list)

class CartridgeSandbox:
    """
    Control layer for secure cartridge execution.
    Acts as the 'Iron Gate' at the tool-execution level.
    """
    
    def __init__(self):
        self.active_sessions: Dict[str, SandboxSession] = {}
        print("[Sandbox] Isolation Layer Online")

    def run_cartridge_tool(self, manifest: CartridgeManifest, tool_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool from a cartridge within the sandbox environment.
        Validates against whitelists and enforces resource budgets.
        """
        session_id = f"sess_{manifest.cartridge_id}_{int(time.time())}"
        session = SandboxSession(cartridge_id=manifest.cartridge_id)
        self.active_sessions[session_id] = session
        
        try:
            # 1. Governance Check: Tool Whitelist
            if not self._check_governance(manifest.governance, tool_id):
                error_msg = f"Security Violation: Tool '{tool_id}' is not whitelisted for cartridge '{manifest.cartridge_id}'"
                session.logs.append(error_msg)
                return {"status": "error", "error": error_msg}

            # 2. Resource Check: Token Budget (Pre-check estimate)
            if session.token_usage >= manifest.resource_budget.max_tokens:
                return {"status": "error", "error": "Resource Exhausted: Token budget exceeded"}

            # 3. Execution (Simulated Kinetic Execution)
            print(f"[Sandbox] Executing {tool_id} for {manifest.cartridge_id}...")
            result = self._execute_kinetic_tool(tool_id, params)
            
            # 4. Telemetry Update
            session.calls_made += 1
            session.token_usage += result.get("token_cost", 100) # Mock cost
            session.memory_peak_mb = max(session.memory_peak_mb, 25.5) # Mock peak
            
            # 5. Latency Check
            latency = (time.time() - session.start_time) * 1000
            if latency > manifest.resource_budget.max_latency_ms:
                 session.logs.append(f"Performance Warning: Latency {latency:.2f}ms exceeds budget {manifest.resource_budget.max_latency_ms}ms")

            return {
                "status": "success",
                "result": result.get("data"),
                "telemetry": {
                    "tokens": session.token_usage,
                    "latency_ms": latency,
                    "memory_mb": session.memory_peak_mb
                }
            }

        except Exception as e:
            session.logs.append(f"Execution Failure: {str(e)}")
            return {"status": "error", "error": str(e)}

    def _check_governance(self, policy: GovernancePolicy, tool_id: str) -> bool:
        """Verify tool usage against governance policy."""
        # Handle wildcard whitelist
        if "*" in policy.allowed_tools:
            return True
            
        return tool_id in policy.allowed_tools

    def _execute_kinetic_tool(self, tool_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal dispatcher to the Kinetic Stack (Saltare/Cribo).
        In production, this calls local binaries or JIT adapters.
        """
        # Add tiny delay for budget testing
        time.sleep(0.005)
        # Mock execution for Node 3.5 implementation
        return {
            "token_cost": 250,
            "data": f"Executed {tool_id} with params {json.dumps(params)}"
        }

    def get_session_report(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve telemetry and logs for a specific sandbox session."""
        if session_id not in self.active_sessions:
            return None
        return asdict(self.active_sessions[session_id])

if __name__ == "__main__":
    # Test Sandbox
    from .cartridge_schemas import CartridgeManifest
    
    sb = CartridgeSandbox()
    
    # Mock Manifest with strict policy
    mock_manifest = CartridgeManifest(
        cartridge_id="RESTRICTED_CORE",
        description="Test restricted cartridge",
        signature="sha256:test",
        governance=GovernancePolicy(allowed_tools=["CodeGen"]),
        resource_budget=ResourceBudget(max_latency_ms=10)
    )
    
    # Case 1: Valid tool
    res1 = sb.run_cartridge_tool(mock_manifest, "CodeGen", {"code": "print('hello')"})
    print(f"Valid Tool Result: {res1['status']}")
    
    # Case 2: Blocked tool
    res2 = sb.run_cartridge_tool(mock_manifest, "NetworkStrike", {})
    print(f"Blocked Tool Result: {res2['error']}")