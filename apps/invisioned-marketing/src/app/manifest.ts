// SPDX-License-Identifier: MIT
import type { MetadataRoute } from 'next';

export default function manifest(): MetadataRoute.Manifest {
  return {
    id: 'invisioned-marketing-agency',
    name: 'Invisioned Marketing Inc. — Sovereign Digital Factory',
    short_name: 'Invisioned',
    description: 'Autonomous multi-agent digital marketing agency, paid media attribution, and real-time client oracle.',
    start_url: '/',
    scope: '/',
    display: 'standalone',
    display_override: ['window-controls-overlay', 'standalone', 'minimal-ui'],
    orientation: 'portrait-primary',
    background_color: '#0B0B0E',
    theme_color: '#0B0B0E',
    categories: ['business', 'marketing', 'productivity', 'utilities'],
    icons: [
      { src: '/icon.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'any' },
      { src: '/icon.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'maskable' },
    ],
    shortcuts: [
      {
        name: 'Client Oracle',
        short_name: 'Oracle',
        description: 'Instant AI Knight dialogue and paid media performance check',
        url: '/#oracle',
        icons: [{ src: '/icon.svg', sizes: 'any' }],
      },
      {
        name: 'Instant Audit',
        short_name: 'Audit',
        description: '60-Second AI Paid Media & Funnel Conversion Audit',
        url: '/#audit',
        icons: [{ src: '/icon.svg', sizes: 'any' }],
      },
      {
        name: 'B2B Proposal Simulator',
        short_name: 'Proposal',
        description: 'Kinetic 2.5D proposal and ROAS yield agreement',
        url: '/#proposal',
        icons: [{ src: '/icon.svg', sizes: 'any' }],
      },
    ],
  };
}
