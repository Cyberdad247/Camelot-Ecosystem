# CI Guide — Adding a standalone npm project

This guide explains how to wire a new standalone npm project into
[`forge-ci.yml`](../.github/workflows/forge-ci.yml) using the shared
[`npm-install` composite action](../.github/actions/npm-install/action.yml).

A **standalone npm project** is a directory under `02_FORGE/` that has its own
`package.json` and is managed with plain `npm install` / `npm run build` — it is
**not** part of the pnpm workspace.

---

## 3-step checklist

| Step | What to do | Where |
|------|------------|-------|
| 1 | Add a change-detection filter | `changes` job → `dorny/paths-filter` → `filters` |
| 2 | Add the build job | New job at the bottom of `forge-ci.yml` |
| 3 | Add the required status check | `.github/settings.yml` |

---

## Step 1 — Change-detection filter

In the `changes` job, add two entries.

### 1a — Declare the output

Under `jobs.changes.outputs`, add a key for your project:

```yaml
my-new-app: ${{ steps.filter.outputs.my-new-app }}
```

### 1b — Define the filter pattern

Under `dorny/paths-filter` → `with.filters`, add:

```yaml
my-new-app:
  - '02_FORGE/apps/my-new-app/**'
```

### Important — exclude from workspace-lint

If your standalone project lives under `02_FORGE/apps/`, add an exclusion to the
existing `workspace-lint` filter so it doesn't trigger the pnpm/Turborepo jobs:

```yaml
workspace-lint:
  - '02_FORGE/apps/**'
  - '!02_FORGE/apps/my-new-app/**'   # ← add this line
  - '02_FORGE/packages/**'
  # ... rest unchanged
```

If your project is not under `apps/` (e.g. `02_FORGE/dyad-apps/` or
`02_FORGE/PORTAL_CORE/`), this exclusion is not needed.

---

## Step 2 — Build job (standard case)

Copy this template and replace the four placeholders:

```yaml
  # ── My New App: Build ──────────────────────────────────────────
  my-new-app-build:
    name: My New App Build
    needs: changes
    if: needs.changes.outputs.my-new-app == 'true' || github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: ./.github/actions/npm-install
        with:
          working-directory: 02_FORGE/apps/my-new-app
          package-json-path: 02_FORGE/apps/my-new-app/package.json
          cache-key-prefix: my-new-app
          node-version: ${{ env.NODE_VERSION }}
```

### What the npm-install action does

| Step | Effect |
|------|--------|
| `setup-node` | Installs the Node.js version from the workflow's `NODE_VERSION` env |
| Cache | Caches `~/.npm` + `node_modules/` keyed on the project's `package.json` |
| `npm install` | Installs dependencies |
| Build (`npm run build`) | Runs the project's `build` script (default; see below) |

That's it — the action handles **setup → cache → install → build** in one
`uses:` call.

### Input reference

| Input | Required | Default | Notes |
|-------|----------|---------|-------|
| `working-directory` | yes | — | Path to the npm project (relative to repo root) |
| `package-json-path` | yes | — | **Literal** path for cache hashing (no expressions!) |
| `cache-key-prefix` | yes | — | Unique short name for the cache namespace |
| `node-version` | no | `'20'` | Node.js version |
| `build-command` | no | `'npm run build'` | Pass `''` to skip, or a custom command (e.g. `npm run build:prod`) |

---

## Step 2b — Custom build pipeline

If your project needs extra steps before or instead of the standard build (e.g.
Prisma client generation, a different build tool, or multi-step build), set
`build-command: ''` to skip the action's build and add your own steps:

```yaml
  # ── My App: Custom Build ────────────────────────────────────────
  my-app-build:
    name: My App Build
    needs: changes
    if: needs.changes.outputs.my-app == 'true' || github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: ./.github/actions/npm-install
        with:
          working-directory: 02_FORGE/dyad-apps/my-app
          package-json-path: 02_FORGE/dyad-apps/my-app/package.json
          cache-key-prefix: my-app
          node-version: ${{ env.NODE_VERSION }}
          build-command: ''

      - name: Generate Prisma client
        working-directory: 02_FORGE/dyad-apps/my-app
        run: npx prisma generate

      - name: Build My App
        working-directory: 02_FORGE/dyad-apps/my-app
        run: npx next build
```

This is the pattern used by `invoice-generator-build` in the live workflow.

---

## Step 3 — Required status check

Add the job's display name to `.github/settings.yml` under
`required_status_checks`:

```yaml
required_status_checks:
  strict: false
  contexts:
    # ... existing entries ...
    - "My New App Build"
```

---

## Quick reference — existing standalone npm jobs

| Job | Directory | Build type |
|-----|-----------|------------|
| `holotable-build` | `02_FORGE/holotable` | Standard (`npm run build`) |
| `portal-core-build` | `02_FORGE/PORTAL_CORE` | Standard (`npm run build`) |
| `i2l-phygital-build` | `02_FORGE/apps/i2l-phygital` | Standard (`npm run build`) |
| `invoice-generator-build` | `02_FORGE/dyad-apps/invoice-generator` | Custom (`build-command: ''` + Prisma + Next) |

---

## Project requirements

Your standalone npm project needs at minimum:

- A `package.json` with a `"build"` script (or use a custom `build-command`)
- All dependencies installed via `npm install` (not pnpm/yarn)

If your project is a Next.js + TypeScript app, it should also include:

- `tsconfig.json` — standard Next.js TS config
- `next.config.js` — at minimum `reactStrictMode: true`
- `postcss.config.mjs` — if using Tailwind
- An `app/layout.tsx` — root layout (even a minimal one)
- An `app/page.tsx` — at least one page so the build succeeds
