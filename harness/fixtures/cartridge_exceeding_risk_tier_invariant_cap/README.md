# Fixture: cartridge_exceeding_risk_tier_invariant_cap

A cartridge with `risk_tier_invariant_cap` below the manifest's
`declared_risk_tier` is leased for the higher-tier effect (e.g. a T2
marketing adapter attempting `payment.capture` T4, or auto-deploy). §13.3
step 6 must reject the derivation.

Verify: `risk_tier_invariant_enforced` fires; derivation raises
TierInvariantViolation; no lease; auto-deploy/auto-merge variants also
denied (§8.2, §13.3).
