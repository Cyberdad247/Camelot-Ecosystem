# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
PERSONA_TEST_HARNESS_v1.0
Simulates and scores multi-expert debates for objective validation.
"""

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List

from Engines.merlin_llm import MerlinLLM
from Engines.ukg_runtime import UKGRuntime


class PersonaTestHarness:
    """
    Runs multiple ToT (Tree-of-Thought) branches using different experts
    and scores their responses against the Sovereign Law.
    """

    def __init__(self):
        self.merlin_llm = MerlinLLM()
        self.ukg = UKGRuntime()
        self.test_reports = Path("03_VAULT/99_HISTORY/TEST_REPORTS")
        os.makedirs(self.test_reports, exist_ok=True)

    async def run_simulation(self, objective: str, experts: List[str]) -> Dict[str, Any]:
        """
        Runs a simulated debate where each expert provides their 'Strike'.
        """
        print(f"🔬 [HARNESS] Starting Simulation for: {objective}")
        branches = []

        for expert_role in experts:
            # 1. Forge/Load Persona TAL
            tal = self.ukg.execute(expert_role, mode="LOWER")["tal_manifest"]

            # 2. Generate System Prompt
            system_prompt = self.merlin_llm.generate_system_prompt(tal)

            # 3. Simulate Response
            print(f"  - Branch: {expert_role} is thinking...")
            response = await self.merlin_llm.generate_response(system_prompt, objective)

            # 4. Score Response (Simulated scoring against laws)
            score = self._score_response(response, tal)

            branches.append({"expert": expert_role, "response": response, "score": score, "tal": tal})

        # 5. Determine Winner (Highest Score)
        winner = max(branches, key=lambda x: x["score"])

        report = {
            "objective": objective,
            "branches": branches,
            "winner": winner["expert"],
            "consensus_score": sum(b["score"] for b in branches) / len(branches),
        }

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._save_report, report)
        return report

    def _score_response(self, response: str, tal: Dict[str, Any]) -> float:
        """
        [⚖️] Evaluates response quality.
        In a real scenario, this would check for keywords, logic consistency,
        and adherence to the Titanium Laws.
        """
        score = 0.5  # Baseline

        # Keyword-based heuristics
        keywords = ["kinetic", "sovereign", "purity", "security", "optimize", "rust", "go"]
        for kw in keywords:
            if kw in response.lower():
                score += 0.05

        # Symbol adherence
        if tal["branch"]["symbols"] in response:
            score += 0.1

        # Error check
        if "❌" in response or "ERROR" in response:
            score = 0.1

        return min(1.0, score)

    def _save_report(self, report: Dict[str, Any]):
        Path("03_VAULT/99_HISTORY/last_test_run.txt")
        # Save detailed JSON report
        report_id = os.urandom(4).hex().upper()
        file_path = self.test_reports / f"PROMPT_WAR_{report_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)


if __name__ == "__main__":
    import os

    async def test_harness():
        harness = PersonaTestHarness()
        objective = "Implement a secure MCP handshake protocol using Ed25519."
        experts = ["System_Engineer", "Security_Auditor", "Lukas_Müller"]

        report = await harness.run_simulation(objective, experts)
        print("\n--- SIMULATION COMPLETE ---")
        print(f"Winner: {report['winner']}")
        print(f"Consensus Score: {report['consensus_score']:.2f}")

    asyncio.run(test_harness())
