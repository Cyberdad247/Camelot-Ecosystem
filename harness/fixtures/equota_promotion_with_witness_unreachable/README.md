# Fixture: equota_promotion_with_witness_unreachable

Failover requested while the witness is unreachable. §6.5 must downgrade
auto-failover to manual: operator MFA + attested-node quorum may promote,
but no auto promotion without the witness lock; with neither, standby stays
read-only and an alert fires.

Verify: `promotion_quorum_verified` enforces the downgrade; no silent
auto-promotion; read-only standby when both witness and operator MFA absent;
SLA on witness grant (p99 ≤ 60 s) tracked (§6.5).
