import React, { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import type { ServiceHealth } from '@/types/camelot';

interface StatusDotProps {
  service: ServiceHealth;
  showLabel?: boolean;
  className?: string;
}

async function ping(url: string): Promise<{ ok: boolean; latency_ms: number }> {
  const start = performance.now();
  try {
    const res = await fetch(url, { method: 'GET', signal: AbortSignal.timeout(3000) });
    return { ok: res.ok, latency_ms: Math.round(performance.now() - start) };
  } catch {
    return { ok: false, latency_ms: 0 };
  }
}

export function StatusDot({ service, showLabel = false, className }: StatusDotProps) {
  const [health, setHealth] = useState<ServiceHealth>(service);

  useEffect(() => {
    let cancelled = false;
    async function check() {
      setHealth((s) => ({ ...s, status: 'checking' }));
      const { ok, latency_ms } = await ping(service.healthUrl);
      if (!cancelled) {
        setHealth((s) => ({ ...s, status: ok ? 'live' : 'dark', latency_ms, last_checked: Date.now() }));
      }
    }
    check();
    const id = setInterval(check, 30_000);
    return () => { cancelled = true; clearInterval(id); };
  }, [service.healthUrl]);

  const dot = health.status === 'live'
    ? 'bg-emerald-400 shadow-[0_0_6px_#34d399]'
    : health.status === 'checking'
    ? 'bg-amber-400 animate-pulse'
    : 'bg-red-600';

  return (
    <span className={cn('inline-flex items-center gap-1.5', className)}>
      <span className={cn('h-2 w-2 rounded-full', dot)} />
      {showLabel && (
        <span className="text-xs text-slate-400">
          {health.label}
          {health.status === 'live' && health.latency_ms != null && (
            <span className="ml-1 text-slate-600">{health.latency_ms}ms</span>
          )}
        </span>
      )}
    </span>
  );
}

export const SERVICES: ServiceHealth[] = [
  { name: 'morgana_bridge', label: 'Morgana', port: 8001, healthUrl: 'http://127.0.0.1:8001/bifrost/status', status: 'checking' },
  { name: 'saltare', label: 'Saltare', port: 8085, healthUrl: 'http://127.0.0.1:8085/health', status: 'checking' },
  { name: 'rotel', label: 'Rotel', port: 4317, healthUrl: 'http://127.0.0.1:4317/health', status: 'checking' },
  { name: 'excalibur', label: 'Excalibur', port: 8000, healthUrl: 'http://127.0.0.1:8000/health', status: 'checking' },
  { name: 'qdrant', label: 'Qdrant', port: 6333, healthUrl: 'http://127.0.0.1:6333/', status: 'checking' },
  { name: 'modal_lt', label: 'Modal LT', port: 0, healthUrl: 'https://cyberdad247--camelot-lt-memory-health.modal.run', status: 'checking' },
];
