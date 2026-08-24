import React, { useCallback, useEffect, useState } from 'react';
import { Check, Loader2, Settings2, ShieldAlert } from 'lucide-react';
import { cn } from '@/lib/utils';
import { bifrostFetch } from '@/lib/bifrostClient';
import { runtimeConfig } from '@/config/runtime';

interface CognitiveConfig {
  sync_interval: number;
  sync_query?: string;
}

type LoadState = 'idle' | 'loading' | 'ok' | 'error';
type SaveState = 'idle' | 'saving' | 'saved' | 'error';

/**
 * Config surface — reads/writes cognitive_service's /config (proxied through
 * go_router at /cognitive/config). Exposes the //sync cadence and the query
 * text used for periodic syncs; the backend persists whatever it's given to
 * disk and the scheduler picks up changes live.
 */
export default function ConfigPanel() {
  const [config, setConfig] = useState<CognitiveConfig | null>(null);
  const [loadState, setLoadState] = useState<LoadState>('idle');
  const [saveState, setSaveState] = useState<SaveState>('idle');
  const [draftInterval, setDraftInterval] = useState('');
  const [draftQuery, setDraftQuery] = useState('');

  const fetchConfig = useCallback(async () => {
    setLoadState('loading');
    try {
      const res = await bifrostFetch(runtimeConfig.cognitive.configUrl, {
        signal: AbortSignal.timeout(5000),
      });
      if (!res.ok) throw new Error(`${res.status}`);
      const data: CognitiveConfig = await res.json();
      setConfig(data);
      setDraftInterval(String(data.sync_interval));
      setDraftQuery(data.sync_query ?? '');
      setLoadState('ok');
    } catch {
      setLoadState('error');
    }
  }, []);

  useEffect(() => { fetchConfig(); }, [fetchConfig]);

  const save = useCallback(async () => {
    const parsed = Number(draftInterval);
    if (!Number.isFinite(parsed) || parsed < 0 || !draftQuery.trim()) {
      setSaveState('error');
      return;
    }
    setSaveState('saving');
    try {
      const res = await bifrostFetch(runtimeConfig.cognitive.configUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sync_interval: parsed, sync_query: draftQuery }),
        signal: AbortSignal.timeout(5000),
      });
      if (!res.ok) throw new Error(`${res.status}`);
      const data: CognitiveConfig = await res.json();
      setConfig(data);
      setDraftInterval(String(data.sync_interval));
      setDraftQuery(data.sync_query ?? '');
      setSaveState('saved');
    } catch {
      setSaveState('error');
    }
  }, [draftInterval, draftQuery]);

  const dirty = config !== null && (
    draftInterval !== String(config.sync_interval) ||
    draftQuery !== (config.sync_query ?? '')
  );

  return (
    <div className="rounded-xl border border-slate-800/60 bg-slate-900/60 p-4">
      <h2 className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-3 flex items-center gap-2">
        <Settings2 className="h-3.5 w-3.5" /> Config
      </h2>

      {loadState === 'loading' && !config && (
        <div className="flex items-center justify-center py-8 text-slate-600">
          <Loader2 className="h-4 w-4 animate-spin mr-2" /> Loading config…
        </div>
      )}

      {loadState === 'error' && !config && (
        <div className="flex items-center gap-2 rounded-lg border border-red-900/50 bg-red-950/20 p-3 text-red-400 text-xs">
          <ShieldAlert className="h-4 w-4 shrink-0" />
          Cognitive Service unreachable via /cognitive/config
        </div>
      )}

      {config && (
        <div className="space-y-3">
          <label className="block">
            <span className="text-[10px] uppercase tracking-widest text-slate-600 mb-1.5 block">
              //sync interval (seconds, 0 = off)
            </span>
            <input
              type="number"
              min={0}
              step="any"
              value={draftInterval}
              onChange={(e) => { setDraftInterval(e.target.value); setSaveState('idle'); }}
              className="w-32 rounded-lg border border-slate-700 bg-slate-950/60 px-2.5 py-1.5 text-sm text-slate-200 font-mono focus:outline-none focus:border-fuchsia-500/60"
            />
          </label>

          <label className="block">
            <span className="text-[10px] uppercase tracking-widest text-slate-600 mb-1.5 block">
              //sync query
            </span>
            <input
              type="text"
              value={draftQuery}
              onChange={(e) => { setDraftQuery(e.target.value); setSaveState('idle'); }}
              className="w-full rounded-lg border border-slate-700 bg-slate-950/60 px-2.5 py-1.5 text-sm text-slate-200 focus:outline-none focus:border-fuchsia-500/60"
            />
          </label>

          <div className="flex items-center gap-2">
            <button
              onClick={save}
              disabled={!dirty || saveState === 'saving'}
              className={cn(
                'rounded-lg border px-3 py-1.5 text-xs font-semibold transition-colors disabled:opacity-40',
                'border-fuchsia-500/40 bg-fuchsia-950/30 text-fuchsia-300 hover:brightness-125',
              )}
            >
              {saveState === 'saving' ? <Loader2 className="h-3 w-3 animate-spin" /> : 'Save'}
            </button>
            {saveState === 'saved' && !dirty && (
              <Check className="h-4 w-4 text-emerald-400" aria-label="Saved" />
            )}
          </div>

          {saveState === 'error' && (
            <p className="text-[10px] text-red-400">Failed to save — check the values and try again.</p>
          )}
        </div>
      )}
    </div>
  );
}
