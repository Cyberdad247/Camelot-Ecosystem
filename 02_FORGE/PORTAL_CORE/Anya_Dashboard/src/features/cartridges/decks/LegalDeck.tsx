import React, { useState } from 'react';
import { Send, Loader2, Scale, ShieldAlert } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { DeckProps } from '../CartridgeDeck';

type AnalysisType = 'contract' | 'compliance' | 'risk' | 'ip' | 'privacy';
type Severity = 'low' | 'medium' | 'high' | 'critical';

const TYPE_DESC: Record<AnalysisType, string> = {
  contract: 'Review clauses, identify risks, flag ambiguities',
  compliance: 'Check against GDPR, SOC2, HIPAA, CCPA',
  risk: 'Threat modeling, liability exposure mapping',
  ip: 'Patent, trademark, copyright analysis',
  privacy: 'PII detection, data handling audit',
};

export default function LegalDeck({ cartridge, onDispatch, dispatching }: DeckProps) {
  const [intent, setIntent] = useState('');
  const [analysisType, setAnalysisType] = useState<AnalysisType>('contract');
  const [jurisdiction, setJurisdiction] = useState('US');
  const [minSeverity, setMinSeverity] = useState<Severity>('medium');
  const [piiDetect, setPiiDetect] = useState(true);
  const [agentArmor, setAgentArmor] = useState(true);

  const submit = () =>
    onDispatch(intent, {
      analysis_type: analysisType,
      jurisdiction,
      min_severity: minSeverity,
      pii_detection: piiDetect,
      agent_armor: agentArmor,
    });

  return (
    <div className="space-y-5">
      <p className="text-xs text-slate-500">
        SIR_SENTINEL — Agent-Armor v2.0 + PDG compliance gate.
      </p>

      <div className="space-y-2">
        <label className="text-xs font-semibold uppercase tracking-widest text-purple-400">
          Document / Scenario
        </label>
        <textarea
          rows={4}
          placeholder="Paste contract text, describe the compliance scenario, or enter the legal question…"
          value={intent}
          onChange={(e) => setIntent(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) submit();
          }}
          className="w-full rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-2.5 text-sm text-slate-100 placeholder-slate-600 outline-none focus:border-purple-500 resize-none"
        />
      </div>

      <div>
        <label className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-2 block">
          Analysis Type
        </label>
        <div className="space-y-1.5">
          {(['contract', 'compliance', 'risk', 'ip', 'privacy'] as AnalysisType[]).map((t) => (
            <button
              key={t}
              onClick={() => setAnalysisType(t)}
              className={cn(
                'w-full text-left rounded-lg border px-3 py-2 transition-colors',
                analysisType === t
                  ? 'bg-purple-950/50 border-purple-500/40'
                  : 'border-slate-700 hover:border-slate-600',
              )}
            >
              <p
                className={cn(
                  'text-xs font-bold capitalize',
                  analysisType === t ? 'text-purple-300' : 'text-slate-400',
                )}
              >
                {t}
              </p>
              <p className="text-[10px] text-slate-600">{TYPE_DESC[t]}</p>
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="text-xs text-slate-500 mb-1 block">Jurisdiction</label>
          <select
            value={jurisdiction}
            onChange={(e) => setJurisdiction(e.target.value)}
            className="w-full rounded-lg border border-slate-700 bg-slate-900 px-2 py-1.5 text-sm text-slate-300 outline-none"
          >
            {['US', 'EU', 'UK', 'CA', 'Global'].map((j) => (
              <option key={j}>{j}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-xs text-slate-500 mb-1 block">Min Severity</label>
          <select
            value={minSeverity}
            onChange={(e) => setMinSeverity(e.target.value as Severity)}
            className="w-full rounded-lg border border-slate-700 bg-slate-900 px-2 py-1.5 text-sm text-slate-300 outline-none"
          >
            {['low', 'medium', 'high', 'critical'].map((s) => (
              <option key={s}>{s}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="flex flex-wrap gap-4">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={piiDetect}
            onChange={(e) => setPiiDetect(e.target.checked)}
            className="accent-purple-500"
          />
          <span className="text-xs text-slate-400">PII Detection</span>
        </label>
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={agentArmor}
            onChange={(e) => setAgentArmor(e.target.checked)}
            className="accent-purple-500"
          />
          <span className="text-xs text-slate-400">Agent-Armor Gate</span>
        </label>
      </div>

      <button
        onClick={submit}
        disabled={dispatching || !intent.trim()}
        className="w-full flex items-center justify-center gap-2 rounded-xl bg-purple-700 hover:bg-purple-600 disabled:opacity-40 py-3 text-sm font-bold text-white transition-colors"
      >
        {dispatching ? <Loader2 className="h-4 w-4 animate-spin" /> : <Scale className="h-4 w-4" />}
        {dispatching ? 'Auditing…' : 'Dispatch to SIR_SENTINEL'}
      </button>
    </div>
  );
}
