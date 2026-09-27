# SPDX-License-Identifier: MIT
"""
Comprehensive Unit Test Suite for the 5 Ratified and Hardened Invariants:
- INVARIANT-1: Scarcity Governor & Memory Pinning
- INVARIANT-2: Zero-Latency SPSC Ring-Buffer IPC & Core Affinity
- INVARIANT-3: 64-Byte Bucket Padding & Isochronous Cadence
- INVARIANT-4: Spectral SVD Projection with 1.58-bit Ternary Residual
- INVARIANT-5: Z3 Formal SMT Ring Arithmetic Verification
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pytest

repo_root = Path(__file__).resolve().parent.parent
kernel_path = str(repo_root / "01_KERNEL")
# Unconditional front-insertion: other suite modules prepend entries holding
# a colliding top-level ``merlin.py`` (03_VAULT/training/configs); a guarded
# insert would leave 01_KERNEL behind it and shadow the package.
if kernel_path in sys.path:
    sys.path.remove(kernel_path)
sys.path.insert(0, kernel_path)

from merlin.invariants.hardened_invariants import HardenedInvariantsEngine
from merlin.invariants.ring_buffer_ipc import SPSCChannel, ThreadAffinityManager
from merlin.invariants.scarcity_governor import GovernorState, MemoryPinner, ScarcityGovernor
from merlin.invariants.side_channel_guard import IsochronousChannel, SideChannelGuard
from merlin.invariants.spectral_projection import SpectralProjectionEngine
from merlin.invariants.z3_ring_verifier import Z3RingVerifier


def test_invariant_1_scarcity_governor_hysteresis():
    """Verify Schmitt-trigger dual-threshold hysteresis and admission gating."""
    gov = ScarcityGovernor(high_watermark_gb=3.60, low_watermark_gb=3.30, hard_ceiling_gb=3.85)

    # 1. Starts in NORMAL
    assert gov.state == GovernorState.NORMAL
    assert gov.evaluate_task_admission("SPECULATIVE") is True

    # 2. Cross high watermark (3.65 GB) -> triggers SHEDDING
    rss_365 = int(3.65 * (1024**3))
    gov.update_rss(rss_365)
    assert gov.state == GovernorState.SHEDDING
    assert gov.evaluate_task_admission("SPECULATIVE") is False
    assert gov.evaluate_task_admission("CRITICAL") is True

    # 3. Inside deadband (3.45 GB) -> MUST REMAIN IN SHEDDING (hysteresis)
    rss_345 = int(3.45 * (1024**3))
    gov.update_rss(rss_345)
    assert gov.state == GovernorState.SHEDDING
    assert gov.evaluate_task_admission("SPECULATIVE") is False

    # 4. Cross low watermark (3.25 GB) -> resets to NORMAL
    rss_325 = int(3.25 * (1024**3))
    gov.update_rss(rss_325)
    assert gov.state == GovernorState.NORMAL
    assert gov.evaluate_task_admission("SPECULATIVE") is True

    # 5. Cross hard ceiling (3.86 GB) -> triggers CRITICAL
    rss_386 = int(3.86 * (1024**3))
    gov.update_rss(rss_386)
    assert gov.state == GovernorState.CRITICAL
    assert gov.evaluate_task_admission("CRITICAL") is False
    assert gov.evaluate_task_admission("ROOT") is True


def test_invariant_1_memory_pinner():
    """Verify cross-platform memory pinner interface."""
    pinner = MemoryPinner()
    assert isinstance(pinner.is_windows, bool)
    assert pinner.total_pinned_bytes() == 0


def test_invariant_2_spsc_ring_buffer_and_affinity():
    """Verify lockless SPSC queue and thread affinity manager."""
    # Enforce power-of-two requirement
    with pytest.raises(AssertionError):
        SPSCChannel(capacity=1000)

    ring = SPSCChannel[str](capacity=8)
    assert ring.capacity == 8
    assert ring.mask == 7
    assert ring.is_empty() is True

    # Fill ring to capacity
    for i in range(8):
        ok = ring.push("sender", "recipient", f"payload_{i}")
        assert ok is True

    assert ring.is_full() is True
    # Next push should fail (no overwrite)
    assert ring.push("sender", "recipient", "overflow") is False

    # Pop in strict FIFO order
    for i in range(8):
        msg = ring.pop()
        assert msg is not None
        assert msg.payload == f"payload_{i}"

    assert ring.is_empty() is True
    assert ring.pop() is None

    # Affinity and deadline test
    affinity = ThreadAffinityManager()
    t0 = time.perf_counter_ns()
    affinity.record_latency(t0)
    assert affinity.verify_deadline_compliance(deadline_ms=12.0) is True


def test_invariant_3_side_channel_guard_and_cadence():
    """Verify 64-byte bucket padding and isochronous ticks with decoy frames."""
    guard = SideChannelGuard()

    # Bucket padding checks
    data = b"sovereign_agent_pulse"
    padded = guard.pad(data)
    assert len(padded) % 64 == 0

    unpadded, is_decoy = guard.unpad(padded)
    assert unpadded == data
    assert is_decoy is False

    # Decoy frame check
    decoy = guard.create_decoy_frame()
    assert len(decoy) == 64
    _, decoy_flag = guard.unpad(decoy)
    assert decoy_flag is True

    # Isochronous channel check
    iso = IsochronousChannel(interval_ms=20.0)
    iso.enqueue(b"real_payload")

    # Tick 1: Should transmit real payload (padded)
    frame1 = iso.tick_once()
    assert frame1.is_decoy is False
    assert frame1.total_bytes % 64 == 0

    # Tick 2: Queue empty -> should transmit decoy null-frame
    frame2 = iso.tick_once()
    assert frame2.is_decoy is True
    assert frame2.total_bytes == 64


def test_invariant_4_spectral_projection():
    """Verify rank-64 SVD decomposition and 1.58-bit ternary residual correction."""
    engine = SpectralProjectionEngine(rank=64, divergence_threshold=0.00038)

    # Realistic decaying spectrum matrix
    u_rand, _ = np.linalg.qr(np.random.randn(128, 128))
    v_rand, _ = np.linalg.qr(np.random.randn(128, 128))
    s_decay = np.array([1.0 / (i + 1)**2 for i in range(128)], dtype=np.float32)
    w = np.dot(u_rand * s_decay, v_rand).astype(np.float32)

    u_k, s_k, vt_k, ternary_res, alpha = engine.factorize_weight_matrix(w)
    assert u_k.shape == (128, 64)
    assert len(s_k) == 64
    assert set(np.unique(ternary_res)).issubset({-1, 0, 1})

    x = np.random.randn(128).astype(np.float32)
    anchor = np.dot(w, x)

    res = engine.project_and_correct(x, u_k, s_k, vt_k, ternary_res, alpha, anchor_vec=anchor)
    assert res.error_bound_satisfied is True
    assert res.cosine_divergence <= 0.00038


def test_invariant_5_z3_ring_verifier():
    """Verify formal Z3 SMT machine-checked proofs and certificate generation."""
    verifier = Z3RingVerifier(default_capacity=1024)

    t1 = verifier.prove_bitwise_mask_equivalence(capacity=1024)
    assert t1 is True

    t2 = verifier.prove_slot_isolation_and_no_overflow(capacity=1024)
    assert t2 is True

    receipt = verifier.generate_proof_certificate(repo_root=repo_root)
    assert receipt.proved is True
    assert receipt.theorems_verified == 2
    assert len(receipt.proof_hash) == 64

    proof_file = repo_root / "03_VAULT" / "runtime_state" / "proofs" / "ring_buffer_z3.proof"
    assert proof_file.exists()


def test_unified_hardened_invariants_engine():
    """Verify the master HardenedInvariantsEngine facade."""
    engine = HardenedInvariantsEngine(ring_capacity=1024, svd_rank=64)
    status = engine.verify_all_invariants()
    assert status.all_invariants_operational is True
    assert status.invariant_1_governor.state == GovernorState.NORMAL
    assert status.invariant_3_bucket_size == 64
    assert status.invariant_4_rank == 64
    assert status.invariant_5_z3_proof_ok is True
