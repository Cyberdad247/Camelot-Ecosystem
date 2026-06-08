// Client-side wrapper — calls the Next.js Route Handler at /api/infer,
// which spawns the ouroboros binary server-side.

const LATENCY_CEILING_MS = 101;

export interface InferRequest {
  intent:     string;
  state_dim?: number;
}

export interface InferResult {
  ast_json:       string;
  latency_ms:     number;  // wall-clock round-trip to route handler
  engine_latency: number;  // time inside the ouroboros binary
}

export class LatencyError extends Error {
  constructor(public readonly latency: number) {
    super(`[LATENCY_BREACH] ${latency.toFixed(1)}ms exceeds ${LATENCY_CEILING_MS}ms`);
  }
}

export class InferError extends Error {
  constructor(
    public readonly status: number,
    public readonly detail: string,
  ) {
    super(`[INFER:${status}] ${detail}`);
  }
}

export async function dispatchInference(req: InferRequest): Promise<InferResult> {
  const t0 = performance.now();

  const resp = await fetch('/api/infer', {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(req),
  });

  if (!resp.ok) {
    const body = await resp.json().catch(() => ({ error: resp.statusText }));
    throw new InferError(resp.status, body.error ?? resp.statusText);
  }

  const data = await resp.json() as InferResult;
  const latency = performance.now() - t0;

  if (latency > LATENCY_CEILING_MS) {
    throw new LatencyError(latency);
  }

  return { ...data, latency_ms: latency };
}
