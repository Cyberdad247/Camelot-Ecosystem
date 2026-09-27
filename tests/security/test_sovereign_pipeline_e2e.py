# SPDX-License-Identifier: MIT
"""End-to-End & Adversarial Test Suite for Sovereign Pipeline (Phase 9).
=======================================================================
Validates the complete 6-stage lifecycle orchestrator:
    - Stage 1: Ingress Idempotency, Compound Keys, and AuthorityVector Dominance.
    - Stage 2: Zero-Trust Security Gate (Allow, Require Approval, Deny) and Capability Lease.
    - Stage 3: Bounded Sandbox Execution (<50MB RAM, VFS confinement, Evidence streaming).
    - Stage 4: Sir Gideon 13-Gate Independent Audit (Verdict signing, gate checks, block rules).
    - Stage 5: King Arthur Sovereign Resolution & Atomic Merkle Chain Commit.
    - Stage 6: Telemetry Streaming & BFF Pub-Sub Integration.
"""
from __future__ import annotations


from control_plane.dispatch.idempotency_guardian import (
    DurableIdempotencyStore,
    FastMutexAccelerator,
    IdempotencyDecision,
    IdempotencyGuardian,
    IdempotencyStatus,
)
from control_plane.pipeline.sovereign_pipeline import (
    PipelineStage,
    PipelineStatus,
    SovereignPipeline,
    TaskProposal,
)
from control_plane.sandbox.wasmtime_runner import (
    HostEvidenceEnclave,
    HostVFSEnclave,
    WasmtimeSandboxRunner,
)
from control_plane.security.arthur_resolution import (
    ArthurResolutionGovernor,
)
from control_plane.security.authority_vector import AuthorityVector
from control_plane.security.receipt_chain import (
    SovereignMerkleCheckpointGovernor,
)
from control_plane.security.sir_gideon import GideonVerifier
from security.warden import SecurityWarden


def make_pipeline(
    auto_ratify_high_risk: bool = False,
    trusted_authority_vector: AuthorityVector | None = None,
) -> SovereignPipeline:
    """Helper to instantiate an isolated SovereignPipeline with in-memory stores."""
    idempotency_store = DurableIdempotencyStore(":memory:")
    fast_mutex = FastMutexAccelerator(default_ttl_sec=5.0)
    guardian = IdempotencyGuardian(store=idempotency_store, fast_mutex=fast_mutex)
    warden = SecurityWarden()
    sandbox = WasmtimeSandboxRunner()
    gideon = GideonVerifier()
    arthur = ArthurResolutionGovernor()
    checkpoint_gov = SovereignMerkleCheckpointGovernor()

    return SovereignPipeline(
        idempotency_guardian=guardian,
        security_warden=warden,
        sandbox_runner=sandbox,
        gideon_verifier=gideon,
        arthur_governor=arthur,
        checkpoint_governor=checkpoint_gov,
        trusted_authority_vector=trusted_authority_vector or AuthorityVector.genesis(),
        auto_ratify_high_risk=auto_ratify_high_risk,
    )


MIN_TIERS = {
    "ro.fetch": "T0",
    "ro.audit": "T0",
    "internal.synth": "T1",
    "workspace.test": "T1",
    "workspace.patch": "T2",
    "promote.worktree.merge": "T3",
    "promote.deploy": "T4",
}


def make_proposal(
    task_id: str = "task_sovereign_01",
    tenant_id: str = "tenant_alpha_01",
    correlation_id: str = "cor_alpha_01",
    idempotency_key: str = "client_key_01",
    intent: str = "ro.fetch read system documentation",
    effect_class: str = "ro.fetch",
    declared_risk_tier: str | None = None,
    authority_vector: list[int] | None = None,
    manifest: dict | None = None,
    operator_approved: bool = False,
    guest_fn = None,
    simulated_memory_mb: float = 12.0,
    target_paths: list[str] | None = None,
    virtual_fs: dict | None = None,
    test_runs: list[dict] | None = None,
    arthur_resolution = None,
) -> TaskProposal:
    """Helper to build a valid TaskProposal conforming to Sir Gideon and SADD requirements."""
    if declared_risk_tier is None:
        declared_risk_tier = MIN_TIERS.get(effect_class, "T1")

    if manifest is None:
        manifest = {
            "schema_version": "effect-manifest/1",
            "task_id": task_id,
            "target_paths": target_paths or ["vfs/workspaces", "docs/architecture"],
            "effect_class": effect_class,
            "declared_risk_tier": declared_risk_tier,
            "max_memory_mb": 25.0,
            "requires_cleanup": False,
            "rollback_snapshot_ref": "snap_test_01",
        }
    else:
        if "effect_class" not in manifest:
            manifest["effect_class"] = effect_class
        if "requires_cleanup" not in manifest:
            manifest["requires_cleanup"] = False
        if "rollback_snapshot_ref" not in manifest:
            manifest["rollback_snapshot_ref"] = "snap_test_01"
        if "declared_risk_tier" not in manifest:
            manifest["declared_risk_tier"] = declared_risk_tier

    if authority_vector is None:
        authority_vector = [1, 1, 0, 1, 1, 1]

    return TaskProposal(
        task_id=task_id,
        tenant_id=tenant_id,
        correlation_id=correlation_id,
        idempotency_key=idempotency_key,
        manifest=manifest,
        authority_vector=authority_vector,
        intent=intent,
        effect_class=effect_class,
        declared_risk_tier=declared_risk_tier,
        target_paths=target_paths or ["vfs/workspaces", "docs/architecture"],
        guest_fn=guest_fn,
        simulated_memory_mb=simulated_memory_mb,
        virtual_fs=virtual_fs,
        test_runs=test_runs,
        operator_approved=operator_approved,
        arthur_resolution=arthur_resolution,
    )


# =============================================================================
# 1. Happy Path End-to-End Execution
# =============================================================================

def test_pipeline_e2e_happy_path():
    pipeline = make_pipeline()
    proposal = make_proposal(
        task_id="task_happy_01",
        tenant_id="tenant_omega_01",
        intent="ro.fetch inspect system status",
        effect_class="ro.fetch",
        declared_risk_tier="T1",
        virtual_fs={"docs/architecture/spec.md": "# Camelot Spec"},
    )

    result = pipeline.execute(proposal)

    assert result.status == PipelineStatus.SUCCESS
    assert result.current_stage == PipelineStage.TELEMETRY_DISPATCH
    assert result.idempotency_decision == IdempotencyDecision.PROCEED
    assert result.error_message is None
    assert result.security_decision is not None
    assert result.security_decision.decision == "allow"
    assert result.lease is not None
    assert result.lease["lease_id"].startswith("lease_")
    assert result.execution_envelope is not None
    assert result.execution_envelope.status == "SUCCESS"
    assert result.gideon_verdict is not None
    assert result.gideon_verdict.verdict == "pass"
    assert result.receipt is not None
    assert result.receipt.chain_height == 0
    assert result.receipt.parent_hash.startswith("sha256:")
    assert len(result.telemetry_events) >= 3

    # Check chain head
    chain = pipeline.get_tenant_chain("tenant_omega_01")
    assert chain.chain_height == 1
    assert chain.head_hash == result.receipt.self_hash


# =============================================================================
# 2. Idempotency Replay Protection & Payload Mismatch
# =============================================================================

def test_pipeline_idempotency_replay_protection():
    pipeline = make_pipeline()
    proposal = make_proposal(
        task_id="task_replay_01",
        tenant_id="tenant_omega_01",
        idempotency_key="key_replay_01",
    )

    # First execution succeeds
    res1 = pipeline.execute(proposal)
    assert res1.status == PipelineStatus.SUCCESS
    assert res1.idempotency_decision == IdempotencyDecision.PROCEED

    # Second execution with identical key & manifest returns REPLAY
    res2 = pipeline.execute(proposal)
    assert res2.status == PipelineStatus.REPLAYED
    assert res2.idempotency_decision == IdempotencyDecision.REPLAY
    assert res2.receipt is None  # stages 2-5 bypassed

    # Tenant chain height remains 1 (no duplicate receipt appended)
    chain = pipeline.get_tenant_chain("tenant_omega_01")
    assert chain.chain_height == 1


def test_pipeline_idempotency_payload_mismatch():
    pipeline = make_pipeline()
    prop1 = make_proposal(
        task_id="task_mismatch_01",
        tenant_id="tenant_omega_01",
        idempotency_key="key_mismatch_01",
        manifest={"schema_version": "effect-manifest/1", "version": 1, "task_id": "task_mismatch_01"},
    )

    res1 = pipeline.execute(prop1)
    assert res1.status == PipelineStatus.SUCCESS

    # Attempt to reuse the same idempotency key with a mutated manifest
    prop2 = make_proposal(
        task_id="task_mismatch_01",
        tenant_id="tenant_omega_01",
        idempotency_key="key_mismatch_01",
        manifest={"schema_version": "effect-manifest/1", "version": 2, "task_id": "task_mismatch_01", "tampered": True},
    )

    res2 = pipeline.execute(prop2)
    assert res2.status == PipelineStatus.BLOCKED
    assert res2.idempotency_decision == IdempotencyDecision.REJECTED
    assert "IDEMPOTENCY_PAYLOAD_MISMATCH" in res2.error_message


def test_pipeline_idempotency_conflict_in_flight():
    pipeline = make_pipeline()
    prop = make_proposal(
        task_id="task_conflict_01",
        tenant_id="tenant_omega_01",
        idempotency_key="key_conflict_01",
    )

    # Acquire fast mutex lock manually to simulate in-flight execution
    pipeline.idempotency_guardian.fast_mutex.try_acquire("tenant_omega_01", "key_conflict_01", ttl_sec=10.0)

    res = pipeline.execute(prop)
    assert res.status == PipelineStatus.CONFLICT
    assert res.idempotency_decision == IdempotencyDecision.CONFLICT
    assert res.retry_after_sec is not None
    assert res.retry_after_sec >= 1


# =============================================================================
# 3. Authority Vector Evaluation (Revocation & Drift)
# =============================================================================

def test_pipeline_authority_vector_revocation_blocked():
    # Host vector has active revocation counter (r_revocation = 2)
    host_vec = AuthorityVector(1, 1, 2, 1, 1, 1)
    pipeline = make_pipeline(trusted_authority_vector=host_vec)

    # Proposal has stale revocation counter (r_revocation = 0)
    proposal = make_proposal(
        task_id="task_revoked_01",
        authority_vector=[1, 1, 0, 1, 1, 1],
    )

    res = pipeline.execute(proposal)
    assert res.status == PipelineStatus.BLOCKED
    assert res.current_stage == PipelineStage.INGRESS_IDEMPOTENCY
    assert "[AUTHORITY_VECTOR_REJECTED]" in res.error_message
    assert "REVOKED" in res.error_message


def test_pipeline_authority_vector_contract_drift_blocked():
    # Host vector has contract revision 1
    host_vec = AuthorityVector(1, 1, 0, 1, 1, 1)
    pipeline = make_pipeline(trusted_authority_vector=host_vec)

    # Proposal claims contract revision 2
    proposal = make_proposal(
        task_id="task_drift_01",
        authority_vector=[1, 1, 0, 1, 1, 2],
    )

    res = pipeline.execute(proposal)
    assert res.status == PipelineStatus.BLOCKED
    assert res.current_stage == PipelineStage.INGRESS_IDEMPOTENCY
    assert "CONTRACT_DRIFT" in res.error_message


# =============================================================================
# 4. Zero-Trust Security Gate (Deny & Approval-Required)
# =============================================================================

def test_pipeline_security_gate_critical_deny_blocked():
    pipeline = make_pipeline()
    proposal = make_proposal(
        task_id="task_deny_01",
        tenant_id="tenant_omega_01",
        idempotency_key="key_deny_01",
        intent="rm -rf /",  # Critical destructive command
        effect_class="workspace.patch",
    )

    res = pipeline.execute(proposal)
    assert res.status == PipelineStatus.BLOCKED
    assert res.current_stage == PipelineStage.SECURITY_GATE
    assert res.security_decision.decision == "deny"
    assert "SECURITY BLOCK" in res.error_message

    # Ensure idempotency record was rejected
    rec = pipeline.idempotency_guardian.store.get_by_key("key_deny_01", "tenant_omega_01")
    assert rec.status == IdempotencyStatus.REJECTED


def test_pipeline_security_gate_approval_required_unapproved():
    pipeline = make_pipeline()
    proposal = make_proposal(
        task_id="task_approval_01",
        tenant_id="tenant_omega_01",
        intent="workspace.patch update component config",
        effect_class="workspace.patch",
        operator_approved=False,
    )

    res = pipeline.execute(proposal)
    assert res.status == PipelineStatus.BLOCKED
    assert res.current_stage == PipelineStage.SECURITY_GATE
    assert res.security_decision.decision == "require_approval"
    assert "APPROVAL REQUIRED" in res.error_message


def test_pipeline_security_gate_approval_required_approved_success():
    pipeline = make_pipeline()
    proposal = make_proposal(
        task_id="task_approved_01",
        tenant_id="tenant_omega_01",
        intent="workspace.patch update component config",
        effect_class="workspace.patch",
        operator_approved=True,
    )

    res = pipeline.execute(proposal)
    assert res.status == PipelineStatus.SUCCESS
    assert res.security_decision.decision == "require_approval"
    assert res.receipt is not None


# =============================================================================
# 5. Bounded Sandbox Execution (VFS Confinement & Hardware Memory Limit)
# =============================================================================

def test_pipeline_bounded_runtime_vfs_confinement_breach():
    pipeline = make_pipeline()

    # Guest function attempts path traversal outside leased read scopes
    def malicious_guest(vfs: HostVFSEnclave, ev: HostEvidenceEnclave):
        vfs.read("../etc/shadow")

    proposal = make_proposal(
        task_id="task_escape_01",
        tenant_id="tenant_omega_01",
        target_paths=["vfs/workspaces"],
        guest_fn=malicious_guest,
    )

    res = pipeline.execute(proposal)
    assert res.status == PipelineStatus.BLOCKED
    assert res.current_stage == PipelineStage.BOUNDED_EXECUTION
    assert "[VFS_CONFINEMENT_BREACH]" in res.error_message


def test_pipeline_bounded_runtime_memory_exceeded():
    pipeline = make_pipeline()
    proposal = make_proposal(
        task_id="task_oom_01",
        tenant_id="tenant_omega_01",
        simulated_memory_mb=60.0,  # Exceeds the 50MB Sovereign RAM hard cap
    )

    res = pipeline.execute(proposal)
    assert res.status == PipelineStatus.BLOCKED
    assert res.current_stage == PipelineStage.BOUNDED_EXECUTION
    assert "[WASI_OOM_GUARD]" in res.error_message


# =============================================================================
# 6. Sir Gideon 13-Gate Audit & Arthur Sovereign Override
# =============================================================================

def test_pipeline_gideon_audit_failure_blocks_pipeline():
    pipeline = make_pipeline()

    # Proposal with failing test runs (Gate 4 failure)
    failing_test_runs = [
        {"suite_id": "suite_core_01", "status": "failed", "failed": 3, "passed": 10}
    ]

    proposal = make_proposal(
        task_id="task_gideon_fail_01",
        tenant_id="tenant_omega_01",
        test_runs=failing_test_runs,
    )

    res = pipeline.execute(proposal)
    assert res.status == PipelineStatus.BLOCKED
    assert res.current_stage == PipelineStage.INDEPENDENT_AUDIT
    assert res.gideon_verdict.verdict == "block"
    assert any("TEST_RESULT_VALIDITY" in r for r in res.gideon_verdict.block_reasons)

    # Verify no receipt committed to chain
    chain = pipeline.get_tenant_chain("tenant_omega_01")
    assert chain.chain_height == 0


def test_pipeline_gideon_block_with_arthur_sovereign_override():
    pipeline = make_pipeline()

    # Gideon would block due to failing tests
    failing_test_runs = [
        {"suite_id": "suite_core_01", "status": "failed", "failed": 1, "passed": 5}
    ]

    # King Arthur issues a signed SOVEREIGN_OVERRIDE resolution
    override_res = pipeline.arthur_governor.create_resolution(
        directive_type="SOVEREIGN_OVERRIDE",
        target_scope="task_override_01",
        rationale="Emergency hotfix approved by King Arthur under emergency protocol.",
        authority_vector=[1, 1, 0, 1, 1, 1],
    )

    proposal = make_proposal(
        task_id="task_override_01",
        tenant_id="tenant_omega_01",
        test_runs=failing_test_runs,
        arthur_resolution=override_res,
    )

    res = pipeline.execute(proposal)
    assert res.status == PipelineStatus.SUCCESS
    assert res.gideon_verdict.verdict == "block"
    assert res.arthur_resolution.directive_type == "SOVEREIGN_OVERRIDE"
    assert res.receipt is not None
    assert res.receipt.proof.signer == "king-arthur"


# =============================================================================
# 7. High-Risk Tier (T3/T4) Sovereign Crown Requirement
# =============================================================================

def test_pipeline_high_risk_tier_t3_requires_arthur_crown():
    pipeline = make_pipeline(auto_ratify_high_risk=False)
    proposal = make_proposal(
        task_id="task_highrisk_01",
        tenant_id="tenant_omega_01",
        declared_risk_tier="T3",
        intent="promote.worktree.merge release merge",
        effect_class="promote.worktree.merge",
        operator_approved=True,
    )

    res = pipeline.execute(proposal)
    assert res.status == PipelineStatus.ERROR
    assert res.current_stage == PipelineStage.SOVEREIGN_RESOLUTION
    assert "[ARTHUR_CROWN_REQUIRED]" in res.error_message


def test_pipeline_high_risk_tier_t3_auto_ratify():
    pipeline = make_pipeline(auto_ratify_high_risk=True)
    proposal = make_proposal(
        task_id="task_autoratify_01",
        tenant_id="tenant_omega_01",
        declared_risk_tier="T3",
        intent="promote.worktree.merge release merge",
        effect_class="promote.worktree.merge",
        operator_approved=True,
    )

    res = pipeline.execute(proposal)
    assert res.status == PipelineStatus.SUCCESS
    assert res.arthur_resolution is not None
    assert res.arthur_resolution.directive_type == "CONSENSUS_RATIFICATION"
    assert res.receipt.declared_risk_tier == "T3"


# =============================================================================
# 8. Per-Tenant Merkle Receipt Chain Integrity & Isolation
# =============================================================================

def test_pipeline_per_tenant_merkle_chain_integrity():
    pipeline = make_pipeline()

    # Append 3 sequential receipts
    for i in range(3):
        prop = make_proposal(
            task_id=f"task_seq_{i:02d}",
            tenant_id="tenant_merkle_01",
            idempotency_key=f"key_seq_{i:02d}",
        )
        res = pipeline.execute(prop)
        assert res.status == PipelineStatus.SUCCESS

    chain = pipeline.get_tenant_chain("tenant_merkle_01")
    assert chain.chain_height == 3
    valid, msg = chain.verify_chain()
    assert valid is True
    assert msg == "CHAIN_VALID"


def test_pipeline_telemetry_streaming_pubsub():
    pipeline = make_pipeline()
    emitted_events: list[dict] = []

    def subscriber(evt: dict):
        emitted_events.append(evt)

    pipeline.subscribe_telemetry(subscriber)

    proposal = make_proposal(
        task_id="task_telemetry_01",
        tenant_id="tenant_omega_01",
    )

    res = pipeline.execute(proposal)
    assert res.status == PipelineStatus.SUCCESS
    assert len(emitted_events) >= 3
    kinds = [e.get("kind") for e in emitted_events]
    assert "pipeline.stage2.lease_issued" in kinds
    assert "pipeline.stage4.gideon_passed" in kinds
    assert "pipeline.stage6.committed" in kinds
