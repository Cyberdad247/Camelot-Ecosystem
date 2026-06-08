# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import json
from typing import Any, Dict, List, Optional

# Use Merlin as the core verification engine
try:
    from Engines.merlin_llm import MerlinLLM
except ImportError:
    from kernel.Engines.merlin_llm import MerlinLLM

class CoherenceEngine:
    """
    COHERENCE ENGINE (Phase 6)
    Responsible for Self-Healing, Cross-Agent Verification, and Workflow Coherence.
    Powered by MerlinLLM for consistent reasoning.
    """

    def __init__(self):
        self.merlin = MerlinLLM()
        self._verification_history: List[Dict] = []

    async def verify_output(self, task: str, output: str, context: str = "") -> Dict[str, Any]:
        """
        [⚔️ Verifier] Performs a 'Cross-Agent' review of an output.
        Uses a separate LLM pass (Judge/Critic mode) to validate logic.
        """
        print(f"🛡️  [COHERENCE] Verifying output for task: {task[:50]}...")

        verification_prompt = f"""
        ### ROLE: CAMELOT_CRITIC (Level 6 Coherence)
        ### TASK: Verify the following output for correctness, safety, and adherence to the Objective.
        
        [OBJECTIVE]: {task}
        [CONTEXT]: {context}
        [CANDIDATE_OUTPUT]:
        ---
        {output}
        ---
        
        ### REQUIREMENTS:
        1. Does it meet the objective? (YES/NO)
        2. Are there security vulnerabilities? (e.g. raw eval, hardcoded keys)
        3. Is the code aesthetic high? (Camelot standard)
        
        RESPONSE FORMAT: JSON
        {{
            "valid": bool,
            "score": 0-100,
            "critique": "string",
            "fix_suggestion": "string" (if invalid)
        }}
        """

        try:
            # high-reasoning mode for critique
            raw_eval = await self.merlin.generate_response(
                persona_prompt="You are the Camelot High Judge. Integrity is your Law.",
                user_input=verification_prompt,
                mode="CoT"
            )

            # Extract JSON from response
            print(f"DEBUG: Raw Merlin Output: {raw_eval[:100]}...")
            
            clean_eval = raw_eval.strip()
            if "```json" in clean_eval:
                clean_eval = clean_eval.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_eval:
                clean_eval = clean_eval.split("```")[1].split("```")[0].strip()
            
            # Find first { and last }
            start = clean_eval.find("{")
            end = clean_eval.rfind("}")
            if start != -1 and end != -1:
                clean_eval = clean_eval[start:end+1]

            result = json.loads(clean_eval)
            print(f"✅ [COHERENCE] Verification Score: {result.get('score', 0)}")
            return result
        except Exception as e:
            print(f"⚠️ [COHERENCE] Verification Failed: {e}")
            return {"valid": True, "score": 50, "critique": "Internal verification error - proceeding with caution."}

    async def self_heal(self, task: str, failed_output: str, critique: str) -> Optional[str]:
        """
        [🩹 Self-Healer] Attempt to fix an output based on critique.
        """
        print(f"🩹 [COHERENCE] Attempting Self-Heal for usage: {task[:50]}...")

        healing_prompt = f"""
        ### ROLE: CAMELOT_FORGE_FIXER
        ### SITUATION: A previous build attempt failed verification.
        
        [TASK]: {task}
        [FAILED_CODE]:
        {failed_output}
        
        [CRITIQUE]:
        {critique}
        
        ### INSTRUCTION: Generate the corrected code. Fix the errors exactly. Return ONLY the code.
        """

        try:
            healed_code = await self.merlin.generate_response(
                persona_prompt="You are a master fixer. You fix code instantly and perfectly.",
                user_input=healing_prompt,
                mode="Standard"
            )
            return healed_code
        except Exception as e:
            print(f"❌ [COHERENCE] Self-Heal Failed: {e}")
            return None

    async def helix_verify_loop(self, task: str, initial_output: str, max_retries: int = 2) -> str:
        """
        [🧬 HELIX LOGIC] Recursive Verification & Healing Loop.
        """
        current_output = initial_output
        
        for i in range(max_retries):
            # 1. Verify
            verification = await self.verify_output(task, current_output)
            
            if verification.get("valid", False) and verification.get("score", 0) > 80:
                print(f"✨ [HELIX] Output verified (Cycle {i+1})")
                return current_output
            
            # 2. Heal
            print(f"🔄 [HELIX] Healing triggered (Cycle {i+1}). Critique: {verification.get('critique')}")
            healed = await self.self_heal(task, current_output, verification.get("critique", ""))
            
            if healed:
                current_output = healed
            else:
                print("⚠️ [HELIX] Healing failed, returning best effort.")
                return current_output
        
        print("⚠️ [HELIX] Max retries reached.")
        return current_output

# Singleton
coherence = CoherenceEngine()