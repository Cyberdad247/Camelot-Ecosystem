import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  // Alias parity with apps/pwa/tsconfig.json paths and apps/pwa/next.config.js:
  // first-party tests import through these specifiers (e.g. the voice-first
  // cartridge crucible), so vitest must resolve them the same way.
  resolve: {
    alias: [
      {
        find: /^@\/(.*)/,
        replacement: fileURLToPath(new URL('./apps/pwa/src/$1', import.meta.url)),
      },
      {
        find: '@camelot/voice-first-runtime',
        replacement: fileURLToPath(
          new URL('./apps/pwa/src/lib/voice-first-runtime/index.ts', import.meta.url)
        ),
      },
    ],
  },
  test: {
    include: ['apps/*/src/**/*.test.ts', 'packages/*/src/**/*.test.ts'],
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
      '**/__pycache__/**',
      '**/.git/**',
    ],
  },
});
