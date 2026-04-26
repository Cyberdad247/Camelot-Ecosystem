// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'three-core': ['three'],
          'three-react': ['@react-three/fiber', '@react-three/drei'],
          'three-postprocessing': ['@react-three/postprocessing'],
          'three-rapier': ['@react-three/rapier'],
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
        },
      },
    },
    // Rapier is an intentionally lazy-loaded physics engine chunk for the legacy 3D brain scene.
    chunkSizeWarningLimit: 2200,
  },
})
