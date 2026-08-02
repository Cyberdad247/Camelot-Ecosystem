import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
process.stderr.write('[NEXT_CONFIG] loaded from: ' + __dirname + '\n');

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  outputFileTracingRoot: __dirname,
  // Webpack bundler — Turbopack can't resolve next/package.json from app/
  // directory in pnpm monorepo (known issue with Next.js 16 on Windows).
  // The --webpack flag is passed via the build script.
  // TypeScript errors are checked separately in CI via forge-typecheck.
  typescript: {
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
