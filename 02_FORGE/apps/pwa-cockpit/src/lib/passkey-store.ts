import "server-only";

import { randomBytes } from "node:crypto";
import {
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
import type { AuthenticatorTransportFuture, CredentialDeviceType } from "@simplewebauthn/server";

export type StoredPasskey = {
  id: string;
  publicKey: string;
  counter: number;
  transports?: AuthenticatorTransportFuture[];
  deviceType: CredentialDeviceType;
  backedUp: boolean;
  createdAt: string;
  lastUsedAt?: string;
};

type PasskeyStore = {
  version: 1;
  userId: string;
  credentials: StoredPasskey[];
};

const CAMELOT_ROOT = process.env.CAMELOT_OS_HOME
  ? path.resolve(/* turbopackIgnore: true */ process.env.CAMELOT_OS_HOME)
  : path.resolve(/* turbopackIgnore: true */ process.cwd(), "../../..");
const STORE_PATH = path.join(/* turbopackIgnore: true */ CAMELOT_ROOT, "03_VAULT", "runtime_state", "pwa_cockpit_passkeys.json");
const BACKUP_PATH = `${STORE_PATH}.bak`;

function emptyStore(): PasskeyStore {
  return { version: 1, userId: randomBytes(32).toString("base64url"), credentials: [] };
}

function isStoredPasskey(value: unknown): value is StoredPasskey {
  if (typeof value !== "object" || value === null || Array.isArray(value)) return false;
  const item = value as Record<string, unknown>;
  return typeof item.id === "string"
    && typeof item.publicKey === "string"
    && typeof item.counter === "number"
    && Number.isSafeInteger(item.counter)
    && typeof item.deviceType === "string"
    && typeof item.backedUp === "boolean"
    && typeof item.createdAt === "string";
}

function parseStore(raw: string): PasskeyStore | null {
  const value: unknown = JSON.parse(raw);
  if (typeof value !== "object" || value === null || Array.isArray(value)) return null;
  const store = value as Record<string, unknown>;
  if (store.version !== 1 || typeof store.userId !== "string" || !Array.isArray(store.credentials)) return null;
  return { version: 1, userId: store.userId, credentials: store.credentials.filter(isStoredPasskey) };
}

function readStore(): PasskeyStore {
  for (const candidate of [STORE_PATH, BACKUP_PATH]) {
    if (!existsSync(/* turbopackIgnore: true */ candidate)) continue;
    try {
      const store = parseStore(readFileSync(/* turbopackIgnore: true */ candidate, "utf8"));
      if (store) return store;
    } catch {
      // A malformed primary never replaces a valid backup.
    }
  }
  return emptyStore();
}

function persistStore(store: PasskeyStore) {
  mkdirSync(/* turbopackIgnore: true */ path.dirname(STORE_PATH), { recursive: true });
  const tempPath = `${STORE_PATH}.${process.pid}.tmp`;
  const descriptor = openSync(/* turbopackIgnore: true */ tempPath, "w", 0o600);
  try {
    writeFileSync(descriptor, JSON.stringify(store, null, 2), "utf8");
    fsyncSync(descriptor);
  } finally {
    closeSync(descriptor);
  }
  if (existsSync(/* turbopackIgnore: true */ STORE_PATH)) copyFileSync(/* turbopackIgnore: true */ STORE_PATH, BACKUP_PATH);
  renameSync(/* turbopackIgnore: true */ tempPath, STORE_PATH);
}

const globalState = globalThis as typeof globalThis & {
  __camelotPasskeyStoreLock?: Promise<void>;
};

export async function withPasskeyStore<T>(operation: (store: PasskeyStore) => Promise<{ result: T; changed?: boolean }>): Promise<T> {
  const previous = globalState.__camelotPasskeyStoreLock ?? Promise.resolve();
  let release = () => {};
  globalState.__camelotPasskeyStoreLock = new Promise<void>((resolve) => { release = resolve; });
  await previous;
  try {
    const store = readStore();
    const { result, changed } = await operation(store);
    if (changed) persistStore(store);
    return result;
  } finally {
    release();
  }
}

export function decodePublicKey(value: string) {
  return new Uint8Array(Buffer.from(value, "base64url"));
}

export function encodePublicKey(value: Uint8Array) {
  return Buffer.from(value).toString("base64url");
}

export async function passkeyStatus() {
  return withPasskeyStore(async (store) => ({
    result: { configured: store.credentials.length > 0, count: store.credentials.length },
  }));
}
