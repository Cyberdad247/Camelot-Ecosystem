import React, { useEffect, useMemo, useState } from 'react';
import {
  Activity,
  Archive,
  BookOpen,
  BrainCircuit,
  CheckCircle2,
  Cloud,
  Database,
  GitBranch,
  HardDrive,
  KeyRound,
  Layers3,
  Network,
  RefreshCcw,
  ShieldCheck,
  Sparkles,
  Zap,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { cn } from '@/lib/utils';
import {
  activateSupportSession,
  loadCamelotOsState,
  revokeSupportSession,
} from './camelotOsClient';
import type { CamelotOsState, FileState, FrontierNode, MemoryTier } from './types';

const statusTone: Record<string, string> = {
  OK: 'text-emerald-300 border-emerald-500/30 bg-emerald-950/20',
  LIVE_UI: 'text-cyan-300 border-cyan-500/30 bg-cyan-950/20',
  QUEUE_CLEAR: 'text-emerald-300 border-emerald-500/30 bg-emerald-950/20',
  QUEUE_PENDING: 'text-amber-300 border-amber-500/30 bg-amber-950/20',
  CONFIGURED: 'text-fuchsia-300 border-fuchsia-500/30 bg-fuchsia-950/20',
  active: 'text-emerald-300 border-emerald-500/30 bg-emerald-950/20',
  available: 'text-cyan-300 border-cyan-500/30 bg-cyan-950/20',
  disabled: 'text-slate-300 border-slate-700 bg-slate-900',
  expired: 'text-amber-300 border-amber-500/30 bg-amber-950/20',
  revoked: 'text-red-300 border-red-500/30 bg-red-950/20',
};

function fmtDate(value?: string | number) {
  if (!value) return 'unknown';
  const date = typeof value === 'number' ? new Date(value * 1000) : new Date(value);
  if (Number.isNaN(date.valueOf())) return 'unknown';
  return date.toLocaleString();
}

function fileLabel(file: FileState) {
  if (!file.exists) return 'missing';
  const kb = file.bytes
    ? `${Math.max(1, Math.round(file.bytes / 1024)).toLocaleString()} KB`
    : 'tracked';
  return `${kb} · ${fmtDate(file.updated)}`;
}

function StatusPill({ status }: { status: string }) {
  return (
    <span
      className={cn(
        'rounded-full border px-2.5 py-1 text-[10px] font-bold uppercase tracking-widest',
        statusTone[status] ?? 'border-slate-700 bg-slate-900 text-slate-300',
      )}
    >
      {status.replace(/_/g, ' ')}
    </span>
  );
}

function Metric({
  label,
  value,
  icon: Icon,
}: { label: string; value: string | number; icon: React.ElementType }) {
  return (
    <div className="rounded-lg border border-slate-800/70 bg-slate-950/60 p-4">
      <div className="flex items-center justify-between gap-3">
        <p className="text-xs text-slate-500">{label}</p>
        <Icon className="h-4 w-4 text-cyan-300" />
      </div>
      <p className="mt-2 text-2xl font-black text-slate-100">{value}</p>
    </div>
  );
}

function MemoryTierRow({ tier }: { tier: MemoryTier }) {
  const Icon = tier.id === 'flash' ? Zap : tier.id === 'short' ? Cloud : Archive;
  return (
    <div className="grid gap-3 border-t border-slate-800/70 px-5 py-4 md:grid-cols-[160px_1fr_220px]">
      <div className="flex items-start gap-3">
        <div className="grid h-9 w-9 shrink-0 place-items-center rounded-lg border border-slate-700 bg-slate-950">
          <Icon className="h-4 w-4 text-fuchsia-300" />
        </div>
        <div>
          <p className="font-black text-slate-100">{tier.label}</p>
          <p className="text-xs text-slate-500">{tier.owner}</p>
        </div>
      </div>
      <div>
        <p className="text-sm leading-6 text-slate-300">{tier.purpose}</p>
        <p className="mt-1 font-mono text-[11px] text-slate-500">{tier.source}</p>
        {tier.notebook_url && (
          <a
            className="mt-2 inline-flex text-xs font-semibold text-cyan-300 hover:text-cyan-200"
            href={tier.notebook_url}
            target="_blank"
            rel="noreferrer"
          >
            Open Cloudbrain notebook
          </a>
        )}
        {tier.local_db && (
          <p className="mt-2 text-xs text-slate-500">Local LT DB: {fileLabel(tier.local_db)}</p>
        )}
      </div>
      <div className="flex flex-col items-start gap-2 md:items-end">
        <StatusPill status={tier.status} />
        <p className="text-xs leading-5 text-slate-500 md:text-right">{tier.action}</p>
      </div>
    </div>
  );
}

function SurfaceGrid({ surfaces }: { surfaces: Record<string, boolean> }) {
  const entries = Object.entries(surfaces);
  return (
    <div className="grid grid-cols-2 gap-2 md:grid-cols-5">
      {entries.map(([key, online]) => (
        <div
          key={key}
          className="flex items-center gap-2 rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2"
        >
          <CheckCircle2 className={cn('h-4 w-4', online ? 'text-emerald-400' : 'text-slate-600')} />
          <span className="text-xs font-semibold capitalize text-slate-300">{key}</span>
        </div>
      ))}
    </div>
  );
}

function FrontierNodeCard({ node }: { node: FrontierNode }) {
  return (
    <div className="rounded-lg border border-slate-800/70 bg-slate-950/60 p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="truncate text-sm font-black text-slate-100">{node.surface}</p>
          <p className="mt-1 font-mono text-[11px] text-slate-500">{node.node_id}</p>
        </div>
        <StatusPill status={node.status} />
      </div>
      <p className="mt-3 text-xs font-semibold uppercase tracking-widest text-cyan-300">
        {node.role}
      </p>
      <div className="mt-3 flex flex-wrap gap-1.5">
        {node.memory_tiers.map((tier) => (
          <span
            key={tier}
            className="rounded border border-fuchsia-500/20 bg-fuchsia-950/20 px-2 py-0.5 text-[10px] font-bold uppercase text-fuchsia-200"
          >
            {tier}
          </span>
        ))}
      </div>
      <p className="mt-3 line-clamp-2 text-xs leading-5 text-slate-500">
        {node.permissions.join(' / ')}
      </p>
    </div>
  );
}

export default function CamelotOsCommand() {
  const [state, setState] = useState<CamelotOsState | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [supportReason, setSupportReason] = useState('client-requested support window');
  const [operatorToken, setOperatorToken] = useState(
    () => window.sessionStorage.getItem('camelot.operatorToken') ?? '',
  );
  const [supportToken, setSupportToken] = useState('');

  async function refresh() {
    setLoading(true);
    setError('');
    try {
      setState(await loadCamelotOsState());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Camelot OS status unavailable');
    } finally {
      setLoading(false);
    }
  }

  async function activateSupport() {
    setLoading(true);
    setError('');
    try {
      window.sessionStorage.setItem('camelot.operatorToken', operatorToken);
      const next = await activateSupportSession(supportReason, 120);
      setState(next);
      setSupportToken(next.frontier.one_time_token ?? '');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Support activation failed');
    } finally {
      setLoading(false);
    }
  }

  async function revokeSupport() {
    setLoading(true);
    setError('');
    try {
      window.sessionStorage.setItem('camelot.operatorToken', operatorToken);
      const active = state?.frontier.support.active_session;
      setState(await revokeSupportSession(active?.session_id));
      setSupportToken('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Support revoke failed');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void refresh();
  }, []);

  const ledgerFiles = useMemo(() => {
    if (!state) return [];
    return [
      ['Root Provenance', state.ledgers.root],
      ['Verification Ledger', state.ledgers.verification],
      ['Cloudbrain Manifest', state.ledgers.cloudbrain_manifest],
      ['Codex Integration', state.ledgers.codex_integration],
      ['Knight Configuration', state.ledgers.knight_configuration],
    ] as const;
  }, [state]);

  if (loading && !state) {
    return (
      <div className="grid min-h-full place-items-center p-6">
        <div className="text-center">
          <RefreshCcw className="mx-auto h-6 w-6 animate-spin text-fuchsia-300" />
          <p className="mt-3 text-sm font-semibold text-slate-300">Loading Camelot OS state</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-full space-y-6 p-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <div className="flex items-center gap-3">
            <Layers3 className="h-6 w-6 text-fuchsia-300" />
            <h1 className="text-2xl font-black tracking-tight text-slate-100">
              Camelot OS Command
            </h1>
          </div>
          <p className="mt-1 max-w-3xl text-sm leading-6 text-slate-500">
            Whole-system map for orchestration, Cloudbrain memory tiers, ledgers, active cartridges,
            and launch surfaces.
          </p>
        </div>
        <button
          onClick={() => void refresh()}
          className="inline-flex items-center justify-center gap-2 rounded-lg border border-cyan-500/30 bg-cyan-950/20 px-4 py-2 text-sm font-bold text-cyan-200 hover:bg-cyan-900/30"
        >
          <RefreshCcw className={cn('h-4 w-4', loading && 'animate-spin')} />
          Refresh
        </button>
      </div>

      {error && (
        <div className="rounded-lg border border-amber-500/30 bg-amber-950/20 p-4 text-sm text-amber-200">
          {error}
        </div>
      )}

      {state && (
        <>
          <div className="grid gap-3 md:grid-cols-3 xl:grid-cols-6">
            <Metric label="Layers" value={state.summary.architecture_layers} icon={Layers3} />
            <Metric label="Edges" value={state.summary.schematic_edges} icon={GitBranch} />
            <Metric label="Cartridges" value={state.summary.active_cartridges} icon={Sparkles} />
            <Metric label="Knights" value={state.summary.knights} icon={ShieldCheck} />
            <Metric label="Surfaces" value={state.summary.codex_surfaces_online} icon={Activity} />
            <Metric label="Queue" value={state.summary.cloudbrain_queue_pending} icon={Database} />
          </div>

          <section className="overflow-hidden rounded-lg border border-slate-800/70 bg-slate-900/35">
            <div className="flex items-center justify-between gap-4 px-5 py-4">
              <div>
                <h2 className="text-sm font-black uppercase tracking-widest text-slate-200">
                  Strategic Orchestration
                </h2>
                <p className="mt-1 text-xs text-slate-500">
                  Generated {fmtDate(state.generated_utc)} from {state.version}
                </p>
              </div>
              <StatusPill status={state.status} />
            </div>
            <div className="border-t border-slate-800/70 p-5">
              <SurfaceGrid surfaces={state.orchestration.codex_surfaces} />
            </div>
            <div className="grid border-t border-slate-800/70 md:grid-cols-2 xl:grid-cols-3">
              {state.orchestration.layers.map((layer) => (
                <div key={layer.layer} className="border-b border-r border-slate-800/70 p-4">
                  <p className="text-xs font-bold uppercase tracking-widest text-fuchsia-300">
                    {layer.layer}
                  </p>
                  <p className="mt-2 text-sm font-black text-slate-100">{layer.owner}</p>
                  <p className="mt-2 text-xs leading-5 text-slate-400">{layer.purpose}</p>
                  <p className="mt-3 font-mono text-[10px] text-slate-600">{layer.source}</p>
                </div>
              ))}
            </div>
          </section>

          <section className="overflow-hidden rounded-lg border border-slate-800/70 bg-slate-900/35">
            <div className="px-5 py-4">
              <h2 className="flex items-center gap-2 text-sm font-black uppercase tracking-widest text-slate-200">
                <BrainCircuit className="h-4 w-4 text-cyan-300" /> Cloudbrain Memory Routing
              </h2>
              <p className="mt-1 text-xs text-slate-500">
                Flash for now, Short for NotebookLM synthesis, Long for durable archive and LT
                memory.
              </p>
            </div>
            {state.memory_tiers.map((tier) => (
              <MemoryTierRow key={tier.id} tier={tier} />
            ))}
          </section>

          <div className="grid gap-6 xl:grid-cols-[1fr_420px]">
            <section className="overflow-hidden rounded-lg border border-slate-800/70 bg-slate-900/35">
              <div className="px-5 py-4">
                <h2 className="flex items-center gap-2 text-sm font-black uppercase tracking-widest text-slate-200">
                  <HardDrive className="h-4 w-4 text-emerald-300" /> Ledgers And Runtime Artifacts
                </h2>
              </div>
              <div className="divide-y divide-slate-800/70 border-t border-slate-800/70">
                {ledgerFiles.map(([label, file]) => (
                  <div key={label} className="flex items-center justify-between gap-4 px-5 py-3">
                    <div className="min-w-0">
                      <p className="text-sm font-semibold text-slate-200">{label}</p>
                      <p className="truncate font-mono text-[11px] text-slate-600">{file.path}</p>
                    </div>
                    <p className="shrink-0 text-right text-xs text-slate-500">{fileLabel(file)}</p>
                  </div>
                ))}
              </div>
            </section>

            <section className="rounded-lg border border-slate-800/70 bg-slate-900/35 p-5">
              <h2 className="flex items-center gap-2 text-sm font-black uppercase tracking-widest text-slate-200">
                <BookOpen className="h-4 w-4 text-fuchsia-300" /> Launch Surfaces
              </h2>
              <div className="mt-4 grid gap-2">
                <Link
                  to="/dev"
                  className="rounded-lg border border-slate-800 bg-slate-950/60 px-4 py-3 text-sm font-semibold text-slate-200 hover:border-fuchsia-500/40"
                >
                  Development Portal
                </Link>
                <Link
                  to="/defense-grid"
                  className="rounded-lg border border-slate-800 bg-slate-950/60 px-4 py-3 text-sm font-semibold text-slate-200 hover:border-emerald-500/40"
                >
                  Defense Grid
                </Link>
                <Link
                  to="/brain"
                  className="rounded-lg border border-slate-800 bg-slate-950/60 px-4 py-3 text-sm font-semibold text-slate-200 hover:border-cyan-500/40"
                >
                  Flash Brain HUD
                </Link>
                <Link
                  to="/openviking"
                  className="rounded-lg border border-slate-800 bg-slate-950/60 px-4 py-3 text-sm font-semibold text-slate-200 hover:border-blue-500/40"
                >
                  OpenViking Map
                </Link>
              </div>
            </section>
          </div>

          <section className="overflow-hidden rounded-lg border border-slate-800/70 bg-slate-900/35">
            <div className="flex flex-col gap-4 px-5 py-4 xl:flex-row xl:items-start xl:justify-between">
              <div>
                <h2 className="flex items-center gap-2 text-sm font-black uppercase tracking-widest text-slate-200">
                  <Network className="h-4 w-4 text-cyan-300" /> Empire Nodes
                </h2>
                <p className="mt-1 max-w-3xl text-xs leading-5 text-slate-500">
                  Frontier model chats become registered Camelot nodes with roles, memory tiers,
                  permissions, and ledgered activity.
                </p>
              </div>
              <p className="font-mono text-[11px] text-slate-600">{state.frontier.artifact_path}</p>
            </div>
            <div className="grid gap-3 border-t border-slate-800/70 p-5 md:grid-cols-2 xl:grid-cols-5">
              {state.frontier.nodes.map((node) => (
                <FrontierNodeCard key={node.node_id} node={node} />
              ))}
            </div>
          </section>

          <section className="overflow-hidden rounded-lg border border-slate-800/70 bg-slate-900/35">
            <div className="grid gap-5 p-5 xl:grid-cols-[1fr_360px]">
              <div>
                <h2 className="flex items-center gap-2 text-sm font-black uppercase tracking-widest text-slate-200">
                  <KeyRound className="h-4 w-4 text-amber-300" /> Break-Glass Support Portal
                </h2>
                <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
                  Future access is disabled by default. Activate it only when a client needs help;
                  Camelot creates a temporary token, stores only its hash, expires it automatically,
                  and writes the action to the ledger.
                </p>
                <div className="mt-4 grid gap-3 md:grid-cols-[1fr_160px_160px]">
                  <input
                    value={supportReason}
                    onChange={(event) => setSupportReason(event.target.value)}
                    className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-200 outline-none focus:border-cyan-500/70"
                    placeholder="Support reason"
                  />
                  <input
                    value={operatorToken}
                    onChange={(event) => setOperatorToken(event.target.value)}
                    className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-200 outline-none focus:border-cyan-500/70 md:col-span-2"
                    placeholder="Operator token"
                    type="password"
                  />
                  <button
                    onClick={() => void activateSupport()}
                    className="rounded-lg border border-emerald-500/30 bg-emerald-950/30 px-4 py-2 text-sm font-bold text-emerald-200 hover:bg-emerald-900/30"
                  >
                    Activate 2h
                  </button>
                  <button
                    onClick={() => void revokeSupport()}
                    className="rounded-lg border border-red-500/30 bg-red-950/20 px-4 py-2 text-sm font-bold text-red-200 hover:bg-red-900/30"
                  >
                    Revoke
                  </button>
                </div>
                {supportToken && (
                  <div className="mt-4 rounded-lg border border-amber-500/30 bg-amber-950/20 p-4">
                    <p className="text-xs font-bold uppercase tracking-widest text-amber-200">
                      One-time token
                    </p>
                    <p className="mt-2 break-all font-mono text-sm text-amber-100">
                      {supportToken}
                    </p>
                    <p className="mt-2 text-xs text-amber-200/70">
                      This token is shown once. The runtime artifact stores only a SHA-256 hash.
                    </p>
                  </div>
                )}
              </div>
              <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-4">
                <div className="flex items-center justify-between gap-3">
                  <p className="text-xs font-black uppercase tracking-widest text-slate-400">
                    Support State
                  </p>
                  <StatusPill status={state.frontier.support.status} />
                </div>
                {state.frontier.support.active_session ? (
                  <div className="mt-4 space-y-3 text-xs text-slate-400">
                    <p>
                      <span className="text-slate-500">Session:</span>{' '}
                      {state.frontier.support.active_session.session_id}
                    </p>
                    <p>
                      <span className="text-slate-500">Portal:</span>{' '}
                      {state.frontier.support.active_session.portal_path}
                    </p>
                    <p>
                      <span className="text-slate-500">Expires:</span>{' '}
                      {fmtDate(state.frontier.support.active_session.expires_utc)}
                    </p>
                    <p>
                      <span className="text-slate-500">Reason:</span>{' '}
                      {state.frontier.support.active_session.reason}
                    </p>
                  </div>
                ) : (
                  <p className="mt-4 text-xs leading-5 text-slate-500">
                    No active support session. The portal is closed.
                  </p>
                )}
              </div>
            </div>
          </section>
        </>
      )}
    </div>
  );
}
