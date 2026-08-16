import React, { useState } from 'react';
import { Send, Loader2, Target, ShieldAlert, Scale } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { DeckProps } from '../CartridgeDeck';

type CritMode = 'socratic' | 'red_team' | 'bias' | 'failure' | 'proof';

const MODE_DESC: Record<CritMode, string> = {
  socratic: 'Question assumptions and surface hidden claims',
  red_team: 'Adversarial challenge and scenario stress test',
  bias: 'Bias, blind spot, and inconsistency audit',
  failure: 'Find failure modes and edge conditions',
  proof: 'Demand evidence, citations, and support',
};

export default function CriticalDeck({ cartridge, onDispatch, dispatching }: DeckProps) {
  const [intent, setIntent] = useState('');
  const [mode, setMode] = useState<CritMode>('socratic');
  const [severityFloor, setSeverityFloor] = useState(2);
  const [needCounterpoints, setNeedCounterpoints] = useState(true);
  const [needActionPlan, setNeedActionPlan] = useState(true);

  const submit = () =>
    onDispatch(intent, {
      critique_mode: mode,
      severity_floor: severityFloor,
      counterpoints: needCounterpoints,
      action_plan: needActionPlan,
    });

  return (
    <div className="space-y-5">
      <p className="text-xs text-slate-500">
        SIR_ALEX â€” Socratic analysis, Devil's Advocate, bias surfacing.
      </p>

      <div className="space-y-2">
        <label className="text-xs font-semibold uppercase tracking-widest text-red-400">
          Claim / Decision
        </label>
        <textarea
          rows={4}
          placeholder="Paste the claim, plan, or decision that should be pressure-testedâ€¦"
          value={intent}
          onChange={(e) => setIntent(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) submit();
          }}
          className="w-full rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-2.5 text-sm text-slate-100 placeholder-slate-600 outline-none focus:border-red-500 resize-none"
        />
      </div>

      <div>
        <label className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-2 block flex items-center gap-1.5">
          <Target className="h-3.5 w-3.5" /> Critique Mode
        </label>
        <div className="grid grid-cols-5 gap-1.5">
          {(['socratic', 'red_team', 'bias', 'failure', 'proof'] as CritMode[]).map((m) => (
            <button
              key={m}
              onClick={() => setMode(m)}
              className={cn(
                'rounded-lg border py-2 text-[11px] font-bold uppercase transition-colors',
                mode === m
                  ? 'bg-red-900/50 border-red-500/50 text-red-200'
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
          <Scale className="h-3.5 w-3.5" /> Severity Floor
        </label>
        <input
          type="range"
          min={1}
          max={5}
          value={severityFloor}
          onChange={(e) => setSeverityFloor(Number(e.target.value))}
          className="w-full accent-red-500"
        />
        <p className="mt-1 text-[11px] text-slate-500">
          Minimum issue severity:{' '}
          <span className="text-red-300 font-semibold">{severityFloor}</span>/5
        </p>
      </div>

      <div className="flex flex-wrap gap-4">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={needCounterpoints}
            onChange={(e) => setNeedCounterpoints(e.target.checked)}
            className="accent-red-500"
          />
          <span className="text-xs text-slate-400">Require counterpoints</span>
        </label>
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={needActionPlan}
            onChange={(e) => setNeedActionPlan(e.target.checked)}
            className="accent-red-500"
          />
          <span className="text-xs text-slate-400">Return action plan</span>
        </label>
      </div>

      <button
        onClick={submit}
        disabled={dispatching || !intent.trim()}
        className="w-full flex items-center justify-center gap-2 rounded-xl bg-red-700 hover:bg-red-600 disabled:opacity-40 py-3 text-sm font-bold text-white transition-colors"
      >
        {dispatching ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <ShieldAlert className="h-4 w-4" />
        )}
        {dispatching ? 'Pressuringâ€¦' : 'Dispatch to SIR_ALEX'}
      </button>
    </div>
  );
}
