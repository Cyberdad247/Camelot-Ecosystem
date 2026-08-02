# SPDX-FileCopyrightText: 2026 Invisioned Marketing Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Chronos Haystack-UKG Plugin

Enhances Chronos memory agent with Haystack-UKG RAG capabilities.
Adds UKG semantic search alongside existing LightRAG engine.

Architecture:
    User Query → Chronos → [LightRAG | HaystackUKG] → Merged Results
    
Usage:
    >>> from kernel.rag.chronos_haystack import ChronosHaystackNode
    >>> chronos = ChronosHaystackNode()
    >>> await chronos.start()
"""

import logging
from typing import Any, Dict

from kernel.agora.node import AgentNode
from kernel.agora.protocol import ANPEnvelope

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChronosHaystackNode(AgentNode):
    """
    Enhanced Chronos Node with Haystack-UKG integration.
    
    Provides dual memory:
    1. LightRAG: Real-time session memory and chat history
    2. Haystack-UKG: Long-term knowledge graph (38,742 nodes)
    
    Query Routing:
    - Knowledge questions → Haystack-UKG (e.g., "What is the Septem Regna?")
    - Session context → LightRAG (e.g., "What did I ask 5 minutes ago?")
    - Hybrid mode → Both engines, merge results
    """
    
    def __init__(self, enable_haystack: bool = True, enable_lightrag: bool = True):
        """
        Initialize Chronos with optional dual memory.
        
        Args:
            enable_haystack: Enable Haystack-UKG knowledge graph retrieval
            enable_lightrag: Enable LightRAG session memory
        """
        super().__init__("CHRONOS_HAYSTACK")
        self.identity = "Chronos_DualMemory"
        
        # LightRAG engine (existing)
        self.lightrag = None
        if enable_lightrag:
            try:
                from kernel.rag.lightrag_engine import get_lightrag_engine
                self.lightrag = get_lightrag_engine()
                logger.info("✅ LightRAG engine initialized")
            except Exception as e:
                logger.warning(f"⚠️ LightRAG init failed: {e}")
        
        # Haystack-UKG bridge (new)
        self.haystack_ukg = None
        if enable_haystack:
            try:
                from integrations.haystack_ukg_bridge import HaystackUKGBridge
                self.haystack_ukg = HaystackUKGBridge()
                logger.info("✅ Haystack-UKG bridge initialized")
            except Exception as e:
                logger.warning(f"⚠️ Haystack-UKG init failed: {e}")
        
        # Load Persona (Phase 2 Integration)
        self.persona = None
        try:
            import json
            with open("03_VAULT/UKG/MERLIN_PERSONA.jsonld", 'r', encoding='utf-8') as f:
                self.persona = json.load(f)
                logger.info(f"🧬 Loaded Persona: {self.persona.get('identity_hash')}")
        except FileNotFoundError:
            logger.info("ℹ️ No persona profile found (defaulting to Standard mode)")
        except Exception as e:
            logger.warning(f"⚠️ Persona load failed: {e}")

    async def receive(self, envelope: ANPEnvelope) -> None:
        """
        Handle incoming memory requests.
        
        Protocols:
            - Query: Semantic Search (dual engine)
            - Index: Store observation (to LightRAG)
            - UKG_Query: Direct UKG knowledge graph query
        """
        sender = envelope.sender
        protocol = envelope.protocol
        payload = envelope.payload
        
        logger.info(f"📜 [CHRONOS_HAYSTACK] Received {protocol} from {sender}")
        
        from kernel.agora.router import AgoraRouter
        router = AgoraRouter()
        
        # Protocol routing
        if protocol == "Query":
            await self._handle_query(router, sender, payload)
        
        elif protocol == "Index":
            await self._handle_index(router, sender, payload)
        
        elif protocol == "UKG_Query":
            await self._handle_ukg_query(router, sender, payload)
        
        else:
            logger.warning(f"⚠️ Unknown protocol: {protocol}")
            await self.send(
                router, sender, "Error", 
                {"message": f"Unsupported protocol: {protocol}"}
            )
    
    async def _handle_query(self, router, sender: str, payload: Dict[str, Any]):
        """
        Dual-engine query handler.
        
        Strategy:
        1. Query both LightRAG and Hay stack-UKG
        2. Merge results (dedup by content hash)
        3. Return combined ranked results
        """
        query_text = payload.get("query", "")
        mode = payload.get("mode", "hybrid")  # "hybrid", "lightrag", "ukg"
        top_k = payload.get("top_k", 5)
        
        results = []
        
        # LightRAG query (session memory)
        if mode in ["hybrid", "lightrag"] and self.lightrag:
            try:
                lightrag_results = self.lightrag.query(query_text)
                results.extend([
                    {
                        "content": r.content,
                        "score": r.score,
                        "metadata": {**r.metadata, "source_engine": "LightRAG"},
                    }
                    for r in lightrag_results.results
                ])
                logger.info(f"🔍 LightRAG found {len(lightrag_results.results)} results")
            except Exception as e:
                logger.error(f"❌ LightRAG query failed: {e}")
        
        # Haystack-UKG query (knowledge graph)
        if mode in ["hybrid", "ukg"] and self.haystack_ukg:
            try:
                ukg_response = self.haystack_ukg.query(
                    question=query_text,
                    top_k=top_k,
                    generator_model="merlin"
                )
                
                # Add UKG documents to results
                results.extend([
                    {
                        "content": doc["content"],
                        "score": doc.get("score", 0.5),  # BM25 score
                        "metadata": {
                            "source": doc["source"],
                            "source_engine": "Haystack-UKG"
                        }
                    }
                    for doc in ukg_response["documents"]
                ])
                
                logger.info(f"🔍 Haystack-UKG found {len(ukg_response['documents'])} results")
                
                # If Merlin generated an answer, include it
                if ukg_response.get("answer"):
                    results.insert(0, {
                        "content": ukg_response["answer"],
                        "score": 1.0,  # Highest priority
                        "metadata": {
                            "type": "generated_answer",
                            "source_engine": "Merlin (via Haystack-UKG)",
                            "generator_meta": ukg_response["metadata"].get("generator_meta", {})
                        }
                    })
                    logger.info("✅ Merlin-generated answer included")
            
            except Exception as e:
                logger.error(f"❌ Haystack-UKG query failed: {e}")
        
        # Rank and merge (simple: sort by score, take top_k)
        results.sort(key=lambda x: x["score"], reverse=True)
        results = results[:top_k]
        
        # Send back to requester
        await self.send(router, sender, "Result", {
            "results": results,
            "total": len(results),
            "query": query_text,
            "mode": mode
        })
        
        logger.info(f"✅ Returned {len(results)} results to {sender}")
    
    async def _handle_index(self, router, sender: str, payload: Dict[str, Any]):
        """
        Index content to LightRAG (session memory).
        
        Note: UKG is read-only (static knowledge graph).
        """
        if not self.lightrag:
            await self.send(router, sender, "Error", {
                "message": "LightRAG not available. Cannot index."
            })
            return
        
        content = payload.get("content", "")
        metadata = payload.get("metadata", {})
        
        try:
            res = self.lightrag.index(content, metadata)
            
            await self.send(router, sender, "ACK", {
                "doc_id": res.doc_id,
                "status": "indexed" if res.success else "failed"
            })
            
            logger.info(f"✅ Indexed document {res.doc_id}")
        
        except Exception as e:
            logger.error(f"❌ Indexing failed: {e}")
            await self.send(router, sender, "Error", {
                "message": f"Indexing failed: {str(e)}"
            })
    
    async def _handle_ukg_query(self, router, sender: str, payload: Dict[str, Any]):
        """
        Direct UKG knowledge graph query (bypass LightRAG).
        
        Use this for:
        - Architecture questions
        - Knowledge graph traversal
        - Historical context retrieval
        """
        if not self. haystack_ukg:
            await self.send(router, sender, "Error", {
                "message": "Haystack-UKG not available."
            })
            return
        
        question = payload.get("question", "")
        top_k = payload.get("top_k", 5)
        
        try:
            # Recursive Search (Phase 3)
            final_docs = None
            if self.persona and "Deep" in self.persona.get("reasoning_style", ""):
                try:
                    from rag.recursive_search import ReflectionEngine
                    reflector = ReflectionEngine()
                    
                    # 1. Initial Retrieval
                    docs_1 = self.haystack_ukg.retrieve_documents(question, top_k=top_k)
                    
                    # 2. Reflect & Critique
                    critique = reflector.evaluate_coverage(question, docs_1)
                    
                    if critique["needs_recursion"]:
                        logger.info(f"🔄 Reflection: {critique['missing']} -> Triggering Recursion")
                        follow_up = reflector.generate_followup(question, critique["missing"])
                        
                        # 3. Recursive Retrieval
                        docs_2 = self.haystack_ukg.retrieve_documents(follow_up, top_k=top_k)
                        
                        # 4. Merge & Dedupe
                        seen = {d.id for d in docs_1}
                        final_docs = docs_1 + [d for d in docs_2 if d.id not in seen]
                        logger.info(f"✅ Merged {len(docs_1)} initial + {len(docs_2)} recursive docs -> {len(final_docs)} total")
                    else:
                        final_docs = docs_1
                except Exception as e:
                    logger.warning(f"⚠️ Recursive Search failed: {e}")
                    final_docs = None

            # Construct Persona-aware prompt (Phase 2)
            prompt_tmpl = None
            if self.persona:
                style = self.persona.get("reasoning_style", "Standard")
                prompt_tmpl = f"[IDENTITY: MERLIN] [STYLE: {style}]\n\nContext:\n{{documents}}\n\nUser Query: {{query}}\n\nResponse:"

            response = self.haystack_ukg.query(
                question=question,
                top_k=top_k,
                generator_model="merlin",
                prompt_template=prompt_tmpl,
                documents=final_docs
            )
            
            await self.send(router, sender, "UKG_Result", response)
            
            logger.info(f"✅ UKG query returned {len(response['documents'])} docs")
        
        except Exception as e:
            logger.error(f"❌ UKG query failed: {e}")
            await self.send(router, sender, "Error", {
                "message": f"UKG query failed: {str(e)}"
            })


def test_chronos_haystack():
    """Test dual-engine memory query."""
    import asyncio
    
    async def run_test():
        # Initialize node
        chronos = ChronosHaystackNode(enable_haystack=True, enable_lightrag=False)
        
        # Simulate query from Merlin
        from kernel.agora.protocol import ANPEnvelope
        from kernel.agora.router import AgoraRouter
        
        router = AgoraRouter()
        router.register(chronos)
        
        envelope = ANPEnvelope(
            sender="MERLIN_TEST",
            receiver="CHRONOS_HAYSTACK",
            protocol="UKG_Query",
            payload={
                "question": "What is the Septem Regna architecture?",
                "top_k": 3
            }
        )
        
        await chronos.receive(envelope)
    
    asyncio.run(run_test())
    print("✅ Test complete. Check logs above.")


if __name__ == "__main__":
    test_chronos_haystack()
