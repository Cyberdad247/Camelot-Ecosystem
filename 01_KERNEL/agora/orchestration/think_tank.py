# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import sys
import os
from pathlib import Path

# Add 01_KERNEL to sys.path
kernel_path = Path(__file__).parent.parent
if str(kernel_path) not in sys.path:
    sys.path.insert(0, str(kernel_path))

import asyncio
import json
from typing import Dict, Any, List
from Engines.ukg_runtime import UKGRuntime
from Engines.merlin_llm import MerlinLLM
from Engines.mcp_adapter import MCPAdapter
from swarm_controller import swarm
from assimilation.core.verification import check_harmony

class ThinkTankOrchestrator:
    """
    AGNO_FORGE v3.0 [SINGULARITY]: The Versatile Think Tank Orchestrator.
    Orchestrates LLMs, APIs, and MCP tools with dynamic assignment.
    """

    def __init__(self):
        self.ukg = UKGRuntime()
        self.merlin = MerlinLLM()
        self.mcp = MCPAdapter()
        self.session_log = "03_VAULT/99_HISTORY/AGNO_SESSION_LOG.md"
        os.makedirs(os.path.dirname(self.session_log), exist_ok=True)

    async def execute_session(self, objective: str, repo_path: str, priority: str = "medium") -> Dict[str, Any]:
        """
        [UNIFIED_ORCHESTRATION] Executes the 5-Panel Debate with Resource-Optimized Reasoning.
        """
        session_id = f"AGNO_{os.urandom(4).hex().upper()}"
        print(f"🧠 [AGNO] Initializing v3.2 Session {session_id} for: {objective}")
        
        # [RESOURCE_CHECK] Simulated 8GB RAM Constraint Gate
        low_resource_mode = priority == "low"
        print(f"⚖️ [RESOURCE_GATE] Low-Resource Mode: {low_resource_mode}")

        # 1. Select Planning Model (Dynamic Assignment)
        planning_model = self.merlin.select_model(f"PLANNING: {objective}", priority, low_resource=low_resource_mode)
        
        # Load Lukas for Strategic Planning
        lukas_manifest = self.merlin.load_persona("lukas")
        lukas_prompt = self.merlin.render_persona_prompt(lukas_manifest) if lukas_manifest else "You are Lukas, the Planner."

        results = {
            "session_id": session_id, 
            "objective": objective,
            "orchestrator_config": {
                "model": planning_model, 
                "priority": priority,
                "low_resource": low_resource_mode
            }
        }

        # PHASE 1: STRATEGIC PLANNING & ARCHITECTURE (Lukas Müller)
        print(f"💻 [PHASE 1] Lukas Architecting Strategy via {planning_model}...")
        results["architect_plan"] = await self.merlin.generate_response(
            persona_prompt=lukas_prompt,
            user_input=f"ARCHITECT: {objective}",
            mode="Standard",
            model=planning_model
        )
        
        # PHASE 2: PERSONA ASSEMBLY (Merlin Forge)
        print(f"🧙‍♂️ [PHASE 2] Merlin Forging 5-Panel Experts...")
        expert_ids = ["sec_expert", "lukas", "merlin"] # Core personas
        
        # Hydrate full prompts for debate
        experts_manifests = []
        for eid in expert_ids:
            manifest = self.merlin.load_persona(eid)
            if manifest:
                manifest["rendered_prompt"] = self.merlin.render_persona_prompt(manifest)
                experts_manifests.append(manifest)
        
        results["experts"] = [m["name"] for m in experts_manifests]
        
        # PHASE 3: THE DEBATE (Resource-Optimized Specialized Reasoning)
        print(f"📖 [PHASE 3] Agno Coordinating 5-Panel Debate...")
        debate_model = self.merlin.select_model("REASONING: deep debate", priority, low_resource=low_resource_mode)
        
        # [DYNAMIC_DISCOVERY] Capture live API capabilities
        tools = self.mcp.list_tools()
        tools_desc = "\n".join([f"- {t['name']}: {t['description']}" for t in tools])
        
        # Prepare debate context with expert identities
        experts_info = "\n".join([f"### {m['name']} ({m['role']})\n{m['core_identity']['summary']}" for m in experts_manifests])
        
        debate_mode = "Compressed" if low_resource_mode else "CoT"
        debate_context = f"Expert Panel:\n{experts_info}\n\nAvailable Tools:\n{tools_desc}\n\nObjective: {objective}"
        
        debate_summary = await self.merlin.generate_response(
            persona_prompt="You are Agno, the High Orchestrator of Camelot. Synthesize a 5-expert debate based on the provided panel.",
            user_input=debate_context,
            mode=debate_mode,
            model=debate_model
        )
        results["debate_summary"] = debate_summary

        # PHASE 4: KINETIC EXECUTION (MCP Tool Usage & Distilled Execution)
        print(f"🔨 [PHASE 4] MCP Kinetic Execution Ignition...")
        # Check if debate requires external tools
        if "external" in debate_summary.lower():
            # Standard search if required
            search_res = await self.mcp.call("UKG_Query", {"query": objective}, hitl_approved=True)
            results["tool_interaction"] = search_res

        swarm_phases = ["build", "audit", "lint"]
        results["kinetic_result"] = await swarm.execute_crusade(objective, swarm_phases)

        # PHASE 5: HARMONY GATE
        print(f"👑 [PHASE 5] Harmony Gate Verification...")
        # Final safety check on results using the standard AssimilationRequest model
        from assimilation.core.types import AssimilationRequest
        harmony_req = AssimilationRequest(repo_path=repo_path, origin="local", description=f"Verification for {objective}")
        results["harmony"] = check_harmony(harmony_req)
        
        self._log_agno_session(results)
        return results

    def _log_agno_session(self, results: Dict[str, Any]):
        with open(self.session_log, "a", encoding="utf-8") as f:
            f.write(f"\n# 🧠 AGNO SESSION v3.1: {results['session_id']}\n")
            f.write(f"- **Objective:** {results['objective']}\n")
            f.write(f"- **Models Used:** {results['orchestrator_config']['model']} (Low-Res: {results['orchestrator_config']['low_resource']})\n")
            f.write(f"- **Experts Assembly:** {', '.join(results['experts'])}\n")
            f.write(f"- **External API Interaction:** {results.get('external_data', 'NONE')}\n")
            f.write(f"- **Kinetic Status:** {results['kinetic_result'].get('status', 'SIMULATED')}\n")
            f.write(f"- **Harmony Status:** {results['harmony'].get('status', 'PENDING')}\n")
            f.write("---\n")

async def test_agno_orchestrator():
    agno = ThinkTankOrchestrator()
    res = await agno.execute_session("Develop a secure multi-API adapter for WolframAlpha and Google Search.", "C:/Users/vizio/CAMELOT_OS", priority="high")
    print("\n🚀 [AGNO] Versatile Session Complete.")

if __name__ == "__main__":
    asyncio.run(test_agno_orchestrator())