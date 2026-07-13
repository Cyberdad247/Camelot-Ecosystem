export type DevicePlatform = "desktop" | "ios" | "android";

export const deviceCapabilityCatalog = {
  desktop: ["system.status", "desktop.notification", "desktop.window.focus"],
  ios: ["system.status", "mobile.haptic", "mobile.notification", "mobile.intent.open"],
  android: ["system.status", "mobile.haptic", "mobile.notification", "mobile.intent.open"],
} as const satisfies Record<DevicePlatform, readonly string[]>;

export type DeviceActionStatus = "awaiting_approval" | "queued" | "delivered" | "completed" | "failed" | "rejected";

export type DeviceSummary = {
  id: string;
  name: string;
  platform: DevicePlatform;
  capabilities: string[];
  fingerprint: string;
  createdAt: string;
  lastSeenAt?: string;
  revokedAt?: string;
};

export type DeviceAction = {
  id: string;
  deviceId: string;
  capability: string;
  arguments: Record<string, string | number | boolean>;
  status: DeviceActionStatus;
  createdAt: string;
  updatedAt: string;
  attempts: number;
  result?: string;
};

export type DeviceHallSnapshot = {
  devices: DeviceSummary[];
  actions: DeviceAction[];
};

export function capabilitiesFor(platform: DevicePlatform) {
  return [...deviceCapabilityCatalog[platform]];
}
