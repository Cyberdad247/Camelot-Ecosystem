from __future__ import annotations

import base64
import copy
import hashlib
import json
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "packages" / "contracts"


class ContractRejected(ValueError):
    pass


def _normalize(value):
    if isinstance(value, float):
        raise ContractRejected("camelot-c14n-json/1 forbids floating point")
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, list):
        return [_normalize(v) for v in value]
    if isinstance(value, dict):
        return {unicodedata.normalize("NFC", k): _normalize(v) for k, v in value.items()}
    return value


def canonical_bytes(value: dict) -> bytes:
    return json.dumps(
        _normalize(value),
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")


def signing_projection(obj: dict) -> dict:
    return {k: copy.deepcopy(v) for k, v in obj.items() if k != "integrity"}


def content_digest(obj: dict) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(signing_projection(obj))).hexdigest()


def full_object_digest(obj: dict) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(obj)).hexdigest()


def validate_schema(obj: dict, schema_name: str) -> None:
    with (SCHEMA_DIR / schema_name).open("r", encoding="utf-8") as fh:
        schema = json.load(fh)
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(obj),
        key=lambda e: list(e.path),
    )
    if errors:
        raise ContractRejected(errors[0].message)


def verify_signed(
    obj: dict,
    schema_name: str,
    keyring: Mapping[str, Ed25519PublicKey],
    *,
    now: datetime | None = None,
    accepted_lifecycles: set[str] | None = None,
) -> None:
    validate_schema(obj, schema_name)
    integ = obj["integrity"]
    expected_digest = content_digest(obj)
    if integ["digest"] != expected_digest:
        raise ContractRejected("digest mismatch")

    expected_domain = f"camelot-signature:{obj['schema_version']}"
    if integ["signature_domain"] != expected_domain:
        raise ContractRejected("signature domain mismatch")

    key = keyring.get(integ["signer_key_id"])
    if key is None:
        raise ContractRejected("untrusted signer")

    digest_bytes = bytes.fromhex(expected_digest.split(":", 1)[1])
    signature_input = expected_domain.encode("utf-8") + b"\x00" + digest_bytes
    try:
        key.verify(base64.b64decode(integ["signature"]), signature_input)
    except (InvalidSignature, ValueError) as exc:
        raise ContractRejected("invalid signature") from exc

    if now is None:
        now = datetime.now(timezone.utc)

    if "not_before" in obj:
        start = datetime.fromisoformat(obj["not_before"].replace("Z", "+00:00"))
        if now < start:
            raise ContractRejected("object not yet valid")
    if "expires_at" in obj:
        end = datetime.fromisoformat(obj["expires_at"].replace("Z", "+00:00"))
        if now >= end:
            raise ContractRejected("object expired")
    if "effective_at" in obj:
        effective = datetime.fromisoformat(obj["effective_at"].replace("Z", "+00:00"))
        if now < effective:
            raise ContractRejected("certificate not yet effective")

    if accepted_lifecycles is not None and obj.get("lifecycle") not in accepted_lifecycles:
        raise ContractRejected("lifecycle not admissible")
