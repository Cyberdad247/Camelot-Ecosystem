# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
MCP_ADAPTER_v1.0
The Unified API Gateway and Multi-Adapter MCP Interface.
Enables dynamic tool discovery and secure external API consumption.
"""

from typing import Any, Dict, List, Optional

import httpx


class MCPAdapter:
    """
    The Multi-Adapter MCP Interface for Agno.
    Wraps external APIs into a uniform interface for personas.
    """
    
    def __init__(self):
        self.registry: Dict[str, Dict[str, Any]] = {}
        self.client = httpx.AsyncClient(timeout=30.0)
        self._load_internal_tools()

    def _load_internal_tools(self):
        """Registers built-in Camelot tools."""
        self.register_adapter(
            name="UKG_Query",
            description="Query the Universal Knowledge Graph.",
            endpoint="local://ukg/query",
            capability="semantic_search"
        )
        self.register_adapter(
            name="Kinetic_Exec",
            description="Execute Rust/Go binaries locally.",
            endpoint="local://kinetic/execute",
            capability="binary_execution"
        )

    def register_adapter(self, name: str, description: str, endpoint: str, capability: str, params_schema: Optional[Dict] = None):
        """
        [DYNAMIC_DISCOVERY] Registers a new API Adapter to the registry.
        """
        self.registry[name] = {
            "name": name,
            "description": description,
            "endpoint": endpoint,
            "capability": capability,
            "params": params_schema or {},
            "status": "ONLINE"
        }
        print(f"🔌 [MCP_ADAPTER]: Registered {name} ({capability})")

    async def call(self, adapter_name: str, payload: Dict[str, Any], hitl_approved: bool = False, requestor: str = "unknown") -> Dict[str, Any]:
        """
        [UNIFIED_GATEWAY] Routes requests to the correct adapter.
        Includes HITL and safety checks with standardized return.
        """
        if adapter_name not in self.registry:
            return {"status": "ERROR", "message": f"Adapter '{adapter_name}' not found."}
            
        adapter = self.registry[adapter_name]
        
        # [HITL_GATE] Enhanced logic for pending approvals
        is_external = "external" in adapter["endpoint"] or adapter["endpoint"].startswith("https")
        if not hitl_approved and is_external:
            return {
                "status": "PENDING_APPROVAL",
                "message": f"HITL_REQUIRED: {adapter_name} call by {requestor} requires manual approval.",
                "preview": self._generate_preview(adapter_name, payload),
                "adapter": adapter_name,
                "payload": payload
            }

        try:
            # Handle local vs external routing
            if adapter["endpoint"].startswith("local://"):
                result = await self._execute_internal(adapter["endpoint"], payload)
                return {"status": "SUCCESS", "data": result}
            else:
                response = await self.client.post(adapter["endpoint"], json=payload)
                return {"status": "SUCCESS", "data": response.json()}
        except Exception as e:
            return {"status": "ERROR", "message": f"ADAPTER_FAILURE on {adapter_name}: {str(e)}"}

    def _generate_preview(self, adapter_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generates a human-readable preview of the requested action."""
        return {
            "title": f"External API Call: {adapter_name}",
            "summary": f"Requesting {adapter_name} with parameters: {list(payload.keys())}",
            "risk_level": "MODERATE" if "external" in adapter_name.lower() else "LOW",
            "payload_snapshot": payload
        }

    async def _execute_internal(self, uri: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Executes internal system logic."""
        # Simulated internal execution for now
        return {"status": "SUCCESS", "result": f"Internal execution of {uri} completed.", "data": payload}

    def list_tools(self) -> List[Dict[str, Any]]:
        """Returns all registered tools for persona tool-discovery."""
        return list(self.registry.values())

if __name__ == "__main__":
    import asyncio
    
    async def test_mcp_adapter():
        adapter = MCPAdapter()
        # Register a mock external API
        adapter.register_adapter(
            name="WolframAlpha",
            description="Compute mathematical queries.",
            endpoint="https://api.wolframalpha.com/v1/result",
            capability="math_engine"
        )
        
        print("\n--- TOOL DISCOVERY ---")
        for tool in adapter.list_tools():
            print(f"- {tool['name']}: {tool['description']}")
            
        print("\n--- TEST CALL (Internal) ---")
        res = await adapter.call("UKG_Query", {"query": "What is Camelot?"})
        print(res)
        
        print("\n--- TEST CALL (External - No HITL) ---")
        res = await adapter.call("WolframAlpha", {"q": "integrate x^2"})
        print(res)

    asyncio.run(test_mcp_adapter())