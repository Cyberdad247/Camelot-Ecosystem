# PWA Cockpit — Deployment Runbook

**Scope.** Production deploy + day-2 operations for the Camelot PWA Cockpit
(`02_FORGE/apps/pwa-cockpit/`). The Cockpit is a Next.js 14 App Router app
deployed to Vercel Edge (`iad1`). Edge runtime applies — see [Edge runtime
caveats](#edge-runtime-caveats) before rotating any secret.

**Operator audience.** On-call engineer with Vercel + LLM provider console
access. Document is self-contained: no need to read the codebase to follow it.

**Source of truth.** The values in this runbook are derived from
[`vercel.json`](./vercel.json), [`src/lib/agents/llm-adapter.ts`](./src/lib/agents/llm-adapter.ts),
[`src/lib/telemetry.ts`](./src/lib/telemetry.ts), and
[`src/lib/security/gate.ts`](./src/lib/security/gate.ts). If a value drifts,
update the runbook in the same commit as the code change.

---

## 1. Required environment variables

All env vars below are declared in `vercel.json` under `env` and are wired to
Vercel encrypted secrets via the `@<name>` syntax. None of them are committed
in plaintext.

| Name | Required? | Consumed by | Behavior if missing in prod |
|---|---|---|---|
| `LLM_PROVIDER` | **Yes** | `src/lib/agents/llm-adapter.ts:createLLMAdapter()` | Defaults to `"stub"`. Stub returns a deterministic final answer. The Phase 8 stub guard throws if `NODE_ENV=production` and this is unset or `"stub"` — deploy will be rejected at the edge. |
| `GEMINI_API_KEY` | Conditional | `src/lib/agents/llm-adapter.ts:GeminiAdapter` | Required only if `LLM_PROVIDER=gemini`. Read at call time. Adapter throws `missing GEMINI_API_KEY` on first use if unset. |
| `OPENAI_API_KEY` | Conditional | `src/lib/agents/llm-adapter.ts:OpenAIAdapter` | Required only if `LLM_PROVIDER=openai`. Same pattern. |
| `ANTHROPIC_API_KEY` | Conditional | `src/lib/agents/llm-adapter.ts:AnthropicAdapter` | Required only if `LLM_PROVIDER=anthropic`. Same pattern. |
| `NEXT_PUBLIC_TELEMETRY_URL` | Recommended | `src/lib/telemetry.ts:init()` | Telemetry events POST here (fire-and-forget). If unset, events stay in the in-memory buffer (read via `GET /api/health` → `telemetry.recent`). The PWA works without it; observability is reduced. |
| `CAMELOT_COCKPIT_TOKEN` | **Yes** | `src/lib/security/gate.ts:isValidBearerToken` (Phase 7) | All `/api/agent/*` requests must carry `Authorization: Bearer <token>`. Middleware rejects with `401` if the format is invalid (regex pre-filter); the route handler does the HMAC verification against this secret. |
| `GEMINI_MODEL` | No | `GeminiAdapter` | Overrides default `gemini-2.0-flash`. |
| `OPENAI_MODEL` | No | `OpenAIAdapter` | Overrides default `gpt-4o-mini`. |
| `ANTHROPIC_MODEL` | No | `AnthropicAdapter` | Overrides default `claude-3-5-haiku-latest`. |
| `AGENTS_A1_BASE_URL` | Conditional | `src/lib/agents/llm-adapter.ts:AgentsA1Adapter` (Phase 9) | Required only if `LLM_PROVIDER=agents_a1`. Points at an OpenAI-compatible HTTP endpoint serving [Agents-A1](https://github.com/Cyberdad247/Agents-A1.git) (a 35B MoE agentic LLM, typically via vLLM or SGLang). Adapter throws `missing AGENTS_A1_BASE_URL` on first use if unset. See [§4 edge runtime caveats](#4-edge-runtime-caveats) — `http://localhost:8000` is unreachable from Vercel Edge; expose the inference server via a public tunnel. |
| `AGENTS_A1_API_KEY` | No | `AgentsA1Adapter` | Often empty for local vLLM. Read at call time; not required. |
| `AGENTS_A1_MODEL` | No | `AgentsA1Adapter` | Overrides default `InternScience/Agents-A1`. |

### 1.1 Pre-deploy checklist

Before running `vercel --prod`, confirm every box:

- [ ] `LLM_PROVIDER` is set to a real provider (`gemini` / `openai` / `anthropic`), **not** `stub`. Stub is for local dev only.
- [ ] The matching `*_API_KEY` env var is set for the chosen provider.
- [ ] `CAMELOT_COCKPIT_TOKEN` is set (≥ 32 chars of base64url). It is the secret the cockpit uses to mint Bearer tokens via the HMAC path in `src/lib/security/hmac.ts`.
- [ ] `NEXT_PUBLIC_TELEMETRY_URL` points at a reachable collector (Vercel log drain endpoint, Datadog, or self-hosted). If you intentionally skip telemetry, set it to empty string and accept the [degraded observability mode](#4-llm-degraded-alert-path).
- [ ] `NODE_ENV=production` is set by Vercel automatically — do not override.

### 1.2 Deploy procedure

```bash
# 1. Link the project (once per machine).
vercel link --yes

# 2. Set encrypted secrets. Vercel prompts for each value; they are
#    stored encrypted and injected as the @<name> refs in vercel.json.
vercel env add LLM_PROVIDER        production
vercel env add GEMINI_API_KEY      production   # or OPENAI_API_KEY / ANTHROPIC_API_KEY
vercel env add CAMELOT_COCKPIT_TOKEN production
vercel env add NEXT_PUBLIC_TELEMETRY_URL production

# 3. Deploy.
vercel --prod

# 4. Verify.
curl -fsS https://<deployment-host>/api/health | jq
curl -fsS -X POST https://<deployment-host>/api/agent/run \
  -H "Authorization: Bearer $CAMELOT_COCKPIT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"agentId":"example","input":"hello"}' | jq
```

`GET /api/health` must return `ok: true` for the `v1_registry` and
`v2_platform` checks. The Phase 8 stub guard ensures the agent route
rejects with a clear error if `LLM_PROVIDER` is still `stub` in prod.

---

## 2. Secrets rotation policy

### 2.1 Cadence

| Secret | Routine rotation | Triggered rotation |
|---|---|---|
| `LLM_PROVIDER` | Not rotated (config, not a secret). | Change via PR + redeploy when switching providers. |
| `GEMINI_API_KEY` / `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | **Every 90 days**. | On suspected compromise, on employee offboarding with access, on provider-side incident disclosure. |
| `CAMELOT_COCKPIT_TOKEN` | **Every 90 days**, aligned with the LLM key. | Same as above. Rotate together so audit trails stay coherent. |
| `NEXT_PUBLIC_TELEMETRY_URL` | Not rotated (URL, not a secret). | Change via PR + redeploy. |

### 2.2 Procedure (LLM provider key)

> **Critical:** because the Cockpit runs on the **edge runtime**, secrets are
> inlined into the bundle at build time. A rotation **requires a redeploy**
> — there is no runtime hot-reload. Plan rotations for a low-traffic window.

1. **Generate the new key** in the provider's console (e.g. Google AI Studio
   for Gemini, platform.openai.com for OpenAI, console.anthropic.com for
   Anthropic). Note the key ID for the audit trail.
2. **Add the new key as a new Vercel env var name** (e.g. `GEMINI_API_KEY_V2`)
   so the old key can stay valid for a brief overlap window. This avoids a
   hard cutover if a long-running request is still in flight on the old key.
3. **Redeploy** to a preview environment first, smoke-test, then promote to
   production: `vercel --prod`.
4. **Update `vercel.json`** to point the `env.GEMINI_API_KEY` ref at the new
   secret. Commit + redeploy.
5. **Wait 24 hours** for the overlap window to drain. Long-running agent
   dispatches cap at the route's `maxDuration` (15s on Vercel Edge), so 24h
   is well over the worst case.
6. **Revoke the old key** in the provider console.
7. **Audit log**: append a row to `SOVEREIGNTY_LEDGER.md` in the repo with
   the key ID, timestamp, operator, and the PR that performed the rotation.
   Do not record the key value itself.

### 2.3 Procedure (`CAMELOT_COCKPIT_TOKEN`)

1. **Generate** a new 32+ char base64url token
   (`openssl rand -base64 48 | tr -d '=+/' | head -c 48`).
2. **Add as `CAMELOT_COCKPIT_TOKEN_V2`** in Vercel, redeploy.
3. **Minting**: the client signs new tokens with the new secret.
4. **Overlap window**: keep the old token valid for 24h so already-issued
   Bearer tokens don't 401 mid-flight.
5. **Drop the old secret** from Vercel after the overlap. Force-redeploy.
6. **Audit log** as above.

### 2.4 Rollback

If a rotation goes wrong:

1. `vercel env rm <NEW_NAME> production` to drop the new secret.
2. `vercel env add <OLD_NAME> production` to re-add the old (if it was
   already removed from Vercel, re-paste it from the password manager).
3. `vercel --prod` to redeploy with the old secret.
4. If the provider-side old key was already revoked, you must generate a
   fresh one and treat the rollback as a new rotation. This is why the
   overlap window is mandatory.

### 2.5 Storage rules

- **Never** commit `.env`, `.env.local`, or any plaintext secret to git.
- **Never** echo a secret in logs. The Cockpit's `src/lib/telemetry.ts`
  explicitly swallows payload errors, but operators should still avoid
  putting secrets in any field that gets serialized.
- **Never** include a secret in a W3C `traceparent` header or in any
  telemetry event. The trace module uses `crypto.getRandomValues` for IDs,
  not secrets.
- Vercel encrypted env refs (`@<name>` in `vercel.json`) are the only
  acceptable production storage.

---

## 3. LLM-degraded alert path

The Cockpit is designed to **degrade gracefully** when the LLM is unhealthy:
the user-facing flow keeps working (rate-limited or stub fallback), but the
degradation must be detected and surfaced to operators within minutes.

### 3.1 What "degraded" means

| Mode | Trigger | User-visible? | Operator action |
|---|---|---|---|
| **Stub fallback** | `LLM_PROVIDER=stub` (or unset) in prod | Yes — agent responses are the deterministic stub text. | **Page on-call.** This means deploy misconfig or fallback was triggered. |
| **LLM 5xx after retry exhaustion** | All retries fail (network, 5xx, 429); Phase 8 retry wrapper exhausts `maxAttempts=3`. | Yes — `/api/agent/run` returns 500 with the last error in `reason`. | **Alert on-call** after 3 such failures in 5 min from a single IP, or after 10 across all IPs. |
| **LLM 4xx (auth)** | Provider rejects the key (401/403) | Yes — first call returns 500. | **Page on-call immediately** — likely rotated/revoked key. |
| **Rate-limited at the provider** | Provider returns 429 on every retry. | Yes — same as 5xx exhaustion, but the `reason` field will be `"rate limited"`. | Warn after 5 such events in 5 min. Check provider quota. |
| **Telemetry endpoint down** | `NEXT_PUBLIC_TELEMETRY_URL` returns 5xx or times out | No — telemetry is fire-and-forget, failures are swallowed. | **Do not alert on this alone.** If telemetry is down for > 1h, run the [recovery procedure](#34-recovery-procedures). |
| **Per-IP rate limit hit** | The Cockpit's own rate limiter (60 req/min/IP) returns 429. | Yes — caller sees 429 with `Retry-After`. | Warn if > 10% of `/api/agent/*` traffic is 429 over 5 min. |
| **vLLM/SGLang server unreachable** (Agents-A1 only) | The operator's local inference host is down, OOM, network-unreachable, or behind a tunnel that's down. | Yes — `/api/agent/run` returns 500. If the env is unset, the adapter throws `missing AGENTS_A1_BASE_URL` (surfaced via the route's `reason` field after Phase 8's retry exhausts). If the env is set but the host is down, the openai SDK throws a fetch error (also surfaced via `reason`). | **Page on-call** after 3 consecutive failures. Unlike managed providers, there is no status page — the operator must inspect the inference host directly (`docker ps`, `nvidia-smi`, `journalctl -u vllm`). |
| **Bearer token rejections** | Invalid/expired/missing `Authorization` header | Yes — 401. | **Page on-call** if > 50 in 5 min (likely credential-stuffing or rotation mishap). |

### 3.2 Detection hooks (already in code)

The Cockpit exposes three signals operators can wire to an alerting system.
No code change is needed to enable them — only the downstream wiring.

1. **`GET /api/health`** (Phase 8, Node runtime). Returns a JSON body with
   per-check `ok` flags:
   - `v1_registry.ok` — cartridge registry reachable
   - `v2_platform.ok` — V2 cartridge platform reachable
   - `version` — current `VERSION` (e.g. `1.0.0-phase8`)
   - `telemetry.recent` — last 20 events from the in-memory buffer

   **Suggested extension (Phase 9 candidate):** add a `v3_llm` check that
   pings the configured LLM provider with a 1-token prompt and reports
   `{ ok, latencyMs, model }`. Document the extension in the `v3_llm` slot
   before depending on it for alerting.

2. **Telemetry events** (`src/lib/telemetry.ts`). Wire
   `NEXT_PUBLIC_TELEMETRY_URL` to a collector (Vercel log drain → Datadog,
   Better Stack, or self-hosted). Filter on:
   - `level=error` and `category=system` → operator errors (Phase 8
     `telemetry.error()` calls land here)
   - `level=warn` and `category=v2` → verify failures
   - High volume of `category=voice` state=`error` → voice pipeline broken

3. **Response headers** (Phase 7). Every `/api/agent/*` response carries
   `traceparent` and `X-RateLimit-*` headers. Log drain can correlate a
   single request across the edge → LLM provider via the W3C trace ID.

### 3.3 Wiring (Datadog example)

```
NEXT_PUBLIC_TELEMETRY_URL = https://http-intake.logs.datadoghq.com/v1/input/<api-key>?ddsource=camelot-cockpit&service=pwa-cockpit&ddtags=env:production
```

Then in Datadog:

- **Monitor A — Stub in prod.** Alert when
  `source:camelot-cockpit "stub" "deterministic"` appears. Indicates
  `LLM_PROVIDER=stub` leaked into prod.
- **Monitor B — LLM error rate.** Count telemetry events with
  `category:system level:error` over 5 min. Page if > 10.
- **Monitor C — 401 storm.** Count 401 responses on `/api/agent/*` over
  5 min. Page if > 50.
- **Monitor D — Rate-limit saturation.** Count 429 responses on
  `/api/agent/*` over 5 min. Warn if ratio > 10% of total.

### 3.4 Recovery procedures

**A. Stub in prod detected.**

1. `vercel env ls production | grep LLM_PROVIDER` — confirm current value.
2. `vercel env add LLM_PROVIDER production` — set to the real provider.
3. `vercel --prod` — redeploy.
4. `curl -fsS https://<host>/api/health` — confirm `version` matches the
   expected build.
5. Send a test dispatch: `curl -fsS -X POST .../api/agent/run -d '{...}'` —
   confirm `ok: true` and a non-stub response.

**B. LLM provider 5xx or 429 storm.**

1. Check the provider's status page (status.openai.com, status.anthropic.com,
   status.cloud.google.com for Gemini).
2. If provider is healthy: check API key validity, then check whether the
   provider quota was hit (`vercel env ls` for the key, then provider
   console).
3. If provider is degraded: consider temporarily setting
   `LLM_PROVIDER=stub` and redeploying to keep the PWA reachable. **Do not
   leave it on stub** — track the restoration as a follow-up and alert
   on-call when the provider recovers.
4. After provider recovery: revert `LLM_PROVIDER`, redeploy, smoke-test.

**C. Suspected key compromise.**

1. Follow [§2.2](#22-procedure-llm-provider-key) with the urgency flag:
   the overlap window can be shortened to 1 hour for compromise.
2. Audit `SOVEREIGNTY_LEDGER.md` for the last legitimate rotation; anything
   since then is a potential misuse window — review provider logs for that
   period.
3. Notify the provider's abuse team if billing or quota anomalies are
   found.

**D. Telemetry collector down.**

1. Telemetry failures are non-blocking; user flows are unaffected. The
   in-memory buffer in `src/lib/telemetry.ts` keeps the last 100 events
   (readable via `/api/health`).
2. Fix the collector endpoint or update `NEXT_PUBLIC_TELEMETRY_URL`.
3. No redeploy needed if only the URL changed and the new endpoint is
   reachable — but if `vercel.json` references it, follow the redeploy
   procedure. (If the URL is set as a plain Vercel env var, an
   `vercel env rm` + `vercel env add` + redeploy is the cleanest path.)

---

## 4. Edge runtime caveats

These are the operational consequences of the Cockpit running on Vercel
Edge (configured via `export const runtime = "edge"` in route handlers and
`export const config = { matcher: ... }` in `middleware.ts`).

1. **Secrets are inlined at build time.** Rotating a secret requires a
   redeploy. There is no `process.env` mutation that takes effect for an
   in-flight request.
2. **Single region.** `vercel.json` pins `regions: ["iad1"]`. For
   multi-region HA, change this to an array and update the rate limiter
   accordingly (the in-memory `Map` in `src/lib/security/rate-limit.ts` is
   per-instance; multi-region requires swapping it for Vercel KV or
   Upstash — the `checkRateLimit()` shape stays the same).
3. **No Node primitives.** Any code in `/api/*` or `middleware.ts` must
   avoid `fs`, `path`, `crypto.createHmac`, etc. Use Web Crypto
   (`crypto.subtle`, `crypto.getRandomValues`). The HMAC path in
   `src/lib/security/hmac.ts` uses Web Crypto for this reason.
4. **15s max function duration.** Configured in `vercel.json` under
   `functions."src/app/api/agent/**/*".maxDuration`. Long agent dispatches
   must respect the route's `budget.maxMs` (default 5000) or fail with
   `reason: "budget exceeded"`. The Phase 8 LLM retry wrapper's backoff
   is bounded so it cannot exceed this on its own, but operators should
   size `budget.maxMs` for the worst-case retry (3 attempts × ~1.5s
   backoff ≈ 4.5s).
5. **Local vLLM unreachable from edge.** The Cockpit runs on Vercel Edge,
   which cannot reach `http://localhost:8000` on the operator's homelab
   box. The Agents-A1 inference server must be exposed via a public
   tunnel (ngrok, Cloudflare Tunnel, Tailscale Funnel) and the tunnel
   URL set as `AGENTS_A1_BASE_URL`. A single tunnel is a single point
   of failure — for HA, run a fleet of vLLM replicas behind a load
   balancer and point `AGENTS_A1_BASE_URL` at the LB.

---

## 5. Related documents

- [`vercel.json`](./vercel.json) — deploy config (regions, env refs, headers).
- [`src/lib/agents/llm-adapter.ts`](./src/lib/agents/llm-adapter.ts) — LLM provider factory, key validation.
- [`src/lib/telemetry.ts`](./src/lib/telemetry.ts) — telemetry hook, in-memory buffer.
- [`src/lib/security/gate.ts`](./src/lib/security/gate.ts) — Bearer token regex (Phase 7 HMAC lives in `hmac.ts`).
- [`src/lib/security/rate-limit.ts`](./src/lib/security/rate-limit.ts) — sliding-window rate limiter.
- [`src/lib/observability/trace.ts`](./src/lib/observability/trace.ts) — W3C `traceparent` parse/generate.
- [`../../PROVENANCE_LEDGER.md`](../../PROVENANCE_LEDGER.md) — append rotation audit rows here.
- [`../../SOVEREIGNTY_LEDGER.md`](../../SOVEREIGNTY_LEDGER.md) — sovereign-level change log.
- Top-level [`../../DEPLOYMENT_GUIDE.md`](../../DEPLOYMENT_GUIDE.md) — broader Camelot ecosystem deploy (not pwa-cockpit-specific).
