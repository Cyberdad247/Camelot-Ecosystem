// Copyright (c) 2026 Invisioned Marketing Inc. All rights reserved.
// Camelot Apex OS — CONFIDENTIAL AND PROPRIETARY
/**
 * TitanLink Client (v1.0)
 * Handles WebSocket connection to Camelot Kernel over Tailscale.
 */

export type Listener = (msg: any) => void;

export class TitanLinkClient {
  private ws: WebSocket | null = null;
  private url: string;
  private listeners: Set<Listener> = new Set();
  private reconnectAttempts = 0;
  private maxBackoff = 30000; // 30 seconds

  constructor(url = 'ws://100.64.0.1:18788') {
    // Example Tailscale IP
    this.url = url;
  }

  connect() {
    console.log(`[TITANLINK] Connecting to ${this.url}...`);
    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      console.log('[TITANLINK] Connected.');
      this.reconnectAttempts = 0;
      this.startHeartbeat();
    };

    this.ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        this.listeners.forEach((l) => l(msg));
      } catch (e) {
        console.error('[TITANLINK] Parse Error:', e);
      }
    };

    this.ws.onclose = () => {
      console.log('[TITANLINK] Connection closed.');
      this.handleReconnect();
    };

    this.ws.onerror = (err) => {
      console.error('[TITANLINK] WebSocket Error:', err);
    };
  }

  private handleReconnect() {
    this.reconnectAttempts++;
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), this.maxBackoff);
    console.log(`[TITANLINK] Reconnecting in ${delay}ms...`);
    setTimeout(() => this.connect(), delay);
  }

  private startHeartbeat() {
    setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send({
          kind: 'heartbeat',
          payload: { timestamp: new Date().toISOString() },
        });
      }
    }, 30000); // 30s heartbeat
  }

  send(message: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          id: Math.random().toString(36).substring(7),
          timestamp: new Date().toISOString(),
          version: 'v1.0',
          ...message,
        }),
      );
    } else {
      console.warn('[TITANLINK] Send failed: Socket not open.');
    }
  }

  addListener(listener: Listener) {
    this.listeners.add(listener);
  }

  removeListener(listener: Listener) {
    this.listeners.delete(listener);
  }
}
