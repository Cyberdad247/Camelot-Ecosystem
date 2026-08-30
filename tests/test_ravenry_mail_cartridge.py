# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.

import pytest
import time
from control_plane.cartridges.ravenry_mail import RavenryMailCartridge, CapabilityLease


def test_ravenry_mail_lease_enforcement():
    engine = RavenryMailCartridge(tenant_id="tenant_test_001")
    
    # Attempting to draft without lease should fail
    with pytest.raises(PermissionError) as exc:
        engine.generate_draft(
            recipient="jane@example.com",
            subject="Invoice #1024",
            context="Please review the quarterly invoice.",
            lease=None
        )
    assert "[SENTINEL_DENIED]" in str(exc.value)


def test_ravenry_mail_draft_and_approval_flow():
    engine = RavenryMailCartridge(tenant_id="tenant_test_001")
    
    # 1. Issue Sentinel Capability Lease
    lease = engine.issue_sentinel_lease(target_scope="gmail.read", risk_tier="R4")
    assert lease.lease_id.startswith("lease_")
    assert lease.risk_tier == "R4"
    
    # 2. Generate Draft (AC-1: <5s)
    t0 = time.time()
    draft = engine.generate_draft(
        recipient="jane@example.com",
        subject="Invoice #1024",
        context="Regarding the payment schedule.",
        tone="professional",
        lease=lease
    )
    duration = time.time() - t0
    assert duration < 5.0
    assert draft.approval_status == "APPROVAL_PENDING"
    assert draft.plan_hash.startswith("sha256:")
    
    # 3. Generate A2UI Approval Card (AC-2)
    card = engine.create_a2ui_approval_card(draft)
    assert card.version == "a2ui/v1"
    assert card.risk_tier == "R4"
    assert card.hold_duration_sec == 1.5
    assert len(card.layout["components"]) == 4
    
    # 4. Attempt unauthenticated approval (AC-3: rejected)
    with pytest.raises(PermissionError) as exc:
        engine.approve_and_seal(draft.draft_id, {"authenticated": False})
    assert "[ARTHUR_GATE]" in str(exc.value)
    
    # 5. Approve with WebAuthn assertion (AC-4 & AC-5: signed QR artifact & receipt)
    approved_draft = engine.approve_and_seal(draft.draft_id, {"authenticated": True, "user": "VaShawn O. Head"})
    assert approved_draft.approval_status == "APPROVED"
    assert approved_draft.qr_artifact_ref.startswith("object://minio/qr-artifacts/")
