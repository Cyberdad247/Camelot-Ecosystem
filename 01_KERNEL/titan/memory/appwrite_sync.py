# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import os
from datetime import datetime
from typing import List

from appwrite.client import Client
from appwrite.query import Query
from appwrite.services.databases import Databases

from .base_memory import AgentMemoryStore, MemoryNode


class AppwriteMemoryBridge:
    """
    Synchronizes local Memory Spine with the Appwrite Fortress.
    Implements the Canonical Memory Store logic.
    """

    def __init__(self):
        self._init_client()
        self.database_id = os.getenv("APPWRITE_DB_ID", "sovereign_db")
        self.collection_id = os.getenv("APPWRITE_COLLECTION_ID", "memory_spine")

    def _init_client(self):
        self.client = Client()
        self.client.set_endpoint(os.getenv("APPWRITE_ENDPOINT"))
        self.client.set_project(os.getenv("APPWRITE_PROJECT_ID"))
        self.client.set_key(os.getenv("APPWRITE_API_KEY"))
        self.db = Databases(self.client)

    def push_node(self, node: MemoryNode):
        """Push a single MemoryNode to Appwrite (The Write Path)"""
        try:
            data = node.model_dump(mode="json")
            # Appwrite specific adjustments
            data["created_at"] = node.created_at.isoformat()
            if node.last_accessed:
                data["last_accessed"] = node.last_accessed.isoformat()

            # Use content_hash as document ID to ensure deduplication at the DB level
            self.db.create_document(
                self.database_id, self.collection_id, node.content_hash[:36], data  # Appwrite ID limit
            )
            return True
        except Exception as e:
            # If document exists, we might want to update last_accessed
            if "already exists" in str(e).lower():
                try:
                    self.db.update_document(
                        self.database_id,
                        self.collection_id,
                        node.content_hash[:36],
                        {"last_accessed": datetime.utcnow().isoformat()},
                    )
                    return True
                except:
                    pass
            print(f"Appwrite Sync Error: {e}")
            return False

    def pull_long_term(self, agent_id: str) -> List[MemoryNode]:
        """Fetch long-term memory for an agent (The Read Path)"""
        try:
            result = self.db.list_documents(
                self.database_id,
                self.collection_id,
                queries=[Query.equal("agent_id", agent_id), Query.order_desc("confidence"), Query.limit(100)],
            )
            nodes = []
            for doc in result["documents"]:
                # Clean up Appwrite system fields before Pydantic validation
                doc_data = {k: v for k, v in doc.items() if not k.startswith("$")}
                nodes.append(MemoryNode.model_validate(doc_data))
            return nodes
        except Exception as e:
            print(f"Appwrite Pull Error: {e}")
            return []

    def sync_store(self, store: AgentMemoryStore):
        """Full bi-directional sync (Working set -> Appwrite -> Long term)"""
        # 1. Push new working nodes
        for node in store.working_set:
            self.push_node(node)

        # 2. Pull updated long-term nodes
        cloud_nodes = self.pull_long_term(store.agent_id)

        # 3. Merge (Simple overwrite for now, in v2 use conflict rules)
        existing_hashes = {m.content_hash for m in store.long_term}
        for cn in cloud_nodes:
            if cn.content_hash not in existing_hashes:
                store.long_term.append(cn)

        return store