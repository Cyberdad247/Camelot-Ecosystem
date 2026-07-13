import { Capacitor } from "@capacitor/core";
import { Haptics, NotificationType } from "@capacitor/haptics";
import { LocalNotifications } from "@capacitor/local-notifications";
import { AppLauncher } from "@capacitor/app-launcher";
import "./style.css";

type DeviceAction = { id: string; capability: string; arguments: Record<string, string | number | boolean> };
type PollResponse = { action: DeviceAction | null };
const encoder = new TextEncoder();
const byId = <T extends HTMLElement>(id: string) => document.getElementById(id) as T;
let timer: number | null = null;

function base64Url(bytes: ArrayBuffer | Uint8Array) {
  const values = bytes instanceof Uint8Array ? bytes : new Uint8Array(bytes);
  let binary = "";
  values.forEach((value) => { binary += String.fromCharCode(value); });
  return btoa(binary).replaceAll("+", "-").replaceAll("/", "_").replaceAll("=", "");
}

async function database() {
  return new Promise<IDBDatabase>((resolve, reject) => {
    const request = indexedDB.open("camelot-device-bridge", 1);
    request.onupgradeneeded = () => request.result.createObjectStore("identity");
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

async function identity() {
  const db = await database();
  const existing = await new Promise<CryptoKeyPair | undefined>((resolve, reject) => {
    const request = db.transaction("identity").objectStore("identity").get("ed25519");
    request.onsuccess = () => resolve(request.result as CryptoKeyPair | undefined);
    request.onerror = () => reject(request.error);
  });
  const keys = existing ?? await crypto.subtle.generateKey({ name: "Ed25519" }, false, ["sign", "verify"]);
  if (!existing) await new Promise<void>((resolve, reject) => {
    const request = db.transaction("identity", "readwrite").objectStore("identity").put(keys, "ed25519");
    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
  });
  const spki = await crypto.subtle.exportKey("spki", keys.publicKey);
  const encoded = btoa(String.fromCharCode(...new Uint8Array(spki))).match(/.{1,64}/g)?.join("\n") ?? "";
  const publicKey = `-----BEGIN PUBLIC KEY-----\n${encoded}\n-----END PUBLIC KEY-----\n`;
  const hash = await crypto.subtle.digest("SHA-256", spki);
  return { keys, publicKey, fingerprint: [...new Uint8Array(hash)].slice(0, 12).map((value) => value.toString(16).padStart(2, "0")).join("") };
}

function checkedEndpoint(value: string) {
  const url = new URL(value);
  const loopback = ["127.0.0.1", "localhost", "::1"].includes(url.hostname);
  if (url.protocol !== "https:" && !(url.protocol === "http:" && loopback)) throw new Error("HTTPS is required outside loopback development.");
  return url;
}

async function signedHeaders(method: string, path: string, body: string, deviceId: string, privateKey: CryptoKey) {
  const timestamp = Date.now().toString();
  const nonce = base64Url(crypto.getRandomValues(new Uint8Array(18)));
  const digest = [...new Uint8Array(await crypto.subtle.digest("SHA-256", encoder.encode(body)))].map((value) => value.toString(16).padStart(2, "0")).join("");
  const canonical = [method, path, timestamp, nonce, digest].join("\n");
  const signature = base64Url(await crypto.subtle.sign("Ed25519", privateKey, encoder.encode(canonical)));
  return { "x-camelot-device-id": deviceId, "x-camelot-timestamp": timestamp, "x-camelot-nonce": nonce, "x-camelot-signature": signature };
}

async function execute(action: DeviceAction) {
  if (action.capability === "system.status") return `${Capacitor.getPlatform()} native bridge online`;
  if (action.capability === "mobile.haptic") {
    await Haptics.notification({ type: NotificationType.Success });
    return "Native confirmation haptic completed.";
  }
  if (action.capability === "mobile.notification") {
    const permission = await LocalNotifications.requestPermissions();
    if (permission.display !== "granted") throw new Error("Notification permission denied.");
    const body = String(action.arguments.message ?? "Anya device action received.").slice(0, 200);
    await LocalNotifications.schedule({ notifications: [{ id: Date.now() % 2_147_483_647, title: "Camelot-OS - Anya", body, schedule: { at: new Date(Date.now() + 250) } }] });
    return "Local notification scheduled.";
  }
  if (action.capability === "mobile.intent.open") {
    const target = String(action.arguments.target ?? "");
    if (!target.startsWith("https://cybertronia.tailcd0c29.ts.net") && target !== "app-settings:") throw new Error("Intent target is outside the mobile allowlist.");
    const available = await AppLauncher.canOpenUrl({ url: target });
    if (!available.value) throw new Error("Approved intent is unavailable on this device.");
    await AppLauncher.openUrl({ url: target });
    return "Approved mobile intent opened.";
  }
  throw new Error("Capability is not implemented by the mobile allowlist.");
}

async function tick(keys: CryptoKeyPair) {
  const endpoint = checkedEndpoint(byId<HTMLInputElement>("endpoint").value.trim());
  const deviceId = byId<HTMLInputElement>("device-id").value.trim();
  if (!deviceId.startsWith("dev-")) throw new Error("Enter the enrolled dev- identifier.");
  const pollPath = "/api/device-bridge/poll";
  const poll = await fetch(new URL(pollPath, endpoint), { headers: await signedHeaders("GET", pollPath, "", deviceId, keys.privateKey) });
  if (!poll.ok) throw new Error(`Cockpit rejected poll with HTTP ${poll.status}.`);
  const action = (await poll.json() as PollResponse).action;
  if (!action) return "No approved action is queued.";
  let success = true;
  let result = "";
  try { result = await execute(action); } catch (error) { success = false; result = error instanceof Error ? error.message : String(error); }
  const body = JSON.stringify({ actionId: action.id, success, result });
  const receiptPath = "/api/device-bridge/receipt";
  const receipt = await fetch(new URL(receiptPath, endpoint), { method: "POST", headers: { "Content-Type": "application/json", ...await signedHeaders("POST", receiptPath, body, deviceId, keys.privateKey) }, body });
  if (!receipt.ok) throw new Error(`Cockpit rejected receipt with HTTP ${receipt.status}.`);
  return `${action.id}: ${result}`;
}

window.addEventListener("DOMContentLoaded", async () => {
  const currentIdentity = await identity();
  byId("fingerprint").textContent = currentIdentity.fingerprint;
  byId<HTMLTextAreaElement>("public-key").value = currentIdentity.publicKey;
  byId<HTMLInputElement>("endpoint").value = localStorage.getItem("camelot.endpoint") ?? "https://cybertronia.tailcd0c29.ts.net";
  byId<HTMLInputElement>("device-id").value = localStorage.getItem("camelot.deviceId") ?? "";
  byId("copy-key").addEventListener("click", () => void navigator.clipboard.writeText(currentIdentity.publicKey));
  const run = async () => {
    const output = byId<HTMLOutputElement>("result");
    output.textContent = "Signing queue request...";
    try {
      output.textContent = await tick(currentIdentity.keys);
      byId("state-dot").classList.add("online");
      localStorage.setItem("camelot.endpoint", byId<HTMLInputElement>("endpoint").value.trim());
      localStorage.setItem("camelot.deviceId", byId<HTMLInputElement>("device-id").value.trim());
    } catch (error) {
      output.textContent = error instanceof Error ? error.message : String(error);
      byId("state-dot").classList.remove("online");
    }
  };
  byId("connect").addEventListener("click", () => void run());
  byId<HTMLInputElement>("continuous").addEventListener("change", (event) => {
    if (timer !== null) window.clearInterval(timer);
    timer = (event.currentTarget as HTMLInputElement).checked ? window.setInterval(() => void run(), 10_000) : null;
    if (timer !== null) void run();
  });
});
