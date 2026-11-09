import { existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import type { Plugin } from 'vite';
import { defineConfig } from 'vitest/config';

const rootDir = fileURLToPath(new URL('.', import.meta.url));

// The shared voice runtime lives in the separate 02_FORGE pnpm workspace, which
// the root npm `workspaces` globs (`apps/*`, `packages/*`) do not cover, so it
// resolves by path rather than through node_modules. Mirrors the alias in
// apps/pwa/vitest.config.ts.
const voiceFirstRuntime = path.join(rootDir, '02_FORGE/packages/voice-first-runtime/src/index.ts');

// `@/…` means "this app's own src" (every app's tsconfig maps `@/* -> ./src/*`),
// so the target depends on WHO is importing. A plain Vite alias cannot express
// that: it matches only the specifier, never the importer, so pointing `@/` at
// one app would make every other app's `@/…` imports silently load that app's
// files — a green test running against the wrong module. Resolving per importer
// keeps each app honest (today pwa and invisioned-marketing both use `@/`).
function appScopedSrcAlias(): Plugin {
  return {
    name: 'camelot-app-scoped-src',
    enforce: 'pre',
    resolveId(id, importer) {
      if (!id.startsWith('@/') || !importer) return null;
      const app = importer.replace(/\\/g, '/').match(/\/apps\/([^/]+)\//)?.[1];
      if (!app) return null;
      // Probe the extensions ourselves and return a forward-slash absolute path:
      // handing a backslash path back to Vite's resolver drops the Windows drive
      // letter and yields `/apps/…`, which then fails to load.
      // `@/*` maps to `./src/*` in every app, so the `src` segment is required.
      const target = path.join(rootDir, 'apps', app, 'src', id.slice(2));
      const hit = ['', '.ts', '.tsx', '/index.ts', '/index.tsx']
        .map((suffix) => `${target}${suffix}`)
        .find((candidate) => existsSync(candidate));
      return hit ? hit.replace(/\\/g, '/') : null;
    },
  };
}

export default defineConfig({
  plugins: [appScopedSrcAlias()],
  resolve: {
    alias: [{ find: '@camelot/voice-first-runtime', replacement: voiceFirstRuntime }],
  },
  css: {
    // Inline (empty) PostCSS config so Vite never discovers an app's
    // postcss.config.js — autoprefixer → browserslist needs caniuse-lite, whose
    // unpacker/agents is corrupted on this host (see apps/pwa/vitest.config.ts).
    // These are TypeScript unit tests; none of them need a CSS pipeline.
    postcss: { plugins: [] },
  },
  test: {
    include: ['apps/*/src/**/*.test.ts', 'packages/*/src/**/*.test.ts'],
    // The pwa's two voice suites boot the real route module and the shared
    // runtime, so they need a generous hook timeout rather than the 5 s default.
    hookTimeout: 60_000,
    testTimeout: 30_000,
    // The exclude list has to cover every non-source tree in this repo, not just
    // node_modules/dist. Two concrete reasons:
    //
    //  1. `.camelot/` holds 543 staged `*.test.ts` files (`vault/staging/
    //     openclaude`). Without an exclude the root suite tries to collect
    //     vendored third-party tests, and `data/pytest-boot-sequence/` contains
    //     whole nested copies of the repo.
    //  2. Walking those trees is what made the root suite unrunnable: the glob
    //     hit a permission-locked `data/.pytest_cache` and vitest aborted with
    //     EPERM before collecting a single test.
    //
    // Only apps/*/src and packages/*/src are meant to hold first-party tests.
    exclude: [
      '**/node_modules/**',
      '**/dist/**',
      '**/.next/**',
      '**/.claude/**',
      '**/e2e/**',
      // Staged / vendored and generated trees.
      '**/.camelot/**',
      '**/.agent/**',
      '**/03_VAULT/**',
      '**/99_ARCHIVE/**',
      // Build + runtime output.
      '**/target/**',
      '**/data/**',
      '**/.venv/**',
      '**/venv/**',
      '**/.pytest_cache/**',
      '**/.pytest_temp/**',
      '**/.pytest_tmp*/**',
      '**/.runtime_logs/**',
      '**/__pycache__/**',
      '**/.git/**',
    ],
  },
});
