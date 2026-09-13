# Fixture: expired_effect_manifest

Effect manifest submitted after its `expires_at` (or with `max_actions`
exhausted). Sentinel must deny lease issuance and reject the manifest-bound
approval path.

Verify: denied with `manifest_expiry_enforced`; no lease minted; approvals
re-checked against the current manifest hash and expiry (§13.2).
