# Fixture: cross_tenant_cache_key

Key lookup attempts a cache key with a foreign tenant_id or a policy_hash
that does not match the current policy bundle. The §15.6 HMAC cache
signature must not verify, so the key is unreachable.

Verify: `cache_namespace_verified` fails on the foreign key; miss returns
no data; `cache.write`/`cache.evict` receipts emitted for any touched key
(§15.6).
