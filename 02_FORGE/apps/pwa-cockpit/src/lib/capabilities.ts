import "server-only";

import {
  appendFileSync,
  closeSync,
  copyFileSync,
  existsSync,
  fsyncSync,
  mkdirSync,
  openSync,
  readFileSync,
  renameSync,
  writeFileSync,
} from "node:fs";
import path from "node:path";
import { createHash, createHmac, randomBytes, timingSafeEqual } from "node:crypto";
import type { NextRequest } from "next/server";

import { isAuthorized, isCrossSiteRequest } from "./cockpit-auth";

// Phase 1 hardening: capability grants ride a short-lived HMAC blob bound to
// (capability, payload digest, target, expiry, single-use nonce). Sessions
// stay camelot_operator_session shaped; capability grants ride the
// X-Camelot-Capability-Grant header and are validated per-route via
// requireCapability(). Nonces are now disk-backed under
// 03_VAULT/runtime_state/pwa_cockpit_capability_nonces.json so process restarts
// cannot reopen the replay window.

export const CAPABILITY_GRANT_VERSION = 3 as const;
export const CAPABILITY_GRANT_TTL_SECONDS = 90;
const CAPABILITY_GRANT_CONTEXT = "camelot-pwa-cockpit/capability-grant/v3";
const CAPABILITY_NONCE_TTL_MS = CAPABILITY_GRANT_TTL_SECONDS * 2 * 1000;

export type Capability =
  | "status.read"
  | "voice.use"
  | "vision.capture"
  | "approval.manage"
  | "device.control"
  | "forge.execute"
  | "cartridge.install";

export const ALL_CAPABILITIES: readonly Capability[] = [
  "status.read",
  "voice.use",
  "vision.capture",
  "approval.manage",
  "device.control",
  "forge.execute",
  "cartridge.install",
] as const;

export type CapabilityBinding = {
  capability: Capability;
  payloadDigest: string;
  target?: string | null;
};

export type CapabilityGrantClaims = {
  version: 3;
  grantId: string;
  capability: Capability;
  payloadDigest: string;
  target: string | null;
  issuedAt: number;
  expiresAt: number;
  nonce: string;
  approvalId: string | null;
};

export type IssueCapabilityGrantInput = {
  capability: Capability;
  payloadDigest: string;
  target?: string | null;
  approvalId?: string | null;
  expiresAt?: number;
};

const CAMELOT_ROOT = process.env.CAMELOT_OS_HOME
  ? path.resolve(/* turbopackIgnore: true */ process.env.CAMELOT_OS_HOME)
  : path.resolve(/* turbopackIgnore: true */ process.cwd(), "../../..");
const NONCE_STORE_PATH = path.join(/* turbopackIgnore: true */ CAMELOT_ROOT, "03_VAULT", "runtime_state", "pwa_cockpit_capability_nonces.json");
const NONCE_BACKUP_PATH = `${NONCE_STORE_PATH}.bak`;

function base64urlEncode(value: string) {
  return Buffer.from(value, "utf8").toString("base64url");
}

function base64urlDecode(value: string) {
  return Buffer.from(value, "base64url").toString("utf8");
}

function equalText(left: string, right: string) {
  if (left.length !== right.length) return false;
  return timingSafeEqual(Buffer.from(left), Buffer.from(right));
}

type NonceStore = { nonces: Record<string, number> };

const emptyStore = (): NonceStore => ({ nonces: {} });

function isNonceStore(value: unknown): value is NonceStore {
  if (typeof value !== "object" || value === null || Array.isArray(value)) return false;
  const record = value as Record<string, unknown>;
  if (typeof record.nonces !== "object" || record.nonces === null || Array.isArray(record.nonces)) return false;
  const nonces = record.nonces as Record<string, unknown>;
  for (const entry of Object.values(nonces)) {
    if (typeof entry !== "number") return false;
  }
  return true;
}

function archiveInvalidNonceStore() {
  if (!existsSync(/* turbopackIgnore: true */ NONCE_STORE_PATH)) return;
  try {
    copyFileSync(/* turbopackIgnore: true */ NONCE_STORE_PATH, `${NONCE_STORE_PATH}.corrupt-${Date.now()}`);
  } catch {
    // Recovery still continues from the backup when archival is unavailable.
  }
}

function loadNonceStore(): NonceStore {
  for (const candidate of [NONCE_STORE_PATH, NONCE_BACKUP_PATH]) {
    if (!existsSync(/* turbopackIgnore: true */ candidate)) continue;
    try {
      const parsed: unknown = JSON.parse(readFileSync(/* turbopackIgnore: true */ candidate, "utf8"));
      if (!isNonceStore(parsed)) {
        if (candidate === NONCE_STORE_PATH) archiveInvalidNonceStore();
        continue;
      }
      if (candidate === NONCE_BACKUP_PATH) {
        // Mirror control-plane.ts: when the primary is invalid or missing,
        // archive any stale primary file and auto-restore the backup so the
        // on-disk store self-heals without operator intervention.
        archiveInvalidNonceStore();
        try {
          copyFileSync(/* turbopackIgnore: true */ NONCE_BACKUP_PATH, NONCE_STORE_PATH);
        } catch {
          // Auto-restore is best-effort; in-memory state is authoritative
          // for this process and the next mutation will repersist.
        }
      }
      pruneExpiredNonces(parsed, Date.now());
      return parsed;
    } catch {
      if (candidate === NONCE_STORE_PATH) archiveInvalidNonceStore();
    }
  }
  return emptyStore();
}

function pruneExpiredNonces(store: NonceStore, now: number) {
  for (const [key, ts] of Object.entries(store.nonces)) {
    if (now - ts > CAPABILITY_NONCE_TTL_MS) delete store.nonces[key];
  }
}

function persistNonceStore(store: NonceStore) {
  pruneExpiredNonces(store, Date.now());
  mkdirSync(/* turbopackIgnore: true */ path.dirname(NONCE_STORE_PATH), { recursive: true });
  const tempPath = `${NONCE_STORE_PATH}.tmp`;
  const descriptor = openSync(/* turbopackIgnore: true */ tempPath, "w");
  try {
    writeFileSync(descriptor, JSON.stringify(store, null, 2), "utf8");
    fsyncSync(descriptor);
  } finally {
    closeSync(descriptor);
  }
  if (existsSync(/* turbopackIgnore: true */ NONCE_STORE_PATH)) copyFileSync(/* turbopackIgnore: true */ NONCE_STORE_PATH, NONCE_BACKUP_PATH);
  renameSync(/* turbopackIgnore: true */ tempPath, NONCE_STORE_PATH);
}

const globalNonces = globalThis as typeof globalThis & { __pwaCockpitNonceStore?: NonceStore };
const nonceStore: NonceStore = globalNonces.__pwaCockpitNonceStore ?? loadNonceStore();
globalNonces.__pwaCockpitNonceStore = nonceStore;

export function consumeCapabilityNonce(nonce: string): boolean {
  const now = Date.now();
  if (Object.prototype.hasOwnProperty.call(nonceStore.nonces, nonce)) return false;
  nonceStore.nonces[nonce] = now;
  try {
    persistNonceStore(nonceStore);
  } catch {
    // Disk write failed; fall back to best-effort in-memory state.
    // The replay defense still holds locally for this process lifetime,
    // and a follow-up grant validation will re-attempt the write.
    delete nonceStore.nonces[nonce];
    return false;
  }
  return true;
}

// Test + recovery helper: clear all recorded nonces. Used by automated tests
// and by the recovery flow if the operator explicitly requests a nonce reset.
export function clearSeenNonces() {
  for (const key of Object.keys(nonceStore.nonces)) delete nonceStore.nonces[key];
  try {
    persistNonceStore(nonceStore);
  } catch {
    // Best-effort; in-memory state is already cleared.
  }
}

export function digestPayload(payload: string): string {
  return createHash("sha256").update(payload, "utf8").digest("hex");
}

export function issueCapabilityGrant(input: IssueCapabilityGrantInput) {
  const key = process.env.CAMELOT_COCKPIT_TOKEN?.trim() ?? "";
  if (key.length < 16) throw new Error("Cockpit signing key is not configured.");
  if (!ALL_CAPABILITIES.includes(input.capability)) {
    throw new Error(`Unknown capability: ${input.capability}`);
  }
  const issuedAt = Math.floor(Date.now() / 1000);
  const maxExpiry = issuedAt + CAPABILITY_GRANT_TTL_SECONDS;
  const expiresAt = Math.min(input.expiresAt ?? maxExpiry, maxExpiry);
  const claims: CapabilityGrantClaims = {
    version: CAPABILITY_GRANT_VERSION,
    grantId: randomBytes(12).toString("base64url"),
    capability: input.capability,
    payloadDigest: input.payloadDigest,
    target: input.target ?? null,
    issuedAt,
    expiresAt,
    nonce: randomBytes(18).toString("base64url"),
    approvalId: input.approvalId ?? null,
  };
  const payload = base64urlEncode(JSON.stringify(claims));
  const signature = createHmac("sha256", key)
    .update(`${CAPABILITY_GRANT_CONTEXT}:${payload}`)
    .digest("base64url");
  return { grant: `${payload}.${signature}`, claims };
}

export type VerifyCapabilityGrantResult =
  | { ok: true; claims: CapabilityGrantClaims }
  | { ok: false; reason: "expired" | "replayed" | "signature" | "malformed" | "payload-mismatch" | "capability-mismatch" | "token-missing" | "target-mismatch" };

export function verifyCapabilityGrant(
  grantValue: string | null | undefined,
  expected: { capability: Capability; payloadDigest?: string; target?: string | null },
): VerifyCapabilityGrantResult {
  const key = process.env.CAMELOT_COCKPIT_TOKEN?.trim() ?? "";
  if (key.length < 16) return { ok: false, reason: "token-missing" };
  if (!grantValue || typeof grantValue !== "string") return { ok: false, reason: "malformed" };
  const dot = grantValue.indexOf(".");
  if (dot <= 0 || dot >= grantValue.length - 1) return { ok: false, reason: "malformed" };
  const payload = grantValue.slice(0, dot);
  const suppliedSignature = grantValue.slice(dot + 1);
  const expectedSig = createHmac("sha256", key)
    .update(`${CAPABILITY_GRANT_CONTEXT}:${payload}`)
    .digest("base64url");
  if (!equalText(expectedSig, suppliedSignature)) return { ok: false, reason: "signature" };
  let claims: CapabilityGrantClaims;
  try {
    claims = JSON.parse(base64urlDecode(payload)) as CapabilityGrantClaims;
  } catch {
    return { ok: false, reason: "malformed" };
  }
  if (claims.version !== CAPABILITY_GRANT_VERSION || !ALL_CAPABILITIES.includes(claims.capability)) {
    return { ok: false, reason: "malformed" };
  }
  const now = Math.floor(Date.now() / 1000);
  if (claims.expiresAt <= now) return { ok: false, reason: "expired" };
  if (claims.capability !== expected.capability) return { ok: false, reason: "capability-mismatch" };
  if (expected.payloadDigest && claims.payloadDigest !== expected.payloadDigest) {
    return { ok: false, reason: "payload-mismatch" };
  }
  if (expected.target !== undefined && expected.target !== null && claims.target !== expected.target) {
    return { ok: false, reason: "target-mismatch" };
  }
  if (!consumeCapabilityNonce(claims.nonce)) return { ok: false, reason: "replayed" };
  return { ok: true, claims };
}

export class CapabilityRejected extends Error {
  readonly status: number;
  readonly capability: Capability;
  readonly reason: string;
  constructor(capability: Capability, reason: string, status = 403) {
    super(`Capability rejected: ${capability} (${reason})`);
    this.name = "CapabilityRejected";
    this.status = status;
    this.capability = capability;
    this.reason = reason;
  }
}

export type RequireCapabilityOptions = {
  payloadDigest?: string;
  target?: string | null;
  grant?: string | null;
};

function parseBearerOrRaw(header: string): string {
  // Equivalent of /^Bearer\s+(.+)$/i: case-insensitive "Bearer" prefix,
  // any whitespace (tab, newline, space) between prefix and token, no trailing
  // anchor required since slice(i) consumes the remainder.
  const trimmed = header.trim();
  if (trimmed.length < 7) return trimmed;
  if (trimmed.slice(0, 6).toLowerCase() !== "bearer") return trimmed;
  let i = 6;
  while (i < trimmed.length && /\s/.test(trimmed[i])) i += 1;
  return trimmed.slice(i);
}

export function requireCapability(
  request: NextRequest,
  capability: Capability,
  options: RequireCapabilityOptions = {},
): CapabilityGrantClaims {
  if (isCrossSiteRequest(request)) {
    throw new CapabilityRejected(capability, "cross-site", 403);
  }
  if (!isAuthorized(request)) {
    throw new CapabilityRejected(capability, "unauthorized", 401);
  }
  const header = options.grant ?? request.headers.get("x-camelot-capability-grant") ?? "";
  const grantValue = parseBearerOrRaw(header);
  const result = verifyCapabilityGrant(grantValue, {
    capability,
    payloadDigest: options.payloadDigest,
    target: options.target ?? undefined,
  });
  if (!result.ok) throw new CapabilityRejected(capability, `grant-${result.reason}`);
  return result.claims;
}

// Phase 1: route mutating runes to their declared capability so callers know which
// scope is required for Iron Gate clearance. The producer of the rune knows best;
// //CRYSTALLIZE and //EXECUTE_PROMPT require forge.execute, //DEVICE_… maps to
// device.control, //CARTRIDGE_/install/activate/rollback map to cartridge.install,
// //PLAN / //SWARM map to approval.manage, and any other mutating rune defaults to
// forge.execute so Iron Gate stays bounded.
export function directiveToCapability(directive: string): Capability | null {
  const root = directive.split(/\s+/)[0]?.toUpperCase() ?? "";
  if (!root.startsWith("//")) return null;
  if (root === "//CRYSTALLIZE" || root === "//EXECUTE_PROMPT") return "forge.execute";
  if (root === "//CARTRIDGE" || root === "//CARTRIDGE_INSTALL" || root === "//INSTALL" || root === "//ACTIVATE" || root === "//ROLLBACK") return "cartridge.install";
  if (root === "//PLAN" || root === "//SWARM" || root === "//FORGE") return "approval.manage";
  if (root.startsWith("//CARTRIDGE")) return "cartridge.install";
  if (root.startsWith("//DEVICE")) return "device.control";
  return "forge.execute";
}

// Phase 1.5 hardening: append-only JSONL audit log for grant mints that take
// the admin-override path (session does not carry the requested scope but
// CAMELOT_COCKPIT_GRANT_ADMIN=true is set). This is the high-trust escape
// hatch — a compromised admin env must leave a paper trail. The log lives at
// ${CAMELOT_ROOT}/03_VAULT/runtime_state/pwa_cockpit_grant_audit.log and is
// best-effort: a disk failure does NOT block the mint response.
const GRANT_AUDIT_LOG_PATH = path.join(/* turbopackIgnore: true */ CAMELOT_ROOT, "03_VAULT", "runtime_state", "pwa_cockpit_grant_audit.log");

export type GrantAuditRecord = {
  ts: number;
  source: "admin-override";
  capability: Capability;
  target: string | null;
  approvalId: string | null;
  sessionCapabilities: readonly Capability[];
};

export function appendGrantAuditLog(record: GrantAuditRecord) {
  try {
    mkdirSync(/* turbopackIgnore: true */ path.dirname(GRANT_AUDIT_LOG_PATH), { recursive: true });
    appendFileSync(/* turbopackIgnore: true */ GRANT_AUDIT_LOG_PATH, `${JSON.stringify(record)}\n`, "utf8");
  } catch {
    // Audit log is best-effort; the mint response is still authoritative.
  }
}
