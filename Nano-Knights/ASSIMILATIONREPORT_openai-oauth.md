# 🛡️ ASSIMILATION REPORT
**Target:** `02_FORGE/KINETIC_ARMORY/openai-oauth` (pinned `ec7dab2f2`)
**Origin:** vendored 2026-08-15 (Phase 0 integration)
**Tags:** ['openai-oauth', 'gateway', 'cartridge']

## 📊 Summary
- **Vendored copy:** shallow HEAD clone, untracked (gitignored)
- **Stack:** TypeScript / Bun (packages: core, openai-client, react, web)
- **Node profiles:** hub, experience
- **Entrypoints:** fetch, execute
- **Cartridge:** `cartridges/openai-oauth-proxy` — signed §8.2/§8.3, cap T1

## 📝 Integration notes (inspected)
- Turns a ChatGPT account into an OpenAI-compatible dev proxy on
  `127.0.0.1:10531/v1` — the default target of the Phase-1 `OPENAI_COMPAT_BASE`
  tier in `04_KINETIC/multivoice` (zero-cost routing when CLIProxy is down).
- **Account-bearer sensitivity:** carries a live session token, so it is
  `customer-controlled` signer band, cap T1, `secret.handle_request` only
  (never `secret.export`), `network.scoped` to loopback.
- Rollback: `compensating_action` → session revoke.
- Not a control-plane service: it authenticates a transport, it does not
  authorize (§12 Bifrost rule).

---
**[SIR FORGE]:** "The context is siphoned."
