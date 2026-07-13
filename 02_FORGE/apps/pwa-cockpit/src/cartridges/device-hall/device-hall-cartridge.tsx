"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { Bell, Fingerprint, Focus, KeyRound, LoaderCircle, RefreshCw, ShieldOff, Smartphone, Vibrate } from "lucide-react";
import type { CartridgeProps } from "../types";
import { capabilitiesFor, type DeviceHallSnapshot, type DevicePlatform, type DeviceSummary } from "@/lib/device-contract";

const emptySnapshot: DeviceHallSnapshot = { devices: [], actions: [] };

function primaryAction(device: DeviceSummary): { capability: string; arguments: Record<string, string | number | boolean>; label: string; Icon: typeof Bell } {
  if (device.platform === "desktop") return { capability: "desktop.notification", arguments: { message: "Anya device link confirmed." }, label: "Notify", Icon: Bell };
  return { capability: "mobile.haptic", arguments: { pattern: "confirm" }, label: "Pulse", Icon: Vibrate };
}

export default function DeviceHallCartridge({ busy }: CartridgeProps) {
  const [snapshot, setSnapshot] = useState<DeviceHallSnapshot>(emptySnapshot);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [name, setName] = useState("");
  const [platform, setPlatform] = useState<DevicePlatform>("desktop");
  const [publicKey, setPublicKey] = useState("");

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch("/api/devices", { cache: "no-store" });
      const data = await response.json() as DeviceHallSnapshot & { message?: string };
      if (!response.ok) throw new Error(data.message ?? "Device Hall could not load.");
      setSnapshot(data);
      setMessage("");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Device Hall could not load.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { void refresh(); }, [refresh]);

  async function enroll(event: FormEvent) {
    event.preventDefault();
    setMessage("");
    const response = await fetch("/api/devices", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, platform, publicKey, capabilities: capabilitiesFor(platform) }),
    });
    const data = await response.json() as { message?: string };
    if (!response.ok) {
      setMessage(data.message ?? "Enrollment failed.");
      return;
    }
    setName("");
    setPublicKey("");
    setMessage("Device enrolled with an explicit capability allowlist.");
    await refresh();
  }

  async function requestAction(device: DeviceSummary, capability: string, actionArguments: Record<string, string | number | boolean>) {
    const response = await fetch(`/api/devices/${encodeURIComponent(device.id)}/actions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ capability, arguments: actionArguments }),
    });
    const data = await response.json() as { message?: string };
    setMessage(response.ok ? `${capability} is awaiting Iron Gate approval.` : data.message ?? "Action request failed.");
    await refresh();
  }

  async function revoke(device: DeviceSummary) {
    const response = await fetch(`/api/devices/${encodeURIComponent(device.id)}`, { method: "DELETE" });
    const data = await response.json() as { message?: string };
    setMessage(response.ok ? `${device.name} revoked.` : data.message ?? "Revocation failed.");
    await refresh();
  }

  const activeDevices = snapshot.devices.filter((device) => !device.revokedAt);

  return (
    <div className="cartridge-view device-hall" data-cartridge="device-hall">
      <section className="metric-strip" aria-label="Device Hall summary">
        <div><Smartphone aria-hidden="true" /><span>Enrolled</span><strong>{activeDevices.length}</strong></div>
        <div><KeyRound aria-hidden="true" /><span>Signed</span><strong>{activeDevices.filter((device) => device.lastSeenAt).length}</strong></div>
        <div><Fingerprint aria-hidden="true" /><span>Awaiting gate</span><strong>{snapshot.actions.filter((action) => action.status === "awaiting_approval").length}</strong></div>
        <div><RefreshCw aria-hidden="true" /><span>Delivered</span><strong>{snapshot.actions.filter((action) => action.status === "completed").length}</strong></div>
      </section>

      <div className="device-hall-grid">
        <section className="surface device-registry" aria-labelledby="device-registry-title">
          <div className="surface-heading"><div><p className="eyebrow">Signed companions</p><h2 id="device-registry-title">Device registry</h2></div><button className="icon-button" type="button" onClick={() => void refresh()} disabled={loading} aria-label="Refresh devices" title="Refresh devices">{loading ? <LoaderCircle className="spin" /> : <RefreshCw />}</button></div>
          <div className="device-list">
            {activeDevices.map((device) => {
              const action = primaryAction(device);
              return (
                <article key={device.id} className="device-row">
                  <div className="device-mark"><Smartphone aria-hidden="true" /></div>
                  <div><strong>{device.name}</strong><small>{device.platform} · {device.fingerprint}</small><p>{device.capabilities.join(" · ")}</p></div>
                  <span className={device.lastSeenAt ? "device-state online" : "device-state"}>{device.lastSeenAt ? "signed" : "enrolled"}</span>
                  <div className="device-actions">
                    <button type="button" onClick={() => void requestAction(device, action.capability, action.arguments)} disabled={busy}><action.Icon aria-hidden="true" /> {action.label}</button>
                    {device.capabilities.includes("desktop.window.focus") ? <button type="button" onClick={() => void requestAction(device, "desktop.window.focus", {})} disabled={busy}><Focus aria-hidden="true" /> Focus</button> : null}
                    <button type="button" className="danger" onClick={() => void revoke(device)} disabled={busy}><ShieldOff aria-hidden="true" /> Revoke</button>
                  </div>
                </article>
              );
            })}
            {!loading && activeDevices.length === 0 ? <p className="empty-state">No signed companion is enrolled.</p> : null}
          </div>
        </section>

        <section className="surface device-enrollment" aria-labelledby="device-enrollment-title">
          <div className="surface-heading"><div><p className="eyebrow">Operator ceremony</p><h2 id="device-enrollment-title">Enroll companion</h2></div><KeyRound /></div>
          <form onSubmit={enroll}>
            <label htmlFor="device-name">Device name</label>
            <input id="device-name" value={name} onChange={(event) => setName(event.target.value)} maxLength={64} required />
            <label htmlFor="device-platform">Platform</label>
            <select id="device-platform" value={platform} onChange={(event) => setPlatform(event.target.value as DevicePlatform)}>
              <option value="desktop">Desktop</option><option value="ios">iOS</option><option value="android">Android</option>
            </select>
            <label htmlFor="device-public-key">Ed25519 public key</label>
            <textarea id="device-public-key" value={publicKey} onChange={(event) => setPublicKey(event.target.value)} rows={6} placeholder="-----BEGIN PUBLIC KEY-----" required />
            <p>{capabilitiesFor(platform).join(" · ")}</p>
            <button type="submit" disabled={busy || name.trim().length === 0 || publicKey.trim().length < 80}><KeyRound aria-hidden="true" /> Enroll with allowlist</button>
          </form>
          {message ? <p className="device-message" role="status">{message}</p> : null}
        </section>

        <section className="surface device-receipts" aria-labelledby="device-receipts-title">
          <div className="surface-heading"><div><p className="eyebrow">Delivery evidence</p><h2 id="device-receipts-title">Recent actions</h2></div><Fingerprint /></div>
          <div className="device-action-list">
            {snapshot.actions.slice(0, 10).map((action) => <div key={action.id}><span className={`action-status status-${action.status}`} /> <strong>{action.capability}</strong><small>{action.status} · attempts {action.attempts}</small><p>{action.result ?? action.id}</p></div>)}
            {!loading && snapshot.actions.length === 0 ? <p className="empty-state">No hardware action has been requested.</p> : null}
          </div>
        </section>
      </div>
    </div>
  );
}
