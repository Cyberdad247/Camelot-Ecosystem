# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — Graphiti Temporal Knowledge Graph Engine
r"""
Knight-partitioned temporal knowledge graph engine based on Graphiti / Zep architecture.
Maintains temporal entity-relation-fact triplets with valid_at and expired_at intervals,
enabling historical time-travel analysis, entity resolution, and targeted subgraph extraction.
Reduces LLM token consumption by retrieving precise subgraph facts instead of raw documents.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("camelot.graphiti")

CAMELOT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(CAMELOT_ROOT))
sys.path.insert(0, str(CAMELOT_ROOT / "01_KERNEL"))
DEFAULT_GRAPHITI_VAULT = CAMELOT_ROOT / "03_VAULT" / "memory" / "graphiti"


class KnightGraphitiEngine:
    """Temporal Knowledge Graph engine partitioned per Knight of the Round Table."""

    def __init__(self, knight_id: str, vault_dir: Optional[Path] = None):
        self.knight_id = knight_id.upper()
        self.vault_dir = Path(vault_dir) if vault_dir else DEFAULT_GRAPHITI_VAULT
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.vault_dir / f"{self.knight_id.lower()}_graphiti.db"
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    summary TEXT,
                    attributes TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name);
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS temporal_facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject TEXT NOT NULL,
                    predicate TEXT NOT NULL,
                    object TEXT NOT NULL,
                    valid_at TEXT NOT NULL,
                    expired_at TEXT,
                    confidence REAL DEFAULT 1.0,
                    source TEXT,
                    metadata TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_facts_subject ON temporal_facts(subject);
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_facts_object ON temporal_facts(object);
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_facts_predicate ON temporal_facts(predicate);
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_facts_validity ON temporal_facts(valid_at, expired_at);
            """)
            conn.commit()

    def add_entity(
        self,
        name: str,
        category: str = "concept",
        summary: str = "",
        attributes: Optional[Dict[str, Any]] = None,
    ) -> str:
        now_iso = datetime.now(timezone.utc).isoformat()
        entity_id = f"{self.knight_id}:{name.lower().replace(' ', '_')}"
        attrs_json = json.dumps(attributes or {})
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO entities (id, name, category, summary, attributes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    category=excluded.category,
                    summary=CASE WHEN excluded.summary != '' THEN excluded.summary ELSE entities.summary END,
                    attributes=excluded.attributes,
                    updated_at=excluded.updated_at
            """, (entity_id, name, category, summary, attrs_json, now_iso, now_iso))
            conn.commit()
        return entity_id

    def add_fact(
        self,
        subject: str,
        predicate: str,
        object_: str,
        valid_at: Optional[str] = None,
        expired_at: Optional[str] = None,
        confidence: float = 1.0,
        source: str = "local",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        now_iso = datetime.now(timezone.utc).isoformat()
        valid_str = valid_at or now_iso
        meta_json = json.dumps(metadata or {})
        with self._get_conn() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO temporal_facts (subject, predicate, object, valid_at, expired_at, confidence, source, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (subject, predicate, object_, valid_str, expired_at, confidence, source, meta_json, now_iso))
            fact_id = cur.lastrowid
            conn.commit()
        return fact_id

    def query_subgraph(
        self,
        entity_name: str,
        as_of: Optional[str] = None,
        depth: int = 1,
        limit: int = 25,
    ) -> Dict[str, Any]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            entity_row = cur.execute(
                "SELECT * FROM entities WHERE name = ? COLLATE NOCASE OR id = ?",
                (entity_name, entity_name)
            ).fetchone()
            
            ent_data = dict(entity_row) if entity_row else {"name": entity_name, "category": "unknown"}
            
            query = """
                SELECT * FROM temporal_facts
                WHERE (subject = ? COLLATE NOCASE OR object = ? COLLATE NOCASE)
            """
            params: List[Any] = [entity_name, entity_name]

            if as_of:
                query += " AND valid_at <= ? AND (expired_at IS NULL OR expired_at > ?)"
                params.extend([as_of, as_of])

            query += " ORDER BY valid_at DESC LIMIT ?"
            params.append(limit)

            rows = cur.execute(query, params).fetchall()
            facts = [dict(r) for r in rows]

            return {
                "knight_id": self.knight_id,
                "queried_entity": entity_name,
                "entity_info": ent_data,
                "temporal_facts_count": len(facts),
                "facts": facts,
            }

    def stats(self) -> Dict[str, Any]:
        with self._get_conn() as conn:
            cur = conn.cursor()
            ent_count = cur.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
            facts_count = cur.execute("SELECT COUNT(*) FROM temporal_facts").fetchone()[0]
            db_size_bytes = self.db_path.stat().st_size if self.db_path.exists() else 0
            return {
                "knight_id": self.knight_id,
                "db_path": str(self.db_path),
                "entities": ent_count,
                "temporal_facts": facts_count,
                "size_bytes": db_size_bytes,
            }


def forge_graphiti_for_all_knights(verbose: bool = True) -> Dict[str, Dict[str, Any]]:
    """Instantiate Graphiti temporal knowledge graph for every Round Table Knight and seed initial domain ontology."""
    from memory.cloudbrain_connector import KNIGHT_NOTEBOOKS, NOTEBOOK_DOMAIN_TAGS
    
    results: Dict[str, Dict[str, Any]] = {}
    
    for knight_id, notebook_uuid in KNIGHT_NOTEBOOKS.items():
        engine = KnightGraphitiEngine(knight_id=knight_id)
        
        engine.add_entity(
            name=knight_id,
            category="knight_agent",
            summary=f"Round Table Knight {knight_id} tethered to CloudBrain node {notebook_uuid}",
            attributes={"notebook_uuid": notebook_uuid, "tether": "worldtree"},
        )
        
        tags = NOTEBOOK_DOMAIN_TAGS.get(knight_id, ["general", "camelot_kernel"])
        for tag in tags:
            tag_ent = tag.title()
            engine.add_entity(name=tag_ent, category="domain_specialization")
            engine.add_fact(
                subject=knight_id,
                predicate="specializes_in",
                object_=tag_ent,
                confidence=1.0,
                source="cloudbrain_ontology",
            )
            
        engine.add_fact(
            subject=knight_id,
            predicate="tethers_to_cloudbrain_node",
            object_=notebook_uuid,
            confidence=1.0,
            source="cloudbrain_registry",
        )
        
        results[knight_id] = engine.stats()
        if verbose:
            logger.info(f"[GRAPHITI_FORGE] {knight_id} -> {results[knight_id]['temporal_facts']} facts seeded.")
            
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("--- Forging Graphiti Temporal Knowledge Graphs for all Knights ---")
    res = forge_graphiti_for_all_knights(verbose=False)
    print(f"Successfully forged and seeded Graphiti databases for {len(res)} Knights.")
    example = KnightGraphitiEngine("HERMES_PRIME").query_subgraph("HERMES_PRIME")
    print(f"Hermes Prime Subgraph Sample: {len(example['facts'])} facts found.")
