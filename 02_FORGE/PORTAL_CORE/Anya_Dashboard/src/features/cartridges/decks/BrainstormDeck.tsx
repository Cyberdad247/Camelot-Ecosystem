import React, { useState } from 'react';
import { Send, Loader2, Lightbulb, Shuffle, Layers } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { DeckProps } from '../CartridgeDeck';

type IdeationMode = 'divergent' | 'convergent' | 'scamper' | 'triz' | 'auto';

const MODE_DESC: Record<IdeationMode, string> = {
  divergent: 'Explore many directions before narrowing',
  convergent: 'Refine toward one strong direction',
  scamper: 'Systematic trigger-based ideation',
  triz: 'Contradiction-first innovation framing',
  auto: 'Let Merlin choose the best framework',
};

export default function BrainstormDeck({ cartridge, onDispatch, dispatching }: DeckProps) {
  const [intent, setIntent] = useState('');
  const [mode, setMode] = useState<IdeationMode>('auto');
  const [ideaCount, setIdeaCount] = useState(12);
  const [includeAnalysis, setIncludeAnalysis] = useState(true);
  const [crossDomain, setCrossDomain] = useState(true);

  const submit = () =>
    onDispatch(intent, {
      methodology: mode,
      idea_count: ideaCount,
      include_analysis: includeAnalysis,
      cross_domain: crossDomain,
    });

  return (
    <div className="space-y-5">
      <p className="text-xs text-slate-500">
        MERLIN_OMEGA â€” Divergent ideation, SCAMPER, TRIZ, cross-domain synthesis.
      </p>

      <div className="space-y-2">
        <label className="text-xs font-semibold uppercase tracking-widest text-amber-400">
          Challenge / Prompt
        </label>
        <textarea
          rows={4}
          placeholder="Describe the problem, opportunity, or prompt to brainstormâ€¦"
          value={intent}
          onChange={(e) => setIntent(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) submit();
          }}
          className="w-full rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-2.5 text-sm text-slate-100 placeholder-slate-600 outline-none focus:border-amber-500 resize-none"
        />
      </div>

      <div>
        <label className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-2 block flex items-center gap-1.5">
          <Shuffle className="h-3.5 w-3.5" /> Methodology
        </label>
        <div className="grid grid-cols-5 gap-1.5">
          {(['divergent', 'convergent', 'scamper', 'triz', 'auto'] as IdeationMode[]).map((m) => (
            <button
              key={m}
              onClick={() => setMode(m)}
              className={cn(
                'rounded-lg border py-2 text-[11px] font-bold uppercase transition-colors',
                mode === m
                  ? 'bg-amber-900/50 border-amber-500/50 text-amber-200'
                  : 'border-slate-700 text-slate-500 hover:border-slate-600',
              )}
            >
              {m}
            </button>
          ))}
        </div>
        <p className="mt-1.5 text-[11px] text-slate-600 italic">{MODE_DESC[mode]}</p>
      </div>

      <div>
        <label className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-2 block flex items-center gap-1.5">
          <Layers className="h-3.5 w-3.5" /> Idea Count
        </label>
        <input
          type="range"
          min={3}
          max={24}
          value={ideaCount}
          onChange={(e) => setIdeaCount(Number(e.target.value))}
          className="w-full accent-amber-500"
        />
        <p className="mt-1 text-[11px] text-slate-500">
          Target concepts: <span className="text-amber-300 font-semibold">{ideaCount}</span>
        </p>
      </div>

      <div className="flex flex-wrap gap-4">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={includeAnalysis}
            onChange={(e) => setIncludeAnalysis(e.target.checked)}
            className="accent-amber-500"
          />
          <span className="text-xs text-slate-400">Include feasibility analysis</span>
        </label>
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={crossDomain}
            onChange={(e) => setCrossDomain(e.target.checked)}
            className="accent-amber-500"
          />
          <span className="text-xs text-slate-400">Cross-domain synthesis</span>
        </label>
      </div>

      <button
        onClick={submit}
        disabled={dispatching || !intent.trim()}
        className="w-full flex items-center justify-center gap-2 rounded-xl bg-amber-700 hover:bg-amber-600 disabled:opacity-40 py-3 text-sm font-bold text-white transition-colors"
      >
        {dispatching ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Lightbulb className="h-4 w-4" />
        )}
        {dispatching ? 'Ideatingâ€¦' : 'Dispatch to MERLIN_OMEGA'}
      </button>
    </div>
  );
}
