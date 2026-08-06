import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: ['tests/router/**/*.test.ts', 'handover/payload/bifrost/ffi-policy.test.ts'],
    exclude: [
      '**/node_modules/**',
      '**/Projects/**'
    ],
  },
});
