# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY

import json
import logging
from typing import Optional, Any

# Fallback or hypothetical notebooklm wrapper based on previous code
try:
    from notebooklmpy import NotebookLM
except ImportError:
    NotebookLM = None

# Mapping of Knight names to NotebookLM IDs
KNIGHT_NOTEBOOKS = {
    "SIR_BORIS": "f7707daa-2d10-4db8-8fda-be4661a27793",
    "SIR_ALEX": "f490c05e-d8c4-4008-87e1-5f901bf57c6a",
    "SIR_FORGE": "91c5da8b-e2de-4a56-b7fd-c8b76c00afc7",
    "SIR_SENTINEL": "07cbb441-f008-424c-820a-85676210be39",
    "SIR_DEBUG": "fdc42a4a-3060-4eac-b57c-8e6009ed634a",
    "SIR_GHOST": "422a184b-93e7-4dfd-8a12-75d2268b6c60",
    "LADY_APIS": "378d6049-ffc3-4ed3-a9e7-47ffc5c0ac3f",
    "MERLIN_OMEGA": "af927fde-d7eb-42ee-8c79-51b3e78ef39b",
    "SIR_HELIO": "56820318-bb91-451f-aac4-4b46424898cf",
    "SIR_SONUS": "b8a1c3d5-e2f4-4687-9a01-234567890abc",
}

class CloudBrainConnector:
    """Connects Camelot OS memory tiers to the external NotebookLM Cloud Brain."""

    def __init__(self, knight_id: str = "DEFAULT"):
        self.knight_id = knight_id.upper()
        self.notebook_id = KNIGHT_NOTEBOOKS.get(self.knight_id)
        if not self.notebook_id:
            logging.warning(f"[CLOUD_BRAIN] Unmapped Knight ID: {knight_id}. Cloud Brain sync disabled.")

    def push_to_notebook(self, artifact_type: str, content: Any, title: str) -> bool:
        """Push high-complexity artifacts to the Knight's NotebookLM workspace."""
        if not self.notebook_id or not NotebookLM:
            return False

        try:
            if isinstance(content, dict) or isinstance(content, list):
                content_str = json.dumps(content, indent=2)
            else:
                content_str = str(content)

            # Initialize workspace connection
            ws = NotebookLM(notebook_id=self.notebook_id)
            
            # Push based on artifact type (source or note)
            if artifact_type == "source":
                ws.add_source(text=content_str, title=title)
            elif artifact_type == "note":
                ws.create_note(title=title, content=content_str)
            else:
                ws.add_source(text=content_str, title=title)
            
            logging.info(f"[CLOUD_BRAIN] Successfully pushed artifact '{title}' to {self.knight_id}'s Notebook.")
            return True
        except Exception as e:
            logging.error(f"[CLOUD_BRAIN] Push failed for {self.knight_id}: {str(e)}")
            return False

    def query_notebook(self, query: str) -> Optional[str]:
        """Retrieve synthesized insights from the Knight's NotebookLM workspace."""
        if not self.notebook_id or not NotebookLM:
            return None

        try:
            ws = NotebookLM(notebook_id=self.notebook_id)
            result = ws.query(query)
            logging.info(f"[CLOUD_BRAIN] Successfully queried {self.knight_id}'s Notebook.")
            return result
        except Exception as e:
            logging.error(f"[CLOUD_BRAIN] Query failed for {self.knight_id}: {str(e)}")
            return None
