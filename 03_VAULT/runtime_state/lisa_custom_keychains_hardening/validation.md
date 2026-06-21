# Lisa Custom Keychains Production Validation

> **Validator:** Sir Codex

**Purpose:** Prove that the hardening work fixed the actual problems. A checkbox
is marked PASS only when the listed command and expected result agree.

**Repository:** `C:\tmp\LisaCustomKeychains.com-audit`

**Release rule:** Any failed P0 gate means `BLOCKED`. Do not deploy or promote.

---

## Evidence Header

Fill these values from command output. Do not type secrets.

```text
Validation date:
Validator:
Branch:
Commit:
Node version:
npm version:
Deployment URL:
```

## V0 - Source and Secret Safety

```powershell
Set-Location C:\tmp\LisaCustomKeychains.com-audit
git status --short --branch
git rev-parse HEAD
node --version
npm --version
git diff --check
git diff --cached --check
```

Run the local privacy scanner from Camelot without auto-approving a HITL prompt:

```powershell
Set-Location C:\Users\vizio\CAMELOT_OS
.\.venv\Scripts\python.exe -m squires.colony ghost C:\tmp\LisaCustomKeychains.com-audit
```

**PASS when:**

- [ ] The expected hardening branch and commit are shown.
- [ ] Both diff checks exit `0`.
- [ ] The privacy scan finds no committed credentials.
- [ ] No HUMAN_GATE prompt was auto-approved.

## V1 - Owner Authentication Unit Gate

```powershell
Set-Location C:\tmp\LisaCustomKeychains.com-audit
cmd /c npm test -- src/lib/owner-auth.test.ts
```

**PASS when:**

- [ ] Missing owner cookie is rejected.
- [ ] Invalid owner cookie is rejected.
- [ ] Valid owner session is accepted.
- [ ] The test command exits `0`.

## V2 - Content Queue Runtime Gate

Start the production build:

```powershell
Set-Location C:\tmp\LisaCustomKeychains.com-audit
cmd /c npm run build
$env:PORT="3417"
cmd /c npm start
```

In a second PowerShell window:

```powershell
$base = "http://127.0.0.1:3417"

try {
  Invoke-WebRequest "$base/api/content-queue" -UseBasicParsing
} catch {
  [int]$_.Exception.Response.StatusCode
}

try {
  Invoke-WebRequest "$base/api/content-queue" `
    -Method Patch `
    -ContentType "application/json" `
    -Body '{"id":"missing","status":"approved"}' `
    -UseBasicParsing
} catch {
  [int]$_.Exception.Response.StatusCode
}
```

**PASS when:**

- [ ] Anonymous `GET` returns `401`.
- [ ] Anonymous `PATCH` returns `401`.
- [ ] No queue content appears in either response.
- [ ] `src/app/api/content-queue/route.test.ts` passes.

## V3 - Design AI Process Gate

```powershell
$base = "http://127.0.0.1:3417"

try {
  Invoke-WebRequest "$base/api/design-ai" `
    -Method Post `
    -ContentType "application/json" `
    -Body '{}' `
    -UseBasicParsing
} catch {
  [int]$_.Exception.Response.StatusCode
}

Set-Location C:\tmp\LisaCustomKeychains.com-audit
cmd /c npm test -- src/app/api/design-ai/route.test.ts
```

**PASS when:**

- [ ] Anonymous `POST` returns `401`.
- [ ] The anonymous test proves the child-process function was not called.
- [ ] The timeout test proves the child is killed at 8 seconds.
- [ ] Timeout returns `504`.
- [ ] Process failure returns controlled JSON without a stack trace.

## V4 - Durable Storage Gate

```powershell
Set-Location C:\tmp\LisaCustomKeychains.com-audit
cmd /c npm test -- src/lib/content-repository.test.ts
rg -n "writeFile|writeFileSync|mkdir|mkdirSync" src
rg -n "SUPABASE_SERVICE_ROLE_KEY" src
```

**PASS when:**

- [ ] Repository tests create, read, update, and delete each editable record type.
- [ ] A new repository instance can read data written by the previous instance.
- [ ] Upload tests return a durable object URL.
- [ ] No production editor route writes into `public`, `data`, or the deployment root.
- [ ] `SUPABASE_SERVICE_ROLE_KEY` appears only in server-only modules.
- [ ] Supabase row-level security is enabled and anonymous writes are denied.

## V5 - Stored XSS Gate

```powershell
Set-Location C:\tmp\LisaCustomKeychains.com-audit
cmd /c npm test -- "src/app/blog/[slug]/page.test.tsx"
```

Required malicious fixtures:

```text
<script>alert(1)</script>
<img src=x onerror=alert(1)>
[bad](javascript:alert(1))
[data](data:text/html,<script>alert(1)</script>)
[good](https://example.com/product)
```

**PASS when:**

- [ ] No fixture creates a script element or executable event handler.
- [ ] `javascript:` and `data:` links become `#` or plain text.
- [ ] The HTTPS link remains usable.
- [ ] External affiliate links include `noopener`, `noreferrer`, and `sponsored`.

## V6 - Lint and CI Gate

```powershell
Set-Location C:\tmp\LisaCustomKeychains.com-audit
cmd /c npm run lint
Get-Content .github\workflows\production.yml
```

**PASS when:**

- [ ] Lint exits `0` with zero warnings.
- [ ] `package.json` does not call `next lint`.
- [ ] `eslint.config.mjs` exists.
- [ ] CI runs install, lint, tests, production audit, and build.
- [ ] Deployment has `needs: verify`.
- [ ] Workflow permissions are limited to `contents: read`.
- [ ] Workflow contains secret names but no secret values.

## V7 - Dependency Security Gate

```powershell
Set-Location C:\tmp\LisaCustomKeychains.com-audit
cmd /c npm ls axios form-data ws @supabase/supabase-js
cmd /c npm audit --omit=dev --audit-level=high
```

**PASS when:**

- [ ] `axios` is absent unless an application import proves it is required.
- [ ] Direct `form-data` is absent unless an application import proves it is required.
- [ ] The resolved `ws` version is not affected by
  `GHSA-58qx-3vcg-4xpx` or `GHSA-96hv-2xvq-fx4p`.
- [ ] The production audit exits `0`.
- [ ] No high or critical production advisory remains.

## V8 - P1 Security Gate

```powershell
Set-Location C:\tmp\LisaCustomKeychains.com-audit
cmd /c npm test
```

**PASS when:**

- [ ] Anonymous blog listing contains published posts only.
- [ ] Draft listing requires an owner session.
- [ ] Two Meta OAuth starts produce different state values.
- [ ] Meta OAuth callback rejects missing or mismatched state.
- [ ] OAuth state cookie is HttpOnly, Secure in production, and SameSite=Lax.
- [ ] Missing `CRON_SECRET` returns `503`.
- [ ] Wrong cron authorization returns `401`.
- [ ] `.env.example` never suggests an Admin `shpat_` token for `NEXT_PUBLIC_*`.

## V9 - Full Local Quality Gate

Run from a clean dependency install:

```powershell
Set-Location C:\tmp\LisaCustomKeychains.com-audit
cmd /c npm ci
cmd /c npm run lint
cmd /c npm test
cmd /c npm audit --omit=dev --audit-level=high
cmd /c npm run build
```

**PASS when:**

- [ ] Clean install exits `0`.
- [ ] Lint exits `0`.
- [ ] Every test passes.
- [ ] Production dependency audit exits `0`.
- [ ] Production build exits `0`.
- [ ] Build output contains no missing-required-environment warning.

## V10 - Container Gate

```powershell
Set-Location C:\tmp\LisaCustomKeychains.com-audit
docker build -t lisa-keychains:release .
docker run -d --rm `
  --name lisa-keychains-validation `
  --read-only `
  --tmpfs /tmp:rw,noexec,nosuid,size=64m `
  -p 3418:3000 `
  --env-file .env.local `
  lisa-keychains:release
docker inspect lisa-keychains-validation --format "{{.Config.User}}"
Invoke-WebRequest http://127.0.0.1:3418 -UseBasicParsing
docker logs lisa-keychains-validation
docker stop lisa-keychains-validation
```

Optional gVisor host validation:

```powershell
docker run --rm `
  --runtime=runsc `
  --read-only `
  --tmpfs /tmp:rw,noexec,nosuid,size=64m `
  -p 3418:3000 `
  --env-file .env.local `
  lisa-keychains:release
```

**PASS when:**

- [ ] Image builds.
- [ ] Container user is non-root.
- [ ] Root filesystem is read-only.
- [ ] Homepage returns HTTP `200`.
- [ ] Logs contain no unhandled startup error.
- [ ] gVisor starts successfully when `runsc` is installed on the host.

## V11 - Vercel Preview Gate

```powershell
Set-Location C:\tmp\LisaCustomKeychains.com-audit
cmd /c vercel pull --yes --environment=preview
cmd /c vercel build
cmd /c vercel deploy --prebuilt
```

Copy the deployment URL printed by the final command into `$previewUrl`:

```powershell
$previewUrl = Read-Host "Preview deployment URL"

try {
  Invoke-WebRequest "$previewUrl/api/content-queue" -UseBasicParsing
} catch {
  [int]$_.Exception.Response.StatusCode
}

try {
  Invoke-WebRequest "$previewUrl/api/design-ai" `
    -Method Post `
    -ContentType "application/json" `
    -Body '{}' `
    -UseBasicParsing
} catch {
  [int]$_.Exception.Response.StatusCode
}
```

**PASS when:**

- [ ] Preview deployment succeeds.
- [ ] Storefront homepage is reachable through the configured preview protection.
- [ ] Anonymous content queue request returns `401`.
- [ ] Anonymous design AI request returns `401`.
- [ ] Preview logs show no unhandled application errors.

## V12 - Production Release Gate

Run only after V0 through V11 pass:

```powershell
Set-Location C:\tmp\LisaCustomKeychains.com-audit
$releaseCommit = git rev-parse HEAD
cmd /c vercel pull --yes --environment=production
cmd /c vercel build --prod
cmd /c vercel deploy --prebuilt --prod
Write-Output "Validated release commit: $releaseCommit"
cmd /c vercel inspect --logs
```

Copy the production URL printed by Vercel into `$productionUrl`:

```powershell
$productionUrl = Read-Host "Production deployment URL"
Invoke-WebRequest $productionUrl -UseBasicParsing

try {
  Invoke-WebRequest "$productionUrl/api/content-queue" -UseBasicParsing
} catch {
  [int]$_.Exception.Response.StatusCode
}

try {
  Invoke-WebRequest "$productionUrl/api/design-ai" `
    -Method Post `
    -ContentType "application/json" `
    -Body '{}' `
    -UseBasicParsing
} catch {
  [int]$_.Exception.Response.StatusCode
}
```

**PASS when:**

- [ ] Production homepage returns `200`.
- [ ] Anonymous content queue request returns `401`.
- [ ] Anonymous design AI request returns `401`.
- [ ] Deployed commit equals the validated release commit.
- [ ] Recent production logs contain no unhandled error.
- [ ] The owner can sign in and complete one authorized editor read and write.
- [ ] The written record remains present after a fresh request and deployment restart.

## Final Decision

Mark exactly one:

- [ ] `PASS - PRODUCTION READY`
- [ ] `BLOCKED - P0 VALIDATION FAILED`

Record failures:

```text
Gate:
Command:
Observed result:
Expected result:
Owner:
Next action:
```

## Release Evidence

```text
Validated commit:
GitHub Actions run:
Vercel deployment:
Tests passed:
Production advisories:
Anonymous content queue status:
Anonymous design AI status:
Durable write proof:
Production log result:
Final decision:
```
