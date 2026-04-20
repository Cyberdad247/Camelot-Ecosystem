# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
try:
    from agora.node import AgentNode
    from agora.protocol import ANPEnvelope
except ImportError:
    from kernel.agora.node import AgentNode
    from kernel.agora.protocol import ANPEnvelope

try:
    from rag.lightrag_engine import get_lightrag_engine
except ImportError:
    from kernel.rag.lightrag_engine import get_lightrag_engine


class ChronosNode(AgentNode):
    """
    Chronos Node: The Persistent Memory Agent.
    Wraps LightRAGEngine and listens on the Agora for Query/Index tasks.
    """

    def __init__(self):
        super().__init__("CHRONOS")  # Agora ID
        self.engine = get_lightrag_engine()
        self.identity = "Chronos_Memory"

    async def receive(self, envelope: ANPEnvelope) -> None:
        """
        Handle incoming memory requests.
        Protocols:
        - QUERY: Semantic Search
        - INDEX: Store observation
        """
        sender = envelope.sender
        protocol = envelope.protocol
        payload = envelope.payload

        print(f"📜 [CHRONOS] Received {protocol} from {sender}")

        from kernel.agora.router import AgoraRouter

        router = AgoraRouter()

        if protocol == "Query":
            query_text = payload.get("query", "")
            results = self.engine.query(query_text)

            # Format results for the requester
            data = {
                "results": [{"content": r.content, "score": r.score, "metadata": r.metadata} for r in results.results],
                "total": results.total_results,
            }
            await self.send(router, sender, "Result", data)

        elif protocol == "Index":
            content = payload.get("content", "")
            metadata = payload.get("metadata", {})

            # Index the document
            res = self.engine.index(content, metadata)

            await self.send(
                router, sender, "ACK", {"doc_id": res.doc_id, "status": "indexed" if res.success else "failed"}
            )