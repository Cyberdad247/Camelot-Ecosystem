// SPDX-License-Identifier: MIT

import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vitest/config';

const srcDir = fileURLToPath(new URL('./src', import.meta.url));

// The shared voice runtime lives in the separate 02_FORGE pnpm workspace, which
// the root npm `workspaces` globs (`apps/*`, `packages/*`) do not cover, so it is
// resolved by path alias rather than node_modules resolution. Mirrors the
// tsconfig `paths` entry and the webpack alias in next.config.js.
const voiceFirstRuntime = fileURLToPath(
  new URL('../../02_FORGE/packages/voice-first-runtime/src/index.ts', import.meta.url)
);

export default defineConfig({
  resolve: {
    // Regex form for `@/` so it cannot swallow the `@camelot/*` scoped package
    // name below (a bare `'@'` string alias would rewrite it to ./src/camelot/...).
    alias: [
      { find: /^@\//, replacement: `${srcDir}/` },
      { find: '@camelot/voice-first-runtime', replacement: voiceFirstRuntime },
    ],
  },
  css: {
    // Inline (empty) PostCSS config so Vite never discovers the PWA's
    // postcss.config.js — autoprefixer → browserslist needs caniuse-lite,
    // whose unpacker/agents is corrupted on this host. Pure TS unit tests
    // need no CSS pipeline.
    postcss: { plugins: [] },
  },
  test: {
    environment: 'node',
    // The OmniVoice crucible boots the router through ts-node, which needs far
    // more than the 5 s default to compile and bind.
    hookTimeout: 60_000,
    testTimeout: 30_000,
    // Whole of src/lib, not just operator_console: scoping the glob to one
    // subfolder silently orphaned voice.test.ts and telemetry.test.ts, so they
    // were never run (and could not fail) while still looking like coverage.
    include: ['src/lib/**/*.test.ts'],
  },
});
