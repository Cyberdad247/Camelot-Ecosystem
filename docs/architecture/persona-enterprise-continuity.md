# Persona Enterprise Continuity Foundation

**Status:** v3 reforge implementation foundation, additive to the v1.2 contract family.  
**Authority rule:** this document does not supersede the SADD. Sentinel remains the sole policy / lease / revocation authority.

## Purpose

Camelot-OS must preserve its persona-based digital-enterprise character while hardening the machine authority plane. Personas are not decorative UI. They are persistent human-facing organizational entities with identity continuity, role continuity, relational continuity, memory continuity, and communication continuity.

The reforge therefore separates three layers:

1. **Persona Continuity Plane** — Soul, enterprise role, relationships, communication profile, governed memory, skills and historical continuity.
2. **Cognitive Runtime** — replaceable model engines, context compilation, Runes, Pills, routing and fallback.
3. **Sovereign Runtime** — Sentinel policy, epochs, leases, Bifrost admission/transport, VFS preflight, bounded execution, Gideon verification, Arthur resolution, receipts and canonical state.

A persona may persist across model changes. Model identity is not persona identity.

## Non-negotiable invariants

- A Soul defines identity and constitutional limits; it never grants effect authority.
- An Enterprise Role defines organizational responsibility and relationships; it never grants effect authority.
- A Spark is short-lived compiled task context; it expires and never carries reusable authority.
- A Rune defines reasoning procedure; `grants_capabilities=false` is structural.
- A Pill defines possible executable reach and ceilings; actual permission still requires Sentinel policy plus a current lease.
- Persona memory may retain enterprise history, relationships, preferences, decisions, and procedures. It may never encode reusable leases, signing keys, epoch-promotion rights, or remembered permission.
- A model/provider is replaceable. The persona survives because continuity comes from signed Camelot artifacts and governed memory.
- Human operators retain final authority over consequential effects under the existing risk/quorum model.

## Digital enterprise model

```text
Human intent
    |
    v
Persona / enterprise layer
Anya | Merlin | Synthetos | Helios | Heimdall | specialist departments
    |
    v
Cognitive runtime
model routing | context compiler | Rune | Pill | skills
    |
    v
Sovereign runtime
Sentinel | Epoch | Bifrost | VFS | Node Agent | Gideon | Arthur | Ledger
    |
    v
Verified digital / physical effects
```

The enterprise graph is executable organizational metadata, not authority. It may express responsibility, delegation targets, collaboration, escalation and shared-context scope. Any consequential action produced by that organization still enters the same effect-manifest -> policy -> lease -> preflight -> execution -> verification -> resolution -> receipt pipeline.

## Contract mapping

| Concept | Contract |
|---|---|
| Persistent constitutional persona identity | `camelot-soul/1` |
| Department / relationships / organizational continuity | `camelot-enterprise-role/1` |
| Existing runtime persona competence contract | `camelot-persona/1` |
| Short-lived task context | `camelot-spark/1` |
| Reasoning procedure | `camelot-rune/1` |
| Bounded executable package | `camelot-pill/1` |
| Provisional learned memory | `camelot-memory-candidate/1` |
| Governed active memory | `camelot-memory-object/1` |
| Sentinel-compiled executor projection | `camelot-effective-capability-set/1` |

## Authority attenuation

Cognition level and risk tier remain separate vocabularies. `L0..L5` describes cognitive / offline effect ceilings from the continuity model. `T0..T4` remains the current risk/quorum taxonomy for effect authorization.

The effective executable ceiling is always the most restrictive applicable layer:

```text
effective ceiling =
min(policy, persona, spark, pill, cartridge, lease)
```

A higher ceiling in one artifact can never widen a lower ceiling elsewhere.

## Hybrid enterprise principle

Camelot's target is not human replacement. The architecture deliberately combines:

- **Humans:** purpose, values, consent, judgment and consequential approval.
- **Persistent digital personas:** continuity, translation, coordination, specialization and organizational memory.
- **Machine runtime:** speed, verification, cryptographic authority, bounded execution and auditability.

This is the foundation for organic/machine hybrid enterprise evolution while keeping authority outside model memory and personality.
