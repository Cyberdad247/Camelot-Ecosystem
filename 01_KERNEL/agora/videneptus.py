# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
from .node import AgentNode
from .protocol import ANPEnvelope
from .router import AgoraRouter
import json
from kernel.Engines.prism_gateway import PrismAdapter
from kernel.Engines.coherence_engine import coherence


class Videneptus(AgentNode):
    """
    VIDENEPTUS PRIME: The Semantic Router Node.
    Assimilated from WilmerAI's 'CategorizationNode'.

    Responsibility:
    1. Analyze the SovereignContext.
    2. Classify Intent (PLAN, CODE, AUDIT, EXECUTE).
    3. Route to the appropriate Specialist Knight.
    """

    def __init__(self):
        super().__init__("VIDENEPTUS")
        self.router = AgoraRouter()

        # Register the Template Knights
        # These are empty shells waiting for a Soul (Persona)
        from kernel.agora.knights.notebook_knight import NotebookKnight
        from kernel.agora.knights.omni_knight import OmniKnight

        self.lancelot = OmniKnight("LANCELOT", default_role="The Architect")
        self.galahad = OmniKnight("GALAHAD", default_role="The Coder")
        self.percival = OmniKnight("PERCIVAL", default_role="The Auditor")
        self.librarian = NotebookKnight("GALAHAD_RESEARCH")

        self.router.register(self.lancelot)
        self.router.register(self.galahad)
        self.router.register(self.percival)
        self.router.register(self.librarian)

    async def receive(self, envelope: ANPEnvelope) -> None:
        """
        Receives a sovereign_context and routes it.
        Envelope Payload expected: {"context": SovereignContext.dict()}
        """
        if envelope.protocol != "ROUTING_REQUEST":
            return

        payload = envelope.payload
        # Rehydrate Context
        context_data = payload.get("context", {})
        # Basic dict for now, or rehydrate object if needed.
        # We'll treat it as a dict to be safe for serialization.

        intent = context_data.get("intent", "").lower()
        print(f"👁️ [VIDENEPTUS] Analyzing Intent: '{intent[:50]}...'")

        target_agent = self._classify_route(intent)
        print(f"👁️ [VIDENEPTUS] Route Selected: {target_agent}")

        # Forward the Context to the Target
        await self.send(
            self.router, recipient=target_agent, protocol="TASK_ASSIGNMENT", payload={"context": context_data}
        )

    def _classify_route(self, intent: str) -> str:
        """
        Heuristic Semantic Routing (Layer 1).
        Future: Upgrade to LLM-based classification.
        """
        if any(w in intent for w in ["search", "find", "research", "look up"]):
            return "GALAHAD_RESEARCH"  # The Librarian

        if any(w in intent for w in ["plan", "design", "architect", "roadmap", "strategy"]):
            return "LANCELOT"  # The Architect

        if any(w in intent for w in ["code", "write", "implement", "fix", "debug", "refactor"]):
            return "GALAHAD"  # The Coder

        if any(w in intent for w in ["audit", "verify", "secure", "scan", "check"]):
            return "PERCIVAL"  # The Auditor

        return "MERLIN_OMEGA"  # Default / Fallback / Complex Reasoning

    async def execute_lac_loop(self, prompt: str, context_str: str) -> str:
        """
        Executes the 3-Phase Learning-at-Criticality Loop with UKG Runtime integration.
        
        UKG Enhancement:
        - Phase 1: DIVERGENCE (T=1.2) - Generate approaches
        - Phase 2: CRITICALITY (T=0.9) - Critique via UKG anchors
        - Phase 3: CONVERGENCE (T=0.0) - Deterministic synthesis using UKG Runtime
        """
        print(f"🌀 [VIDENEPTUS] Engaging UKG-Enhanced LaC Loop for: {prompt[:50]}...")
        
        # Initialize UKG Runtime
        from kernel.Engines.ukg_runtime import UKGRuntime
        ukg = UKGRuntime()
        
        # PHASE 1: DIVERGENCE (Creative exploration)
        print("[VIDENEPTUS] Phase 1: DIVERGENCE (T=1.2)")
        divergence_prompt = f"""
        [CONTEXT]
        {context_str}

        [INSTRUCTION]
        Generate 3 distinct, divergent architectural approaches or solutions for the user's request: "{prompt}".
        They must be fundamentally different in strategy or technology stack.
        Label them APPROACH A, APPROACH B, APPROACH C.
        """
        divergence_res = await PrismAdapter.transmit(
            model="gemini-1.5-flash", 
            prompt=divergence_prompt, 
            system_persona="You are a divergent thinker. Explore the solution space widely."
        )

        # PHASE 2: CRITICALITY (UKG-anchored critique)
        print("[VIDENEPTUS] Phase 2: CRITICALITY (T=0.9) - UKG Anchoring")
        
        # Extract anchors from divergence results
        ukg_analysis = ukg.execute(divergence_res)
        print(f"[UKG] Analysis: {ukg_analysis}")
        
        criticality_prompt = f"""
        [OPTIONS]
        {divergence_res}
        
        [UKG_ANCHORS]
        {ukg_analysis}

        [INSTRUCTION]
        Critique each approach against First Principles (Security, Scalability, Simplicity).
        Use the UKG anchors to validate against known patterns.
        Assign a score (0-100) to each.
        Select the best single approach or a hybrid of the best features.
        """
        criticality_res = await PrismAdapter.transmit(
            model="gemini-1.5-flash",
            prompt=criticality_prompt,
            system_persona="You are a critical auditor. Be harsh but fair."
        )

        # PHASE 3: CONVERGENCE (Deterministic synthesis - T=0.0)
        print("[VIDENEPTUS] Phase 3: CONVERGENCE (T=0.0) - Deterministic UKG Synthesis")
        
        # Final UKG weave for deterministic output
        final_ukg = ukg.execute(criticality_res)
        
        convergence_prompt = f"""
        [WINNING ANALYSIS]
        {criticality_res}
        
        [UKG_VALIDATION]
        {final_ukg}

        [USER REQUEST]
        {prompt}

        [INSTRUCTION]
        Synthesize the winning approach into a definite, stepwise execution plan.
        Output must be actionable, rigorous, and deterministic.
        Use ONLY validated UKG anchors. Reject hallucinated concepts.
        """
        final_res = await PrismAdapter.transmit(
            model="gemini-1.5-flash",
            prompt=convergence_prompt,
            system_persona="You are the Sovereign Kernel. Output definitive, high-quality plans. Temperature=0.0 for determinism."
        )
        
        # Auto-repair UKG graph after execution
        repair_stats = ukg.auto_repair()
        print(f"[UKG] Auto-Repair: {repair_stats}")

        return f"🌀 [VIDENEPTUS UKG-LaC RESULT]\n{final_res}\n\n[UKG_STATS] {final_ukg}"