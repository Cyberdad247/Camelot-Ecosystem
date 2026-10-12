# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import hashlib
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field

# --- CANONICAL UNITS (v2.0 - Symmetry Sync) ---

MemoryType = Literal[
    "persona", "skill", "fact", "pattern", "glyph", "event", "preference", "project", "constraint", "log", "task"
]
MemorySource = Literal["user", "system", "agent", "inferred"]


class MemoryNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str  # Namespacing
    type: MemoryType
    content: str
    tags: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    source: MemorySource = "user"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: datetime | None = None
    content_hash: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def __init__(self, **data):
        super().__init__(**data)
        if not self.content_hash:
            # Hash includes agent_id to allow same fact in different agent contexts
            hash_input = f"{self.agent_id}:{self.content.lower().strip()}"
            self.content_hash = hashlib.sha256(hash_input.encode()).hexdigest()


class AgentMemoryStore(BaseModel):
    """
    Anya's Reusable Agent Template
    Stores Working Memory (Active) and Long-Term Memory (Canonical)
    """

    agent_id: str
    persona_core: Dict[str, str] = Field(default_factory=dict)

    # The 3 Planes
    ephemeral_buffer: List[str] = Field(default_factory=list)  # L1 (RAM/Session)
    working_set: List[MemoryNode] = Field(default_factory=list)  # L2 (Short-term Persistence)
    long_term: List[MemoryNode] = Field(default_factory=list)  # L3 (Canonical/Vault)

    max_working_size: int = 50

    def promote(self, node_id: str):
        """Move working memory into long-term memory (Cognitive Hardening)"""
        for i, node in enumerate(self.working_set):
            if node.id == node_id:
                target = self.working_set.pop(i)
                self.long_term.append(target)
                return True
        return False

    def add_working(self, node: MemoryNode):
        all_hashes = {m.content_hash for m in self.working_set + self.long_term}
        if node.content_hash in all_hashes:
            return False

        self.working_set.append(node)
        if len(self.working_set) > self.max_working_size:
            self.working_set.pop(0)
        return True

    def recall(self, query: str = None, m_type: MemoryType = None, limit: int = 12) -> List[MemoryNode]:
        # Simple similarity would go here. For now, we merge and sort by confidence/recency.
        pool = self.long_term + self.working_set

        if m_type:
            pool = [m for m in pool if m.type == m_type]

        # In v2, we'd use embeddings. For v1, we do keyword match or just recency.
        if query:
            pool = [m for m in pool if query.lower() in m.content.lower()]

        pool.sort(key=lambda x: (x.confidence, x.created_at), reverse=True)

        results = pool[:limit]
        for m in results:
            m.last_accessed = datetime.utcnow()
        return results


# --- KERNEL ENGINE ---


class SovereignMemoryEngine:
    """The Memory Spine - Git for Cognition"""

    def __init__(self, agent_id: str, persona_core: Dict[str, str] = None, storage_dir: str = "03_VAULT/MEMORIES"):
        self.agent_id = agent_id
        os.makedirs(storage_dir, exist_ok=True)
        self.storage_path = os.path.join(storage_dir, f"{agent_id.lower()}_spine.json")
        self.store = self._load(persona_core)

    def _load(self, persona_core: Dict[str, str] = None) -> AgentMemoryStore:
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r") as f:
                return AgentMemoryStore.model_validate_json(f.read())
        return AgentMemoryStore(agent_id=self.agent_id, persona_core=persona_core or {})

    def save(self):
        with open(self.storage_path, "w") as f:
            f.write(self.store.model_dump_json(indent=2))

    def observe(self, content: str, m_type: MemoryType, confidence: float = 0.8, source: MemorySource = "inferred"):
        node = MemoryNode(agent_id=self.agent_id, type=m_type, content=content, confidence=confidence, source=source)
        if self.store.add_working(node):
            self.save()
            return node
        return None

    def get_context(self) -> str:
        relevant = self.store.recall(limit=15)
        if not relevant:
            return ""

        lines = [f"[{self.agent_id}_COGNITIVE_RECALL]:"]
        for m in relevant:
            plane = "L3" if m in self.store.long_term else "L2"
            lines.append(f"- ({plane}:{m.type}) {m.content}")
        return "\n".join(lines)