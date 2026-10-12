// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
import {
  type TitanLinkCommand,
  type TitanLinkEvent,
  TitanLinkEventSchema,
} from '@camelot/anya-domain';

type Listener = (event: TitanLinkEvent) => void;

export class TitanLinkClient {
  private ws: WebSocket | null = null;
  private listeners = new Set<Listener>();
  private url: string;
  private heartbeatInterval: any;

  constructor(url: string) {
    this.url = url; // e.g. wss://lukas-tailnet:8443/titanlink
  }

  connect() {
    if (this.ws) return;

    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      console.log('[TITANLINK] Connected to Kernel');
      this.startHeartbeat();
    };

    this.ws.onmessage = (evt) => {
      try {
        const raw = JSON.parse(evt.data);
        const parsed = TitanLinkEventSchema.parse(raw);
        this.listeners.forEach((fn) => fn(parsed));
      } catch (err) {
        console.warn('[TITANLINK] Parse error', err);
      }
    };

    this.ws.onclose = () => {
      console.log('[TITANLINK] Disconnected. Reconnecting...');
      this.stopHeartbeat();
      this.ws = null;
      setTimeout(() => this.connect(), 2000); // simple backoff
    };

    this.ws.onerror = (err) => {
      console.error('[TITANLINK] WS Error', err);
      this.ws?.close();
    };
  }

  private startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ kind: 'heartbeat' }));
      }
    }, 15000);
  }

  private stopHeartbeat() {
    if (this.heartbeatInterval) clearInterval(this.heartbeatInterval);
  }

  send(command: TitanLinkCommand) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(command));
    } else {
      console.warn('[TITANLINK] Cannot send, WS not open');
    }
  }

  onEvent(listener: Listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }
}
