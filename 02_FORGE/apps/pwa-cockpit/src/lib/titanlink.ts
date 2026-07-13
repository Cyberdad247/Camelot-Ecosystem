export type TitanLinkCommand = {
  id: string;
  kind: "command" | "approval" | "voice.start" | "voice.stop" | "heartbeat";
  payload?: Record<string, unknown>;
  issuedAt: string;
};

export type TitanLinkEvent = {
  id: string;
  kind: "status" | "log" | "voice.partial" | "voice.final" | "approval.required" | "receipt";
  source: string;
  payload: Record<string, unknown>;
  ts: string;
};

type Listener = (event: TitanLinkEvent) => void;

type TitanLinkOptions = {
  heartbeatMs?: number;
  reconnectMs?: number;
  maxReconnects?: number;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export function parseTitanLinkEvent(value: unknown): TitanLinkEvent {
  if (!isRecord(value)) throw new Error("event must be an object");
  if (typeof value.id !== "string") throw new Error("event.id must be a string");
  if (typeof value.kind !== "string") throw new Error("event.kind must be a string");
  if (typeof value.source !== "string") throw new Error("event.source must be a string");
  if (!isRecord(value.payload)) throw new Error("event.payload must be an object");
  if (typeof value.ts !== "string") throw new Error("event.ts must be a string");

  return value as TitanLinkEvent;
}

export class TitanLinkClient {
  private ws: WebSocket | null = null;
  private listeners = new Set<Listener>();
  private heartbeatHandle: number | null = null;
  private reconnects = 0;
  private readonly heartbeatMs: number;
  private readonly reconnectMs: number;
  private readonly maxReconnects: number;

  constructor(private readonly url: string, options: TitanLinkOptions = {}) {
    this.heartbeatMs = options.heartbeatMs ?? 15000;
    this.reconnectMs = options.reconnectMs ?? 2000;
    this.maxReconnects = options.maxReconnects ?? 10;
  }

  connect() {
    if (this.ws) return;

    this.ws = new WebSocket(this.url);
    this.ws.onopen = () => {
      this.reconnects = 0;
      this.startHeartbeat();
    };
    this.ws.onmessage = (evt) => {
      const parsed = parseTitanLinkEvent(JSON.parse(evt.data as string));
      this.listeners.forEach((listener) => listener(parsed));
    };
    this.ws.onclose = () => {
      this.stopHeartbeat();
      this.ws = null;
      if (this.reconnects >= this.maxReconnects) return;
      this.reconnects += 1;
      window.setTimeout(() => this.connect(), this.reconnectMs);
    };
    this.ws.onerror = () => this.ws?.close();
  }

  disconnect() {
    this.stopHeartbeat();
    this.ws?.close();
    this.ws = null;
  }

  send(command: TitanLinkCommand) {
    if (this.ws?.readyState !== WebSocket.OPEN) {
      throw new Error("TitanLink socket is not open");
    }
    this.ws.send(JSON.stringify(command));
  }

  onEvent(listener: Listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private startHeartbeat() {
    this.stopHeartbeat();
    this.heartbeatHandle = window.setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send({ id: `hb-${Date.now()}`, kind: "heartbeat", issuedAt: new Date().toISOString() });
      }
    }, this.heartbeatMs);
  }

  private stopHeartbeat() {
    if (this.heartbeatHandle !== null) {
      window.clearInterval(this.heartbeatHandle);
      this.heartbeatHandle = null;
    }
  }
}
