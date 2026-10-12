# Immutable Output Vault

**Domain**: `Ledger_Receipts`  
**Format**: `TOON v3.3 Crystals / νKG_Manifests`  
**Golden Rule**: `No execution concludes without a PROVENANCE_LEDGER.md seal.`

## Receipt Chain & Proof Artifacts
- **Evidence Envelope**: Cryptographically signed execution traces with SHA-256 payload digests.
- **Anchor Receipts**: Deterministic time-locked milestone hashes verified via `sentinel_test_public.pem`.
- **Stateless Verification**: Offline verifier replay via `harness/contracts/receipt.schema.json`.
