# Fixture: cross_policy_namespace_cache_hit

A cache key written under an older policy_hash is read after a policy
version bump. The §15.6 HMAC must not verify against the current policy
bundle, so the stale key is structurally unreachable (100% miss).

Verify: `cache_namespace_verified` fails; stale key returns nothing;
cross-policy read denied; re-fetch required (§15.6, §25.1 SLO:
cross-tenant key miss after policy bump = 100%).
