import { cn } from '@/lib/utils';
import { Cpu, GitBranch, Layers, Loader2, Send } from 'lucide-react';
import React, { useState } from 'react';
import type { DeckProps } from '../CartridgeDeck';

type ReasoningMode = 'ToT' | 'GoT' | 'DoT' | 'ReAct' | 'TCoT';
type SubGoals = 1 | 2 | 3;

const MODE_DESC: Record<ReasoningMode, string> = {
  ToT: 'Tree of Thought — explore branching solution paths',
  GoT: 'Graph of Thought — non-linear reasoning network',
  DoT: 'Diagram of Thought — structured visual decomposition',
  ReAct: 'Reason + Act — interleave reasoning with tool calls',
  TCoT: 'Typed Chain-of-Thought — symbolic Z3-style verification',
};

export default function CognitiveDeck({ cartridge, onDispatch, dispatching }: DeckProps) {
  const [intent, setIntent] = useState('');
  const [mode, setMode] = useState<ReasoningMode>('ToT');
  const [subGoals, setSubGoals] = useState<SubGoals>(3);
  const [showWork, setShowWork] = useState(true);
  const [formalVerify, setFormalVerify] = useState(false);

  const submit = () =>
    onDispatch(intent, {
      mode,
      sub_goals: subGoals,
      show_work: showWork,
      formal_verify: formalVerify,
    });

  return (
    <div className="space-y-5">
      <div>
        <p className="text-xs text-slate-500 mb-1">
          SIR_ALEX governs all reasoning chains. NPE error target: ≤0.7%.
        </p>
      </div>

      {/* Intent */}
      <div className="space-y-2">
        <label className="text-xs font-semibold uppercase tracking-widest text-indigo-400">
          Intent / Problem
        </label>
        <textarea
          rows={4}
          placeholder="Describe the problem or decision that needs structured reasoning…"
          value={intent}
          onChange={(e) => setIntent(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) submit();
          }}
          className="w-full rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-2.5 text-sm text-slate-100 placeholder-slate-600 outline-none focus:border-indigo-500 resize-none"
        />
      </div>

      {/* Reasoning Mode */}
      <div>
        <label className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-2 block flex items-center gap-1.5">
          <GitBranch className="h-3.5 w-3.5" /> Reasoning Mode
        </label>
        <div className="grid grid-cols-5 gap-1.5">
          {(['ToT', 'GoT', 'DoT', 'ReAct', 'TCoT'] as ReasoningMode[]).map((m) => (
            <button
              key={m}
              onClick={() => setMode(m)}
              className={cn(
                'rounded-lg border py-2 text-xs font-bold transition-colors',
                mode === m
                  ? 'bg-indigo-700/60 border-indigo-500/60 text-indigo-200'
                  : 'border-slate-700 text-slate-500 hover:border-slate-600 hover:text-slate-300',
              )}
            >
              {m}
            </button>
          ))}
        </div>
        <p className="mt-1.5 text-[11px] text-slate-600 italic">{MODE_DESC[mode]}</p>
      </div>

      {/* Sub-goal cap */}
      <div>
        <label className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-2 block flex items-center gap-1.5">
          <Layers className="h-3.5 w-3.5" /> Sub-goal Cap (NPE: max 3)
        </label>
        <div className="flex gap-2">
          {([1, 2, 3] as SubGoals[]).map((n) => (
            <button
              key={n}
              onClick={() => setSubGoals(n)}
              className={cn(
                'flex-1 rounded-lg border py-2 text-sm font-black transition-colors',
                subGoals === n
                  ? 'bg-indigo-700/60 border-indigo-500/60 text-indigo-200'
                  : 'border-slate-700 text-slate-400 hover:border-slate-600',
              )}
            >
              {n}
            </button>
          ))}
        </div>
      </div>

      {/* Toggles */}
      <div className="flex flex-wrap gap-4">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={showWork}
            onChange={(e) => setShowWork(e.target.checked)}
            className="accent-indigo-500"
          />
          <span className="text-xs text-slate-400">Show Work (TCoT)</span>
        </label>
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={formalVerify}
            onChange={(e) => setFormalVerify(e.target.checked)}
            className="accent-indigo-500"
          />
          <span className="text-xs text-slate-400">Formal Verification (Z3-style)</span>
        </label>
      </div>

      {/* NPE notice */}
      <div className="rounded-lg border border-indigo-500/20 bg-indigo-950/20 px-3 py-2 flex items-center gap-2">
        <Cpu className="h-3.5 w-3.5 text-indigo-400 shrink-0" />
        <p className="text-[11px] text-slate-500">
          NPE: sub-goal cap <strong className="text-indigo-400">{subGoals}</strong> · mode{' '}
          <strong className="text-indigo-400">{mode}</strong> · ~18KB persona overhead/sub-goal
        </p>
      </div>

      <button
        onClick={submit}
        disabled={dispatching || !intent.trim()}
        className="w-full flex items-center justify-center gap-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 py-3 text-sm font-bold text-white transition-colors"
      >
        {dispatching ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
        {dispatching ? 'Reasoning…' : 'Dispatch to SIR_ALEX'}
      </button>
    </div>
  );
}
