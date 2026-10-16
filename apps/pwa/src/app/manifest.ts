// SPDX-License-Identifier: MIT

import type { MetadataRoute } from 'next';

// PWA manifest — installable "Sovereign Universal Dashboard".
export default function manifest(): MetadataRoute.Manifest {
  return {
    id: 'sovereign-universal-dashboard',
    name: 'Sovereign Universal Dashboard',
    short_name: 'Sovereign',
    description: 'Sovereign Executive Intelligence — KickBox Audio & Lakisha Voice OS',
    start_url: '/',
    scope: '/',
    display: 'standalone',
    display_override: ['window-controls-overlay', 'standalone', 'minimal-ui'],
    orientation: 'portrait-primary',
    background_color: '#050507',
    theme_color: '#050507',
    categories: ['business', 'finance', 'productivity', 'utilities'],
    icons: [
      { src: '/icon.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'any' },
      { src: '/icon.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'maskable' },
    ],
    shortcuts: [
      {
        name: 'Lakisha Voice HUD',
        short_name: 'Voice HUD',
        description: 'Open immediate Lakisha Voice interface',
        url: '/?tab=voice',
        icons: [{ src: '/icon.svg', sizes: 'any' }],
      },
      {
        name: 'Citadel Matrix',
        short_name: 'Citadel',
        description: 'Open Camelot Citadel multi-agent status matrix',
        url: '/?tab=citadel',
        icons: [{ src: '/icon.svg', sizes: 'any' }],
      },
      {
        name: 'Invisioned Marketing Oracle',
        short_name: 'Oracle',
        description: 'Open Invisioned Marketing autonomous client oracle and ROAS telemetry',
        url: '/invisioned',
        icons: [{ src: '/icon.svg', sizes: 'any' }],
      },
    ],
  };
}
