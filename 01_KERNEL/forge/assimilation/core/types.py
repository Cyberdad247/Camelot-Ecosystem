# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
from typing import List

from pydantic import BaseModel, Field


class AssimilationRequest(BaseModel):
    repo_path: str = Field(..., description="Local path or checked-out path to the repository")
    origin: str = Field(default="local", description="Source origin (e.g. 'local', 'github')")
    tags: List[str] = Field(default_factory=list, description="Taxonomy tags")
    description: str = Field(default="", description="Short human description")


class AssimilationResult(BaseModel):
    repo_path: str
    origin: str
    tags: List[str]
    files_indexed: int = 0
    chunks_created: int = 0
    graph_nodes_created: int = 0
    skills_registered: int = 0
    rag_collections: List[str] = Field(default_factory=list)
    report_path: str = ""
    ledger_entry_id: str = ""
    status: str = Field(..., pattern="^(success|partial|failed)$")
    messages: List[str] = Field(default_factory=list)