const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === 'development',
});

const nextConfig = {
  reactStrictMode: true,
  // next-pwa adds a webpack config — use webpack bundler (via --webpack flag)
  turbopack: {},
};

module.exports = withPWA(nextConfig);
