# Contract Forge Canonicalization and Signing v1

## Scope

This profile applies to the additive v3 reforge contracts introduced in the Contract Forge vertical slice. Existing v1.2 contracts retain their current semantics until an ADR explicitly migrates them.

## Canonicalization: `camelot-c14n-json/1`

For the signing projection:

1. Remove the top-level `integrity` member entirely.
2. Normalize all JSON object keys and string values to Unicode NFC.
3. Signed contract schemas MUST NOT use floating-point numbers. Integers are permitted.
4. Serialize UTF-8 JSON with:
   - object keys sorted lexicographically by Unicode scalar value,
   - no insignificant whitespace,
   - JSON literals exactly `true`, `false`, `null`,
   - UTF-8 characters preserved rather than ASCII-escaped.
5. Compute SHA-256 over the canonical UTF-8 bytes.
6. Encode the digest as `sha256:<lowercase hex>`.

## Domain-separated Ed25519 signature

Each schema fixes a `signature_domain`, for example:

`camelot-signature:camelot-soul/1`

The signature input is:

```text
UTF8(signature_domain) || 0x00 || raw_sha256_digest_bytes
```

Sign with Ed25519. Store the signature as standard Base64.

A signature valid for one contract family is therefore not valid for another family even when content digests collide by construction or operator error.

## Verification order

```text
parse
 -> JSON Schema
 -> schema version
 -> canonicalize signing projection
 -> SHA-256 digest
 -> signature domain
 -> Ed25519 signature
 -> issuer/key trust
 -> tenant/workspace scope
 -> not-before / expiry
 -> lifecycle
 -> epoch/policy semantics where applicable
 -> accept or reject
```

Unknown major contract families reject by default.

## Authority rule

Cryptographic validity means only that a trusted issuer signed an object. It does not imply effect permission. Only Sentinel policy plus a current valid capability lease can authorize consequential execution.
