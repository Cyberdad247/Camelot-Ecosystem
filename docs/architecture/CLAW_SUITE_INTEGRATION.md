# Claw Suite Integration

Status: `FORGED_GUARDED`

This document records the guarded Camelot interpretation of the Claw Suite
directive. The suite is registered as a control-plane capability manifest, not
as autonomous scraping, commerce, or fraud-enforcement execution.

## Safety Rewrite

The source directive requested bypassing Datadome/Cloudflare and strip-mining
external platforms. Camelot rejects that execution path.

Allowed Openclaw sources are:

- approved public APIs
- merchant-owned data
- licensed datasets
- manual research exports
- robots/terms-compliant page fetches

Blocked capabilities are:

- anti-bot evasion
- Datadome or Cloudflare bypass
- CAPTCHA evasion
- protected-content scraping
- secret value storage
- automatic fraud denial without HUMAN_GATE

## Forged Knights

| Knight | Role | Evidence |
|---|---|---|
| `sir_openclaw` | compliant trend research and source attribution | planned |
| `sir_rustclaw` | Rust image pipeline contract for CMYK, underbase, and AVIF work | planned |
| `sir_hermes` | Shopify Admin plus Storefront GraphQL/Webhook courier | confirmed switchboard surface |
| `lady_nanobot` | Next.js edge component-agent contract for phygital UI | planned |
| `sir_zeroclaw` | zero-trust IP/trademark, affiliate-abuse, and checkout-risk guard | planned |

## Shopify Lanes

`sir_hermes` owns two separate lanes:

- Admin GraphQL API: product/media publication. Required scope: `write_products`.
- Storefront GraphQL API: cart and checkout flow. Entry points include
  `cartCreate` and `Cart.checkoutUrl`.

Secrets remain presence flags only. Tokens must not be written into manifests,
logs, config files, or docs.

## Runtime Surface

Use `//CLAW <objective>` to route the guarded manifest through
`control_plane.runic_router`. The rune queues to `sir_boris` in `ORACLE` mode
and returns metadata with `execution.auto_execute = false`.

Runtime commerce actions, fingerprinting, fraud blocks, product publication, and
external-source ingestion require separate scoped implementation plus the
appropriate HITL gate.
