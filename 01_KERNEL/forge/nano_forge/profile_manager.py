# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
# Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
"""
PROFILE MANAGER: Multi-Login Clone (v1.0)
Manages isolated browser profiles with rich fingerprinting.
"""

import json
import os
import secrets
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional


class ProfileManager:
    def __init__(self, workspace_root: str = None):
        if not workspace_root:
            workspace_root = os.path.join(os.path.dirname(__file__), "..", "..", "workspace", "nano_knights")

        self.workspace_root = Path(workspace_root)
        self.workspace_root.mkdir(parents=True, exist_ok=True)

        self.schema_path = os.path.join(os.path.dirname(__file__), "rich_fingerprint_schema.json")

    def create_profile(self, profile_id: str, base_fingerprint: Optional[Dict] = None) -> Dict[str, Any]:
        """Creates a new isolated profile with unique fingerprint."""
        profile_dir = self.workspace_root / profile_id

        if profile_dir.exists():
            raise ValueError(f"Profile {profile_id} already exists")

        # Create profile directory structure
        profile_dir.mkdir(parents=True)
        (profile_dir / "cookies").mkdir()
        (profile_dir / "cache").mkdir()
        (profile_dir / "localStorage").mkdir()

        # Generate or use provided fingerprint
        if base_fingerprint:
            fingerprint = base_fingerprint
        else:
            fingerprint = self._generate_default_fingerprint()

        fingerprint["id"] = profile_id

        # Save fingerprint
        with open(profile_dir / "fingerprint.json", "w") as f:
            json.dump(fingerprint, f, indent=2)

        # Initialize empty session history
        with open(profile_dir / "history.jsonl", "w") as f:
            pass  # Empty file

        print(f"[PROFILE_MGR] Created profile: {profile_id}")
        return fingerprint

    def load_profile(self, profile_id: str) -> Dict[str, Any]:
        """Loads an existing profile's fingerprint."""
        profile_dir = self.workspace_root / profile_id

        if not profile_dir.exists():
            raise ValueError(f"Profile {profile_id} not found")

        with open(profile_dir / "fingerprint.json", "r") as f:
            return json.load(f)

    def update_profile(self, profile_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Updates profile fingerprint with new values."""
        fingerprint = self.load_profile(profile_id)
        fingerprint.update(updates)

        profile_dir = self.workspace_root / profile_id
        with open(profile_dir / "fingerprint.json", "w") as f:
            json.dump(fingerprint, f, indent=2)

        print(f"[PROFILE_MGR] Updated profile: {profile_id}")
        return fingerprint

    def delete_profile(self, profile_id: str):
        """Deletes a profile and all associated data."""
        profile_dir = self.workspace_root / profile_id

        if not profile_dir.exists():
            raise ValueError(f"Profile {profile_id} not found")

        shutil.rmtree(profile_dir)
        print(f"[PROFILE_MGR] Deleted profile: {profile_id}")

    def list_profiles(self) -> List[str]:
        """Lists all available profiles."""
        return [p.name for p in self.workspace_root.iterdir() if p.is_dir()]

    def get_profile_path(self, profile_id: str) -> Path:
        """Returns the absolute path to a profile's directory."""
        return self.workspace_root / profile_id

    def _generate_default_fingerprint(self) -> Dict[str, Any]:
        """Generates a basic fingerprint (minimal set for v1)."""
        return {
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "screen": {
                "width": 1920,
                "height": 1080,
                "availWidth": 1920,
                "availHeight": 1040,
                "colorDepth": 24,
                "pixelDepth": 24,
            },
            "viewport": {"width": 1920, "height": 1080},
            "timezone": "America/New_York",
            "locale": "en-US",
            "languages": ["en-US", "en"],
            "platform": "Win32",
            "vendor": "Google Inc.",
            "hardwareConcurrency": 8,
            "deviceMemory": 8,
            "webgl": {
                "vendor": "Google Inc. (NVIDIA)",
                "renderer": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1050 Ti Direct3D11 vs_5_0 ps_5_0, D3D11)",
            },
            "webrtc": {"mode": "disabled"},
            "canvas": {"noiseSeed": secrets.token_hex(16), "enabled": True},
            "audioContext": {"noiseSeed": secrets.token_hex(16), "enabled": True},
            "fonts": ["Arial", "Times New Roman", "Courier New"],
            "plugins": [],
            "doNotTrack": "null",
            "cookiesEnabled": True,
            "risk_tier": "STANDARD",  # Options: STANDARD, ELEVATED, MAXIMUM
        }


if __name__ == "__main__":
    # Test
    manager = ProfileManager()

    # Create test profile
    profile = manager.create_profile("test_profile_01")
    print(f"Created: {profile['id']}")
    print(f"Canvas Seed: {profile['canvas']['noiseSeed']}")

    # List profiles
    print(f"Available profiles: {manager.list_profiles()}")

    # Load and verify
    loaded = manager.load_profile("test_profile_01")
    print(f"Loaded: {loaded['id']}")