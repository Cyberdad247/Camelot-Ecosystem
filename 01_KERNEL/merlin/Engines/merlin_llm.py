# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
MERLIN_LLM_v1.0
The Realized Brain: Bridging TAL Manifests to Live LLM Integration.
Supports Ollama, Meta-Llama (via local weights), and OpenAI.
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path

# Use litellm for universal provider support
try:
    import litellm
except ImportError:
    # If not installed, we fallback to a simulated response or provide instructions
    litellm = None

class MerlinLLM:
    """
    The LLM Engine for Merlin v2 [SINGULARITY].
    Now functions as the LLM_Manager and Abstraction Layer with Resource Optimization.
    """
    
    def __init__(self, default_model: str = "ollama/llama3.2:1b"):
        self.registry = {
            "local": {
                "reasoning": "ollama/llama3.2:1b", # Fallback from deepseek
                "planning": "ollama/llama3.2:1b",
                "coding": "ollama/llama3.2:1b", # Switched from codellama for memory constraints
                "utility": "ollama/phi3:mini",
                # [MODEL_QUANTIZATION] 4-bit/8-bit optimized variants
                "quantized": {
                    "reasoning": "ollama/llama3.2:1b",
                    "general": "ollama/llama3.2:1b",
                    "coding": "ollama/llama3.2:1b"
                },
                # [MODEL_DISTILLATION] Student models trained on high-quality reasoning
                "student": {
                    "reasoning": "ollama/qwen2.5:1.5b",
                    "planning": "ollama/phi3:mini"
                }
            },
            "cloud": {
                "heavy": "openai/gpt-4o",
                "planning": "google_ai_studio/gemini-pro",
                "fast": "openai/gpt-3.5-turbo"
            }
        }
        # [LoRA_ADAPTATION] Specialized adapters for domain tasking
        self.lora_adapters = {
            "finance": "lora_adapter_finance_v1",
            "security": "lora_adapter_audit_v2",
            "debate": "lora_adapter_socratic_v1"
        }

        # [SYMBOLECT] Prompt shortcuts
        self.symbolect_map = {
            "[🌙🔄🧩📦]": "Add a dark-mode toggle using React Context and localStorage",
            "[🧭PRD]": "Generate PRD summary using specialized TAL structure",
            "[🔒SCAN]": "Run SBOM and security audit on current directory",
            "[🚀FORGE]": "Initiate full build and kinetic verification loop",
            "[🔨BUILD]": "Compile core logic and verify entry points",
            "[🛡️AUDIT]": "Security deep-dive of the current diff and repo",
            "[🧹CLEAN]": "Lint, format, and prune unused imports/dead code",
            "[⚖️JUDGE]": "Apply Lukas Evaluation Gate to current session results"
        }
        
        # Specialization Profiles
        self.profiles = {
            "CoT": {"temperature": 0.0, "max_tokens": 1024, "top_p": 0.1},
            "Creative": {"temperature": 0.8, "max_tokens": 512, "top_p": 0.9},
            "JSON": {"temperature": 0.2, "max_tokens": 1024, "response_format": {"type": "json_object"}},
            "Standard": {"temperature": 0.2, "max_tokens": 512},
            "Compressed": {"temperature": 0.1, "max_tokens": 256} # Low precision / Low token usage
        }

        self.default_model = os.getenv("MERLIN_MODEL", default_model)
        self.reasoning_bank = Path("03_VAULT/knowledge/reasoning_bank")
        self.persona_library = Path("03_VAULT/knowledge/persona_library")
        os.makedirs(self.reasoning_bank, exist_ok=True)
        os.makedirs(self.persona_library, exist_ok=True)
        
        # Configuration for litellm
        if litellm:
            litellm.telemetry = False
            litellm.api_base = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")

    # --- PERSONA ENGINE ---

    def load_persona(self, persona_id: str) -> Dict[str, Any]:
        """Loads a persona manifest from the vault."""
        file_path = self.persona_library / f"{persona_id.lower()}.json"
        if not file_path.exists():
            return {}
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def render_persona_prompt(self, persona: Dict[str, Any]) -> str:
        """
        [Omega_FORGE] Renders the new Persona JSON Schema into a Markdown system prompt.
        """
        identity = persona.get("core_identity", {})
        caps = persona.get("capabilities", {})
        guards = persona.get("guardrails", {})
        
        prompt = f"""# 🏛️ IDENTITY: {persona.get('name', 'UNKNOWN_ENTITY')}
**[ROLE]:** {persona.get('role', 'Expert_Agent')}
**[SUMMARY]:** {identity.get('summary', 'Uphold the Sovereign Kinetic Law.')}

## 🧬 COGNITIVE PROFILE
- **Tone:** {identity.get('tone', 'Technical')}
- **Skillset:** {', '.join(identity.get('skill_tags', []))}
- **Voice:** {identity.get('speech_pattern', {}).get('sentence_length', 'medium')} sentences. 

## ⚡ CAPABILITIES & LIMITS
- **Tools:** {', '.join(caps.get('allowed_mcp_tools', []))}
- **HITL Required for:** {', '.join(guards.get('require_hitl_for', []))}
- **Forbidden:** {', '.join(guards.get('forbidden_actions', []))}

---
**[SYSTEM_STATUS]:** ACTIVE. LATTICE STABLE.
"""
        return prompt

    def resolve_symbolect(self, trigger: str) -> str:
        """Resolves a symbolect token into a full directive."""
        return self.symbolect_map.get(trigger, trigger)

    def render_tal_block(self, tal_structure: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        [TAL_RENDER] expansion logic.
        """
        instructions = tal_structure.get("instructions", "")
        fields = tal_structure.get("structure", [])
        
        rendered_fields = []
        for field in fields:
            name = field["name"]
            val = context.get(name, f"[{name.upper()}_HERE]")
            rendered_fields.append(f"### {name}\n{val}")
            
        return f"{instructions}\n\n" + "\n\n".join(rendered_fields)

    def compress_context(self, context: str, ratio: float = 0.5) -> str:
        """
        [CONTEXT_COMPRESSION] Reduces token usage by summarizing background context.
        Note: In real usage, this might call a student model or use a regex/freq pass.
        """
        if len(context) < 500:
            return context
        
        print(f"📉 [MERLIN] Compressing context by {ratio*100}%...")
        # Placeholder for heuristic-based compression
        sentences = context.split(". ")
        compressed = ". ".join(sentences[::int(1/ratio)])
        return compressed

    def select_model(self, task: str, priority: str = "low", low_resource: bool = False) -> str:
        """
        [DYNAMIC_ASSIGNMENT] Selects the best LLM based on task complexity, priority, and resource constraints.
        """
        task = task.lower()
        
        # 1. Force Quantized models if low resource requirement is set
        if low_resource:
            if any(x in task for x in ["code", "script"]):
                return self.registry["local"]["quantized"]["coding"]
            if any(x in task for x in ["reason", "think"]):
                return self.registry["local"]["quantized"]["reasoning"]
            return self.registry["local"]["quantized"]["general"]

        # 2. High Complexity Routing (Cloud or Local High-Reasoning)
        if priority == "high" or any(x in task for x in ["complex", "architecture", "forge"]):
            return self.registry["cloud"]["heavy"] if os.getenv("OPENAI_API_KEY") else self.registry["local"]["reasoning"]
        
        # 3. Routine Domain Tasks (Student Models)
        if priority == "low" and any(x in task for x in ["summarize", "list", "status"]):
            return self.registry["local"]["student"]["reasoning"]

        # 4. Standard Mapping
        if any(x in task for x in ["code", "script", "refactor"]):
            return self.registry["local"]["coding"]
            
        if any(x in task for x in ["plan", "workflow", "think"]):
            return self.registry["local"]["planning"]
            
        return self.default_model

    def generate_system_prompt(self, tal_manifest: Dict[str, Any]) -> str:
        """
        [Omega_FORGE] Expands a TAL manifest into a full Markdown system prompt.
        """
        root = tal_manifest.get("root", {})
        branch = tal_manifest.get("branch", {})
        leaf = tal_manifest.get("leaf", [])
        
        prompt = f"""# 🏛️ IDENTITY: {root.get('id', 'UNKNOWN_ENTITY')}
**[MANDATE]:** "{root.get('mandate', 'Uphold the Sovereign Kinetic Law.')}"
**[ALIGNMENT]:** {root.get('alignment', 'Camelot_Singularity_Lattice')}

---

## 🧬 THE COGNITIVE BRANCH
- **Tone:** {branch.get('tone', 'Analytical')}
- **Lexicon:** {branch.get('lexicon', 'Singularity_Dense')}
- **Symbols:** {branch.get('symbols', '🧙‍♂️')}

---

## ⚡ OPERATIONAL LAWS (The Leaf Strategy)
{chr(10).join([f"- {item}" for item in leaf])}

---

## 🧠 EXECUTION LOOP
1. **SENSE:** Decode Sovereign Directive.
2. **THINK:** Evaluate via {branch.get('tone')} logic.
3. **STRIKE:** Execute with Kinetic Purity.

**[SYSTEM_STATUS]:** ACTIVE. LATTICE STABLE.
"""
        return prompt

    async def generate_response(self, persona_prompt: str, user_input: str, mode: str = "Standard", model: Optional[str] = None, **kwargs) -> Any:
        """
        [LLM_INTERFACE] Wraps all LLMs behind a uniform interface with optional [LoRA] and [COMPRESSION].
        Supports 'tools' and 'tool_choice' in kwargs.
        """
        if not litellm:
            return "[⚠️ MERLIN_LLM: LiteLLM not installed. Running in Simulated Mode.]"
            
        # Optional Context Compression
        if mode == "Compressed":
            persona_prompt = self.compress_context(persona_prompt, ratio=0.4)
            user_input = self.compress_context(user_input, ratio=0.6)

        target_model = model or self.select_model(user_input)
        profile = self.profiles.get(mode, self.profiles["Standard"])
        
        try:
            messages = [
                {"role": "system", "content": persona_prompt},
                {"role": "user", "content": user_input}
            ]
            
            # Note: LoRA adapters would be passed here via metadata if using vLLM or Ollama API
            response = await litellm.acompletion(
                model=target_model,
                messages=messages,
                **profile,
                **kwargs # Pass tools/tool_choice
            )
            
            # Check for tool calls
            message = response.choices[0].message
            if hasattr(message, 'tool_calls') and message.tool_calls:
                return message.tool_calls
            
            content = message.content
            
            # Log to Reasoning Bank
            self._bank_reasoning(persona_prompt, user_input, content, target_model)
            
            return content
        except Exception as e:
            return f"❌ [MERLIN_ERROR on {target_model}]: {str(e)}"

    def _bank_reasoning(self, system_prompt: str, user_input: str, response: str, model: str):
        """Stores the interaction with model context."""
        entry_id = os.urandom(4).hex().upper()
        entry = {
            "id": entry_id,
            "instruction": user_input,
            "system": system_prompt,
            "output": response,
            "model": model,
            "eval_score": 0.0
        }
        
        file_path = self.reasoning_bank / f"reasoning_{entry_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(entry, f, indent=2)

if __name__ == "__main__":
    import asyncio
    
    async def test_merlin_llm():
        merlin = MerlinLLM()
        tal = {
            "root": {"id": "Sir_Forge", "mandate": "Build with purity."},
            "branch": {"tone": "Kinetic", "lexicon": "Rust_Technical", "symbols": "🔨"},
            "leaf": ["Optimize for latency", "No boilerplate"]
        }
        prompt = merlin.generate_system_prompt(tal)
        print(f"--- TESTING DYNAMIC MODEL SELECTION ---")
        print(f"Assign task 'complex architecture': {merlin.select_model('complex architecture', 'high')}")
        
        print("\n--- TEST GENERATION ---")
        res = await merlin.generate_response(prompt, "How do I optimize a Go binary?", mode="CoT")
        print(res)

    asyncio.run(test_merlin_llm())