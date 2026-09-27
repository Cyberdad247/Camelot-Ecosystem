import { cn } from '@/lib/utils';
import { Radio } from 'lucide-react';
import React from 'react';
import { useKnightStream } from './useKnightStream';

// Mirror of go_router's knightRoster in main.go.
const KNIGHTS = ['anya', 'merlin', 'codex', 'hashimoto', 'boris', 'helios'];

export default function KnightStreamBanner() {
  const { isConnected, node, activeKnight } = useKnightStream();
  const active = activeKnight?.knight ?? null;

  return (
    <div className="rounded-xl border border-slate-800/60 bg-slate-900/60 p-4">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="flex items-center gap-2 text-xs font-semibold uppercase tracking-widest text-slate-500">
          <Radio className="h-3.5 w-3.5" /> Knight Stream
          <span className="font-mono text-[10px] text-slate-600">
            {node ? `node:${node}` : 'go_router'}
          </span>
        </h2>
        <span
          className={cn(
            'rounded-full px-2 py-0.5 text-[10px] font-semibold',
            isConnected ? 'bg-emerald-950/40 text-emerald-400' : 'bg-rose-950/40 text-rose-400',
          )}
        >
          {isConnected ? 'live' : 'offline'}
        </span>
      </div>

      <div className="flex flex-wrap gap-2">
        {KNIGHTS.map((knight) => {
          const on = knight === active;
          return (
            <span
              key={knight}
              className={cn(
                'rounded-lg border px-3 py-1.5 text-xs capitalize transition-all',
                on
                  ? 'border-fuchsia-500/60 bg-fuchsia-950/40 text-fuchsia-200 shadow-[0_0_18px_-6px] shadow-fuchsia-500'
                  : 'border-slate-800/50 bg-slate-900/40 text-slate-500',
              )}
            >
              {knight}
            </span>
          );
        })}
      </div>

      {activeKnight && (
        <p className="mt-3 font-mono text-[11px] text-slate-500">
          {activeKnight.rune} · {activeKnight.status} ·{' '}
          {new Date(activeKnight.ts).toLocaleTimeString()}
        </p>
      )}
    </div>
  );
}
