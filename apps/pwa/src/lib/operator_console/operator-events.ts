// SPDX-License-Identifier: MIT

'use client';

import { type OperatorTaskSnapshot, OperatorTaskSnapshotSchema } from './schemas';

const BFF_BASE = process.env.NEXT_PUBLIC_BIFROST_HTTP_URL ?? 'http://localhost:3001';

/**
 * SSE subscription to the operator BFF event stream. Returns an unsubscribe
 * function. Reconnects on error with a 2s backoff (bounded to 5 attempts).
 */
export function subscribe(
  taskId: string,
  onSnapshot: (s: OperatorTaskSnapshot) => void,
): () => void {
  let closed = false;
  let es: EventSource | null = null;
  let attempts = 0;
  let timer: ReturnType<typeof setTimeout> | undefined;

  const connect = () => {
    if (closed || attempts >= 5) return;
    attempts += 1;
    es = new EventSource(`${BFF_BASE}/v1/operator/tasks/${taskId}/events`);
    es.onmessage = (event: MessageEvent<string>) => {
      try {
        const msg = JSON.parse(event.data) as { type?: string; payload?: unknown };
        if (msg.type === 'snapshot') {
          onSnapshot(OperatorTaskSnapshotSchema.parse(msg.payload));
        }
      } catch {
        // Ignore malformed frames; never fabricate state (design §18).
      }
    };
    es.onerror = () => {
      es?.close();
      es = null;
      timer = setTimeout(connect, 2000);
    };
  };

  connect();
  return () => {
    closed = true;
    if (timer) clearTimeout(timer);
    es?.close();
    es = null;
  };
}
