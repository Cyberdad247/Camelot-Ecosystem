// SPDX-License-Identifier: MIT
//
// Voice-First Cartridge — Phase 3 crucible: OmniVoice binary frame ingress.
//
// Covers `docs/plans/voice-first-cartridge/verification.md` § Network and
// Security: "OmniVoice `/ingest_pcm` accepts only loopback callers and valid
// Int16 frames" plus the bounded HTTP peer state.
//
// The router is a top-level-executing script with no exports and a
// `server.listen()` at module scope, so it cannot be imported — this is a real
// integration test against a spawned process, which is also the only way to
// exercise the actual wire contract.
//
// Scope note: the 403 `loopback_only` branch is not asserted here because a
// client running on this host always presents 127.0.0.1 as its socket address;
// asserting it would require binding a non-loopback interface.
//
// The router's tracked `omnivoice-router.js` build artifact is STALE (it
// predates the `/ingest_pcm` handler and contains none of the validation
// branches), so this test runs the TypeScript source through ts-node rather
// than the compiled output.

import { type ChildProcess, spawn } from 'node:child_process';
import { mkdtempSync, rmSync } from 'node:fs';
import { request as httpRequest } from 'node:http';
import { createServer } from 'node:net';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';

const ROUTER_DIR = fileURLToPath(
  new URL('../../../../../02_FORGE/KINETIC_ARMORY/omnivoice-router', import.meta.url)
);
const TS_NODE_BIN = join(ROUTER_DIR, 'node_modules', 'ts-node', 'dist', 'bin.js');
const PORT = 3002;
const PCM_FRAME_BYTES = 3_200;
const MAX_HTTP_SESSIONS = 16;

let child: ChildProcess | null = null;
let home: string;
let routerRunnable = true;

/** Sessions that actually got past the metadata/size checks and were created. */
const createdSessions = new Set<string>();
let sessionCounter = 0;

function newSessionId(): string {
  sessionCounter += 1;
  return `vfc-${sessionCounter.toString(16).padStart(24, '0')}`;
}

function canBind(port: number): Promise<boolean> {
  return new Promise((resolve) => {
    const probe = createServer();
    probe.once('error', () => resolve(false));
    probe.once('listening', () => probe.close(() => resolve(true)));
    probe.listen(port, '127.0.0.1');
  });
}

interface IngestOptions {
  session?: string;
  sequence?: number;
  contentType?: string | null;
  sampleRate?: string;
  body?: Buffer;
}

interface IngestResult {
  status: number;
  body: Record<string, unknown>;
}

function ingest(options: IngestOptions = {}): Promise<IngestResult> {
  const session = options.session ?? newSessionId();
  const body = options.body ?? Buffer.alloc(PCM_FRAME_BYTES);
  const headers: Record<string, string> = {
    'content-length': String(body.byteLength),
    'x-voice-session': session,
    'x-voice-sequence': String(options.sequence ?? 0),
    'x-voice-sample-rate': options.sampleRate ?? '16000',
  };
  if (options.contentType !== null) {
    headers['content-type'] = options.contentType ?? 'application/octet-stream';
  }

  return new Promise((resolve, reject) => {
    const req = httpRequest(
      { host: '127.0.0.1', port: PORT, path: '/ingest_pcm', method: 'POST', headers },
      (res) => {
        const chunks: Buffer[] = [];
        res.on('data', (chunk: Buffer) => chunks.push(chunk));
        res.on('end', () => {
          const raw = Buffer.concat(chunks).toString('utf8');
          let parsed: Record<string, unknown> = {};
          try {
            parsed = JSON.parse(raw) as Record<string, unknown>;
          } catch {
            parsed = { raw };
          }
          if (res.statusCode === 202 || res.statusCode === 409) createdSessions.add(session);
          resolve({ status: res.statusCode ?? 0, body: parsed });
        });
      }
    );
    req.on('error', reject);
    req.end(body);
  });
}

async function waitForOnline(timeoutMs = 45_000): Promise<boolean> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (child?.exitCode !== null) return false;
    try {
      await ingest({ contentType: 'application/json' });
      return true;
    } catch {
      await new Promise((r) => setTimeout(r, 250));
    }
  }
  return false;
}

beforeAll(async () => {
  if (!(await canBind(PORT))) {
    routerRunnable = false;
    return;
  }
  home = mkdtempSync(join(tmpdir(), 'camelot-vfc-omnivoice-'));
  child = spawn(process.execPath, [TS_NODE_BIN, '--esm', 'omnivoice-router.ts'], {
    cwd: ROUTER_DIR,
    env: { ...process.env, CAMELOT_OS_HOME: home },
    stdio: ['ignore', 'ignore', 'ignore'],
  });
  routerRunnable = await waitForOnline();
}, 60_000);

afterAll(async () => {
  if (child) {
    child.kill();
    child = null;
  }
  if (home) rmSync(home, { recursive: true, force: true });
});

describe('OmniVoice /ingest_pcm binary frame validation', () => {
  it('boots and serves the loopback ingest endpoint', () => {
    expect(routerRunnable).toBe(true);
  });

  it('rejects a non-octet-stream content type with 415', async () => {
    const result = await ingest({ contentType: 'application/json' });
    expect(result.status).toBe(415);
    expect(result.body.error).toBe('unsupported_media_type');
  });

  it('rejects a missing content type with 415', async () => {
    const result = await ingest({ contentType: null });
    expect(result.status).toBe(415);
  });

  it('rejects a malformed session id with 400', async () => {
    const result = await ingest({ session: 'vfc-not-a-24-hex-id' });
    expect(result.status).toBe(400);
    expect(result.body.error).toBe('invalid_frame_metadata');
  });

  it('rejects a non-16 kHz sample rate with 400', async () => {
    const result = await ingest({ sampleRate: '8000' });
    expect(result.status).toBe(400);
    expect(result.body.error).toBe('invalid_frame_metadata');
  });

  it('rejects a negative sequence with 400', async () => {
    const result = await ingest({ sequence: -1 });
    expect(result.status).toBe(400);
    expect(result.body.error).toBe('invalid_frame_metadata');
  });

  it('rejects an oversized frame with 413', async () => {
    const result = await ingest({ body: Buffer.alloc(PCM_FRAME_BYTES + 2) });
    expect(result.status).toBe(413);
    expect(result.body.error).toBe('invalid_frame_size');
  });

  it('rejects an odd byte length with 413', async () => {
    const result = await ingest({ body: Buffer.alloc(3) });
    expect(result.status).toBe(413);
    expect(result.body.error).toBe('invalid_frame_size');
  });

  it('rejects an empty frame with 413', async () => {
    const result = await ingest({ body: Buffer.alloc(0) });
    expect(result.status).toBe(413);
    expect(result.body.error).toBe('invalid_frame_size');
  });

  it('accepts a valid bounded Int16 frame with 202', async () => {
    const result = await ingest({ sequence: 0 });
    expect(result.status).toBe(202);
    expect(result.body).toMatchObject({ accepted: true, sequence: 0 });
  });

  it('accepts exactly the 3,200 byte frame bound', async () => {
    const result = await ingest({ sequence: 0, body: Buffer.alloc(PCM_FRAME_BYTES) });
    expect(result.status).toBe(202);
  });

  it('rejects a replayed or out-of-order sequence with 409', async () => {
    const session = newSessionId();
    const first = await ingest({ session, sequence: 5 });
    expect(first.status).toBe(202);

    const replay = await ingest({ session, sequence: 5 });
    expect(replay.status).toBe(409);
    expect(replay.body.error).toBe('stale_sequence');

    const stale = await ingest({ session, sequence: 4 });
    expect(stale.status).toBe(409);
  });
});

describe('OmniVoice bounded peer state', () => {
  it('caps concurrent HTTP sessions at 16 and refuses the overflow', async () => {
    let refusals = 0;
    for (let attempt = 0; attempt < MAX_HTTP_SESSIONS + 4; attempt += 1) {
      const result = await ingest({ sequence: 0 });
      if (result.status === 503) {
        expect(result.body.error).toBe('session_capacity_reached');
        refusals += 1;
        // Once the bound is hit, every further distinct session is refused.
        expect(createdSessions.size).toBeGreaterThanOrEqual(MAX_HTTP_SESSIONS);
      } else {
        expect(result.status).toBe(202);
      }
    }
    expect(refusals).toBeGreaterThan(0);
  });

  it('never admits more than 16 concurrent sessions', () => {
    expect(createdSessions.size).toBeLessThanOrEqual(MAX_HTTP_SESSIONS);
  });

  it('reuses an existing session instead of consuming a new slot', async () => {
    // Array.from, not spread: this project compiles at target es5 without
    // downlevelIteration, so spreading a Set is a type error.
    const session = Array.from(createdSessions)[0];
    expect(session).toBeDefined();
    const result = await ingest({ session, sequence: 99 });
    // A known session either accepts the new sequence or reports staleness —
    // neither path allocates a new peer slot.
    expect([202, 409]).toContain(result.status);
    expect(createdSessions.size).toBeLessThanOrEqual(MAX_HTTP_SESSIONS);
  });
});
