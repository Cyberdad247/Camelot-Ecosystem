// CamelotClient — the ONLY path from a Kickbox surface into Camelot.
//
// Boundary enforcement (ADR-001): the PWA never calls a tool or node-agent
// directly. This client therefore exposes exactly the governed endpoint
// surface and nothing else — no generic request escape hatch, no tool
// invocation method. The allow-list below is frozen and checked at call time;
// tests assert both properties (client-guard.test.ts).

import type {
  BargeInResponse,
  CamelotTurnResponse,
  ConfirmationRequest,
  ConfirmationResponse,
  AuditEvent,
  HealthResponse,
  SessionEvent,
  VoiceBargeIn,
  VoiceTurn,
} from './types.js';

/** The complete governed HTTP surface. Frozen — additions require an ADR. */
export const ALLOWED_PATHS = Object.freeze([
  '/v1/voice/turns',
  '/v1/voice/barge-in',
  '/v1/confirmations',
  '/v1/audit/',
  '/healthz',
] as const);

export class BoundaryViolationError extends Error {
  constructor(path: string) {
    super(
      `Boundary violation: "${path}" is not part of the governed Camelot surface. ` +
        'The PWA must never call tools or node agents directly (ADR-001).',
    );
    this.name = 'BoundaryViolationError';
  }
}

export interface CamelotClientOptions {
  /** Gateway origin, e.g. "http://localhost:8788". */
  baseUrl: string;
  /** Injectable for tests; defaults to global fetch. */
  fetchImpl?: typeof fetch;
  /** Injectable for tests; defaults to global WebSocket. */
  webSocketImpl?: typeof WebSocket;
}

export class CamelotClient {
  readonly #baseUrl: string;
  readonly #fetch: typeof fetch;
  readonly #WebSocket: typeof WebSocket | undefined;

  constructor(options: CamelotClientOptions) {
    this.#baseUrl = options.baseUrl.replace(/\/+$/, '');
    // Bind the global fetch: an unbound reference throws "Illegal invocation"
    // in browsers when called with a non-window `this`.
    this.#fetch = options.fetchImpl ?? ((...args: Parameters<typeof fetch>) => fetch(...args));
    this.#WebSocket =
      options.webSocketImpl ?? (typeof WebSocket !== 'undefined' ? WebSocket : undefined);
    Object.freeze(this);
  }

  async submitTurn(turn: VoiceTurn): Promise<CamelotTurnResponse> {
    return this.#post('/v1/voice/turns', turn);
  }

  async bargeIn(event: VoiceBargeIn): Promise<BargeInResponse> {
    return this.#post('/v1/voice/barge-in', event);
  }

  async confirm(request: ConfirmationRequest): Promise<ConfirmationResponse> {
    return this.#post('/v1/confirmations', request);
  }

  async getAudit(auditId: string): Promise<AuditEvent> {
    return this.#get(`/v1/audit/${encodeURIComponent(auditId)}`);
  }

  async health(): Promise<HealthResponse> {
    return this.#get('/healthz');
  }

  /** Open the session-events WebSocket. Returns a close function. */
  connectEvents(sessionId: string, onEvent: (event: SessionEvent) => void): () => void {
    if (!this.#WebSocket) {
      throw new Error('No WebSocket implementation available');
    }
    const wsBase = this.#baseUrl.replace(/^http/, 'ws');
    const socket = new this.#WebSocket(
      `${wsBase}/v1/sessions/${encodeURIComponent(sessionId)}/events`,
    );
    socket.onmessage = (msg: MessageEvent) => {
      onEvent(JSON.parse(String(msg.data)) as SessionEvent);
    };
    return () => socket.close();
  }

  #guard(path: string): void {
    const ok = ALLOWED_PATHS.some((allowed) =>
      allowed.endsWith('/') ? path.startsWith(allowed) : path === allowed,
    );
    if (!ok) throw new BoundaryViolationError(path);
  }

  async #post<T>(path: string, body: unknown): Promise<T> {
    this.#guard(path);
    const res = await this.#fetch(`${this.#baseUrl}${path}`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`${path} -> HTTP ${res.status}: ${text}`);
    }
    return (await res.json()) as T;
  }

  async #get<T>(path: string): Promise<T> {
    this.#guard(path);
    const res = await this.#fetch(`${this.#baseUrl}${path}`);
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`${path} -> HTTP ${res.status}: ${text}`);
    }
    return (await res.json()) as T;
  }
}
