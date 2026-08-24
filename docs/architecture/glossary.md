# Camelot-OS — Canonical Glossary (v1.2)

**Canonical source of:** the Glossary block of `Camelot-OS SADD + LLDD v1.2.md` (Appendix A).
**Rule:** these terms bind the SADD, LLDD, threat model, schemas, and code. Drift between prose and code is a defect; report it to the SADD owner.

---

- **Camelot-OS** — the system as a whole (control + commerce + agency PWAs + mobile).
- **Cybertronia** — the authoritative control plane (VPS + twin + Sentinel + Bifrost + registries + receipts).
- **Knight** — a bounded persona compiled by Stunspot with declared prohibited capabilities.
- **Nano-Knight** — a derivative Knight compiled for short-lived, ephemeral tasks under the same authority model.
- **Cartridge** — signed, versioned, registered, admitted bounded behavior. Never an authority.
- **Manifest** — pinned, hash-bound declaration of intent (`effect_manifest`).
- **Lease** — short-lived signed permission bound to a manifest, node, workload, and authority epoch.
- **Authority epoch** — monotonic, globally observed counter that invalidates stale leases on key/policy rotation or failover.
- **Receipt** — hash-linked, signed record of a meaningful state transition.
- **Sentinel** — the sole authority-issuing service. Has the only privilege to grant leases.
- **Bifrost** — the only transport-with-identity service. It authenticates; it does not authorize.
- **VFS Guardian** — the only workspace and source-admission authority.
- **Cloudbrain** — the memory plane (MemPalace, OpenViking, Graphify, Redis, Open Notebook). Scopes memory; does not authorize.
- **Stunspot** — the persona compiler.
- **Symbolect** — the compact approved task-structure language.
- **Gideon** — independent verifier. Pass/block only.
- **Boris** — bounded contract-test generator and runner. Read-only / test-worktree-write under lease.
- **Scribe** — receipt-aggregator/verifier-summary Knight. Distinct from Gideon (binary verdict) and Herald (notification). Direct effect authority: None.
- **Herald** — receipt-to-user surfacing (notifications, dashboards). Direct effect authority: None.
- **Anya** — intent, planning, expression gate. Direct effect authority: None.
- **Merlin** — task-DAG compilation, adapter selection, bounded dispatch. Direct effect authority: None.
- **HiVeiDe / HiveIDE** — repository mapping, path locks, dependency graph. Direct effect authority: None.
- **Witness** — external grantor of a promotion lock that does not run agents.
- **Operator** — authenticated human with tenant-scoped role and effect-approval privileges.
- **Effect class** — canonical label for a classified effect (§5.5 of the SADD), e.g. `workspace.patch`, `payment.capture`, `promote.failover`. Closed enum; classification is not freeform.
- **Risk tier** — the approval/quorum class (T0–T4) assigned by Sentinel to an effect; it cannot be downgraded by an operator.
- **Trust band** — the admission class of a node (§7.3 of the SADD): `attested`, `attested-witness`, `enrolled`, `probationary`, `quarantined`, `revoked`.
- **Policy pack** — a domain-scoped set of policy rules (consent/suppression, claims, wellness, commerce) applied by Sentinel at classification time.
- **Receipt chain** — the per-tenant hash-linked, ledger-anchored record of consequential state transitions; the single source of truth (§11.3 of the SADD).
- **Promotion lock** — an exclusive fencing primitive granted by a witness (or operator MFA + attested-node quorum) that permits standby promotion (§6.5 of the SADD).

---

**Coordination authority** ≠ **Direct effect authority**. A Knight may coordinate execution without being able to perform or grant a consequential effect; that distinction is made explicit per persona in §4 of the SADD.
