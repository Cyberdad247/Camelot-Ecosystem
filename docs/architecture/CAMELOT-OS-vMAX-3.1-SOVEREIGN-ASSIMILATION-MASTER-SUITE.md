# Camelot-OS vMAX 3.1
## Sovereign Assimilation and Enterprise Production Master Suite

**Document ID:** `CAMELOT-OS-MASTER-SUITE-vMAX-3.1-20260914`  
**Version:** `3.1.0`  
**Status:** `LIVING BASELINE | CONVERGED | ASSIMILATION-GOVERNED | ENTERPRISE-PREPRODUCTION`  
**Authority:** `⚜ SOVEREIGN_TRUTH`  
**Supersedes:** `CAMELOT-OS-MASTER-SUITE-vMAX-20260913 v3.0.0` only where this document explicitly changes or clarifies the prior baseline.  
**Primary scope:** Camelot-Ecosystem, Camelot-VPS, Cybertronia, Bifrost, authority services, World Tree/Ecoshell, Twin-Brain, Shadow/UKG continuity, governed extensions, enterprise operations, and the Documentation OS.

---

# 0. Executive Convergence

## 0.1 Canonical mission

Camelot-OS converts intent into bounded, evidence-backed outcomes without allowing models, routers, clients, personas, cartridges, or network reachability to become authority.

```text
Human intent
  -> typed proposal
  -> policy decision
  -> immutable effect manifest
  -> exact approval when required
  -> current manifest-bound capability lease
  -> VFS/resource preflight
  -> bounded execution
  -> evidence envelope
  -> Gideon verification
  -> Arthur resolution
  -> Ledger receipt
  -> State projection
  -> World Tree / Ecoshell verified view
```

The core constitutional rule remains:

> **Models propose. Camelot authorizes. Execution is bounded. Evidence is verified. Receipts establish canonical truth.**

## 0.2 Reforged architecture decisions

This revision incorporates the full thread, the vMAX 3.0 suite, enterprise-readiness amendments, Twin-Brain work, Shadow/UKG continuity design, cartridge/pill architecture, and the new Assimilation Protocol.

| Domain | vMAX 3.1 canonical decision |
|---|---|
| Authority | Sentinel is the sole policy, capability-lease, and revocation authority. Excalibur binds human approval. Gideon verifies. Arthur resolves. Ledger proves. |
| Leadership fencing | Signed monotonic `authorityEpoch` remains the deployed v1 fencing primitive. A multi-revision Authority Vector is an additive v2 target, not a silent breaking replacement. |
| Transport | Tailscale provides the private WireGuard mesh. Bifrost provides Camelot message admission, signed-envelope trust, route allowlists, replay defense, and governed cross-node/external transport. |
| Local authority communication | Same-host Court services prefer Unix domain sockets or loopback with OS ACLs. Bifrost is not required for every local function call. |
| Runtime | Rust native control plane, Go transport/gateway services, Wasmtime for constrained trusted components, Firecracker for untrusted evaluation. |
| Deployment | Hardened systemd and cgroup v2. No Docker/Kubernetes runtime dependency in the sovereign authority hot path. |
| Data | PostgreSQL is the authoritative relational store. Retrieval is abstracted behind `RetrievalIndexPort`. Redis is optional acceleration only. Local content-addressed storage is the minimal artifact backend; S3/MinIO is optional. |
| Experience | World Tree, Ecoshell, Excalibur, Battle Mode, Throne Room, Voice, mobile, and avatars are projections or intent surfaces. They do not manufacture authority or finality. |
| Extensions | Cartridges are signed installable packages. Pills are signed declarative overlays that may narrow but never expand authority. Personas and Avatars are presentation/configuration layers. |
| Continuity | Shadow Brain and UKG preserve cognition, retrieval, drafts, and provisional evidence. Isolation does not create sovereign authority. |
| Documentation | Documentation is a governed part of the system. Runtime architecture layers and documentation truth layers use separate names to eliminate ambiguity. |
| Assimilation | New knowledge may challenge the baseline, but cannot silently rewrite `SOVEREIGN_TRUTH`. All material changes pass the Assimilation Protocol. |

## 0.3 Naming correction: runtime versus documentation layers

Earlier materials used `L0-L6` for runtime layers and `L0-L5` for documentation truth layers. This is ambiguous. vMAX 3.1 separates them.

### Runtime Planes

```text
RP0  Sovereign Infrastructure
RP1  Authority and Evidence
RP2  Governed Connectivity
RP3  Routing and Orchestration
RP4  Cognition, Knowledge, Voice, Continuity
RP5  Experience and Command Surfaces
RP6  Extensions and Embodiment
```

### Documentation Layers

```text
DL0  Governance
DL1  Intent
DL2  Structure
DL3  Guardrails
DL4  Operations
DL5  Reflection
```

A document, service, policy, or implementation artifact MUST specify which namespace it uses.

## 0.4 Constitutional doctrine

```text
STRUCTURE CONSTRAINS POWER.
IDENTITY GRANTS RECOGNITION.
CONNECTIVITY GRANTS REACHABILITY.
POLICY GRANTS PERMISSION.
LEASES BOUND ACTION.
EVIDENCE GRANTS CONFIDENCE.
RECEIPTS GRANT PROOF.

THE ROAD GRANTS PASSAGE.
THE CROWN GRANTS PERMISSION.

THE SHADOW MAY PRESERVE COGNITION.
THE SHADOW MAY NOT CREATE SOVEREIGN AUTHORITY.

NEW KNOWLEDGE MAY CHALLENGE THE CASTLE.
IT MAY NOT SILENTLY REWRITE IT.
```

---

# Part I - Business Requirements Document

## 1. Business purpose

Camelot-OS provides a sovereign, multi-tenant operating fabric for AI-assisted work in which high-value intent can be transformed into safe, attributable, reversible where possible, and independently verifiable outcomes.

The platform exists to reduce the gap between:

```text
"the model suggested it"
```

and:

```text
"an authenticated actor requested it,
policy allowed it,
the exact effect was approved when required,
execution occurred inside explicit bounds,
independent verification passed,
and the result has a durable receipt."
```

## 2. Business objectives

| ID | Objective | Primary measure |
|---|---|---|
| BR-001 | Govern multi-tenant AI-assisted work | Every material task binds tenant/workspace and ends in receipt or explicit denial/failure evidence |
| BR-002 | Preserve human authority | Consequential effects cannot bypass Sentinel/Excalibur policy |
| BR-003 | Enable modular capabilities | Signed cartridges and Pills can be admitted, pinned, revoked, upgraded, and rolled back |
| BR-004 | Deliver premium UX without reducing assurance | All security/task claims are traceable to authoritative sources |
| BR-005 | Improve safely | Candidates are evaluated, versioned, compared, and promoted only with evidence |
| BR-006 | Operate on constrained infrastructure | Sovereign Core remains protected under the defined resource budget |
| BR-007 | Support enterprise governance | Identity, tenancy, audit, recovery, incident response, supply chain, and ownership are testable |
| BR-008 | Evolve without architectural entropy | Assimilation deduplicates, challenges, and governs changes before baseline promotion |

## 3. Stakeholders

| Stakeholder | Need | Permitted authority |
|---|---|---|
| Sovereign operator / tenant owner | Control, visibility, safe effects | Approves policy-defined actions |
| Tenant member | Productive governed workflows | Creates intent and reviews permitted evidence |
| Security/compliance owner | Auditability, isolation, incident evidence | Reviews controls, policy and incidents |
| SRE/operator | Recoverability and deployability | Operates infrastructure, not business authority |
| Cartridge publisher | Stable extension surface | Publishes signed bounded packages |
| Knight/persona designer | Modular roles and behaviors | Publishes signed configuration, never authority |
| Research/domain owner | Traceable domain outcomes | Reviews/approves domain outputs where policy requires |
| Developer | Stable contracts and deterministic gates | Proposes implementation change |
| Auditor | Independent proof | Verifies receipts, contracts, evidence and release artifacts |

## 4. Business non-goals

Camelot-OS is not:

- an unrestricted autonomous-agent platform;
- a system where model confidence equals authority;
- a system where connectivity implies permission;
- a system where a browser, phone, avatar, Knight, router, cartridge, or Pill can mint its own authority;
- a generic remote shell fabric;
- a system that permits undocumented hot-path authority dependencies;
- a system that claims regulatory compliance solely because controls are described in architecture;
- a system where documentation can claim deployment without implementation evidence.

---

# Part II - Product Requirements Document

## 5. Product vision

Camelot-OS is a visually rich, evidence-driven PWA ecosystem backed by a compact sovereign control plane. Users interact through Ecoshell, World Tree, Excalibur, Questboard, Voice, Avatar Knights, and cartridge workspaces. Those interfaces capture intent and render state, while the authority plane controls permission and canonical truth.

## 6. Product capabilities

| Capability | Value | Required systems |
|---|---|---|
| Ecoshell / World Tree | Spatial operational visibility | State Service, projection API/SSE, receipts, accessibility fallback |
| Mission execution | Intent to bounded work | Omni-Router, Omni-Knight Router, Sentinel, VFS, Moon, executor |
| Excalibur | Exact human control | Approval Certificate, WebAuthn/step-up, immutable effect manifest |
| Evidence timeline | Auditable outcomes | Gideon, Arthur, Ledger, Receipt Verifier |
| Cartridge Vault / Armory | Modular functionality | Registry, signatures, provenance, entitlement, revocation |
| Evaluation Forge | Safe candidate testing | Firecracker, fixtures, Gideon, Arthur, Ledger |
| Research Intelligence | First Golden Mission | VFS, Wasmtime, source provenance, evidence, export controls |
| Twin-Brain continuity | Fenced leadership and recovery | Epoch Fencer, convergence checks, backup/failover drills |
| Shadow continuity | Offline cognition without sovereignty | Shadow Brain, inference runtime, UKG, provisional journal |
| Voice and mobile | Low-friction intent and approval | Voice Gateway, Bifrost, consent, session binding, step-up |
| Avatar Knights | Embodied governed interaction | Signed profile, Knight assignment, Voice/PWA, no owned leases |
| Assimilation Workbench | Govern architectural evolution | DL0-DL5, diff engine, Gideon, ADRs, release evidence |

## 7. Product truth states

All stateful UI components MUST distinguish:

```text
FIXTURE
SIMULATED
OBSERVED
VERIFIED
DEGRADED
STALE
UNKNOWN
DENIED
FAILED
```

`VERIFIED` MUST require a traceable authoritative source and, for completion claims, a valid receipt.

Green styling alone is never proof.

## 8. Golden Path user story

### US-GOLD-001

As a tenant member, I want to submit a read-only research mission so that Camelot can return a verified result without granting external mutation authority.

Acceptance:

1. tenant/workspace derived server-side;
2. task is typed and classified;
3. Sentinel emits a signed policy decision;
4. read-only lease is short-lived and manifest-bound;
5. VFS attests the exact source/artifact scope;
6. Wasmtime component receives no ambient authority;
7. evidence envelope contains source provenance and hashes;
8. Gideon returns a signed verdict;
9. Arthur resolves lifecycle state;
10. Ledger emits a valid receipt;
11. State Service projects ordered events;
12. World Tree shows `VERIFIED` only after receipt verification.

---

# Part III - Functional Requirements Document

## 9. P0 requirements

| ID | Requirement |
|---|---|
| FR-001 | WebAuthn-capable secure authentication with server-revocable sessions |
| FR-002 | Server-derived tenant/workspace/membership scope for every request |
| FR-003 | Frozen typed contract catalog and canonical serialization |
| FR-004 | Bifrost signed envelope validation, route allowlists, idempotency and replay defense |
| FR-005 | Sentinel signed policy decision and short-lived manifest-bound leases |
| FR-006 | Dynamic authority-epoch enforcement across all consequential decision boundaries |
| FR-007 | VFS resource/path/artifact preflight with signed attestation |
| FR-008 | Bounded Wasmtime execution without generic shell or ambient network/filesystem |
| FR-009 | Append-only signed receipt chain and independent replay verifier |
| FR-010 | PostgreSQL application-scope enforcement plus RLS |
| FR-011 | Snapshot + ordered replay + SSE authoritative projection |
| FR-012 | Read-Only Research Golden Mission end to end |
| FR-013 | Doc-Check traceability from DL0-DL4 requirements to code/tests |
| FR-014 | Assimilation Protocol for architecture and documentation mutation |

## 10. P1 requirements

| ID | Requirement |
|---|---|
| FR-101 | Excalibur exact-manifest Approval Certificate |
| FR-102 | Revocation propagation with bounded SLO and worker termination/queue behavior |
| FR-103 | Tenant/workspace receipt partitions and signed sovereign checkpoints |
| FR-104 | WIT/Component Model capability surface for trusted Wasmtime workloads |
| FR-105 | Firecracker Evaluation Chamber or remote equivalent |
| FR-106 | OIDC federation and enterprise role/attribute integration |
| FR-107 | Cartridge manifest staging, verification, activation, pinning, rollback and revocation |
| FR-108 | Pill non-escalation verification |
| FR-109 | Enterprise observability, SLOs, runbooks and incident classification |
| FR-110 | Backup/restore, Twin-Brain promotion, failover and failback drills |

## 11. P2 requirements

| ID | Requirement |
|---|---|
| FR-201 | Authority Vector additive schema |
| FR-202 | Formal Convergence Root |
| FR-203 | Shadow Brain + isolated local inference runtime |
| FR-204 | UKG signed knowledge capsules and provisional journal reconciliation |
| FR-205 | SCIM lifecycle and optional SAML enterprise profile |
| FR-206 | Remote Evaluation Forge profile |
| FR-207 | Voice/Avatar high-assurance approval handoff |
| FR-208 | Cartridge Vault / trusted publisher ecosystem |

---

# Part IV - Software Requirements Specification

## 12. Security invariants

1. Default deny.
2. Client tenant/workspace claims are untrusted hints.
3. Bifrost transport success never equals effect authorization.
4. Routers never issue leases.
5. Knights/models never issue leases or receipts.
6. Excalibur approval cannot override a Sentinel denial.
7. Approval binds the exact effect manifest digest.
8. VFS attestation binds the exact workspace/resource/artifact scope.
9. Executor rejects stale authority immediately according to freshness policy.
10. Gideon is independent of the executor being verified.
11. Arthur cannot bypass policy, approval, verification or receipt requirements.
12. Ledger history is append-only.
13. UI cannot manufacture canonical completion.
14. Shadow/UKG offline state is provisional until reconciliation.
15. No generic shell, arbitrary URL proxy, or browser-exposed privileged token is a production authority primitive.

## 13. Tenant isolation

Tenant scope MUST be enforced at:

- Bifrost admission and route resolution;
- application authorization;
- PostgreSQL RLS;
- State/SSE subscription;
- receipts;
- VFS;
- object/CAS paths;
- retrieval/vector/cache keys;
- UKG;
- logs/traces;
- support access;
- cartridge activation;
- backup/export/deletion workflows.

Cross-tenant negative tests are release blocking.

## 14. Data classification

```text
PUBLIC
INTERNAL
CONFIDENTIAL
RESTRICTED
SECRET
```

Classification propagates to task envelopes, VFS sources, evidence, UKG, retrieval records, logs/traces, backups, exports, voice transcripts, and external connectors.

`SECRET` data MUST NOT enter model prompts, broad logs, client projections, general vector indexes, or ordinary cartridge state.

## 15. Time integrity

- Monotonic clock for intervals, deadlines, retries, heartbeat age and TTL accounting.
- Wall clock only for signed validity windows and audit timestamps.
- Authority decisions fail closed when time uncertainty exceeds the relevant policy bound.
- Clock recovery requires fresh authority state before consequential work resumes.
- Clock-skew events are operational evidence.

## 16. Availability principle

Safety is never relaxed merely to increase availability.

If authority freshness, revocation state, key status, or receipt health cannot be established within the decision-class bound, Camelot queues, degrades or denies according to policy. It does not guess.

---

# Part V - System Architecture Document

## 17. Runtime planes

### RP0 - Sovereign Infrastructure

Owns:

- VPS/host compute;
- systemd and cgroup v2;
- encrypted storage;
- local sockets;
- private mesh;
- backups;
- base telemetry;
- resource pressure controls.

May not:

- interpret user intent;
- decide business policy;
- create model/persona-specific authority.

### RP1 - Authority and Evidence

Canonical services:

```text
Sentinel
Epoch Fencer
Excalibur approval backend
VFS Guardian
Node Agent / Wasmtime executor
Gideon
Arthur
Ledger / Receipt Service
State Service
Identity assurance adapters
```

This plane is intentionally small.

### RP2 - Governed Connectivity

```text
Bifrost
Tailscale / Headscale mesh
service/workload identities
route allowlists
replay defense
event delivery
```

Bifrost is the governed road, not the Crown.

### RP3 - Routing and Orchestration

```text
Omni-Router
Omni-Knight Router
Moon scheduler
Knight Registry
Workflow Registry
Task Graph
```

These components coordinate work and request capability. They do not authorize effects.

### RP4 - Cognition, Knowledge and Modality

```text
Crown Brains
Shadow Brain
isolated inference runtime
Cloudbrain
UKG
retrieval index
Voice Gateway
Context Compiler
```

Cognition is proposal-producing and lease-consuming.

### RP5 - Experience and Command Surfaces

```text
Camelot Shell
World Tree
Excalibur
Questboard
Battle Mode
Throne Room
Knight Hall
Armory
Shadow Subspace
Voice Deck
S26 PWA
```

### RP6 - Extensions and Embodiment

```text
Cartridges
Pills
Persona Profiles
Avatar Knights
UI extension manifests
Model adapters
```

Everything in RP6 is signed, bounded and revocable.

## 18. Single-writer truth domains

Every authoritative fact has exactly one writer.

| Truth | Single writer |
|---|---|
| leadership epoch | Epoch Fencer |
| policy/lease/revocation | Sentinel |
| human approval record | Excalibur approval service |
| VFS preflight attestation | VFS Guardian |
| evidence verdict | Gideon |
| lifecycle resolution | Arthur |
| immutable receipt | Ledger |
| ordered workspace projection | State Service |
| cartridge admission state | Registry |
| tenant identity/membership | Identity/Tenant service |
| UI visualization | never authoritative |

Readers may cache signed truth subject to freshness rules. They do not become alternate writers.

## 19. Local Court communication

Inside a single host:

```text
systemd service identity
  + Unix domain socket / loopback
  + filesystem/socket ACL
  + signed object verification where authority-sensitive
```

Across hosts, clients, mobile, or external realms:

```text
private mesh
  -> Bifrost admission
  -> signed envelope
  -> route policy
  -> service authority check
```

This reduces attack surface and avoids turning Bifrost into an unnecessary internal RPC tax.

## 20. Data architecture

### Authoritative relational state

PostgreSQL owns:

- tenants;
- memberships;
- workspaces;
- missions/tasks;
- approval requests;
- policy decisions;
- leases/revocations;
- receipt indexes;
- cartridge installations;
- source metadata;
- operational references.

### Receipt bodies and artifacts

Minimal deployment:

```text
LocalCAS
/var/lib/camelot/cas/sha256/<digest>
```

Extended deployment:

```text
S3-compatible / MinIO backend
```

Authority semantics do not depend on which artifact backend is selected.

### Retrieval abstraction

Canonical interface:

```text
RetrievalIndexPort
```

Supported implementations may include:

- PostgreSQL full-text and/or vector extension;
- SQLite-family local vector adapter;
- remote tenant-scoped vector service;
- disabled vector mode with deterministic FTS only.

The architecture MUST NOT make one vector extension a constitutional dependency.

### Redis

Redis MAY provide:

- cache;
- transient queue acceleration;
- rate windows;
- short-lived replay cache;
- ephemeral presence.

Redis MUST NOT be the sole copy of:

- approval;
- policy;
- authority epoch;
- task finality;
- revocation;
- receipts;
- durable idempotency for consequential effects.

## 21. Runtime profiles

### Sovereign Core - 8 GB class

Must preserve under pressure:

```text
Bifrost
Sentinel
Epoch Fencer
Excalibur backend
VFS
Gideon
Arthur
Ledger
State
PostgreSQL
```

Shedding order:

```text
Evaluation Chamber
background Nanobot work
local model inference
graph indexing
analytics / visual enrichment
external adapters
nonessential retrieval acceleration
```

### Enterprise HA

Requires independent failure domains. Multiple processes on one host are not HA.

Logical profile:

```text
multiple Bifrost gateways
HA PostgreSQL
replicated receipt/checkpoint storage
fenced single active authority lineage
off-host immutable backup
separate Evaluation Forge
redundant projection path
```

---

# Part VI - Technical Design Document

## 22. Canonical contract catalog

### Frozen v1 catalog

```text
actor/1
tenant/1
workspace/1
node/1
quest-envelope/1
task/1
task-assignment/1
effect-manifest/1
policy-decision/1
approval-certificate/1
capability-request/1
capability-lease/1
vfs-attestation/2
evidence-envelope/1
gideon-verdict/1
arthur-resolution/1
receipt/2
workspace-event/1
authority-epoch/1
promotion/1
cartridge/1
pill/1
avatar-profile/1
context-packet/1
device-action/1
assimilation/1
```

Each contract release MUST include:

```text
JSON Schema
canonical serialization rules
Rust type/binding
Go type/binding
TypeScript type/binding
positive golden fixture
negative fixtures
canonical digest fixture
backward-compatibility declaration
owner
security classification
```

## 23. Contract lock

`CONTRACTS.lock` records:

```text
schema id
version
schema SHA-256
canonicalization profile
generated binding digests
owner
status
```

A contract change that breaks a frozen consumer requires a new schema major version or an approved compatibility migration.

## 24. Status taxonomy

A control or capability is one of:

```text
ARCHITECTURE_DEFINED
EXPERIMENTAL
IMPLEMENTED
CI_GATED
PILOT
PRODUCTION_READY
DEPRECATED
REVOKED
```

`PRODUCTION_READY` requires:

1. versioned contract;
2. merged implementation;
3. positive/negative tests;
4. metrics and alerting;
5. runbook;
6. rollback/recovery;
7. tenant/security tests;
8. signed build and provenance;
9. release approval evidence;
10. explicit failure behavior.

Documentation alone never upgrades the status.

## 25. Capability lease

A lease binds at minimum:

```text
leaseId
tenantId
workspaceId
missionId
taskId
principal/workload identity
actions
resource constraints
effect tier
manifest digest
authority epoch
policy digest
issuedAt
expiresAt
quota
issuer/keyId/signature
```

Delegated leases may only attenuate:

```text
scope narrower
duration shorter
quota smaller
effect tier lower
capabilities fewer
```

Never expand.

## 26. Approval Certificate

Excalibur emits a signed exact-manifest approval record.

```json
{
  "schemaVersion": "approval-certificate/1",
  "manifestDigest": "sha256:...",
  "tenantId": "tenant_...",
  "workspaceId": "workspace_...",
  "taskId": "task_...",
  "actorId": "principal_...",
  "decision": "APPROVED",
  "authorityEpoch": 43,
  "authentication": {
    "method": "webauthn",
    "assurance": "step-up"
  },
  "issuedAt": "RFC3339",
  "expiresAt": "RFC3339",
  "keyId": "excalibur-...",
  "signature": "ed25519:..."
}
```

Material manifest changes invalidate approval.

## 27. Receipt architecture

Receipts are tenant/workspace partitioned.

Each receipt includes:

```text
receiptId
partitionId
tenantSequence
previousReceiptDigest
subjectDigest
decisionType
authorityEpoch
policy digest/revision where relevant
issuedAt
keyId
signature
```

Periodic checkpoints combine partition heads into a signed sovereign checkpoint tree.

A verifier MUST detect:

- sequence gaps;
- duplicate receipt IDs;
- digest breaks;
- revoked/unknown signer;
- epoch regression;
- tenant scope mismatch;
- checkpoint inconsistency.

Historical receipts are never rewritten. Compensation creates new receipts.

## 28. Durable idempotency

Camelot assumes transport can be at-least-once.

Consequential effects therefore store durable idempotency records:

```text
tenant/workspace
idempotency key
manifest digest
effect identifier
current disposition
receipt reference
expiry/retention policy
```

A duplicate exact request returns the existing disposition. It does not execute twice.

---

# Part VII - Low-Level Design Document

## 29. Authority predicate

```text
permit_effect iff

authenticated_principal
AND tenant_scope_server_resolved
AND current_policy_allows
AND immutable_manifest_valid
AND required_approval_current
AND capability_lease_valid
AND authority_epoch_current
AND revocation_state_fresh
AND vfs_preflight_valid
AND resource_budget_available
AND workload_identity_valid
AND execution_backend_allowed
AND required_verification_defined
AND receipt_chain_healthy
```

Connectivity is intentionally absent from this predicate as a permission grant.

## 30. Authority epoch v1

The current fencing contract uses a signed monotonic integer:

```text
authorityEpoch = N
```

Promotion advances:

```text
N -> N+1
```

Never reuse an old epoch during failback.

```text
Open Notebook 41
NotebookLM    42
Open Notebook 43
```

not `41` again.

### Enforcement

Authority-sensitive services consume a verified EpochSource.

They MUST reject:

- input epoch below current;
- invalid signature;
- revoked/unknown fencer key;
- freshness beyond decision-class bound;
- unsafe clock state;
- epoch regression.

Old epoch objects remain historical evidence, not current authority.

## 31. Authority Vector v2 target

After v1 is completely enforced and production-drilled, introduce:

```json
{
  "leadershipEpoch": 43,
  "policyRevision": 921,
  "revocationRevision": 188,
  "registryRevision": 77,
  "identityRevision": 204,
  "contractRevision": 31
}
```

This is additive and permits precise invalidation.

It MUST NOT be introduced by silently changing `authority-epoch/1`.

## 32. Convergence Root target

Planned Twin-Brain handoff eventually binds:

```text
SHA256(
  workspace_authority_root
  || receipt_checkpoint
  || policy_digest
  || revocation_revision
  || registry_digest
  || identity_revision
  || contract_revision
)
```

Both brains may reason and retrieve. Only the active authority lineage may contribute authority-recognized artifacts where the workflow requires active-Crown participation.

Shadow Brain is never in the sovereign promotion quorum.

## 33. Promotion ceremony

States:

```text
STABLE
-> PREPARING
-> ASSERTED
-> FENCED
-> CERTIFIED
-> PROPAGATING
-> STABLE
```

Failure:

```text
DENIED
EXPIRED
CONFLICT
AUTHORITY_LOCKED
```

Planned promotion requires:

- expected epoch match;
- expected active brain match;
- fresh/ready target;
- receipt-head catch-up;
- matching required state digest/root;
- valid single-use promotion assertion;
- durable certificate commit before publication.

Failover requires explicit failover approval and policy-defined stale-source conditions.

## 34. VFS preflight

VFS Guardian proves that abstract capability is valid for an exact resource.

It validates:

```text
lease signature
lease epoch
lease resource bounds
workspace/task/session
typed operation
safe relative path
artifact hash if supplied
classification constraints
quota
provenance/license policy where applicable
```

Outputs a signed attestation.

The executor is unable to run a governed workload unless the attestation agrees with the lease and current authority.

## 35. Wasmtime trusted workload runtime

Production target:

```text
Wasm Component Model + WIT
```

A component receives only declared imports.

Example conceptual interface:

```wit
world camelot-research-pill {
    import camelot:vfs/read;
    import camelot:evidence/emit;
    import camelot:clock/monotonic;

    export run: func(task: research-task)
        -> result<research-result, pill-error>;
}
```

No network import means no network API.
No process import means no shell.
No filesystem import means no host filesystem access.

Current module-based Wasmtime implementations may coexist during migration if they preserve the same security invariant.

## 36. Firecracker Evaluation Forge

Evaluation is separate from production authority.

Candidate flow:

```text
signed candidate
-> provenance/SBOM checks
-> disposable microVM
-> synthetic secrets
-> read-only fixtures
-> no default egress
-> contract/security/tenant/resource tests
-> Gideon evidence
-> Arthur resolution
-> Ledger receipt
-> optional Excalibur promotion ceremony
```

If KVM is unavailable:

```text
EVALUATION_BACKEND_UNAVAILABLE
```

Camelot does not weaken sandboxing to preserve convenience.

Enterprise deployments SHOULD support a separate Evaluation node.

## 37. State Service

State Service owns ordered workspace projection.

Clients consume:

```text
initial snapshot
+ Last-Event-ID replay
+ live SSE
```

Canonical task states:

```text
DRAFT
CLASSIFIED
POLICY_PENDING
APPROVAL_PENDING
PREFLIGHT
LEASED
QUEUED
RUNNING
VERIFYING
RESOLVED
RECEIPTED
```

Exception/final states:

```text
DENIED
FAILED
TIMED_OUT
CANCELLED
REVOKED
QUARANTINED
```

UI may decorate these states, not redefine them.

`COMPLETE`, `SUCCESS`, or `VERIFIED` requires the receipt rule defined by product policy.

## 38. Offline / Shadow / UKG reconciliation

Connectivity states:

```text
CONNECTED
ISLANDED
REJOINING
PROMOTED
RENDERED
```

ISLANDED:

- local cognition may continue;
- retrieval may continue according to verified cache policy;
- drafts may continue;
- provisional signed journal may continue;
- no new sovereign L4/L5 authority exists;
- narrow offline L3 is prohibited unless separately safety-cased and explicitly shipped.

Reconciliation strategy per event:

```text
IDEMPOTENT_APPEND
COMMUTATIVE_MERGE
COMPARE_AND_SET
SERIALIZED_EFFECT
HITL_REQUIRED
```

Canonical state appears only after verification, resolution and receipt.

---

# Part VIII - Enterprise Identity, Security and Operations

## 39. Enterprise IAM

Baseline:

- WebAuthn for strong operator authentication;
- OIDC/OAuth federation;
- RBAC for broad role assignment;
- ABAC for tenant/workspace/data/device/time/effect constraints;
- JIT privileged access;
- workload/service identity;
- revocable sessions;
- optional SCIM lifecycle before broad enterprise onboarding;
- optional SAML profile where customer environments require it;
- break-glass procedure with separate storage and mandatory retrospective review.

Voice biometrics or speaker recognition may be a convenience signal. It is not the sole authenticator for consequential effects.

## 40. Cryptographic trust hierarchy

```text
Offline Root
  -> Intermediate Trust Issuer
      -> Epoch Fencer signing identity
      -> Sentinel lease/revocation identity
      -> Excalibur approval identity
      -> Ledger/checkpoint identity
      -> VFS attestation identity
      -> Gideon verdict identity
      -> Node/workload identity
      -> Bifrost transport/service identity
      -> Cartridge publisher identity
```

Requirements:

- protected key storage;
- key inventory;
- key IDs and validity windows;
- dual-trust overlap for routine rotation;
- signed revocation;
- compromise runbooks;
- algorithm/canonicalization agility;
- private keys never in UKG, QR, logs, browser bundles or ordinary environment templates.

## 41. Network trust

Canonical wording:

```text
Headscale/Tailscale
  -> private WireGuard reachability
  -> Bifrost service/message admission
  -> signed envelope / replay / route checks
  -> Sentinel capability decision
  -> VFS / execution effect
```

Reachability is not authority.

Default network posture is deny.

## 42. SLO framework

Example pre-production objectives:

| Class | Availability target | Example latency | RTO | Failure behavior |
|---|---:|---:|---:|---|
| Authority critical | 99.95% monthly | p95 policy < 250 ms regional | 15 min | fail closed |
| Evidence/state | 99.9% | p95 read < 500 ms | 30 min | queue/degrade, no false finality |
| Bifrost | 99.9% | p95 admission < 300 ms | 30 min | reject safely |
| Routing | 99.9% | deterministic route < 2 s | 60 min | no new orchestration |
| Experience | 99.9% | state view < 2 s | 60 min | explicit stale mode |
| Shadow continuity | node-specific | local retrieval < 2 s target | node-specific | cognition only |

These are target profiles until measured production evidence justifies contractual SLAs.

## 43. Disaster recovery

Every production profile defines:

```text
RPO
RTO
backup inventory
encryption
off-host copy
restore order
authority lineage validation
key recovery
receipt/checkpoint verification
```

Restore rule:

If restored database state, authority certificate chain, Ledger checkpoint and key state disagree, boot:

```text
RECOVERY_READ_ONLY
```

not ACTIVE.

Backups must be tested, not merely produced.

## 44. Incident severity

```text
SEV-1 authority compromise / cross-tenant exposure / receipt-integrity failure
SEV-2 authority-plane outage / broad admission failure / major loss risk
SEV-3 single-tenant degradation / cartridge outage / projection failure
SEV-4 minor defect without material security/availability impact
```

Each alert/runbook defines owner, customer impact, containment action, acknowledgment target, escalation path and evidence export.

## 45. Supply chain

Every production artifact requires:

```text
source revision
immutable digest
dependency lock digest
builder identity
SBOM
test summary
vulnerability scan
provenance attestation
release approval evidence
```

Cartridges, Pills, WASM modules, model assets, UI extensions and Avatar assets follow the same provenance principle.

---

# Part IX - Documentation OS and VKG Crystal

## 46. Documentation truth layers

### DL0 - Governance

Examples:

```text
governance.yaml
truth precedence
permissions
constitutional invariants
baseline version
```

Knights read. They do not rewrite.

### DL1 - Intent

```text
BRD
PRD
NFRs
user stories
anti-goals
```

### DL2 - Structure

```text
SAD
TDD
LLDD
OpenAPI
schemas
SQL
state machines
WIT
contracts lock
```

### DL3 - Guardrails

```text
security
privacy
accessibility
performance
resource budgets
test rules
threat model
```

### DL4 - Operations

```text
CI/CD
systemd
monitoring
SLOs
runbooks
backup/restore
release evidence
```

### DL5 - Reflection

```text
drift findings
ADRs
debt
candidate amendments
assimilation manifests
postmortems
release retrospectives
```

DL5 is proposal-oriented. It cannot silently mutate DL0-DL4.

## 47. Documentation precedence

Default precedence:

```text
approved DL0 governance
> current approved SOVEREIGN_TRUTH baseline
> frozen DL2 contracts
> approved ADR/amendment
> implementation evidence
> proposed architecture
> research/recommendations
> conversation/voice/model output
```

Important rule:

> Implementation evidence that conflicts with the baseline creates a drift finding. It does not silently overwrite the baseline.

## 48. Doc-Check

Every material code change SHOULD map:

```text
requirement
-> contract
-> implementation
-> tests
-> operational control
-> release evidence
```

A mismatch produces a DL5 finding.

---

# Part X - Camelot Assimilation Protocol v1

## 49. Purpose

The Assimilation Protocol converts new information into governed candidate changes.

Accepted source classes include:

```text
DOCUMENT
VOICE
CODE
CI
TELEMETRY
INCIDENT
RESEARCH
MODEL_OUTPUT
KNIGHT_OUTPUT
OPERATOR_INTENT
EXTERNAL_STANDARD
```

The source can be valuable without being authoritative.

## 50. Assimilation pipeline

```text
SOURCE
  -> INGEST + HASH
  -> PROVENANCE
  -> CLASSIFICATION
  -> ATOMIC CLAIM EXTRACTION
  -> DL/RP/CONTRACT MAPPING
  -> THREE-WAY DELTA
       A current SOVEREIGN_TRUTH
       B candidate claim
       C implementation evidence
  -> DUPLICATION/CONFLICT/GAP ANALYSIS
  -> CONSTITUTIONAL INVARIANT CHECK
  -> RISK/VALUE ASSESSMENT
  -> ASSIMILATION CHANGESET
  -> GIDEON VERIFICATION
  -> EXCALIBUR APPROVAL IF REQUIRED
  -> ARTHUR RESOLUTION
  -> IMPLEMENTATION / DOC PATCH
  -> DOC-CHECK + CI + DRILLS
  -> LEDGER RECEIPT
  -> BASELINE/VKG PROMOTION
```

## 51. Three-way delta dispositions

| Condition | Disposition |
|---|---|
| candidate duplicates baseline | `DUPLICATE` |
| candidate explains baseline more precisely | `CLARIFICATION` |
| candidate strengthens control without break | `REFINEMENT_CANDIDATE` |
| candidate adds new bounded capability | `EXTENSION_CANDIDATE` |
| candidate contradicts current truth | `CONFLICT_REVIEW` |
| implementation already changed but docs did not | `DOCUMENTATION_DRIFT` |
| docs require behavior not implemented | `IMPLEMENTATION_GAP` |
| implementation violates baseline | `CONFORMANCE_FAILURE` |
| candidate is superior but breaking | `MIGRATION_REQUIRED` |
| candidate weakens constitutional invariant | `REJECT` |
| evidence insufficient | `QUARANTINE` |

## 52. Claim relation vocabulary

```text
DUPLICATES
CLARIFIES
STRENGTHENS
NARROWS
EXTENDS
IMPLEMENTS
SUPERSEDES
CONFLICTS
DEPRECATES
MIGRATES
```

## 53. Hard assimilation blockers

A routine assimilation candidate MUST be rejected or escalated to explicit constitutional amendment if it attempts to:

- let a model or Knight issue sovereign authority;
- let a router issue leases;
- let Bifrost convert connectivity into permission;
- let UI state become canonical truth;
- bypass tenant isolation;
- bypass exact-manifest approval where required;
- bypass VFS/execution bounds;
- remove independent verification;
- rewrite receipt history;
- allow stale authority to execute;
- equate offline cognition with offline sovereign authority;
- add a generic shell or arbitrary execution path to the authority surface;
- expose privileged browser tokens or direct browser-to-L1 data paths.

## 54. Assimilation modes

```text
ANALYZE_ONLY
PROPOSE
IMPLEMENT
```

### ANALYZE_ONLY

May create:

- claim graph;
- conflict report;
- gap report;
- recommendations.

May not change baseline or implementation.

### PROPOSE

May additionally create:

- ADR;
- candidate contracts;
- migration plan;
- test plan;
- branch/change manifest.

May not approve or merge itself.

### IMPLEMENT

Requires a governed effect/change manifest and appropriate approval. Produces implementation and documentation evidence.

## 55. Anti-entropy test

Before introducing a new daemon/service/schema:

```text
Does this already exist?
Can an existing owner absorb it?
Can this be a contract instead of a daemon?
Can this be a library instead of a service?
Can this be a cartridge instead of Core?
Can this extend a versioned schema rather than create a parallel schema?
Does this shrink or expand the authority plane?
```

Preferred order:

```text
contract > service
library > daemon
cartridge > Core
projection > duplicate state
reference > copied data
extension > parallel subsystem
```

## 56. Assimilation status machine

```text
INGESTED
-> NORMALIZED
-> COMPARED
-> PROPOSED
-> VERIFIED
-> APPROVED
-> IMPLEMENTED
-> TESTED
-> OPERABLE
-> RECEIPTED
-> ASSIMILATED
```

Failure/hold:

```text
DUPLICATE
REJECTED
QUARANTINED
CONFLICT
MIGRATION_REQUIRED
```

Only `ASSIMILATED` changes the canonical baseline.

## 57. Assimilation manifest

Required root artifact:

```json
{
  "schemaVersion": "camelot-assimilation/1",
  "assimilationId": "asm_...",
  "baseline": {
    "documentId": "CAMELOT-OS-MASTER-SUITE-vMAX-3.1-20260914",
    "version": "3.1.0",
    "digest": "sha256:..."
  },
  "sources": [],
  "scope": [],
  "claims": [],
  "conflicts": [],
  "acceptedDeltas": [],
  "rejectedDeltas": [],
  "quarantinedDeltas": [],
  "requiredMigrations": [],
  "requiredTests": [],
  "requiredApprovals": [],
  "rollbackPlan": {},
  "evidenceBundleDigest": "sha256:...",
  "status": "PROPOSED"
}
```

## 58. Assimilation implementation location

Assimilation is NOT a new RP1 authority service.

Recommended placement:

```text
RP3/RP4 governance workflow
+ DL5 reflection artifacts
+ existing Sentinel / Excalibur / Gideon / Arthur / Ledger controls
```

A signed `Architecture Assimilation Cartridge` MAY perform ingest, diffing, mapping and proposal generation.

It cannot approve itself, issue leases, merge itself, or promote `SOVEREIGN_TRUTH`.

---

# Part XI - Extensions, Voice, QR and Embodiment

## 59. Cartridge contract

A cartridge is a signed immutable capability package.

It may contain:

- WASM components;
- schemas;
- workflows;
- prompts;
- UI panels;
- tool adapters;
- test vectors;
- provenance;
- declared network/data/effect requirements.

Installation does not grant action authority.

Runtime actions still require current leases.

## 60. Pill contract

Pills are signed declarative overlays.

They MAY:

- narrow a tool allowlist;
- enable a declared skill;
- modify presentation/tone;
- add retrieval constraints;
- lower effect tier;
- require extra evidence.

They MUST NOT:

- add undeclared tools;
- raise effect tier;
- alter tenant scope;
- override Sentinel;
- inject unrestricted authority instructions;
- introduce arbitrary native code by default.

## 61. Avatar Knight

Avatar Knight = embodiment, not authority.

The Avatar may carry:

```text
visual assets
voice profile
persona profile
skill metadata
task assignment
read-only authority/evidence context
```

The Avatar cannot own policy keys or sovereign leases.

## 62. Voice

Voice converts speech into intent.

For consequential actions:

```text
voice intent
-> canonical operation preview
-> step-up confirmation
-> Excalibur Approval Certificate
-> Sentinel decision/lease
```

A wake phrase is not authorization.

## 63. QR

QR payloads are untrusted intent/pairing/reference carriers.

Allowed categories:

```text
Quest QR
Prompt Template QR
Install QR
Pairing QR
Approval QR
Recovery Crystal QR
World Tree read-only QR
```

QR MUST NOT contain:

- Sentinel leases;
- reusable bearer tokens;
- private keys;
- mTLS private keys;
- database credentials;
- promotion authority;
- generic shell commands;
- unsandboxed package binaries.

---

# Part XII - Enterprise Release and Delivery

## 64. Mandatory production gates

A production release requires:

- architecture/threat-model approval;
- versioned contracts;
- reproducible signed build;
- SBOM and provenance;
- secret/license/dependency/vulnerability scans;
- no unresolved Critical finding;
- Rust fmt/check/test/clippy for relevant crates;
- Go test/vet for gateways;
- TypeScript typecheck/build for PWA;
- canonicalization fixtures;
- key rotation/revocation tests;
- epoch freshness/fencing tests;
- promotion replay/conflict tests;
- receipt-chain verifier;
- RLS/cross-tenant tests;
- Bifrost route deny/replay/idempotency tests;
- VFS traversal/artifact mismatch tests;
- Wasmtime sandbox tests;
- Firecracker isolation tests where enabled;
- revocation propagation test;
- World Tree stale/verified labeling tests;
- backup and fresh-host restore drill;
- Twin-Brain planned promotion/failover/failback drill;
- resource pressure/shedding drill;
- clock-skew drill;
- dashboards/alerts/runbooks validated;
- release approval receipt;
- Doc-Check.

## 65. Golden Path acceptance rehearsal

A release candidate is not considered enterprise-ready until this sequence passes repeatedly:

```text
Create tenant
Create operator
Authenticate
Create workspace
Submit read-only research mission
Bifrost admits
Sentinel decides
Lease issued
VFS attests
WASM executes
Evidence emitted
Gideon verifies
Arthur resolves
Ledger receipts
State projects
World Tree displays VERIFIED

Restart services

Replay mission history
Verify Ledger chain
Verify same final state

Attempt foreign-tenant access -> DENIED
Attempt stale lease -> DENIED
Attempt stale epoch -> DENIED
Tamper receipt -> INVALID
Retry same consequential idempotency key -> existing disposition
Restore clean host -> authority lineage validates
```

## 66. Delivery train

### T0 - Convergence

- zero required CI red gates;
- contract and formatting discipline;
- no architectural expansion.

### T1 - Contract Freeze

- frozen v1 catalog;
- bindings/fixtures;
- CONTRACTS.lock.

### T2 - Sovereign Spine

- Bifrost;
- Sentinel;
- PostgreSQL/RLS;
- Ledger/replay;
- State.

### T3 - Safe Execution

- VFS;
- governed Wasmtime;
- evidence envelope.

### T4 - Golden Mission

- read-only research;
- Gideon;
- Arthur;
- receipt;
- verified World Tree.

### T5 - Consequential Authority

- Excalibur Approval Certificate;
- typed effect registry;
- controlled reversible writes.

### T6 - Evaluation Forge

- Firecracker/remote evaluation;
- candidate promotion evidence.

### T7 - Resilience

- Twin-Brain;
- backup/restore;
- failover/failback;
- authority-lock/key compromise drills.

### T8 - Enterprise Identity and Operations

- OIDC;
- JIT privilege;
- SCIM as required;
- SLO/error budget;
- incident program.

### T9 - Controlled Extension

- signed cartridges;
- Pills;
- Voice;
- Avatars;
- broader connectors.

### T10 - Sovereign Platform

- multi-failure-domain deployment;
- trusted publisher ecosystem;
- mature Assimilation loop;
- measured enterprise SLA.

---

# Part XIII - Current Implementation Truth and Feedback

## 67. Thread-derived implementation state

The thread indicates substantial implementation already exists in Camelot-VPS, including native Bifrost contracts, signed Sentinel leases, VFS attestations, bounded Wasmtime execution, State snapshot/SSE projection, hardened systemd services, and draft Twin-Brain fencing work.

This documentation does NOT independently certify those implementations. Their production status remains governed by CI, repository review, deployment evidence and release receipts.

## 68. Principal architectural strengths

1. **Proposal and authority are separated.** This is the strongest property of Camelot.
2. **Offline cognition does not become offline sovereignty.**
3. **Receipt-backed finality creates a defensible audit model.**
4. **World Tree is a projection rather than a second control plane.**
5. **Cartridge/Pill modularity can scale without granting implicit privilege.**
6. **Twin-Brain epochs provide a strong split-brain fencing primitive.**
7. **The native/systemd posture matches the constrained VPS objective.**
8. **The new Assimilation Protocol turns architectural evolution itself into a governed workflow.**

## 69. Highest-priority unresolved work

1. Finish dynamic epoch enforcement through every consequential consumer, especially Arthur and receipt admission if not already complete.
2. Freeze the full v1 contract catalog and canonicalization profile.
3. Make durable Bifrost idempotency/replay authoritative for consequential effects.
4. Prove PostgreSQL RLS and application tenancy with adversarial tests.
5. Finish the Read-Only Research Golden Mission end to end.
6. Implement exact-manifest Approval Certificate.
7. Complete independent receipt verification and checkpoint restore.
8. Define and test key lifecycle/rotation/revocation.
9. Perform clean-host backup restore and Twin-Brain failover/failback drills.
10. Establish enterprise IAM and operational ownership before broad tenants.
11. Keep Firecracker and external integrations out of the critical path until the Golden Mission is boringly reliable.
12. Prevent architecture accretion by requiring Assimilation manifests for material new subsystems.

## 70. Architecture simplifications adopted

This reforge intentionally avoids several sources of needless complexity:

- Bifrost is not mandatory for every local same-host call.
- Redis is not authority storage.
- MinIO is not a constitutional dependency.
- Vector retrieval is an adapter, not a sovereign database requirement.
- Assimilation is not a new authority daemon.
- Avatar/Voice/World Tree remain RP5/RP6 concerns.
- The authority plane stays compact.
- `authorityEpoch` v1 is finished before Authority Vector v2 is introduced.
- Runtime planes and documentation layers no longer collide in naming.

## 71. Development guidance

The next development objective should be:

> **One complete, receipt-backed Golden Mission that survives restart, replay, tenant substitution, stale authority, tampering, and clean-host restoration.**

Do not add new power before existing power is provably governed.

---

# Part XIV - Legacy Assimilation Map

## 72. Cognitive Camelot / Magnum Opus legacy normalization

Earlier Cognitive Camelot and Magnum Opus materials contain valuable persona, cartridge, memory, and orchestration concepts. vMAX 3.1 retains them only in bounded form.

| Legacy concept | vMAX 3.1 normalization |
|---|---|
| Round Table personas | signed Persona/Knight profiles in RP6 |
| Cartridges / Knowledge Glyphs | governed signed Cartridges |
| Persona prompt overlays | declarative Pills, subject to non-escalation |
| Titan memory / graph memory | Cloudbrain/UKG/retrieval under tenant/data policy |
| Reflexion/MIRAS | proposal/evaluation workflow, never authority |
| Squire commands | UI/CLI intent syntax that produces Quest Envelopes |
| Forge a Knight | creates signed candidate persona/skill metadata, not direct runtime authority |
| “Hive mind” | orchestration metaphor only; no shared implicit authority |
| Legacy security persona | policy/security proposals; Sentinel remains authority |
| Legacy “memory writes” | proposals or provisional events until governed canonicalization |

Legacy material is historical inspiration, not an authority contract unless explicitly assimilated into the current baseline.

---

# Part XV - Final SOVEREIGN_TRUTH

```text
THE VPS HOSTS.
THE ROAD GRANTS PASSAGE.
THE ROUTER ASSIGNS THE QUEST.
THE KNIGHT PROPOSES THE DEED.
THE CROWN GRANTS PERMISSION.
THE EXECUTOR ACTS WITHIN BOUNDS.
GIDEON VERIFIES.
ARTHUR RESOLVES.
THE LEDGER REMEMBERS.
THE STATE SERVICE ORDERS.
THE WORLD TREE REVEALS VERIFIED STATE.

THE SHADOW PRESERVES KNOWLEDGE.
ISOLATION DOES NOT CREATE SOVEREIGN POWER.

NEW KNOWLEDGE MAY CHALLENGE THE CASTLE.
IT MAY NOT SILENTLY REWRITE IT.

NO UI, VOICE, AVATAR, CARTRIDGE, PILL, KNIGHT, MODEL, ROUTER,
OR TRANSPORT MAY POSSESS IMPLICIT SOVEREIGN AUTHORITY.

IDENTITY DEFINES SCOPE.
POLICY DEFINES PERMISSION.
LEASES BOUND ACTION.
EPOCHS FENCE AUTHORITY.
EVIDENCE PRECEDES FINALITY.
RECEIPTS PRESERVE TRUTH.
RECOVERY IS TESTED, NOT ASSUMED.
PRODUCTION STATUS IS EVIDENCE-BASED.
```

**⚜ SOVEREIGN_TRUTH**
