import type { CockpitStatus } from "./cockpit-types";

const DB_NAME = "camelot-anya-cockpit";
const STORE_NAME = "snapshots";
const DB_VERSION = 1;
const SNAPSHOT_KEY = "latest";

export type OfflineSnapshot = {
  status: CockpitStatus;
  cachedAt: string;
};

function sanitizeStatus(status: CockpitStatus): CockpitStatus {
  return {
    ...status,
    lastCommand: {},
    warnings: [...status.warnings.filter((warning) => !warning.toLowerCase().includes("command")), "Offline snapshot contains status only."],
  };
}

function openDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) db.createObjectStore(STORE_NAME);
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

export async function saveOfflineSnapshot(snapshot: OfflineSnapshot) {
  if (typeof indexedDB === "undefined") return;
  const db = await openDb();
  await new Promise<void>((resolve, reject) => {
    const transaction = db.transaction(STORE_NAME, "readwrite");
    transaction.objectStore(STORE_NAME).put({ ...snapshot, status: sanitizeStatus(snapshot.status) }, SNAPSHOT_KEY);
    transaction.oncomplete = () => resolve();
    transaction.onerror = () => reject(transaction.error);
  });
  db.close();
}

export async function readOfflineSnapshot(): Promise<OfflineSnapshot | null> {
  if (typeof indexedDB === "undefined") return null;
  const db = await openDb();
  const snapshot = await new Promise<OfflineSnapshot | null>((resolve, reject) => {
    const request = db.transaction(STORE_NAME, "readonly").objectStore(STORE_NAME).get(SNAPSHOT_KEY);
    request.onsuccess = () => resolve((request.result as OfflineSnapshot | undefined) ?? null);
    request.onerror = () => reject(request.error);
  });
  db.close();
  return snapshot;
}
