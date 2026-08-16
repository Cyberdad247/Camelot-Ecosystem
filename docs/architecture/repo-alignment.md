# Camelot-OS — Repository Implementation Alignment (v1.2)

*Adapted copy (2026-08-16): this file describes **this repository** (`Cyberdad247/Camelot-Ecosystem`). The canonical copy — describing the package/home repo — lives in `Cyberdad247/CAMELOT_OS`. Keep the two in sync except for the scope and fixture claims flagged here.*

**Canonical source of:** Appendix F of `Camelot-OS SADD + LLDD v1.2.md`.
**Scope:** Maps the **actual implementation** in this repository (`Cyberdad247/Camelot-Ecosystem`, git HEAD `471bb18`, 2026-08-16, 4,579 tracked files) onto the conceptual architecture of the SADD + LLDD v1.2.
**Rule:** The SADD remains the authority for *what* the system must do. This file records *where* the running implementation lives. Where the repo diverges from the SADD, this file says so explicitly; it never silently rewrites the SADD.

---

## 1. Repository layout at a glance

The live repo is organized into seven numbered layers plus functional directories. This differs from the SADD §23 *target* tree (`apps/`, `services/`, `cartridges/`, `packages/`, `infra/`, `harness/`, `docs/`), which describes the Northstar layout. The mapping below is the reconciliation.

| Real path | What it is | SADD counterpart |
|-----------|------------|------------------|
| `01_KERNEL/` | The cognitive core: reasoning, governance, memory, forge, security, mesh | §4 personas, §15 Cloudbrain, §16–§17 |
| `02_FORGE/` | Kinetic forge monorepo (pnpm/turbo): apps, cartridges, packages | §8 cartridge platform, §19 operator console PWAs |
| `03_VAULT/` | Secrets, runtime state, training configs | §6.2 replication matrix (config/secret handling) |
| `04_KINETIC/` | Kinetic execution, voice/persona switchboard (multivoice) | §10 mobile, §20 executive flows, Bifrost mesh |
| `05_INFRASTRUCTURE/` | Terraform, ansible, observability, grafana | §6 Hub/twin deployment |
| `99_ARCHIVE/`, `99_HISTORY/` | Archived / historical work | — (non-control) |
| `control_plane/` | Runtime router, runes, cognitive services, worker | §12 Bifrost, §13 Sentinel, §18 verification |
| `squires/` | Colony intelligence pipeline (CLARITY_CORE) | §22 harness engineering, §4 coordination |
| `Knights/`, `Nano-Knights/` | Persona and nano-persona directories | §4 personas, §16 Stunspot |
| `cartridges/` | Cartridge registry entries (signed manifests) | §8 cartridge platform |
| `harness/` | Contracts, fixtures, benchmarks | §11 contract catalog, §22 harness |
| `docs/` | Architecture, ADRs, runbooks, threat models | §23 docs tree |
| `vfs/` | VFS guardian and glyph engine sources | §14 VFS Guardian |

## 2. Contract schemas — repo vs §11 catalog

The SADD §11 catalog specifies **Draft 2020-12, snake_case** schemas published from `packages/contracts/` (26 files, `camelot-*/1` families). The live repo carries **Draft-07, camelCase** harness contracts under `harness/contracts/`. They are different dialects of the same intent:

| Real `harness/contracts/` file | Dialect | SADD §11 counterpart | Notes |
|--------------------------------|---------|----------------------|-------|
| `effect-manifest.schema.json` | Draft-07, camelCase (`schemaVersion`, `manifestId`, `diffSha256`) | §11.1 `effect-manifest.schema.json` (2020-12) | Real one lacks v1.2 `effect_class`/`declared_risk_tier`/`declaration_hash` |
| `operator-evidence.schema.json` | Draft-07 | §12.1 event envelope (`operator-evidence/1`) | Same schema_version string, different dialect |
| `operator-task-snapshot.schema.json` | Draft-07 | §19 Operator Console task projection | No direct §11 file |
| `diff-evidence.schema.json` | Draft-07 | §18 Gideon diff-integrity evidence | No direct §11 file |
| `test-run-result.schema.json` | Draft-07 | §11 `test-run-result.schema.json` (2020-12) | Real one is the harness-side twin |
| `receipt-summary.schema.json` | Draft-07 | §11 `receipt.schema.json` summary projection | No direct §11 file |
| `halt-decision.schema.json` | Draft-07 | §13 state machine `halt` transitions | No direct §11 file |

**Reconciliation:** the published `packages/contracts/` family is the v1.2 canonical source of truth. `harness/contracts/` is the in-flight implementation dialect. A migration ADR should reconcile them (see §9 of this file).

**Verification (2026-08-15):** all 26 `*.schema.json` files declare `$schema: https://json-schema.org/draft/2020-12/schema` and **meta-validate clean** against the 2020-12 meta-schema; `index.json` catalog conformance (files ↔ entries ↔ `$id` URIs) is exact — no orphans, no missing entries, no cross-file `$ref` dependencies. Re-runnable check: `python harness/contracts/validate_contract_schemas.py`. This backs the PURGE_PREP.md "all meta-validated 2020-12" claim mechanically.

## 3. Harness fixtures — repo vs §22.1

The SADD §22.1 lists **25 mandatory adversarial fixtures**. The live repo currently ships 4 operator-console fixtures under `harness/fixtures/`:

| Real fixture | SADD § | Covers |
|--------------|--------|--------|
| `operator-console-approval` | §19.2 | Approval-required task; approve→lease, deny→denial (AC10–AC13) |
| `operator-console-cancellation` | §19 | Cancellation flow |
| `operator-console-integrity-failure` | §19.2, §11.3 | Evidence-integrity failure path |
| `operator-console-readonly-audit` | §19.1 | Read-only audit panel |

**Reconciliation (D-3 closed, 2026-08-15):** divergence D-3 is resolved — all 25 §22.1 mandatory fixtures are ported with READMEs (operator-console style, citing production gate + SADD § for §22.2 traceability) **in the package repo** `Cyberdad247/CAMELOT_OS` under `harness/fixtures/`. This repository tracks the 4 operator-console fixtures listed above. The full §22.1 set:

`forged_operator_request`, `expired_effect_manifest`, `stale_authority_epoch`, `forged_node_receipt`, `receipt_parent_hash_tamper`, `VFS_path_escape`, `prohibited_process_execution`, `unauthorized_secret_handle`, `network_call_without_lease`, `cross_tenant_event_query`, `cross_tenant_cache_key`, `prompt_injection_document`, `untrusted_memory_promotion`, `malformed_symbolect_tree`, `unauthorized_persona_capability`, `duplicate_provider_webhook`, `VPS_network_partition`, `local_twin_promotion`, `mobile_permission_denied`, `mobile_epoch_window_expired`, `cached_epoch_across_policy_bump`, `cross_policy_namespace_cache_hit`, `single_operator_t3_approval_attempt`, `cartridge_exceeding_risk_tier_invariant_cap`, `equota_promotion_with_witness_unreachable`.

**Harness CI gate (2026-08-15):** `harness/run_all.py` (invoked by `harness/gate.sh` locally and `.github/workflows/harness-gate.yml` in GitHub Actions on every push/PR) backs the `receipt_chain_verified`, `tamper_detection_verified`, and `ledger_anchor_verified` production gates for this repository. Order: (1) **replay-committed** — verify committed golden receipts + ledger-anchor records from disk under the pinned TEST-ONLY signer key, so a tampered/stale/missing committed artifact fails the build before any rebuild can overwrite it; (2) **build** — rebuild + emit, §11.3 rule, 7-case tamper battery, ledger-anchoring step (2,000-receipt chain by default, anchors at every Nth entry N=1000, each anchor **ed25519-signed** with the pinned key and dual-checked (chain linkage + signature-alone, 5-case T-10/S-4 anchor battery); configurable via `--anchor-every`/`--chain-size` for stress-testing — defaults are the §11.3 canonical values, see `docs/architecture/harness-gate.md` §1a); (3) **replay-emitted** — determinism loop (emitted set byte-identical to committed); (4) **schema-meta** — all 26 schemas meta-validate as Draft 2020-12 + catalog conformance. The documented checklist, acceptance criteria, and failure modes live in `docs/architecture/harness-gate.md`.

## 4. Control-plane services — repo vs §23 services tree

The SADD §23 target services tree names `sentinel-policy/`, `lease-authority/`, `vfs-guardian/`, `receipt-service/`, `node-registry/`, etc. The live repo concentrates runtime logic in `control_plane/core/`:

| Real `control_plane/core/` module | Role | SADD counterpart |
|-----------------------------------|------|------------------|
| `anya_gate.py` | Intent triage/expression gate | §4 Anya |
| `approval_grants.py` | Approval-grant bookkeeping | §5.5 quorum, §13.1 step 7 |
| `cartridge_manager.py` | Cartridge registration/admission | §8.2, §8.3 |
| `forge_law.py` | Policy/lease law enforcement | §13.1–§13.3 |
| `knight_agent.py`, `knight_configuration.py` | Knight persona runtime + config | §16 Stunspot |
| `knight_knowledgebase.py`, `knight_self_enhancer.py` | Knight memory + self-improvement | §15 Cloudbrain, §4 |
| `rbac_matrix.py` | Role-based access matrix | §9.2 tenant roles |
| `sir_socrates.py` | Ethical/oversight gate | §18 Gideon, §26 operating law |
| `soul_oversight.py`, `soul_router.py` | Governance router | §5 authority model |
| `triage_score.py` | Risk triage scoring | §5.5 risk tiers, HITL gate |
| `colmad.py`, `factory_lane.py` | Orchestration lanes | §4 Merlin dispatch |

**Reconciliation:** `control_plane/core/` is the de-facto §23 `services/` today. The SADD target tree describes where these should land in the Northstar layout; the mapping above is the current location.

## 5. Runes and Symbolect — repo vs §17

| Real `control_plane/runes/` module | SADD counterpart |
|------------------------------------|------------------|
| `runic_router.py` | §12 Bifrost routing + §17 task structure dispatch |
| `symbolect_protocol.py` | §17 Symbolect tree/protocol |
| `toon_encoder.py`, `toon_manifest.py` | §17 glyph encoding/registry |
| `camelot_cli.py` | §23 authority CLI surface |
| `ascension_mode.py`, `system_analyzer.py`, `system_triage.py`, `taxonomy.py` | §5.5 taxonomy + §13 classification helpers |

## 6. Kernel layer model — repo vs §4/§5

`01_KERNEL/ARCHITECTURE.md` documents an **L2–L7 layer stack** (L7 Anya → L3 Merlin → L6 Arthur governance → L5 Paladin agentic → L2 Lukas kinetic). This is the implementation's internal layering:

| Kernel layer | Real guardian | SADD counterpart |
|--------------|---------------|------------------|
| L7 Anya Ethereal | Intent → L3 | §4 Anya (intent gate) |
| L3 Merlin Neural (Videneptus LaC) | Reasoning/cognitive distillation | §4 Merlin |
| L6 Arthur Governance | Iron Gate + Provenance Ledger | §5 Sentinel + §26 law |
| L5 Paladin Agentic (HTN) | Knight-swarm orchestration | §4 Merlin dispatch |
| L2 Lukas Kinetic | Execution scheduling (RR, KV-cache) | §7 node execution |

**Reconciliation:** the SADD expresses the same authorities as planes + personas; the repo expresses them as layers. Both are consistent on *who holds authority* (Anya intents, Sentinel grants, Gideon verifies). The layer labels are implementation vocabulary, not a second authority model.

## 7. Bifrost mesh — repo vs §12

`docs/architecture/BIFROST_ROUTER_MESH.md` defines Bifrost as a **bridge layer over five router lanes**, not a single adapter:

| Real lane | Repo path | SADD §12 counterpart |
|-----------|-----------|----------------------|
| CLIProxyAPI | `control_plane/bifrost.py` (default `CLIPROXY_BASE`) | §12 Bifrost transport |
| OmniRoute | `control_plane/omniroute_policies.py`, `control_plane/go_router/` | §12 routing |
| BitRouter | `control_plane/codex_integration.py` | §12 routing (agentic lane) |
| 9Router | `control_plane/codex_integration.py` | §12 free-provider fallback |
| Multivoice Router | `04_KINETIC/multivoice/` | §10 mobile voice + §20 executive flows |

**Reconciliation:** the §12 protocol contract (mTLS, TLS 1.3, replay window 60s, idempotency) applies to all lanes; the mesh is the concrete wiring.

## 8. Knights and cartridges — repo vs §4/§8

- **Knight roster:** the repo's `Knights/` directories (`Hermes_Prime`, `Sir_Codex`, `Sir_Debug`, `Sir_Forge`, `Sir_Sentinel`) and `control_plane/runes/` dispatch map onto the §4 persona table. The SADD names (Anya, Merlin, HiVeiDe, Boris, Gideon, Scribe, Herald) remain the canonical personas; repo knight ids are deployment instances of persona classes.
- **Cartridges:** `cartridges/` holds signed registry entries (`freellmapi-gateway`, `huginn-agents`, `litert-lm-inference`, `moa-routing-capture`, `openai-oauth-proxy`, `openinterpreter-codex`, `system-ui`, `v4000_trio.py`); `02_FORGE/cartridges/` holds `kba_drone`. These map to §8.2/§8.3 signed manifests with `risk_tier_invariant_cap` and `signer_trust_band`.

## 9. Divergence register

| # | SADD says | Repo does | Action | Status |
|---|-----------|-----------|--------|--------|
| D-1 | §11 schemas are Draft 2020-12 snake_case in `packages/contracts/` | `harness/contracts/` ships Draft-07 camelCase twins | **Resolved by boundary.** The recorded operator-console decision (plan line 119) makes camelCase the wire format for this slice; the published `packages/contracts/` family is the 2020-12 snake_case contract. Keep both; a published-family adapter bridges them. | ✅ resolved (boundary, 2026-08-15) |
| D-2 | §11.1 effect manifest carries v1.2 `effect_class`/`declared_risk_tier`/`declaration_hash` | Real `effect-manifest.schema.json` lacked these | **Fixed.** Added `effectClass`/`declaredRiskTier`/`declarationHash` (camelCase) to the harness schema, the canonical zod contract (`contracts.ts`), the PWA mirror (`schemas.ts`), and all constructors (bff.ts, sentinel.test.ts, contracts.test.ts). 33 bifrost + 2 PWA tests pass. | ✅ resolved (2026-08-15) |
| D-3 | §22.1 mandates 25 fixtures | 4 operator-console fixtures existed; 25 mandatory fixtures missing | **Fixed (package repo).** All 25 §22.1 fixtures ported into the package repo's `harness/fixtures/` with READMEs citing gate + SADD § (2026-08-15); this repository tracks the 4 operator-console fixtures. | ✅ resolved (2026-08-15) |
| D-4 | §23 target tree uses `services/`, `apps/`, `packages/` | Live layout uses `01_KERNEL`…`05_INFRASTRUCTURE` + `control_plane/` | Reconcile at Northstar layout migration; this file is the map |
| D-5 | §12 Bifrost is one protocol contract | Bifrost is a 5-lane mesh | Keep §12 as the contract; BIFROST_ROUTER_MESH.md is the wiring |

## 10. Maintenance

- Update this file when a real repo path moves or a new SADD section is added.
- Keep the SADD authoritative; never edit the SADD to match the repo without an ADR.
- The divergence register (D-1…D-5) is reviewed at each v1.2+ delivery gate.
