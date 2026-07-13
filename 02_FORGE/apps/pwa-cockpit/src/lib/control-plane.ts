import "server-only";

import { randomUUID } from "node:crypto";
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
import type { Approval, CockpitEvent, CommandReceipt } from "./cockpit-types";
import { getRuntimeStatus } from "./runtime-status";

type CockpitStore = {
  events: CockpitEvent[];
  approvals: Approval[];
  receipts: CommandReceipt[];
};

const CAMELOT_ROOT = process.env.CAMELOT_OS_HOME
  ? path.resolve(/* turbopackIgnore: true */ process.env.CAMELOT_OS_HOME)
  : path.resolve(/* turbopackIgnore: true */ process.cwd(), "../../..");
const STORE_PATH = path.join(/* turbopackIgnore: true */ CAMELOT_ROOT, "03_VAULT", "runtime_state", "pwa_cockpit_store.json");
const BACKUP_PATH = `${STORE_PATH}.bak`;
const receiptStatuses = new Set<CommandReceipt["status"]>([
  "accepted",
  "requires_approval",
  "approved",
  "rejected",
  "execution_blocked",
  "executed",
  "failed",
]);

function initialStore(message = "Cockpit API initialized with durable local runtime state.", level: CockpitEvent["level"] = "info"): CockpitStore {
  return {
    events: [
      {
        id: `evt-${randomUUID()}`,
        ts: new Date().toISOString(),
        level,
        source: "pwa-cockpit",
        message,
      },
    ],
    approvals: [],
    receipts: [],
  };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isEvent(value: unknown): value is CockpitEvent {
  return isRecord(value)
    && typeof value.id === "string"
    && typeof value.ts === "string"
    && (value.level === "info" || value.level === "warn" || value.level === "error")
    && typeof value.source === "string"
    && typeof value.message === "string";
}

function isApproval(value: unknown): value is Approval {
  return isRecord(value)
    && typeof value.id === "string"
    && typeof value.command === "string"
    && typeof value.reason === "string"
    && (value.status === "pending" || value.status === "approved" || value.status === "rejected")
    && typeof value.createdAt === "string"
    && (value.resolvedAt === undefined || typeof value.resolvedAt === "string");
}

function isReceipt(value: unknown): value is CommandReceipt {
  return isRecord(value)
    && typeof value.id === "string"
    && typeof value.command === "string"
    && typeof value.status === "string"
    && receiptStatuses.has(value.status as CommandReceipt["status"])
    && typeof value.createdAt === "string";
}

function parseStore(raw: string): CockpitStore | null {
  const parsed: unknown = JSON.parse(raw);
  if (!isRecord(parsed) || !Array.isArray(parsed.events) || !Array.isArray(parsed.approvals) || !Array.isArray(parsed.receipts)) {
    return null;
  }
  return {
    events: parsed.events.filter(isEvent).slice(0, 100),
    approvals: parsed.approvals.filter(isApproval).slice(0, 50),
    receipts: parsed.receipts.filter(isReceipt).slice(0, 100),
  };
}

function archiveInvalidPrimary() {
  if (!existsSync(/* turbopackIgnore: true */ STORE_PATH)) return;
  try {
    copyFileSync(/* turbopackIgnore: true */ STORE_PATH, `${STORE_PATH}.corrupt-${Date.now()}`);
  } catch {
    // Recovery still continues from the backup when archival is unavailable.
  }
}

function loadStore(): CockpitStore {
  for (const candidate of [STORE_PATH, BACKUP_PATH]) {
    if (!existsSync(/* turbopackIgnore: true */ candidate)) continue;
    try {
      const store = parseStore(readFileSync(/* turbopackIgnore: true */ candidate, "utf8"));
      if (!store) {
        if (candidate === STORE_PATH) archiveInvalidPrimary();
        continue;
      }
      if (candidate === BACKUP_PATH) {
        copyFileSync(/* turbopackIgnore: true */ BACKUP_PATH, STORE_PATH);
        store.events.unshift({
          id: `evt-${randomUUID()}`,
          ts: new Date().toISOString(),
          level: "warn",
          source: "pwa-cockpit",
          message: "Primary Cockpit store was invalid; recovered durable evidence from the backup.",
        });
      }
      return store;
    } catch {
      if (candidate === STORE_PATH) archiveInvalidPrimary();
    }
  }
  return initialStore("No valid Cockpit store was available; initialized a new store without deleting prior evidence.", "warn");
}

const globalStore = globalThis as typeof globalThis & { __pwaCockpitStore?: CockpitStore };
export const cockpitStore = globalStore.__pwaCockpitStore ?? loadStore();
globalStore.__pwaCockpitStore = cockpitStore;

function persistStore() {
  mkdirSync(/* turbopackIgnore: true */ path.dirname(STORE_PATH), { recursive: true });
  const tempPath = `${STORE_PATH}.tmp`;
  const descriptor = openSync(/* turbopackIgnore: true */ tempPath, "w");
  try {
    writeFileSync(descriptor, JSON.stringify(cockpitStore, null, 2), "utf8");
    fsyncSync(descriptor);
  } finally {
    closeSync(descriptor);
  }
  if (existsSync(/* turbopackIgnore: true */ STORE_PATH)) copyFileSync(/* turbopackIgnore: true */ STORE_PATH, BACKUP_PATH);
  renameSync(/* turbopackIgnore: true */ tempPath, STORE_PATH);
}

function appendEvent(event: Omit<CockpitEvent, "id" | "ts">) {
  const completeEvent: CockpitEvent = {
    ...event,
    id: `evt-${randomUUID()}`,
    ts: new Date().toISOString(),
  };
  cockpitStore.events.unshift(completeEvent);
  cockpitStore.events = cockpitStore.events.slice(0, 100);
  return completeEvent;
}

function appendReceipt(command: string, status: CommandReceipt["status"]) {
  const receipt = {
    id: `rcpt-${randomUUID()}`,
    command,
    status,
    createdAt: new Date().toISOString(),
  } satisfies CommandReceipt;
  cockpitStore.receipts.unshift(receipt);
  cockpitStore.receipts = cockpitStore.receipts.slice(0, 100);
  return receipt;
}

export function listEvents() {
  return cockpitStore.events.slice(0, 100);
}

export function listApprovals() {
  return cockpitStore.approvals.slice(0, 50);
}

export async function getStatus() {
  return getRuntimeStatus();
}

export function pushEvent(event: Omit<CockpitEvent, "id" | "ts">) {
  appendEvent(event);
  persistStore();
}

export function createReceipt(command: string, status: CommandReceipt["status"]): CommandReceipt {
  const receipt = appendReceipt(command, status);
  persistStore();
  return receipt;
}

export function createApproval(command: string, reason: string): Approval {
  const approval = {
    id: `appr-${randomUUID()}`,
    command,
    reason,
    status: "pending",
    createdAt: new Date().toISOString(),
  } satisfies Approval;
  cockpitStore.approvals.unshift(approval);
  cockpitStore.approvals = cockpitStore.approvals.slice(0, 50);
  appendReceipt(command, "requires_approval");
  appendEvent({ level: "warn", source: "iron-gate", message: `Approval required for ${command}.` });
  persistStore();
  return approval;
}

export function resolveApproval(id: string, decision: "approved" | "rejected") {
  const approval = cockpitStore.approvals.find((item) => item.id === id);
  if (!approval || approval.status !== "pending") return null;
  approval.status = decision;
  approval.resolvedAt = new Date().toISOString();
  const receipt = appendReceipt(approval.command, decision);
  appendEvent({
    level: decision === "approved" ? "info" : "warn",
    source: "iron-gate",
    message: `${approval.command} ${decision}; receipt ${receipt.id}.`,
  });
  persistStore();
  return { approval, receipt };
}
