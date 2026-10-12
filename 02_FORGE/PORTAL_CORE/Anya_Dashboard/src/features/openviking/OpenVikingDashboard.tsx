import { runtimeConfig } from '@/config/runtime';
import { useDisplayProfile } from '@/hooks/useDisplayProfile';
import { bifrostFetch, bifrostWebSocketUrl } from '@/lib/bifrostClient';
import {
  Activity,
  BrainCircuit,
  CheckCircle2,
  ChevronRight,
  Cpu,
  Database,
  ExternalLink,
  File,
  FileText,
  Folder,
  GitBranch,
  HelpCircle,
  LayoutPanelTop,
  Map,
  Radio,
  RefreshCw,
  Search,
  ShieldCheck,
  SplitSquareHorizontal,
  TerminalSquare,
  X,
} from 'lucide-react';
import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useAnyaSocket } from '../brain/useAnyaSocket';

const MAP_URL = runtimeConfig.bifrost.openVikingMapUrl;
const GRADIO_URL = runtimeConfig.gradioUrl;

type ViewMode = 'bridge' | 'sandbox' | 'map' | 'raw';

interface OpenVikingMapPayload {
  name: string;
  path: string;
  bytes: number;
  modified_ms: number;
  line_count: number;
  section_count: number;
  directory_markers: number;
  preview: string;
  content: string;
  error?: string;
}

interface TreeEntry {
  id: string;
  name: string;
  depth: number;
  kind: 'folder' | 'file';
  raw: string;
  line: number;
  core: boolean;
}

function formatBytes(bytes: number) {
  if (bytes > 1024 * 1024) return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
  if (bytes > 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${bytes} B`;
}

function formatModified(ms: number) {
  if (!ms) return 'unknown';
  return new Date(ms).toLocaleString();
}

function normalizeMapLine(line: string) {
  return line
    .replace(/[^\x20-\x7E]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

function extractHeadings(content: string) {
  return content
    .split('\n')
    .filter((line) => line.startsWith('## '))
    .map((line) => line.replace(/^##\s+/, '').trim())
    .slice(0, 16);
}

function extractRows(content: string, query: string) {
  const normalized = query.trim().toLowerCase();
  return content
    .split('\n')
    .map((line, index) => ({ line, index: index + 1 }))
    .filter(({ line }) => {
      if (!line.trim()) return false;
      if (!normalized) {
        return (
          line.startsWith('|') ||
          line.startsWith('## ') ||
          line.includes('[CORE]') ||
          line.includes('LOCAL') ||
          line.includes('CLOUD')
        );
      }
      return line.toLowerCase().includes(normalized);
    })
    .slice(0, 80);
}

function extractFileTree(content: string) {
  const lines = content.split('\n');
  const start = lines.findIndex((line) => line.includes('DIRECTORY TREE'));
  const source = start >= 0 ? lines.slice(start + 1) : lines;

  return source
    .map((raw, offset): TreeEntry | null => {
      const clean = normalizeMapLine(raw);
      if (!clean || clean === '---' || clean.startsWith('#')) return null;
      const isFile = clean.startsWith('- ');
      const looksLikeFolder =
        clean.includes('/') || clean.includes('[CORE]') || clean.endsWith(':');
      if (!isFile && !looksLikeFolder) return null;

      const depth = Math.min(Math.floor((raw.match(/^\s*/)?.[0].length ?? 0) / 2), 12);
      const name = clean.replace(/^- /, '').replace(/^ /, '');
      return {
        id: `${start + offset + 2}-${name}`,
        name,
        depth,
        kind: isFile ? 'file' : 'folder',
        raw,
        line: start + offset + 2,
        core: clean.includes('[CORE]') || clean.includes('EXCALIBUR') || clean.includes('KERNEL'),
      };
    })
    .filter((entry): entry is TreeEntry => Boolean(entry))
    .slice(0, 420);
}

function systemSignals(content: string) {
  const signals = [
    { label: 'Modal Brain', key: 'MODAL_BRAIN' },
    { label: 'NotebookLM', key: 'CLOUD_BRAIN' },
    { label: 'Excalibur', key: 'EXCALIBUR' },
    { label: 'Kinetic Edge', key: 'KINETIC_EDGE' },
    { label: 'Forge UI', key: 'FORGE_UI' },
    { label: 'Vault', key: 'VAULT' },
    { label: 'Bifrost', key: 'Bifrost' },
    { label: 'Saltare', key: 'Saltare' },
  ];

  return signals.map((signal) => ({
    ...signal,
    active: content.includes(signal.key),
  }));
}

function GradioFrame({ compact = false }: { compact?: boolean }) {
  return (
    <div className="flex h-full min-h-0 flex-col overflow-hidden rounded-[1.5rem] border border-fuchsia-400/25 bg-black shadow-2xl shadow-fuchsia-950/30">
      <div className="flex shrink-0 items-center justify-between border-b border-fuchsia-400/20 bg-white/[0.04] px-4 py-3">
        <div>
          <p className="text-xs font-black uppercase tracking-[0.24em] text-fuchsia-200">
            Embedded Gradio Sandbox
          </p>
          <p className="text-sm font-bold text-slate-300">{GRADIO_URL}</p>
        </div>
        <a
          href={GRADIO_URL}
          target="_blank"
          rel="noreferrer"
          aria-label="Open Gradio sandbox in a new browser tab"
          className="rounded-xl border border-fuchsia-300/20 bg-fuchsia-300/10 p-2 text-fuchsia-100 transition hover:bg-fuchsia-300/20"
        >
          <ExternalLink className="h-4 w-4" />
        </a>
      </div>
      <iframe
        title="OpenViking Gradio Sandbox"
        src={GRADIO_URL}
        className={`${compact ? 'min-h-[300px]' : 'min-h-[520px]'} min-h-0 w-full flex-1 bg-white`}
      />
    </div>
  );
}

export default function OpenVikingDashboard() {
  const display = useDisplayProfile();
  const syncingRef = useRef(false);
  const [mapPayload, setMapPayload] = useState<OpenVikingMapPayload | null>(null);
  const [error, setError] = useState('');
  const [lastSync, setLastSync] = useState('');
  const [isSyncing, setIsSyncing] = useState(false);
  const [query, setQuery] = useState('EXCALIBUR');
  const [treeQuery, setTreeQuery] = useState('');
  const [selectedEntry, setSelectedEntry] = useState<TreeEntry | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('bridge');
  const [showGuide, setShowGuide] = useState(true);
  const { isConnected, latestEvent } = useAnyaSocket(bifrostWebSocketUrl());

  async function syncMap() {
    if (syncingRef.current) return;
    syncingRef.current = true;
    setIsSyncing(true);
    try {
      const response = await bifrostFetch(MAP_URL, { cache: 'no-store' });
      const data = (await response.json()) as OpenVikingMapPayload;
      if (!response.ok || data.error) throw new Error(data.error || `map ${response.status}`);
      setMapPayload(data);
      setError('');
      setLastSync(
        new Date().toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
        }),
      );
    } catch (syncError) {
      setError(syncError instanceof Error ? syncError.message : 'OpenViking map sync failed');
    } finally {
      syncingRef.current = false;
      setIsSyncing(false);
    }
  }

  useEffect(() => {
    syncMap();
    const timer = window.setInterval(syncMap, 7000);
    return () => window.clearInterval(timer);
  }, []);

  const content = mapPayload?.content ?? '';
  const headings = useMemo(() => extractHeadings(content), [content]);
  const rows = useMemo(() => extractRows(content, query), [content, query]);
  const tree = useMemo(() => extractFileTree(content), [content]);
  const visibleTree = useMemo(() => {
    const needle = treeQuery.trim().toLowerCase();
    if (!needle) return tree.slice(0, 220);
    return tree.filter((entry) => entry.name.toLowerCase().includes(needle)).slice(0, 220);
  }, [tree, treeQuery]);
  const signals = useMemo(() => systemSignals(content), [content]);
  const latestEventText = latestEvent
    ? `${latestEvent.event} | ${latestEvent.source ?? 'bridge'}`
    : 'waiting for bridge pulse';
  const viewDescriptions: Record<ViewMode, string> = {
    bridge:
      'Use this when you want the full command bridge: Gradio sandbox beside the live Camelot file map.',
    sandbox: 'Use this when you only need the Gradio brain sandbox without the map taking space.',
    map: 'Use this to inspect the live entiremap.md structure, search nodes, and inspect file lines.',
    raw: 'Use this when you need the terminal-style source mirror of the full map file.',
  };

  useEffect(() => {
    if (!selectedEntry && visibleTree.length > 0) setSelectedEntry(visibleTree[0]);
  }, [selectedEntry, visibleTree]);

  const metrics = [
    {
      label: 'Map Size',
      value: mapPayload ? formatBytes(mapPayload.bytes) : 'offline',
      icon: FileText,
    },
    { label: 'Nodes', value: tree.length || '--', icon: GitBranch },
    { label: 'Lines', value: mapPayload?.line_count ?? '--', icon: TerminalSquare },
    { label: 'Bridge', value: isConnected ? 'live' : 'offline', icon: Radio },
  ];
  const shellPad = display.compact ? 'px-2 pb-2 pt-2' : 'px-4 pb-3 pt-4 lg:px-8';
  const headerTitle = display.compact ? 'text-2xl' : 'text-3xl md:text-5xl';
  const cockpitRows = display.compact
    ? 'grid-rows-[auto_auto_minmax(0,1fr)]'
    : display.lowHeight
      ? 'grid-rows-[auto_auto_minmax(0,1fr)]'
      : 'grid-rows-[auto_auto_minmax(0,1fr)]';

  return (
    <div className="h-full min-h-0 overflow-hidden bg-[#050208] text-slate-100">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_50%_12%,rgba(217,70,239,0.26),transparent_34%),radial-gradient(circle_at_15%_20%,rgba(6,182,212,0.16),transparent_30%),linear-gradient(115deg,rgba(2,6,23,0.98),rgba(25,5,38,0.95))]" />
      <div className="pointer-events-none fixed inset-0 opacity-[0.13] [background-image:linear-gradient(rgba(217,70,239,.7)_1px,transparent_1px),linear-gradient(90deg,rgba(217,70,239,.7)_1px,transparent_1px)] [background-size:42px_42px]" />

      <main
        className={`relative mx-auto grid h-full min-h-0 max-w-[1600px] ${cockpitRows} gap-3 ${shellPad}`}
      >
        <header className="min-h-0 shrink-0 overflow-hidden rounded-[1.5rem] border border-fuchsia-300/25 bg-black/45 shadow-2xl shadow-fuchsia-950/35 backdrop-blur">
          <div
            className={`${display.compact ? 'px-4 py-3' : 'px-6 py-5'} border-b border-fuchsia-300/20`}
          >
            <div className="flex flex-wrap items-center justify-between gap-5">
              <div className="flex items-center gap-4">
                <div
                  className={`${display.compact ? 'h-11 w-11' : 'h-16 w-16'} grid place-items-center rounded-2xl bg-fuchsia-500 text-white shadow-lg shadow-fuchsia-500/30`}
                >
                  <BrainCircuit className={display.compact ? 'h-6 w-6' : 'h-9 w-9'} />
                </div>
                <div>
                  <p className="text-xs font-black uppercase tracking-[0.34em] text-fuchsia-200">
                    Camelot-OS OpenViking
                  </p>
                  <h1 className={`${headerTitle} font-black tracking-tight`}>
                    Throne Room Virtual CPU
                  </h1>
                  <p
                    className={`${display.compact ? 'hidden' : 'block'} mt-2 max-w-5xl text-sm leading-6 text-slate-400`}
                  >
                    Starship command bridge meets Matrix core: Gradio sandbox, Bifrost telemetry,
                    and an interactive live file structure synced from `entiremap.md`.
                  </p>
                </div>
              </div>
              <button
                onClick={syncMap}
                className="flex items-center gap-2 rounded-xl border border-fuchsia-300/30 bg-fuchsia-300/10 px-5 py-3 text-xs font-black uppercase tracking-[0.2em] text-fuchsia-100 shadow-lg shadow-fuchsia-950/30 transition hover:bg-fuchsia-300/20"
              >
                <RefreshCw className={`h-4 w-4 ${isSyncing ? 'animate-spin' : ''}`} />
                Sync Entire Map
              </button>
            </div>
          </div>

          <div className={`${display.compact ? 'hidden' : 'grid'} gap-3 p-4 md:grid-cols-4`}>
            {metrics.map((metric) => {
              const Icon = metric.icon;
              return (
                <div
                  key={metric.label}
                  className="rounded-2xl border border-white/10 bg-white/[0.04] p-4"
                >
                  <div className="mb-3 flex items-center justify-between">
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
                      {metric.label}
                    </p>
                    <Icon className="h-5 w-5 text-fuchsia-200" />
                  </div>
                  <p className="text-2xl font-black">{metric.value}</p>
                </div>
              );
            })}
          </div>
        </header>

        <section className="grid min-h-0 shrink-0 gap-3 xl:grid-cols-[0.74fr_1.26fr]">
          <VirtualCpu
            signals={signals}
            selectedEntry={selectedEntry}
            isConnected={isConnected}
            lastSync={lastSync}
            latestEventText={latestEventText}
            compact={display.compact || display.lowHeight}
          />

          <div className="rounded-[1.5rem] border border-fuchsia-300/20 bg-black/45 p-3 shadow-2xl shadow-fuchsia-950/20 backdrop-blur">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div
                role="tablist"
                aria-label="OpenViking display mode"
                className="flex flex-wrap gap-2"
              >
                {[
                  { id: 'bridge' as const, label: 'Bridge', icon: SplitSquareHorizontal },
                  { id: 'sandbox' as const, label: 'Sandbox', icon: LayoutPanelTop },
                  { id: 'map' as const, label: 'Map', icon: Map },
                  { id: 'raw' as const, label: 'Raw', icon: TerminalSquare },
                ].map((mode) => {
                  const Icon = mode.icon;
                  const active = viewMode === mode.id;
                  return (
                    <button
                      key={mode.id}
                      role="tab"
                      aria-selected={active}
                      onClick={() => setViewMode(mode.id)}
                      className={`flex items-center gap-2 rounded-xl px-4 py-3 text-sm font-bold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300 ${
                        active
                          ? 'bg-fuchsia-500 text-white shadow-lg shadow-fuchsia-950/40'
                          : 'bg-white/[0.06] text-slate-400 hover:bg-white/[0.1] hover:text-slate-100'
                      }`}
                    >
                      <Icon className="h-4 w-4" />
                      {mode.label}
                    </button>
                  );
                })}
              </div>

              <div className="flex flex-wrap items-center gap-3 text-xs font-semibold text-slate-500">
                <span>Last sync: {lastSync || 'pending'}</span>
                <span className={display.compact ? 'hidden' : ''}>
                  Modified: {formatModified(mapPayload?.modified_ms ?? 0)}
                </span>
                <span className={isConnected ? 'text-cyan-300' : 'text-amber-300'}>
                  {latestEventText}
                </span>
                <span className="rounded-full border border-white/10 px-2 py-1 text-slate-400">
                  {display.displayClass}:{display.width}x{display.height}
                </span>
              </div>
            </div>
            <div className="mt-3 flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-white/10 bg-white/[0.035] px-4 py-3">
              <p className="text-sm font-semibold leading-6 text-slate-300">
                {viewDescriptions[viewMode]}
              </p>
              <button
                onClick={() => setShowGuide((current) => !current)}
                className="flex items-center gap-2 rounded-xl border border-cyan-300/20 bg-cyan-300/10 px-3 py-2 text-xs font-black uppercase tracking-[0.16em] text-cyan-100 transition hover:bg-cyan-300/20 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300"
              >
                <HelpCircle className="h-4 w-4" />
                {showGuide ? 'Hide Guide' : 'Show Guide'}
              </button>
            </div>
          </div>
        </section>

        {error && (
          <p className="rounded-2xl border border-red-400/30 bg-red-500/10 p-4 text-sm font-semibold text-red-200">
            {error}
          </p>
        )}

        <div className={`min-h-0 ${display.compact ? 'overflow-y-auto' : 'overflow-hidden'}`}>
          {showGuide && (
            <section className="mb-3 rounded-[1.5rem] border border-cyan-300/20 bg-cyan-300/10 p-4 shadow-2xl shadow-cyan-950/15">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className="text-xs font-black uppercase tracking-[0.24em] text-cyan-200">
                    Operator Guide
                  </p>
                  <h2 className="mt-1 text-xl font-black">Start here</h2>
                  <p className="mt-2 max-w-4xl text-sm leading-6 text-slate-300">
                    Press <span className="font-black text-fuchsia-100">Sync Entire Map</span> to
                    refresh `entiremap.md`, then use Map to inspect the system tree or Bridge to
                    work with Gradio and the map together.
                  </p>
                </div>
                <button
                  onClick={() => setShowGuide(false)}
                  aria-label="Dismiss OpenViking operator guide"
                  className="rounded-xl border border-white/10 bg-black/30 p-2 text-slate-400 transition hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
              <div className="mt-4 grid gap-2 sm:grid-cols-3">
                <button
                  onClick={() => setViewMode('bridge')}
                  className="rounded-2xl border border-fuchsia-300/20 bg-black/30 px-4 py-3 text-left transition hover:bg-fuchsia-300/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-300"
                >
                  <p className="font-black text-fuchsia-100">Bridge Mode</p>
                  <p className="mt-1 text-xs leading-5 text-slate-400">
                    Sandbox plus live file map.
                  </p>
                </button>
                <button
                  onClick={() => setViewMode('map')}
                  className="rounded-2xl border border-cyan-300/20 bg-black/30 px-4 py-3 text-left transition hover:bg-cyan-300/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300"
                >
                  <p className="font-black text-cyan-100">Map Mode</p>
                  <p className="mt-1 text-xs leading-5 text-slate-400">
                    Inspect nodes and search Camelot.
                  </p>
                </button>
                <button
                  onClick={syncMap}
                  className="rounded-2xl border border-emerald-300/20 bg-black/30 px-4 py-3 text-left transition hover:bg-emerald-300/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-300"
                >
                  <p className="font-black text-emerald-100">Refresh Brain Map</p>
                  <p className="mt-1 text-xs leading-5 text-slate-400">
                    Pull the latest terminal map.
                  </p>
                </button>
              </div>
            </section>
          )}
          {viewMode === 'bridge' && (
            <section
              className={`${display.compact ? 'h-auto overflow-visible' : 'h-full overflow-hidden'} grid min-h-0 gap-4 lg:grid-cols-[0.9fr_1.1fr]`}
            >
              <GradioFrame compact={display.compact || display.lowHeight} />
              <MapExplorer
                headings={headings}
                rows={rows}
                query={query}
                setQuery={setQuery}
                signals={signals}
                mapPayload={mapPayload}
                visibleTree={visibleTree}
                treeQuery={treeQuery}
                setTreeQuery={setTreeQuery}
                selectedEntry={selectedEntry}
                setSelectedEntry={setSelectedEntry}
                compact={display.compact || display.lowHeight}
              />
            </section>
          )}

          {viewMode === 'sandbox' && <GradioFrame compact={display.compact || display.lowHeight} />}

          {viewMode === 'map' && (
            <MapExplorer
              headings={headings}
              rows={rows}
              query={query}
              setQuery={setQuery}
              signals={signals}
              mapPayload={mapPayload}
              visibleTree={visibleTree}
              treeQuery={treeQuery}
              setTreeQuery={setTreeQuery}
              selectedEntry={selectedEntry}
              setSelectedEntry={setSelectedEntry}
              expanded
              compact={display.compact || display.lowHeight}
            />
          )}

          {viewMode === 'raw' && (
            <section
              className={`${display.compact ? 'h-auto' : 'h-full min-h-0 overflow-hidden'} flex flex-col rounded-[2rem] border border-fuchsia-300/20 bg-black/60 p-5 shadow-2xl shadow-fuchsia-950/20 backdrop-blur`}
            >
              <div className="mb-4 flex items-center justify-between gap-4">
                <div>
                  <p className="text-xs font-bold uppercase tracking-[0.26em] text-fuchsia-200">
                    Raw Brain Map
                  </p>
                  <h2 className="text-2xl font-black">Terminal Mirror</h2>
                </div>
                <p className="max-w-xl text-right text-xs leading-5 text-slate-500">
                  {mapPayload?.path ?? 'C:\\Users\\vizio\\CAMELOT_OS\\entiremap.md'}
                </p>
              </div>
              <pre
                className={`${display.compact ? 'max-h-[58dvh]' : 'min-h-0 flex-1'} overflow-auto rounded-2xl border border-fuchsia-300/20 bg-slate-950 p-4 text-xs leading-5 text-cyan-100`}
              >
                {mapPayload?.content ?? 'Waiting for entiremap.md sync...'}
              </pre>
            </section>
          )}
        </div>
      </main>
    </div>
  );
}

function VirtualCpu({
  signals,
  selectedEntry,
  isConnected,
  lastSync,
  latestEventText,
  compact,
}: {
  signals: Array<{ label: string; key: string; active: boolean }>;
  selectedEntry: TreeEntry | null;
  isConnected: boolean;
  lastSync: string;
  latestEventText: string;
  compact: boolean;
}) {
  const activeSignals = signals.filter((signal) => signal.active).length;

  return (
    <section
      className={`${compact ? 'min-h-[172px]' : 'min-h-[300px]'} relative overflow-hidden rounded-[1.5rem] border border-fuchsia-300/25 bg-black/55 p-4 shadow-2xl shadow-fuchsia-950/40 backdrop-blur`}
    >
      <div className="absolute inset-x-8 top-10 h-32 rounded-[50%] border border-fuchsia-400/25 bg-fuchsia-500/10 blur-sm" />
      <div
        className={`${compact ? 'top-10 h-40 w-28' : 'top-12 h-64 w-40'} absolute left-1/2 -translate-x-1/2 rounded-t-[5rem] bg-gradient-to-b from-slate-950 via-black to-black shadow-[0_0_80px_rgba(217,70,239,0.42)]`}
      />
      <div
        className={`${compact ? 'top-12 h-16 w-16' : 'top-16 h-24 w-24'} absolute left-1/2 -translate-x-1/2 rounded-full bg-black shadow-[0_0_35px_rgba(6,182,212,0.28)]`}
      />
      <div
        className={`${compact ? 'top-20 h-3 w-20' : 'top-28 h-4 w-32'} absolute left-1/2 -translate-x-1/2 rounded-full border border-cyan-200/50 bg-cyan-200/10`}
      />
      <div
        className={`${compact ? 'top-24' : 'top-36'} absolute inset-x-0 h-px bg-fuchsia-400/40 shadow-[0_0_24px_rgba(217,70,239,0.9)]`}
      />

      <div className="relative z-10 flex h-full flex-col justify-between gap-8">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs font-black uppercase tracking-[0.3em] text-fuchsia-200">
              Virtual CPU
            </p>
            <h2 className="mt-2 text-3xl font-black">Camelot Core</h2>
          </div>
          <div
            className={`rounded-full px-3 py-2 text-xs font-black uppercase tracking-[0.18em] ${isConnected ? 'bg-cyan-300/15 text-cyan-200' : 'bg-amber-300/15 text-amber-200'}`}
          >
            {isConnected ? 'online' : 'offline'}
          </div>
        </div>

        <div
          className={`${compact ? 'hidden' : 'grid'} gap-3 md:grid-cols-3 xl:grid-cols-1 2xl:grid-cols-3`}
        >
          <div className="rounded-2xl border border-white/10 bg-black/60 p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Mapped Systems</p>
            <p className="mt-2 text-3xl font-black text-cyan-100">
              {activeSignals}/{signals.length}
            </p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-black/60 p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Selected Node</p>
            <p className="mt-2 truncate text-lg font-black text-fuchsia-100">
              {selectedEntry?.name ?? 'none'}
            </p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-black/60 p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Sync Pulse</p>
            <p className="mt-2 text-lg font-black text-emerald-100">{lastSync || 'pending'}</p>
          </div>
        </div>

        <div
          className={`${compact ? 'hidden' : 'block'} rounded-2xl border border-cyan-300/20 bg-cyan-300/10 p-4`}
        >
          <div className="mb-2 flex items-center gap-2">
            <Cpu className="h-4 w-4 text-cyan-200" />
            <p className="text-xs font-black uppercase tracking-[0.24em] text-cyan-200">
              Bridge Event
            </p>
          </div>
          <p className="text-sm leading-6 text-slate-300">{latestEventText}</p>
        </div>
      </div>
    </section>
  );
}

function MapExplorer({
  headings,
  rows,
  query,
  setQuery,
  signals,
  mapPayload,
  visibleTree,
  treeQuery,
  setTreeQuery,
  selectedEntry,
  setSelectedEntry,
  expanded = false,
  compact = false,
}: {
  headings: string[];
  rows: Array<{ line: string; index: number }>;
  query: string;
  setQuery: (query: string) => void;
  signals: Array<{ label: string; key: string; active: boolean }>;
  mapPayload: OpenVikingMapPayload | null;
  visibleTree: TreeEntry[];
  treeQuery: string;
  setTreeQuery: (query: string) => void;
  selectedEntry: TreeEntry | null;
  setSelectedEntry: (entry: TreeEntry) => void;
  expanded?: boolean;
  compact?: boolean;
}) {
  return (
    <section
      className={`${compact ? 'h-auto overflow-visible' : 'h-full min-h-0 overflow-auto'} grid gap-5 ${expanded ? '2xl:grid-cols-[0.88fr_1.12fr]' : ''}`}
    >
      <div className="min-h-0 rounded-[2rem] border border-fuchsia-300/20 bg-black/55 p-5 shadow-2xl shadow-fuchsia-950/20 backdrop-blur">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.26em] text-fuchsia-200">
              Interactive File Structure
            </p>
            <h2 className="text-2xl font-black">OpenViking Navigator</h2>
          </div>
          <ShieldCheck className="h-6 w-6 text-cyan-200" />
        </div>

        <div className={`${compact ? 'hidden' : 'mb-4 grid'} gap-3 md:grid-cols-3`}>
          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">Markers</p>
            <p className="mt-2 text-2xl font-black">{mapPayload?.directory_markers ?? '--'}</p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">
              Selected Line
            </p>
            <p className="mt-2 text-2xl font-black">{selectedEntry?.line ?? '--'}</p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">Kind</p>
            <p className="mt-2 text-2xl font-black">{selectedEntry?.kind ?? '--'}</p>
          </div>
        </div>

        <div className="mb-4 flex items-center gap-2 rounded-2xl border border-fuchsia-300/20 bg-slate-950 px-3 py-2">
          <Search className="h-4 w-4 text-fuchsia-200" />
          <input
            value={treeQuery}
            onChange={(event) => setTreeQuery(event.target.value)}
            placeholder="Search file structure: EXCALIBUR, forge, vault..."
            className="w-full bg-transparent py-2 text-sm text-slate-100 outline-none placeholder:text-slate-600"
          />
        </div>

        <div className="grid min-h-0 gap-4 xl:grid-cols-[1fr_0.9fr]">
          <div
            className={`${compact ? 'max-h-[280px]' : 'max-h-[46dvh]'} overflow-auto rounded-2xl border border-fuchsia-300/20 bg-slate-950 p-3 font-mono text-xs`}
          >
            {visibleTree.length === 0 ? (
              <p className="p-3 text-slate-500">No file structure rows yet.</p>
            ) : (
              visibleTree.map((entry) => {
                const Icon = entry.kind === 'folder' ? Folder : File;
                const active = selectedEntry?.id === entry.id;
                return (
                  <button
                    key={entry.id}
                    onClick={() => setSelectedEntry(entry)}
                    className={`grid w-full grid-cols-[1rem_1.25rem_1fr] items-center gap-2 rounded-lg px-2 py-1.5 text-left transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300 ${
                      active
                        ? 'bg-fuchsia-500/20 text-fuchsia-100'
                        : 'text-slate-300 hover:bg-white/10'
                    }`}
                    style={{ paddingLeft: `${8 + entry.depth * 12}px` }}
                  >
                    <ChevronRight
                      className={`h-3 w-3 ${active ? 'text-cyan-200 opacity-100' : 'opacity-20'}`}
                    />
                    <Icon
                      className={`h-4 w-4 ${entry.core ? 'text-cyan-200' : entry.kind === 'folder' ? 'text-fuchsia-200' : 'text-slate-500'}`}
                    />
                    <span className="truncate">{entry.name}</span>
                  </button>
                );
              })
            )}
          </div>

          <div className="rounded-2xl border border-cyan-300/20 bg-cyan-300/10 p-4">
            <div className="mb-4 flex items-center gap-2">
              <Database className="h-5 w-5 text-cyan-200" />
              <h3 className="font-black">Node Inspector</h3>
            </div>
            {selectedEntry ? (
              <div className="space-y-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Name</p>
                  <p className="mt-1 break-words text-lg font-black text-cyan-50">
                    {selectedEntry.name}
                  </p>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <InfoPill label="Line" value={String(selectedEntry.line)} />
                  <InfoPill label="Depth" value={String(selectedEntry.depth)} />
                  <InfoPill label="Core" value={selectedEntry.core ? 'yes' : 'no'} />
                </div>
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Raw</p>
                  <pre className="mt-2 whitespace-pre-wrap rounded-xl bg-black/60 p-3 text-xs leading-5 text-slate-300">
                    {selectedEntry.raw}
                  </pre>
                </div>
              </div>
            ) : (
              <p className="text-sm text-slate-400">Select a node to inspect it.</p>
            )}
          </div>
        </div>
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <div className="rounded-[2rem] border border-white/10 bg-black/45 p-5 backdrop-blur">
          <div className="mb-4 flex items-center gap-2">
            <Map className="h-5 w-5 text-fuchsia-200" />
            <h3 className="font-black">Topology Headings</h3>
          </div>
          <div className={`${compact ? 'max-h-[220px]' : 'max-h-[360px]'} space-y-2 overflow-auto`}>
            {headings.length === 0 ? (
              <p className="text-sm text-slate-500">Waiting for map headings...</p>
            ) : (
              headings.map((heading) => (
                <div
                  key={heading}
                  className="rounded-xl border border-white/10 bg-white/[0.04] px-3 py-2 text-sm font-semibold text-slate-300"
                >
                  {heading}
                </div>
              ))
            )}
          </div>
        </div>

        <div className="rounded-[2rem] border border-white/10 bg-black/45 p-5 backdrop-blur">
          <div className="mb-4 flex items-center gap-2">
            <Activity className="h-5 w-5 text-cyan-200" />
            <h3 className="font-black">System Signals</h3>
          </div>
          <div className="grid gap-2">
            {signals.map((signal) => (
              <div
                key={signal.key}
                className="flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.04] px-3 py-2"
              >
                <span className="text-sm font-semibold text-slate-300">{signal.label}</span>
                <span
                  className={`flex items-center gap-1 rounded-full px-2 py-1 text-[10px] font-black uppercase tracking-[0.16em] ${signal.active ? 'bg-cyan-300/15 text-cyan-200' : 'bg-slate-700 text-slate-400'}`}
                >
                  {signal.active && <CheckCircle2 className="h-3 w-3" />}
                  {signal.active ? 'mapped' : 'missing'}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="rounded-[2rem] border border-white/10 bg-black/45 p-5 backdrop-blur">
        <div className="mb-4 flex items-center gap-2">
          <Search className="h-5 w-5 text-emerald-200" />
          <h3 className="font-black">Map Search</h3>
        </div>
        <div className="mb-4 flex items-center gap-2 rounded-2xl border border-white/10 bg-slate-950 px-3 py-2">
          <Search className="h-4 w-4 text-slate-500" />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search map: MODAL_BRAIN, EXCALIBUR, Saltare..."
            className="w-full bg-transparent py-2 text-sm text-slate-100 outline-none placeholder:text-slate-600"
          />
        </div>
        <div
          className={`${compact ? 'max-h-[240px]' : 'max-h-[360px]'} overflow-auto rounded-2xl border border-white/10 bg-slate-950 p-3 font-mono text-xs`}
        >
          {rows.length === 0 ? (
            <p className="p-3 text-slate-500">No matching map rows yet.</p>
          ) : (
            rows.map((row) => (
              <div
                key={`${row.index}-${row.line}`}
                className="grid grid-cols-[4rem_1fr] gap-3 rounded-lg px-2 py-1.5 text-slate-300 hover:bg-white/10"
              >
                <span className="text-right text-slate-600">{row.index}</span>
                <span className="whitespace-pre-wrap">{row.line}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </section>
  );
}

function InfoPill({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl bg-black/50 p-3">
      <p className="text-[10px] uppercase tracking-[0.16em] text-slate-500">{label}</p>
      <p className="mt-1 font-black text-cyan-50">{value}</p>
    </div>
  );
}
