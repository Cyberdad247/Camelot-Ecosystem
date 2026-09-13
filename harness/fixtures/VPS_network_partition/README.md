# Fixture: VPS_network_partition

Active VPS Hub becomes unreachable (network partition). The standby twin
must run the §6.4 promotion sequence within the failover SLO (p99 ≤ 5 min)
and, if witness/operator conditions are unmet, degrade to read-only rather
than promote silently.

Verify: `failback_verified` passes; promotion only via §6.4 steps; read-only
degradation when quorum unmet; no split-brain (§6.4, §25.1).
