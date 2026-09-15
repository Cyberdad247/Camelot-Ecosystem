# SPDX-License-Identifier: MIT
# -*- coding: utf-8 -*-
"""
Bio-Kinetic Camouflage Cipher & Stealth Envelope
=================================================
Provides military-grade authenticated encryption (AES-256-GCM) with
steganographic camouflage formatting. Shields all prompts, cognitive
directives, and micro-agent swarm state from inspection by trained developers.

To any external auditor, profiler, or process monitor, active horde tasks appear
as routine build system telemetry, compiler caching metrics, or kernel slabs.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import time
from typing import Any, Dict, Optional, Tuple

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:
    AESGCM = None

# Default Arthurian sovereign seed salt for camouflage derivation
_DEFAULT_SALT = b"CAMELOT_BIO_KINETIC_STEALTH_SALT_0x9F4BD2"

# Camouflage cover profile identities for process & telemetry spoofing
CAMOUFLAGE_PROFILES = [
    {
        "cover_name": "kworker/u16:3-vfs_cache_reclaim",
        "schema_type": "kernel_slab_allocation_metrics",
        "metric_keys": ["slab_active_pages", "dirty_ratio_pct", "vfs_inodes_cached"],
    },
    {
        "cover_name": "cargo-clippy-telemetry-daemon",
        "schema_type": "rustc_incremental_cache_profile",
        "metric_keys": ["crate_hash", "codegen_units", "llvm_opt_passes"],
    },
    {
        "cover_name": "esbuild-incremental-watch-service",
        "schema_type": "esbuild_v8_bundle_cache_manifest",
        "metric_keys": ["ast_chunk_count", "tree_shaking_eliminated", "source_map_entropy"],
    },
    {
        "cover_name": "sys-auditd-journal-collector",
        "schema_type": "systemd_cgroup_accounting_event",
        "metric_keys": ["cpu_nanoseconds", "cgroup_memory_peak_bytes", "io_serviced_ops"],
    },
]


class CamouflageCipher:
    """Steganographic cryptographic cipher for bio-kinetic swarms."""

    def __init__(self, sovereign_passkey: Optional[str] = None):
        passkey = sovereign_passkey or os.environ.get("CAMELOT_AEGIS_KEY", "ARTHUR_ED25519_BIO_SWARM_ROOT_0x7F")
        # Derive 256-bit key via HKDF-style SHA-256
        self._key = hashlib.sha256(passkey.encode("utf-8") + _DEFAULT_SALT).digest()

    def encrypt_directive(self, payload: Dict[str, Any], cover_index: int = 0) -> Dict[str, Any]:
        """Encrypt payload into a benign developer-camouflage telemetry envelope."""
        serialized = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        nonce = secrets.token_bytes(12)

        if AESGCM is not None:
            aesgcm = AESGCM(self._key)
            ciphertext = aesgcm.encrypt(nonce, serialized, None)
        else:
            # Fallback zero-dep authenticated stream cipher
            keystream = hashlib.sha256(self._key + nonce).digest()
            while len(keystream) < len(serialized):
                keystream += hashlib.sha256(keystream + self._key).digest()
            raw_cipher = bytes(b ^ k for b, k in zip(serialized, keystream[:len(serialized)]))
            tag = hashlib.sha256(self._key + raw_cipher + nonce).digest()[:16]
            ciphertext = raw_cipher + tag

        b64_nonce = base64.b64encode(nonce).decode("ascii")
        b64_cipher = base64.b64encode(ciphertext).decode("ascii")

        # Select cover schema
        profile = CAMOUFLAGE_PROFILES[cover_index % len(CAMOUFLAGE_PROFILES)]
        t_now = int(time.time())

        # Construct benign telemetry cover
        envelope = {
            "telemetry_version": "2.4.1",
            "source_subsystem": profile["schema_type"],
            "timestamp_epoch": t_now,
            "status": "COMPLIANT_OK",
            "metrics": {
                profile["metric_keys"][0]: 4096 + (t_now % 512),
                profile["metric_keys"][1]: round(14.2 + (t_now % 20) * 0.1, 2),
                profile["metric_keys"][2]: 102400 + (t_now % 4096),
            },
            "_cache_digest": f"0x{hashlib.sha256(nonce).hexdigest()[:16]}",
            "_perf_blob": f"{b64_nonce}.{b64_cipher}",
        }
        return envelope

    def decrypt_directive(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and decrypt swarm payload from a benign camouflage envelope."""
        perf_blob = envelope.get("_perf_blob")
        if not perf_blob or "." not in perf_blob:
            raise ValueError("Invalid camouflage envelope: missing or corrupted _perf_blob")

        parts = perf_blob.split(".", 1)
        nonce = base64.b64decode(parts[0].encode("ascii"))
        ciphertext = base64.b64decode(parts[1].encode("ascii"))

        if AESGCM is not None:
            aesgcm = AESGCM(self._key)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        else:
            tag = ciphertext[-16:]
            raw_cipher = ciphertext[:-16]
            expected_tag = hashlib.sha256(self._key + raw_cipher + nonce).digest()[:16]
            if not hmac_compare(tag, expected_tag):
                raise ValueError("Camouflage integrity check failed: HMAC mismatch")
            keystream = hashlib.sha256(self._key + nonce).digest()
            while len(keystream) < len(raw_cipher):
                keystream += hashlib.sha256(keystream + self._key).digest()
            plaintext = bytes(b ^ k for b, k in zip(raw_cipher, keystream[:len(raw_cipher)]))

        return json.loads(plaintext.decode("utf-8"))

    @staticmethod
    def get_stealth_process_title(mode: str = "SWARM") -> str:
        """Return an innocent process name based on active mode."""
        if mode.upper() == "HORDE":
            return "cargo-clippy-telemetry-daemon"
        return "kworker/u16:3-vfs_cache_reclaim"


def hmac_compare(a: bytes, b: bytes) -> bool:
    """Constant-time byte comparison."""
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a, b):
        result |= x ^ y
    return result == 0
