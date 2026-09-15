// SPDX-License-Identifier: MIT
//
// Voice-First Cartridge — operator auth for the voice frame ingress.
//
// Re-homed from the purged `02_FORGE/apps/pwa-cockpit` `lib/cockpit-auth.ts`
// (deleted in 944e4532, "purge redundant PWAs"). Only the surfaces
// `/api/voice/frames` actually consumed are carried over — `isAuthorized`,
// `isCrossSiteRequest`, `isLocalRequest`, and `operatorCapabilities`. The
// cockpit's capability-grant/nonce machinery is NOT reproduced here because the
// frame route never read it; reintroducing it without a consumer would be dead
// security surface.
//
// Two credential paths are accepted, both compared against the same
// `CAMELOT_COCKPIT_TOKEN` with a timing-safe compare:
//   1. `camelot_operator_session` — the HMAC-signed cockpit session cookie.
//   2. `x-operator-token` — the PWA-native header already used by
//      `src/lib/operator_console/operator-api.ts`.
// Neither path weakens the other: same secret, same constant-time comparison.

import { createHmac, timingSafeEqual } from 'node:crypto';
import type { NextRequest } from 'next/server';

export const OPERATOR_COOKIE = 'camelot_operator_session';
export const CAPABILITIES_COOKIE = 'camelot_operator_caps';
const SESSION_SALT = 'camelot-pwa-cockpit/v1';
const CAPABILITIES_SALT = 'camelot-pwa-cockpit/capability-scope/v1';
export const OPERATOR_SESSION_TTL_SECONDS = 60 * 60 * 12;
const MIN_TOKEN_LENGTH = 16;

export const ALL_CAPABILITIES = [
  'status.read',
  'voice.use',
  'vision.capture',
  'approval.manage',
  'device.control',
  'forge.execute',
] as const;

export type Capability = (typeof ALL_CAPABILITIES)[number];

function configuredToken(): string {
  return process.env.CAMELOT_COCKPIT_TOKEN?.trim() ?? '';
}

function equalText(left: string, right: string): boolean {
  if (left.length !== right.length || left.length === 0) return false;
  return timingSafeEqual(Buffer.from(left), Buffer.from(right));
}

function signature(value: string, secret: string): string {
  return createHmac('sha256', secret).update(`${SESSION_SALT}:${value}`).digest('base64url');
}

function hostName(request: NextRequest): string {
  return (request.headers.get('host') ?? request.nextUrl.hostname)
    .split(':')[0]
    .replace(/^\[|\]$/g, '')
    .toLowerCase();
}

export function isLocalRequest(request: NextRequest): boolean {
  const host = hostName(request);
  return host === 'localhost' || host === '127.0.0.1' || host === '::1';
}

function validateSessionCookie(
  cookie: string,
  secret: string,
  nowSeconds = Math.floor(Date.now() / 1000)
): boolean {
  const [version, issuedAtText, expiresAtText, nonce, suppliedSignature, ...extra] =
    cookie.split('.');
  if (version !== 'v1' || extra.length > 0 || !nonce || !suppliedSignature) return false;

  const issuedAt = Number(issuedAtText);
  const expiresAt = Number(expiresAtText);
  if (!Number.isSafeInteger(issuedAt) || !Number.isSafeInteger(expiresAt)) return false;
  if (issuedAt > nowSeconds + 60 || expiresAt <= nowSeconds) return false;
  if (expiresAt - issuedAt !== OPERATOR_SESSION_TTL_SECONDS) return false;

  const unsigned = [version, issuedAtText, expiresAtText, nonce].join('.');
  return equalText(suppliedSignature, signature(unsigned, secret));
}

export function isAuthorized(request: NextRequest): boolean {
  // Development bypass mirrors the cockpit contract: dev traffic on loopback is
  // usable without manual cookie minting. Production never takes this branch.
  if (process.env.NODE_ENV !== 'production' && isLocalRequest(request)) return true;

  const secret = configuredToken();
  if (secret.length < MIN_TOKEN_LENGTH) return false;

  const header = request.headers.get('x-operator-token');
  if (header) return equalText(header, secret);

  const cookie = request.cookies.get(OPERATOR_COOKIE)?.value ?? '';
  return cookie.length > 0 && validateSessionCookie(cookie, secret);
}

export function isCrossSiteRequest(request: NextRequest): boolean {
  const fetchSite = request.headers.get('sec-fetch-site');
  return fetchSite !== null && fetchSite !== 'same-origin' && fetchSite !== 'none';
}

function parseDefaultCapabilities(): Capability[] {
  const raw = process.env.CAMELOT_COCKPIT_DEFAULT_CAPABILITIES?.trim() ?? '';
  if (!raw) return [];
  const requested = raw
    .split(',')
    .map((value) => value.trim())
    .filter((value) => value.length > 0);
  const verified: Capability[] = [];
  for (const candidate of requested) {
    if ((ALL_CAPABILITIES as readonly string[]).includes(candidate)) {
      verified.push(candidate as Capability);
    }
  }
  return verified.sort();
}

// Deliberately NOT memoized: the previous module-level cache made a changed
// `CAMELOT_COCKPIT_DEFAULT_CAPABILITIES` invisible for the life of the process,
// so a session that should have lost `voice.use` kept it. Reading the env is
// cheap; a stale authorization scope is not.
export function defaultOperatorCapabilities(): Capability[] {
  return parseDefaultCapabilities();
}

function validateCapabilitiesCookie(cookie: string, secret: string): Capability[] {
  const dot = cookie.indexOf('.');
  if (dot <= 0 || dot >= cookie.length - 1) return [];
  const payload = cookie.slice(0, dot);
  const suppliedSignature = cookie.slice(dot + 1);
  const expected = createHmac('sha256', secret)
    .update(`${CAPABILITIES_SALT}:${payload}`)
    .digest('base64url');
  if (!equalText(expected, suppliedSignature)) return [];

  let parsed: unknown;
  try {
    parsed = JSON.parse(Buffer.from(payload, 'base64url').toString('utf8'));
  } catch {
    return [];
  }
  if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) return [];
  const record = parsed as Record<string, unknown>;
  if (record.version !== 1 || !Array.isArray(record.capabilities)) return [];

  const granted: Capability[] = [];
  for (const candidate of record.capabilities) {
    if (typeof candidate !== 'string') return [];
    if (!(ALL_CAPABILITIES as readonly string[]).includes(candidate)) return [];
    granted.push(candidate as Capability);
  }
  return granted;
}

export function operatorCapabilities(request: NextRequest): Capability[] {
  const secret = configuredToken();
  if (secret.length < MIN_TOKEN_LENGTH) return [];
  // Development bypass mirrors `isAuthorized`: in dev on loopback, advertise the
  // configured defaults so local capture is usable without manual cookie minting.
  if (process.env.NODE_ENV !== 'production' && isLocalRequest(request)) {
    return defaultOperatorCapabilities();
  }
  // Cookie sessions carry an explicit HMAC-signed scope sidecar.
  const cookie = request.cookies.get(CAPABILITIES_COOKIE)?.value ?? '';
  if (cookie) return validateCapabilitiesCookie(cookie, secret);
  // Header sessions (see `isAuthorized`) carry the operator's configured scopes.
  // Without this branch the capability check would be satisfiable only by a
  // sidecar cookie that nothing in this PWA mints, i.e. voice would be
  // permanently 403 in production.
  const header = request.headers.get('x-operator-token');
  if (header && equalText(header, secret)) return defaultOperatorCapabilities();
  return [];
}
