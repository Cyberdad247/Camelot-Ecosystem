# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# SPDX-FileCopyrightText: 2026 Invisioned Marketing Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Merlin Generator for Haystack

Integrates Camelot's native Merlin LLM engine with Haystack's RAG pipeline.
Replaces the OpenAI generator stub with Merlin-native answer generation.

Architecture:
    Haystack Pipeline → MerlinGenerator → MerlinLLM.generate_response()
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

# Haystack imports
try:
    from haystack import Document, component
    from haystack.dataclasses import StreamingChunk  # noqa: F401
    HAYSTACK_AVAILABLE = True
except ImportError:
    HAYSTACK_AVAILABLE = False
    # Stub for type hints
    def component(cls): return cls
    class Document: pass

# Merlin engine import
try:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent / "Engines"))
    from merlin_llm import MerlinLLM
    MERLIN_AVAILABLE = True
except ImportError:
    MERLIN_AVAILABLE = False
    MerlinLLM = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@component
class MerlinGenerator:
    """
    Haystack RAG Generator powered by Camelot's Merlin LLM.
    
    Replaces OpenAI/Anthropic generators with Merlin-native answer generation.
    Supports all Merlin profiles (CoT, Standard, Compressed, etc.).
    
    Usage:
        >>> from merlin_haystack_generator import MerlinGenerator
        >>> generator = MerlinGenerator(mode="CoT")
        >>> result = generator.run(
        ...     prompt="Answer: {{documents}}\\n\\nQuestion: {{query}}",
        ...     documents=[doc1, doc2],
        ...     query="What is the empire map?"
        ... )
        >>> print(result['reply'])
    """
    
    def __init__(
        self,
        mode: str = "Standard",
        model: Optional[str] = None,
        system_prompt: Optional[str] = None
    ):
        """
        Initialize Merlin generator.
        
        Args:
            mode: Merlin profile ("CoT", "Standard", "Compressed", "Creative", "JSON")
            model: Override model selection (e.g., "ollama/deepseek-r1:8b")
            system_prompt: Optional system prompt (defaults to Merlin sovereign prompt)
        """
        if not HAYSTACK_AVAILABLE:
            raise ImportError("Haystack not installed. Install: pip install haystack-ai")
        
        if not MERLIN_AVAILABLE:
            raise ImportError(
                "MerlinLLM not available. Check: 01_KERNEL/Engines/merlin_llm.py"
            )
        
        self.merlin = MerlinLLM()
        self.mode = mode
        self.model = model
        
        # Default Merlin system prompt (Sovereign-aligned)
        self.system_prompt = system_prompt or """# 🏛️ IDENTITY: MERLIN (RAG Assistant)
**[MANDATE]:** "Answer questions using retrieved knowledge context."
**[ALIGNMENT]:** Camelot_OS_Singularity

## ⚡ OPERATIONAL LAWS
- Base answers ONLY on provided documents
- Cite sources when possible
- If documents don't contain the answer, say "Information not available in context"
- Be concise but comprehensive
- Maintain Camelot's kinetic purity (no speculation beyond context)

**[SYSTEM_STATUS]:** ACTIVE. RAG MODE.
"""
        
        logger.info(f"🧙‍♂️ MerlinGenerator initialized (Mode: {mode})")
    
    @component.output_types(replies=List[str], meta=List[Dict[str, Any]])
    def run(
        self,
        prompt: str,
        generation_kwargs: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate answer using Merlin LLM.
        
        Args:
            prompt: Template string with {{variables}} placeholders
            generation_kwargs: Additional generation parameters (unused, for compatibility)
            **kwargs: Template variables (e.g., documents, query, question)
        
        Returns:
            Dictionary with:
                - replies: List of generated answers
                - meta: List of metadata dictionaries
        """
        # Inject template variables into prompt
        rendered_prompt = prompt
        for key, value in kwargs.items():
            placeholder = f"{{{{{key}}}}}"  # {{variable}} format
            
            # Special handling for documents list
            if key == "documents" and isinstance(value, list):
                docs_text = self._format_documents(value)
                rendered_prompt = rendered_prompt.replace(placeholder, docs_text)
            else:
                rendered_prompt = rendered_prompt.replace(placeholder, str(value))
        
        logger.info(f"🔮 Merlin generating answer (Mode: {self.mode})...")
        logger.debug(f"Prompt length: {len(rendered_prompt)} chars")
        
        # Call Merlin LLM (async wrapper)
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            response = loop.run_until_complete(
                self.merlin.generate_response(
                    persona_prompt=self.system_prompt,
                    user_input=rendered_prompt,
                    mode=self.mode,
                    model=self.model
                )
            )
            
            loop.close()
            
            logger.info(f"✅ Merlin response generated ({len(response)} chars)")
            
            return {
                "replies": [response],
                "meta": [{
                    "model": self.model or self.merlin.default_model,
                    "mode": self.mode,
                    "length": len(response)
                }]
            }
            
        except Exception as e:
            logger.error(f"❌ Merlin generation failed: {e}")
            
            # Fallback response
            return {
                "replies": [f"[Merlin Error: {str(e)}]"],
                "meta": [{"error": str(e)}]
            }
    
    def _format_documents(self, documents: List[Document]) -> str:
        """
        Format Haystack Documents into readable context for Merlin.
        
        Args:
            documents: List of Haystack Document objects
        
        Returns:
            Formatted string with numbered documents
        """
        formatted = []
        
        for idx, doc in enumerate(documents, 1):
            # Extract content and metadata
            content = doc.content if hasattr(doc, 'content') else str(doc)
            source = ""
            
            if hasattr(doc, 'meta') and doc.meta:
                source_name = doc.meta.get('source', 'Unknown')
                source = f" [Source: {source_name}]"
            
            formatted.append(f"Document {idx}{source}:\n{content}")
        
        return "\n\n".join(formatted)


# Convenience function for quick testing
def test_merlin_generator():
    """Test Merlin generator with sample documents."""
    from haystack import Document
    
    # Sample documents
    docs = [
        Document(
            content="The Septem Regna is a 7-layer sovereign stack in Camelot OS.",
            meta={"source": "ARCHITECTURE.md"}
        ),
        Document(
            content="Layer 3 is Merlin, the Neural routing layer with Videneptus LaC.",
            meta={"source": "EMPIRE_MAP.md"}
        )
    ]
    
    # Initialize generator
    generator = MerlinGenerator(mode="CoT")
    
    # Generate answer
    result = generator.run(
        prompt="Based on these documents:\n\n{{documents}}\n\nQuestion: {{query}}",
        documents=docs,
        query="What is the Septem Regna and where is Merlin located?"
    )
    
    print("=" * 60)
    print("MERLIN GENERATOR TEST")
    print("=" * 60)
    print("\nQuery: What is the Septem Regna?")
    print(f"\nMerlin Response:\n{result['replies'][0]}")
    print(f"\nMetadata: {result['meta'][0]}")


if __name__ == "__main__":
    test_merlin_generator()
