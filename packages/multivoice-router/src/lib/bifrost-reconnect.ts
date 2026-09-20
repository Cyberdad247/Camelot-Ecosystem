// SPDX-License-Identifier: MIT
/**
 * Bifrost WebSocket Heartbeat & Resilient Reconnection Manager
 * ============================================================
 * Implements full-jitter exponential backoff, keepalive ping/pong frames (15s),
 * and transparent in-flight message buffering for Multivoice & Bifrost UI.
 */

export interface ReconnectConfig {
  baseDelayMs?: number;
  maxDelayMs?: number;
  maxRetries?: number;
  pingIntervalMs?: number;
  pongTimeoutMs?: number;
}

export type ConnectionState = 'DISCONNECTED' | 'CONNECTING' | 'CONNECTED' | 'RECONNECTING';

export class BifrostReconnectManager {
  private url: string;
  private ws: WebSocket | null = null;
  private state: ConnectionState = 'DISCONNECTED';
  private retryCount = 0;
  private reconnectTimer: any = null;
  private pingTimer: any = null;
  private pongTimer: any = null;
  private messageQueue: string[] = [];
  
  private baseDelayMs: number;
  private maxDelayMs: number;
  private maxRetries: number;
  private pingIntervalMs: number;
  private pongTimeoutMs: number;

  public onOpen?: () => void;
  public onClose?: (code: number, reason: string) => void;
  public onMessage?: (data: any) => void;
  public onError?: (error: any) => void;
  public onStateChange?: (state: ConnectionState) => void;
  public onReconnected?: () => void;

  constructor(url: string, config: ReconnectConfig = {}) {
    this.url = url;
    this.baseDelayMs = config.baseDelayMs ?? 500;
    this.maxDelayMs = config.maxDelayMs ?? 8000;
    this.maxRetries = config.maxRetries ?? 10;
    this.pingIntervalMs = config.pingIntervalMs ?? 15000;
    this.pongTimeoutMs = config.pongTimeoutMs ?? 5000;
  }

  public connect(): void {
    if (this.state === 'CONNECTED' || this.state === 'CONNECTING') return;

    this.setState(this.retryCount > 0 ? 'RECONNECTING' : 'CONNECTING');
    try {
      this.ws = new WebSocket(this.url);
      this.setupHandlers();
    } catch (err) {
      this.handleDisconnect();
    }
  }

  private setupHandlers(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      this.setState('CONNECTED');
      const wasReconnecting = this.retryCount > 0;
      this.retryCount = 0;
      this.startHeartbeat();
      this.flushQueue();
      this.onOpen?.();
      if (wasReconnecting) {
        this.onReconnected?.();
      }
    };

    this.ws.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data);
        if (parsed.type === 'pong' || parsed.type === 'HEARTBEAT_ACK') {
          this.clearPongTimeout();
          return;
        }
      } catch {
        // Raw message, forward to caller
      }
      this.onMessage?.(event.data);
    };

    this.ws.onclose = (event) => {
      this.cleanup();
      this.onClose?.(event.code, event.reason);
      this.handleDisconnect();
    };

    this.ws.onerror = (error) => {
      this.onError?.(error);
    };
  }

  public send(data: string | object): boolean {
    const payload = typeof data === 'string' ? data : JSON.stringify(data);
    if (this.state === 'CONNECTED' && this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(payload);
      return true;
    }
    // Buffer in-flight message during network drop
    this.messageQueue.push(payload);
    return false;
  }

  private flushQueue(): void {
    while (this.messageQueue.length > 0 && this.ws && this.ws.readyState === WebSocket.OPEN) {
      const msg = this.messageQueue.shift();
      if (msg) this.ws.send(msg);
    }
  }

  private handleDisconnect(): void {
    this.setState('DISCONNECTED');
    if (this.retryCount >= this.maxRetries) {
      return;
    }

    this.retryCount++;
    // Full jitter exponential backoff: sleep = rand(0, min(maxDelay, base * 2^attempt))
    const expDelay = Math.min(this.maxDelayMs, this.baseDelayMs * Math.pow(2, this.retryCount - 1));
    const jitterDelay = Math.floor(Math.random() * expDelay);

    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, jitterDelay);
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();
    this.pingTimer = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }));
        this.pongTimer = setTimeout(() => {
          // Pong timed out, force socket teardown to trigger reconnect
          this.ws?.close();
        }, this.pongTimeoutMs);
      }
    }, this.pingIntervalMs);
  }

  private clearPongTimeout(): void {
    if (this.pongTimer) {
      clearTimeout(this.pongTimer);
      this.pongTimer = null;
    }
  }

  private stopHeartbeat(): void {
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
    this.clearPongTimeout();
  }

  private cleanup(): void {
    this.stopHeartbeat();
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  public disconnect(): void {
    this.cleanup();
    this.retryCount = this.maxRetries; // Prevent auto-reconnect on explicit disconnect
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.setState('DISCONNECTED');
  }

  public getState(): ConnectionState {
    return this.state;
  }

  private setState(state: ConnectionState): void {
    if (this.state !== state) {
      this.state = state;
      this.onStateChange?.(state);
    }
  }
}
