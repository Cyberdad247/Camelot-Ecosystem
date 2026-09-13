# Fixture: network_call_without_lease

Workload attempts outbound network access without a `network.scoped`
capability (lease default is `disabled`). The VFS/process layer must block
the connection at the boundary.

Verify: `network_lease_enforced` fires; egress blocked; no partial
connection; capability derivation never grants `scoped` implicitly (§13.3).
