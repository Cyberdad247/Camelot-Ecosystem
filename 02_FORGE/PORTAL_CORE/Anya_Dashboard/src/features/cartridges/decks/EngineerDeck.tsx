import React, { useState } from 'react';
import { Send, Loader2, Code2, FileCode, Wrench } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { DeckProps } from '../CartridgeDeck';

type Language = 'rust' | 'go' | 'python' | 'typescript' | 'bash';
type EngMode = 'generate' | 'debug' | 'review' | 'refactor' | 'test';

const LANG_COLOR: Record<Language, string> = {
  rust: 'text-orange-400 border-orange-600',
  go: 'text-cyan-400 border-cyan-600',
  python: 'text-yellow-400 border-yellow-600',
  typescript: 'text-blue-400 border-blue-600',
  bash: 'text-slate-400 border-slate-600',
};

const MODE_DESC: Record<EngMode, string> = {
  generate: 'Generate new code from spec',
  debug: 'Diagnose and fix errors',
  review: 'Security + quality audit',
  refactor: 'Improve structure without changing behavior',
  test: 'Write unit and integration tests',
};

export default function EngineerDeck({ cartridge, onDispatch, dispatching }: DeckProps) {
  const [intent, setIntent] = useState('');
  const [lang, setLang] = useState<Language>('rust');
  const [mode, setMode] = useState<EngMode>('generate');
  const [filePath, setFilePath] = useState('');
  const [kineticPurity, setKineticPurity] = useState(true);

  const submit = () =>
    onDispatch(intent, {
      language: lang,
      mode,
      file_path: filePath,
      kinetic_purity: kineticPurity,
    });

  return (
    <div className="space-y-5">
      <p className="text-xs text-slate-500">
        SIR_FORGE — Kinetic Purity enforced: Rust/Go preferred over Python.
      </p>

      {/* Intent */}
      <div className="space-y-2">
        <label className="text-xs font-semibold uppercase tracking-widest text-emerald-400">
          Task / Spec
        </label>
        <textarea
          rows={4}
          placeholder="Describe what to build, debug, or review. Be precise: include function names, data types, constraints…"
          value={intent}
          onChange={(e) => setIntent(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) submit();
          }}
          className="w-full rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-2.5 text-sm text-slate-100 placeholder-slate-600 outline-none focus:border-emerald-500 resize-none font-mono"
        />
      </div>

      {/* Language */}
      <div>
        <label className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-2 block">
          Language
        </label>
        <div className="flex gap-2 flex-wrap">
          {(['rust', 'go', 'python', 'typescript', 'bash'] as Language[]).map((l) => (
            <button
              key={l}
              onClick={() => setLang(l)}
              className={cn(
                'rounded-lg border px-3 py-1.5 text-xs font-bold uppercase transition-colors',
                lang === l
                  ? cn('bg-emerald-950/60', LANG_COLOR[l])
                  : 'border-slate-700 text-slate-500 hover:border-slate-600',
              )}
            >
              {l}
            </button>
          ))}
        </div>
      </div>

      {/* Mode */}
      <div>
        <label className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-2 block flex items-center gap-1.5">
          <Wrench className="h-3.5 w-3.5" /> Mode
        </label>
        <div className="grid grid-cols-5 gap-1.5">
          {(['generate', 'debug', 'review', 'refactor', 'test'] as EngMode[]).map((m) => (
            <button
              key={m}
              onClick={() => setMode(m)}
              className={cn(
                'rounded-lg border py-2 text-xs font-bold capitalize transition-colors',
                mode === m
                  ? 'bg-emerald-900/50 border-emerald-500/50 text-emerald-200'
                  : 'border-slate-700 text-slate-500 hover:border-slate-600',
              )}
            >
              {m}
            </button>
          ))}
        </div>
        <p className="mt-1 text-[11px] text-slate-600 italic">{MODE_DESC[mode]}</p>
      </div>

      {/* File target */}
      <div>
        <label className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-1.5 block flex items-center gap-1.5">
          <FileCode className="h-3.5 w-3.5" /> File Path (optional)
        </label>
        <input
          placeholder="e.g. 01_KERNEL/senses/morgana_bridge/src/main.rs"
          value={filePath}
          onChange={(e) => setFilePath(e.target.value)}
          className="w-full rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-300 placeholder-slate-600 outline-none focus:border-emerald-500 font-mono"
        />
      </div>

      <label className="flex items-center gap-2 cursor-pointer">
        <input
          type="checkbox"
          checked={kineticPurity}
          onChange={(e) => setKineticPurity(e.target.checked)}
          className="accent-emerald-500"
        />
        <span className="text-xs text-slate-400">
          Kinetic Purity — prefer Rust/Go, reject Python for binary work
        </span>
      </label>

      <button
        onClick={submit}
        disabled={dispatching || !intent.trim()}
        className="w-full flex items-center justify-center gap-2 rounded-xl bg-emerald-700 hover:bg-emerald-600 disabled:opacity-40 py-3 text-sm font-bold text-white transition-colors"
      >
        {dispatching ? <Loader2 className="h-4 w-4 animate-spin" /> : <Code2 className="h-4 w-4" />}
        {dispatching ? 'Forging…' : 'Dispatch to SIR_FORGE'}
      </button>
    </div>
  );
}
