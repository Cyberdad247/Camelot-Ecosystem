# 🛡️ ASSIMILATION REPORT
**Target:** `02_FORGE/KINETIC_ARMORY/freellmapi` (pinned `f419a89c3`)
**Origin:** vendored 2026-08-15 (assimilation protocol)
**Tags:** ['freellmapi', 'gateway', 'routing', 'zero-cost']

## 📊 Summary
- **Vendored copy:** shallow HEAD clone, untracked (gitignored)
- **Stack:** TypeScript server (`server/src/`), Docker + docker-compose, vitest
- **License:** MIT
- **Role in SADD:** Control-plane transport / zero-cost gateway aggregation (§12 Bifrost; §13.1 rate/spend limits)

## 🔒 Secrets audit (2026-08-15, GHOST squire)
- **No real key values shipped.** `.env`/`.env.local` gitignored; only
  `.env.example` tracked, and it holds placeholders (`ENCRYPTION_KEY=your-64-char-hex-key-here` —
  the code fail-fasts on this literal).
- GHOST's 3 CRITICAL `generic_token` flags are all benign: two README example
  tokens (`freellmapi-your-unified-key`) and one crypto round-trip test fixture
  (`sk-legacy-secret` in `crypto-keyfile.test.ts`).
- Real-format sweep (`sk-`, `AIza`, `ghp_`, `AKIA`, `xox`, private keys,
  `api_key=` assignments): **zero matches**.

## 📝 Integration notes (inspected)
- OpenAI-compatible `/v1` aggregator across 18 free providers / 161 models with
  per-key usage caps and rate-limit failover — a superset of the role the
  Phase-1 `OPENAI_COMPAT_BASE` tier currently assigns to openai-oauth. Point
  `OPENAI_COMPAT_BASE` at freellmapi's `/v1` and the Go router gains the whole
  aggregation fabric with no protocol change.
- **Crypto posture is genuinely sound** (`server/src/lib/crypto.ts`): AES-256-GCM,
  `ENCRYPTION_KEY` length-validated with fail-fast, dev key in a separate
  chmod-0600 `.encryption-key` file — NOT beside ciphertext in the DB. Matches
  the Camelot privacy rule (no key values in source; env-driven).
- Per-key usage tracking implements the SADD §13.1 step-8 spend/rate-limit
  enforcement better than anything in-tree today.
- Compliance note: keys-at-rest encrypted is fine; `ENCRYPTION_KEY` itself must
  come from the secret broker (env), never a committed value.

---
**[SIR FORGE]:** "The context is siphoned."
