import React from 'react';
import { Link } from 'react-router-dom';
import {
  Activity, ArrowRight, Cpu, Database, Zap, ShieldCheck,
  TrendingUp, AlertTriangle,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { CARTRIDGES } from '@/features/cartridges/registry';
import { SERVICES, StatusDot } from '@/components/ui/StatusDot';
import EventFeed from '@/components/ui/EventFeed';
import { useAnyaSocket } from '@/features/brain/useAnyaSocket';
import KnightStreamBanner from '@/features/knights/KnightStreamBanner';
import KnightAvatarScene from '@/features/knights/KnightAvatarScene';
import VisualPlanOverlay from '@/features/knights/VisualPlanOverlay';
import { useKnightStream } from '@/features/knights/useKnightStream';

const STAT_CARDS = [
  { label: 'Active Knights', value: '7', icon: Zap, color: 'text-fuchsia-400' },
  { label: 'Tasks In Flight', value: '—', icon: Activity, color: 'text-blue-400' },
  { label: 'LT Memories', value: '—', icon: Database, color: 'text-emerald-400' },
  { label: 'Threat Level', value: 'LOW', icon: ShieldCheck, color: 'text-emerald-400' },
];

export default function SystemHub() {
  const { events, isConnected, latestEvent } = useAnyaSocket();
  const { latestPlan } = useKnightStream();

  return (
    <div className="min-h-full p-6 space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-black tracking-tight text-slate-100">System Hub</h1>
          <p className="text-sm text-slate-500 mt-0.5">CAMELOT Apex OS v400.1.0 — LATTICE_RADIANT</p>
        </div>
        {latestEvent && (
          <div className="rounded-lg border border-fuchsia-500/20 bg-fuchsia-950/20 px-3 py-1.5 max-w-xs">
            <p className="text-[10px] uppercase tracking-widest text-fuchsia-500 mb-0.5">Latest Event</p>
            <p className="text-xs text-slate-300 truncate">{latestEvent.event}</p>
          </div>
        )}
      </div>

      {/* Live knight stream from go_router SSE */}
      <KnightStreamBanner />

      {/* Live 3D knight avatar, driven by the same SSE stream */}
      <div className="h-72">
        <KnightAvatarScene />
      </div>

      {/* Visual plan overlay — renders `mdx` events from go_router /plan */}
      <VisualPlanOverlay plan={latestPlan} />

      {/* Stat row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {STAT_CARDS.map((s) => {
          const Icon = s.icon;
          return (
            <div
              key={s.label}
              className="rounded-xl border border-slate-800/60 bg-slate-900/60 p-4"
            >
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs text-slate-500">{s.label}</p>
                <Icon className={cn('h-4 w-4', s.color)} />
              </div>
              <p className={cn('text-2xl font-black', s.color)}>{s.value}</p>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Service Grid */}
        <div className="lg:col-span-1">
          <h2 className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-3 flex items-center gap-2">
            <Cpu className="h-3.5 w-3.5" /> Services
          </h2>
          <div className="space-y-2">
            {SERVICES.map((svc) => (
              <div
                key={svc.name}
                className="flex items-center gap-3 rounded-lg border border-slate-800/50 bg-slate-900/40 px-3 py-2.5"
              >
                <StatusDot service={svc} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-200">{svc.label}</p>
                  {svc.port > 0 && (
                    <p className="text-[10px] text-slate-600 font-mono">:{svc.port}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Cartridge Quick-Launch */}
        <div className="lg:col-span-1">
          <h2 className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-3 flex items-center gap-2">
            <Zap className="h-3.5 w-3.5" /> Cartridges
          </h2>
          <div className="space-y-1.5">
            {CARTRIDGES.map((c) => {
              const Icon = c.icon;
              return (
                <Link
                  key={c.id}
                  to={`/cartridge/${c.slug}`}
                  className={cn(
                    'flex items-center gap-3 rounded-lg border px-3 py-2.5 transition-colors',
                    c.borderClass,
                    c.bgClass,
                    'hover:brightness-125',
                  )}
                >
                  <Icon className={cn('h-4 w-4 shrink-0', c.textClass)} />
                  <div className="flex-1 min-w-0">
                    <p className={cn('text-sm font-semibold', c.textClass)}>{c.label}</p>
                    <p className="text-[10px] text-slate-500 truncate">{c.knight}</p>
                  </div>
                  <ArrowRight className="h-3.5 w-3.5 text-slate-600 shrink-0" />
                </Link>
              );
            })}
          </div>
        </div>

        {/* Live Event Feed */}
        <div className="lg:col-span-1 flex flex-col">
          <h2 className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-3 flex items-center gap-2">
            <TrendingUp className="h-3.5 w-3.5" /> Activity
          </h2>
          <div className="flex-1 rounded-xl border border-slate-800/50 bg-slate-900/40 p-3 overflow-hidden" style={{ minHeight: 320 }}>
            <EventFeed
              events={events}
              isConnected={isConnected}
              maxRows={30}
              className="h-full"
            />
          </div>
        </div>
      </div>

      {/* Quick actions */}
      <div>
        <h2 className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-3 flex items-center gap-2">
          <AlertTriangle className="h-3.5 w-3.5" /> Quick Actions
        </h2>
        <div className="flex flex-wrap gap-2">
          <Link
            to="/camelot-os"
            className="rounded-lg border border-fuchsia-500/40 bg-fuchsia-950/30 px-4 py-2 text-sm font-semibold text-fuchsia-300 hover:brightness-125 transition-all"
          >
            Camelot OS
          </Link>
          <Link
            to="/alex"
            className="rounded-lg border border-indigo-500/40 bg-indigo-950/30 px-4 py-2 text-sm font-semibold text-indigo-300 hover:brightness-125 transition-all"
          >
            + New Task
          </Link>
          <Link
            to="/research"
            className="rounded-lg border border-blue-500/40 bg-blue-950/30 px-4 py-2 text-sm font-semibold text-blue-300 hover:brightness-125 transition-all"
          >
            Run Research
          </Link>
          <Link
            to="/defense-grid"
            className="rounded-lg border border-slate-700 bg-slate-900/60 px-4 py-2 text-sm font-semibold text-slate-300 hover:brightness-125 transition-all"
          >
            Open Defense Grid
          </Link>
        </div>
      </div>
    </div>
  );
}
