import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    include: ['tests/**/*.test.ts'],
    exclude: [
      '**/node_modules/**',
      '**/AppData/**',
      '**/CAMELOT_OS/**',
      '**/CLIProxyAPI/**',
      '**/LisaCustomKeychains/**',
      '**/Projects/**',
    ],
  },
});
