import { useEffect, useRef, useState } from 'react';
import { runtimeConfig } from '@/config/runtime';

/**
 * Payload of an `active_knight` SSE event emitted by control_plane/go_router.
 * Mirrors the struct broadcast in main.go's /rune handler.
 */
export interface ActiveKnightEvent {
  knight: string;
  rune: string;
  status: string;
  node: string;
  ts: string;
}

/**
 * Payload of an `mdx` SSE event emitted by go_router's /plan handler — a
 * markdown "visual plan" to render in the overlay.
 */
export interface PlanEvent {
  title: string;
  knight: string;
  content: string;
  node: string;
  ts: string;
}

const DEFAULT_EVENTS_URL = runtimeConfig.goRouter.eventsUrl;

function parseKnight(raw: string): ActiveKnightEvent | null {
  try {
    const parsed = JSON.parse(raw) as ActiveKnightEvent;
    if (!parsed || typeof parsed !== 'object' || typeof parsed.knight !== 'string') {
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
}

/**
 * Subscribes to the go_router SSE stream (`/events`) and tracks the live
 * active knight. EventSource handles reconnection on its own; we only mirror
 * the connection state. Shaped to match `useAnyaSocket` for consistency.
 */
export function useKnightStream(url: string = DEFAULT_EVENTS_URL) {
  const sourceRef = useRef<EventSource | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [node, setNode] = useState<string | null>(null);
  const [activeKnight, setActiveKnight] = useState<ActiveKnightEvent | null>(null);
  const [history, setHistory] = useState<ActiveKnightEvent[]>([]);
  const [latestPlan, setLatestPlan] = useState<PlanEvent | null>(null);

  useEffect(() => {
    const source = new EventSource(url);
    sourceRef.current = source;

    source.onopen = () => setIsConnected(true);
    source.onerror = () => setIsConnected(false); // EventSource auto-retries

    const onNode = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data) as { node?: string };
        if (data?.node) setNode(data.node);
      } catch {
        /* ignore malformed greeting */
      }
    };

    const onKnight = (event: MessageEvent) => {
      const next = parseKnight(event.data);
      if (!next) return;
      setActiveKnight(next);
      setHistory((current) => [...current.slice(-39), next]);
    };

    const onPlan = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data) as PlanEvent;
        if (data && typeof data.content === 'string') setLatestPlan(data);
      } catch {
        /* ignore malformed plan */
      }
    };

    source.addEventListener('node', onNode as EventListener);
    source.addEventListener('active_knight', onKnight as EventListener);
    source.addEventListener('mdx', onPlan as EventListener);

    return () => {
      source.removeEventListener('node', onNode as EventListener);
      source.removeEventListener('active_knight', onKnight as EventListener);
      source.removeEventListener('mdx', onPlan as EventListener);
      source.close();
      sourceRef.current = null;
    };
  }, [url]);

  return { isConnected, node, activeKnight, history, latestPlan };
}
