import "server-only";

import { createHmac, randomBytes, timingSafeEqual } from "node:crypto";
import type { NextRequest } from "next/server";

import { ALL_CAPABILITIES, type Capability } from "./capabilities";

export const OPERATOR_COOKIE = "camelot_operator_session";
export const CAPABILITIES_COOKIE = "camelot_operator_caps";
const SESSION_SALT = "camelot-pwa-cockpit/v1";
const CAPABILITIES_SALT = "camelot-pwa-cockpit/capability-scope/v1";
export const OPERATOR_SESSION_TTL_SECONDS = 60 * 60 * 12;
const attempts = new Map<string, { count: number; resetAt: number }>();

// Phase 1 hardening (Item 3): per-session capability scopes are HMAC-signed
// into a sidecar cookie so the operator session advertises only the scopes
// production granted it (via CAMELOT_COCKPIT_DEFAULT_CAPABILITIES), not the
// entire ALL_CAPABILITIES list. The cookie format is a base64url-encoded JSON
// payload followed by an HMAC signature, same shape as CAMELOT_COCKPIT_TOKEN
// gate verification.

function parseDefaultCapabilities(): Capability[] {
  const raw = process.env.CAMELOT_COCKPIT_DEFAULT_CAPABILITIES?.trim() ?? "";
  if (!raw) return [];
  const requested = raw.split(",").map((value) => value.trim()).filter((value) => value.length > 0);
  const verified: Capability[] = [];
  for (const candidate of requested) {
    if (ALL_CAPABILITIES.includes(candidate as Capability)) verified.push(candidate as Capability);
  }
  return verified.sort();
}

let cachedDefaultCapabilities: Capability[] | null = null;
export function defaultOperatorCapabilities(): Capability[] {
  if (cachedDefaultCapabilities === null) cachedDefaultCapabilities = parseDefaultCapabilities();
  return cachedDefaultCapabilities.slice();
}

export type OperatorSession = {
  required: boolean;
  configured: boolean;
  authenticated: boolean;
  local: boolean;
};

function signature(value: string, token: string) {
  return createHmac("sha256", token).update(`${SESSION_SALT}:${value}`).digest("base64url");
}

function equalText(left: string, right: string) {
  if (left.length !== right.length) return false;
  return timingSafeEqual(Buffer.from(left), Buffer.from(right));
}

function validateSessionCookie(cookie: string, token: string, nowSeconds = Math.floor(Date.now() / 1000)) {
  const [version, issuedAtText, expiresAtText, nonce, suppliedSignature, ...extra] = cookie.split(".");
  if (version !== "v1" || extra.length > 0 || !nonce || !suppliedSignature) return false;

  const issuedAt = Number(issuedAtText);
  const expiresAt = Number(expiresAtText);
  if (!Number.isSafeInteger(issuedAt) || !Number.isSafeInteger(expiresAt)) return false;
  if (issuedAt > nowSeconds + 60 || expiresAt <= nowSeconds) return false;
  if (expiresAt - issuedAt !== OPERATOR_SESSION_TTL_SECONDS) return false;

  const unsigned = [version, issuedAtText, expiresAtText, nonce].join(".");
  return equalText(suppliedSignature, signature(unsigned, token));
}

function hostName(request: NextRequest) {
  return (request.headers.get("host") ?? request.nextUrl.hostname)
    .split(":")[0]
    .replace(/^\[|\]$/g, "")
    .toLowerCase();
}

export function isLocalRequest(request: NextRequest) {
  const host = hostName(request);
  return host === "localhost" || host === "127.0.0.1" || host === "::1";
}

export function operatorSession(request: NextRequest): OperatorSession {
  const local = isLocalRequest(request);
  const developmentBypass = process.env.NODE_ENV !== "production" && local;
  const token = process.env.CAMELOT_COCKPIT_TOKEN?.trim() ?? "";
  const configured = token.length >= 16;
  const cookie = request.cookies.get(OPERATOR_COOKIE)?.value ?? "";
  const authenticated = developmentBypass || (configured && cookie.length > 0 && validateSessionCookie(cookie, token));
  return {
    required: !developmentBypass,
    configured,
    authenticated,
    local,
  };
}

export function isAuthorized(request: NextRequest) {
  return operatorSession(request).authenticated;
}

export function isCrossSiteRequest(request: NextRequest) {
  const fetchSite = request.headers.get("sec-fetch-site");
  return fetchSite !== null && fetchSite !== "same-origin" && fetchSite !== "none";
}

export function isSecureRequest(request: NextRequest) {
  const forwardedProtocol = request.headers.get("x-forwarded-proto")?.split(",")[0]?.trim().toLowerCase();
  return request.nextUrl.protocol === "https:" || forwardedProtocol === "https";
}

function attemptKey(request: NextRequest) {
  return request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || hostName(request);
}

export function allowPairingAttempt(request: NextRequest) {
  const key = attemptKey(request);
  const now = Date.now();
  const current = attempts.get(key);
  if (!current || current.resetAt <= now) {
    attempts.set(key, { count: 1, resetAt: now + 60_000 });
    return true;
  }
  if (current.count >= 5) return false;
  current.count += 1;
  return true;
}

export function validateOperatorToken(input: string) {
  const expected = process.env.CAMELOT_COCKPIT_TOKEN?.trim() ?? "";
  if (expected.length < 16) return false;
  return equalText(input, expected);
}

export function sessionCookieValue() {
  const token = process.env.CAMELOT_COCKPIT_TOKEN?.trim() ?? "";
  if (token.length < 16) return "";
  const issuedAt = Math.floor(Date.now() / 1000);
  const expiresAt = issuedAt + OPERATOR_SESSION_TTL_SECONDS;
  const unsigned = `v1.${issuedAt}.${expiresAt}.${randomBytes(18).toString("base64url")}`;
  return `${unsigned}.${signature(unsigned, token)}`;
}

// Phase 1 hardening (Item 3): mint a sidecar cookie containing the granted
// capability scopes. Sorted so the payload is stable across reads.
export function capabilitiesCookieValue(caps: readonly Capability[]): string {
  const token = process.env.CAMELOT_COCKPIT_TOKEN?.trim() ?? "";
  if (token.length < 16) return "";
  const sorted = Array.from(new Set(caps)).sort() as Capability[];
  const payload = Buffer.from(JSON.stringify({ version: 1, capabilities: sorted }), "utf8").toString("base64url");
  const sig = createHmac("sha256", token).update(`${CAPABILITIES_SALT}:${payload}`).digest("base64url");
  return `${payload}.${sig}`;
}

function validateCapabilitiesCookie(cookie: string, token: string): Capability[] {
  const dot = cookie.indexOf(".");
  if (dot <= 0 || dot >= cookie.length - 1) return [];
  const payload = cookie.slice(0, dot);
  const suppliedSignature = cookie.slice(dot + 1);
  const expectedSig = createHmac("sha256", token).update(`${CAPABILITIES_SALT}:${payload}`).digest("base64url");
  if (!equalText(expectedSig, suppliedSignature)) return [];
  let parsed: unknown;
  try {
    parsed = JSON.parse(Buffer.from(payload, "base64url").toString("utf8"));
  } catch {
    return [];
  }
  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) return [];
  const record = parsed as Record<string, unknown>;
  if (record.version !== 1 || !Array.isArray(record.capabilities)) return [];
  const granted: Capability[] = [];
  for (const candidate of record.capabilities) {
    if (typeof candidate !== "string") return [];
    if (!ALL_CAPABILITIES.includes(candidate as Capability)) return [];
    granted.push(candidate as Capability);
  }
  return granted;
}

export function operatorCapabilities(request: NextRequest): Capability[] {
  const token = process.env.CAMELOT_COCKPIT_TOKEN?.trim() ?? "";
  if (token.length < 16) return [];
  // Development bypass mirrors operatorSession: in dev on loopback, advertise
  // the configured defaults so the cockpit is usable locally without manual
  // cookie minting.
  if (process.env.NODE_ENV !== "production" && isLocalRequest(request)) {
    return defaultOperatorCapabilities();
  }
  const cookie = request.cookies.get(CAPABILITIES_COOKIE)?.value ?? "";
  if (!cookie) return [];
  return validateCapabilitiesCookie(cookie, token);
}
