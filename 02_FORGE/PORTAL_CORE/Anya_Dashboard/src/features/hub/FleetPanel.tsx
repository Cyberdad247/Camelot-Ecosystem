import React, { useCallback, useEffect, useState } from 'react';
import { Loader2, Radio, RefreshCw, Satellite, Server, ShieldAlert } from 'lucide-react';
import { cn } from '@/lib/utils';
import { bifrostFetch } from '@/lib/bifrostClient';
import { runtimeConfig } from '@/config/runtime';

interface DaemonStatus {
  name: string;
  role: string;
  up: boolean;
}

interface TailnetNode {
  name: string;
  ip: string | null;
  os: string | null;
  online: boolean;
  self: boolean;
}

interface FleetStatus {
  daemons: DaemonStatus[];
  tailnet: {
    tailnet?: string;
    nodes: TailnetNode[];
    error?: string;
  };
  vault_items: number;
  cloud_reachable: boolean;
  cloud: string;
}

type LoadState = 'idle' | 'loading' | 'ok' | 'error';

const POLL_MS = 15_000;

/**
 * Live Fleet panel — polls cognitive_service's /fleet endpoint (proxied
 * through go_router at /cognitive/fleet) for daemon health and tailnet node
 * reachability, and renders it inside the 3D System Hub.
 */
export default function FleetPanel() {
  const [fleet, setFleet] = useState<FleetStatus | null>(null);
  const [loadState, setLoadState] = useState<LoadState>('idle');
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);

  const fetchFleet = useCallback(async () => {
    setLoadState((s) => (s === 'ok' ? 'ok' : 'loading'));
    try {
      const res = await bifrostFetch(runtimeConfig.cognitive.fleetUrl, {
        signal: AbortSignal.timeout(5000),
      });
      if (!res.ok) throw new Error(`${res.status}`);
      const data: FleetStatus = await res.json();
      setFleet(data);
      setLoadState('ok');
      setLastRefresh(new Date());
    } catch {
      setLoadState('error');
    }
  }, []);

  useEffect(() => {
    fetchFleet();
  }, [fetchFleet]);
  useEffect(() => {
    const id = setInterval(fetchFleet, POLL_MS);
    return () => clearInterval(id);
  }, [fetchFleet]);

  const daemons = fleet?.daemons ?? [];
  const nodes = fleet?.tailnet?.nodes ?? [];
  const upCount = daemons.filter((d) => d.up).length;

  return (
    <div className="rounded-xl border border-slate-800/60 bg-slate-900/60 p-4">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-xs font-semibold uppercase tracking-widest text-slate-500 flex items-center gap-2">
          <Satellite className="h-3.5 w-3.5" /> Live Fleet
        </h2>
        <div className="flex items-center gap-2">
          {loadState === 'ok' && (
            <span
              className={cn(
                'text-[10px] font-bold uppercase tracking-wide',
                upCount === daemons.length && daemons.length > 0
                  ? 'text-emerald-400'
                  : 'text-amber-400',
              )}
            >
              {upCount}/{daemons.length} daemons up
            </span>
          )}
          <button
            onClick={fetchFleet}
            disabled={loadState === 'loading'}
            aria-label="Refresh fleet status"
            className="rounded-lg border border-slate-700 bg-slate-900 p-1 text-slate-400 hover:text-slate-200 hover:border-slate-500 transition-colors disabled:opacity-40"
          >
            <RefreshCw className={cn('h-3 w-3', loadState === 'loading' && 'animate-spin')} />
          </button>
        </div>
      </div>

      {loadState === 'loading' && !fleet && (
        <div className="flex items-center justify-center py-8 text-slate-600">
          <Loader2 className="h-4 w-4 animate-spin mr-2" /> Probing fleet…
        </div>
      )}

      {loadState === 'error' && !fleet && (
        <div className="flex items-center gap-2 rounded-lg border border-red-900/50 bg-red-950/20 p-3 text-red-400 text-xs">
          <ShieldAlert className="h-4 w-4 shrink-0" />
          Cognitive Service unreachable via /cognitive/fleet
        </div>
      )}

      {fleet && (
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-2">
            {daemons.map((d) => (
              <div
                key={d.name}
                className="flex items-center gap-2 rounded-lg border border-slate-800/50 bg-slate-900/40 px-2.5 py-2"
              >
                <span
                  className={cn(
                    'h-2 w-2 rounded-full shrink-0',
                    d.up ? 'bg-emerald-400 shadow-[0_0_6px_#34d399]' : 'bg-red-600',
                  )}
                />
                <div className="min-w-0">
                  <p className="text-xs font-medium text-slate-200 truncate">{d.name}</p>
                  <p className="text-[9px] text-slate-600 truncate">{d.role}</p>
                </div>
              </div>
            ))}
          </div>

          <div>
            <p className="text-[10px] uppercase tracking-widest text-slate-600 mb-1.5 flex items-center gap-1.5">
              <Radio className="h-3 w-3" /> Tailnet
              {fleet.tailnet.tailnet ? ` — ${fleet.tailnet.tailnet}` : ''}
            </p>
            {fleet.tailnet.error ? (
              <p className="text-[10px] text-slate-600 italic">{fleet.tailnet.error}</p>
            ) : nodes.length === 0 ? (
              <p className="text-[10px] text-slate-600 italic">No tailnet nodes reported</p>
            ) : (
              <div className="space-y-1">
                {nodes.map((n) => (
                  <div key={n.name} className="flex items-center gap-2 text-[10px]">
                    <span
                      className={cn(
                        'h-1.5 w-1.5 rounded-full shrink-0',
                        n.online ? 'bg-emerald-400' : 'bg-slate-600',
                      )}
                    />
                    <Server className="h-3 w-3 text-slate-600 shrink-0" />
                    <span className="text-slate-300 truncate">{n.name}</span>
                    {n.self && <span className="text-fuchsia-400 font-bold">(self)</span>}
                    {n.ip && <span className="text-slate-600 font-mono ml-auto">{n.ip}</span>}
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="flex items-center justify-between text-[9px] text-slate-600 pt-1 border-t border-slate-800/50">
            <span>
              Vault {fleet.vault_items} · Cloud{' '}
              <span className={fleet.cloud_reachable ? 'text-emerald-500' : 'text-red-500'}>
                {fleet.cloud_reachable ? 'reachable' : 'dark'}
              </span>
            </span>
            {lastRefresh && <span>Updated {lastRefresh.toLocaleTimeString()}</span>}
          </div>
        </div>
      )}
    </div>
  );
}
