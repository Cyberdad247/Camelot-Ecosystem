const path = require('path');
process.stderr.write('[NEXT_CONFIG] loaded from: ' + __dirname + '\n');

/** @type {import('next').NextConfig} */
const nextConfig = {
  turbopack: {
    root: path.resolve(__dirname),
  },
  outputFileTracingRoot: path.resolve(__dirname),
};

module.exports = nextConfig;
