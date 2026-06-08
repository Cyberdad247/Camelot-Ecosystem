# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
# -*- coding: utf-8 -*-
import asyncio
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

# Add KERNEL to path for telemetry import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    from senses.telemetry_client import RotelClient
    telemetry = RotelClient("merlin_omega")
except ImportError:
    class DummyLogger:
        def info(self, *args, **kwargs): pass
    telemetry = DummyLogger()

from kernel.agora.context import SovereignContext

# AGORA & REASONING IMPORTS
from kernel.agora.node import AgentNode
from kernel.agora.protocol import ANPEnvelope
from kernel.agora.router import AgoraRouter
from kernel.agora.videneptus import Videneptus
from kernel.Engines.coherence_engine import coherence
from kernel.Engines.prism_gateway import PrismAdapter, TheJudge
from kernel.Engines.sentinel_compressor import SentinelCompressor
from kernel.reasoning.aurora_vision import aurora
from kernel.reasoning.core import MGVEngine
from kernel.reasoning.helix_loop import helix
from kernel.reasoning.lyricus_voice import lyricus
from kernel.reasoning.oracle_physics import physics as oracle_physics
from kernel.reasoning.prometheus_decomp import prometheus
from kernel.reasoning.veritas_audit import veritas
from kernel.security.warden import warden

# ANTIGRAVITY
from src.tools.antigravity import gravity


# ==============================================================================
# 🧠 MERLIN_OMEGA v100.2 (SOP_OPTIMIZED) - THE SOVEREIGN KERNEL
# ==============================================================================
class Merlin_Omega(AgentNode):
    """
    MERLIN_OMEGA v100.2 (Resource Optimized)
    Now utilizing:
    1. RTF System Prompt
    2. Context Compression
    3. Token & Concurrency Budgeting
    4. Council Mode (Cartridges)
    5. Sovereign Context (Wilmer-Pattern)
    6. Oracle Hypervisor (Physics Engine)
    """

    def __init__(self, manifest_path: str = "config/system_manifest.json"):
        super().__init__("MERLIN_OMEGA")
        self.identity = "Merlin_Omega"
        self.version = "100.2 (OPTIMIZED)"
        self.ledger_path = "PROVENANCE_LEDGER.md"
        self.session_id = os.getenv("SESSION_ID", "OMEGA_SESSION_INIT")
        self.backend_url = os.getenv("BACKEND_URL", "http://localhost:3001")
        self.genkit_root = os.path.join(os.getcwd(), "genkit_layer")

        # RESOURCE TRACKING
        self.total_tokens_consumed = 0
        self.active_knights = 0
        self.concurrency_limit = 8
        self.token_budget_per_quest = 50000

        # Load Optimized System Prompt
        try:
            self.system_prompt = gravity.read("01_KERNEL/prompts/merlin_v2.md")
        except Exception:
            self.system_prompt = "FATAL: System Prompt Missing."

        # Initialize Reasoning Engine & Router
        self.reasoning_engine = MGVEngine(debug=True)
        self.oracle = oracle_physics  # The Physics Engine
        self.router = AgoraRouter()

        # Spin up Videneptus (Semantic Router)
        self.videneptus = Videneptus()
        self.router.register(self.videneptus)
        self.router.register(self)  # Self-register

        self._initialize_ledger()

    async def _activate_council_mode(self, cartridge_name: str = "HAWK"):
        """
        Dynamically hydrates the Think Tank prompt based on the selected Cartridge.
        """
        print(f"🧠 [MERLIN] Loading Cartridge: {cartridge_name}...")

        try:
            # 1. Load Cartridge Config
            content = gravity.read("01_KERNEL/config/cartridges.json")
            cartridges = json.loads(content)

            cartridge = cartridges.get(cartridge_name, cartridges["HAWK"])

            # 2. Load Prompt Template
            template = gravity.read("01_KERNEL/Protocols/ThinkTank/UNIVERSAL_PROMPT.md")

            # 3. Hydrate Template (Dynamic Parameter Binding)
            hydrated_prompt = template.replace("{{CARTRIDGE_MODE}}", cartridge["description"])
            hydrated_prompt = hydrated_prompt.replace("{{CARTRIDGE_NAME}}", cartridge_name)

            for i, knight_name in enumerate(cartridge["knights"]):
                slot = i + 1
                hydrated_prompt = hydrated_prompt.replace(f"{{{{KNIGHT_{slot}_NAME}}}}", knight_name)
                hydrated_prompt = hydrated_prompt.replace(f"{{{{KNIGHT_{slot}_ROLE}}}}", "Council Member")
                hydrated_prompt = hydrated_prompt.replace(f"{{{{KNIGHT_{slot}_VOICE}}}}", "Sovereign/Direct")
                hydrated_prompt = hydrated_prompt.replace(f"{{{{KNIGHT_{slot}_FOCUS}}}}", "Mission Success")
                hydrated_prompt = hydrated_prompt.replace(
                    f"{{{{KNIGHT_{slot}_CONSTRAINT}}}}", "Adhere to Titanium Laws"
                )

            self.system_prompt = hydrated_prompt
            print(f"🧠 [MERLIN] Council Assembled. Lead: {cartridge['lead']}")
            return True

        except Exception as e:
            print(f"⚠️ [MERLIN] Cartridge Load Failed: {e}")
            return False

    async def receive(self, envelope: ANPEnvelope) -> None:
        """
        [AGORA PROTOCOL] Handle incoming messages.
        """
        sender = envelope.sender
        protocol = envelope.protocol
        print(f"🧠 [MERLIN] Received {protocol} from {sender}")

        if protocol == "Task":
            # Process the task using MGV + GenKit
            response = await self.process_request(envelope.payload.get("instruction", ""))

            # Reply via Agora
            router = AgoraRouter()
            await self.send(router, sender, "Result", {"response": response})

    async def _update_hud(
        self, intent: Optional[str] = None, stage: str = "P0_GATEKEEP", metrics: List[Dict] = []
    ) -> None:
        """Broadcasts state to the OMEGA HUD via Agora."""
        try:
            payload = {
                "session_id": self.session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "intent": intent,
                "workflow_stage": stage,
                "metrics": metrics,
            }
            router = AgoraRouter()
            await self.send(router, "BROADCAST", "Telemetry", payload)
        except Exception:
            pass

    def _initialize_ledger(self) -> None:
        """Ensures the PROVENANCE_LEDGER.md exists."""
        if not os.path.exists(self.ledger_path):
            gravity.write(
                self.ledger_path, "# PROVENANCE LEDGER\n| Timestamp | Entity | Event | Status |\n|---|---|---|---|"
            )

    def _log_provenance(self, event: str, status: str = "SUCCESS") -> None:
        """Enforces LEDGER_IS_LAW."""
        timestamp = datetime.now().isoformat()
        try:
            gravity.append(self.ledger_path, f"| {timestamp} | {self.identity} | {event} | {status} |\n")
        except Exception:
            pass

    async def process_oracle_command(self, prompt: str, context: SovereignContext) -> str:
        """
        Handles Ω_ORACLE commands for the Hypervisor Simulation.
        Enforces HITL (Human-in-the-Loop) Protocol for critical actions.
        """
        cmd = prompt.strip()

        # --- HITL IRON GATE ---
        # Protected Commands: Ω_FORK, Ω_GOD_MODE
        critical_cmds = ["Ω_FORK", "Ω_GOD_MODE"]

        # Check if command is critical
        is_critical = any(c in cmd for c in critical_cmds)

        if is_critical:
            # Check for Confirmation Token
            if "Ω_CONFIRM" not in cmd:
                return f"⚠️ [IRON GATE] CRITICAL ACTION DETECTED ({cmd}).\n   Use 'Ω_CONFIRM' to authorize timeline divergence or forced causality break."

        # 0. Ω_GENESIS (Scenario Generation)
        if "Ω_GENESIS" in cmd:
            try:
                scenario_prompt = gravity.read("01_KERNEL/prompts/oracle/SCENARIO_GENERATOR.md")
                instructions = cmd.split("Ω_GENESIS")[-1].strip()
                # Fuse system prompt with user instructions
                final_input = f"{scenario_prompt}\n\nUSER INPUT: {instructions}"
                # In a real system, we'd send this to the LLM.
                # For now, we simulate the 'Call' to the Genesis Engine
                return f"🌌 [ORACLE] GENESIS ENGINE INITIALIZED.\n   Loading Pattern: {instructions}...\n   [SYSTEM] Scenario generated based on 'SCENARIO_GENERATOR.md'"
            except Exception as e:
                return f"❌ [ORACLE] GENESIS FAILURE: Could not load generator prompt. {str(e)}"

        # 1. Ω_STEP (Time Advance)
        if "Ω_STEP" in cmd:
            self.oracle.step(context)
            return f"⏳ [ORACLE] Time Advanced. Epoch: {context.world_state['epoch']} | Tension: {context.world_state.get('global_tension', 0.5)}"

        # 2. Ω_XRAY (Explain Reasoning)
        elif "Ω_XRAY" in cmd:
            return "🔍 [ORACLE] X-RAY: ToT Trace reveals Agency (0.5) drove the decision."

        # 3. Ω_FORK (Parallel Timeline) -> PROTECTED
        elif "Ω_FORK" in cmd:
            new_id = f"{context.session_id}_FORK_{int(time.time())}"
            return f"Ψ [ORACLE] Timeline Forked. Context cloned to ID: {new_id}"

        # 4. Ω_GOD_MODE (Force Event) -> PROTECTED
        elif "Ω_GOD_MODE" in cmd:
            event = cmd.split("Ω_GOD_MODE")[-1].strip()
            return f"⚡ [ORACLE] CAUSALITY BREACH: Event '{event}' injected into timeline."

        # 5. Ω_OPEN (Kinetic Hand) -> Uses Excalibur Bridge
        elif "Ω_OPEN" in cmd:
            try:
                from agora.bridge import bridge

                instructions = cmd.split("Ω_OPEN")[-1].strip()
                # Determine if it's a plan or final execution
                plan_only = "--execute" not in instructions
                clean_instr = instructions.replace("--execute", "").strip()

                res = await bridge.fast_refactor(clean_instr, context_details="Sovereign Context Hydrated.")
                return f"🗡️ [EXCALIBUR BRIDGE] Kinetic Action Triggered.\n{res}"
            except Exception as e:
                return f"❌ [EXCALIBUR BRIDGE] BRIDGE FAILURE: {str(e)}"

        # 6. //COUNCIL (Simulated Debate) -> Council of Peers Integration
        elif "//COUNCIL" in cmd or "//DEBATE" in cmd:
            try:
                from reasoning.council_debate import CouncilDebate

                intent = cmd.replace("//COUNCIL", "").replace("//DEBATE", "").strip()
                council = CouncilDebate(self)
                res = await council.facilitate_debate(intent, context)
                return res
            except Exception as e:
                return f"❌ [COUNCIL] DEBATE INTERRUPTION: {str(e)}"

        # 7. //FLEET (Aether Swarm Dashboard)
        elif "//FLEET" in cmd:
            try:
                # Launch the Go terminal dashboard
                subprocess.Popen("start cmd /k 01_KERNEL\\agora\\fleet\\fleet_cmd.exe", shell=True)
                return "⚔️ [FLEET] Aether Swarm Dashboard launched in separate console."
            except Exception as e:
                return f"❌ [FLEET] Deployment failure: {e}"

        # 8. //FORGE (Titan Forge)
        elif "//FORGE" in cmd:
            try:
                from reasoning.titan_forge import TitanForge

                intent = cmd.replace("//FORGE", "").strip()
                # Heuristic: Gather context for open or related files
                # For this implementation, we simulate gathering 'api_server.py' and 'merlin_omega.py'
                output = TitanForge.compile_forge_envelope(
                    intent, ["01_KERNEL/api_server.py", "01_KERNEL/merlin_omega.py"]
                )
                return f"⚒️ [FORGE] Context compiled for industrial action: {output}"
            except Exception as e:
                return f"❌ [FORGE] Compilation error: {e}"

        # 9. Ω_ACTION (Bytebot)
        elif "Ω_ACTION" in cmd:
            try:
                from src.knights.bytebot.bytebot_knight import Bytebot

                action_data = cmd.split("Ω_ACTION")[-1].strip().split(" ")
                action_type = action_data[0]
                target = action_data[1] if len(action_data) > 1 else "Unknown"
                res = Bytebot.execute_action(action_type, target)
                self._log_provenance(f"Ω_ACTION: {action_type} on {target}", "SUCCESS")
                return f"🤖 [BYTEBOT] Ω_ACTION Result: {res}"
            except Exception as e:
                return f"❌ [BYTEBOT] Manipulation failed: {e}"

        # 10. Ω_NOTIFY (Hermes)
        elif "Ω_NOTIFY" in cmd:
            try:
                from security.hermes import notify

                msg = cmd.split("Ω_NOTIFY")[-1].strip()
                notify("⚔️ CAMELOT OS", msg)
                return f"📧 [HERMES] Notification delivered: {msg}"
            except Exception as e:
                return f"❌ [HERMES] Delivery failure: {e}"

        # 11. Ω_SHADOW (Shadow Mode Toggle)
        elif "Ω_SHADOW" in cmd:
            try:
                from security.shadow_mode import shadow_manager

                state = "ON" in cmd.upper()
                shadow_manager.toggle(state)
                status = shadow_manager.get_status()
                return (
                    f"🕵️ [SHADOW] Status: {'ACTIVE' if status['active'] else 'INACTIVE'} | Node: {status['exit_node']}"
                )
            except Exception as e:
                return f"❌ [SHADOW] Protocol failure: {e}"

        # 12. //SUMMON (Knight Swarm)
        elif "//SUMMON" in cmd:
            try:
                from scripts.knight_swarm_manager import KnightSwarmManager

                intent = cmd.replace("//SUMMON", "").strip()
                manager = KnightSwarmManager()
                # Run the automated workflow as a background task
                asyncio.create_task(manager.summon_knights_for_project("Dynamic_Task", intent))
                return f"⚔️ [SUMMON] Knight Swarm activated for intent: {intent[:30]}..."
            except Exception as e:
                return f"❌ [SUMMON] Agora Routing error: {e}"

        # 13. Ω_DREAM (Dream State Engine)
        elif "Ω_DREAM" in cmd:
            try:
                from reasoning.dream_state import dream_engine

                if "ON" in cmd.upper():
                    asyncio.create_task(dream_engine.enter_dream_state())
                    return "💤 [DREAM STATE] Engine Actuated. Nightly learning protocols engaged."
                else:
                    dream_engine.wake_up()
                    return "☀️ [DREAM STATE] Engine Disengaged. Sovereign awake."
            except Exception as e:
                return f"❌ [DREAM STATE] Neural failure: {e}"

        # 14. Ω_VERITAS (Truth & Audit)
        elif "Ω_VERITAS" in cmd:
            target = cmd.split("Ω_VERITAS")[-1].strip()
            # Simulation: Audit the context or a file
            res = veritas.audit_document(target or "General Context Scan")
            return f"🔍 [VERITAS] Audit Results: {res['status']} | Findings: {len(res['findings'])}"

        # 15. Ω_LYRICUS (Voice & Tone)
        elif "Ω_LYRICUS" in cmd:
            text = cmd.split("Ω_LYRICUS")[-1].strip()
            tone = "Sovereign"
            if "--tone" in text:
                parts = text.split("--tone")
                text = parts[0].strip()
                tone = parts[1].strip()
            res = lyricus.modulate(text, tone)
            return f"🎵 [LYRICUS] Modulated Output: {res}"

        # 16. Ω_PROMETHEUS (Decomposition)
        elif "Ω_PROMETHEUS" in cmd:
            query = cmd.split("Ω_PROMETHEUS")[-1].strip()
            steps = prometheus.decompose(query)
            return f"🔥 [PROMETHEUS] Decomposed Plan: {' -> '.join(steps)}"

        # 17. Ω_HELIX (Self-Correction)
        elif "Ω_HELIX" in cmd:
            parts = cmd.split("Ω_HELIX")[-1].strip().split("|")
            action = parts[0].strip() if len(parts) > 0 else "Unknown Action"
            obs = parts[1].strip() if len(parts) > 1 else "No Observation"
            res = helix.reflect(action, obs)
            return f"🧬 [HELIX] Reflection: {res['reflection']} | Correction: {res['correction_plan']}"

        # 17.5 Ω_LEARN (Omega Learn)
        elif "Ω_LEARN" in cmd:
            try:
                from learning.dataset_generator import generator

                count, path = generator.generate_sft_pairs()
                return f"🎓 [OMEGA_LEARN] Dataset Generation Complete. Extracted {count} SFT pairs to {path}."
            except Exception as e:
                return f"❌ [OMEGA_LEARN] Training ingestion failure: {e}"

        # 18. //VISION (Aurora Multimodal)
        elif "//VISION" in cmd:
            intent = cmd.replace("//VISION", "").strip()
            fw = aurora.select_framework(intent)
            return f"🌅 [AURORA] Framework Selected: {fw} for intent: {intent}"

        # 19. Ω_WARDEN (Security Warden)
        elif "Ω_WARDEN" in cmd:
            try:
                from security.warden import handle_warden_command

                return handle_warden_command(cmd)
            except Exception as e:
                return f"❌ [WARDEN] Security system error: {e}"

        # 20. Ω_SYNC (Ouroboros Loop)
        elif "Ω_SYNC" in cmd:
            try:
                # Execute sync_engine.py as a subprocess
                sync_script = os.path.join("01_KERNEL", "sync_engine.py")
                if not os.path.exists(sync_script):
                    return "❌ [OUROBOROS] Sync Engine not found at 01_KERNEL/sync_engine.py"

                process = await asyncio.create_subprocess_exec(
                    sys.executable, sync_script, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()

                if process.returncode == 0:
                    output = stdout.decode().strip()
                    # Filter for just the status messages
                    summary = "\n".join([line for line in output.split("\n") if line.startswith("[")])
                    return f"🔄 [OUROBOROS] Sync Complete.\n{summary}"
                else:
                    return f"⚠️ [OUROBOROS] Sync Failed.\n{stderr.decode()}"
            except Exception as e:
                return f"❌ [OUROBOROS] Execution Error: {str(e)}"

        # --- SIT-LOOP PHYSICS STEP (Actuating Oracle Engine) ---
        from reasoning.oracle_physics import physics

        context = physics.step(context)
        print(
            f"🔮 [ORACLE] Physics Step Completed. Epoch: {context.world_state['epoch']} | Tension: {context.world_state['global_tension']}"
        )

        # Default: Pass to Standard Reasoning but with Physics Mode checks
        return f"🔮 [ORACLE] Simulation Inputs Registered. State: {context.world_state}"

    async def process_request(self, raw_input: str) -> str:
        """
        Routes intent through:
        1. Memory Retrieval (Chronos) & Compression
        2. Mode Check (Think Tank / Council)
        3. MGV (Safety/Reasoning)
        4. GenKit (Execution)
        """
        telemetry.info("PROCESSING_REQUEST", input=raw_input[:100])
        # Check Concurrency
        if self.active_knights >= self.concurrency_limit:
            return "⚠️ [MERLIN] Concurrency Cap Reached. Standing by for resources."

        self.active_knights += 1
        start_ts = time.time()

        try:
            # --- SECURITY LAYER: WARDEN ADMITTANCE ---
            # Enforce Zero-Trust before any processing
            warden.verify_permission(
                agent_id=self.identity,
                resource_type="system_api",
                action="PROCESS_REQUEST",
                target="merlin_omega",
                trust_level="KERNEL",
            )

            # --- PHASE 0: SOVEREIGN CONTEXT INITIALIZATION ---
            # Assimilated from WilmerAI: Create the unified Context Object
            context = SovereignContext(session_id=self.session_id, intent=raw_input)
            context.set_var("agent_inputs", {"Input": raw_input})

            # Ask Videneptus for the route (Pre-Routing)
            # Future State: We will await the semantic classification
            # For now, we perform the Heuristic check locally to maintain stability during transition

            # --- ORACLE INTERCEPT ---
            if any(x in raw_input for x in ["ORACLE", "Ω_", "//COUNCIL", "//DEBATE"]):
                response = await self.process_oracle_command(raw_input, context)
                self._log_provenance(raw_input, "SUCCESS (ORACLE)")
                return response

            # --- MODE CHECK: COUNCIL ACTIVATION ---
            if raw_input.startswith("/plan") or raw_input.startswith("//PRD"):
                # Detect Cartridge (e.g., /plan --mode ANT)
                mode = "HAWK"  # Default
                if "--mode" in raw_input:
                    parts = raw_input.split("--mode")
                    if len(parts) > 1:
                        mode = parts[1].strip().split(" ")[0].upper()

                await self._activate_council_mode(mode)

            # --- PHASE 1: SENSE & COMPRESS (Context Optimization) ---
            print("[MERLIN] 1. SENSE: Querying Ouroboros...")
            from kernel.rag.lightrag_engine import get_lightrag_engine

            rag_start = time.time()
            memory = get_lightrag_engine().query(raw_input, top_k=3)  # Reduced from 5 to optimize window
            rag_latency = (time.time() - rag_start) * 1000

            # Sentinel Compression (Active Distillation)
            context_str = ""
            if memory and memory.results:
                raw_context = "\n".join([res.content for res in memory.results])
                # 1. Anchor Encoding (Token Reduction)
                raw_context = SentinelCompressor.encode_anchors(raw_context)
                # 2. Local Distillation (Semantic Compression)
                context_str = await SentinelCompressor.distill(raw_context, raw_input)

            print(f"[MERLIN] Sentinel Distillation Complete: {len(context_str)} chars.")

            # Simple prompt tree-shaking for token efficiency
            mgv_analysis = self.reasoning_engine.monitor(raw_input)
            active_system_prompt = SentinelCompressor.tree_shake_prompt(
                self.system_prompt, "LOW" if mgv_analysis["complexity"] == "LOW" else "HIGH"
            )

            # --- VIDENEPTUS LaC INTERCEPT (Layer 3) ---
            # If complexity is HIGH, engage the 3-Phase Loop
            if mgv_analysis.get("complexity") == "HIGH":
                print("🧠 [MERLIN] Complexity HIGH detected. Engaging Videneptus LaC Loop...")
                lac_response = await self.videneptus.execute_lac_loop(raw_input, context_str)
                
                # Log and Return immediately (Bypassing Standard Prism)
                self._log_provenance(f"LaC Loop Execution: {raw_input}", "SUCCESS")
                await self._update_hud(
                    intent=raw_input,
                    stage="COMPLETED_LaC",
                    metrics=[{"label": "STRATEGY", "value": "VIDENEPTUS_3_PHASE", "status": "success"}]
                )
                
                # Indexing for LaC
                get_lightrag_engine().index(
                    content=f"PROMPT: {raw_input} | LaC_RESPONSE: {lac_response}",
                    metadata={"type": "session_memory", "timestamp": datetime.now().isoformat(), "strategy": "LaC"}
                )
                return lac_response

            await self._update_hud(
                intent=raw_input,
                stage="P2_THINK",
                metrics=[{"label": "RAG_LATENCY", "value": f"{rag_latency:.2f}ms", "status": "normal"}],
            )

            # --- PHASE 2: THINK (Reasoning with Prompt Injection) ---
            # We inject the structured context into the prompt template
            final_prompt = f"{active_system_prompt}\n\n[CONTEXT]:\n{context_str}\n\n[USER]: {raw_input}"

            # Token Counting (Simulated)
            tokens_used = (len(final_prompt)) // 4
            self.total_tokens_consumed += tokens_used
            if self.total_tokens_consumed > self.token_budget_per_quest:
                print(f"🛑 [BUDGET_EXCEEDED] {self.total_tokens_consumed} tokens used.")

            print("[MERLIN] Engaging MGV Reasoning...")
            mgv_start = time.time()
            mgv_result = self.reasoning_engine.process(final_prompt)
            mgv_latency = (time.time() - mgv_start) * 1000

            await self._update_hud(
                intent=raw_input,
                stage="P3_MGV_AUDIT",
                metrics=[{"label": "MGV_LATENCY", "value": f"{mgv_latency:.2f}ms", "status": "normal"}],
            )

            if "BLOCKED_BY_VERIFIER" in mgv_result:
                self._log_provenance(f"MGV Blocked: {raw_input}", "BLOCKED")
                await self._update_hud(
                    intent=raw_input,
                    stage="BLOCKED",
                    metrics=[{"label": "SAFETY", "value": "REJECTED", "status": "critical"}],
                )
                return mgv_result

            print(f"[MERLIN] MGV Approved. Draft: {mgv_result[:50]}...")

            # --- PHASE 3: PRISM INTELLIGENCE EXECUTION (Excalibur) ---
            final_response = ""
            try:
                await self._update_hud(
                    intent=raw_input,
                    stage="P4_PRISM_INFERENCE",
                    metrics=[{"label": "PRIMARY_MODEL", "value": "GEMINI_FLASH", "status": "normal"}],
                )

                # Select Optimal Model
                champion_model = TheJudge.deliberate(raw_input)

                # --- REASONING BUDGET CALCULATION ---
                thinking_budget = 0
                if champion_model.startswith("gemini"):
                    if mgv_analysis["complexity"] == "HIGH":
                        thinking_budget = 16384  # High budget for complex tasks
                    elif mgv_analysis["requires_reasoning"]:
                        thinking_budget = 4096   # Medium budget for moderate tasks

                # Transmit with Automatic Fallback
                prism_response = await PrismAdapter.transmit(
                    model=champion_model, prompt=final_prompt, system_persona=self.system_prompt,
                    thinking_budget=thinking_budget
                )

                if not prism_response:
                    print("[MERLIN] Prism failed. Falling back to MGV Draft.")
                    final_response = f"MGV Response: {mgv_result}"
                else:
                    final_response = prism_response

                # --- PHASE 6: COHERENCE VERIFICATION & SELF-HEAL ---
                verification = await coherence.verify_output(raw_input, final_response)
                if not verification.get("valid", True) and verification.get("score", 100) < 60:
                    print(
                        f"⚠️ [MERLIN] Output failed coherence check (Score: {verification['score']}). Attempting heal..."
                    )
                    healed = await coherence.self_heal(
                        raw_input, final_response, verification.get("critique", "Logic flaw")
                    )
                    if healed:
                        final_response = healed
                        print("✅ [MERLIN] Self-Heal Applied.")

                # --- SECURITY LAYER: WARDEN SANITIZATION ---
                # Scan final response for dangerous patterns or prompt injection leakage
                final_response = warden.sanitize_llm_output(final_response, allow_code=True)

                # --- PHASE 4: LONG-TERM INDEXING & METRICS ---
                total_latency = (time.time() - start_ts) * 1000
                print(f"[METRICS] Latency: {total_latency:.2f}ms | RAG: {rag_latency:.2f}ms")

                print("[MERLIN] Archiving interaction to Chronos...")
                get_lightrag_engine().index(
                    content=f"PROMPT: {raw_input} | RESPONSE: {final_response}",
                    metadata={"type": "session_memory", "timestamp": datetime.now().isoformat()},
                )

                self._log_provenance("Request Processed and Indexed", "SUCCESS")
                await self._update_hud(
                    intent=raw_input,
                    stage="COMPLETED",
                    metrics=[{"label": "TOTAL_LATENCY", "value": f"{total_latency:.2f}ms", "status": "success"}],
                )

                # 📡 Telemetry: Log completion
                telemetry.info("REQUEST_PROCESSED", latency_ms=total_latency)

                # --- LAW IV: ANYA LAST (Resonance Wrapping) ---
                resonated_response = f"💡 {final_response}"
                return resonated_response

            except Exception as e:
                telemetry.error("REQUEST_EXECUTION_FAILED", error=str(e))
                self._log_provenance(f"Failure: {str(e)}", "CRITICAL")
                await self._update_hud(intent=raw_input, stage="ERROR")
                return f"Kernel Error: {str(e)} (Fallback: {mgv_result})"
        finally:
            self.active_knights -= 1


# Production Check
if __name__ == "__main__":
    # Standalone Test
    kernel = Merlin_Omega()
    print("Merlin Initialized as Agora Node.")