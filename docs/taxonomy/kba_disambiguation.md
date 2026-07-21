# KBA Namespace Disambiguation (DRAFT / PENDING HITL)

> **Status:** PROPOSAL ONLY. This ADR-style entry is not yet ratified. It exists to clear
> Gate `G4_kba_taxonomy` in `docs/seeds/gcmn_vmax_nano_seed/Plan.json`. Operator sign-off
> required before the GCMN vMAX stub activation (Gate G6) can clear.
>
> **Source seeds:**
> - Pasted `gcmn_vmax_nano_seed` (untrusted external input, owner=`untrusted_external_seed`).
>   See `docs/seeds/gcmn_vmax_nano_seed/Plan.json`.
> - Existing CAMELOT-OS subsystems. See `control_plane/drone_node.py`,
>   `control_plane/KBA_DRONE_RUNBOOK.md`, `02_FORGE/cartridge/kba_tools.py`,
>   `blueprints/v9000.96/wasmtime_sentinel_audit.md`,
>   `03_VAULT/UKG/nodes/UKG_NANO_SWARM_V1000.json`.

---

## 1. TL;DR

The `KBA` prefix in CAMELOT-OS is **not** a wildcard. It already names the deployed **KickBox
Audio empire-drone ecosystem** and several siblings. The pasted GCMN vMAX seed proposed a
separate `KBA_SERVICES_NODE_PRIME` with 6 cartridges — two of those cartridge names
(`AALIYAH`, `AEGIS`) collide with **deployed** KBA infrastructure. Without renames, the seed
cannot be ratified.

**Decision proposed:** **(B) Strict Separation** — the seed lives under `GCMN_*` namespace;
`KBA` remains canonically KickBox Audio. Carve-outs:
- `AALIYAH` (seed) must be renamed before seal — collides with `aaliyah_comms.wasm`.
- `AEGIS` (seed) must be renamed before seal — collides with `Aegis_eBPF_O1_Telemetry_Redaction`.
- All other seed cartridge names are clean.

## 2. The Deployed KBA Ecosystem (DO NOT BREAK)

| Surface | Surface ID | Kind | Where it lives | Notes |
|---|---|---|---|---|
| `kba-drone-1`    | `KBA_DRONE_NODE`        | deployed | `control_plane/drone_node.py` | Default empire-drone on `100.125.205.66:9000` |
| `kba-drone-lakesha` | `KBA_DRONE_NODE`     | deployed | `blueprints/v9000.99/lakesha_taildrop_plan.md` | Taildrop variant at `100.100.155.55:9000` |
| `kba-drone-test` | `KBA_DRONE_NODE`        | deployed (tests) | `control_plane/test_drone_node.py` | Loopback test rig |
| `KBA_CORE` cartridge | `KBA_CARTRIDGE`     | deployed | `drone_node.py` L62 + manifests at `02_FORGE/cartridge/packages/KBA_CORE/manifest.json` | Signed via `CAMELOT_CARTRIDGE_HMAC_KEY` |
| AALIYAH comms WASM | `AALIYAH_COMMS_CARTRIDGE` | deployed | `blueprints/v9000.96/wasmtime_sentinel_audit.md`: sha256=`9D8CF6B5F8E13622B1087FB596B722A30E58CABF953F4A4B7A55AA24C72F1095` | Deployed to `/opt/camelot/cartridges/pills/aaliyah_comms.wasm` |
| AEGIS eBPF redact | `AEGIS_EBPF_REDACT`    | deployed | `03_VAULT/UKG/nodes/UKG_NANO_SWARM_V1000.json` `Aegis_eBPF_O1_Telemetry_Redaction` + `01_KERNEL/security/aegis_ebpf_redact()` | Bind-to-sink node in swarm; security swiss-army |

`KBA` in `KBA_DRONE` = **KickBox Audio** (literal — this came from the original product line
at `bin/kba_drone_boot.sh`). The patterns are battle-tested, audit-anchored in
`docs/reports/external_camelot_custody_audit.md`, and **cannot be moved or renamed without
coordinated tailnet cutover**.

> **Round-trip note:** the row above lists 6 surfaces, but the JSON companion
> (`kba_disambiguation.json`) collapses the 3 KBA-drone instances (`kba-drone-1`,
> `kba-drone-lakesha`, `kba-drone-test`) into a single `KBA_DRONE_NODE` member with
> `instance_examples[]` for the 3 names. The collapse is intentional — the drone is one
> surface with multiple meshnodes, not three surfaces.

## 3. The Seed Proposal (WHAT KBA_SERVICES Claims)

`KBA_SERVICES_NODE_PRIME` (νKG fingerprint `νKG_CRYSTAL_OMEGA_STANDARDIZED`, owner
`untrusted_external_seed`, vMAX) is an aspirational "context-compiler hypervisor under an 8GB
edge ceiling." The seed proposes 6 cartridges:

| Seed ID | Seed domain | Vendor stack | Surface mapping |
|---|---|---|---|
| `AALIYAH`   | Email SaaS           | Listmonk, Mautic     | ~~collides with `AALIYAH_COMMS_CARTRIDGE`~~ |
| `CASTELLON` | Property Mgmt        | Plane, Docspell      | clean |
| `AEGIS`     | Streaming Support    | Chatwoot, KillBill   | ~~collides with `AEGIS_EBPF_REDACT`~~ |
| `BARISTA`   | Coffee Logistics     | Odoo Community       | clean |
| `CHRONO`    | Executive Scheduling | Cal.com, n8n         | clean |
| `LEDGER`    | Financial Core       | Frappe Accounting    | clean |

Plus 4 stub runes in `control_plane/runic_router.py` (gated by
`CAMELOT_GCMN_STUBS_ENABLED=1`):

| Seed Rune | Cross-reference to existing surfaces |
|---|---|
| `//SYNC_KBA_DATABASES_SQLCIPHER` | none — clean |
| `//LOCK_BIFROST_mTLS_KYBER768`   | partly overlaps `//BIFROST_LOCK` and `bin/bifrost.py` + `control_plane/pqcrypto_bridge.py` (the seed's own stub metadata already acknowledges this) |
| `//ENGAGE_RUST_IRON_DAEMON`      | may namespace-clash with `04_KINETIC/` binaries |
| `//CRYSTALLIZE_GCMN_vMAX`        | overlaps semantics with `//NANO_SWARM_EXPAND` + `cartridge_manager` |

## 4. Collision Map (the substantive finding)

| Seed term | Deployed reality | Severity | Resolution required |
|---|---|---|---|
| `AALIYAH` (seed: email SaaS) | `aaliyah_comms.wasm` (deployed communications cartridge) | **HARD** | seed must rename to e.g. `AMANI_email` |
| `AEGIS` (seed: streaming support) | `Aegis_eBPF_O1_Telemetry_Redaction` (deployed security subsystem) | **HARD** | seed must rename to e.g. `ARGUS_streaming` |
| `KBA_SERVICES` (seed: orchestrator) | `KBA_DRONE_NODE` (deployed tailnet audio worker) | **HARD** | seed lives under `KBA_SERVICES` only as a sibling surface; mark routing_policy = `strict_separated` |
| `//LOCK_BIFROST_mTLS_KYBER768` (seed stub) | `bin/bifrost.py` + `control_plane/pqcrypto_bridge.py` (deployed mTLS+Kyber) | MEDIUM (already noted in seed stub metadata) | approve seed stub as documentation-only, never as alternate stack |
| `CASTELLON`, `BARISTA`, `CHRONO`, `LEDGER` | none | LOW | clean |

## 5. Recommended Action

### Decision: (B) Strict Separation

> **"KBA_SERVICES"** in the pasted seed is independent from **`KBA_DRONE`**; the
> shared `KBA` prefix is incidental and the namespaces will diverge. Renames of
> `AALIYAH` and `AEGIS` are required before seed ratification.

The seed remains inert (`CAMELOT_GCMN_STUBS_ENABLED=0` by default) — but the seed's
collisions are surfaced here for the next operator walk-around.

### Concrete renames (proposed)

| Original (seed) | Renamed (proposed) | Reason |
|---|---|---|
| `AALIYAH`  | `AMANI`   | collides with `aaliyah_comms.wasm` (operator should also lock `AMANI*` reserved) |
| `AEGIS`    | `ARGUS`   | collides with `Aegis_eBPF_O1_Telemetry_Redaction` security swiss-army |
| `KBA_SERVICES_NODE_PRIME` | `GCMN_SERVICES_NODE_PRIME` | clarifies the family-root divergence |

Note: the seed itself in `Plan.json` already records `R6 — KBA_SERVICES vs KBA_DRONE
namespace clash (LOW severity)` — it just hadn't yet discovered `AALIYAH` and `AEGIS`
collisions because the seed-author didn't have visibility into the deployed ecosystem.

## 6. Machine-readable Companion

See `kba_disambiguation.json` (in this same directory). The JSON carries:

- `members[]`: {surface_id, kind, parent, scope.allowed_tools}
- `conflicts[]`: {seed_name, deployed, severity, resolution_required}
- `disambiguation_aliases`: maps both sides → family-root labels
- `routing_policy.default_kba_route`: `KBA_DRONE_NODE` (so the runic_router never lets
  unratified `KBA_*` invocations slip into the seed path)

## 7. Action Items for Operator (Gate G4 clearing checklist)

- [ ] Read this ADR.
- [ ] Set `hitl_gates[G4_kba_taxonomy].cleared` to `true` after operator sign-off. The
      field already exists on the gate and is currently `false`. Optionally also append
      `// CLEARED by operator YYYY-MM-DD` to the same gate's `criteria` string for human
      readability — the JSON boolean is the source of truth.
- [ ] Apply renames in `control_plane/runic_router.py` (`AALIYAH`→`AMANI`, `AEGIS`→`ARGUS`)
      and update `tests/control_plane/test_runic_router_gcmn_stubs.py` accordingly.
- [ ] Bump `Plan.json.stub_runes[].collision_warning` to reflect resolved status.
- [ ] Decide whether to ratify (B) Strict Separation or pivot to (C) Family — see Open Q1.
- [ ] Once G4 clears, the rest of the GCMN vMAX DAG can resume (Step 4 CART_IGNITION).

## 8. Open Questions

1. **(B) Strict Separation vs (C) Family**: This ADR recommends (B). If the operator prefers
   (C) — treating the seed as a sibling KBA-but-divergent family member — the JSON companion
   would need a `family_root: "CONVERGED_KBA"` field and the renames would not be required
   (but conflicts would remain documented).
2. **Should `KBA_CORE` (the existing cartridge) appear in the runic_router dispatch table?**
   Today it lives only as the deployed drone's signed manifest. Routing it as `//KBA_CORE`
   would let the omni-router dispatch to the drone directly — but that's a separate ADR.
3. **Should the `routing_policy` block land in `control_plane/runic_router.py` as a
   loadable companion**, or stay external? This ADR recommends external (JSON) until an
   operator wants it pinned.
4. **What happens to the existing `kba_drone_bundle/` and `camelot_kba_drone.zip`
   archives?** These are referenced in `docs/reports/external_camelot_custody_audit.md`.
   They MUST stay aligned to the deployed `KBA_DRONE` family — no cleanups without an admin.

## 9. Glossary

- **KBA** — the deployed abbreviation for **KickBox Audio**, originating in `bin/kba_drone_boot.sh`.
- **KBA_DRONE_NODE** — A Camelot-OS `tag:empire-drone` worker serving KickBox Audio; tags identify
  tailnet mesh position. Multiple instances exist (`kba-drone-1`, `kba-drone-lakesha`).
- **KBA_CORE** — The signed cartridge manifest installed on a KBA_DRONE_NODE, allowing
  `kba.status / kba.echo / kba.tts / kba.transcribe / kba.voices` plus safe built-ins.
- **AALIYAH_COMMS_CARTRIDGE** — Pre-existing WASM cartridge (`aaliyah_comms.wasm`) for
  communications workflows. NOT to be confused with the seed's "AALIYAH = Email SaaS".
- **AEGIS_EBPF_REDACT** — Pre-existing security subsystem (`01_KERNEL/security/aegis_ebpf_redact()`)
  performing O(1) telemetry redaction via eBPF. NOT to be confused with the seed's
  "AEGIS = Streaming Support".
- **KBA_SERVICES_NODE_PRIME** (seed) — Aspirational 8GB-edge hypervisor from the
  GCMN vMAX nano-seed; **inert**; **NOT** part of the KBA family by this ADR's recommendation.
- **GCMN_SERVICES_NODE_PRIME** (renamed canonical) — Post-rename canonical ID for what the
  seed originally called `KBA_SERVICES_NODE_PRIME`. Use this on the seed once the ADR ratifies.
- **AMANI** (rename proposed) — Replacement ID for the seed's `AALIYAH` (Email SaaS); chosen
  to defuse collision with `AALIYAH_COMMS_CARTRIDGE`. Treat the `AMANI` namespace as
  reserved for the seed's email pipeline.
- **ARGUS** (rename proposed) — Replacement ID for the seed's `AEGIS` (Streaming Support);
  chosen to defuse collision with `AEGIS_EBPF_REDACT` security swiss-army. Treat `ARGUS` as
  reserved for the seed's streaming cartridge.

## 10. Cross-references

```json
{
  "plan_id": "gcmn_vmax_nano_seed_plan_2026_07_15",
  "seed_doc": "docs/seeds/gcmn_vmax_nano_seed/Plan.json",
  "seed_markdown": "docs/seeds/gcmn_vmax_nano_seed/seed.md",
  "taxonomy_doc_markdown": "docs/taxonomy/kba_disambiguation.md",
  "taxonomy_doc_json": "docs/taxonomy/kba_disambiguation.json",
  "stub_dispatch_module": "control_plane/runic_router.py",
  "stub_tests": "tests/control_plane/test_runic_router_gcmn_stubs.py"
}
```
