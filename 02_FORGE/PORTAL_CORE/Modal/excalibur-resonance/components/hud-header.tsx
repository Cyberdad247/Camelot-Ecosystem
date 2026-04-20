"use client";

import { Activity, Shield } from "lucide-react";

export function HudHeader() {
  return (
    <header className="flex flex-col gap-3 rounded-2xl border border-zinc-800 bg-white/5 p-6 backdrop-blur">
      <div className="flex items-center gap-3">
        <Shield className="h-6 w-6 text-yellow-400" />
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
            Camelot Agent-OS
          </p>
          <h1 className="text-2xl font-semibold text-white">Excalibur Resonance</h1>
        </div>
      </div>
      <div className="flex flex-wrap items-center gap-3 text-sm text-slate-300">
        <StatusPill label="Bridge" value="Online" tone="text-green-400" />
        <StatusPill label="Knights" value="4 active" tone="text-purple-300" />
        <StatusPill label="Latency" value="~12ms" tone="text-emerald-300" />
      </div>
    </header>
  );
}

function StatusPill({ label, value, tone }: { label: string; value: string; tone: string }) {
  return (
    <span className="inline-flex items-center gap-2 rounded-full bg-black/40 px-3 py-1 text-xs border border-zinc-800">
      <Activity className="h-3.5 w-3.5 text-slate-500" />
      <span className="text-slate-400">{label}:</span>
      <span className={tone}>{value}</span>
    </span>
  );
}
