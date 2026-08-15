# 🛡️ ASSIMILATION REPORT
**Target:** `02_FORGE/KINETIC_ARMORY/LiteRT-LM` (pinned `df23d6389`)
**Origin:** vendored 2026-08-15 (Phase 0 integration)
**Tags:** ['litert-lm', 'inference', 'cartridge']

## 📊 Summary
- **Vendored copy:** shallow HEAD clone, untracked (gitignored)
- **Stack:** C++ on-device LLM orchestration (CMake; LiteRT/TFLite runtime)
- **Node profiles:** inference (SADD §7.1 Inference Node)
- **Entrypoints:** execute, summarize
- **Cartridge:** `cartridges/litert-lm-inference` — signed §8.2/§8.3, cap T1

## 📝 Integration notes (inspected)
- Serves the **OpenAI-compatible protocol** (`litert-lm run --serve`), so the
  Phase-1 router tier (`OPENAI_COMPAT_BASE`, `04_KINETIC/multivoice`) is the
  adapter — no custom inference protocol in Camelot.
- Local-only by construction: cap T1 (no external effects), memory 1024 MB,
  single worker — matches the 8 GB node budget (§7.2).
- Explicitly OUTSIDE the Northstar 16 MB control budget (SADD Appendix B
  boundary: local model adapters are non-control-plane).
- Rollback: `destroy_ephemeral_worktree` (stateless local runtime).

---
**[SIR FORGE]:** "The context is siphoned."
