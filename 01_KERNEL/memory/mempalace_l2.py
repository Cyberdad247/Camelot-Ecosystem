import os
import json
from pathlib import Path
from typing import Any, Optional

try:
    import chromadb
except ImportError:
    chromadb = None

class MemPalaceL2:
    """Persistent local vector index manager (Layer 2 Memory)."""

    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path:
            self.storage_path = storage_path
        else:
            # Default to 03_VAULT/memory/l2_index
            repo_root = Path(__file__).resolve().parent.parent.parent
            self.storage_path = repo_root / "03_VAULT" / "memory" / "l2_index"
        
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        if chromadb:
            self.client = chromadb.PersistentClient(path=str(self.storage_path))
        else:
            self.client = None
            # Log warning or handle gracefully
            print("WARNING: chromadb not installed. L2 Memory is in DARK mode.")
