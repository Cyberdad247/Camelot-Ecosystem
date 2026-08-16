# Camelot-OS — Trust Bands (v1.2)

**Canonical source of:** §7.3 and Appendix C of `Camelot-OS SADD + LLDD v1.2.md`.
**Rule:** this table is authoritative. Changes land here first, then the SADD is synchronized.

A node is admitted at a trust band that gates what it may receive, run, and attest. Bands are issued by Sentinel based on hardware attestation, network class, and recent health.

| Band | Admission criteria | Capabilities |
|------|---------------------|--------------|
| `attested` | Verified TPM/SEV/TEE root + signed CSR + current epoch + healthy heartbeat | Receive leases for any effect class; participate in promotion quorum |
| `attested-witness` | Above + dedicated signing key pinned in policy bundle | Issue promotion lock grants |
| `enrolled` | Signed CSR + current epoch + healthy heartbeat | Receive T0–T2 leases only |
| `probationary` | Enrolled missing one of {fresh epoch, recent health, signed bundle} | Receive T0 leases only |
| `quarantined` | Manual or Sentinel-quarantined | No new leases; existing leases revoked at next epoch |
| `revoked` | Explicit revocation record | No Bifrost session; evidence-only |

## Promotion quorum

A failover proceeds only if at least 3 nodes in the `attested` band have responded to epoch broadcast within the SLO budget (§25.1 of the SADD). Two is acceptable only for `manual_failover` with operator MFA.

## Witness band specifics

- A witness must hold an `attested-witness` trust band with hardware-root attestation and a publicly verifiable signing key.
- The witness key fingerprint is pinned into the policy bundle; rotation requires a Sentinel epoch increment (§6.5 of the SADD).

## Enforcement points

- Sentinel admission flow (`/v1/nodes/enroll`) issues bands from this table (Phase 0, §24 of the SADD).
- Capability derivation (§13.3) subtracts capabilities when `node.trust_band` does not permit the effect class.
- VFS preflight includes `node_trust_band_permits` (§14.1 of the SADD).
- STRIDE threat model tracks band bypass as S-2/S-6 (spoofing of node or witness identity).

## Maintenance

- Update this file when admission criteria or per-band capabilities change.
- Sync the change into §7.3 / Appendix C of the SADD (which defer to this file as canonical).
