# -*- coding: utf-8 -*-
"""
Hydration Manager — Tiered Context Protocol (L4 Semantic)
========================================================
Manages context mounting across Flash (L0), Structured (L1), and Raw (L2) tiers.
Enforces the 8GB RAM Law and maintains Kinetic Purity.

Pipeline Mapping:
- Flash (L0):      Local Storage (SQLite)
- Short-Term (L1): Local Redis (dark-store fallback)
- Agent (L1.5):    Redis Agent Memory — session + semantic long-term (cloud, MP2P7SN8)
- Long-Term (L2):  NotebookLM (Cloud Brain)
"""

import sqlite3
import json
import psutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Dict

from .cloudbrain_connector import CloudBrainConnector
from .redis_store import redis_store

try:
    from .agent_memory import agent_memory as _agent_memory
except Exception:
    _agent_memory = None

RAM_LAW_LIMIT_GB = 8.0
PROVENANCE_LEDGER = Path("C:/Users/vizio/CAMELOT_OS/PROVENANCE_LEDGER.md")

class HydrationManager:
    """Tiered Context Manager for Camelot OS."""

    def __init__(self, storage_dir: Optional[Path] = None, knight_id: str = "SIR_BORIS"):
        self.root = Path("C:/Users/vizio/CAMELOT_OS")
        self.storage_dir = storage_dir or self.root / "01_KERNEL" / "memory" / "tissue"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        # L0 Flash Storage (Local Disk/SQLite)
        self.l0_db_path = self.storage_dir / "flash_context.toon"
        self.knight_id = knight_id
        self.cloudbrain = CloudBrainConnector(knight_id=self.knight_id)
        self._init_l0_storage()

    def _init_l0_storage(self):
        """Initialize L0 SQLite storage (Local Flash)."""
        conn = sqlite3.connect(self.l0_db_path)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS flash_tissue (
                    id TEXT PRIMARY KEY,
                    intent TEXT,
                    content TEXT,
                    complexity INTEGER,
                    timestamp TEXT
                )
            """)
            conn.commit()
        finally:
            conn.close()

    def _log_provenance(self, event_type: str, details: str, status: str = "HYDRATED"):
        """Log event to the Provenance Ledger in Kinetic Purity format."""
        timestamp = datetime.now(timezone.utc).isoformat()
        log_entry = f"| {timestamp} | HYDRATION_MGR | {event_type} [{details}] | {status} |\n"
        try:
            with open(PROVENANCE_LEDGER, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Failed to log to provenance: {e}")

    def check_ram_law(self) -> bool:
        """Verify RAM usage is below the 8GB limit."""
        mem = psutil.virtual_memory()
        used_gb = mem.used / (1024**3)
        return used_gb < RAM_LAW_LIMIT_GB

    def hydrate_context(self, intent: str, complexity: int) -> Dict[str, Any]:
        """
        Hydrate context based on Tiered Context Protocol.
        L0 (Flash): Local Storage
        L1 (Short-Term): Redis
        L2 (Long-Term): NotebookLM
        """
        results = {"tiers_active": []}
        
        # L0: Flash (Local SQLite)
        if complexity >= 1:
            conn = sqlite3.connect(self.l0_db_path)
            try:
                cursor = conn.execute(
                    "SELECT content FROM flash_tissue WHERE intent = ? ORDER BY timestamp DESC LIMIT 1",
                    (intent,)
                )
                row = cursor.fetchone()
                if row:
                    try:
                        results["L0"] = json.loads(row[0])
                        results["tiers_active"].append("L0_LOCAL")
                    except (json.JSONDecodeError, TypeError):
                        # Fallback: Treat as raw text if JSON parsing fails
                        results["L0"] = row[0]
                        results["tiers_active"].append("L0_LOCAL_RAW")
            finally:
                conn.close()

        # L1: Short-Term (local Redis)
        if complexity >= 4:
            hits = redis_store.search(collection=f"intent:{intent}", vector=[1.0], limit=1)
            if hits:
                results["L1"] = hits[0].get("payload")
                results["tiers_active"].append("L1_REDIS")

        # L1.5: Redis Agent Memory — semantic long-term recall (cloud, MP2P7SN8)
        if complexity >= 4 and _agent_memory and _agent_memory.is_configured():
            recalled = _agent_memory.recall(intent, top_k=3)
            if recalled:
                results["L1_5"] = recalled
                results["tiers_active"].append("L1_5_AGENT_MEMORY")
                self._log_provenance("L1_5_AGENT_RECALL", f"Intent: {intent}, hits={len(recalled)}")

        # L2: Long-Term (NotebookLM)
        if complexity >= 8:
            if self.check_ram_law():
                # Query NotebookLM Cloud Brain for context burst
                cb_context = self.cloudbrain.query_notebook(intent)
                if cb_context:
                    results["L2"] = f"Cloud Brain Burst: {cb_context}"
                    results["tiers_active"].append("L2_CLOUD")
                    self._log_provenance("L2_CLOUD_MOUNT", f"Intent: {intent}, Complexity: {complexity}")
                else:
                    results["L2"] = f"NotebookLM query yielded no results for {intent}"
                    results["tiers_active"].append("L2_CLOUD_EMPTY")
            else:
                self._log_provenance("L2_REJECT", f"RAM Limit Exceeded | Intent: {intent}", "VIOLATION")
                results["L2_ERROR"] = "L2 Mount Rejected: 8GB RAM Law Violation"

        self._log_provenance("HYDRATE", f"Intent: {intent}, Tiers: {','.join(results['tiers_active'])}")
        return results

    def store_tissue(self, intent: str, content: Any, complexity: int, tier: str = "L0"):
        """Store context tissue in the appropriate tier."""
        content_json = json.dumps(content) if not isinstance(content, str) else str(content)
        
        # L0: Flash (Local SQLite)
        if tier == "L0" or complexity >= 1:
            conn = sqlite3.connect(self.l0_db_path)
            try:
                conn.execute(
                    "INSERT OR REPLACE INTO flash_tissue (id, intent, content, complexity, timestamp) VALUES (?, ?, ?, ?, ?)",
                    (f"{intent}_{int(datetime.now().timestamp())}", intent, content_json, complexity, datetime.now(timezone.utc).isoformat())
                )
                conn.commit()
            finally:
                conn.close()
                
        # L1: Short-Term (local Redis)
        if tier == "L1" or complexity >= 4:
            success = redis_store.upsert(
                collection=f"intent:{intent}",
                id=f"{intent}_{int(datetime.now().timestamp())}",
                vector=[1.0],
                payload={"data": content}
            )
            if not success:
                self._log_provenance("L1_REDIS_WARN", f"Redis upsert failed, fell back to dark store for '{intent}'")

        # L1.5: Redis Agent Memory — persist as long-term semantic fact
        if (tier in ("L1", "L1.5", "L2") or complexity >= 6) and _agent_memory and _agent_memory.is_configured():
            mem_id = f"camelot:{intent}:{int(datetime.now().timestamp())}"
            text = content_json if len(content_json) <= 2000 else content_json[:2000]
            stored = _agent_memory.store_fact(mem_id, text)
            if stored:
                self._log_provenance("L1_5_AGENT_STORE", f"Stored '{intent}' to Agent Memory (MP2P7SN8)")

        # L2: Long-Term (NotebookLM)
        if tier == "L2" or complexity >= 8:
            self.cloudbrain.push_to_notebook(
                artifact_type="note",
                content=content_json,
                title=f"L2_Artifact_{intent}"
            )
            self._log_provenance("L2_CLOUD_PUSH", f"Pushed intent '{intent}' to Cloud Brain")
            
        self._log_provenance("STORE", f"Tier: {tier}, Intent: {intent}")

if __name__ == "__main__":
    # Quick self-test
    mgr = HydrationManager()
    mgr.store_tissue("test_pipeline", {"data": "pipeline mapping test"}, 9, tier="L2")
    hydration = mgr.hydrate_context("test_pipeline", 9)
    print(json.dumps(hydration, indent=2))
