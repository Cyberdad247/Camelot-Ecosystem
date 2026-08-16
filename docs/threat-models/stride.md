# Camelot-OS Threat Model (STRIDE)

**Authoritative companion:** `Camelot-OS SADD + LLDD v1.2.md` (this directory's parent).
**Version:** v1.2 (delta on v1.1 — adds two-person rule, trust bands, witness, mobile epoch cache, cache-namespace HMAC, receipt chain canonicality).
**Scope:** All six planes of Camelot-OS (Experience, Control, Safety, Cloudbrain Execution, Evidence Data, Evidence Audit) and the active/standby Hub twin.
**Out of scope:** Underlying hypervisor/container escapes, physical hardware attacks, language-runtime bugs in third-party libraries (handled at supply-chain level, not in this document).
**Implementation map:** fixture rows below cite the §22.1 catalog names. The live repository mapping (real `harness/fixtures/` files → STRIDE rows) lives in `docs/architecture/repo-alignment.md` §3 (SADD Appendix F) — see §16.

## 1. Methodology

This document follows Microsoft STRIDE — six threat categories applied per element — combined with the **fixture → production-gate** traceability matrix from §22.2 of the SADD. Every threat listed has at least one named fixture that exercises it and at least one named production gate that asserts its absence.

Where the SADD introduces a v1.2 hardening, this document captures the threat that hardening addresses. Where the v1.1 architecture lacked coverage, the new fixture and gate are marked **(v1.2)**.

## 2. STRIDE primer

| Letter | Category | Core question |
|--------|----------|---------------|
| **S** | Spoofing | Can an attacker impersonate a principal? |
| **T** | Tampering | Can an attacker corrupt data or code? |
| **R** | Repudiation | Can a legitimate actor deny they acted? |
| **I** | Information Disclosure | Can a party read data they should not? |
| **D** | Denial of Service | Can legitimate use be prevented? |
| **E** | Elevation of Privilege | Can a party act beyond granted authority? |

## 3. Trust boundaries

```mermaid
graph LR
    subgraph usr["User trust (operator / client / member)"]
        U[Operator Console PWA]
        M[Camelot Mobile]
    end

    subgraph mesh["Private mesh (Camelot nodes)"]
        ENG[Engineering Node]
        EXP[Experience Node]
        MKT[Marketing Node]
        COM[Commerce Node]
        WEL[Wellness Node]
        RES[Research Node]
        INF[Inference Node]
    end

    subgraph cb["Cybertronia control plane"]
        VPS[VPS Active Hub]
        LOC[Local CPU twin]
        WIT[Witness(s)]
        SEC[Secret Broker / HSM]
    end

    subgraph memory["Cloudbrain memory plane"]
        VFSG[VFS Guardian]
        MP[MemPalace]
        OV[OpenViking]
        GR[Graphify]
        RED[Redis]
        ON[Open Notebook]
    end

    subgraph ext["External world"]
        PRV[Providers HubSpot Mailchimp Stripe Calendar]
        LM[NotebookLM external low-trust]
    end

    U -. mTLS .-> VPS
    M -. mTLS .-> VPS
    ENG -. mesh .-> VPS
    EXP -. mesh .-> VPS
    MKT -. mesh .-> VPS
    COM -. mesh .-> VPS
    WEL -. mesh .-> VPS
    RES -. mesh .-> VPS
    INF -. mesh .-> VPS
    LOC -. replicate .-> VPS
    WIT -. signed promotion lock .-> VPS
    SEC -. only-handles .-> VPS
    PRV -. signed webhooks only .-> MKT
    PRV -. signed webhooks only .-> COM
    LM -. quarantine only .-> VFSG
    VFSG -. quarantine .-> MP
    OV -. namespace-scoped .-> MP
    GR -. namespace-scoped .-> MP
    RED -. cache hash under tenant key .-> MP
    ON -. quarantine .-> VFSG
```

**Boundary rules** (all v1.2):

- The user/operator perimeter is **mTLS + replay-protected only.** No Bearer tokens; no shared secrets per session.
- The mesh/cross-node perimeter is **mTLS with signed updates** to Bifrost.
- The control-twin perimeter is **encrypted replication** with omitted root keys and excluded plain tokens (§6.2 replication matrix).
- The provider perimeter is **signed webhooks only**, idempotency-keyed.
- The Cloudbrain perimeter is **scoped by `policy_hash` HMAC (§15.6)**; cross-policy reads are unreachable after a policy bump.
- The NotebookLM perimeter is **always Tier 4 (VFS quarantine)** — the most hostile external source.

## 4. Element inventory

| Element | Plane | Primary authority | Anti-authority mitigations |
|---------|-------|-------------------|----------------------------|
| Anya PWA / Operator Console | Experience | None | Tenant-scoped UI; offline draft queue |
| Camelot Mobile | Experience | None | Cached-epoch window (§10.3) |
| Edge Node agents | Mesh | Knight runtime under lease | Trust band admission (§7.3) |
| Bifrost Hub | Control | Auth, transport only | mTLS + replay protection (§12.2) |
| Sentinel | Control | Sole effect authority | 2-of-N MFA + epoch increment |
| Authority Epoch | Control | Monotonic versioning | Producer = Sentinel; signature required |
| Promotion Lock | Control | Fencing primitive | Witness + operator MFA (§6.5) |
| Registries (node, cartridge) | Control | Admission authority | Signed entries + revocation metadata |
| Receipt chain | Evidence Audit | Canonical truth | Hash-linked; ledger-anchored |
| VFS Guardian | Safety | Source/write authority | Pre-flight deny rules (§14.3) |
| Process supervisor | Safety | Allowlist enforcement | Resource budget + worker reap |
| Secret Broker | Safety | Handle broker | HSM-backed; no plaintext export |
| OpenViking / MemPalace / Graphify | Cloudbrain | Scope authority | Tenant/org namespace |
| Redis | Cloudbrain | Acceleration only | Cache-secret HMAC (§15.6); no policy truth |
| Open Notebook | Cloudbrain | Research container | VFS quarantine + receive-only on NotebookLM |
| Cartridges | Evidence Data | Portable bounded behavior | risk_tier_invariant_cap (§8.2) |

Each row is iterated through STRIDE in §5–§10 below. Where an attack is generic (e.g. mTLS bypass), it appears in the table for the relevant element. Where an attack is category-wide, it appears in §11.

## 5. Spoofing (S)

| ID | Threat | Element / plane | v1.2 mitigation | Fixture(s) | Production gate(s) |
|----|--------|-----------------|------------------|------------|---------------------|
| S-1 | Operator impersonation via stolen cookie or replay | Operator Console, Mobile | mTLS session + nonces + replay window 60s (§12.2); MFA enforced (no shared admin) | `forged_operator_request` | `MFA_for_operators`, `no_shared_admin_accounts` |
| S-2 | Edge node spoofing another node_id | Bifrost Hub, edge agents | Node identity = hardware-attested key pinned in registry; signed heartbeat | `forged_operator_request` (used in node-spoof variant) | `node_and_workload_identity`, `stale_epoch_rejection_tested` |
| S-3 | Tenant masquerade: one tenant sending another tenant's manifest/redacted payload | Bifrost, Cloudbrain | Tenant key bound to `parent_hash` and `tenant_id` in every receipt (§11.3); cross-tenant retrieval structurally denied (§15.5/§15.6) | `cross_tenant_event_query`, `cross_tenant_cache_key` | `cross_tenant_retrieval_denied`, `cache_namespace_verified` |
| S-4 | Receipt signer impersonation (e.g. forged `signer: "sentinel"`) | Receipt chain | Signer trust band required; `ed25519` signature verified against `policy_bundle` | `forged_node_receipt` | `receipt_signature_verified` (v1.2), `receipt_chain_verified` |
| S-5 | Cartridge signer impersonation (e.g. customer pushing cartridge claiming camelot-commercial signer) | Cartridge registry | `signer_trust_band` enum + signer public-key pinning in registry (§8.3) | `cartridge_exceeding_risk_tier_invariant_cap` (variants) | `risk_tier_invariant_enforced` |
| S-6 | Witness impersonation (rogue actor granting promotion locks) | Hub twin | Witness key fingerprint pinned in policy bundle; rotation requires epoch increment (§6.5) | `equota_promotion_with_witness_unreachable` (signed-only variant) | `promotion_quorum_verified`, `authority_epoch_verified` |
| S-7 | Provider webhook spoofing (HubSpot/Stripe/Calendar imitating Camelot) | Marketing, Commerce | Signed webhooks + idempotency key + replay protection | `duplicate_provider_webhook` | `webhook_signature_verified`, `idempotent_provider_action_verified` |

## 6. Tampering (T)

| ID | Threat | Element / plane | v1.2 mitigation | Fixture(s) | Production gate(s) |
|----|--------|-----------------|------------------|------------|---------------------|
| T-1 | Chain link tampering (`parent_hash` rewrite) | Receipt chain | Hash-linked chain + re-derivation rule (§11.3); ledger anchor every N=1000 entries | `receipt_parent_hash_tamper` | `tamper_detection_verified`, `receipt_chain_verified`, `ledger_anchor_verified` |
| T-2 | Manifest tampering after approval | Operator Console, Sentinel | `manifest_hash_at_approval` recorded in lease approvals block; approvals re-checked against current manifest hash | `expired_effect_manifest` | `manifest_expiry_enforced`, `manifest_bound_leases` |
| T-3 | Lease tampering (modify permissions after issue) | Sentinel, edge | Lease signed at issue; re-validate signature and epoch on every node use | `expired_effect_manifest` | `lease_revocation_tested`, `stale_epoch_rejection_tested` |
| T-4 | VFS path escape (write outside `worktree/`) | VFS Guardian | Preflight denies (§14.3); runtime path resolution rejects parent escapes | `VFS_path_escape` | `VFS_path_escape_denied`, `protected_write_denied` |
| T-5 | Worktree or source revision tampering after VFS attestation | VFS, receipt service | Receipts include `immutable_inputs` checksum; Sentinel refetches on hash mismatch | `forged_node_receipt` | `receipt_chain_verified` |
| T-6 | Cartridge binary tampering post-signature | Cartridge registry | `artifact_hash` + `signature_algorithm` required; build-time signature re-verification at admission | (covered indirectly by S-5) | `risk_tier_invariant_enforced` |
| T-7 | Policy bundle tampering (downgrade attack) | Sentinel | Policy versioning → new epoch on bump; old leases reject | `stale_authority_epoch` | `stale_epoch_rejection_tested`, `policy_outside_models` |
| T-8 | Cloudbrain memory tampering across tenants | Redis, Open Notebook | Cache HMAC scoped to tenant+policy; cross-policy reads unreachable (§15.6); NotebookLM always quarantine | `untrusted_memory_promotion`, `cross_policy_namespace_cache_hit` | `memory_promotion_verified`, `cache_namespace_verified` |
| T-9 | Auth chain tampering (Boris test report) | Boris, Scribe | Boris reports are signed and chain-linked | `unauthorized_persona_capability` (variant) | `receipt_chain_verified` |
| T-10 | Ledger anchor tampering | Ledger anchor | Anchor service writes to immutable log operator controls; anchor records are ed25519-signed (pinned key) so tampering is detectable from the record alone, without re-deriving the chain (§11.3) | `harness/contracts/verify_receipt_chain.py` STEP 5 (signed anchors, 5-case T-10/S-4 battery, dual chain+signature checks) + `--replay` re-verifying committed `anchor_*.json` and `golden-anchor-0000.json` from disk | `ledger_anchor_verified` |

## 7. Repudiation (R)

Repudiation in Camelot is countered structurally by the receipt chain — every consequential action emits a chain-linked receipt. The threats below describe cases where the receipt chain itself could be subverted.

| ID | Threat | Element / plane | v1.2 mitigation | Fixture(s) | Production gate(s) |
|----|--------|-----------------|------------------|------------|---------------------|
| R-1 | Operator denies approving an effect | Operator Console, receipt chain | Approvals block captured at the moment of approval with `manifest_hash_at_approval` and approver identity + trust band | `forged_operator_request` | `receipt_chain_verified` |
| R-2 | Provider denies executing an action (e.g. charge) | Marketing, Commerce | Signed + idempotent webhooks; provider-side reconciliation | `duplicate_provider_webhook` | `webhook_signature_verified`, `idempotent_provider_action_verified` |
| R-3 | Knight denies producing a side effect | Sentinel, receipt chain | Knight identity in receipt `actor.id`, `node_id`, `trust_band`; receipt signed by signer trust band | `forged_node_receipt` | `receipt_chain_verified`, `tamper_detection_verified` |
| R-4 | Sentinel denies issuing a lease | Receipt chain | Policy-decision receipt + lease issuance receipt both chain-linked | `expired_effect_manifest` | `manifest_bound_leases`, `receipt_chain_verified` |
| R-5 | Promotion actor denies failover decision | Hub twin | Promotion lock is signed by witness; promotion receipt chain-linked with `witness_lock_ref` (§6.5) | `local_twin_promotion`, `equota_promotion_with_witness_unreachable` | `promotion_fencing_verified`, `promotion_quorum_verified` |

## 8. Information Disclosure (I)

| ID | Threat | Element / plane | v1.2 mitigation | Fixture(s) | Production gate(s) |
|----|--------|-----------------|------------------|------------|---------------------|
| I-1 | Secret exfiltration via unsanctioned handle | Secret Broker | Handle broker only; no plaintext export; per-cartridge secret scope | `unauthorized_secret_handle` | `secret_handle_authorization_verified` |
| I-2 | Cross-tenant retrieval leak | Cloudbrain | Tenant-scoped namespace; cache HMAC scoped to `tenant_id` (§15.6); retrieval lease scoped to tenant | `cross_tenant_event_query`, `cross_tenant_cache_key` | `cross_tenant_retrieval_denied`, `cache_namespace_verified` |
| I-3 | RAG/document prompt-injection exfiltration | OpenViking, Graphify, Open Notebook | Context compiler strips untrusted instruction content (§15.3); prompt-injection fixture denied | `prompt_injection_document` | `prompt_injection_fixture_denied`, `retrieval_trajectory_receipted` |
| I-4 | Untrusted memory promotion (Tier 4 → Tier 2) | MemPalace, Redis | Memory promotion requires VFS admission + retrieval lease | `untrusted_memory_promotion` | `memory_promotion_verified` |
| I-5 | Replication of unredacted tenant content to twin | Hub twin | Replication matrix (§6.2) explicitly excludes raw unredacted tenant content | `local_twin_promotion` | `replication_integrity_verified` |
| I-6 | Payment/PII in raw voice or audio logs | Evidence Data | Evidence excludes raw voice/audio and payment data (§6.2); redaction at source | (covered by retention policy) | `consent_and_suppression_verified`, evidence production gate |
| I-7 | Provider token leakage via replication | Hub config | Config replication excludes plaintext provider tokens (§6.2) | (covered by replication matrix) | `replication_integrity_verified` |
| I-8 | Receipt payload leaking redacted data | Receipt chain | `payload_redacted` is role-scoped; consumers receive only what their role permits (§11.3) | `forged_node_receipt` (variant) | `receipt_chain_verified` |
| I-9 | Boundary violation: mobile emits effect after policy bump without fresh epoch | Mobile / Sentinel | Cached-epoch window refuses effect past expiry (§10.3); window resets on epoch change | `cached_epoch_across_policy_bump`, `mobile_epoch_window_expired` | `mobile_epoch_window_enforced`, `no_offline_effect_bypass` |
| I-10 | Symbolect tree revealing invisible capabilities | Symbolect compiler, Sentinel | Compiler capability self-authorization is forbidden (§17.3); tree rejected at registration | `malformed_symbolect_tree` | `symbolect_validation_enforced` |

## 9. Denial of Service (D)

| ID | Threat | Element / plane | v1.2 mitigation | Fixture(s) | Production gate(s) |
|----|--------|-----------------|------------------|------------|---------------------|
| D-1 | Manifest explosion (long-lived or spike-heavy) | Sentinel, ledger | Hard expiry + `max_actions` on every lease (§11.2); expired manifests denied | `expired_effect_manifest`, `cached_epoch_across_policy_bump` | `manifest_expiry_enforced`, `manifest_bound_leases` |
| D-2 | Resource exhaustion (CPU/memory) | Resource governor | Hard limits per worker (§7.2); worker reaping verified | (covered by resource unit tests) | `resource_budget_enforced`, `worker_cleanup_verified` |
| D-3 | Quota exhaustion per tenant | Sentinel | Tenant policy hierarchy with `rate/spend/concurrency` | `unauthorized_secret_handle` (quota variant) | `resource_budget_enforced` |
| D-4 | Stale-epoch denial (legacy nodes stuck) | Sentinel | Epoch rejection succeeds only because old leases were already revoked | `stale_authority_epoch`, `single_operator_t3_approval_attempt` | `stale_epoch_rejection_tested` |
| D-5 | Hub partition (VPS unreachable) | Hub twin | Twin promotion + failback drills (§6.4); SLO budget; quorum rules (§6.5) | `VPS_network_partition`, `local_twin_promotion`, `equota_promotion_with_witness_unreachable` | `failback_verified`, `promotion_quorum_verified`, `replication_integrity_verified` |
| D-6 | Witness outage denial of failover | Promotion lock | Witness outage downgrades to manual failover (operator MFA only) (§6.5); stalled standby read-only | `equota_promotion_with_witness_unreachable` | `promotion_quorum_verified` |
| D-7 | Two-person approval bottleneck | Operator Console | SLA for finding a 2nd operator; quorum per tier; calendar/reminder at T2 only so single-operator remains viable | `single_operator_t3_approval_attempt` | `two_person_rule_enforced` |
| D-8 | Mobile device offline | Mobile / Sentinel | Cached-epoch window for read-only + low-tier write; higher-tier denied past window | `mobile_permission_denied`, `mobile_epoch_window_expired` | `mobile_epoch_window_enforced`, `OS_permission_flow_verified` |
| D-9 | Duplicate provider webhook triggering re-execution | Marketing, Commerce | Idempotency key required | `duplicate_provider_webhook` | `idempotent_provider_action_verified` |
| D-10 | Console rendering overload via large receipts | Operator Console | `payload_redacted` keeps payloads role-scoped; streaming endpoints | (UI performance tests) | `retrieval_trajectory_receipted` |
| D-11 | Context-packet budget exhaustion (token flood) | Cloudbrain | Hard `total_input_tokens_hard_max` per task (§15.4) | (covered by unit tests) | `packet_token_budget_enforced` |
| D-12 | Worker process runaway | Native supervisor | Worker reaping on timeout + lifecycle cleanup | (resource tests) | `worker_cleanup_verified` |

## 10. Elevation of Privilege (E)

Elevation in Camelot is the most dangerous category — it is the only one that lets a wrong principal do a right (but unauthorized) action. The SADD's strong deny-by-default posture and the v1.2 two-person rule are the primary defenses.

| ID | Threat | Element / plane | v1.2 mitigation | Fixture(s) | Production gate(s) |
|----|--------|-----------------|------------------|------------|---------------------|
| E-1 | Knight persona granting itself forbidden capabilities | Stunspot compiler | Persona `prohibited` list enforced at compile + at §13.3 step 3 | `unauthorized_persona_capability` | `persona_prohibited_enforced` |
| E-2 | Cartridge requesting capabilities beyond its denial list | Sentinel, cartridge registry | §13.3 step 2 subtracts `denied_capabilities`; `risk_tier_invariant_cap` enforced at step 6 | `cartridge_exceeding_risk_tier_invariant_cap` | `risk_tier_invariant_enforced` |
| E-3 | Network access without explicit lease | Edge node, VFS | §13.3 derivation requires `network.scoped`; default is `disabled` | `network_call_without_lease` | `network_lease_enforced` (v1.2 listed) |
| E-4 | Process execution outside allowlist | VFS, supervisor | Executable allowlist matched; privileges dropped | `prohibited_process_execution`, `unauthorized_persona_capability` | `unapproved_process_denied` |
| E-5 | Symbolect node self-authorizing | Symbolect compiler | §17.3 final rule: no tree node can self-authorize | `malformed_symbolect_tree` | `symbolect_validation_enforced` |
| E-6 | Operator overriding Sentinel's `denied` decision | Operator Console, Sentinel | Approval UI can only *confirm* what Sentinel offers; `single_operator_t3_approval_attempt` proves T3+ requires second identity | `single_operator_t3_approval_attempt` | `two_person_rule_enforced` |
| E-7 | Auto-promotion / auto-deploy path | Sentinel, cartridge registry | Default `denied` includes `auto_merge`, `auto_deploy`; risk tier + witness required | `cartridge_exceeding_risk_tier_invariant_cap` (auto-deploy variant) | `risk_tier_invariant_enforced`, `manifest_bound_leases` |
| E-8 | Replaying a lease across a key rotation | Sentinel, edge | Epoch increments on key rotation; replay window 60s; nonce in mTLS | `expired_effect_manifest`, `forged_operator_request` | `stale_epoch_rejection_tested`, `manifest_expiry_enforced` |
| E-9 | Promotion-lock grant without witness | Promotion controller | §6.5 requires witness lock OR operator MFA + attested-node quorum | `equota_promotion_with_witness_unreachable` | `promotion_quorum_verified`, `promotion_fencing_verified` |
| E-10 | Tenant policy overrides weakening global controls | Tenant profile registration | `tenant_profile.policy_overrides` validated as narrowing-only (§9.2); Sentinel refuses weakening | (covered by tenant unit tests) | `policy_outside_models` |
| E-11 | Knowledge-graph traversal widening scope | Graphify | §15.3 strict `scope/depth` constraints on retrieval | `untrusted_memory_promotion` | `memory_promotion_verified` |
| E-12 | NotebookLM reaching into Camelot as Tier 2 | VFS Guardian | NotebookLM is always VFS quarantine (§20, §11.0 catalog note) | `prompt_injection_document` | `prompt_injection_fixture_denied` |
| E-13 | Customer-controlled cartridge claiming commercial capabilities | Cartridge registry | `signer_trust_band=customer-controlled` cannot exceed its own `risk_tier_invariant_cap` (§8.3); admission review | `cartridge_exceeding_risk_tier_invariant_cap` | `risk_tier_invariant_enforced` |

## 11. Cross-cutting threat patterns

These threats recur across multiple planes and are tracked as systemic mitigations rather than per-element rows.

### 11.1 Version & epoch drift

- Producer: Sentinel only (§6.3).
- Receivers: every node and every replay tool.
- Gate: `stale_epoch_rejection_tested`.
- Fixtures: `stale_authority_epoch`, `cached_epoch_across_policy_bump`, `expired_effect_manifest`.
- Residual risk: epoch consumer cache must explicitly invalidate on epoch change; verify under `mobile_epoch_window_expired`.

### 11.2 Cross-tenant leakage

- Shape: any path where tenant A's bytes may be observed by tenant B.
- Mitigations: §15.6 cache HMAC, §15.5 Redis policy, §6.2 replication matrix, §10.3 mobile epoch window reset.
- Fixtures: `cross_tenant_event_query`, `cross_tenant_cache_key`, `cross_policy_namespace_cache_hit`.
- Residual: third-party provider webhooks do not have tenant-of-Camelot crossing; they cross into Camelot only via signed + idempotent endpoints.

### 11.3 Untrusted external content

- Sources: NotebookLM, opened files, retriever responses, provider payloads, scraped web pages, uploaded documents.
- Default: Tier 4 (VFS quarantine).
- Promotion requires a retrieval lease and VFS admission.
- Fixtures: `prompt_injection_document`, `untrusted_memory_promotion`, `duplicate_provider_webhook`.
- Residual: prompt-injection patterns shift; the fixture must be regenerated periodically.

### 11.4 Consequential effect path

- Shape: anything classified T3 or above in §5.5.
- Default: two distinct operator approvals + (for T4) witness promotion lock or external confirmation.
- Gate: `two_person_rule_enforced`, `promotion_quorum_verified`.
- Fixtures: `single_operator_t3_approval_attempt`, `equota_promotion_with_witness_unreachable`.
- Residual: collusion between two operators is out-of-band (human trust). Watchlists via SIEM are an operational concern, not a Camelot control.

### 11.5 Failover & partition

- Shape: VPS unreachable, twin must promote.
- Mitigations: §6.5 quorum, §25.1 SLOs, §6.4 promotion requirements, fencing.
- Fixtures: `VPS_network_partition`, `local_twin_promotion`, `equota_promotion_with_witness_unreachable`.
- Residual: extended twin operation depends on replication lag SLO and witness availability behaviour; both are operational concerns.

## 12. Out-of-scope trust boundaries

These are deliberately NOT covered here; they belong in the supplier/vendor security review process. They are listed so reviewers do not search for mitigations in this document.

- Hardware root-of-trust (TPM/SEV/TEE) integrity.
- OS kernel bugs.
- TLS stack CVEs (handling: dependency scanning, not a Camelot design concern).
- Container runtime escapes.
- Physical attacks on twin servers.
- Side-channel attacks on inference nodes.
- Endpoint device compromise (lost phone with screen unlocked) — partial coverage via OS permission broker, but full coverage requires MDM.
- Insider threat of a person who already holds operator + witness roles.

## 13. Coverage matrix — STRIDE × Fixture × Gate

A flat view of what every fixture and gate looks like, organised by STRIDE category. Fixtures not belonging cleanly to a single category are placed in the column they primarily cover.

| STRIDE | Fixtures | Production gates |
|--------|----------|------------------|
| S | forged_operator_request, forged_node_receipt, cross_tenant_event_query, cross_tenant_cache_key, duplicate_provider_webhook, carbonate_signer_mismatch (in `cartridge_exceeding_risk_tier_invariant_cap`), equota_promotion_with_witness_unreachable | MFA_for_operators, no_shared_admin_accounts, node_and_workload_identity, receipt_signature_verified, cross_tenant_retrieval_denied, cache_namespace_verified, webhook_signature_verified, idempotent_provider_action_verified, risk_tier_invariant_enforced, promotion_quorum_verified, authority_epoch_verified |
| T | receipt_parent_hash_tamper, VFS_path_escape, expired_effect_manifest, forged_node_receipt, untrusted_memory_promotion, cross_policy_namespace_cache_hit, cached_epoch_across_policy_bump, stale_authority_epoch | tamper_detection_verified, receipt_chain_verified, ledger_anchor_verified, VFS_path_escape_denied, protected_write_denied, manifest_bound_leases, manifest_expiry_enforced, memory_promotion_verified, source_admission_enforced, cache_namespace_verified, stale_epoch_rejection_tested, policy_outside_models, lease_revocation_tested |
| R | forged_operator_request, forged_node_receipt, duplicate_provider_webhook, local_twin_promotion, equota_promotion_with_witness_unreachable, expired_effect_manifest | receipt_chain_verified, manifest_bound_leases, manifest_expiry_enforced, idempotent_provider_action_verified, webhook_signature_verified, promotion_fencing_verified, promotion_quorum_verified |
| I | unauthorized_secret_handle, cross_tenant_event_query, cross_tenant_cache_key, prompt_injection_document, untrusted_memory_promotion, forged_node_receipt, cached_epoch_across_policy_bump, mobile_epoch_window_expired, malformed_symbolect_tree, local_twin_promotion | secret_handle_authorization_verified, cross_tenant_retrieval_denied, cache_namespace_verified, prompt_injection_fixture_denied, memory_promotion_verified, retrieval_trajectory_receipted, replication_integrity_verified, receipt_chain_verified, mobile_epoch_window_enforced, no_offline_effect_bypass, symbolect_validation_enforced |
| D | expired_effect_manifest, stale_authority_epoch, single_operator_t3_approval_attempt, VPS_network_partition, local_twin_promotion, equota_promotion_with_witness_unreachable, mobile_permission_denied, mobile_epoch_window_expired, duplicate_provider_webhook | manifest_expiry_enforced, resource_budget_enforced, worker_cleanup_verified, stale_epoch_rejection_tested, failback_verified, promotion_quorum_verified, replication_integrity_verified, two_person_rule_enforced, mobile_epoch_window_enforced, OS_permission_flow_verified, idempotent_provider_action_verified |
| E | unauthorized_persona_capability, network_call_without_lease, prohibited_process_execution, malformed_symbolect_tree, single_operator_t3_approval_attempt, carbonate_exceeding_risk_tier_invariant_cap, equota_promotion_with_witness_unreachable, untrusted_memory_promotion | persona_prohibited_enforced, risk_tier_invariant_enforced, lease_revocation_tested, manifest_bound_leases, unapproved_process_denied, symbolect_validation_enforced, two_person_rule_enforced, promotion_quorum_verified, memory_promotion_verified, network_lease_enforced |

> Note: some fixtures appear in multiple columns because the v1.2 fixture catalog describes the *attack*, while the production gate asserts the *defence* that covers many similar attacks. For example, `forged_operator_request` exercises spoofing, repudiation, and (in some variants) tampering — and is matched by several gates.

## 14. Residual risk register

| Risk ID | Description | Owners | Planned reduction |
|---------|-------------|--------|--------------------|
| RR-1 | Two-operator collusion on T3+ effects | Compliance / Operations | SIEM watchlists, audit reconciliation, behavioural analytics (out of scope v1.2) |
| RR-2 | Hardware attestation bypass on consumer hardware | Hardware team | Recommend attested hardware for T3+; restrict commodity hardware to T0–T2 |
| RR-3 | Knowledge-graph drift causing false-positive trust in stale entities | Cloudbrain | Memory TTLs + retrieval lease expiries; future ADR on lineage assertion format (Open Question §27.11) |
| RR-4 | Witness PKI single-principal trust | Hub ops | Witness quorum can include multiple independent authorities; selection TBD (Open Question §27.3) |
| RR-5 | Payment-charge recovery edge cases (capture-then-dispute) | Commerce / Finance | Compensation playbook authoring (Open Question §27.4) |
| RR-6 | Mobile operator handover (approved-then-revoked effect) | Mobile / Sentinel | Epoch revocation propagates to mobile via §10.3; effect already issued is not undone by revocation |
| RR-7 | Cartridge evolution breaking `risk_tier_invariant_cap` semantic | Cartridge registry | Admission review + ADRs for tier taxonomy changes |
| RR-8 | Telemetry/timing side-channels via effect classification | Sentinel | Hazard-aware design not in v1.2 scope; flagged for future STRIDE iteration |

## 15. Maintenance

This document updates when:

- A new STRIDE-relevant fixture is added to §22.1.
- A new production gate is added to §25.
- A new plane or element is added to §3 of the SADD.
- A risk in §14 of this document is reduced or accepted formally.
- A STRIDE category gains a new attack pattern documented by an external review.

Cross-link audit:

- Each row in §5–§10 cites at least one SADD § and at least one fixture and at least one production gate.
- The §13 matrix is the canonical flat view used by assurance/security review.
- The §14 register is reviewed quarterly by the operational risk owner.
- §16 maps the §22.1 fixture names to the real `harness/fixtures/` files in the live repository.

## 16. Fixture implementation map (Appendix F)

The fixture names in §5–§13 are the §22.1 catalog. The live Camelot-OS repository ships every one of them as a real file under `harness/fixtures/` (canonical map: `docs/architecture/repo-alignment.md` §3, SADD Appendix F). The table below maps the STRIDE rows to the real harness files — all 25 §22.1 fixtures plus the 4 operator-console fixtures exist on disk (divergence D-3 closed, 2026-08-15).

| STRIDE row(s) exercised | Real harness fixture | What the fixture proves |
|-------------------------|----------------------|--------------------------|
| E-6, R-1 | `harness/fixtures/operator-console-approval/` | Approval-required task: approve issues a lease, deny records a denial; controls enabled only with valid operator session + evidence gates green (AC10–AC13) |
| T-3, R-4, D-12 | `harness/fixtures/operator-console-cancellation/` | Active task cancelled mid-run: cancellation receipt, lease revoked, workers stopped, VFS workspace cleaned (AC20) |
| S-4, T-1, I-8 | `harness/fixtures/operator-console-integrity-failure/` | Snapshot carries `integrity: integrity_failed` with a forged receipt hash: alert raised, approval disabled, record preserved (AC17–AC18) |
| I-8, D-10 | `harness/fixtures/operator-console-readonly-audit/` | Deterministic read-only audit task: six panels render real state, no fabricated content, no-write receipt (AC19) |

**All §22.1 fixtures ported (2026-08-15).** The other 21 §22.1 fixtures (chain-tamper, epoch-stale, mobile-epoch-window, cross-policy-cache, tier-quorum, …) now have real READMEs under `harness/fixtures/`; each cites its production gate and SADD section. The full mapping and divergence register live in `docs/architecture/repo-alignment.md` §3 + §9.

---

*Authoritative source: `Camelot-OS SADD + LLDD v1.2.md`. Any divergence here should be reported to the SADD owner.*
