# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
Prism Gateway - Multi-Model LLM Routing
Assimilated from CC_v32_Kingdom

Provides intelligent model selection via TheJudge deliberation system.
Features:
- Automatic Fallback (Cloud -> Local)
- Tiny Model Support (Llama 3.2 1B)
- Multimodal Frontier Defaults
"""

import asyncio
import os
from enum import Enum
from typing import Dict, List, Optional


class ModelTier(Enum):
    """Model capability tiers for routing."""

    FLASH = "flash"  # Fast, lightweight tasks (Gemini 3 Flash)
    PRO = "pro"  # Balanced performance (Gemini 3 Pro)
    TINY = "tiny"  # Ultra-fast local-only (Llama 3.2 1B / Phi-3)
    ULTRA = "ultra"  # Complex reasoning
    SPECIALIST = "specialist"  # Domain-specific (e.g., code, vision)


class TheJudge:
    """
    Intelligent model selection system with Tier-aware routing.
    """

    MODEL_REGISTRY: Dict[ModelTier, List[str]] = {
        ModelTier.FLASH: ["gemini-3-flash", "gemini-1.5-flash"],
        ModelTier.PRO: ["gemini-3-pro", "gemini-1.5-pro"],
        ModelTier.TINY: ["llama3.2:1b", "phi3:mini", "qwen2.5:1.5b"],
        ModelTier.ULTRA: ["gemini-3-pro"],
        ModelTier.SPECIALIST: ["gemini-3-pro"],
    }

    @staticmethod
    def deliberate(user_intent: str) -> str:
        """Select the champion model for the given intent."""
        intent_lower = user_intent.lower()

        # Tiny tier triggers (very short, simple commands)
        if len(user_intent) < 50 and not any(kw in intent_lower for kw in ["code", "analyze"]):
            tier = ModelTier.TINY
        # Ultra tier triggers
        elif any(kw in intent_lower for kw in ["complex", "advanced", "deep reasoning"]) or len(user_intent) > 1000:
            tier = ModelTier.ULTRA
        # Specialist tier triggers
        elif any(kw in intent_lower for kw in ["code", "debug", "refactor"]):
            tier = ModelTier.SPECIALIST
        # Pro tier triggers
        elif any(kw in intent_lower for kw in ["design", "architecture", "strategy"]):
            tier = ModelTier.PRO
        # Flash tier (default)
        else:
            tier = ModelTier.FLASH

        champion = TheJudge.MODEL_REGISTRY[tier][0]
        print(f"🌟 [JUDGE] Selected: {champion} (Tier: {tier.value})")
        return champion


class PrismAdapter:
    """
    Unified LLM communication adapter with robust Fallback (Cloud -> Local).
    """

    @staticmethod
    def _get_provider() -> str:
        return os.getenv("LLM_PROVIDER", "gemini").lower()

    @staticmethod
    def _get_client(provider: str):
        """Returns the appropriate client based on provider."""
        if provider == "gemini":
            import google.generativeai as genai

            if not os.getenv("GOOGLE_API_KEY"):
                print("⚠️ [PRISM] GOOGLE_API_KEY not found.")
                return None
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            return genai

        elif provider in ["ollama", "lm_studio"]:
            try:
                from openai import OpenAI

                base_url = os.getenv("LLM_BASE_URL")
                if not base_url:
                    base_url = "http://localhost:11434/v1" if provider == "ollama" else "http://localhost:1234/v1"
                return OpenAI(base_url=base_url, api_key=os.getenv("LLM_API_KEY", "ollama"))
            except ImportError:
                return None
        return None

    @staticmethod
    async def transmit(model: str, prompt: str, system_persona: str = "", thinking_budget: int = 0) -> Optional[str]:
        """
        Transmits prompt to LLM with automatic fallback.
        Sequence: Gemini -> Ollama (Llama 3.2 1B) -> Fail
        """
        provider = PrismAdapter._get_provider()
        providers_to_try = [provider]

        # If Gemini is primary, always add Ollama as secondary/fallback
        if provider == "gemini":
            providers_to_try.append("ollama")

        for current_provider in providers_to_try:
            try:
                print(f"📡 [PRISM] Attempting {current_provider}...")
                client = PrismAdapter._get_client(current_provider)
                if not client:
                    continue

                if current_provider == "gemini":
                    # Use provided model or default to 3 Flash
                    m_name = model if "gemini" in model else "gemini-3-flash"
                    
                    # --- THINKING CONFIG INTEGRATION ---
                    generation_config = {}
                    if thinking_budget > 0:
                        generation_config["thinking_config"] = {"include_thoughts": True, "thinking_budget": thinking_budget}

                    model_instance = client.GenerativeModel(
                        model_name=m_name, system_instruction=system_persona or None,
                        generation_config=generation_config if generation_config else None
                    )
                    response = await asyncio.to_thread(model_instance.generate_content, prompt)
                    return response.text

                elif current_provider == "ollama":
                    # Use provided model if it looks like an Ollama model, else fallback to tiny
                    local_model = model if ":" in model else os.getenv("OLLAMA_MODEL", "llama3.2:1b")
                    messages = []
                    if system_persona:
                        messages.append({"role": "system", "content": system_persona})
                    messages.append({"role": "user", "content": prompt})

                    response = await asyncio.to_thread(
                        client.chat.completions.create, model=local_model, messages=messages, temperature=0.7
                    )
                    return response.choices[0].message.content

            except Exception as e:
                print(f"⚠️ [PRISM] {current_provider} Error: {e}")
                if current_provider == providers_to_try[-1]:
                    return None
        return None

    @staticmethod
    async def stream_transmit(model: str, prompt: str, system_persona: str = "", callback=None):
        """Streaming version of transmit (fallback not fully automated in stream yet)."""
        provider = PrismAdapter._get_provider()
        try:
            client = PrismAdapter._get_client(provider)
            if not client:
                return

            if provider == "gemini":
                m_name = model if "gemini" in model else "gemini-3-flash"
                model_instance = client.GenerativeModel(model_name=m_name, system_instruction=system_persona or None)
                response = await asyncio.to_thread(model_instance.generate_content, prompt, stream=True)
                for chunk in response:
                    if callback and chunk.text:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(chunk.text)
                        else:
                            callback(chunk.text)

            elif provider == "ollama":
                local_model = model if ":" in model else os.getenv("OLLAMA_MODEL", "llama3.2:1b")
                stream = await asyncio.to_thread(
                    client.chat.completions.create,
                    model=local_model,
                    messages=[{"role": "user", "content": prompt}],
                    stream=True,
                )
                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content and callback:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(content)
                        else:
                            callback(content)
        except Exception as e:
            print(f"⚠️ [PRISM] Stream Error: {e}")