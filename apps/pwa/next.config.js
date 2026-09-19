// SPDX-License-Identifier: MIT

const path = require('path');
const webpack = require('webpack');

const VPS_HUB_IP = process.env.NEXT_PUBLIC_HUB_IP || '162.35.107.134';

/** @type {import("next").NextConfig} */
const nextConfig = {
  // The shared voice runtime lives in the separate 02_FORGE pnpm workspace,
  // outside this app's root, so Next must be told to compile it. Paired with the
  // webpack alias below, the tsconfig `paths` entry, and the vitest alias.
  experimental: {
    externalDir: true,
  },
  async rewrites() {
    return [
      {
        source: '/api/vps/bifrost/:path*',
        destination: `http://${VPS_HUB_IP}/bifrost/:path*`,
      },
      {
        source: '/api/vps/hermes/:path*',
        destination: `http://${VPS_HUB_IP}/v1/:path*`,
      },
      {
        source: '/api/vps/mesh/:path*',
        destination: `http://${VPS_HUB_IP}/mesh/:path*`,
      },
    ];
  },
  webpack: (config, { isServer }) => {


    config.plugins.push(
      new webpack.IgnorePlugin({
        resourceRegExp: /^virtual:/,
      })
    );

    config.resolve.alias['@agent-native/core'] = path.resolve(
      __dirname,
      'src/lib/agent-native-mock.ts'
    );

    config.resolve.alias['@camelot/voice-first-runtime'] = path.resolve(
      __dirname,
      'src/lib/voice-first-runtime/index.ts'
    );

    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        path: false,
        os: false,
        crypto: false,
        stream: false,
        child_process: false,
        net: false,
        tls: false,
      };

      config.resolve.alias = {
        ...config.resolve.alias,
        'better-sqlite3': false,
        'bindings': false,
      };
    }

    return config;
  },
};

module.exports = nextConfig;
