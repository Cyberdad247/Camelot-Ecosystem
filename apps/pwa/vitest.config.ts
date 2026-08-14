// SPDX-License-Identifier: MIT

import { defineConfig } from 'vitest/config';

export default defineConfig({
  css: {
    // Inline (empty) PostCSS config so Vite never discovers the PWA's
    // postcss.config.js — autoprefixer → browserslist needs caniuse-lite,
    // whose unpacker/agents is corrupted on this host. Pure TS unit tests
    // need no CSS pipeline.
    postcss: { plugins: [] },
  },
  test: {
    environment: 'node',
    include: ['src/lib/operator_console/**/*.test.ts'],
  },
});
