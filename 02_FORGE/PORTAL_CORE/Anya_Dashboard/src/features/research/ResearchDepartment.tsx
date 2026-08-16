import React, { useState, useRef } from 'react';
import {
  FlaskConical,
  Send,
  ChevronDown,
  ChevronRight,
  BookOpen,
  Globe,
  Search,
  Cpu,
  CheckCircle2,
  Loader2,
  Copy,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { bifrostFetch } from '@/lib/bifrostClient';
import { runtimeConfig } from '@/config/runtime';
import { useAnyaSocket } from '@/features/brain/useAnyaSocket';
import EventFeed from '@/components/ui/EventFeed';

type SearchDepth = 'quick' | 'medium' | 'deep';
type SourceType = 'web' | 'github' | 'arxiv' | 'notebooklm';

interface ChimeraRound {
  id: string;
  knight: string;
  role: string;
  output: string;
}

interface ResearchResult {
  query: string;
  ancestor?: string;
  chimera_rounds: ChimeraRound[];
  synthesis: string;
  sources: string[];
  ts: number;
}

const ROUNDS_META = [
  {
    id: 'R1',
    knight: 'Sir Octavian',
    role: 'Semantic Audit',
    color: 'text-purple-300',
    border: 'border-purple-500/30',
  },
  {
    id: 'R2',
    knight: 'Merlin / Viden',
    role: 'Topology Shift',
    color: 'text-blue-300',
    border: 'border-blue-500/30',
  },
  {
    id: 'R3',
    knight: 'Sir Myrmidon',
    role: 'Anchor Compression',
    color: 'text-emerald-300',
    border: 'border-emerald-500/30',
  },
];

function CollapsiblePanel({
  title,
  color,
  border,
  children,
  defaultOpen = false,
}: {
  title: string;
  color: string;
  border: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className={cn('rounded-xl border', border, 'bg-slate-900/40')}>
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center gap-2 px-4 py-3 text-left"
      >
        {open ? (
          <ChevronDown className={cn('h-3.5 w-3.5', color)} />
        ) : (
          <ChevronRight className={cn('h-3.5 w-3.5', color)} />
        )}
        <span className={cn('text-sm font-semibold', color)}>{title}</span>
      </button>
      {open && <div className="px-4 pb-4">{children}</div>}
    </div>
  );
}

export default function ResearchDepartment() {
  const [query, setQuery] = useState('');
  const [depth, setDepth] = useState<SearchDepth>('medium');
  const [sources, setSources] = useState<Set<SourceType>>(new Set(['web', 'notebooklm']));
  const [chimeraEnabled, setChimeraEnabled] = useState(true);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<ResearchResult | null>(null);
  const [history, setHistory] = useState<ResearchResult[]>([]);
  const { events, isConnected } = useAnyaSocket();

  const toggleSource = (s: SourceType) =>
    setSources((prev) => {
      const next = new Set(prev);
      next.has(s) ? next.delete(s) : next.add(s);
      return next;
    });

  const run = async () => {
    if (!query.trim() || running) return;
    setRunning(true);
    setResult(null);
    try {
      const res = await bifrostFetch(runtimeConfig.bifrost.dispatchUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          intent: query.trim(),
          cartridge: 'RESEARCH',
          preferred_knight: 'LADY_APIS',
          params: { depth, sources: [...sources], chimera: chimeraEnabled },
        }),
      });
      if (res.ok) {
        const data = await res.json().catch(() => ({}));
        const built: ResearchResult = {
          query: query.trim(),
          ancestor: data.ancestor,
          chimera_rounds: data.chimera_rounds ?? [],
          synthesis: data.result ?? data.synthesis ?? '(Awaiting knight response via WebSocket…)',
          sources: data.sources_added ?? [],
          ts: Date.now(),
        };
        setResult(built);
        setHistory((h) => [built, ...h.slice(0, 9)]);
      }
    } catch {
      setResult({
        query: query.trim(),
        chimera_rounds: [],
        synthesis: 'Bifrost unreachable — ensure morgana_bridge is running on :8001',
        sources: [],
        ts: Date.now(),
      });
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="min-h-full p-6 space-y-5">
      {/* Header */}
      <div className="flex items-center gap-3">
        <FlaskConical className="h-6 w-6 text-blue-400" />
        <div>
          <h1 className="text-2xl font-black text-slate-100">Research Department</h1>
          <p className="text-xs text-slate-500">
            CHIMERA pipeline · LADY_APIS · NotebookLM ancestor synthesis
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* LEFT: Controls */}
        <div className="space-y-4">
          {/* Query */}
          <div className="rounded-xl border border-blue-500/30 bg-blue-950/20 p-4 space-y-3">
            <label className="text-xs font-semibold uppercase tracking-widest text-blue-400">
              Research Query
            </label>
            <textarea
              rows={4}
              placeholder="What do you want to research? Be specific for best CHIMERA results…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) run();
              }}
              className="w-full rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-100 placeholder-slate-600 outline-none focus:border-blue-500 resize-none"
            />
            <button
              onClick={run}
              disabled={running || !query.trim()}
              className="w-full flex items-center justify-center gap-2 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-40 py-2.5 text-sm font-semibold text-white transition-colors"
            >
              {running ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
              {running ? 'Running CHIMERA…' : 'Run Research'}
            </button>
          </div>

          {/* Settings */}
          <div className="rounded-xl border border-slate-700 bg-slate-900/40 p-4 space-y-3">
            <p className="text-xs font-semibold uppercase tracking-widest text-slate-500">
              Settings
            </p>

            <div>
              <label className="text-xs text-slate-500 mb-1.5 block">Search Depth</label>
              <div className="flex rounded-lg border border-slate-700 overflow-hidden">
                {(['quick', 'medium', 'deep'] as SearchDepth[]).map((d) => (
                  <button
                    key={d}
                    onClick={() => setDepth(d)}
                    className={cn(
                      'flex-1 py-1.5 text-xs font-semibold capitalize transition-colors',
                      depth === d ? 'bg-blue-700 text-white' : 'text-slate-400 hover:bg-slate-800',
                    )}
                  >
                    {d}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="text-xs text-slate-500 mb-1.5 block">Sources</label>
              <div className="flex flex-wrap gap-1.5">
                {(['web', 'github', 'arxiv', 'notebooklm'] as SourceType[]).map((s) => (
                  <button
                    key={s}
                    onClick={() => toggleSource(s)}
                    className={cn(
                      'rounded px-2 py-1 text-xs font-semibold capitalize transition-colors border',
                      sources.has(s)
                        ? 'bg-blue-900/60 border-blue-500/40 text-blue-300'
                        : 'border-slate-700 text-slate-500 hover:border-slate-600',
                    )}
                  >
                    {s === 'notebooklm' ? 'NLM' : s}
                  </button>
                ))}
              </div>
            </div>

            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={chimeraEnabled}
                onChange={(e) => setChimeraEnabled(e.target.checked)}
                className="accent-blue-500"
              />
              <span className="text-xs text-slate-400">CHIMERA 3-Round Refinement</span>
            </label>
          </div>

          {/* History */}
          {history.length > 0 && (
            <div className="rounded-xl border border-slate-700 bg-slate-900/40 p-4 space-y-2">
              <p className="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-2">
                History
              </p>
              {history.slice(0, 5).map((h, i) => (
                <button
                  key={i}
                  onClick={() => setResult(h)}
                  className="w-full text-left rounded-lg px-3 py-2 hover:bg-slate-800/50 transition-colors"
                >
                  <p className="text-xs font-medium text-slate-300 truncate">{h.query}</p>
                  <p className="text-[10px] text-slate-600">
                    {new Date(h.ts).toLocaleTimeString()}
                  </p>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* RIGHT: Results */}
        <div className="lg:col-span-2 space-y-4">
          {!result && !running && (
            <div className="rounded-xl border border-dashed border-slate-700 flex flex-col items-center justify-center py-20 text-center">
              <Search className="h-10 w-10 text-slate-700 mb-3" />
              <p className="text-sm text-slate-600">Run a query to see CHIMERA results here.</p>
              <p className="text-xs text-slate-700 mt-1">Ctrl+Enter to submit</p>
            </div>
          )}

          {running && (
            <div className="rounded-xl border border-blue-500/30 bg-blue-950/20 flex items-center justify-center py-16 gap-3">
              <Loader2 className="h-6 w-6 text-blue-400 animate-spin" />
              <span className="text-sm text-blue-300 font-semibold">CHIMERA pipeline running…</span>
            </div>
          )}

          {result && !running && (
            <div className="space-y-3">
              {/* Query label */}
              <div className="flex items-center gap-2 px-1">
                <Globe className="h-4 w-4 text-blue-400" />
                <span className="text-sm font-semibold text-slate-200">"{result.query}"</span>
                <span className="ml-auto text-[10px] text-slate-600">
                  {new Date(result.ts).toLocaleTimeString()}
                </span>
              </div>

              {/* Ancestor */}
              {result.ancestor && (
                <CollapsiblePanel
                  title="NotebookLM Ancestor"
                  color="text-fuchsia-300"
                  border="border-fuchsia-500/30"
                >
                  <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap">
                    {result.ancestor}
                  </p>
                </CollapsiblePanel>
              )}

              {/* CHIMERA rounds */}
              {result.chimera_rounds.length > 0 &&
                ROUNDS_META.map((meta, i) => {
                  const round = result.chimera_rounds[i];
                  if (!round) return null;
                  return (
                    <CollapsiblePanel
                      key={meta.id}
                      title={`${meta.id} — ${meta.knight}: ${meta.role}`}
                      color={meta.color}
                      border={meta.border}
                    >
                      <p className="text-sm text-slate-300 leading-relaxed whitespace-pre-wrap">
                        {round.output}
                      </p>
                    </CollapsiblePanel>
                  );
                })}

              {/* Synthesis */}
              <div className="rounded-xl border border-emerald-500/30 bg-emerald-950/20 p-4">
                <div className="flex items-center gap-2 mb-3">
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                  <span className="text-sm font-semibold text-emerald-300">Final Synthesis</span>
                  <button
                    onClick={() => navigator.clipboard.writeText(result.synthesis)}
                    className="ml-auto text-slate-600 hover:text-slate-400 transition-colors"
                  >
                    <Copy className="h-3.5 w-3.5" />
                  </button>
                </div>
                <p className="text-sm text-slate-200 leading-relaxed whitespace-pre-wrap">
                  {result.synthesis}
                </p>
              </div>

              {/* Sources */}
              {result.sources.length > 0 && (
                <CollapsiblePanel
                  title={`Sources (${result.sources.length})`}
                  color="text-slate-400"
                  border="border-slate-700"
                >
                  <ul className="space-y-1">
                    {result.sources.map((s, i) => (
                      <li key={i} className="flex items-center gap-2 text-xs text-blue-400">
                        <BookOpen className="h-3 w-3 shrink-0 text-slate-600" />
                        <a
                          href={s}
                          target="_blank"
                          rel="noreferrer"
                          className="truncate hover:underline"
                        >
                          {s}
                        </a>
                      </li>
                    ))}
                  </ul>
                </CollapsiblePanel>
              )}
            </div>
          )}

          {/* Live feed */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-3 h-40 overflow-hidden">
            <EventFeed
              events={events}
              isConnected={isConnected}
              maxRows={15}
              compact
              filterSource="research"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
