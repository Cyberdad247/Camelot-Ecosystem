"""Provenance and Audit Ledger Manager — Structured Mission Traceability."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from pydantic import BaseModel, Field


class LaneEvent(BaseModel):
    """A single event within a browser lane."""
    type: str
    timestamp: int
    offset_ms: int
    data: dict[str, Any]


class MissionLane(BaseModel):
    """Execution trace of a single Nano-Knight lane."""
    lane_id: str
    goal: str
    status: str
    evaluation: Optional[dict[str, Any]] = None
    events: list[LaneEvent] = Field(default_factory=list)


class MissionRecord(BaseModel):
    """Complete audit record for a Precise Mode mission."""
    mission_id: str
    objective: str
    operator: str
    timestamp_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str
    compute_tier: str
    browser_isolation: str
    lanes: dict[str, MissionLane] = Field(default_factory=dict)
    summary: Optional[str] = None


class VerificationRun(BaseModel):
    """Record of a system verification or acceptance run."""
    run_id: str
    timestamp_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    operator: str
    command: str
    results: dict[str, Any]
    success: bool


class ProvenanceManager:
    """Manages structured JSON ledgers and mission archival."""

    def __init__(self, vault_path: Optional[Path] = None):
        if vault_path:
            self.vault_path = vault_path
        else:
            # Default to 03_VAULT/Missions
            repo_root = Path(__file__).resolve().parent.parent
            self.vault_path = repo_root / "03_VAULT" / "Missions"
        
        self.vault_path.mkdir(parents=True, exist_ok=True)
        self.verification_ledger = self.vault_path / "verification_ledger.jsonl"

    def log_mission(self, record: MissionRecord):
        """Save a complete mission record to the vault."""
        file_path = self.vault_path / f"mission_{record.mission_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(record.model_dump(), f, indent=2)
        return file_path

    def log_verification(self, run: VerificationRun):
        """Append a verification run to the JSONL ledger."""
        with open(self.verification_ledger, "a", encoding="utf-8") as f:
            f.write(json.dumps(run.model_dump()) + "\n")
        return self.verification_ledger

    def get_retention_stats(self) -> dict[str, Any]:
        """Compute stats for log rotation policy (Task E5)."""
        files = list(self.vault_path.glob("mission_*.json"))
        total_size = sum(f.stat().st_size for f in files)
        return {
            "mission_count": len(files),
            "total_size_bytes": total_size,
            "verification_entries": self._count_verification_entries()
        }

    def _count_verification_entries(self) -> int:
        if not self.verification_ledger.exists():
            return 0
        with open(self.verification_ledger, "r") as f:
            return sum(1 for _ in f)

    def rotate_logs(self, max_files: int = 100):
        """Archive old mission logs if count exceeds threshold."""
        files = sorted(
            list(self.vault_path.glob("mission_*.json")),
            key=lambda x: x.stat().st_mtime
        )
        if len(files) <= max_files:
            return 0

        archived_count = 0
        archive_dir = self.vault_path / "Archive"
        archive_dir.mkdir(exist_ok=True)

        for f in files[:-max_files]:
            f.rename(archive_dir / f.name)
            archived_count += 1
        
        return archived_count
