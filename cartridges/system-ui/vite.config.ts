import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      injectRegister: 'auto',
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,vrm,mp4,json}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/fonts\.(?:googleapis|gstatic)\.com\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'google-fonts',
              expiration: {
                maxEntries: 10,
                maxAgeSeconds: 60 * 60 * 24 * 365, // 1 year
              },
            },
          },
          {
            // Bifrost websocket/SSE events are dynamic and bypass workbox cache
            urlPattern: /\/bifrost\/stream.*/i,
            handler: 'NetworkOnly',
          },
        ],
      },
      manifest: {
        name: 'Camelot-OS Excalibur PWA',
        short_name: 'Excalibur UI',
        description: 'Universal System UI Cartridge for Camelot-OS nodes',
        theme_color: '#05050A',
        background_color: '#05050A',
        display: 'standalone',
        orientation: 'portrait',
        icons: [
          {
            src: '/icons/icon-192x192.png',
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: '/icons/icon-512x512.png',
            sizes: '512x512',
            type: 'image/png',
          },
        ],
      },
    }),
  ],
  server: {
    port: 3004,
    host: true,
    proxy: {
      '/bifrost': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        ws: true,
      },
      '/goRouter': {
        target: 'http://127.0.0.1:8077',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/goRouter/, ''),
      },
      '/api/chatterbox': {
        target: 'http://127.0.0.1:8300',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/chatterbox/, '') || '/',
      },
      '/api/multivoice': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/multivoice/, '') || '/',
      },
      '/api': {
        target: 'http://127.0.0.1:3000',
        changeOrigin: true,
      },
    },
  },
});
