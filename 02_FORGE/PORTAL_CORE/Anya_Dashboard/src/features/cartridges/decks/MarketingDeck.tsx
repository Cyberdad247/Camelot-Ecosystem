import { cn } from '@/lib/utils';
import { Loader2, Send, TrendingUp } from 'lucide-react';
import React, { useState } from 'react';
import type { DeckProps } from '../CartridgeDeck';

type CampaignType = 'content' | 'seo' | 'social' | 'email' | 'paid';
type Platform = 'twitter' | 'linkedin' | 'instagram' | 'tiktok' | 'web';
type MarketingTone = 'professional' | 'casual' | 'aggressive' | 'empathetic';

export default function MarketingDeck({ cartridge, onDispatch, dispatching }: DeckProps) {
  const [intent, setIntent] = useState('');
  const [campaign, setCampaign] = useState<CampaignType>('content');
  const [platforms, setPlatforms] = useState<Set<Platform>>(new Set(['twitter', 'linkedin']));
  const [tone, setTone] = useState<MarketingTone>('professional');
  const [audience, setAudience] = useState('');
  const [roiFocus, setRoiFocus] = useState(true);

  const togglePlatform = (p: Platform) =>
    setPlatforms((prev) => {
      const n = new Set(prev);
      n.has(p) ? n.delete(p) : n.add(p);
      return n;
    });

  const submit = () =>
    onDispatch(intent, {
      campaign_type: campaign,
      platforms: [...platforms],
      tone,
      target_audience: audience,
      roi_focus: roiFocus,
    });

  return (
    <div className="space-y-5">
      <p className="text-xs text-slate-500">SIR_VALERIAN — Growth, campaigns, ROI maximization.</p>

      <div className="space-y-2">
        <label className="text-xs font-semibold uppercase tracking-widest text-orange-400">
          Campaign Brief
        </label>
        <textarea
          rows={3}
          placeholder="Describe the product, offer, or message to promote…"
          value={intent}
          onChange={(e) => setIntent(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) submit();
          }}
          className="w-full rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-2.5 text-sm text-slate-100 placeholder-slate-600 outline-none focus:border-orange-500 resize-none"
        />
      </div>

      <div>
        <label className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-2 block">
          Campaign Type
        </label>
        <div className="grid grid-cols-5 gap-1.5">
          {(['content', 'seo', 'social', 'email', 'paid'] as CampaignType[]).map((c) => (
            <button
              key={c}
              onClick={() => setCampaign(c)}
              className={cn(
                'rounded-lg border py-2 text-xs font-bold uppercase transition-colors',
                campaign === c
                  ? 'bg-orange-900/50 border-orange-500/50 text-orange-200'
                  : 'border-slate-700 text-slate-500 hover:border-slate-600',
              )}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-2 block">
          Platforms
        </label>
        <div className="flex gap-2 flex-wrap">
          {(['twitter', 'linkedin', 'instagram', 'tiktok', 'web'] as Platform[]).map((p) => (
            <button
              key={p}
              onClick={() => togglePlatform(p)}
              className={cn(
                'rounded px-2.5 py-1 text-xs font-semibold capitalize border transition-colors',
                platforms.has(p)
                  ? 'bg-orange-900/50 border-orange-500/40 text-orange-300'
                  : 'border-slate-700 text-slate-500 hover:border-slate-600',
              )}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="text-xs text-slate-500 mb-1 block">Target Audience</label>
        <input
          placeholder="e.g. B2B SaaS founders, Gen-Z consumers…"
          value={audience}
          onChange={(e) => setAudience(e.target.value)}
          className="w-full rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-300 placeholder-slate-600 outline-none focus:border-orange-500"
        />
      </div>

      <div className="flex flex-wrap gap-4">
        <div className="flex gap-1.5">
          {(['professional', 'casual', 'aggressive', 'empathetic'] as MarketingTone[]).map((t) => (
            <button
              key={t}
              onClick={() => setTone(t)}
              className={cn(
                'rounded px-2 py-1 text-xs font-semibold capitalize border transition-colors',
                tone === t
                  ? 'bg-orange-900/50 border-orange-500/40 text-orange-300'
                  : 'border-slate-700 text-slate-500',
              )}
            >
              {t}
            </button>
          ))}
        </div>
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={roiFocus}
            onChange={(e) => setRoiFocus(e.target.checked)}
            className="accent-orange-500"
          />
          <span className="text-xs text-slate-400">ROI-focused output</span>
        </label>
      </div>

      <button
        onClick={submit}
        disabled={dispatching || !intent.trim()}
        className="w-full flex items-center justify-center gap-2 rounded-xl bg-orange-700 hover:bg-orange-600 disabled:opacity-40 py-3 text-sm font-bold text-white transition-colors"
      >
        {dispatching ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <TrendingUp className="h-4 w-4" />
        )}
        {dispatching ? 'Strategizing…' : 'Dispatch to SIR_VALERIAN'}
      </button>
    </div>
  );
}
