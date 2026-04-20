# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
AETHER Engine: Saltare MCP Gateway Client
Handles semantic routing of natural language queries to MCP tools.
"""

import json
import os
from typing import Any, Dict

import toml


class AetherEngine:
    """
    AETHER Connectivity Engine
    Routes natural language intent to the correct Model Context Protocol tool.
    """

    def __init__(
        self,
        config_path: str = "01_KERNEL/config/saltare.toml",
        registry_path: str = "01_KERNEL/config/mcp_registry.json",
    ):
        # Resolve absolute paths based on CWD
        base_dir = os.getcwd()
        if not os.path.exists(config_path):
            # Try to find it if running from inside a subdir
            if os.path.exists(os.path.join("..", config_path)):
                config_path = os.path.join("..", config_path)
                registry_path = os.path.join("..", registry_path)

        self.config = toml.load(config_path)
        with open(registry_path, "r") as f:
            self.registry = json.load(f)

        self.primary_provider = self.config["llm"]["primary"]["provider"]
        self.active_tools = {}
        self._initialize_tools()

    def _initialize_tools(self):
        """Pre-load tool definitions for routing context"""
        print(f"[AETHER] Initializing {len(self.registry['mcp_tools'])} MCP tools...")
        for tool in self.registry["mcp_tools"]:
            self.active_tools[tool["id"]] = {"keywords": tool["keywords"], "description": tool["description"]}

    def route_query(self, query: str) -> Dict[str, Any]:
        """
        Semantically route a query to the best tool or gateway.
        """
        best_tool = None
        max_score = 0

        query_terms = set(query.lower().split())

        # Check for Clawdbot/Multichannel Keywords
        multichannel_keywords = {"whatsapp", "telegram", "slack", "discord", "signal", "imessage", "message", "channel"}
        if any(kw in query_terms for kw in multichannel_keywords):
            return {"target_type": "gateway", "id": "gateway::clawdbot", "confidence": 0.95, "status": "ROUTED"}

        # Check for ClaraVerse Keywords (Workflows, CRM, Data Analyst)
        clara_keywords = {
            "workflow",
            "crm",
            "hubspot",
            "salesforce",
            "notion",
            "airtable",
            "dag",
            "block",
            "lead",
            "pipeline",
        }
        if any(kw in query_terms for kw in clara_keywords):
            return {"target_type": "gateway", "id": "gateway::claraverse", "confidence": 0.90, "status": "ROUTED"}

        for tool_id, meta in self.active_tools.items():
            score = 0
            # Keyword matching
            for kw in meta["keywords"]:
                if kw in query_terms:
                    score += 10

            # Semantic proximity (mock)
            if tool_id == "github-mcp" and "repo" in query:
                score += 50
            if tool_id == "filesystem-mcp" and "file" in query:
                score += 50
            if tool_id == "brave-search-mcp" and ("search" in query or "find" in query):
                score += 40

            if score > max_score:
                max_score = score
                best_tool = tool_id

        if max_score > 0:
            return {"target_type": "tool", "id": best_tool, "confidence": max_score / 100.0, "status": "ROUTED"}
        else:
            return {
                "target_type": "tool",
                "id": self.config["routing"]["default_tool"],
                "confidence": 0.0,
                "status": "FALLBACK",
            }

    def execute_tool(self, tool_id: str, payload: Dict[str, Any]) -> str:
        """
        Execute an MCP tool command via stdio transport.
        Placeholder for actual MCP client protocol implementation.
        """
        tool_def = next((t for t in self.registry["mcp_tools"] if t["id"] == tool_id), None)
        if not tool_def:
            return f"Error: Tool {tool_id} not found."

        print(f"[AETHER] Executing {tool_id} via {tool_def['transport']}...")
        # In a real implementation, this would spawn the process and communicate via JSON-RPC
        return f"Simulated execution of {tool_id} with {payload}"


if __name__ == "__main__":
    # Test AETHER routing
    aether = AetherEngine()

    test_queries = [
        "Find the latest PRs in the atomic-agents repo",
        "Read the config file from local disk",
        "Search Google for LangGraph tutorials",
    ]

    print("\n" + "=" * 50)
    print("AETHER SEMANTIC ROUTING TEST")
    print("=" * 50)

    for q in test_queries:
        route = aether.route_query(q)
        print(f"Query: '{q}'")
        print(f"  → Routed to: {route['tool_id']} (Conf: {route['confidence']:.2f})")


def call_kernel_ws(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    TitanLink Kernel Bridge: Broadcasts a message to all connected Anya Lyte clients.
    """
    print(f"[AETHER] Broadcasting to TitanLink: {message.get('kind')}")
    # In production, this would use a global websocket manager or queue to push to the server
    return {"status": "BROADCAST_QUEUED", "kind": message.get("kind")}


def request_kinetic_approval(action: Dict[str, Any]) -> Dict[str, Any]:
    """
    Trigger an Iron Gate approval request to the mobile device.
    Used for ACTIONS tagged with HIGH risk.
    """
    from security.iron_gate import iron_gate

    action_id = iron_gate.request_approval(action)

    # Send to mobile via TitanLink
    approval_request = {
        "kind": "approval_request",
        "action": {"id": action_id, **action},
        "ttlSeconds": action.get("ttlSeconds", 60),
    }

    call_kernel_ws(approval_request)

    return {"status": "AWAITING_BIOMETRICS", "actionId": action_id}


def call_clawdbot_gateway(message: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Bridge function to communicate with Clawdbot Gateway over HTTP/WebSocket.
    """
    import asyncio

    from connectivity.bridges.clawdbot_client import get_clawdbot_client

    print(f"[AETHER] Bridging to Clawdbot Gateway: {message.get('text', 'Binary Payload')[:20]}...")

    client = asyncio.run(get_clawdbot_client())

    # Extract channel from message metadata if available
    channel = message.get("metadata", {}).get("channel", "webchat")
    text = message.get("text", "")

    # Since Aether is often called from sync contexts, we use run_until_complete or similar
    # In TitanLink, it's called in a thread or task, so we must be careful with loops.
    try:
        res = asyncio.run(client.send_message(text, channel))
        return res
    except Exception as e:
        return {"status": "ERROR", "gateway": "gateway::clawdbot", "message": str(e)}


def call_claraverse_gateway(message: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Bridge function to communicate with ClaraVerse sidecar over HTTP.
    """
    import uuid

    print(f"[AETHER] Bridging to ClaraVerse Sidecar: {message.get('text', 'Binary Payload')[:20]}...")

    # Simulating a ClaraVerse Block-DAG execution result
    return {
        "status": "FORWARDED",
        "gateway": "gateway::claraverse",
        "job_id": str(uuid.uuid4()),
        "workflow": "Clara::Adaptive_CRM_Sync",
        "response": "Workflow initiated in ClaraVerse Sidecar.",
    }