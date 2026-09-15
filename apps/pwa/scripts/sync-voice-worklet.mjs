// SPDX-License-Identifier: MIT
//
// Voice-First Cartridge — AudioWorklet asset sync.
//
// Re-homed from the purged `02_FORGE/apps/pwa-cockpit` (deleted in 944e4532,
// "purge redundant PWAs"). The canonical worklet still lives in the surviving
// `02_FORGE/packages/voice-first-runtime` package, so the PWA copies it into
// `public/` rather than forking a second implementation.
//
// Run from `apps/pwa`: node scripts/sync-voice-worklet.mjs

import { copyFile, mkdir } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const appRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const source = resolve(
  appRoot,
  '../../02_FORGE/packages/voice-first-runtime/worklets/voice-capture.worklet.js'
);
const target = resolve(appRoot, 'public/voice-capture.worklet.js');

await mkdir(dirname(target), { recursive: true });
await copyFile(source, target);
console.log('Synchronized Voice-First Cartridge AudioWorklet.');
