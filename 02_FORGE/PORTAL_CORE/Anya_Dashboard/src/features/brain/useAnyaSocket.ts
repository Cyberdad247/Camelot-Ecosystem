import { useEffect, useMemo, useRef, useState } from 'react';
import { runtimeConfig } from '@/config/runtime';
import { bifrostWebSocketUrl } from '@/lib/bifrostClient';

export interface AnyaSocketEvent {
  event: string;
  source?: string;
  intent?: string;
  detail?: string;
  timestamp_ms?: number;
}

const DEFAULT_WS_URL = bifrostWebSocketUrl(runtimeConfig.bifrost.websocketUrl);

function parseEvent(raw: string): AnyaSocketEvent | null {
  try {
    const parsed = JSON.parse(raw) as AnyaSocketEvent;
    if (!parsed || typeof parsed !== 'object' || typeof parsed.event !== 'string') {
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
}

export function useAnyaSocket(url: string = DEFAULT_WS_URL) {
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectRef = useRef<number | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [events, setEvents] = useState<AnyaSocketEvent[]>([]);

  useEffect(() => {
    let closedByReact = false;
    let attempt = 0;

    function connect() {
      const socket = new WebSocket(url);
      socketRef.current = socket;

      socket.addEventListener('open', () => {
        attempt = 0;
        setIsConnected(true);
      });

      socket.addEventListener('close', () => {
        setIsConnected(false);
        if (closedByReact) return;
        const delay = Math.min(1000 * 2 ** attempt, 10000);
        attempt += 1;
        reconnectRef.current = window.setTimeout(connect, delay);
      });

      socket.addEventListener('error', () => {
        setIsConnected(false);
        socket.close();
      });

      socket.addEventListener('message', (message) => {
        if (typeof message.data !== 'string') {
          return;
        }
        const next = parseEvent(message.data);
        if (!next) {
          return;
        }
        setEvents((current) => [...current.slice(-39), next]);
      });
    }

    connect();

    return () => {
      closedByReact = true;
      if (reconnectRef.current) {
        window.clearTimeout(reconnectRef.current);
        reconnectRef.current = null;
      }
      socketRef.current?.close();
      socketRef.current = null;
    };
  }, [url]);

  const latestEvent = useMemo(
    () => (events.length > 0 ? events[events.length - 1] : null),
    [events],
  );

  return {
    isConnected,
    events,
    latestEvent,
  };
}
