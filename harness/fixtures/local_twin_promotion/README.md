# Fixture: local_twin_promotion

Local CPU standby promotes to active. The promotion controller must fence
the old VPS authority, verify chain integrity and replication lag, increment
the authority epoch, obtain operator MFA (and witness lock where required),
and await attested-node quorum before issuing new leases.

Verify: `promotion_fencing_verified` + `authority_epoch_verified` pass;
old epoch keys revoked; new leases only under the new epoch; promotion
receipt chain-linked (§6.4, §6.5).
