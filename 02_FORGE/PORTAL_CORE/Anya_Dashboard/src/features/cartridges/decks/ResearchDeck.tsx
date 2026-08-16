import React, { useState } from 'react';
import { Send, Loader2, Search, Sliders } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { DeckProps } from '../CartridgeDeck';

type Depth = 'quick' | 'medium' | 'deep';

export default function ResearchDeck({ cartridge, onDispatch, dispatching }: DeckProps) {
  const [intent, setIntent] = useState('');
  const [depth, setDepth] = useState<Depth>('medium');
  const [chimera, setChimera] = useState(true);
  const [maxSources, setMaxSources] = useState(5);
  const [nlmAncestor, setNlmAncestor] = useState(true);

  const submit = () =>
    onDispatch(intent, { depth, chimera, max_sources: maxSources, nlm_ancestor: nlmAncestor });

  return (
    <div className="space-y-5">
      <p className="text-xs text-slate-500">
        LADY_APIS — Browser Nano-Knights + CHIMERA 3-round pipeline.
      </p>

      <div className="space-y-2">
        <label className="text-xs font-semibold uppercase tracking-widest text-blue-400">
          Research Query
        </label>
        <textarea
          rows={4}
          placeholder="What topic, question, or competitor should be researched?…"
          value={intent}
          onChange={(e) => setIntent(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) submit();
          }}
          className="w-full rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-2.5 text-sm text-slate-100 placeholder-slate-600 outline-none focus:border-blue-500 resize-none"
        />
      </div>

      <div>
        <label className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-2 block flex items-center gap-1.5">
          <Sliders className="h-3.5 w-3.5" /> Depth
        </label>
        <div className="flex rounded-lg border border-slate-700 overflow-hidden">
          {(['quick', 'medium', 'deep'] as Depth[]).map((d) => (
            <button
              key={d}
              onClick={() => setDepth(d)}
              className={cn(
                'flex-1 py-2 text-xs font-semibold capitalize transition-colors',
                depth === d ? 'bg-blue-700 text-white' : 'text-slate-400 hover:bg-slate-800',
              )}
            >
              {d}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-2 block">
          Max Sources: <span className="text-blue-400">{maxSources}</span>
        </label>
        <input
          type="range"
          min={1}
          max={20}
          value={maxSources}
          onChange={(e) => setMaxSources(Number(e.target.value))}
          className="w-full accent-blue-500"
        />
      </div>

      <div className="flex flex-wrap gap-4">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={chimera}
            onChange={(e) => setChimera(e.target.checked)}
            className="accent-blue-500"
          />
          <span className="text-xs text-slate-400">CHIMERA 3-Round Refinement</span>
        </label>
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={nlmAncestor}
            onChange={(e) => setNlmAncestor(e.target.checked)}
            className="accent-blue-500"
          />
          <span className="text-xs text-slate-400">NotebookLM Ancestor Seed</span>
        </label>
      </div>

      <button
        onClick={submit}
        disabled={dispatching || !intent.trim()}
        className="w-full flex items-center justify-center gap-2 rounded-xl bg-blue-700 hover:bg-blue-600 disabled:opacity-40 py-3 text-sm font-bold text-white transition-colors"
      >
        {dispatching ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Search className="h-4 w-4" />
        )}
        {dispatching ? 'Scouting…' : 'Dispatch to LADY_APIS'}
      </button>
    </div>
  );
}
