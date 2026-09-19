from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from contract_runtime import ContractRejected, validate_schema, verify_signed


@dataclass(frozen=True)
class ReceiptHead:
    tenant_id: str
    chain_height: int
    self_hash: str


@dataclass(frozen=True)
class ReceiptAdmissionResult:
    receipt_id: str
    authority_epoch: int
    next_chain_height: int


def verify_current_epoch_certificate(
    certificate: dict,
    keyring: Mapping[str, Ed25519PublicKey],
    *,
    expected_domain: str,
    now,
) -> int:
    verify_signed(
        certificate,
        "authority-epoch.schema.json",
        keyring,
        now=now,
        accepted_lifecycles={"ACTIVE"},
    )
    if certificate["authority_domain"] != expected_domain:
        raise ContractRejected("authority domain mismatch")
    return certificate["authority_epoch"]


def admit_receipt(
    receipt: dict,
    *,
    current_epoch_certificate: dict,
    epoch_keyring: Mapping[str, Ed25519PublicKey],
    expected_authority_domain: str,
    expected_tenant_id: str,
    current_head: ReceiptHead | None,
    trusted_receipt_signers: set[str],
    now,
    verify_receipt_signature: Callable[[dict], bool] | None = None,
) -> ReceiptAdmissionResult:
    current_epoch = verify_current_epoch_certificate(
        current_epoch_certificate,
        epoch_keyring,
        expected_domain=expected_authority_domain,
        now=now,
    )

    validate_schema(receipt, "receipt.schema.json")

    receipt_epoch = receipt["authority_epoch"]
    if receipt_epoch != current_epoch:
        direction = "stale" if receipt_epoch < current_epoch else "future"
        raise ContractRejected(f"{direction} authority epoch")

    if receipt["tenant_id"] != expected_tenant_id:
        raise ContractRejected("cross-tenant receipt")

    if receipt["proof"]["signer"] not in trusted_receipt_signers:
        raise ContractRejected("untrusted receipt signer")

    if verify_receipt_signature is not None and not verify_receipt_signature(receipt):
        raise ContractRejected("receipt signature verification failed")

    if current_head is None:
        if receipt["chain_height"] != 0:
            raise ContractRejected("genesis receipt height must be zero")
        if receipt["parent_hash"] != "sha256:" + ("0" * 64):
            raise ContractRejected("genesis receipt parent hash invalid")
    else:
        if current_head.tenant_id != expected_tenant_id:
            raise ContractRejected("chain head tenant mismatch")
        if receipt["chain_height"] != current_head.chain_height + 1:
            raise ContractRejected("receipt chain height discontinuity")
        if receipt["parent_hash"].lower() != current_head.self_hash.lower():
            raise ContractRejected("receipt parent hash mismatch")

    return ReceiptAdmissionResult(
        receipt_id=receipt["receipt_id"],
        authority_epoch=current_epoch,
        next_chain_height=receipt["chain_height"],
    )
