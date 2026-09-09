# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.

import pytest
from control_plane.dispatch.inference_contract import InferenceBroker, InferenceIntent


def test_inference_intent_creation_and_signing():
    broker = InferenceBroker(tenant_id="tenant_sovereign_001")
    
    intent = broker.create_inference_intent(
        agent_id="sir_codex",
        task_class="codegen",
        data_class="confidential",
        raw_prompt="def generate_secure_token(): return secrets.token_hex(32)",
        required_capabilities=["structured_output.v1"]
    )
    
    assert intent.request_id.startswith("req_")
    assert intent.data_class == "confidential"
    assert "qwen-local" in intent.allowed_models
    assert "public-routing-aggregators" in intent.denied_models
    assert len(intent.signature) == 64
    assert intent.payload.prompt_hash.startswith("sha256:")


def test_data_exfiltration_guard_and_receipt():
    broker = InferenceBroker(tenant_id="tenant_sovereign_001")
    
    # Confidential task
    intent = broker.create_inference_intent(
        agent_id="sir_ghost",
        task_class="review",
        data_class="confidential",
        raw_prompt="Review database encryption credentials"
    )
    
    # Attempting to route confidential data to unapproved public model must be blocked
    with pytest.raises(PermissionError) as exc:
        broker.execute_with_fallback_guard(intent, candidate_model="public-routing-aggregators")
    assert "[DATA_EXFILTRATION_GUARD]" in str(exc.value)
    
    # Routing to allowed local model must succeed and issue receipt
    receipt = broker.execute_with_fallback_guard(intent, candidate_model="qwen-local")
    assert receipt.request_id == intent.request_id
    assert receipt.model_id == "qwen-local"
    assert receipt.provider_class == "native_bifrost_gateway"
    assert receipt.policy_decision_hash == intent.signature
    assert receipt.transcript_hash.startswith("sha256:")
