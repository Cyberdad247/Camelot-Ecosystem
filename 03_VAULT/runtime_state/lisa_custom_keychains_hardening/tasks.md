# Lisa Custom Keychains Production Hardening Tasks

> **For Sir Codex:** Execute tasks in order. Use test-driven changes, keep each
> commit focused, and stop deployment when any P0 validation gate fails.

**Goal:** Close every release-blocking security and reliability problem found in
the June 17, 2026 production audit.

**Repository:** `C:\tmp\LisaCustomKeychains.com-audit`

**Starting commit:** `788b8a2`

**Source audit:** `C:\Users\vizio\CAMELOT_OS\03_VAULT\runtime_state\LISA_CUSTOM_KEYCHAINS_PRODUCTION_AUDIT_2026-06-17.json`

**Release rule:** All P0 tasks and validations must pass before production
deployment. P1 tasks should be completed before normal public operation.

---

## Sir Codex Execution Rules

- [ ] Work on branch `hardening/presentation-p0`.
- [ ] Never place real secrets in source files, command history, test fixtures,
  screenshots, or logs.
- [ ] Use environment variable names only. Store real values in Vercel or GitHub
  secret storage.
- [ ] Add a failing test before changing security behavior.
- [ ] Run the matching section in `validation.md` after every task.
- [ ] Commit only after the task's validation gate passes.
- [ ] Do not deploy when lint, tests, dependency audit, build, or runtime probes fail.

## Task DAG

```text
T0
|-- T1 owner authentication
|   |-- T2 content queue protection
|   `-- T3 design AI protection
|-- T4 durable data storage
|-- T5 blog output safety
|-- T6 lint and CI
`-- T7 dependency repair

T1 + T2 + T3 + T4 + T5 + T6 + T7
`-- T8 P1 hardening
    `-- T9 container and deployment
        `-- T10 production verification
```

## T0 - Prepare the Branch

**Priority:** P0

- [ ] Open the audited checkout.
- [ ] Confirm the checkout is clean and still points at commit `788b8a2`.
- [ ] Create the hardening branch.
- [ ] Install exactly what the lockfile specifies.

```powershell
Set-Location C:\tmp\LisaCustomKeychains.com-audit
git status --short --branch
git rev-parse --short HEAD
git checkout -b hardening/presentation-p0
cmd /c npm ci
```

**Pass when:** Git reports branch `hardening/presentation-p0`, commit `788b8a2`,
and `npm ci` exits with code `0`.

## T1 - Add One Reusable Owner-Authentication Gate

**Priority:** P0

**Files:**

- Create: `src/lib/owner-auth.ts`
- Create: `src/lib/owner-auth.test.ts`
- Reuse: `isOwnerSessionValid` from `src/lib/storefront-config.ts`

- [ ] Add tests proving a missing or invalid owner cookie is rejected.
- [ ] Add `requireOwnerSession()` that reads `lisa_owner_session` using
  `cookies()` and validates it through the existing session validator.
- [ ] Return a shared unauthorized response with HTTP `401`.
- [ ] Run the focused test and commit.

```powershell
cmd /c npm test -- src/lib/owner-auth.test.ts
git add src/lib/owner-auth.ts src/lib/owner-auth.test.ts
git commit -m "security: add reusable owner session gate"
```

**Pass when:** The focused test passes and no password or session secret appears
in the committed diff.

## T2 - Lock the Content Queue

**Priority:** P0

**Files:**

- Modify: `src/app/api/content-queue/route.ts`
- Create: `src/app/api/content-queue/route.test.ts`

- [ ] Write tests proving anonymous `GET` and `PATCH` requests return `401`.
- [ ] Require the owner session at the beginning of both handlers.
- [ ] Validate `PATCH` JSON with Zod:
  - `id`: non-empty string
  - `status`: `pending`, `approved`, or `rejected`
  - `body`: optional string, maximum 5,000 characters
- [ ] Return `400` for malformed JSON or invalid fields.
- [ ] Keep the current not-found behavior for valid but unknown IDs.
- [ ] Run the focused tests and commit.

```powershell
cmd /c npm test -- src/app/api/content-queue/route.test.ts
git add src/app/api/content-queue/route.ts src/app/api/content-queue/route.test.ts
git commit -m "security: protect content queue routes"
```

**Pass when:** Anonymous requests cannot read or mutate the queue, and malformed
authenticated requests cannot reach the write path.

## T3 - Lock and Bound the Design AI Process

**Priority:** P0

**Files:**

- Modify: `src/app/api/design-ai/route.ts`
- Create: `src/app/api/design-ai/route.test.ts`

- [ ] Write a test proving an anonymous request returns `401` without spawning a
  child process.
- [ ] Require owner authentication before reading the request body.
- [ ] Validate request size and expected fields before process creation.
- [ ] Add an 8-second timer that kills the child process.
- [ ] Clear the timer on both `close` and `error`.
- [ ] Return `504` for timeout and a controlled `500` response for process failure.
- [ ] Configure a Vercel Firewall rate limit for this route before public release.
- [ ] Run the focused tests and commit.

```powershell
cmd /c npm test -- src/app/api/design-ai/route.test.ts
git add src/app/api/design-ai/route.ts src/app/api/design-ai/route.test.ts
git commit -m "security: protect and bound design ai execution"
```

**Pass when:** Anonymous traffic never starts Python, authorized execution cannot
run longer than 8 seconds, and repeated requests are rate-limited at the edge.

## T4 - Move Editable Data Out of the Deployment Filesystem

**Priority:** P0

**Files:**

- Modify: `src/lib/storefront-config.ts`
- Modify: `src/app/api/blog/route.ts`
- Modify: `src/app/api/social/route.ts`
- Modify: `src/lib/calendar.server.ts`
- Create: `src/lib/content-repository.ts`
- Create: `src/lib/content-repository.test.ts`
- Create: `supabase/migrations/20260617_content_storage.sql`

- [ ] Define one repository interface for storefront settings, blog posts, social
  posts, calendar events, and content queue records.
- [ ] Create Supabase tables with row-level security enabled.
- [ ] Deny anonymous writes in database policies.
- [ ] Use the server-only `SUPABASE_SERVICE_ROLE_KEY` only inside server modules.
- [ ] Move uploaded images to Supabase Storage or Vercel Blob.
- [ ] Replace all runtime `writeFile`, `mkdir`, and public-folder upload writes
  with repository or object-storage calls.
- [ ] Add tests proving writes survive repository re-instantiation and storage
  errors return controlled responses.
- [ ] Run focused tests and commit.

```powershell
cmd /c npm test -- src/lib/content-repository.test.ts
rg -n "writeFile|writeFileSync|mkdir|mkdirSync" src
git add src/lib/content-repository.ts src/lib/content-repository.test.ts src/lib/storefront-config.ts src/app/api/blog/route.ts src/app/api/social/route.ts src/lib/calendar.server.ts supabase/migrations/20260617_content_storage.sql
git commit -m "fix: persist editor content in durable storage"
```

**Pass when:** Editable production data is not written to the Vercel deployment
filesystem and the secret service-role key is never imported into client code.

## T5 - Prevent Stored Blog Script Injection

**Priority:** P0

**Files:**

- Modify: `src/app/blog/[slug]/page.tsx`
- Create: `src/app/blog/[slug]/page.test.tsx`

- [ ] Add tests using `<script>`, event-handler attributes, `javascript:` links,
  malformed URLs, and valid HTTPS links.
- [ ] Escape raw HTML before markdown conversion.
- [ ] Allow affiliate links only when their protocol is `http:` or `https:`.
- [ ] Add `rel="noopener noreferrer sponsored"` to external affiliate links.
- [ ] Confirm normal headings, paragraphs, and links still render.
- [ ] Run the focused tests and commit.

```powershell
cmd /c npm test -- "src/app/blog/[slug]/page.test.tsx"
git add "src/app/blog/[slug]/page.tsx" "src/app/blog/[slug]/page.test.tsx"
git commit -m "security: sanitize rendered blog content"
```

**Pass when:** Script text is displayed as harmless text, unsafe links resolve to
`#`, and valid HTTPS links still work.

## T6 - Restore Lint and Add the Release Gate

**Priority:** P0

**Files:**

- Modify: `package.json`
- Remove after migration: `.eslintrc.json`
- Create: `eslint.config.mjs`
- Create: `.github/workflows/production.yml`

- [ ] Replace `next lint` with `eslint . --max-warnings=0`.
- [ ] Add an ESLint 9 flat configuration for Next.js core web vitals and TypeScript.
- [ ] Make the workflow run `npm ci`, lint, tests, production audit, and build.
- [ ] Make production deployment depend on the verification job.
- [ ] Grant GitHub Actions only `contents: read`.
- [ ] Store `VERCEL_TOKEN`, `VERCEL_ORG_ID`, and `VERCEL_PROJECT_ID` as GitHub
  Actions secrets, never as YAML values.
- [ ] Run lint locally and commit.

```powershell
cmd /c npm run lint
git add package.json package-lock.json eslint.config.mjs .github/workflows/production.yml
git rm .eslintrc.json
git commit -m "ci: restore lint and gate production deployment"
```

**Pass when:** Lint exits `0`, the workflow has a verify-before-deploy dependency,
and no secret values exist in the workflow.

## T7 - Remove or Upgrade Vulnerable Production Packages

**Priority:** P0

**Files:**

- Modify: `package.json`
- Modify: `package-lock.json`

- [ ] Confirm `axios` and direct `form-data` imports are absent from application code.
- [ ] Remove unused direct dependencies.
- [ ] Update `@supabase/supabase-js` to a release whose dependency tree contains a
  fixed `ws` version.
- [ ] Regenerate the lockfile through npm.
- [ ] Run the production dependency audit.
- [ ] Run all tests and build, then commit.

```powershell
rg -n "axios|form-data" src
cmd /c npm uninstall axios form-data
cmd /c npm update @supabase/supabase-js
cmd /c npm audit --omit=dev --audit-level=high
cmd /c npm test
cmd /c npm run build
git add package.json package-lock.json
git commit -m "security: remove vulnerable production dependencies"
```

**Pass when:** `npm audit --omit=dev --audit-level=high` exits `0`, all tests
pass, and the production build succeeds.

## T8 - Complete P1 Security Hardening

**Priority:** P1

**Audit IDs:** `P1-SEC-007`, `P1-OAUTH-008`, `P1-CRON-009`, `P1-ENV-010`

**Files:**

- Modify: `src/app/api/blog/route.ts`
- Modify: `src/app/api/auth/meta/start/route.ts`
- Modify the matching Meta OAuth callback route
- Modify: `src/app/api/cron/generate-content/route.ts`
- Modify: `.env.example`
- Add focused tests beside each changed route

- [ ] Return only published blog posts to anonymous callers.
- [ ] Require owner authentication to list or edit drafts.
- [ ] Generate Meta OAuth `state` with cryptographically secure randomness.
- [ ] Store OAuth state in an HttpOnly, Secure, SameSite=Lax cookie.
- [ ] Reject the callback when cookie state and query state do not match.
- [ ] Make the cron route return `503` when `CRON_SECRET` is absent and `401`
  when authorization is wrong.
- [ ] Change the public Shopify token example so it clearly says Storefront API
  token and never suggests an Admin `shpat_` token.
- [ ] Run focused tests and commit.

```powershell
cmd /c npm test
git add src/app/api/blog src/app/api/auth/meta src/app/api/cron/generate-content .env.example
git commit -m "security: close secondary authentication gaps"
```

**Pass when:** Drafts are private, OAuth state is one-time and verified, cron
fails closed, and `.env.example` cannot be mistaken for an Admin-token guide.

## T9 - Add a Reproducible Production Container

**Priority:** P1

**Files:**

- Modify: `next.config.*`
- Create: `Dockerfile`
- Create: `.dockerignore`

- [ ] Enable Next.js standalone output.
- [ ] Use a multi-stage Node 24 build.
- [ ] Run the final image as a non-root user.
- [ ] Keep the runtime filesystem read-only except for a small `/tmp` mount.
- [ ] Do not copy `.env*`, `.git`, test output, or local audit files into the image.
- [ ] Build and run the image locally.
- [ ] Commit the container files.

```powershell
docker build -t lisa-keychains:release .
docker run --rm --name lisa-keychains-validation --read-only --tmpfs /tmp:rw,noexec,nosuid,size=64m -p 3417:3000 --env-file .env.local lisa-keychains:release
```

In a second PowerShell window:

```powershell
Invoke-WebRequest http://127.0.0.1:3417 -UseBasicParsing
docker stop lisa-keychains-validation
```

**Pass when:** The image builds, starts as non-root, and the homepage returns
HTTP `200` while the container root filesystem is read-only.

## T10 - Final Release and Production Proof

**Priority:** P0 release gate

- [ ] Run every command in `validation.md`.
- [ ] Confirm all P0 rows are marked PASS.
- [ ] Pull the linked Vercel production configuration.
- [ ] Build the Vercel production artifact.
- [ ] Deploy only after the local and CI gates pass.
- [ ] Probe the production routes and inspect recent error logs.
- [ ] Record the deployment URL, Git commit, test totals, audit totals, and probe
  results in the validation evidence section.

```powershell
cmd /c vercel pull --yes --environment=production
cmd /c vercel build --prod
cmd /c vercel deploy --prebuilt --prod
cmd /c vercel inspect --logs
```

**Pass when:** The deployed commit matches the validated commit, anonymous
security probes return the expected denial codes, the storefront is reachable,
and recent production logs contain no unhandled application errors.

## Definition of Done

- [ ] P0-AUTH-001 closed.
- [ ] P0-DOS-002 closed.
- [ ] P0-DATA-003 closed.
- [ ] P0-XSS-004 closed.
- [ ] P0-CI-005 closed.
- [ ] P0-DEPS-006 closed.
- [ ] All tests, lint, audit, build, container, CI, and production probes pass.
- [ ] No real secret was committed or printed.
- [ ] `validation.md` contains reproducible evidence for the released commit.
