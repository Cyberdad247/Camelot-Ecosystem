// SPDX-License-Identifier: MIT
//
// Voice-First Cartridge — Phase 3 crucible: network and security.
//
// Covers `docs/plans/voice-first-cartridge/verification.md` § Network and
// Security for `/api/voice/frames`: authenticated operator session, cross-site
// rejection, payload size, content type, host policy, and loopback-only
// forwarding.

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { NextRequest } from 'next/server';
import { POST } from '@/app/api/voice/frames/route';

const TOKEN = 'crucible-operator-token-0001';
const SESSION = `vfc-${'ab12'.repeat(6)}`;

interface FrameOptions {
  url?: string;
  token?: string | null;
  session?: string;
  sequence?: string;
  sampleRate?: string;
  contentType?: string | null;
  secFetchSite?: string | null;
  declaredLength?: number | null;
  body?: ArrayBuffer | Uint8Array;
}

function frameRequest(options: FrameOptions = {}): NextRequest {
  const headers = new Headers();
  if (options.contentType !== null) {
    headers.set('content-type', options.contentType ?? 'application/octet-stream');
  }
  if (options.token !== null) headers.set('x-operator-token', options.token ?? TOKEN);
  headers.set('x-voice-session', options.session ?? SESSION);
  headers.set('x-voice-sequence', options.sequence ?? '0');
  headers.set('x-voice-sample-rate', options.sampleRate ?? '16000');
  if (options.secFetchSite !== null) {
    headers.set('sec-fetch-site', options.secFetchSite ?? 'same-origin');
  }
  // Normalize to ArrayBuffer: a bare Uint8Array is not assignable to BodyInit
  // under this project's TS lib/target combination.
  const rawBody = options.body ?? new Int16Array(160).buffer;
  const body = rawBody instanceof Uint8Array ? (rawBody.slice().buffer as ArrayBuffer) : rawBody;
  if (options.declaredLength !== null) {
    headers.set('content-length', String(options.declaredLength ?? body.byteLength));
  }

  return new NextRequest(options.url ?? 'http://localhost:3000/api/voice/frames', {
    method: 'POST',
    headers,
    body,
  });
}

let fetchMock: ReturnType<typeof vi.fn>;

beforeEach(() => {
  vi.stubEnv('NODE_ENV', 'production');
  vi.stubEnv('CAMELOT_COCKPIT_TOKEN', TOKEN);
  vi.stubEnv('CAMELOT_COCKPIT_DEFAULT_CAPABILITIES', 'voice.use,status.read');
  fetchMock = vi.fn().mockResolvedValue(new Response('{}', { status: 202 }));
  vi.stubGlobal('fetch', fetchMock);
});

afterEach(() => {
  vi.unstubAllEnvs();
  vi.unstubAllGlobals();
});

describe('operator session', () => {
  it('rejects an unauthenticated caller with 401', async () => {
    const response = await POST(frameRequest({ token: null, url: 'http://camelot.example/api/voice/frames' }));
    expect(response.status).toBe(401);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('rejects a wrong operator token with 401', async () => {
    const response = await POST(
      frameRequest({ token: 'not-the-token', url: 'http://camelot.example/api/voice/frames' })
    );
    expect(response.status).toBe(401);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('accepts a matching operator token', async () => {
    const response = await POST(frameRequest({ url: 'http://camelot.example/api/voice/frames' }));
    expect(response.status).toBe(202);
  });

  it('denies a session that lacks the voice.use capability', async () => {
    vi.stubEnv('CAMELOT_COCKPIT_DEFAULT_CAPABILITIES', 'status.read');
    const response = await POST(frameRequest({ url: 'http://camelot.example/api/voice/frames' }));
    expect(response.status).toBe(403);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('denies a session with a tampered capability cookie', async () => {
    const request = frameRequest({ token: null, url: 'http://camelot.example/api/voice/frames' });
    // Hand-forged sidecar: valid JSON shape, unsigned payload.
    const payload = Buffer.from(JSON.stringify({ version: 1, capabilities: ['voice.use'] })).toString(
      'base64url'
    );
    request.headers.set('cookie', `camelot_operator_caps=${payload}.forged-signature`);
    const response = await POST(request);
    expect(response.status).toBe(401);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('allows development traffic on loopback without credentials', async () => {
    vi.stubEnv('NODE_ENV', 'development');
    const response = await POST(frameRequest({ token: null }));
    expect(response.status).toBe(202);
  });
});

describe('origin and host policy', () => {
  it('rejects a cross-site request with 403', async () => {
    const response = await POST(frameRequest({ secFetchSite: 'cross-site' }));
    expect(response.status).toBe(403);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('accepts same-origin and non-navigational requests', async () => {
    expect((await POST(frameRequest({ secFetchSite: 'same-origin' }))).status).toBe(202);
    expect((await POST(frameRequest({ secFetchSite: 'none' }))).status).toBe(202);
  });

  it('refuses to forward to a non-loopback OmniVoice endpoint', async () => {
    vi.stubEnv('CAMELOT_OMNIVOICE_URL', 'http://10.0.0.5:3002/ingest_pcm');
    const response = await POST(frameRequest());
    expect(response.status).toBe(503);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('refuses a non-http OmniVoice endpoint', async () => {
    vi.stubEnv('CAMELOT_OMNIVOICE_URL', 'https://echo.example/ingest_pcm');
    const response = await POST(frameRequest());
    expect(response.status).toBe(503);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('defaults to the loopback OmniVoice endpoint', async () => {
    await POST(frameRequest());
    expect(fetchMock).toHaveBeenCalledTimes(1);
    const [target] = fetchMock.mock.calls[0] as [URL];
    expect(target.hostname).toBe('127.0.0.1');
    expect(target.pathname).toBe('/ingest_pcm');
  });
});

describe('content type', () => {
  it('rejects a non-octet-stream payload with 415', async () => {
    const response = await POST(frameRequest({ contentType: 'application/json' }));
    expect(response.status).toBe(415);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('rejects a missing content type with 415', async () => {
    const response = await POST(frameRequest({ contentType: null }));
    expect(response.status).toBe(415);
    expect(fetchMock).not.toHaveBeenCalled();
  });
});

describe('frame metadata', () => {
  it('rejects a malformed session id', async () => {
    expect((await POST(frameRequest({ session: 'vfc-nothex' }))).status).toBe(400);
    expect((await POST(frameRequest({ session: '' }))).status).toBe(400);
  });

  it('rejects a non-16 kHz sample rate', async () => {
    expect((await POST(frameRequest({ sampleRate: '8000' }))).status).toBe(400);
  });

  it('rejects a negative or non-integer sequence', async () => {
    expect((await POST(frameRequest({ sequence: '-1' }))).status).toBe(400);
    expect((await POST(frameRequest({ sequence: '1.5' }))).status).toBe(400);
    expect((await POST(frameRequest({ sequence: 'abc' }))).status).toBe(400);
  });

  it('rejects every metadata failure before touching OmniVoice', async () => {
    await POST(frameRequest({ sampleRate: '8000' }));
    expect(fetchMock).not.toHaveBeenCalled();
  });
});

describe('payload size', () => {
  it('rejects a declared length above the 3,200 byte frame bound', async () => {
    const response = await POST(
      frameRequest({ declaredLength: 3_202, body: new Int16Array(1_601).buffer })
    );
    expect(response.status).toBe(413);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('rejects an odd byte length', async () => {
    const response = await POST(frameRequest({ body: new Uint8Array(3) }));
    expect(response.status).toBe(413);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('rejects an empty payload', async () => {
    const response = await POST(frameRequest({ body: new Uint8Array(0) }));
    expect(response.status).toBe(413);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('accepts exactly the 3,200 byte frame bound', async () => {
    const response = await POST(frameRequest({ body: new Int16Array(1_600).buffer }));
    expect(response.status).toBe(202);
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });
});

describe('forwarding', () => {
  it('propagates frame metadata and never caches', async () => {
    const response = await POST(frameRequest({ sequence: '7' }));
    const [, init] = fetchMock.mock.calls[0] as [URL, RequestInit];
    const headers = init.headers as Record<string, string>;

    expect(headers['x-voice-session']).toBe(SESSION);
    expect(headers['x-voice-sequence']).toBe('7');
    expect(headers['x-voice-sample-rate']).toBe('16000');
    expect(headers['x-voice-discontinuity']).toBe('0');
    expect(init.cache).toBe('no-store');
    expect(response.headers.get('Cache-Control')).toBe('no-store');
  });

  it('reports discontinuity as a flag', async () => {
    const request = frameRequest();
    request.headers.set('x-voice-discontinuity', '1');
    await POST(request);
    const [, init] = fetchMock.mock.calls[0] as [URL, RequestInit];
    expect((init.headers as Record<string, string>)['x-voice-discontinuity']).toBe('1');
  });

  it('returns 503 when OmniVoice rejects the frame', async () => {
    fetchMock.mockResolvedValue(new Response('{}', { status: 500 }));
    const response = await POST(frameRequest());
    expect(response.status).toBe(503);
    expect(await response.json()).toMatchObject({ accepted: false });
  });

  it('returns 503 when OmniVoice is unreachable', async () => {
    fetchMock.mockRejectedValue(new Error('connect ECONNREFUSED'));
    const response = await POST(frameRequest());
    expect(response.status).toBe(503);
  });

  it('never persists raw PCM in the response body', async () => {
    const response = await POST(frameRequest());
    const text = await response.text();
    expect(text).not.toContain('samples');
    expect(JSON.parse(text)).toEqual({ accepted: true });
  });
});
