import path from 'path';
import react from '@vitejs/plugin-react';
// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/test/setup.ts',
    include: ['src/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
