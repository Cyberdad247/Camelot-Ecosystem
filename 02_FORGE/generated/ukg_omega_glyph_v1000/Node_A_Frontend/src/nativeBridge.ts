export interface NativeBridgeMessage {
  type: 'camelot.intent' | 'camelot.status';
  payload: Record<string, unknown>;
}

export function encodeNativeMessage(message: NativeBridgeMessage): string {
  return JSON.stringify(message);
}

export function decodeNativeMessage(raw: string): NativeBridgeMessage {
  const parsed = JSON.parse(raw) as NativeBridgeMessage;
  if (parsed.type !== 'camelot.intent' && parsed.type !== 'camelot.status') {
    throw new Error(`Unsupported native bridge message: ${parsed.type}`);
  }
  return parsed;
}

export interface NanoSwarmRouterStatus {
  status: string;
  node: string;
  router: string;
  routes: Array<{ target: string; method: string }>;
}

export const DEFAULT_NANO_SWARM_ROUTER_URL = 'http://127.0.0.1:4180';

export async function fetchNanoSwarmStatus(
  routerUrl = DEFAULT_NANO_SWARM_ROUTER_URL,
): Promise<NanoSwarmRouterStatus> {
  const response = await fetch(`${routerUrl}/v1/nano-swarm/status`);
  if (!response.ok) {
    throw new Error(`Nano swarm router status failed: ${response.status}`);
  }
  return response.json() as Promise<NanoSwarmRouterStatus>;
}
