import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
<<<<<<< HEAD
    include: ['tests/router/**/*.test.ts'],
    exclude: [
      '**/node_modules/**',
      '**/Projects/**'
    ],
=======
    include: ['**/*.test.ts'],
    exclude: ['**/node_modules/**', '**/dist/**', '**/.next/**', '**/.claude/**', '**/e2e/**'],
>>>>>>> 1e753daa6bbb3d6433608f2343c4fa3710e49629
  },
});
