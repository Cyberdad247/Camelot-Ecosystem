# Camelot-OS — Effect Classes & Risk Tiers (v1.2)

**Canonical source of:** §5.5 and Appendix D of `Camelot-OS SADD + LLDD v1.2.md`.
**Rule:** this table is authoritative. Changes land here first, then the SADD and the published `effect_class` enums in `packages/contracts/` are synchronized.

Effect classes are the canonical labels that flow from intent through to receipts. Risk tiers drive the approval/quorum required; they are not assigned freeform by individual agents.

| Effect class | Default tier | Lease required | Quorum | Examples |
|--------------|--------------|----------------|--------|----------|
| `ro.fetch` | T0 | none | n/a | source read, graph query |
| `ro.audit` | T0 | none | n/a | static audit, map |
| `internal.synth` | T1 | yes | 1 | summary, report |
| `workspace.test` | T1 | yes | 1 | run unit tests in worktree |
| `workspace.patch` | T2 | yes | 1 | ephemeral worktree patch, not promoted |
| `promote.worktree.merge` | T3 | yes | 2 | merge candidate to base |
| `promote.deploy` | T4 | yes | 2 + witness | production deploy |
| `external.publish.draft` | T1 | yes | 1 | generate draft only |
| `external.publish.publish` | T3 | yes | 2 | live send / post |
| `external.email.send` | T3 | yes | 2 | transactional outbound |
| `payment.invoice.draft` | T1 | yes | 1 | draft invoice |
| `payment.invoice.issue` | T3 | yes | 2 | collectible invoice |
| `payment.capture` | T4 | yes | 2 + witness | charge customer |
| `payment.refund` | T4 | yes | 2 + witness | reverse charge |
| `device.calendar.write` | T2 | yes | 1 | add event |
| `device.sms.send` | T3 | yes | 2 | outbound SMS |
| `device.call.initiate` | T3 | yes | 2 | outbound call |
| `promote.failover` | T4 | yes | 2 + witness | VPS→local promotion |

## Tiers

- **T0** — no effect; pure read.
- **T1** — single operator approval required.
- **T2** — single operator approval with mandatory manifest disclosure.
- **T3** — two distinct operator approvals (Principle 15 of the SADD).
- **T4** — two approvals **and** witness promotion lock **or** external-confirmation token.

Risk tier is assigned by Sentinel based on the effect manifest and may not be downgraded by the operator.

## Enforcement anchors

- `effect_class` is a closed enum in `receipt.schema.json`, `capability-lease.schema.json`, and `effect-manifest.schema.json`.
- The effect manifest carries `declared_risk_tier`, which cannot exceed the cartridge's `risk_tier_invariant_cap` (§8.2) or the tenant's `max_risk_tier_allowed` (§9.2).
- Gideon's gates include `declared_risk_tier_matches_observable_effect` and `declared_effect_class_consistent` (§18).
- Marketing/Commerce/Wellness agency cartridges are bound to these classes via §20 flows.

## Maintenance

- Update this file when an effect class, its default tier, or its quorum changes.
- Sync the change into §5.5 / Appendix D of the SADD and the `effect_class` enums in `packages/contracts/`.
- Tier taxonomy changes are ADR-gated (see §14 RR-7 of the STRIDE threat model).
