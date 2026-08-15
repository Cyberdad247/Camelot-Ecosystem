# freellmapi — Deployment Guide

**Vendored copy:** `02_FORGE/KINETIC_ARMORY/freellmapi` (pinned `f419a89c3`, shallow/untracked)
**Cartridge:** `cartridges/freellmapi-gateway/manifest.json` (signed §8.2/§8.3, cap T1, `customer-controlled`)
**Router tier:** `04_KINETIC/multivoice` — the local OpenAI-compatible tier (`OPENAI_COMPAT_BASE`)

freellmapi aggregates 18 free LLM providers / 161 models behind one
OpenAI-compatible `/v1` endpoint with per-key usage caps and rate-limit
failover. It is the **recommended upstream** for the multivoice local tier:
point `OPENAI_COMPAT_BASE` at it and the router gains the whole aggregation
fabric with no protocol change.

## 1. Deploy (Docker, loopback-only)

```bash
cd 02_FORGE/KINETIC_ARMORY/freellmapi
cp .env.example .env      # then fill in provider keys you want to use
docker compose up -d      # binds 127.0.0.1:3001 by default
```

- The image is `ghcr.io/tashfeenahmed/freellmapi:latest`.
- **Must stay loopback-bound** (`HOST_BIND=127.0.0.1`, the default). The
  upstream README is explicit: single-user, not internet-exposed. `HOST_BIND`
  to LAN only behind the Camelot Bifrost mTLS boundary, never raw.
- `ENCRYPTION_KEY` comes from `.env` — a 64-hex-char key (32 bytes). Generate:
  `node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"`.
  Never commit it (per Camelot privacy rule, key values live in the secret
  broker / env only; `.env` is gitignored upstream).

## 2. Verify it is up

```bash
curl -fsS http://127.0.0.1:3001/api/ping            # app healthcheck endpoint
curl -fsS http://127.0.0.1:3001/v1/models | head    # OpenAI-compatible liveness probe
```

The multivoice tier probes `GET <base>/models` — the second command must
succeed for the router to pick freellmapi up.

## 3. Wire the router

```bash
# multivoice (04_KINETIC/multivoice)
OPENAI_COMPAT_BASE=http://127.0.0.1:3001/v1
OPENAI_COMPAT_KEY=local        # loopback credential; freellmapi uses its own auth
```

Start order / failure modes:

1. **CLIProxy gateway up** → router uses `CLIPROXY_BASE` (unchanged behavior).
2. **CLIProxy down, freellmapi up** → router degrades to
   `OPENAI_COMPAT_BASE` automatically (probe `/models`).
3. **Both down** → TinyLM stubs. `CAMELOT_REQUIRE_GATEWAY=1` fails closed at
   step 1 regardless.

## 4. Trust posture

- The cartridge is `customer-controlled` signer band, cap **T1**, `network.scoped`
  + `secret.handle_request` only — freellmapi holds your free-tier provider keys
  encrypted at rest (AES-256-GCM), and never exports them (`secret.export`
  denied).
- Rollback is `compensating_action` → `rotate_keys`: on compromise, rotate the
  provider keys through the dashboard and re-issue the cartridge lease.
- It is transport, not authority — per §12 Bifrost rule it authenticates and
  routes; it never issues leases.

## 5. References

- `docs/architecture/integrations.md` — constellation map, row 12.
- `Nano-Knights/ASSIMILATIONREPORT_freellmapi.md` — assimilation report.
- `04_KINETIC/multivoice/README.md` — local OpenAI-compatible tier docs.
