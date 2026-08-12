import { useState, useEffect, useRef, useCallback } from 'react';

export type BifrostConnectionStatus = 'CONNECTED' | 'OFFLINE' | 'CONNECTING';

export interface BifrostIntentPayload {
  action: string;
  tenant_id: string;
  data: Record<string, unknown>;
  timestamp: number;
}

export function useBifrost(endpoint?: string) {
  const [connectionStatus, setConnectionStatus] = useState<BifrostConnectionStatus>('CONNECTING');
  const socketRef = useRef<WebSocket | null>(null);

  const targetWsUrl = endpoint || process.env.NEXT_PUBLIC_BIFROST_WS || 'ws://100.71.218.75:4433/ws/bifrost';

  useEffect(() => {
    let isMounted = true;
    let reconnectTimeout: NodeJS.Timeout;

    const connectWebSocket = () => {
      if (!isMounted) return;
      setConnectionStatus('CONNECTING');

      try {
        const ws = new WebSocket(targetWsUrl);
        socketRef.current = ws;

        ws.onopen = () => {
          if (isMounted) {
            setConnectionStatus('CONNECTED');
            console.log('[BIFROST_WS] Mesh connection established ->', targetWsUrl);
          }
        };

        ws.onclose = () => {
          if (isMounted) {
            setConnectionStatus('OFFLINE');
            console.warn('[BIFROST_WS] Mesh connection lost. Reconnecting in 3s...');
            reconnectTimeout = setTimeout(connectWebSocket, 3000);
          }
        };

        ws.onerror = (err) => {
          if (isMounted) {
            setConnectionStatus('OFFLINE');
            console.error('[BIFROST_WS_ERROR]', err);
          }
        };
      } catch (err) {
        if (isMounted) {
          setConnectionStatus('OFFLINE');
        }
      }
    };

    connectWebSocket();

    return () => {
      isMounted = false;
      clearTimeout(reconnectTimeout);
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [targetWsUrl]);

  const sendIntent = useCallback((intent: BifrostIntentPayload) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify(intent));
      return true;
    } else {
      console.warn('[BIFROST_WS_WARN] Cannot send intent - WebSocket is OFFLINE');
      return false;
    }
  }, []);

  return {
    connectionStatus,
    sendIntent,
  };
}
