# Camelot-OS — Northstar Size Budget (v1.2)

**Canonical source of:** Appendix B of `Camelot-OS SADD + LLDD v1.2.md`.
**Rule:** this table is authoritative. Changes land here first, then Appendix B is synchronized. CI enforces `northstar_size_budget_enforced`.

The 16 MB Camelot control kernel contains the following components. Sizes are upper-bound KiB estimates assuming release-mode C/Rust with `-Os` and minimal dependencies.

| Component | Estimated size (KiB) | Notes |
|-----------|----------------------|-------|
| Sentinel core (policy + lease engine) | 600 | pure logic, deterministic |
| Bifrost Hub core (transport, auth, mTLS) | 450 | includes minimal TLS |
| Receipt service (chain ledger) | 350 | hash-link ring buffer |
| Authority epoch service | 50 | monotonic counter + signer |
| Node registry | 200 | node + cartridge + revocation |
| Cartridge registry | 200 | signed manifest index |
| Secret broker (handles only) | 300 | secrets live in HSM/keystore |
| Evidence index | 250 | pointers + hashes |
| Promotion lock + fencing | 100 | |
| Authority CLI / surface | 80 | |
| Local witness stub | 100 | optional; only if hosting witness role |
| Crypto primitives (sha256, ed25519, xchacha20) | 600 | mandatory |
| Logging + structured events | 200 | |
| Bootloader + signed config loader | 150 | |
| Reserve / fault headroom | ~2,470 | ~15% of budget |
| **Total** | **~16,000 KiB (16 MB)** | |

## Boundary rule

Everything in the table above counts toward the 16 MB control budget. The following are **explicitly non-control-plane** and have their own budgets:

- OpenViking context filesystem
- Graphify knowledge graph
- MemPalace memory lifecycle engine
- Redis TTL cache
- Open Notebook private research
- NotebookLM external integration
- Local model adapters (Inference Node)

Adjacent services may be larger than the control plane by orders of magnitude. The Northstar target is that the **control plane itself** is small enough to fit on constrained hardware and to be auditable in full.

## Verification gate

`northstar_size_budget_enforced`: build artifacts within ±5% of table; CI rejects larger binaries.

## Maintenance

- Update this file when a control-plane component is added, removed, or resized.
- Sync the change into Appendix B of the SADD (which defers to this file as canonical).
- The budget is part of the Phase 0 delivery roadmap (§24 of the SADD).
