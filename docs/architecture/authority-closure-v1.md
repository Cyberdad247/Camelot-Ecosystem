# Sprint 2 — Authority Closure + Signed Knight/Soul Admission

**Status:** additive v3 reforge reference implementation.  
**Boundary:** contracts/harness semantics only. The live VPS/runtime services must consume the same rules before this becomes a production capability.

## 1. Dynamic authority epoch admission

`camelot-authority-epoch/1` is the signed current-authority certificate used at new admission boundaries.

A receipt is admitted only when:

1. the epoch certificate validates under a trusted key,
2. its lifecycle is `ACTIVE`,
3. its authority domain matches the configured Crown domain,
4. the receipt validates against `camelot-receipt/1`,
5. `receipt.authority_epoch == current_certificate.authority_epoch`,
6. tenant scope matches,
7. receipt signer is trusted,
8. receipt proof verification succeeds where the runtime verifier is wired,
9. receipt chain height and parent hash exactly extend the current tenant chain.

Older receipts remain evidence/history. They are not admitted as new canonical transitions after an epoch increment. Future-epoch receipts are also rejected because connectivity or claimed freshness does not grant authority.

## 2. Signed Knight package

`camelot-knight-package/1` cryptographically binds:

- signed immutable Soul,
- existing `camelot-persona/1` competence profile,
- signed enterprise role,
- allowed Runes,
- allowed Pills,
- allowed effect classes,
- maximum risk tier,
- maximum cognition ceiling,
- explicit authority prohibitions.

The package itself is **not authority**. It defines the maximum shape of a Knight that Sentinel may later authorize.

## 3. Immutable Soul enforcement

The package stores the full-object digest of the signed Soul. A Soul mutation, even one that is re-signed independently, produces a different digest and therefore invalidates the package binding until a new Knight package is issued and reviewed.

## 4. Persona continuity preserved

This Sprint deliberately keeps the existing `camelot-persona/1` contract. The loader composes it with Soul and Enterprise Role rather than replacing it.

A persona can therefore retain name, communication style, competence, organizational relationships and governed memory across model-provider changes, while authority remains outside the persona.

## 5. Runtime handoff

The next consuming implementations should be:

- Receipt Service: call dynamic epoch admission before appending any new receipt.
- Sentinel / Knight Registry: load only signed active Knight packages.
- Context Compiler: resolve Soul + persona + role only after package admission.
- Node Agent: consume Sentinel's Effective Capability Set, never Knight package ceilings directly.

This keeps the constitutional rule intact:

> Identity may persist. Cognition may change. Authority must be current.
