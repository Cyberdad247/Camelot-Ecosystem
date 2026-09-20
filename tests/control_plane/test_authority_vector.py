# SPDX-License-Identifier: MIT
"""Unit tests for control_plane.security.authority_vector."""
import pytest
from control_plane.security.authority_vector import AuthorityVector


def test_genesis_authority_vector():
    vec = AuthorityVector.genesis()
    assert vec.to_tuple() == (1, 1, 0, 1, 1, 1)
    assert vec.to_list() == [1, 1, 0, 1, 1, 1]
    assert len(vec.canonical_digest()) == 64


def test_from_sequence():
    vec = AuthorityVector.from_sequence([2, 3, 4, 5, 6, 7])
    assert vec.e_leadership == 2
    assert vec.r_policy == 3
    assert vec.r_revocation == 4
    assert vec.r_registry == 5
    assert vec.r_identity == 6
    assert vec.r_contract == 7

    with pytest.raises(ValueError):
        AuthorityVector.from_sequence([1, 2, 3])  # too short


def test_monotonic_dominance():
    v1 = AuthorityVector(2, 2, 2, 2, 2, 2)
    v2 = AuthorityVector(1, 2, 2, 2, 2, 2)
    v3 = AuthorityVector(3, 1, 2, 2, 2, 2)

    assert v1.dominates(v2) is True
    assert v2.dominates(v1) is False
    assert v1.dominates(v3) is False  # v3 has higher leadership, but lower policy


def test_validate_lease_revocation():
    host = AuthorityVector(1, 1, 5, 1, 1, 1)
    lease_valid = AuthorityVector(1, 1, 5, 1, 1, 1)
    lease_revoked = AuthorityVector(1, 1, 4, 1, 1, 1)

    ok, msg = host.validate_lease(lease_valid)
    assert ok is True
    assert msg == "OK"

    ok, msg = host.validate_lease(lease_revoked)
    assert ok is False
    assert "REVOKED" in msg


def test_validate_lease_contract_drift():
    host = AuthorityVector(1, 1, 0, 1, 1, 2)
    lease_stale_contract = AuthorityVector(1, 1, 0, 1, 1, 1)

    ok, msg = host.validate_lease(lease_stale_contract)
    assert ok is False
    assert "CONTRACT_DRIFT" in msg


def test_bumps():
    v = AuthorityVector.genesis()
    assert v.bump_leadership().e_leadership == 2
    assert v.bump_policy().r_policy == 2
    assert v.bump_revocation().r_revocation == 1
    assert v.bump_registry().r_registry == 2
    assert v.bump_identity().r_identity == 2
    assert v.bump_contract().r_contract == 2
