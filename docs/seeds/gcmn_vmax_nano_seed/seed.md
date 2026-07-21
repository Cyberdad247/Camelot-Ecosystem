# GCMN vMAX — KBA_SERVICES_NODE_PRIME

> **Status:** `STUB_INERT` · **Source-of-truth:** [`Plan.json`](./Plan.json) · **Schema:** `camelot.os/seed/plan.v1`
>
> **Fingerprint (primary):** `νKG_CRYSTAL_OMEGA_STANDARDIZED`
> **Fingerprint (ASCII alias):** `nuKG_CRYSTAL_OMEGA_STANDARDIZED`

This seed was pasted as untrusted external input. It has been persisted as an **inert** plan
gated behind `CAMELOT_GCMN_STUBS_ENABLED=1` with HITL required before activation. See
[`Plan.json`](./Plan.json) for the canonical machine-readable form, and
[`dispatch_receipt.json`](./dispatch_receipt.json) for the verbatim `//PLAN` CLI receipt that
links this artifact to `task_id=rune-54eb616a`.

---

## 1. Prime Directive (verbatim, untrusted)

> Operate as `CONTEXT_COMPILER_HYPERVISOR` under `SUB_8GB_EDGE_CEILING` ➔
> (`Babylonian_Static == NULL`). Compress multi-platform KBA architecture into
> monotonic, isomorphic coordinate states.

`owner`: `untrusted_external_seed` · `authority`: ANYA_Ω as referenced in the seed header —
NOT ratified as authoritative; this seed is treated as level-2 untrusted operator input per
`AGENTS.md` and the `camelot-os` skill.

## 2. Primitives

| axis | value |
|---|---|
| edge ceiling | 8 GB |
| topology | `Vercel_Edge` ⊕ `Rust_Iron_Daemon_WSS` ⊕ `Kyber-768_Omni-Router` |
| mobile tier (≤ 4 GB) | `Local_Audex-2B_GGUF`, `2D_DOM_Sprite_WebGL`, thermal governor ACTIVE |
| desktop tier (≥ 16 GB) | `BiFrost_Leased_Audex-30B_TriModal`, `Tri-Modal_Hunyuan_WebRTC_Live2D`, HTMX SaaS |
| security profile | `Zero_Trust_v6.5` (WebAuthn + 6-digit SMTP OTP TTL 300s + multi-tenant SQLCipher) |
| SQLCipher KDF rotation | **UNDEFINED** — adopt before activation (see `G3`) |

## 3. KINETIC_FLOW_DAG

The seeded 4-step DAG, decomposed into single-knight subtasks. Step `i+1` depends on Step `i` —
order is mandatory and HITL gates fire at every transition.

| # | Step | Knight leads | Subtasks | `risk_score` | HITL |
|---|---|---|---|---|---|
| 1 | `AUTH_SHIELD` | sir_sentinel · sir_forge ×2 · sir_debug | `Setup_SQLCipher_Tenant_Isolation` · `Integrate_WebAuthn_Biometrics` · `Implement_SMTP_OTP_Fallback` · **+** `Test_Auth_Shield_Failovers` | 85 | `PROMPT` |
| 2 | `HARDWARE_ALLOCATION` | sir_boris · sir_alex · sir_sentinel | `Adjudicate_Substrate_Profile` · `Route_Audex_2B_or_BiFrost_30B` · **+** `Hardening_AgentArmor_PDG` | 95 | `HUMAN_GATE` |
| 3 | `TOPOLOGY_MOUNT` | sir_link · sir_sentinel · sir_forge · sir_ghost | `Provision_Vercel_Edge_Gateway` · `Bind_Kyber_768_mTLS_Omni` · `Initialize_Rust_Iron_Daemon_WSS` · **+** `Enforce_Privacy_Routing_Hop` | 90 | `PROMPT` |
| 4 | `CARTRIDGE_IGNITION` | sir_boris · merlin_omega · lady_apis | `Load_Business_Cartridges` · `Ignite_Scabbard_L2_Context` · **+** `Configure_Ledger_Observability` | 50 | `AUTO` |

Subtasks marked **+** are interpretive additions (TEST, HARDENING, PRIVACY routing, LEDGER
observability) — none are explicit in the pasted seed. They fill gaps where the seed is silent
and are **non-blocking** as a group, but each is individually reviewable.

## 4. Cartridges (Step 4)

| ID | Domain | Knight lead | Vendor stack (review pending) |
|---|---|---|---|
| `AALIYAH`   | Email SaaS           | sir_helio        | Listmonk, Mautic |
| `CASTELLON` | Property Management  | sir_boris        | Plane, Docspell |
| `AEGIS`     | Streaming Support    | sir_sentinel     | Chatwoot, KillBill |
| `BARISTA`   | Coffee Logistics     | sir_forge        | Odoo Community |
| `CHRONO`    | Executive Scheduling | lord_archivist   | Cal.com, n8n |
| `LEDGER`    | Financial Core       | sir_gideon       | Frappe Accounting |

> Vendor stack selections are **vendor lock-in gates** — see HITL gate `G5`.

## 5. Stub Runes (4 inert dispatches)

Added to `control_plane/runic_router.py` and gated by `CAMELOT_GCMN_STUBS_ENABLED=1`. The `spec_step`
column mirrors `Plan.json.stub_runes[].spec_step` exactly so round-tripping between the two
artifacts is mechanical:

| Rune | `spec_step` | `knight_hint` | Notes |
|---|---|---|---|
| `//SYNC_KBA_DATABASES_SQLCIPHER` | `step_1_auth_shield`        | `sir_sentinel`  | SQLCipher KDF undefined |
| `//LOCK_BIFROST_mTLS_KYBER768`   | `step_3_topology_mount`     | `sir_heimdall`  | Redundant with deployed `bin/bifrost.py` + `control_plane/pqcrypto_bridge.py` |
| `//ENGAGE_RUST_IRON_DAEMON`      | `step_3_topology_mount`     | `sir_forge`     | Namespace may clash with `04_KINETIC/` binaries |
| `//CRYSTALLIZE_GCMN_vMAX`        | `step_4_cartridge_ignition` | `sir_boris`     | Overlaps `//NANO_SWARM_EXPAND` + `cartridge_manager` |

Tests at `tests/control_plane/test_runic_router_gcmn_stubs.py` pin 8 invariants:
governance shape (governance fingerprint / HITL flag), inert-by-default over all 4 runes,
flag accepts only the literal `"1"`, opt-in sealed TODO metadata, collision-warning surfacing,
`list_runes()` visibility, and privacy-override short-circuit.

## 6. Risks

| ID | Risk | Severity | Owner | Mitigation |
|---|---|---|---|---|
| R1 | 30B OOM on edge                          | HIGH   | sir_boris     | Switch to Audex-2B / offload |
| R2 | Kyber-768 Wasm Edge limits               | HIGH   | sir_sentinel  | Pilot X25519; defer Kyber-768 |
| R3 | Stub redundancy with deployed Bifrost+Kyber | MEDIUM | sir_heimdall  | Reuse `pqcrypto_bridge.py` |
| R4 | SQLCipher KDF undefined                  | MEDIUM | sir_sentinel  | Adopt AGENTS.md KDF policy |
| R5 | Mobile tier adjudication not wired       | MEDIUM | sir_boris     | Extend `SubstrateProfile` |
| R6 | KBA_SERVICES vs KBA_DRONE namespace clash | LOW    | undecided     | Taxonomy ADR |

## 7. HITL Gates

| Gate | Trigger | Blocking? | Criteria |
|---|---|---|---|
| `G1` mobile OOM         | step 2 | ✓ | BiFrost 30B OOM budget acknowledged |
| `G2` Kyber Wasm         | step 3 | ✓ | Kyber-768 Wasm interop verified against `pqcrypto_bridge.py` |
| `G3` SQLCipher KDF      | step 1 | ✓ | SQLCipher KDF rotation policy ratified |
| `G4` KBA taxonomy       | step 4 | — | KBA_SERVICES vs KBA_DRONE namespace decided |
| `G5` vendor selection   | step 4 | ✓ | vendor_stack reviewed and ratified |
| `G6` stub activation    | this doc | ✓ | all five blocking gates cleared + `CAMELOT_GCMN_STUBS_ENABLED=1` |

## 8. Open Questions for the Operator

1. Should the four canonical rune names stay `//UPPER_SNAKE_CASE` or be lowered to
   `//lower_snake_case` for `_RUNE_ALIASES` consistency?
2. Should `//CRYSTALLIZE_GCMN_vMAX` be deprecated in favor of `//NANO_SWARM_EXPAND`?
3. Confirm cartridge ignition order (AALIYAH→CASTELLON vs CASTELLON→AALIYAH vs parallel).
4. Is `//LOCK_BIFROST_mTLS_KYBER768` purely documentation, or should it re-point to
   `bin/bifrost.py.enforce`?

---

## Re-render this seed

> **Note:** Markdown regeneration is **hand-done** — `Plan.json` is the canonical machine-
> readable source. The command below only pretty-prints the JSON; it does **not** regenerate
> this markdown. To rebuild the tables from a fresh `Plan.json`, recompute them by hand (or
> build a minimal extractor if/when R6 settles).

To inspect the canonical form:

```bash
python -c "import json,sys;print(json.dumps(json.load(open('docs/seeds/gcmn_vmax_nano_seed/Plan.json')), indent=2))"
```

To validate that the markdown and JSON stay in sync, focus on the table columns that map
1-to-1: `kinetic_dag.steps[*].risk_score`, `stub_runes[*].{spec_step,knight_hint}`, the
six `risks[*]` IDs (R1–R6), and the six `hitl_gates[*]` IDs (G1–G6).

## Cross-references

```json
{
  "plan_id": "gcmn_vmax_nano_seed_plan_2026_07_15",
  "schema": "camelot.os/seed/plan.v1",
  "Plan.json": "./Plan.json",
  "seed.md": "./seed.md",
  "dispatch_receipt.json": "./dispatch_receipt.json",
  "stub_dispatch": {
    "module": "control_plane/runic_router.py",
    "governance_constant": "GCMN_GOVERNANCE",
    "stub_runes_constant": "GCMN_STUB_RUNES",
    "feature_flag_env": "CAMELOT_GCMN_STUBS_ENABLED",
    "test_pins": "tests/control_plane/test_runic_router_gcmn_stubs.py"
  }
}
```
