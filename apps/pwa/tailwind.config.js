// SPDX-License-Identifier: MIT

// SINGLE source of truth for this app's Tailwind theme. A second file,
// `tailwind.config.ts`, used to sit beside this one. It was never read: Tailwind
// resolves the `.js` candidate first (and v4's `@config` cannot load TypeScript
// at all), so every token that existed only there produced no CSS — classes like
// `backdrop-blur-plate` and `shadow-kinetic` were written in the source and
// silently did nothing. Its three genuinely-used tokens are merged in below and
// the dead file is gone; do not reintroduce a second config.

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Sovereign Aura tokens (blueprint.md §2)
        obsidian: '#050507',
        smoke: { 900: '#0D0D11', 800: '#16161E' },
        gold: {
          DEFAULT: '#D4AF37',
          light: '#e9c349',
          royal: '#FFD700', // Polished Royal Gold — victory numerals
        },
        violet: { DEFAULT: '#9D4EDD', light: '#e0b6ff' },
      },
      fontFamily: {
        // Bound to next/font CSS variables (see app/layout.tsx). `--font-serif`
        // is the Source Serif 4 instance; there is no `--font-source-serif`
        // variable, which is why the deleted `.ts` config's `fontFamily.serif`
        // resolved to a literal font name and fell through to Georgia.
        sans: ['var(--font-inter)', 'system-ui', 'sans-serif'],
        serif: ['var(--font-serif)', '"Source Serif 4"', 'Georgia', 'serif'],
        display: ['var(--font-serif)', '"Libre Caslon Text"', 'Georgia', 'serif'],
      },
      letterSpacing: {
        // Editorial negative tracking on financial values. The deleted `.ts`
        // config had 0.08em here; every screen in this app was built and
        // reviewed against the tight value, so that is the one kept.
        minted: '-0.02em',
        executive: '0.1em', // wide tracking for the uppercase label rows
      },
      backdropBlur: {
        plate: '12px', // frosted glass plate panels
      },
      boxShadow: {
        glow: '0 0 12px rgba(157, 78, 221, 0.45)',
        'glow-lg': '0 0 24px rgba(157, 78, 221, 0.6)',
        gold: '0 0 16px rgba(212, 175, 55, 0.25)',
        kinetic: '0 0 12px rgba(157, 78, 221, 0.9)',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { boxShadow: '0 0 0 0 rgba(157, 78, 221, 0.55)' },
          '50%': { boxShadow: '0 0 0 8px rgba(157, 78, 221, 0)' },
        },
      },
      animation: {
        'pulse-glow': 'pulse-glow 1.4s ease-out infinite',
      },
    },
  },
  plugins: [],
};
