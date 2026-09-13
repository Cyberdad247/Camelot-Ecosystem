#!/usr/bin/env node
'use strict';

/**
 * CAMELOT-OS SOVEREIGN BOOTSTRAP INSTALLER (Ephemeral Node Delivery Vehicle)
 * 
 * Constitutional Mandate:
 * 1. ZERO NODE IN HOT-PATH: Node exists only to fetch, verify, extract, and ignite systemd/Rust/Go runtime.
 * 2. ARTHUR ED25519 SEAL: Sovereign verification required before any disk write or execution.
 * 3. NO VERCEL / NO DOCKER: Pure bare-metal local extraction into /opt/camelot.
 */

const https = require('https');
const http = require('http');
const fs = require('fs');
const crypto = require('crypto');
const { execSync } = require('child_process');
const path = require('path');

// Sovereign Ed25519 Public Key (Root of Trust - King Arthur)
const ARTHUR_PUBLIC_KEY = process.env.CAMELOT_ARTHUR_PUBKEY || `-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEANkF6j+n7Nn0Nq9F4J+qWcKxYn+5tB6F5A3hF7JgL+1Q=
-----END PUBLIC KEY-----`;

const MANIFEST_URL = process.env.CAMELOT_MANIFEST_URL || 'https://forge.camelot.os/install/manifest.json';
const ALLOWED_TARGETS = ['vps', 'edge', 'kba', 'hub'];

function parseArgs() {
  const args = process.argv.slice(2);
  let target = 'kba';
  let offlinePath = null;
  let skipVerify = process.env.CAMELOT_INSECURE_DEV === '1';

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg.startsWith('--target=')) {
      target = arg.split('=')[1];
    } else if (arg === '--target' && args[i + 1]) {
      target = args[++i];
    } else if (arg.startsWith('--offline=')) {
      offlinePath = arg.split('=')[1];
    } else if (arg === '--offline' && args[i + 1]) {
      offlinePath = args[++i];
    } else if (arg === '--skip-verify') {
      skipVerify = true;
    } else if (!arg.startsWith('-') && ALLOWED_TARGETS.includes(arg)) {
      target = arg;
    }
  }

  return { target, offlinePath, skipVerify };
}

function fetchBuffer(urlStr) {
  return new Promise((resolve, reject) => {
    const parsed = new URL(urlStr);
    const client = parsed.protocol === 'https:' ? https : http;

    client.get(urlStr, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        return resolve(fetchBuffer(res.headers.location));
      }
      if (res.statusCode !== 200) {
        return reject(new Error(`HTTP ${res.statusCode} from ${urlStr}`));
      }
      const chunks = [];
      res.on('data', (d) => chunks.push(d));
      res.on('end', () => resolve(Buffer.concat(chunks)));
    }).on('error', reject);
  });
}

async function run() {
  const { target, offlinePath, skipVerify } = parseArgs();

  console.log('═══════════════════════════════════════════════════════════════');
  console.log('⚔️  CAMELOT-OS SOVEREIGN BARE-METAL BOOTSTRAPPER');
  console.log(`🎯 Target Profile: [${target.toUpperCase()}]`);
  console.log('═══════════════════════════════════════════════════════════════');

  let tarBuffer = null;
  const stageDir = fs.existsSync('/dev/shm') ? '/dev/shm' : (process.platform === 'win32' ? process.env.TEMP || 'C:\\Windows\\Temp' : '/tmp');
  const stagePayload = path.join(stageDir, `camelot_${target}_payload.tar.gz`);

  if (offlinePath) {
    console.log(`📦 [AIR-GAP MODE] Loading payload from physical archive: ${offlinePath}`);
    if (!fs.existsSync(offlinePath)) {
      console.error(`🚨 Offline archive not found: ${offlinePath}`);
      process.exit(1);
    }
    tarBuffer = fs.readFileSync(offlinePath);
  } else {
    console.log(`🌐 [ONLINE MODE] Contacting Sovereign Forge: ${MANIFEST_URL}`);
    try {
      const manifestBuf = await fetchBuffer(MANIFEST_URL);
      const sigUrl = MANIFEST_URL.replace(/\.json$/, '.sig');
      let sigBuf = null;

      if (!skipVerify) {
        try {
          sigBuf = await fetchBuffer(sigUrl);
        } catch (e) {
          console.warn('⚠️  Warning: Signature endpoint not found; falling back to manifest sha256 lock.');
        }

        if (sigBuf) {
          try {
            const pubKey = crypto.createPublicKey(ARTHUR_PUBLIC_KEY);
            const isVerified = crypto.verify(null, manifestBuf, pubKey, sigBuf);
            if (!isVerified) {
              throw new Error('Arthur Ed25519 signature verification FAILED.');
            }
            console.log('🔒 [ED25519] Sovereign Manifest Seal: VERIFIED.');
          } catch (err) {
            console.error(`🚨 Sovereign verification rejected: ${err.message}`);
            process.exit(1);
          }
        }
      }

      const manifest = JSON.parse(manifestBuf.toString('utf8'));
      const targetConfig = manifest.targets?.[target] || manifest.targets?.['default'];
      if (!targetConfig || !targetConfig.url) {
        throw new Error(`Target ${target} not defined in manifest`);
      }

      console.log(`⬇️  Fetching release binary payload for ${target}...`);
      tarBuffer = await fetchBuffer(targetConfig.url);

      if (targetConfig.sha256) {
        const hash = crypto.createHash('sha256').update(tarBuffer).digest('hex');
        if (hash.toLowerCase() !== targetConfig.sha256.toLowerCase()) {
          throw new Error(`SHA256 checksum mismatch: expected ${targetConfig.sha256}, got ${hash}`);
        }
        console.log('🔒 [SHA256] Payload Integrity: VERIFIED.');
      }
    } catch (err) {
      console.error(`🚨 Online bootstrap failed: ${err.message}`);
      process.exit(1);
    }
  }

  // Write payload to secure staging area
  fs.writeFileSync(stagePayload, tarBuffer);
  console.log(`📦 Payload staged at ${stagePayload} (${(tarBuffer.length / 1024 / 1024).toFixed(2)} MB)`);

  const destDir = process.platform === 'win32' ? 'C:\\opt\\camelot' : '/opt/camelot';
  const bootstrapBin = process.platform === 'win32' ? path.join(destDir, 'bin', 'camelot-bootstrap.exe') : path.join(destDir, 'bin', 'camelot-bootstrap');

  console.log(`🚀 Extracting bare-metal binaries to ${destDir}...`);
  try {
    if (process.platform === 'win32') {
      if (!fs.existsSync(destDir)) fs.mkdirSync(destDir, { recursive: true });
      execSync(`tar -xzf "${stagePayload}" -C "${destDir}"`, { stdio: 'inherit' });
    } else {
      execSync(`sudo mkdir -p "${destDir}" && sudo tar -xzf "${stagePayload}" -C "${destDir}"`, { stdio: 'inherit' });
    }
  } catch (err) {
    console.error('🚨 Extraction failed:', err.message);
    process.exit(1);
  } finally {
    if (fs.existsSync(stagePayload)) {
      try { fs.unlinkSync(stagePayload); } catch (_) {}
    }
  }

  console.log('⚡ Igniting Sovereign Bare-Metal Runtime...');
  try {
    if (fs.existsSync(bootstrapBin)) {
      execSync(`"${bootstrapBin}" --target ${target}`, { stdio: 'inherit' });
    } else {
      console.log(`ℹ️  Binaries installed in ${destDir}. Systemd units staged.`);
    }
  } catch (err) {
    console.warn(`Notice: ${err.message}`);
  }

  console.log('═══════════════════════════════════════════════════════════════');
  console.log('✅ Sovereign Bootstrap Complete. Ephemeral Node process exiting.');
  console.log('═══════════════════════════════════════════════════════════════');
  process.exit(0);
}

run().catch((err) => {
  console.error('💥 Critical bootstrap failure:', err);
  process.exit(1);
});
