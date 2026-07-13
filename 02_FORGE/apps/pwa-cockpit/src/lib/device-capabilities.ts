export type DeviceCapability = {
  id: "voice" | "vision" | "haptics" | "wake-lock" | "native-bridge";
  label: string;
  available: boolean;
  boundary: "browser" | "native-gated";
};

type WakeLockSentinelLike = {
  released: boolean;
  release(): Promise<void>;
};

type NavigatorWithDeviceApis = Navigator & {
  vibrate?: (pattern: number | number[]) => boolean;
  wakeLock?: { request(type: "screen"): Promise<WakeLockSentinelLike> };
};

export function detectDeviceCapabilities(): DeviceCapability[] {
  if (typeof window === "undefined") return [];
  const deviceNavigator = navigator as NavigatorWithDeviceApis;
  const recognition = "SpeechRecognition" in window || "webkitSpeechRecognition" in window;

  return [
    { id: "voice", label: "Voice", available: recognition, boundary: "browser" },
    { id: "vision", label: "Vision", available: Boolean(navigator.mediaDevices?.getUserMedia), boundary: "browser" },
    { id: "haptics", label: "Haptics", available: typeof deviceNavigator.vibrate === "function", boundary: "browser" },
    { id: "wake-lock", label: "Wake", available: Boolean(deviceNavigator.wakeLock), boundary: "browser" },
    { id: "native-bridge", label: "Device", available: false, boundary: "native-gated" },
  ];
}

export function pulseDevice() {
  const deviceNavigator = navigator as NavigatorWithDeviceApis;
  return deviceNavigator.vibrate?.([24, 30, 44]) ?? false;
}

export async function requestScreenWakeLock() {
  const deviceNavigator = navigator as NavigatorWithDeviceApis;
  if (!deviceNavigator.wakeLock) return null;
  return deviceNavigator.wakeLock.request("screen");
}

export type { WakeLockSentinelLike };
