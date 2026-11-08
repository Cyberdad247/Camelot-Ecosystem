// SPDX-License-Identifier: MIT

// Tailwind 4 no longer ships a PostCSS plugin under its own package name: the
// `tailwindcss` entry in `plugins` was the v3 processor, and v4 exposes it as
// @tailwindcss/postcss instead. Leaving the old entry would silently do nothing —
// the build succeeds and the CSS comes out unstyled.
module.exports = {
  plugins: {
    '@tailwindcss/postcss': {},
    autoprefixer: {},
  },
};
