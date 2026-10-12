# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
"""DG-340 Domain-Restricted Signer Classes & Key Lifecycle Management.
====================================================================
Prevents the 'generic Ed25519 key' vulnerability by enforcing domain-separated
signer classes and key epochs:
- ROOT: Offline sovereign root anchor; key delegation & revocation
- POLICY: Policy decisions and rule declarations (Sentinel)
- EPOCH: Monotonic authority epoch promotion (Arthur / Sentinel)
- RECEIPT: Immutable receipt-chain and Merkle attestation
- KNIGHT_REGISTRY: Stunspot persona package admission
- CONTEXT_COMPILER: Dynamic prompt/context compilation
- UKG_REGISTRY: Canonical Universal Knowledge Graph crystallization
- RELEASE: Release proof and binary artifact signing
- HOST: Node-level hardware identity and Tailscale attestation
- ADAPTER: External model / tool adapter proxy

Invariant:
Signer classes are strictly bound to signature domains. A Context Compiler
or Host key can NEVER sign an authority epoch or policy decision.
"""
from __future__ import annotations

import datetime
from datetime import timezone
from enum import Enum
import hashlib
import hmac
import logging
from typing import Any, Dict, List, Optional, Set, Tuple

LOG = logging.getLogger("camelot.key_lifecycle")


class SignerClass(str, Enum):
    ROOT = "ROOT"
    POLICY = "POLICY"
    EPOCH = "EPOCH"
    RECEIPT = "RECEIPT"
    KNIGHT_REGISTRY = "KNIGHT_REGISTRY"
    CONTEXT_COMPILER = "CONTEXT_COMPILER"
    UKG_REGISTRY = "UKG_REGISTRY"
    RELEASE = "RELEASE"
    HOST = "HOST"
    ADAPTER = "ADAPTER"


# Domain separation table: allowed signature domains per signer class
CLASS_DOMAIN_MAP: Dict[SignerClass, Set[str]] = {
    SignerClass.ROOT: {"ROOT_DELEGATION", "REVOCATION_CERTIFICATE", "EMERGENCY_RECOVERY"},
    SignerClass.POLICY: {"POLICY_DECISION", "ROLE_ASSIGNMENT", "DENY_LIST"},
    SignerClass.EPOCH: {"AUTHORITY_EPOCH_INCREMENT", "EPOCH_ATTESTATION"},
    SignerClass.RECEIPT: {"RECEIPT_CHAIN_COMMIT", "VERIFICATION_RECEIPT", "EVIDENCE_ATTESTATION"},
    SignerClass.KNIGHT_REGISTRY: {"KNIGHT_PACKAGE_ADMISSION", "PERSONA_PROFILE"},
    SignerClass.CONTEXT_COMPILER: {"CONTEXT_PACKET", "DYNAMIC_PROMPT", "MEMORY_FRAME"},
    SignerClass.UKG_REGISTRY: {"UKG_CRYSTAL_COMMIT", "DECOMPRESSION_DICT_SEAL"},
    SignerClass.RELEASE: {"RELEASE_PROOF", "SBOM_ATTESTATION", "BINARY_DIGEST"},
    SignerClass.HOST: {"NODE_HEARTBEAT", "HARDWARE_ATTESTATION", "VFS_STATE"},
    SignerClass.ADAPTER: {"MODEL_INFERENCE_RESPONSE", "TOOL_DISPATCH_RESULT"},
}


class KeyLifecycleManager:
    """Manages creation, rotation, validation, and domain-enforcement of keys."""

    def __init__(self, current_epoch: int = 1):
        self.current_epoch = current_epoch
        self._keys: Dict[str, Dict[str, Any]] = {}
        self._revocations: Set[str] = set()

    def register_key(
        self,
        key_id: str,
        signer_class: SignerClass,
        public_key_hex: str,
        issuer: str = "ARTHUR_SOVEREIGN_ROOT",
        key_epoch: Optional[int] = None,
        validity_days: int = 90,
    ) -> Dict[str, Any]:
        """Register a new domain-restricted key record."""
        epoch = key_epoch if key_epoch is not None else self.current_epoch
        now = datetime.datetime.now(timezone.utc)
        expires = now + datetime.timedelta(days=validity_days)

        allowed_domains = sorted(list(CLASS_DOMAIN_MAP.get(signer_class, set())))

        key_record = {
            "key_id": key_id,
            "signer_class": signer_class.value,
            "public_key_hex": public_key_hex,
            "issuer": issuer,
            "key_epoch": epoch,
            "created_at": now.isoformat(),
            "expires_at": expires.isoformat(),
            "rotation_window_days": validity_days,
            "revocation_status": "ACTIVE",
            "allowed_signature_domains": allowed_domains,
        }
        self._keys[key_id] = key_record
        LOG.info("Registered key %s with class %s for epoch %d", key_id, signer_class.value, epoch)
        return key_record

    def revoke_key(self, key_id: str, reason: str = "KEY_COMPROMISE") -> Dict[str, Any]:
        """Revoke a key immediately."""
        if key_id not in self._keys:
            raise KeyError(f"Key {key_id} not registered")
        self._keys[key_id]["revocation_status"] = "REVOKED"
        self._keys[key_id]["revocation_reason"] = reason
        self._revocations.add(key_id)
        LOG.warning("Revoked key %s (Reason: %s)", key_id, reason)
        return self._keys[key_id]

    def verify_signing_authorization(
        self,
        key_id: str,
        target_domain: str,
        epoch: Optional[int] = None,
    ) -> Tuple[bool, Optional[str]]:
        """Verify that the key is valid, unrevoked, epoch-compatible, and allowed to sign target_domain."""
        key = self._keys.get(key_id)
        if not key:
            return False, f"Unknown key_id: {key_id}"

        if key["revocation_status"] != "ACTIVE":
            return False, f"Key {key_id} is {key['revocation_status']}"

        check_epoch = epoch if epoch is not None else self.current_epoch
        if key["key_epoch"] < check_epoch:
            return False, f"Key epoch {key['key_epoch']} is stale (current epoch: {check_epoch})"

        now = datetime.datetime.now(timezone.utc)
        expires_at = datetime.datetime.fromisoformat(key["expires_at"])
        if now > expires_at:
            return False, f"Key {key_id} expired at {key['expires_at']}"

        allowed = set(key.get("allowed_signature_domains", []))
        if target_domain not in allowed:
            return False, (
                f"DOMAIN_VIOLATION: Signer class '{key['signer_class']}' is prohibited "
                f"from signing domain '{target_domain}'. Allowed: {sorted(list(allowed))}"
            )

        return True, None

    def sign_payload_simulated(
        self,
        key_id: str,
        payload_bytes: bytes,
        target_domain: str,
        secret_seed: str = "sovereign_signing_seed",
    ) -> Dict[str, Any]:
        """Cryptographically sign payload after verifying domain authorization."""
        authorized, reason = self.verify_signing_authorization(key_id, target_domain)
        if not authorized:
            raise PermissionError(f"Signing unauthorized: {reason}")

        # Domain-separated signature construction: H(domain || payload)
        domain_prefix = f"DOMAIN:{target_domain}:".encode("utf-8")
        h = hmac.new(secret_seed.encode("utf-8"), domain_prefix + payload_bytes, hashlib.sha256)
        signature_hex = h.hexdigest()

        return {
            "key_id": key_id,
            "signer_class": self._keys[key_id]["signer_class"],
            "target_domain": target_domain,
            "key_epoch": self._keys[key_id]["key_epoch"],
            "signature": signature_hex,
        }
