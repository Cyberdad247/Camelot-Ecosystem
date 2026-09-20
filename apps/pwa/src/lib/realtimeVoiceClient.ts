// SPDX-License-Identifier: MIT
/**
 * Realtime Voice Client & Fonoster PBX Telephony Bridge for Camelot-OS PWA.
 * Connects to ws://:8765/v1/realtime (OpenAI Realtime Protocol) and exposes
 * programmable Fonoster call flow verbs (Answer, Say, Gather, Stream, Dial).
 */

export interface RealtimeEvent {
  type: string;
  event_id?: string;
  [key: string]: any;
}

export type GatherSource = 'DTMF' | 'SPEECH' | 'SPEECH_AND_DTMF';
export type StreamDirection = 'IN' | 'OUT' | 'BOTH';
export type StreamAudioFormat = 'PCM16' | 'WAV';

export interface VoiceVerbResult {
  verb: string;
  status: string;
  mediaSessionRef: string;
  data?: Record<string, any>;
}

export class RealtimeVoiceClient {
  private ws: WebSocket | null = null;
  private url: string;
  private mediaSessionRef: string;
  private listeners: Map<string, Array<(event: RealtimeEvent) => void>> = new Map();
  public isConnected: boolean = false;

  constructor(url: string = 'ws://localhost:8765/v1/realtime') {
    this.url = url;
    this.mediaSessionRef = `media_${Math.random().toString(36).substring(2, 11)}`;
  }

  public connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);
        this.ws.onopen = () => {
          this.isConnected = true;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data: RealtimeEvent = JSON.parse(event.data);
            this.dispatch(data.type, data);
            this.dispatch('*', data);
          } catch (e) {
            console.error('[RealtimeVoiceClient] Parse error', e);
          }
        };

        this.ws.onerror = (err) => {
          console.warn('[RealtimeVoiceClient] WebSocket error', err);
          reject(err);
        };

        this.ws.onclose = () => {
          this.isConnected = false;
          this.dispatch('close', { type: 'close' });
        };
      } catch (e) {
        reject(e);
      }
    });
  }

  public disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.isConnected = false;
    }
  }

  public send(event: RealtimeEvent): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error('[RealtimeVoiceClient] WebSocket is not connected');
    }
    this.ws.send(JSON.stringify(event));
  }

  public on(eventType: string, handler: (event: RealtimeEvent) => void): void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, []);
    }
    this.listeners.get(eventType)?.push(handler);
  }

  public off(eventType: string, handler: (event: RealtimeEvent) => void): void {
    const list = this.listeners.get(eventType);
    if (!list) return;
    this.listeners.set(
      eventType,
      list.filter((h) => h !== handler)
    );
  }

  private dispatch(eventType: string, event: RealtimeEvent): void {
    const list = this.listeners.get(eventType);
    if (list) {
      for (const h of list) {
        try {
          h(event);
        } catch (err) {
          console.error(`[RealtimeVoiceClient] Listener error for ${eventType}:`, err);
        }
      }
    }
  }

  // ── OpenAI Realtime Protocol Helpers ─────────────────────────────────────

  public appendAudioBuffer(base64Audio: string): void {
    this.send({
      type: 'input_audio_buffer.append',
      audio: base64Audio,
    });
  }

  public commitAudioBuffer(): void {
    this.send({
      type: 'input_audio_buffer.commit',
    });
  }

  public clearAudioBuffer(): void {
    this.send({
      type: 'input_audio_buffer.clear',
    });
  }

  public updateSession(sessionConfig: Record<string, any>): void {
    this.send({
      type: 'session.update',
      session: sessionConfig,
    });
  }

  public cancelResponse(): void {
    this.send({
      type: 'response.cancel',
    });
  }

  // ── Fonoster PBX Telephony Verbs ─────────────────────────────────────────

  public async answer(): Promise<VoiceVerbResult> {
    this.send({
      type: 'conversation.item.create',
      item: {
        type: 'function_call_output',
        output: JSON.stringify({ verb: 'Answer', mediaSessionRef: this.mediaSessionRef }),
      },
    });
    return { verb: 'Answer', status: 'ok', mediaSessionRef: this.mediaSessionRef };
  }

  public async say(text: string, voice: string = 'alloy'): Promise<VoiceVerbResult> {
    this.send({
      type: 'conversation.item.create',
      item: {
        type: 'message',
        role: 'user',
        content: [{ type: 'input_text', text: `[SAY:${voice}] ${text}` }],
      },
    });
    return {
      verb: 'Say',
      status: 'ok',
      mediaSessionRef: this.mediaSessionRef,
      data: { text, voice },
    };
  }

  public async gather(options: {
    source?: GatherSource;
    maxDigits?: number;
    timeoutMs?: number;
    finishOnKey?: string;
  } = {}): Promise<{ digits: string; speech: string }> {
    const { source = 'SPEECH_AND_DTMF', maxDigits = 1, timeoutMs = 4000, finishOnKey = '#' } = options;
    this.send({
      type: 'conversation.item.create',
      item: {
        type: 'function_call',
        name: 'gather',
        arguments: JSON.stringify({ source, maxDigits, timeoutMs, finishOnKey }),
      },
    });
    return { digits: '', speech: '' };
  }

  public async stream(options: {
    direction?: StreamDirection;
    format?: StreamAudioFormat;
  } = {}): Promise<VoiceVerbResult> {
    const { direction = 'BOTH', format = 'PCM16' } = options;
    return {
      verb: 'Stream',
      status: 'ok',
      mediaSessionRef: this.mediaSessionRef,
      data: { direction, format },
    };
  }

  public async dial(destination: string, timeoutS: number = 60): Promise<VoiceVerbResult> {
    this.send({
      type: 'conversation.item.create',
      item: {
        type: 'function_call',
        name: 'dial',
        arguments: JSON.stringify({ destination, timeoutS }),
      },
    });
    return {
      verb: 'Dial',
      status: 'ok',
      mediaSessionRef: this.mediaSessionRef,
      data: { destination, timeoutS },
    };
  }

  public async hangup(): Promise<VoiceVerbResult> {
    this.send({
      type: 'session.update',
      session: { status: 'hangup' },
    });
    return { verb: 'Hangup', status: 'ok', mediaSessionRef: this.mediaSessionRef };
  }
}
