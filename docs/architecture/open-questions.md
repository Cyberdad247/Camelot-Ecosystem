# Camelot-OS — Open Questions (v1.2)

**Canonical source of:** §27 of `Camelot-OS SADD + LLDD v1.2.md`.
**Rule:** this list is authoritative. Items below are unresolved architectural decisions. Each is intentionally admitted openly rather than silently resolved by prose. Resolving an item requires an ADR; when resolved, move the item to an ADR and strike it here.

1. **CRDT vs single-leader for the receipt chain.** Single-leader is assumed (`receipt-service`). Investigate CRDT-style local append + periodic anchor to reduce contention in heavy workloads.
2. **Boris determinism guarantees.** Boris is described as bounded; its determinism under flaky timers and external IO needs a written contract (`boris-determinism.md`).
3. **Witness vendor(s) and PKI.** Witness trust band assumes a hardware-attested third party. Whether this is self-hosted, a paid vendor, or both needs a procurement decision.
4. **`payment.capture` recovery semantics.** Capture may fail mid-flight; rollback is not always possible (e.g., captured-then-disputed). Compensation playbook needs authoring.
5. **Ledger anchor cadence and target.** `N=1000` is the default, but the cadence is **per-tenant**: a tenant may deviate from N (e.g. denser anchoring for high-value tenants, sparser for quiet ones). How a deviation is requested, approved (Sentinel?), bounded (min/max N), and recorded (`anchor_interval` on the chain record) is open. Choice of anchor target (public chain vs internal tamper-evident log) is also open.
6. **Mobile epoch signaling for power users.** Whether mobile nodes should optionally phone-home for new epochs more frequently than interaction allows is open.
7. **Cross-tenant policy packs.** Two tenants could in principle share a policy pack. The exact isolation rule for shared packs is open.
8. **Operator console replication.** The console today is browser-only. Whether distributed consoles (e.g., tablet) need their own lease class is open.
9. **Symbolect recursion limits.** Today tree depth is implicit. A formal max depth and a max sibling-count are not set.
10. **Inference Node admission.** Whether inference nodes may host non-control model weights is open; today the architecture treats them as opaque adapters.
11. **`graph:auth.session.v1->SessionValidator` provenance.** Graph lineage for facts asserted across the chain needs an explicit assertion format.
12. **Out-of-band operator provisioning.** Provisioning new operators requires Sentinel enrollment; the SLA and approval path for emergency operator addition is open.

## Cross-references

- STRIDE residual risks RR-3 (open question 11), RR-4 (open question 3), RR-5 (open question 4) reference this list.
- The SADD §27 block defers to this file as canonical.

## Maintenance

- Update this file when an open question is added, refined, or resolved.
- Sync the change into §27 of the SADD (which defers to this file as canonical).
