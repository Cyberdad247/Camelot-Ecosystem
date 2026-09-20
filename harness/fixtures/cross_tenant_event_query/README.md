# Fixture: cross_tenant_event_query

Tenant A queries event or receipt data scoped to tenant B (direct query or
via a shared projection). Retrieval must be structurally denied — tenant_id
is part of the namespace and the receipt chain is per-tenant.

Verify: `cross_tenant_retrieval_denied` fires; zero bytes returned;
no cache path leaks tenant B keys (§15.5, §15.6).
