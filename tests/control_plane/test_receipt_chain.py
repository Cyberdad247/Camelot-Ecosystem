import copy
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from control_plane.security.receipt_chain import (
    GENESIS_PARENT_HASH,
    ChainVerificationError,
    Receipt,
    ReceiptActor,
    ReceiptProof,
    TenantIsolationViolation,
    TenantReceiptChain,
)


def _make_receipt(
    tenant_id: str,
    height: int,
    parent_hash: str,
    receipt_id: str = "rcp_001",
    epoch: int = 42,
    authority_vector: list[int] = None,
) -> Receipt:
    return Receipt(
        receipt_id=receipt_id,
        tenant_id=tenant_id,
        correlation_id="cor_100",
        task_id="task_200",
        chain_height=height,
        parent_hash=parent_hash,
        authority_epoch=epoch,
        authority_vector=authority_vector or [1, 1, 0, 1, 1, 1],
        effect_class="workspace.patch",
        declared_risk_tier="T1",
        actor=ReceiptActor(id="sir-forge", role="engineering_builder", node_id="cybertronia-1", trust_band="attested"),
        event="patch.applied",
        proof=ReceiptProof(signer="sentinel", signature="ed25519:test_sig_value"),
    )


def test_genesis_receipt_append():
    chain = TenantReceiptChain("tenant_acme", anchor_interval=10)
    r0 = _make_receipt("tenant_acme", height=0, parent_hash=GENESIS_PARENT_HASH, receipt_id="rcp_genesis")

    appended = chain.append(r0)
    assert appended.self_hash is not None
    assert appended.self_hash.startswith("sha256:")
    assert chain.chain_height == 1
    assert chain.head_hash == appended.self_hash

    valid, msg = chain.verify_chain()
    assert valid is True
    assert msg == "CHAIN_VALID"


def test_monotonic_chain_append():
    chain = TenantReceiptChain("tenant_acme", anchor_interval=5)
    r0 = _make_receipt("tenant_acme", height=0, parent_hash=GENESIS_PARENT_HASH, receipt_id="rcp_0")
    chain.append(r0)

    # Append 4 more receipts sequentially
    for i in range(1, 5):
        r = _make_receipt("tenant_acme", height=i, parent_hash=chain.head_hash, receipt_id=f"rcp_{i}")
        chain.append(r)

    assert chain.chain_height == 5
    valid, msg = chain.verify_chain()
    assert valid is True
    assert msg == "CHAIN_VALID"


def test_anchor_interval_trigger():
    chain = TenantReceiptChain("tenant_acme", anchor_interval=3)
    r0 = _make_receipt("tenant_acme", height=0, parent_hash=GENESIS_PARENT_HASH, receipt_id="rcp_0")
    chain.append(r0)

    r1 = _make_receipt("tenant_acme", height=1, parent_hash=chain.head_hash, receipt_id="rcp_1")
    chain.append(r1)
    assert r1.ledger_anchor_eligible is False

    r2 = _make_receipt("tenant_acme", height=2, parent_hash=chain.head_hash, receipt_id="rcp_2")
    chain.append(r2)
    assert r2.ledger_anchor_eligible is False

    # Height 3 % 3 == 0 -> anchor eligible!
    r3 = _make_receipt("tenant_acme", height=3, parent_hash=chain.head_hash, receipt_id="rcp_3")
    chain.append(r3)
    assert r3.ledger_anchor_eligible is True

    head = chain.get_head()
    assert head.last_anchor_height == 3
    assert head.last_anchor_hash == r3.self_hash


def test_broken_parent_hash_rejected():
    chain = TenantReceiptChain("tenant_acme")
    r0 = _make_receipt("tenant_acme", height=0, parent_hash=GENESIS_PARENT_HASH, receipt_id="rcp_0")
    chain.append(r0)

    # Bad parent hash
    r1_tampered = _make_receipt("tenant_acme", height=1, parent_hash="sha256:" + "f" * 64, receipt_id="rcp_1")
    with pytest.raises(ChainVerificationError) as exc_info:
        chain.append(r1_tampered)
    assert "does not match chain head" in str(exc_info.value)


def test_height_gap_rejected():
    chain = TenantReceiptChain("tenant_acme")
    r0 = _make_receipt("tenant_acme", height=0, parent_hash=GENESIS_PARENT_HASH, receipt_id="rcp_0")
    chain.append(r0)

    # Skipping height 1 to height 2
    r_skip = _make_receipt("tenant_acme", height=2, parent_hash=chain.head_hash, receipt_id="rcp_skip")
    with pytest.raises(ChainVerificationError) as exc_info:
        chain.append(r_skip)
    assert "Invalid chain_height" in str(exc_info.value)


def test_cross_tenant_isolation_violation():
    chain_a = TenantReceiptChain("tenant_alpha")
    r0 = _make_receipt("tenant_alpha", height=0, parent_hash=GENESIS_PARENT_HASH, receipt_id="rcp_a0")
    chain_a.append(r0)

    # Tenant Beta receipt cannot be appended to Tenant Alpha chain
    r_b = _make_receipt("tenant_beta", height=1, parent_hash=chain_a.head_hash, receipt_id="rcp_b1")
    with pytest.raises(TenantIsolationViolation) as exc_info:
        chain_a.append(r_b)
    assert "tenant_beta" in str(exc_info.value)
    assert "tenant_alpha" in str(exc_info.value)


def test_stale_authority_epoch_rejected():
    chain = TenantReceiptChain("tenant_acme")
    r_stale = _make_receipt("tenant_acme", height=0, parent_hash=GENESIS_PARENT_HASH, epoch=3)

    # Trusted epoch is 10
    with pytest.raises(ChainVerificationError) as exc_info:
        chain.append(r_stale, trusted_epoch=10)
    assert "below trusted epoch" in str(exc_info.value)


def test_tampered_payload_detected_in_verification():
    chain = TenantReceiptChain("tenant_acme")
    r0 = _make_receipt("tenant_acme", height=0, parent_hash=GENESIS_PARENT_HASH, receipt_id="rcp_0")
    chain.append(r0)
    r1 = _make_receipt("tenant_acme", height=1, parent_hash=chain.head_hash, receipt_id="rcp_1")
    chain.append(r1)

    # Adversary tampers with r0's event payload in storage
    chain._receipts[0].event = "malicious.tampered.event"

    valid, msg = chain.verify_chain()
    assert valid is False
    assert "integrity failed: self_hash tampered" in msg


def test_signed_merkle_checkpoint_arthur_seal():
    """Validates the multi-tenant signed Merkle root checkpoint (Arthur Ed25519 Seal).

    Diagram:
        Tenant A Chain ─── Head A ┐
        Tenant B Chain ─── Head B ├─► Signed Merkle Root Checkpoint (Arthur Ed25519 Seal)
        Tenant C Chain ─── Head C ┘
    """
    from control_plane.security.receipt_chain import SovereignMerkleCheckpointGovernor

    # 1. Initialize chains for 3 tenants
    chain_a = TenantReceiptChain("tenant_a")
    chain_b = TenantReceiptChain("tenant_b")
    chain_c = TenantReceiptChain("tenant_c")

    # Append genesis receipts
    chain_a.append(_make_receipt("tenant_a", 0, GENESIS_PARENT_HASH, "rcp_a0"))
    chain_b.append(_make_receipt("tenant_b", 0, GENESIS_PARENT_HASH, "rcp_b0"))
    chain_c.append(_make_receipt("tenant_c", 0, GENESIS_PARENT_HASH, "rcp_c0"))

    # Append extra receipts
    chain_a.append(_make_receipt("tenant_a", 1, chain_a.head_hash, "rcp_a1"))
    chain_b.append(_make_receipt("tenant_b", 1, chain_b.head_hash, "rcp_b1"))

    # 2. Register with Governor
    gov = SovereignMerkleCheckpointGovernor()
    gov.register_chain(chain_a)
    gov.register_chain(chain_b)
    gov.register_chain(chain_c)

    # 3. Create signed checkpoint with Arthur Ed25519 Seal
    checkpoint = gov.create_signed_checkpoint(authority_epoch=42)

    assert checkpoint.schema_version == "camelot-checkpoint/1"
    assert checkpoint.merkle_root.startswith("sha256:")
    assert checkpoint.proof.signer == "king-arthur"
    assert checkpoint.proof.signature.startswith("ed25519:")
    assert len(checkpoint.proof.public_key) == 64
    assert len(checkpoint.tenant_heads) == 3

    # 4. Cryptographically verify the checkpoint seal
    valid, msg = SovereignMerkleCheckpointGovernor.verify_checkpoint(checkpoint)
    assert valid is True
    assert msg == "CHECKPOINT_SEAL_VALID"

    # 5. Generate and verify Merkle inclusion proof for Tenant B
    leaf_b, proof_b = gov.generate_inclusion_proof("tenant_b")
    assert len(proof_b) >= 1
    verified_b = SovereignMerkleCheckpointGovernor.verify_inclusion_proof(
        leaf_b, proof_b, checkpoint.merkle_root
    )
    assert verified_b is True

    # 6. Tamper test: Altering Tenant A's head breaks Merkle verification
    checkpoint.tenant_heads["tenant_a"]["head_hash"] = "sha256:" + "0" * 64
    valid_tampered, err = SovereignMerkleCheckpointGovernor.verify_checkpoint(checkpoint)
    assert valid_tampered is False
    assert "Merkle root mismatch" in err or "signature verification failed" in err

