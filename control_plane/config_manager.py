"""Camelot-OS Configuration Manager — Persisted Operator Profiles."""

from __future__ import annotations

import os
import json
from pathlib import Path
from typing import Any, Optional
from pydantic import BaseModel, Field

try:
    import yaml
except ImportError:  # pragma: no cover - optional dependency
    yaml = None


class OperatorProfile(BaseModel):
    """Operator policy for browser swarms and cloud services."""
    compute_tier: str = "hybrid"
    browser_isolation: str = "agency"
    residential_proxy: bool = True
    stealth: bool = True
    ephemeral_sessions: bool = True
    privacy_threshold: float = 0.0


class CamelotConfig(BaseModel):
    """Canonical Camelot-OS configuration."""
    cloudbrain_url: Optional[str] = None
    research_agency_url: Optional[str] = None
    active_profile: str = "default"
    profiles: dict[str, OperatorProfile] = Field(default_factory=lambda: {"default": OperatorProfile()})


class ConfigManager:
    """Loads and persists Camelot-OS configuration."""

    def __init__(self, config_path: Optional[Path] = None):
        if config_path:
            self.config_path = config_path
        else:
            # Default to project root or home directory
            project_root = Path(__file__).parent.parent
            self.config_path = project_root / ".camelot-config.yaml"
            if not self.config_path.exists():
                self.config_path = Path.home() / ".camelot-config.yaml"

        self.config = self._load()

    def _load(self) -> CamelotConfig:
        if not self.config_path.exists():
            return CamelotConfig()

        if self.config_path.suffix in {".yaml", ".yml"} and yaml is None:
            return CamelotConfig()

        try:
            with open(self.config_path, "r") as f:
                if self.config_path.suffix in {".yaml", ".yml"}:
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
                return CamelotConfig.model_validate(data or {})
        except Exception as e:
            print(f"Warning: Failed to load config from {self.config_path}: {e}")
            return CamelotConfig()

    def save(self):
        """Persist current configuration to disk."""
        try:
            with open(self.config_path, "w") as f:
                data = self.config.model_dump(exclude_none=True)
                if self.config_path.suffix in {".yaml", ".yml"}:
                    if yaml is None:
                        raise RuntimeError("PyYAML not installed")
                    yaml.safe_dump(data, f, default_flow_style=False)
                else:
                    json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error: Failed to save config to {self.config_path}: {e}")

    def get_profile(self, name: Optional[str] = None) -> OperatorProfile:
        """Retrieve a specific profile or the active one."""
        profile_name = name or self.config.active_profile
        return self.config.profiles.get(profile_name, OperatorProfile())

    def update_profile(self, name: str, profile: OperatorProfile):
        """Update or create a profile."""
        self.config.profiles[name] = profile
        self.save()
