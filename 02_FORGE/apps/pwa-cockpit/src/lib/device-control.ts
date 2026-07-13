import "server-only";

import { createHash, createPublicKey, randomUUID, verify } from "node:crypto";
import { closeSync, copyFileSync, existsSync, fsyncSync, mkdirSync, openSync, readFileSync, renameSync, writeFileSync } from "node:fs";
import path from "node:path";
import type { NextRequest } from "next/server";
import { capabilitiesFor, type DeviceAction, type DeviceHallSnapshot, type DevicePlatform, type DeviceSummary } from "./device-contract";

type StoredDevice = DeviceSummary & { publicKey: string };
type DeviceStore = { devices: StoredDevice[]; actions: DeviceAction[] };

const CAMELOT_ROOT = process.env.CAMELOT_OS_HOME
  ? path.resolve(/* turbopackIgnore: true */ process.env.CAMELOT_OS_HOME)
  : path.resolve(/* turbopackIgnore: true */ process.cwd(), "../../..");
const STORE_PATH = path.join(/* turbopackIgnore: true */ CAMELOT_ROOT, "03_VAULT", "runtime_state", "pwa_cockpit_devices.json");
const BACKUP_PATH = `${STORE_PATH}.bak`;
const globalState = globalThis as typeof globalThis & { __pwaDeviceStore?: DeviceStore; __pwaDeviceNonces?: Map<string, number> };

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function emptyStore(): DeviceStore {
  return { devices: [], actions: [] };
}

function loadStore(): DeviceStore {
  for (const candidate of [STORE_PATH, BACKUP_PATH]) {
    if (!existsSync(/* turbopackIgnore: true */ candidate)) continue;
    try {
      const parsed: unknown = JSON.parse(readFileSync(/* turbopackIgnore: true */ candidate, "utf8"));
      if (isRecord(parsed) && Array.isArray(parsed.devices) && Array.isArray(parsed.actions)) return parsed as DeviceStore;
    } catch {
      // Try the backup before starting with an empty registry.
    }
  }
  return emptyStore();
}

const store = globalState.__pwaDeviceStore ?? loadStore();
const seenNonces = globalState.__pwaDeviceNonces ?? new Map<string, number>();
globalState.__pwaDeviceStore = store;
globalState.__pwaDeviceNonces = seenNonces;

function persist() {
  mkdirSync(/* turbopackIgnore: true */ path.dirname(STORE_PATH), { recursive: true });
  const temporary = `${STORE_PATH}.tmp`;
  const descriptor = openSync(/* turbopackIgnore: true */ temporary, "w");
  try {
    writeFileSync(descriptor, JSON.stringify(store, null, 2), "utf8");
    fsyncSync(descriptor);
  } finally {
    closeSync(descriptor);
  }
  if (existsSync(/* turbopackIgnore: true */ STORE_PATH)) copyFileSync(/* turbopackIgnore: true */ STORE_PATH, BACKUP_PATH);
  renameSync(/* turbopackIgnore: true */ temporary, STORE_PATH);
}

function publicSummary(device: StoredDevice): DeviceSummary {
  const { publicKey: _publicKey, ...summary } = device;
  return summary;
}

export function deviceHallSnapshot(): DeviceHallSnapshot {
  return {
    devices: store.devices.map(publicSummary),
    actions: store.actions.slice(0, 40),
  };
}

export function enrollDevice(input: { name: string; platform: DevicePlatform; publicKey: string; capabilities: string[] }) {
  const name = input.name.trim().slice(0, 64);
  if (!name) throw new Error("Device name is required.");
  const key = createPublicKey(input.publicKey);
  if (key.asymmetricKeyType !== "ed25519") throw new Error("Device key must be Ed25519.");
  const canonicalKey = key.export({ type: "spki", format: "pem" }).toString();
  const allowed = new Set<string>(capabilitiesFor(input.platform));
  const capabilities = Array.from(new Set(input.capabilities)).filter((capability) => allowed.has(capability)).slice(0, 12);
  if (!capabilities.includes("system.status")) capabilities.unshift("system.status");
  const fingerprint = createHash("sha256").update(key.export({ type: "spki", format: "der" })).digest("hex").slice(0, 24);
  if (store.devices.some((device) => device.fingerprint === fingerprint && !device.revokedAt)) throw new Error("This device key is already enrolled.");
  const device: StoredDevice = {
    id: `dev-${randomUUID()}`,
    name,
    platform: input.platform,
    capabilities,
    fingerprint,
    publicKey: canonicalKey,
    createdAt: new Date().toISOString(),
  };
  store.devices.unshift(device);
  persist();
  return publicSummary(device);
}

export function revokeDevice(id: string) {
  const device = store.devices.find((candidate) => candidate.id === id && !candidate.revokedAt);
  if (!device) return null;
  device.revokedAt = new Date().toISOString();
  for (const action of store.actions.filter((candidate) => candidate.deviceId === id && ["awaiting_approval", "queued", "delivered"].includes(candidate.status))) {
    action.status = "rejected";
    action.result = "Device revoked before completion.";
    action.updatedAt = device.revokedAt;
  }
  persist();
  return publicSummary(device);
}

export function createDeviceAction(deviceId: string, capability: string, args: Record<string, string | number | boolean>) {
  const device = store.devices.find((candidate) => candidate.id === deviceId && !candidate.revokedAt);
  if (!device) throw new Error("Active device not found.");
  if (!device.capabilities.includes(capability)) throw new Error("Capability is not granted to this device.");
  if (JSON.stringify(args).length > 2048) throw new Error("Action arguments exceed the 2 KB limit.");
  const now = new Date().toISOString();
  const action: DeviceAction = {
    id: `act-${randomUUID()}`,
    deviceId,
    capability,
    arguments: args,
    status: "awaiting_approval",
    createdAt: now,
    updatedAt: now,
    attempts: 0,
  };
  store.actions.unshift(action);
  store.actions = store.actions.slice(0, 200);
  persist();
  return action;
}

export function resolveDeviceAction(command: string, approved: boolean) {
  const match = /^\/\/DEVICE\s+(act-[a-f0-9-]+)$/i.exec(command.trim());
  if (!match) return null;
  const action = store.actions.find((candidate) => candidate.id === match[1] && candidate.status === "awaiting_approval");
  if (!action) return { handled: true, queued: false, error: "Device action is missing or already resolved." };
  action.status = approved ? "queued" : "rejected";
  action.result = approved ? undefined : "Operator rejected the action.";
  action.updatedAt = new Date().toISOString();
  persist();
  return { handled: true, queued: approved, action };
}

function digest(body: string) {
  return createHash("sha256").update(body).digest("hex");
}

export function authenticateDeviceRequest(request: NextRequest, body = "") {
  const deviceId = request.headers.get("x-camelot-device-id") ?? "";
  const timestamp = request.headers.get("x-camelot-timestamp") ?? "";
  const nonce = request.headers.get("x-camelot-nonce") ?? "";
  const encodedSignature = request.headers.get("x-camelot-signature") ?? "";
  const device = store.devices.find((candidate) => candidate.id === deviceId && !candidate.revokedAt);
  if (!device || !/^\d{13}$/.test(timestamp) || !/^[A-Za-z0-9_-]{16,96}$/.test(nonce)) return null;
  const now = Date.now();
  if (Math.abs(now - Number(timestamp)) > 60_000) return null;
  seenNonces.forEach((expiresAt, key) => { if (expiresAt <= now) seenNonces.delete(key); });
  const nonceKey = `${deviceId}:${nonce}`;
  if (seenNonces.has(nonceKey)) return null;
  const canonical = [request.method.toUpperCase(), request.nextUrl.pathname, timestamp, nonce, digest(body)].join("\n");
  try {
    if (!verify(null, Buffer.from(canonical), device.publicKey, Buffer.from(encodedSignature, "base64url"))) return null;
  } catch {
    return null;
  }
  seenNonces.set(nonceKey, now + 120_000);
  device.lastSeenAt = new Date().toISOString();
  persist();
  return device;
}

export function pollDeviceAction(deviceId: string) {
  const action = store.actions.find((candidate) => candidate.deviceId === deviceId && (candidate.status === "queued" || candidate.status === "delivered"));
  if (!action) return null;
  action.status = "delivered";
  action.attempts += 1;
  action.updatedAt = new Date().toISOString();
  persist();
  return action;
}

export function completeDeviceAction(deviceId: string, actionId: string, success: boolean, result: string) {
  const action = store.actions.find((candidate) => candidate.id === actionId && candidate.deviceId === deviceId && actionIsDeliverable(candidate.status));
  if (!action) return null;
  action.status = success ? "completed" : "failed";
  action.result = result.slice(0, 500);
  action.updatedAt = new Date().toISOString();
  persist();
  return action;
}

function actionIsDeliverable(status: DeviceAction["status"]) {
  return status === "queued" || status === "delivered";
}
