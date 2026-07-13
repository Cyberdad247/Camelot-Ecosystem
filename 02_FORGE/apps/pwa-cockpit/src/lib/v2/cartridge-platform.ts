// src/lib/v2/cartridge-platform.ts
//
// Phase 2 V2 cartridge platform — runtime hydrator.
//
// =====================================================================
// Phase 2 browser limitations (documented for the Phase 3 hardening pass)
// =====================================================================
// - HMAC key is read from `window.CAMELOT_HMAC_KEY` (a global on the
//   window object). Any browser script can read it. Phase 2 browser
//   verification is NOT a security boundary; the CLI is the trust
//   anchor. Encrypt the key with the cockpit session or move HMAC
//   verification entirely server-side in Phase 3.
// - The hydrateV2Cartridge() result for non-V1 archives synthesises
//   inert CartridgeProps (`onCommand: async () => undefined`). Dynamic
//   import of the archive's `entry` module is a Phase 3 follow-up; V2
//   archives cannot yet be mounted in the cockpit UI.
// - The in-browser trusted publisher registry is session-scoped: any
//   publisher added via registerTrustedPublisher() is lost on page
//   reload. The `legacy-v1` seed is deterministic and survives reloads.
//   Persistent registry storage (encrypted localStorage) is a Phase 3
//   follow-up.
// =====================================================================
//
// Mirrors the Python `CartridgeManifestV2` in `02_FORGE/cartridge/cartridge_schemas.py`.
//
// The seven V1 React cartridges in `src/cartridges/` keep working through the
// existing V1 trusted loader — this file is the V2 namespace and only touches
// the V1 layer through the documented `v1-legacy-import` SHA-256 bridge.
//
// API surface:
//   - hydrateV2Cartridge(manifest)        -> CartridgeProps for CartridgeMount
//   - verifyV2Archive(bytes)             -> VerifyResult (sha256 + sig + publisher)
//   - getTrustedPublisher(publisherId)   -> PublisherInfo | null
//   - registerTrustedPublisher(info)     -> add an in-browser trusted publisher
//
// Browser-only: no Node primitives, no shell access. All crypto via
// Web Crypto. The minimal ZIP reader in `cartridge-zip.ts` handles the
// archive format (uncompressed ZIP, STORE method only).

import { readZip, sha256Hex, bytesToHex, type ZipEntry } from "./cartridge-zip";
import { manifestFor } from "@/cartridges/registry";
import type { CartridgeId, CartridgeProps } from "@/cartridges/types";
import * as ed from "@noble/ed25519";
import { sha512 } from "@noble/hashes/sha512";

// Wire the sha512 implementation for browser. @noble/ed25519 requires a
// sha512 function; Node has crypto.createHash but the browser does not.
// This is the only crypto setup needed before calling ed.verify().
ed.etc.sha512Sync = (...m) => sha512(ed.etc.concatBytes(...m));

// ── V1 bridge constant (mirrors V1_LEGACY_SHA256 in Python) ────────────────
export const V1_LEGACY_SHA256 = "v1-legacy-import" as const;
export const V1_HOST_API_VERSION = "1" as const;
export const V2_HOST_API_VERSION = "2" as const;

// ── V2 type definitions ───────────────────────────────────────────────────
export type Capability = string;
export type PhaseGlyph = "[PLAN]" | "[EXECUTE]" | "[VALIDATE]" | "[COLONY]" | "[LIVE]";
export type Accent = "teal" | "amber" | "blue" | "coral";

export type V2RouteEntry = {
  mount: string;
  component: string;
  prefetch: string[];
};

export type V2ResourceBudget = {
  maxTokens: number;
  maxMemoryMb: number;
  maxLatencyMs: number;
};

export type V2CartridgeManifest = {
  // V1 inherited fields (all required by the V1 base class in Python)
  cartridge_id: string;
  version: string;
  description: string;
  agents: string[];
  tools: string[];
  protocols: string[];
  capabilities: Capability[];
  resource_budget: { max_tokens: number; max_memory_mb: number; max_latency_ms: number };
  risk_profile: "low" | "medium" | "high";
  governance: { HITL_required: boolean; allowed_tools: string[]; denied_operations: string[] };
  hooks: { on_load: string[]; on_unload: string[]; health_check: string[] };
  embeddings: { static_docs: string[]; symbolic_snippets: string[] };
  signature: string;
  created_at: string;
  created_by: string;
  // V2-only fields
  hostApiVersion: typeof V1_HOST_API_VERSION | typeof V2_HOST_API_VERSION | string;
  publisher_id: string;
  entry: string;
  sha256: string;
  routes: V2RouteEntry[];
  resourceBudget: V2ResourceBudget;
};

export type PublisherInfo = {
  publisherId: string;
  trustedKids: string[];
  // Map of kid -> base64-encoded public key. Required for Ed25519
  // verification; HMAC schemes resolve keys from env/window at verify
  // time so they don't need an entry here.
  publicKeys: Record<string, string>;
  active: boolean;
  note: string;
};

export type VerifyResult =
  | {
      ok: true;
      manifest: V2CartridgeManifest;
      payload: Uint8Array;
      reason: string;
    }
  | {
      ok: false;
      reason: string;
      stage: "sha256" | "signature" | "publisher" | "malformed" | "legacy-v1";
    };

// ── In-browser trusted-publisher registry ─────────────────────────────────
const trustedPublishers: Map<string, PublisherInfo> = new Map();

function bootstrapPublishers() {
  if (trustedPublishers.size > 0) return;
  // V1 legacy: any V1 cartridge (sha256 == "v1-legacy-import") is trusted
  // by default; the V1 registry is the source of truth for the seven
  // built-in cartridges. V1 publisher_id == "legacy-v1" is implicit.
  trustedPublishers.set("legacy-v1", {
    publisherId: "legacy-v1",
    trustedKids: ["default", "legacy"],
    // V1 legacy shims don't have Ed25519 public keys (they're trusted by
    // the V1 trusted loader, not by the publisher registry). Ed25519
    // verification of V1 shims is a no-op via the isV1Legacy short-circuit.
    publicKeys: {},
    active: true,
    note: "Phase 2: V1 React cartridges mounted via the V1 registry",
  });
}

export function registerTrustedPublisher(info: PublisherInfo): void {
  // Defense in depth: ensure the legacy-v1 seed is registered before any
  // user action so a bundle-loaded legacy-v1 entry cannot silently
  // overwrite the seed's deterministic publicKeys (which are empty for
  // V1 legacy shims).
  bootstrapPublishers();
  // Match the Python contract (PublisherRegistry.add_publisher raises
  // ValueError on duplicates). The seed is registered via the internal
  // trustedPublishers.set() in bootstrapPublishers, not through this
  // public API, so a duplicate check here blocks the only way an
  // external caller could overwrite the seed. Use loadTrustedPublishers
  // (which already throws on duplicates) for bulk bundle loads.
  if (trustedPublishers.has(info.publisherId)) {
    throw new Error(
      `publisher '${info.publisherId}' is already registered; ` +
        `registerTrustedPublisher refuses to overwrite existing publishers. ` +
        `To update a publisher, use loadTrustedPublishers with a fresh bundle.`,
    );
  }
  trustedPublishers.set(info.publisherId, info);
}

// Load a publisher bundle exported by `cartridge_cli export-bundle`.
// The bundle shape is:
//   { version: "1", exported_at: "<iso>", publishers: [{ publisherId,
//     trustedKids: [...], publicKeys: { kid: "base64..." }, active, note }] }
//
// Fails loud on malformed entries (security: don't silently load a partial
// bundle). Returns the number of publishers registered.
export function loadTrustedPublishers(input: string | object): number {
  // Bootstrap the deterministic legacy-v1 seed before processing the
  // bundle so the "refuses to overwrite" check below actually fires for
  // bundles that incorrectly include legacy-v1. Without this call, the
  // seed is only registered lazily on first getTrustedPublisher() call,
  // and a bundle loaded before that would silently overwrite the seed.
  bootstrapPublishers();
  const bundle = typeof input === "string" ? JSON.parse(input) : input;
  if (!bundle || typeof bundle !== "object") {
    throw new Error("publisher bundle must be a JSON object");
  }
  if (bundle.version !== "1") {
    throw new Error(
      `unsupported publisher bundle version: ${JSON.stringify(bundle.version)} ` +
        `(expected "1"); refusing to load unknown version for security`,
    );
  }
  if (!Array.isArray(bundle.publishers)) {
    throw new Error("publisher bundle must have a 'publishers' array");
  }
  let count = 0;
  for (let i = 0; i < bundle.publishers.length; i += 1) {
    const entry = bundle.publishers[i] as Partial<PublisherInfo> & {
      publisherId?: unknown;
      trustedKids?: unknown;
      publicKeys?: unknown;
    };
    if (!entry || typeof entry !== "object" || Array.isArray(entry)) {
      throw new Error(`publishers[${i}] is not an object`);
    }
    if (typeof entry.publisherId !== "string" || entry.publisherId.length === 0) {
      throw new Error(`publishers[${i}].publisherId is missing or invalid`);
    }
    if (!Array.isArray(entry.trustedKids)) {
      throw new Error(`publishers[${i}].trustedKids is not an array`);
    }
    // publicKeys must be a plain object (not an array). Arrays are objects
    // in JS, so guard explicitly to reject a malformed bundle.
    const publicKeys =
      entry.publicKeys &&
      typeof entry.publicKeys === "object" &&
      !Array.isArray(entry.publicKeys)
        ? (entry.publicKeys as Record<string, string>)
        : {};
    // Match the Python contract: refuse to silently overwrite an existing
    // publisher. The legacy-v1 seed is bootstrapped on first
    // getTrustedPublisher() call; bundles generated by `cartridge_cli
    // export-bundle` unconditionally filter out the seed, so operators
    // should never see this error for that reason. For non-seed duplicates,
    // there is currently no public API path to update an existing
    // publisher's `publicKeys`; the only escape is a browser restart
    // (which loses all session-scoped publishers). A `replace: true` opt
    // for `loadTrustedPublishers` is a Phase 3 follow-up.
    if (trustedPublishers.has(entry.publisherId)) {
      throw new Error(
        `publisher '${entry.publisherId}' is already registered; ` +
          `loadTrustedPublishers refuses to overwrite existing publishers. ` +
          `If this is the legacy-v1 seed, omit it from the bundle ` +
          `(it is always present and deterministic).`,
      );
    }
    registerTrustedPublisher({
      publisherId: entry.publisherId,
      trustedKids: entry.trustedKids as string[],
      publicKeys,
      active: entry.active !== false,
      note: typeof entry.note === "string" ? entry.note : "",
    });
    count += 1;
  }
  return count;
}

// Phase 3 bundle wiring helper: load a publisher bundle from a URL at
// runtime. This is the documented way to get a bundle into the browser:
// call this from the app entry point with the path to the exported
// publishers.json. Returns the number of publishers registered.
//
// The URL must be a same-origin relative path (starting with "/") to
// prevent SSRF via a compromised bundle URL. Absolute http(s) URLs are
// rejected; callers that need to fetch from a remote origin should
// proxy the bundle through their own backend first.
//
// The legacy-v1 seed must NOT appear in the bundle (it is bootstrapped
// lazily on first getTrustedPublisher() call); loadTrustedPublishers
// will throw if the bundle includes it. The convention is enforced at
// the source by `cartridge_cli export-bundle`, which unconditionally
// filters out the seed.
//
// Example wiring (call once at app startup):
//   await bootstrapPublishersFromBundle("/publishers.json")
export async function bootstrapPublishersFromBundle(
  url: string,
  init?: RequestInit,
): Promise<number> {
  if (!url.startsWith("/")) {
    throw new Error(
      `bootstrapPublishersFromBundle requires a same-origin relative path ` +
        `(URL must start with "/"); got "${url}". This restriction prevents ` +
        `SSRF via a compromised bundle URL.`,
    );
  }
  const response = await fetch(url, init);
  if (!response.ok) {
    throw new Error(
      `failed to fetch publisher bundle from ${url}: ` +
        `HTTP ${response.status} ${response.statusText}`,
    );
  }
  // Wrap .json() to surface a clear error on malformed JSON. Without
  // this, a bundle served as HTML (e.g. a 404 page) or truncated JSON
  // throws a bare SyntaxError that operators can't easily debug.
  let json: string | object;
  try {
    json = (await response.json()) as string | object;
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    throw new Error(
      `publisher bundle at ${url} is not valid JSON: ${message}`,
    );
  }
  return loadTrustedPublishers(json);
}

export function getTrustedPublisher(publisherId: string): PublisherInfo | null {
  bootstrapPublishers();
  return trustedPublishers.get(publisherId) ?? null;
}

export function isV1Legacy(manifest: V2CartridgeManifest): boolean {
  return manifest.sha256 === V1_LEGACY_SHA256;
}

// ── Hydrator ──────────────────────────────────────────────────────────────
export type HydratedCartridge = {
  id: CartridgeId | string;
  manifest: V2CartridgeManifest;
  isLegacyV1: boolean;
  routes: V2RouteEntry[];
  // The V1 CartridgeProps shape so the existing CartridgeMount component
  // can render the cartridge unchanged. The hydrator synthesises the
  // minimum fields AnyaPresence / CockpitShell consume.
  props: Pick<CartridgeProps, "onCommand" | "onInterrupt" | "busy" | "transport"> & {
    id: CartridgeId;
    status: CartridgeProps["status"];
    events: CartridgeProps["events"];
  };
};

export async function hydrateV2Cartridge(manifest: V2CartridgeManifest): Promise<HydratedCartridge> {
  // V1 legacy shim: delegate to the V1 trusted loader. The V1 manifest
  // table in the V1 registry is the source of truth for the seven built-in
  // cartridges; we synthesise the CartridgeProps from the V1 manifest.
  if (isV1Legacy(manifest)) {
    const v1 = manifestFor(manifest.cartridge_id as CartridgeId);
    return {
      id: v1.id,
      manifest,
      isLegacyV1: true,
      routes: manifest.routes,
      props: {
        id: v1.id,
        status: null,
        events: [],
        onCommand: async () => undefined,
        onInterrupt: () => undefined,
        busy: false,
        transport: { state: "offline", attempt: 0, nextRetryMs: null },
      },
    };
  }
  // V2 archive path: the entry + payload are loaded separately by the caller
  // and validated through verifyV2Archive. The hydrator returns the props
  // shape but the entry module is not yet loaded — dynamic import of the
  // payload is the next phase. For now we synthesise inert props.
  return {
    id: manifest.cartridge_id,
    manifest,
    isLegacyV1: false,
    routes: manifest.routes,
    props: {
      id: manifest.cartridge_id as CartridgeId,
      status: null,
      events: [],
      onCommand: async () => undefined,
      onInterrupt: () => undefined,
      busy: false,
      transport: { state: "offline", attempt: 0, nextRetryMs: null },
    },
  };
}

// ── Verify (archive bytes) ────────────────────────────────────────────────
function bytesToString(bytes: Uint8Array): string {
  return new TextDecoder("utf-8").decode(bytes);
}

function findEntry(entries: ZipEntry[], name: string): ZipEntry | undefined {
  return entries.find((entry) => entry.name === name);
}

function parseSignature(signature: string): { scheme: string; kid: string; rawB64: string } | null {
  if (!signature || typeof signature !== "string") return null;
  const parts = signature.split(":");
  if (parts.length === 3) {
    const [scheme, kid, rawB64] = parts;
    if (scheme !== "ed25519" && scheme !== "hmac") return null;
    return { scheme, kid, rawB64 };
  }
  if (parts.length === 2) {
    const [scheme, rawB64] = parts;
    if (scheme !== "ed25519" && scheme !== "hmac") return null;
    return { scheme, kid: "default", rawB64 };
  }
  return null;
}

function canonicalManifestBytes(manifest: V2CartridgeManifest): Uint8Array {
  // Canonical JSON of the manifest excluding signature + created_at,
  // sorted keys. Matches cartridge_crypto.canonical_bytes in Python.
  // Single source of truth for both HMAC and Ed25519 verification.
  const { signature: _sig, created_at: _created, ...rest } = manifest;
  const sorted = JSON.stringify(rest, Object.keys(rest).sort());
  return new TextEncoder().encode(sorted);
}

async function verifyHmacSignature(
  manifest: V2CartridgeManifest,
  rawB64: string,
  hmacKey: string,
): Promise<boolean> {
  const data = canonicalManifestBytes(manifest);
  const keyBytes = new TextEncoder().encode(hmacKey);
  const key = await crypto.subtle.importKey(
    "raw",
    keyBytes,
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign", "verify"],
  );
  const expected = Uint8Array.from(atob(rawB64), (c) => c.charCodeAt(0));
  // crypto.subtle.verify expects BufferSource (ArrayBuffer | ArrayBufferView<ArrayBuffer>).
  // Our Uint8Array.from() and TextEncoder.encode() return Uint8Array<ArrayBufferLike>
  // (which includes SharedArrayBuffer), so cast through `as BufferSource` to bridge
  // the TS lib's strict generic typing.
  return crypto.subtle.verify("HMAC", key, expected as BufferSource, data as BufferSource);
}

function verifyEd25519Signature(
  manifest: V2CartridgeManifest,
  rawB64: string,
  publicKeyB64: string,
): boolean {
  // @noble/ed25519's ed.verify() is synchronous (no await needed).
  // Ed25519 signature = 64 bytes, public key = 32 bytes.
  // We pass hex strings (not Uint8Array) to sidestep the
  // Uint8Array<ArrayBufferLike> vs Uint8Array<ArrayBuffer> generic
  // mismatch that arises when Uint8Array.from() returns the former
  // but ed.verify's BufferSource type expects the latter.
  const message = canonicalManifestBytes(manifest);
  const signature = Uint8Array.from(atob(rawB64), (c) => c.charCodeAt(0));
  const publicKey = Uint8Array.from(atob(publicKeyB64), (c) => c.charCodeAt(0));
  if (signature.length !== 64) return false;
  if (publicKey.length !== 32) return false;
  return ed.verify(bytesToHex(signature), bytesToHex(message), bytesToHex(publicKey));
}

export async function verifyV2Archive(bytes: ArrayBuffer): Promise<VerifyResult> {
  let entries: ZipEntry[];
  try {
    entries = readZip(bytes);
  } catch (error) {
    return { ok: false, reason: (error as Error).message, stage: "malformed" };
  }

  const manifestEntry = findEntry(entries, "manifest.json");
  const payloadEntry = findEntry(entries, "payload.zip");
  if (!manifestEntry || !payloadEntry) {
    return {
      ok: false,
      reason: "archive must contain exactly manifest.json and payload.zip",
      stage: "malformed",
    };
  }

  let manifest: V2CartridgeManifest;
  try {
    manifest = JSON.parse(bytesToString(manifestEntry.data)) as V2CartridgeManifest;
  } catch (error) {
    return { ok: false, reason: `manifest.json is not valid JSON: ${(error as Error).message}`, stage: "malformed" };
  }

  // V1 legacy manifests are accepted without payload verification.
  if (isV1Legacy(manifest)) {
    return { ok: true, manifest, payload: payloadEntry.data, reason: "v1-legacy-import accepted" };
  }

  // SHA-256 must match.
  const actual = await sha256Hex(payloadEntry.data);
  if (actual !== manifest.sha256) {
    return {
      ok: false,
      reason: `sha256 mismatch: manifest declares ${manifest.sha256.slice(0, 16)}…, payload is ${actual.slice(0, 16)}…`,
      stage: "sha256",
    };
  }

  // Publisher check.
  const publisher = getTrustedPublisher(manifest.publisher_id);
  if (!publisher) {
    return { ok: false, reason: `unknown publisher '${manifest.publisher_id}'`, stage: "publisher" };
  }
  if (!publisher.active) {
    return { ok: false, reason: `publisher '${manifest.publisher_id}' is deactivated`, stage: "publisher" };
  }

  // Signature check (HMAC via Web Crypto, Ed25519 via @noble/ed25519).
  const parsed = parseSignature(manifest.signature);
  if (!parsed) {
    return { ok: false, reason: "signature uses an unrecognised wire format", stage: "signature" };
  }
  if (!publisher.trustedKids.includes(parsed.kid)) {
    return {
      ok: false,
      reason: `publisher '${manifest.publisher_id}' does not own kid '${parsed.kid}'`,
      stage: "publisher",
    };
  }
  if (parsed.scheme === "hmac") {
    const hmacKey = (typeof window !== "undefined" && (window as { CAMELOT_HMAC_KEY?: string }).CAMELOT_HMAC_KEY) ?? "";
    if (!hmacKey) {
      return { ok: false, reason: "HMAC verification requires CAMELOT_HMAC_KEY in the browser", stage: "signature" };
    }
    const ok = await verifyHmacSignature(manifest, parsed.rawB64, hmacKey);
    if (!ok) {
      return { ok: false, reason: "HMAC signature does not match manifest content", stage: "signature" };
    }
  } else if (parsed.scheme === "ed25519") {
    const publicKeyB64 = publisher.publicKeys[parsed.kid];
    if (!publicKeyB64) {
      return {
        ok: false,
        reason: `publisher '${manifest.publisher_id}' has no public key for kid '${parsed.kid}'`,
        stage: "signature",
      };
    }
    const ok = verifyEd25519Signature(manifest, parsed.rawB64, publicKeyB64);
    if (!ok) {
      return { ok: false, reason: "Ed25519 signature does not match manifest content", stage: "signature" };
    }
  }

  return { ok: true, manifest, payload: payloadEntry.data, reason: `verified with publisher '${manifest.publisher_id}'` };
}
