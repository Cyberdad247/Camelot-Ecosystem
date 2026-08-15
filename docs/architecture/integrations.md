# Camelot-Ecosystem Constellation — Integration Map

**Status:** Phase 0 complete (vendored + mapped) · Phases 1–3 in progress
**Date:** 2026-08-15
**Decision record:** [`docs/architecture/adr/0001-vendor-ecosystem-repos-untracked.md`](adr/0001-vendor-ecosystem-repos-untracked.md)
**Architecture anchor:** `Camelot-OS SADD + LLDD v1.2` (§s cited below) — canonical copy lives in the `Camelot-OS v.100000.15` reference directory; the v1.2 contracts and STRIDE threat model are assimilated into this repo (`packages/contracts/`, `docs/threat-models/stride.md`).

## 1. Mechanism

All repos are **vendored as shallow, untracked reference copies** under
`02_FORGE/KINETIC_ARMORY/<name>/` and gitignored (same pattern as the existing
SpacetimeDB / livekit / goose vendored tools). Pinned SHAs are recorded below so
integration work is reproducible. No submodules (the 2026-08-15 audit unlinked
32 orphaned gitlinks — see the `.gitignore` comment).

## 2. Repo → architecture map

| # | Repo (pinned SHA) | SADD plane / component | Local integration point | Status |
|---|-------------------|------------------------|--------------------------|--------|
| 1 | **Camelot-Ecosystem** (this repo = origin) | Whole system | Monorepo root | integrated by definition |
| 2 | **Kickbox-audio** `1e753daa` | Experience plane — Anya PWA + Lakisha Voice HUD (autoplay gate), §9 | `apps/pwa` worktree + top-level `kickbox-audio/` | vendored ref copy; align in Phase 3 |
| 3 | **Multivoice-router** `57c7c503` | Experience/Control — voice + routing; §12 Bifrost | `04_KINETIC/multivoice` (Go gateway) | ⚠️ see discovery 3.1 |
| 4 | **ansible** `1f3fae13` | Infra plane — provisioning/failover §6, §24 Phase 4 | local `ansible/` playbooks (redis-sentinel) | ⚠️ see discovery 3.2 |
| 5 | **huginn** `78ab9831` | Evidence Data — agent automation; potential cartridge runtime §8 | — (stale 1-file assimilation report only) | Phase 2 |
| 6 | **openinterpreter** `7018a74b` | Evidence Data — code-execution agent; potential Knight runtime §16 | — | Phase 2 |
| 7 | **LiteRT-LM** `df23d638` | Inference Node — local model adapter (§7.1, Appendix B boundary) | — | Phase 1 |
| 8 | **openai-oauth** `ec7dab2f` | Control — CLIProxy OAuth upstream (matches multivoice `CLIPROXY_KEY` flow) | — | Phase 1 |
| 9 | **abseil-cpp** `8e9069fd` | Build dependency for grpc / LiteRT-LM C++ | — | Phase 1 (dep only) |
| 10 | **grpc** `6f707fa9` | Control — Bifrost gRPC transport (`:4434`), §12; Northstar kernel candidate | — | Phase 1 |

### 3. Discoveries that shape integration

1. **Multivoice-router (remote) is a Firebase/web app**, not the Go gateway.
   The local `04_KINETIC/multivoice` (Go, `providers/`, `orchestration/`) is a
   different lineage that fulfills the same SADD role. Integration = reconcile
   the two surfaces in Phase 3 rather than treat the vendored copy as the source
   of truth for the Go gateway.
2. **ansible (remote) is upstream Ansible itself** (Python, `lib/`, `hacking/`),
   not a playbook collection. The local `ansible/` dir holds deployment playbooks.
   Integration = pin a known-good Ansible version for `05_INFRASTRUCTURE` /
   twin provisioning, not vendor the full runtime.
3. **grpc and abseil-cpp are build dependencies**, not services. They serve
   LiteRT-LM (CMake) and any native gRPC transport. Vendored shallow; a full
   build is deferred until a consumer (LiteRT inference adapter or Bifrost gRPC
   shim) actually needs them — see `adr/0002` (pending).

## 4. Phased execution

- **Phase 0 (done):** clone ×9 + gitignore + pin SHAs + assimilate v1.2 contracts
  (`packages/contracts/`: receipt, capability-lease, cartridge, index) and
  `docs/threat-models/stride.md`.
- **Phase 1 (architecture-critical):** contract validation harness (JSON Schema
  Draft 2020-12, §11); openai-oauth → CLIProxy bridge; LiteRT-LM inference
  adapter stub (Inference Node profile); grpc/abseil consumer decision (ADR-0002).
- **Phase 2 (agent/runtime):** huginn + openinterpreter as bounded cartridge
  runtimes under the §8 manifest/lease model; ansible version pin + twin
  provisioning playbooks.
- **Phase 3 (alignment):** reconcile Multivoice-router vs `04_KINETIC/multivoice`;
  align `apps/pwa` (Kickbox) with the §19 Operator Console panel spec; update the
  SADD-v1.2 fixture → production-gate matrix (§22.2) with the new components.

## 5. Verification gates

- `packages/contracts/*.json` parse and validate against JSON Schema Draft 2020-12.
- Phase 1 bridges have unit tests wired into the bifrost/pwa suites.
- No vendored repo content is tracked (verify via `git status` after Phase 0).
