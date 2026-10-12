import { runtimeConfig } from '@/config/runtime';
import { useAnyaSocket } from '@/features/brain/useAnyaSocket';
import { bifrostFetch } from '@/lib/bifrostClient';
import { cn } from '@/lib/utils';
import {
  Activity,
  AlertCircle,
  BrainCircuit,
  CheckCircle2,
  Cpu,
  Loader2,
  Radio,
  RefreshCw,
  Shield,
  Users,
  Zap,
} from 'lucide-react';
import React, { useCallback, useEffect, useState } from 'react';

interface BifrostStatus {
  gate: string;
  owner: string;
  hostname: string;
  token_present: boolean;
  bridge: string;
  cartridges: string[];
  cognitive_helm: string;
  bridge_knight: string;
  switchboard?: SwitchboardTerminal[];
  terminals?: SwitchboardTerminal[];
}

interface SwitchboardTerminal {
  id: string;
  name?: string;
  role?: string;
  status?: string;
  engine?: string;
  cost_tier?: string;
  capabilities?: string[];
}

type LoadState = 'idle' | 'loading' | 'ok' | 'error';

const getKnightDtcgYaml = (id: string, name?: string) => {
  const cleanId = (id || name || '').toLowerCase();

  if (cleanId.includes('merlin')) {
    return `merlin_omega:
  role: "ORCHESTRATOR"
  capability: "GoT/ToT Deep Reasoning"
  model: "gemini-3-pro-preview"
  model_tier: "high"
  ocean_profile: "conscientious_open"`;
  }
  if (cleanId.includes('boris')) {
    return `sir_boris:
  role: "EXECUTOR / ARCHITECT"
  capability: "Crucible Conductor"
  model: "gemini-3-pro-preview"
  model_tier: "high"
  ocean_profile: "architect_critic"`;
  }
  if (cleanId.includes('alex')) {
    return `sir_alex:
  role: "PLANNER"
  capability: "Task DAG Planner"
  model: "gemini-3-pro-preview"
  model_tier: "medium"
  ocean_profile: "organized_planner"`;
  }
  if (cleanId.includes('sentinel')) {
    return `sir_sentinel:
  role: "SECURITY"
  capability: "AgentArmor HITL Gate"
  model: "gemini-3-pro-preview"
  model_tier: "medium"
  ocean_profile: "zero_trust_guardian"`;
  }
  if (cleanId.includes('apis') || cleanId.includes('alexandria')) {
    return `lady_apis:
  role: "RESEARCH"
  capability: "BASHR Forager"
  model: "gemini-3.1-pro-preview"
  model_tier: "high"
  ocean_profile: "curious_researcher"`;
  }
  if (cleanId.includes('mnemosyne') || cleanId.includes('lady_m') || cleanId.includes('lady m')) {
    return `lady_mnemosyne:
  role: "ARCHIVIST"
  capability: "Memory Crystallizer"
  model: "gemini-3.1-pro-preview"
  model_tier: "high"
  ocean_profile: "system_memory_guardian"`;
  }
  if (cleanId.includes('forge')) {
    return `sir_forge:
  role: "EXECUTION"
  capability: "Kinetic Code Gen"
  model: "qwen2.5-coder:3b (local)"
  model_tier: "low"
  ocean_profile: "bare_metal_builder"`;
  }
  if (cleanId.includes('ghost')) {
    return `sir_ghost:
  role: "PRIVACY"
  capability: "Air-gapped Secrets Scan"
  model: "qwen3:8b (local)"
  model_tier: "low"
  ocean_profile: "silent_sentinel"`;
  }

  // Generic fallback
  return `${cleanId.replace(/[^a-z0-9]/g, '_')}:
  role: "NANO_KNIGHT"
  capability: "Swarm Node"
  model: "local_llm"
  model_tier: "low"
  ocean_profile: "worker"`;
};

function statusDot(s?: string) {
  const l = (s ?? '').toLowerCase();
  if (l === 'live' || l === 'active' || l === 'assumed_live') return 'bg-emerald-400 animate-pulse';
  if (l === 'idle' || l === 'standby') return 'bg-blue-400';
  if (l === 'error' || l === 'dead') return 'bg-red-400';
  return 'bg-slate-600';
}

function tierBadge(tier?: string) {
  const t = (tier ?? '').toLowerCase();
  if (t === 'free' || t === '0') return 'text-emerald-400 border-emerald-700';
  if (t === 'low' || t === '1') return 'text-blue-400 border-blue-700';
  if (t === 'medium' || t === '2') return 'text-amber-400 border-amber-700';
  if (t === 'high' || t === '3') return 'text-red-400 border-red-700';
  return 'text-slate-400 border-slate-700';
}

export default function SwarmMonitor() {
  const [status, setStatus] = useState<BifrostStatus | null>(null);
  const [loadState, setLoadState] = useState<LoadState>('idle');
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);
  const { events, isConnected } = useAnyaSocket();

  const fetchStatus = useCallback(async () => {
    setLoadState('loading');
    try {
      const res = await bifrostFetch(runtimeConfig.bifrost.statusUrl);
      if (!res.ok) throw new Error(`${res.status}`);
      const data: BifrostStatus = await res.json();
      setStatus(data);
      setLoadState('ok');
      setLastRefresh(new Date());
    } catch {
      setLoadState('error');
    }
  }, []);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);
  useEffect(() => {
    const id = setInterval(fetchStatus, 30_000);
    return () => clearInterval(id);
  }, [fetchStatus]);

  const terminals: SwitchboardTerminal[] = status?.switchboard ?? status?.terminals ?? [];
  const cartridges: string[] = status?.cartridges ?? [];
  const liveCount = terminals.filter((t) => {
    const s = (t.status ?? '').toLowerCase();
    return s === 'live' || s === 'active' || s === 'assumed_live';
  }).length;
  const healthPct = terminals.length
    ? Math.round((liveCount / terminals.length) * 100)
    : loadState === 'ok'
      ? 100
      : 0;

  const recentEvents = events.slice(-8).reverse();

  return (
    <div className="flex flex-col h-full bg-[#06030f] text-slate-100 p-4 gap-4 overflow-y-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-fuchsia-500">
            Swarm Monitor
          </h1>
          <p className="text-[10px] text-slate-500 uppercase tracking-widest mt-0.5">
            {status?.bridge ?? 'Anya Knight Cluster'} — {status?.hostname ?? '…'}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div
            className={cn(
              'flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-bold',
              loadState === 'ok'
                ? 'border-emerald-700 text-emerald-300'
                : 'border-slate-700 text-slate-500',
            )}
          >
            <Activity size={12} className={loadState === 'ok' ? 'animate-pulse' : ''} />
            {loadState === 'ok'
              ? `${healthPct}% LIVE`
              : loadState === 'loading'
                ? 'Polling…'
                : 'DARK'}
          </div>
          <button
            onClick={fetchStatus}
            disabled={loadState === 'loading'}
            className="rounded-lg border border-slate-700 bg-slate-900 p-1.5 text-slate-400 hover:text-slate-200 hover:border-slate-500 transition-colors disabled:opacity-40"
          >
            <RefreshCw size={14} className={loadState === 'loading' ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {/* Metrics row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {[
          {
            label: 'Terminals',
            value: terminals.length || (loadState === 'ok' ? '—' : '…'),
            icon: Users,
            color: 'text-blue-400',
          },
          {
            label: 'Live',
            value: terminals.length ? liveCount : loadState === 'ok' ? '—' : '…',
            icon: Zap,
            color: 'text-emerald-400',
          },
          {
            label: 'Cartridges',
            value: cartridges.length || (loadState === 'ok' ? '—' : '…'),
            icon: Cpu,
            color: 'text-fuchsia-400',
          },
          {
            label: 'Bifrost',
            value: isConnected ? 'LIVE' : 'DARK',
            icon: Radio,
            color: isConnected ? 'text-cyan-400' : 'text-red-400',
          },
        ].map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="rounded-xl border border-slate-800 bg-slate-900/60 p-3">
            <div className="flex items-center justify-between mb-2">
              <p className="text-[10px] uppercase tracking-widest text-slate-500">{label}</p>
              <Icon size={14} className={color} />
            </div>
            <p className={cn('text-xl font-black', color)}>{value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 flex-1 min-h-0">
        {/* Terminal roster */}
        <div className="lg:col-span-2 flex flex-col gap-2 overflow-y-auto">
          <h2 className="text-[10px] font-semibold uppercase tracking-widest text-slate-500 px-1">
            Switchboard Terminals
            {status?.cognitive_helm && (
              <span className="ml-2 text-indigo-400">Helm: {status.cognitive_helm}</span>
            )}
          </h2>

          {loadState === 'loading' && (
            <div className="flex items-center justify-center py-12 text-slate-600">
              <Loader2 size={20} className="animate-spin mr-2" /> Probing switchboard…
            </div>
          )}

          {loadState === 'error' && (
            <div className="flex items-center gap-2 rounded-xl border border-red-900/50 bg-red-950/20 p-4 text-red-400 text-sm">
              <AlertCircle size={16} /> Bifrost unreachable — is Morgana Bridge running on :8001?
            </div>
          )}

          {loadState === 'ok' && terminals.length === 0 && (
            <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-6 text-center">
              <BrainCircuit size={24} className="mx-auto mb-2 text-slate-600" />
              <p className="text-sm text-slate-500">
                No terminals in switchboard — cartridges active via bridge_knight
              </p>
              <div className="mt-3 flex flex-wrap gap-1.5 justify-center">
                {cartridges.map((c) => (
                  <span
                    key={c}
                    className="rounded-md border border-fuchsia-700/40 bg-fuchsia-950/30 px-2 py-0.5 text-[10px] font-bold text-fuchsia-300"
                  >
                    {c}
                  </span>
                ))}
              </div>
            </div>
          )}

          {terminals.map((t) => (
            <div
              key={t.id}
              className="relative group flex items-center gap-3 rounded-xl border border-slate-800 bg-slate-900/50 px-4 py-3 hover:border-[#00FFC2]/50 hover:bg-[#0D0E12] transition-all duration-200"
            >
              <span className={cn('h-2 w-2 shrink-0 rounded-full', statusDot(t.status))} />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold truncate text-white group-hover:text-[#00FFC2] transition-colors">
                  {t.name ?? t.id}
                </p>
                <p className="text-[10px] text-[#8E95A5] font-mono truncate">
                  {t.role ?? 'knight'}
                  {t.engine ? ` · ${t.engine}` : ''}
                </p>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                {t.cost_tier && (
                  <span
                    className={cn(
                      'rounded border px-1.5 py-0.5 text-[9px] font-bold uppercase',
                      tierBadge(t.cost_tier),
                    )}
                  >
                    {t.cost_tier}
                  </span>
                )}
                <span
                  className={cn(
                    'text-[10px] font-bold uppercase',
                    (t.status ?? '').toLowerCase() === 'live'
                      ? 'text-emerald-400'
                      : 'text-slate-600',
                  )}
                >
                  {t.status ?? 'unknown'}
                </span>
              </div>

              {/* DTCG Agentic Schema Tooltip */}
              <div className="absolute bottom-full left-0 mb-2.5 hidden group-hover:flex flex-col w-80 bg-[#08080A] border border-[#1A1D26] rounded-lg shadow-2xl p-3 z-50 pointer-events-none font-mono text-[10px] text-[#8E95A5] border-l-2 border-l-[#00FFC2]">
                <div className="flex items-center justify-between border-b border-[#1A1D26] pb-1.5 mb-2">
                  <span className="text-white font-bold text-xs">{t.name ?? t.id}</span>
                  <span className="text-[#00FFC2] font-semibold tracking-wider text-[8px] uppercase">
                    DTCG YAML SPEC
                  </span>
                </div>
                <pre className="bg-[#0D0E12] p-2 rounded border border-[#1A1D26] text-emerald-400 overflow-x-auto leading-relaxed text-[9px]">
                  {getKnightDtcgYaml(t.id, t.name)}
                </pre>
                <div className="mt-2 text-[8px] text-slate-500 italic">
                  Visual Engineering / Singularity Lattice Genome v1000
                </div>
              </div>
            </div>
          ))}

          {loadState === 'ok' && terminals.length > 0 && cartridges.length > 0 && (
            <div className="mt-2">
              <p className="text-[10px] uppercase tracking-widest text-slate-600 mb-1.5">
                Active Cartridges
              </p>
              <div className="flex flex-wrap gap-1.5">
                {cartridges.map((c) => (
                  <span
                    key={c}
                    className="rounded-md border border-fuchsia-700/40 bg-fuchsia-950/30 px-2 py-0.5 text-[10px] font-bold text-fuchsia-300"
                  >
                    {c}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Live event feed */}
        <div className="flex flex-col gap-2 overflow-hidden">
          <div className="flex items-center justify-between px-1">
            <h2 className="text-[10px] font-semibold uppercase tracking-widest text-slate-500">
              Live Events
            </h2>
            <div
              className={cn(
                'h-1.5 w-1.5 rounded-full',
                isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-slate-600',
              )}
            />
          </div>
          <div className="flex-1 overflow-y-auto rounded-xl border border-slate-800 bg-slate-900/30 p-3 space-y-1.5 min-h-[180px]">
            {recentEvents.length === 0 ? (
              <p className="text-[10px] text-slate-600 italic text-center pt-4">
                {isConnected ? 'Listening for events…' : 'Bifrost DARK'}
              </p>
            ) : (
              recentEvents.map((ev, i) => (
                <div key={i} className="rounded-md bg-slate-800/50 px-2 py-1.5">
                  <div className="flex items-center gap-1.5 mb-0.5">
                    <CheckCircle2 size={10} className="text-emerald-400 shrink-0" />
                    <span className="text-[9px] text-slate-500 font-mono">
                      {(ev as { timestamp?: string }).timestamp?.slice(11, 19) ?? ''}
                    </span>
                    {(ev as { source?: string }).source && (
                      <span className="text-[9px] text-fuchsia-400 font-bold">
                        {(ev as { source?: string }).source}
                      </span>
                    )}
                  </div>
                  <p className="text-[10px] text-slate-300 leading-snug line-clamp-2">
                    {(ev as { message?: string }).message ?? JSON.stringify(ev)}
                  </p>
                </div>
              ))
            )}
          </div>

          {lastRefresh && (
            <p className="text-[9px] text-slate-600 text-right px-1">
              Updated {lastRefresh.toLocaleTimeString()}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
