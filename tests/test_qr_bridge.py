# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.

import pytest
import json
from dataclasses import asdict
from control_plane.cartridges.qr_bridge import QRBridgeEngine, WORLDTREE_ROOT_UUID


def test_qr_bridge_encoding_and_verification(tmp_path):
    engine = QRBridgeEngine(storage_dir=tmp_path)
    
    # 1. Encode and sign QR artifact
    payload = engine.encode_and_sign_artifact(
        artifact_id="draft_test_1024",
        plan_hash="sha256:4a8b8c2d9e1f",
        approved_by="King Arthur"
    )
    
    assert payload.version == "qr.artifact/v1"
    assert payload.worldtree_anchor == WORLDTREE_ROOT_UUID
    assert len(payload.signature) == 64
    
    # 2. Verify valid payload
    payload_dict = asdict(payload)
    assert engine.verify_qr_payload(payload_dict) is True
    
    # 3. Tamper detection (modify plan hash)
    tampered_dict = dict(payload_dict)
    tampered_dict["plan_hash"] = "sha256:tampered_hash_999"
    assert engine.verify_qr_payload(tampered_dict) is False


def test_bitemporal_fact_ingestion(tmp_path):
    engine = QRBridgeEngine(storage_dir=tmp_path)
    
    fact = engine.ingest_bitemporal_fact(
        tenant_id="tenant_sovereign_001",
        namespace="ravenry.mail",
        predicate="approved_reply_to",
        object_value="jane@example.com",
        provenance_ref="object://minio/qr-artifacts/draft_test_1024.json",
        confidence=0.99
    )
    
    assert fact.fact_id.startswith("fact_")
    assert fact.status == "current"
    assert fact.valid_from is not None
    assert fact.valid_to is None
    assert len(fact.provenance) == 2
