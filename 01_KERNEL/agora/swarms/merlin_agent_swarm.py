# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
merlin_agent_swarm.py

Phase 4: The Integrated Agentic Swarm.
- Uses Merlin (L3) for reasoning.
- uses SwarmTools (L2) for kinetic action.
- Uses ReflectionEngine (L3) for self-correction.

This is the Python implementation of the "Titan Protocol" before it moves to Go/Rust (Phase 5).
"""

import sys
import os
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional

# Add KERNEL to path for telemetry import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
try:
    from senses.telemetry_client import RotelClient
    telemetry = RotelClient("merlin_swarm")
except ImportError:
    class DummyLogger:
        def info(self, *args, **kwargs): pass
    telemetry = DummyLogger()

# Path setup for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
kernel_dir = os.path.dirname(current_dir)
sys.path.append(kernel_dir)

from Engines.merlin_llm import MerlinLLM
from tools.swarm_tools_v2 import SwarmTools
from rag.recursive_search import ReflectionEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MerlinSwarm")

class MerlinSwarmAgent:
    """
    Autonomous Agent capable of reasoning, tool use, and reflection.
    """
    def __init__(self, persona: str = "Standard"):
        self.merlin = MerlinLLM()
        self.tools = SwarmTools.get_definitions()
        self.reflector = ReflectionEngine()
        self.persona = persona
        self.max_steps = 5

    async def solve_task(self, task: str) -> str:
        """
        Execute the OODA Loop (Observe, Orient, Decide, Act).
        """
        telemetry.info("SWARM_TASK_RECEIVED", task=task[:100])
        logger.info(f"⚔️ [SWARM] Task Received: {task}")
        
        history = [
            {"role": "system", "content": f"You are Merlin. You have tools. Use them to solve: {task}"},
            {"role": "user", "content": task}
        ]

        for step in range(self.max_steps):
            logger.info(f"🔄 Step {step+1}/{self.max_steps}")
            
            # 1. DECIDE (LLM Call)
            response = await self.merlin.generate_response(
                persona_prompt=history[0]["content"],
                user_input=history[-1]["content"] if step > 0 else task,
                mode=self.persona,
                tools=self.tools,
                tool_choice="auto"
            )

            # 2. ACT (Tool Execution)
            if isinstance(response, list): # It's a tool call list
                tool_outputs = []
                for tool_call in response:
                    func_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    
                    # Execute
                    result = SwarmTools.execute_tool(func_name, args)
                    tool_outputs.append(f"Tool {func_name} output: {result}")
                    
                    # Append strictly to history (simulated)
                    history.append({
                        "role": "function",
                        "name": func_name,
                        "content": result
                    })
                
                # If we acted, loop back to let LLM see results
                continue
            
            else:
                # Text response (Final Answer or Reasoning)
                logger.info(f"🧠 Merlin says: {response}")
                
                # 3. REFLECT (Critique)
                # If response seems short or uncertain, verify
                if "I don't know" in response or len(response) < 50:
                    critique = self.reflector.evaluate_coverage(task, [{"content": response}])
                    if critique.get("needs_recursion"):
                         logger.info("🤔 Reflection triggered recursion...")
                         history.append({"role": "user", "content": f"Critique: {critique['missing']}. Please check UKG."})
                         continue

                # Phase 6: Coherence Verification (Helix Logic)
                final_res = await self._verify_and_return(task, response, str(history))
                telemetry.info("SWARM_TASK_COMPLETE", status="SUCCESS")
                return final_res

        telemetry.info("SWARM_TASK_TIMEOUT", status="MAX_STEPS")
        return "Max steps reached without structured conclusion."

    async def _verify_and_return(self, task: str, candidate: str, context: str) -> str:
        """
        [Phase 6] Invokes Coherence Engine to verify and heal output.
        """
        print("🛡️  [SWARM] Phase 6: Verifying solution with Coherence Engine...")
        
        # Lazy import to avoid circular dependency
        try:
            from Engines.coherence_engine import coherence
        except ImportError:
            from kernel.Engines.coherence_engine import coherence
        
        # Verify
        verification = await coherence.verify_output(task, candidate, context=context)
        
        if verification.get("valid", False):
            print(f"✅ [SWARM] Solution Verified (Score: {verification.get('score')})")
            return candidate
        else:
            print(f"⚠️ [SWARM] Solution failed verification. Triggering Helix Repair...")
            # Trigger Helix Loop
            healed = await coherence.helix_verify_loop(task, candidate)
            return healed

# --- CLI for Testing ---
import argparse

# --- CLI for Testing ---
if __name__ == "__main__":
    async def main():
        parser = argparse.ArgumentParser(description="Merlin Swarm Agent")
        parser.add_argument("--task", type=str, help="Task to execute")
        parser.add_argument("--persona", type=str, default="CoT", help="Persona mode")
        args = parser.parse_args()

        agent = MerlinSwarmAgent(persona=args.persona)
        
        if args.task:
             # Production Mode
             res = await agent.solve_task(args.task)
             print(res)
        else:
            # Test Mode
            print("--- PHASE 4 SWARM TEST ---")
            res = await agent.solve_task("What is the Septem Regna?")
            print(f"\nResult 1: {res}\n")

    asyncio.run(main())