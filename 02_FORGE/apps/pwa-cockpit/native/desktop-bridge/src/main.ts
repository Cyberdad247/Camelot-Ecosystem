import { invoke } from "@tauri-apps/api/core";

type Identity = { publicKey: string; fingerprint: string; capabilities: string[] };
type BridgeTick = { connected: boolean; actionId?: string; result: string };

const byId = <T extends HTMLElement>(id: string) => document.getElementById(id) as T;
let timer: number | null = null;

async function tick() {
  const endpoint = byId<HTMLInputElement>("endpoint").value.trim();
  const deviceId = byId<HTMLInputElement>("device-id").value.trim();
  const result = byId<HTMLOutputElement>("result");
  result.textContent = "Signing queue request...";
  try {
    const response = await invoke<BridgeTick>("bridge_tick", { endpoint, deviceId });
    result.textContent = response.actionId ? `${response.actionId}: ${response.result}` : response.result;
    byId("state-dot").classList.add("online");
    localStorage.setItem("camelot.endpoint", endpoint);
    localStorage.setItem("camelot.deviceId", deviceId);
  } catch (error) {
    result.textContent = String(error);
    byId("state-dot").classList.remove("online");
  }
}

window.addEventListener("DOMContentLoaded", async () => {
  const identity = await invoke<Identity>("device_identity");
  byId("fingerprint").textContent = identity.fingerprint;
  byId<HTMLTextAreaElement>("public-key").value = identity.publicKey;
  byId<HTMLInputElement>("endpoint").value = localStorage.getItem("camelot.endpoint") ?? "https://cybertronia.tailcd0c29.ts.net";
  byId<HTMLInputElement>("device-id").value = localStorage.getItem("camelot.deviceId") ?? "";
  byId("copy-key").addEventListener("click", () => void navigator.clipboard.writeText(identity.publicKey));
  byId("connect").addEventListener("click", () => void tick());
  byId<HTMLInputElement>("continuous").addEventListener("change", (event) => {
    if (timer !== null) window.clearInterval(timer);
    timer = (event.currentTarget as HTMLInputElement).checked ? window.setInterval(() => void tick(), 10_000) : null;
    if (timer !== null) void tick();
  });
});
