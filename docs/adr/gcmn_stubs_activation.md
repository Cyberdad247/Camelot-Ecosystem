# Activation ADR: `CAMELOT_GCMN_STUBS_ENABLED` (RATIFIED 2026-07-15)

> **Status:** ✅ RATIFIED — operator HITL on `2026-07-15T05:30:00Z`. Gate `G6_stub_activation`
> in `docs/seeds/gcmn_vmax_nano_seed/Plan.json` cleared to `true`. The flag may now be
> flipped to `"1"` at the operator's runtime discretion (separate operator act).
>
> **Operator signoff:** `vizio` (chat-message authorization) → activator `sir_sentinel`,
> degraded witness `CAMELOT_OPS_EMERGENCY=1`. Detailed cascade metadata captured in the
> `operator_signoff` block of `gcmn_stubs_activation.json` (cleared_gates, deferred_prereqs,
> ceremony_witness, g4_escalation, r6_owner_reclaimed, ledger_entry_ref) and in
> `PROVENANCE_LEDGER.md` entry 1735.
>
> **Source documents:**
> - `docs/seeds/gcmn_vmax_nano_seed/Plan.json` — 6 risks + 8 HITL gates (post-escalation) + feature_gate block.
> - `docs/taxonomy/kba_disambiguation.md` — sibling ADR for the namespace dispute (Gate G4).
> - `control_plane/runic_router.py::GCMN_STUB_RUNES` — the 4 stub runes that flip on/off with this feature gate.
> - `tests/control_plane/test_runic_router_gcmn_stubs.py` — test pins that gate the invariant.

---

## 1. TL;DR

`CAMELOT_GCMN_STUBS_ENABLED` is a single-string opt-in feature gate. Default value is `null`
(off). Acceptable value on activation is `"1"`. While off, the 4 stub runes
(`//SYNC_KBA_DATABASES_SQLCIPHER`, `//LOCK_BIFROST_mTLS_KYBER768`, `//ENGAGE_RUST_IRON_DAEMON`,
`//CRYSTALLIZE_GCMN_vMAX`) dispatch as `UNKNOWN_RUNE` and escalate. While on, the runes fire
through `_dispatch_gcmn_stub` and emit a sealed TODO envelope (`task_id: gcmn-stub-XXXXXXXX`,
`queued: false`, `metadata.status: "STUB_INERT"`). **Activation is inert-by-design** — the
gate never causes an action-taking invocation, only a documented no-op.

**Decision proposed:** Activation requires **5 of 6 risks explicitly accepted** as
BLOCKER, plus 1 accepted as TRACKER. **Zero IGNORABLE.** Activation ADR is owned by
`sir_sentinel`. The flag carries a 90-day sunset (anchored to the activation timestamp,
not a fixed seed date) and a one-command rollback playbook.

---

## 2. Context & Scope

The 4 stub runes were authored in `control_plane/runic_router.py` to mirror the 4 stub
specs in `Plan.json.stub_runes[]`. They exist so that operator-routed GCMN vMAX DAG traffic
produces audit-able, deterministic envelopes rather than throwing unknown-rune errors. They
are explicitly inert by design: `noop_emitter = control_plane.runic_router._dispatch_gcmn_stub`
returns a JSON envelope; no side-effect, no DB write, no queue push.

The flag is an **environment-level opt-in** — not a persistence-layer setting. It gates the
dispatch path only. Test pins live at `tests/control_plane/test_runic_router_gcmn_stubs.py`:
they must pass **regardless** of the flag's value.

Activation is gated because:
1. Some risks (R1, R2, R4, R5) involve runtime hazards that would surface only when the
   downstream code is *eventually* fleshed out by the planned DAG steps.
2. The taxonomy clash (R6) revealed HARD cartridge-name collisions (`AALIYAH`,
   `AEGIS`) that change the gate calculus.
3. The stub-redundancy risk (R3) needs explicit operator acknowledgement that the
   `//LOCK_BIFROST_mTLS_KYBER768` stub will *never* be promoted to an alternate stack even
   when active.

---

## 3. HITL Risk Adjudication

Every Plan.json risk is mapped to a gate (existing or proposed). Verdict is BLOCKER (must be
cleared before the flag may flip), TRACKER (must be acknowledged in the gate's `criteria`
string but doesn't block), or IGNORABLE (orthogonal — and we have zero of those today).

| Risk | Severity | Existing Gate | Proposed Gate | Verdict | Required Acceptance Artifacts |
|---|---|---|---|---|---|
| **R1** — 30B OOM on edge                          | HIGH   | `G1_mobile_oom`          | —                         | **BLOCKER** | `G1.cleared: true` + signed cognitive-load acknowledgment of BiFrost-30B OOM budget on the 8GB edge ceiling, with Audex-2B mobile-fallback explicitly named. |
| **R2** — Kyber-768 Wasm Edge limits               | HIGH   | `G2_kyber_wasm`          | —                         | **BLOCKER** | `G2.cleared: true` + interop test report against the deployed `pqcrypto_bridge.py` + Vercel Edge route-limit measurement. |
| **R3** — Stub redundancy with deployed Bifrost+Kyber | MEDIUM | (none)                   | `G7_bifrost_redundancy` *(TRACKER / non-blocking)* | **TRACKER** | `G7.cleared: true` after operator asserts the `//LOCK_BIFROST_mTLS_KYBER768` stub will never execute as a live mTLS dispatcher; runtime rejects any attempt to do so. |
| **R4** — SQLCipher KDF undefined                  | MEDIUM | `G3_sqlcipher_kdf`       | —                         | **BLOCKER** | `G3.cleared: true` + ratified KDF rotation policy (quarterly rotation semantics) referenced from `AGENTS.md`. |
| **R5** — Mobile tier adjudication not wired       | MEDIUM | (none)                   | `G8_mobile_adjudication` *(BLOCKER)* | **BLOCKER** | `G8.cleared: true` after `cybertronia-mobile` gate demonstrably cascades from `step_2_hardware_allocation` to `Audex-2B` mobile fallback; integration test recorded. |
| **R6** — KBA_SERVICES vs KBA_DRONE namespace clash | LOW    | `G4_kba_taxonomy` *(currently non-blocking)* | — | **BLOCKER** *(escalated per §4)* | `G4.cleared: true` per `docs/taxonomy/kba_disambiguation.md` ratification + `AALIYAH → AMANI` and `AEGIS → ARGUS` renames applied to the seed + `KBA_SERVICES_NODE_PRIME → GCMN_SERVICES_NODE_PRIME` namespace pivot. |

**Result:** **5 BLOCKER + 1 TRACKER = 6-of-6 risks must carry an explicit, recorded
acceptance artifact before the flag may flip to "1".**

### Proposed Plan.json gate changes

If the operator agrees with this ADR, the Plan.json `hitl_gates[]` should grow by two new
gates (`G7_stub_redundancy`, `G8_mobile_adjudication`), and `G4_kba_taxonomy.blocking`
should escalate from `false` to `true`. The ADR does **not** auto-apply these changes; they
are listed here for operator confirmation.

```diff
   {"gate_id": "G4_kba_taxonomy",     ...   "blocking": false, ...}
-                                       ↓
+  {"gate_id": "G4_kba_taxonomy",     ...   "blocking": true,  ...}

+  {"gate_id": "G7_bifrost_redundancy","trigger_step": "step_3_topology_mount",    "blocking": false, "criteria": "//LOCK_BIFROST_mTLS_KYBER768 acknowledged documentation-only, never executes live",       "cleared": false, "decision_doc": "docs/adr/gcmn_stubs_activation.md"},
+  {"gate_id": "G8_mobile_adjudication","trigger_step": "step_2_hardware_allocation", "blocking": true,  "criteria": "cybertronia-mobile gate wired + Audex-2B fallback demonstrably cascades",      "cleared": false, "decision_doc": "docs/adr/gcmn_stubs_activation.md"},
```

The `G6_stub_activation` gate's `criteria` is updated to read:
`"all six blocking gates cleared (G1, G2, G3, G4 [now blocking], G5, G8) + TRACKER G7 acknowledged + CAMELOT_GCMN_STUBS_ENABLED=1"`.

> **Dependency order (linear, not circular):** ratify `kba_disambiguation` ADR →
> apply renames (`AALIYAH→AMANI`, `AEGIS→ARGUS`, `KBA_SERVICES_NODE_PRIME→GCMN_SERVICES_NODE_PRIME`)
> → mark G4 `cleared: true` → mark G6 `cleared: true` → flip the flag.

---

## 4. Escalation of Gate G4 (from non-blocking to blocking)

The original `hitl_gates[G4_kba_taxonomy].blocking: false` was set when the seed author
didn't yet know about the HARD collisions with `aaliyah_comms.wasm` and
`Aegis_eBPF_O1_Telemetry_Redaction`. The `kba_disambiguation` taxonomy ADR then surfaced
two HARD collisions (`AALIYAH`, `AEGIS`). Without renames land in the seed before any stub
is dispatched, the runic_router cannot guarantee the seed path won't accidentally conflict
with the deployed audio-drone or the eBPF security subsystem. **G4 must therefore become
`blocking: true`** before any flag flip is safe.

This ADR recommends the operator apply the escalation in the same Plan.json update batch
as the new G7/G8 entries, so the field-set change is atomic and audit-linked.

---

## 5. New Gates (G7, G8) Proposed

### G7 — Bifrost Stub Redundancy (R3, TRACKER, non-blocking)

> Named `G7_bifrost_redundancy` for specificity (matches R3's deployed artifact
> `bin/bifrost.py` + `control_plane/pqcrypto_bridge.py`) and to leave room for any future
> generic stub-tracking gate without naming collision.

*   **Why a gate at all?** R3 is documented in the seed's own stub metadata
    (`//LOCK_BIFROST_mTLS_KYBER768.collision_warning`); the operator must explicitly
    acknowledge the seed knows its stub is partly redundant. Tracking the acknowledgement
    in a gate keeps the audit trail honest even though the gate does not block.

*   **What makes it clearable?** Operator (or delegated knight — likely `sir_sentinel`)
    adds a tombstone annotation to the stub's `collision_warning` in Plan.json:
    `"// acknowledged: documentation-only // never promote to alternate stack"`, then sets
    `cleared: true`.

### G8 — Mobile Tier Adjudication Wired (R5, BLOCKER)

*   **Why blocking?** R5 missing means the R1 mitigation (Audex-2B fallback on mobile) is
    unreachable. Activation should not be possible while the cascade is broken.

*   **What makes it clearable?** Run the documented cascade test from
    `step_2_hardware_allocation`, observe Audex-2B routing on the mobile `cybertronia-mobile`
    profile, record the integration test output (sha256 of the test receipt suffices).

---

## 6. Owner Assignment

| Concern | Owner | Rationale |
|---|---|---|
| Activation ADR (this doc)              | `sir_sentinel`        | Cross-cutting authority over security (R4), edge limits (R2), and routing (G6). |
| R6 (escalated from `undecided`)        | `sir_sentinel`        | Already owns the KBA disambiguation ADR; structural integrity of namespace routing is security-adjacent. |
| R1 / R5 (mobile OOM + tier adjudication) | `sir_boris` (per Plan.json) | Unchanged. |
| R2 / R4 (Wasm + KDF)                   | `sir_sentinel` (per Plan.json) | Unchanged. |
| R3 (stub redundancy)                   | `sir_heimdall` (per Plan.json). G7 acknowledgement delegated to activation owner. |
| Activation flip-and-record ceremony    | `sir_sentinel` (operator) + `CAMELOT_OPS_EMERGENCY=1` witness | The witness is the witness env var set by `sir_octavian`; treats ops sign-off as env-var-bearer rather than cryptographic signature. |

---

## 7. Sunset / Expiry Policy

The flag is not a permanent mode. Activation imposes a strict **90-day TTL** anchored to
the **activation timestamp** (recorded at flag-flip time), not to the seed's `generated_at`.
Anchoring to the activation timestamp means each flip gets its own clean 90-day window —
operators who delay ratification do not get unfairly short windows.

*   **`activation_timestamp`** (proposed): recorded in `PROVENANCE_LEDGER.md` at the moment
    `CAMELOT_GCMN_STUBS_ENABLED=1` first takes effect during a session.
*   **Default sunset deadline**: `activation_timestamp + 90 days`.
*   **Reference point for migration**: `seed_generated_at = 2026-07-15T04:30:00Z`; the
    seed was authored on this date. Used for archival only — not for sunset calc.
*   **Auto-deactivation trigger**: a daily cron (`bin/sweep_inert_stubs.sh` — **PROPOSED,
    not shipped**) checks the current time vs `activation_timestamp + 90d`.

**Tiered auto-deactivation** (default is non-destructive — operator must decline renewal
multiple times before the runtime dispatches are pruned):

*   **Tier 1 (first sunset, default):**
    1. Unsets `CAMELOT_GCMN_STUBS_ENABLED` in operator-managed `.env`,
    2. Marks `Plan.json.status: "SUNSET_TIER1"` (recoverable — flip again any time),
    3. Appends `sweep_tier1_<timestamp>` to `PROVENANCE_LEDGER.md`,
    4. Sets `expired: true`, `expired_reason: "tier1 sunset reached without operator ratification"`.
*   **Tier 2 (second consecutive sunset with no renewal between):**
    1. Same as Tier 1, plus
    2. Permanently removes the 4 entries from `control_plane/runic_router.py::GCMN_STUB_RUNES`
       (destructive — write-time code-edit, recorded as `prune_<timestamp>` in PROVENANCE_LEDGER.md),
    3. Sets `Plan.json.status: "ARCHIVED_ABANDONED"`.
    4. Sets `expired_reason: "tier2 sunset reached after consecutive unrecovered cycle"`.

*   **Renewal path**: an operator can extend the deadline by RE-signing this ADR with a new
    `sunset_days` ASR (Activation Sunset Renewal) entry. Each renewal appends to
    `PROVENANCE_LEDGER.md` and resets the consecutive-cycle counter to zero.

*   **No implicit rollover**: the only way the flag survives past the deadline is an
    explicit renewal. This forecloses "the flag has been on for a year and nobody noticed"
    active-maintenance debt.

> **PROPOSED-but-not-shipped dependencies:** `bin/sweep_inert_stubs.sh` does not currently
> exist in the active tree. The activation flip is gated on the operator confirming the
> cron will be installed (or accepting a manual sweep cadence). See §8 for the same caveat
> on `01_KERNEL/audit_redact.py` and `runic_router --purge_stubs`.

---

## 8. Rollback Runbook

A single-command-and-three-step playbook for unflicking the gate after activation. Each step
records into `PROVENANCE_LEDGER.md`.

> **PROPOSED-but-not-shipped dependencies:**
> - **`01_KERNEL/audit_redact.py`** — referenced by steps 2 and 3. Does not currently exist
>   in the active tree. Until shipped, steps 2 and 3 cannot be executed; a working alternative
>   is a manual `grep`-then-annotate loop against `PROVENANCE_LEDGER.md`. The activation flip
>   is gated on operator accepting this manual fallback OR confirming the script will be
>   implemented first.
> - **`bin/sweep_inert_stubs.sh`** — referenced by §7 (sunset cron). Same caveat.
> - **`runic_router --purge_stubs`** flag and **`STUB_PURGED`** tombstone emitter — proposed
>   for the force-kill escalation. Not currently wired; running the force-kill command today
>   will emit `argparse: unrecognized argument: --purge_stubs`. Operator must either land the
>   flag first OR accept a ship-blocking dependency on this PR.
>
> All three are PROPOSED. The activation flip is **conditional on either (a) the operator
> accepting manual-fallback workflows for these steps, or (b) the proposed scripts/flags
> being landed as part of the same activation batch.**

### Step 1 — Flip (one command)

```bash
unset CAMELOT_GCMN_STUBS_ENABLED
# Or, equivalently and more explicit:
CAMELOT_GCMN_STUBS_ENABLED=0 python -m control_plane.runic_router --list
```

After flipping, the 4 stub runes dispatch as `UNKNOWN_RUNE` again. Verification:

```bash
python -m control_plane.runic_router --rune //CRYSTALLIZE_GCMN_vMAX --task "rollback-smoke"
# Expect: directive.UNKNOWN_RUNE; metadata.warning: "ambient env unflagged"
```

### Step 2 — Audit Recall (one command)

```bash
python 01_KERNEL/audit_redact.py --namespace GCMN_STUB --tombstone STUB_REVOKED
# For each [GCMN-STUB] log line emitted while the flag was ON, append:
#   {... "tombstoned_at": "<iso>", "tombstone": "STUB_REVOKED", "decision_doc": "docs/adr/gcmn_stubs_activation.md"}
```

The redactor writes to the appropriate audit sinks (Splunk index `camelot-audit`,
ELK index `provenance`, etc.) without mutating source-of-truth ledgers. It is a read-then-emit
transform; the `[GCMN-STUB]` line stays intact for forensic purposes, but downstream SIEM
queries that filter on `tombstoned = true` SKIP the line so they don't treat vacated
envelopes as live security events.

### Step 3 — Dead-Letter (manual + opt-in)

If the operator wants the tombstoned lines physically moved to a cold archive (off the
active SIEM):

```bash
python 01_KERNEL/audit_redact.py --namespace GCMN_STUB --tombstone STUB_REVOKED --relocate /var/camelot/cold/gcmn_stub_revoked/
# Records the relocation in PROVENANCE_LEDGER.md.
```

### Force-kill variant (escalation only)

If the operator suspects the rollover is incomplete or a stub has gone rogue, an emergency
scrub is available:

```bash
python -m control_plane.runic_router --purge_stubs
# Emits a STUB_PURGED envelope, writes --purge_stubs to PROVENANCE_LEDGER.md, and disables
# the entire GCMN_STUBS path for the rest of the runtime session. Requires
# CAMELOT_OPS_EMERGENCY=1 in env as a witness.
```

---

## 9. Glossary

- **`CAMELOT_GCMN_STUBS_ENABLED`** — single-string feature-gate env var. Default off (`null`);
  the only acceptable activation value is `"1"`. Anything else is treated as off.
- **STUB_INERT** — the `metadata.status` on a sealed TODO envelope produced by the stub
  dispatcher. Confirms: queued = false, no side-effect, audit-able only.
- **STUB_REVOKED** — tombstone marker appended by the rollback's audit-redact step. Marks
  a previously-emitted `[GCMN-STUB]` log line as inert, signalling SIEM filters to skip it.
- **STUB_PURGED** — tombstone marker emitted when an operator force-kills the stub path
  via `--purge_stubs` (PROPOSED — see §8). Higher severity than STUB_REVOKED — signals
  operator-level rollback. **Important:** STUB_PURGED means "session-disabled dispatcher";
  no data is wiped (the stub never executes data — `"purge"` is a metaphor for
  "removed-from-dispatch-surface").
- **GCMN_STUB_ACTIVATION_NAMESPACE** — the logical group name this ADR operates under; the
  JSON sibling uses this as its `namespace` field.
- **Activation Sunset Renewal (ASR)** — the metadata record appended to PROVENANCE_LEDGER.md
  when extending the activation deadline past the initial 90-day sunset.

---

## 10. Cross-references

```json
{
  "plan_id": "gcmn_vmax_nano_seed_plan_2026_07_15",
  "seed_doc": "docs/seeds/gcmn_vmax_nano_seed/Plan.json",
  "seed_markdown": "docs/seeds/gcmn_vmax_nano_seed/seed.md",
  "taxonomy_doc_markdown": "docs/taxonomy/kba_disambiguation.md",
  "taxonomy_doc_json": "docs/taxonomy/kba_disambiguation.json",
  "activation_doc_markdown": "docs/adr/gcmn_stubs_activation.md",
  "activation_doc_json": "docs/adr/gcmn_stubs_activation.json",
  "stub_dispatch_module": "control_plane/runic_router.py",
  "stub_tests": "tests/control_plane/test_runic_router_gcmn_stubs.py",
  "audit_redactor": "01_KERNEL/audit_redact.py",
  "sweep_cron": "bin/sweep_inert_stubs.sh",
  "ledger": "PROVENANCE_LEDGER.md"
}
```
