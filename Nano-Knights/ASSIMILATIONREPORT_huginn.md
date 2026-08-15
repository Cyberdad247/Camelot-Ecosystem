# 🛡️ ASSIMILATION REPORT
**Target:** `02_FORGE/KINETIC_ARMORY/huginn` (pinned `78ab9831a`)
**Origin:** vendored 2026-08-15 (Phase 0 integration)
**Tags:** ['huginn', 'agents', 'cartridge']

## 📊 Summary
- **Vendored copy:** shallow HEAD clone, untracked (gitignored)
- **Stack:** Ruby on Rails agent platform (Gemfile, `app/`, Sidekiq agents)
- **Node profiles:** research, experience (per `cartridges/huginn-agents/manifest.json`)
- **Entrypoints:** execute, summarize, fetch
- **Cartridge:** `cartridges/huginn-agents` — signed §8.2/§8.3, cap T2

## 📝 Integration notes (inspected)
- Standalone self-hosted agents system: cron/task agents with web UI — maps to
  the SADD Evidence-Data plane as a bounded agent runtime, NOT to the control
  plane (it never issues leases).
- Bounded execution: run under a manifest-bound lease with
  `network.scoped` + `process.allowlisted` only; deny list enforced by the
  cartridge manifest (`unrestricted.network`, `direct_main_branch_write`, …).
- Rollback is `manual_compensation_required` — agents may have had side
  effects; the operator must review receipts before re-running.
- Prior `ASSIMILATIONREPORT_C_Users_vizio_Projects_huginn.md` indexed 1 file
  from a local checkout; this report supersedes it with the vendored copy.

---
**[SIR FORGE]:** "The context is siphoned."
