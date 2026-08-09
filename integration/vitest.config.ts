import { defineConfig } from 'vitest/config';

// Scoped to the integration slice only. The repository root has its own
// vitest config (tests/router/**) on a different vitest major — the two
// toolchains are intentionally isolated (bootstrap-plan.md §Risks).
export default defineConfig({
  resolve: {
    alias: {
      // Tests exercise the contracts source directly (no build step needed).
      '@camelot/contracts': new URL('./contracts/src/index.ts', import.meta.url).pathname,
    },
  },
  test: {
    include: [
      'contracts/tests/**/*.test.ts',
      'kickbox/tests/**/*.test.ts',
      'hermes/tests/**/*.test.ts',
      'scripts/tests/**/*.test.ts',
    ],
    exclude: ['**/node_modules/**', '**/dist/**'],
  },
});
