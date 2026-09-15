// SPDX-License-Identifier: MIT

const path = require('path');
const webpack = require('webpack');

/** @type {import("next").NextConfig} */
const nextConfig = {
  // The shared voice runtime lives in the separate 02_FORGE pnpm workspace,
  // outside this app's root, so Next must be told to compile it. Paired with the
  // webpack alias below, the tsconfig `paths` entry, and the vitest alias.
  experimental: {
    externalDir: true,
  },
  webpack: (config, { isServer }) => {
    config.resolve.alias['react'] = path.resolve(__dirname, 'node_modules/react');
    config.resolve.alias['react-dom'] = path.resolve(__dirname, 'node_modules/react-dom');

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
      '../../02_FORGE/packages/voice-first-runtime/src/index.ts'
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
