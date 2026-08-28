# Fixture: stale_authority_epoch

Node presents a lease or control message signed under an authority epoch
below the currently trusted epoch (e.g. after a policy bump, key rotation,
or failover). Receivers must reject the message.

Verify: `stale_epoch_rejection_tested` passes; stale leases and control
messages denied; old leases already revoked at the epoch boundary (§6.3,
§13.1).
