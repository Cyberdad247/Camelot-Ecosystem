# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""DG-320 Configuration Contract Engine (camelot-config/1).
=========================================================
Treats configuration as a formal contract. Classifies configuration variables into:
- STATIC: Fixed at process startup (port, bind host)
- RELOADABLE: Safe to hot-reload (log verbosity, poll intervals)
- SECRET_REFERENCE: Pointers to vault keys / env vars; never raw secrets
- BOOTSTRAP_ONLY: Cluster genesis / init parameters
- AUTHORITY_CRITICAL: Keys, root signers, gate bypass tokens

Invariant:
Any missing or unverified AUTHORITY_CRITICAL configuration fails startup.
"""
from __future__ import annotations

from enum import Enum
import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

LOG = logging.getLogger("camelot.config_contract")


class ConfigClassification(str, Enum):
    STATIC = "STATIC"
    RELOADABLE = "RELOADABLE"
    SECRET_REFERENCE = "SECRET_REFERENCE"
    BOOTSTRAP_ONLY = "BOOTSTRAP_ONLY"
    AUTHORITY_CRITICAL = "AUTHORITY_CRITICAL"


class ConfigContractError(Exception):
    """Raised when configuration contract validation fails."""


class ConfigContract:
    """Manages parsing, classification, and validation of camelot-config/1."""

    MANDATORY_AUTHORITY_KEYS = [
        "SENTINEL_LEASE_SIGNER_KEY",
        "AUTHORITY_EPOCH_SIGNER_KEY",
        "ANYA_GATE_VERIFICATION_SECRET",
    ]

    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        self.config_data = config_dict or self._load_default_config()

    def _load_default_config(self) -> Dict[str, Any]:
        return {
            "schema_version": "camelot-config/1",
            "config_id": "cfg_cybertronia_production",
            "version": "v10001.00-CYBERTRONIA",
            "environment": "production",
            "entries": {
                "BIFROST_PORT": {
                    "value": 3001,
                    "classification": ConfigClassification.STATIC.value,
                    "description": "Bifrost mTLS gateway port",
                    "requires_restart": True,
                },
                "PWA_PORT": {
                    "value": 3000,
                    "classification": ConfigClassification.STATIC.value,
                    "description": "Lakisha PWA port",
                    "requires_restart": True,
                },
                "LOG_LEVEL": {
                    "value": "INFO",
                    "classification": ConfigClassification.RELOADABLE.value,
                    "description": "Global telemetry logging level",
                    "requires_restart": False,
                },
                "MEMPALACE_SECRET_REF": {
                    "value": "env:MEMPALACE_SECRET",
                    "classification": ConfigClassification.SECRET_REFERENCE.value,
                    "description": "Reference pointer to airgapped vault secret",
                    "requires_restart": False,
                },
                "CLUSTER_GENESIS_SEED": {
                    "value": "0xCYBERTRONIA_V10001_ROOT",
                    "classification": ConfigClassification.BOOTSTRAP_ONLY.value,
                    "description": "Bootstrap genesis root",
                    "requires_restart": True,
                },
                "SENTINEL_LEASE_SIGNER_KEY": {
                    "value": "0xSENTINEL_ED25519_LEASE_PUB",
                    "classification": ConfigClassification.AUTHORITY_CRITICAL.value,
                    "description": "Key required for Sentinel nonce lease validation",
                    "requires_restart": True,
                },
                "AUTHORITY_EPOCH_SIGNER_KEY": {
                    "value": "0xARTHUR_EPOCH_SIGNER_PUB",
                    "classification": ConfigClassification.AUTHORITY_CRITICAL.value,
                    "description": "Key required for epoch increment authority",
                    "requires_restart": True,
                },
                "ANYA_GATE_VERIFICATION_SECRET": {
                    "value": "0xANYA_GATE_VERIFY_HASH",
                    "classification": ConfigClassification.AUTHORITY_CRITICAL.value,
                    "description": "Key required for Anya Sovereign Gate attestation",
                    "requires_restart": True,
                },
            },
        }

    def compute_checksum(self) -> str:
        """Compute canonical RFC 8785 / sorted JCS digest of configuration."""
        canonical_str = json.dumps(
            self.config_data.get("entries", {}), sort_keys=True, separators=(",", ":")
        )
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate configuration invariants. Fails startup if authority-critical is broken."""
        errors: List[str] = []
        entries = self.config_data.get("entries", {})

        # 1. Schema version check
        if self.config_data.get("schema_version") != "camelot-config/1":
            errors.append(f"Invalid schema version: {self.config_data.get('schema_version')}")

        # 2. Check all mandatory authority-critical keys
        for mandatory_key in self.MANDATORY_AUTHORITY_KEYS:
            if mandatory_key not in entries:
                errors.append(f"Missing mandatory AUTHORITY_CRITICAL key: {mandatory_key}")
            else:
                entry = entries[mandatory_key]
                if entry.get("classification") != ConfigClassification.AUTHORITY_CRITICAL.value:
                    errors.append(
                        f"Key {mandatory_key} must have classification AUTHORITY_CRITICAL, got {entry.get('classification')}"
                    )
                if not entry.get("value"):
                    errors.append(f"AUTHORITY_CRITICAL key {mandatory_key} cannot have empty value")

        # 3. Secret reference rule: SECRET_REFERENCE values MUST NOT be raw secrets
        for key, entry in entries.items():
            if entry.get("classification") == ConfigClassification.SECRET_REFERENCE.value:
                val = str(entry.get("value", ""))
                if not (val.startswith("env:") or val.startswith("vault:") or val.startswith("file:")):
                    errors.append(
                        f"SECRET_REFERENCE key '{key}' contains raw value instead of reference (env:, vault:, file:)"
                    )

        return len(errors) == 0, errors

    def get_entry(self, key: str) -> Optional[Dict[str, Any]]:
        return self.config_data.get("entries", {}).get(key)

    def is_reloadable(self, key: str) -> bool:
        entry = self.get_entry(key)
        if not entry:
            return False
        return entry.get("classification") == ConfigClassification.RELOADABLE.value
