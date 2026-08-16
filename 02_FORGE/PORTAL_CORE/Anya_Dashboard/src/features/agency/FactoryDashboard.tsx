import React, { useEffect, useState } from 'react';
import {
  ArrowRight,
  Circle,
  Copy,
  ExternalLink,
  Gauge,
  GitBranch,
  LayoutDashboard,
  Play,
  Radio,
  RefreshCw,
  Send,
  Shield,
  TerminalSquare,
  Zap,
} from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { runtimeConfig } from '@/config/runtime';
import { bifrostFetch, bifrostWebSocketUrl } from '@/lib/bifrostClient';
import { useAnyaSocket, type AnyaSocketEvent } from '../brain/useAnyaSocket';

type RouteState = 'online' | 'degraded' | 'offline' | 'checking';

interface BridgeStatus {
  gate: string;
  owner: string;
  current_user: string;
  hostname: string;
  token_present: boolean;
  bridge: string;
  dispatch_url: string;
  websocket_url: string;
  cartridges: string[];
  cognitive_helm: string;
  bridge_knight: string;
}

interface RouteProbe {
  key: string;
  label: string;
  url: string;
  hint: string;
  state: RouteState;
  detail: string;
  latencyMs?: number;
}

interface ConsoleEntry {
  kind: 'system' | 'bridge' | 'command' | 'error';
  text: string;
  stamp: string;
}

interface QuickAction {
  label: string;
  command: string;
  icon: React.ElementType;
}

const ROUTE_TARGETS = [
  {
    key: 'bridge-status',
    label: 'Bridge Status',
    url: runtimeConfig.bifrost.statusUrl,
    hint: 'Bifrost /bifrost/status',
  },
  {
    key: 'dispatch',
    label: 'Dispatch Route',
    url: runtimeConfig.bifrost.dispatchUrl,
    hint: 'Bifrost /agent/dispatch',
  },
  {
    key: 'openviking-map',
    label: 'OpenViking Map',
    url: runtimeConfig.bifrost.openVikingMapUrl,
    hint: 'Live map surface',
  },
  {
    key: 'cloud-brain',
    label: 'Cloud Brain',
    url: runtimeConfig.cloudBrainUrl,
    hint: 'NotebookLM / modal bridge',
  },
] as const;

const QUICK_ACTIONS: QuickAction[] = [
  { label: 'Probe bridge', command: 'probe', icon: RefreshCw },
  { label: 'Dispatch health check', command: 'dispatch bridge health check', icon: Play },
  { label: 'Open status route', command: 'open bridge', icon: ExternalLink },
  { label: 'Copy websocket', command: 'copy ws', icon: Copy },
];

function stamp() {
  return new Date().toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

function toneClass(state: RouteState) {
  if (state === 'online') return 'text-emerald-300';
  if (state === 'degraded') return 'text-amber-300';
  if (state === 'checking') return 'text-cyan-300';
  return 'text-rose-300';
}

function pillClass(state: RouteState) {
  if (state === 'online') return 'border-emerald-400/30 bg-emerald-400/10 text-emerald-200';
  if (state === 'degraded') return 'border-amber-400/30 bg-amber-400/10 text-amber-200';
  if (state === 'checking') return 'border-cyan-400/30 bg-cyan-400/10 text-cyan-200';
  return 'border-rose-400/30 bg-rose-400/10 text-rose-200';
}

function eventBadgeClass(event: string) {
  if (event.includes('dispatch')) return 'border-cyan-400/30 bg-cyan-400/10 text-cyan-200';
  if (event.includes('bridge')) return 'border-emerald-400/30 bg-emerald-400/10 text-emerald-200';
  if (event.includes('deploy')) return 'border-violet-400/30 bg-violet-400/10 text-violet-200';
  return 'border-white/10 bg-white/[0.04] text-slate-200';
}

function formatEvent(event: AnyaSocketEvent) {
  const pieces = [event.event];
  if (event.source) pieces.push(event.source);
  if (event.detail) pieces.push(event.detail);
  return pieces.join(' • ');
}

async function probeRoute(
  target: (typeof ROUTE_TARGETS)[number],
  fetcher: typeof bifrostFetch,
): Promise<RouteProbe> {
  const started = performance.now();
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), 4500);

  try {
    const response = await fetcher(target.url, {
      method: 'GET',
      cache: 'no-store',
      signal: controller.signal,
    });
    const latencyMs = Math.round(performance.now() - started);
    const detail = `${response.status} ${response.statusText || 'OK'} • ${latencyMs}ms`;

    if (response.ok) {
      return { ...target, state: 'online', detail, latencyMs };
    }
    if (response.status === 401 || response.status === 403) {
      return { ...target, state: 'degraded', detail: `${detail} • auth required`, latencyMs };
    }
    if (response.status < 500) {
      return { ...target, state: 'degraded', detail, latencyMs };
    }
    return { ...target, state: 'offline', detail, latencyMs };
  } catch (error) {
    const latencyMs = Math.round(performance.now() - started);
    const detail = error instanceof Error ? error.message : 'probe failed';
    return { ...target, state: 'offline', detail: `${detail} • ${latencyMs}ms`, latencyMs };
  } finally {
    window.clearTimeout(timeout);
  }
}

async function loadBridgeStatus(fetcher: typeof bifrostFetch): Promise<BridgeStatus> {
  const response = await fetcher(runtimeConfig.bifrost.statusUrl, { cache: 'no-store' });
  if (!response.ok) {
    throw new Error(`status ${response.status}`);
  }
  return (await response.json()) as BridgeStatus;
}

async function dispatchThroughBridge(intent: string, fetcher: typeof bifrostFetch) {
  const response = await fetcher(runtimeConfig.bifrost.dispatchUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      intent,
      cartridge: 'ENGINEER',
      preferred_knight: 'anya_merlin',
      execution_target: 'bifrost_bridge',
      metadata: {
        source: 'dev_portal',
        bridge: 'bifrost',
        surface: 'factory_dashboard',
      },
    }),
  });

  let payload: any = null;
  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    throw new Error(payload?.error || `dispatch ${response.status}`);
  }

  return payload;
}

export default function FactoryDashboard() {
  const [bridgeStatus, setBridgeStatus] = useState<BridgeStatus | null>(null);
  const [bridgeError, setBridgeError] = useState('');
  const [routeHealth, setRouteHealth] = useState<RouteProbe[]>(
    ROUTE_TARGETS.map((target) => ({
      ...target,
      state: 'checking',
      detail: 'awaiting probe',
    })),
  );
  const [consoleFeed, setConsoleFeed] = useState<ConsoleEntry[]>([
    {
      kind: 'system',
      text: 'Development portal online. Run probe to refresh live bridge state.',
      stamp: stamp(),
    },
  ]);
  const [command, setCommand] = useState('probe');
  const [isBusy, setIsBusy] = useState(false);
  const [lastRefresh, setLastRefresh] = useState('pending');
  const { isConnected, events, latestEvent } = useAnyaSocket(bifrostWebSocketUrl());

  function pushConsole(kind: ConsoleEntry['kind'], text: string) {
    setConsoleFeed((current) => [
      ...current.slice(-19),
      {
        kind,
        text,
        stamp: stamp(),
      },
    ]);
  }

  async function refreshSurface(announce = false) {
    setIsBusy(true);
    try {
      const [status, probes] = await Promise.all([
        loadBridgeStatus(bifrostFetch),
        Promise.all(ROUTE_TARGETS.map((target) => probeRoute(target, bifrostFetch))),
      ]);

      setBridgeStatus(status);
      setBridgeError('');
      setRouteHealth(probes);
      setLastRefresh(stamp());

      if (announce) {
        const onlineCount = probes.filter((probe) => probe.state === 'online').length;
        pushConsole(
          'system',
          `Bridge refreshed. ${onlineCount}/${probes.length} routes online. Gate ${status.gate} at ${status.hostname}.`,
        );
      }
    } catch (error) {
      setBridgeStatus(null);
      setBridgeError(error instanceof Error ? error.message : 'bridge refresh failed');
      setLastRefresh(stamp());
      if (announce) {
        pushConsole(
          'error',
          `Refresh failed: ${error instanceof Error ? error.message : 'unknown bridge error'}`,
        );
      }
    } finally {
      setIsBusy(false);
    }
  }

  useEffect(() => {
    void refreshSurface(false);
    const timer = window.setInterval(() => {
      void refreshSurface(false);
    }, 12000);
    return () => {
      window.clearInterval(timer);
    };
  }, []);

  useEffect(() => {
    if (!latestEvent) return;
    pushConsole('bridge', formatEvent(latestEvent));
  }, [latestEvent]);

  async function copyText(value: string, successMessage: string) {
    try {
      if (!navigator.clipboard) {
        throw new Error('clipboard unavailable');
      }
      await navigator.clipboard.writeText(value);
      pushConsole('system', successMessage);
    } catch (error) {
      pushConsole(
        'error',
        `Copy failed: ${error instanceof Error ? error.message : 'clipboard error'}`,
      );
    }
  }

  function openRoute(routeKey: string) {
    const route = ROUTE_TARGETS.find((target) => target.key === routeKey);
    if (!route) {
      pushConsole('error', `Unknown route: ${routeKey}`);
      return;
    }
    window.open(route.url, '_blank', 'noopener,noreferrer');
    pushConsole('system', `Opened ${route.label}.`);
  }

  async function executeCommand(rawCommand: string) {
    const cleanCommand = rawCommand.trim();
    if (!cleanCommand || isBusy) return;

    pushConsole('command', `> ${cleanCommand}`);
    setCommand('');

    const lower = cleanCommand.toLowerCase();

    if (lower === 'probe' || lower === 'refresh') {
      await refreshSurface(true);
      return;
    }

    if (lower === 'copy ws') {
      await copyText(bifrostWebSocketUrl(), 'Copied websocket URL.');
      return;
    }

    if (lower === 'copy status') {
      await copyText(runtimeConfig.bifrost.statusUrl, 'Copied bridge status URL.');
      return;
    }

    if (lower === 'clear') {
      setConsoleFeed([
        {
          kind: 'system',
          text: 'Console cleared.',
          stamp: stamp(),
        },
      ]);
      return;
    }

    if (lower.startsWith('open ')) {
      const routeName = lower.replace(/^open\s+/, '').trim();
      if (routeName === 'bridge' || routeName === 'status') {
        openRoute('bridge-status');
        return;
      }
      if (routeName === 'dispatch') {
        openRoute('dispatch');
        return;
      }
      if (routeName === 'map' || routeName === 'openviking') {
        openRoute('openviking-map');
        return;
      }
      if (routeName === 'cloud' || routeName === 'brain') {
        openRoute('cloud-brain');
        return;
      }
      pushConsole('error', `Unknown route target: ${routeName}`);
      return;
    }

    if (lower.startsWith('dispatch ')) {
      const intent = cleanCommand.replace(/^dispatch\s+/i, '').trim();
      if (!intent) {
        pushConsole('error', 'Dispatch command needs an intent.');
        return;
      }

      try {
        const payload = await dispatchThroughBridge(intent, bifrostFetch);
        const summary =
          payload?.response ||
          payload?.payload?.result?.brief ||
          payload?.payload?.status ||
          'Dispatch accepted.';
        pushConsole('system', summary);
      } catch (error) {
        pushConsole(
          'error',
          `Dispatch failed: ${error instanceof Error ? error.message : 'unknown bridge error'}`,
        );
      }
      return;
    }

    pushConsole(
      'error',
      'Unknown command. Try: probe, dispatch <intent>, open bridge|map|cloud, copy ws, copy status, clear',
    );
  }

  const onlineRoutes = routeHealth.filter((route) => route.state === 'online').length;
  const bridgeState = bridgeStatus ? 'online' : 'offline';
  const buildState = 'ready';
  const buildDetail = `${import.meta.env.MODE} bundle mounted • ${navigator.onLine ? 'browser online' : 'browser offline'}`;
  const recentEvents = events.slice(-6).reverse();

  return (
    <div className="min-h-screen overflow-y-auto bg-[#05070b] text-slate-100">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_20%_0%,rgba(34,211,238,0.18),transparent_28%),radial-gradient(circle_at_80%_12%,rgba(168,85,247,0.16),transparent_30%),linear-gradient(135deg,rgba(15,23,42,0.72),rgba(2,6,23,0.98))]" />

      <main className="relative mx-auto flex min-h-screen max-w-7xl flex-col gap-6 px-4 pb-28 pt-5 lg:px-8">
        <header className="grid gap-4 lg:grid-cols-[1.3fr_0.7fr]">
          <section className="rounded-[2rem] border border-white/10 bg-black/35 p-6 shadow-2xl shadow-cyan-950/30 backdrop-blur">
            <div className="mb-8 flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="grid h-12 w-12 place-items-center rounded-2xl bg-cyan-400 text-xl font-black text-slate-950 shadow-lg shadow-cyan-500/30">
                  D
                </div>
                <div>
                  <p className="text-xs uppercase tracking-[0.38em] text-cyan-300">
                    Development Portal
                  </p>
                  <h1 className="text-3xl font-black tracking-tight md:text-5xl">
                    Camelot Command Deck
                  </h1>
                </div>
              </div>
              <div className="rounded-full border border-cyan-300/30 bg-cyan-300/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.25em] text-cyan-200">
                Live Bifrost Surface
              </div>
            </div>

            <div className="grid gap-3 md:grid-cols-4">
              <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                <div className="mb-4 flex items-center justify-between">
                  <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Build</p>
                  <LayoutDashboard className="h-4 w-4 text-cyan-300" />
                </div>
                <p className="text-2xl font-black lowercase">{buildState}</p>
                <p className="mt-2 min-h-[2.5rem] text-xs leading-5 text-slate-400">
                  {buildDetail}
                </p>
              </div>

              <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                <div className="mb-4 flex items-center justify-between">
                  <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Bridge</p>
                  <Shield className={`h-4 w-4 ${toneClass(bridgeStatus ? 'online' : 'offline')}`} />
                </div>
                <p className="text-2xl font-black lowercase">{bridgeState}</p>
                <p className="mt-2 min-h-[2.5rem] text-xs leading-5 text-slate-400">
                  {bridgeStatus
                    ? `${bridgeStatus.current_user}@${bridgeStatus.hostname}`
                    : bridgeError || 'Waiting for Bifrost'}
                </p>
              </div>

              <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                <div className="mb-4 flex items-center justify-between">
                  <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Socket</p>
                  <Radio className={`h-4 w-4 ${toneClass(isConnected ? 'online' : 'offline')}`} />
                </div>
                <p className="text-2xl font-black lowercase">
                  {isConnected ? 'linked' : 'offline'}
                </p>
                <p className="mt-2 min-h-[2.5rem] text-xs leading-5 text-slate-400">
                  {bifrostWebSocketUrl()}
                </p>
              </div>

              <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
                <div className="mb-4 flex items-center justify-between">
                  <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Routes</p>
                  <GitBranch className="h-4 w-4 text-violet-300" />
                </div>
                <p className="text-2xl font-black lowercase">
                  {onlineRoutes}/{routeHealth.length}
                </p>
                <p className="mt-2 min-h-[2.5rem] text-xs leading-5 text-slate-400">
                  Last refresh {lastRefresh}
                </p>
              </div>
            </div>
          </section>

          <aside className="rounded-[2rem] border border-emerald-300/20 bg-emerald-300/[0.06] p-6 backdrop-blur">
            <p className="text-xs uppercase tracking-[0.34em] text-emerald-200">Operator View</p>
            <div className="mt-5 space-y-4">
              <div className="rounded-2xl bg-black/30 p-4">
                <p className="text-sm text-slate-400">Surface</p>
                <p className="text-2xl font-black">Development Console</p>
              </div>
              <div className="rounded-2xl bg-black/30 p-4">
                <p className="text-sm text-slate-400">Bridge Knight</p>
                <p className="text-2xl font-black">{bridgeStatus?.bridge_knight ?? 'sir_link'}</p>
              </div>
              <div className="rounded-2xl bg-black/30 p-4">
                <p className="text-sm text-slate-400">Cognitive Helm</p>
                <p className="text-2xl font-black">{bridgeStatus?.cognitive_helm ?? 'sir_alex'}</p>
              </div>
            </div>
          </aside>
        </header>

        <section className="grid gap-6 lg:grid-cols-[0.92fr_1.08fr]">
          <Card
            className="border border-white/10 bg-slate-950/70 text-white shadow-2xl shadow-cyan-950/20"
            title="Route Health"
            description="Probe the Bifrost surfaces and see which routes are ready, degraded, or offline."
            actions={<Zap className="h-4 w-4 text-amber-300" />}
          >
            <div className="space-y-3">
              {routeHealth.map((route) => (
                <div
                  key={route.key}
                  className="rounded-2xl border border-white/10 bg-white/[0.04] p-4"
                >
                  <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-white">{route.label}</p>
                      <p className="text-xs text-slate-500">{route.hint}</p>
                    </div>
                    <div
                      className={`rounded-full border px-3 py-1 text-[10px] font-bold uppercase tracking-[0.18em] ${pillClass(route.state)}`}
                    >
                      {route.state}
                    </div>
                  </div>
                  <div className="grid gap-2 md:grid-cols-[1fr_auto] md:items-end">
                    <div className="space-y-1">
                      <p className="truncate font-mono text-xs text-cyan-200">{route.url}</p>
                      <p className="text-xs text-slate-400">{route.detail}</p>
                    </div>
                    <button
                      onClick={() => openRoute(route.key)}
                      className="inline-flex items-center justify-center gap-2 rounded-full border border-white/10 bg-black/25 px-3 py-2 text-xs font-semibold text-slate-200 transition hover:border-cyan-300/30 hover:bg-cyan-300/10 hover:text-cyan-100"
                    >
                      <ExternalLink className="h-3 w-3" />
                      Open
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card
            className="border border-white/10 bg-slate-950/70 text-white shadow-2xl shadow-violet-950/20"
            title="Command Console"
            description="Type a command or use quick actions. The console never fails silently."
            actions={<TerminalSquare className="h-4 w-4 text-cyan-300" />}
          >
            <div className="space-y-4">
              <div className="rounded-2xl border border-white/10 bg-black/40 p-4 font-mono">
                <div className="mb-3 flex flex-wrap items-center gap-2 text-[10px] uppercase tracking-[0.24em] text-slate-500">
                  <span>anya@camelot</span>
                  <ArrowRight className="h-3 w-3" />
                  <span>/dev</span>
                  <ArrowRight className="h-3 w-3" />
                  <span>bifrost-console</span>
                </div>
                <textarea
                  value={command}
                  onChange={(event) => setCommand(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter' && !event.shiftKey) {
                      event.preventDefault();
                      void executeCommand(command);
                    }
                  }}
                  className="min-h-28 w-full resize-none rounded-2xl border border-white/10 bg-slate-950/80 p-4 text-sm leading-6 text-slate-100 outline-none transition placeholder:text-slate-600 focus:border-cyan-300"
                  placeholder="probe | dispatch bridge health check | open cloud | copy ws | clear"
                />

                <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
                  <p className="text-xs text-slate-500">
                    Commands: probe, dispatch &lt;intent&gt;, open bridge|map|cloud, copy ws, copy
                    status, clear.
                  </p>
                  <button
                    onClick={() => void executeCommand(command)}
                    disabled={isBusy || !command.trim()}
                    className="inline-flex items-center gap-2 rounded-full bg-cyan-300 px-5 py-3 text-sm font-black uppercase tracking-[0.18em] text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    {isBusy ? 'Working' : 'Execute'}
                    <Send className="h-4 w-4" />
                  </button>
                </div>
              </div>

              <div className="grid gap-2 sm:grid-cols-2">
                {QUICK_ACTIONS.map((action) => {
                  const Icon = action.icon;
                  return (
                    <button
                      key={action.command}
                      onClick={() => void executeCommand(action.command)}
                      className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-left transition hover:border-cyan-300/30 hover:bg-cyan-300/10"
                    >
                      <span className="text-sm font-semibold text-slate-100">{action.label}</span>
                      <Icon className="h-4 w-4 text-cyan-200" />
                    </button>
                  );
                })}
              </div>
            </div>
          </Card>
        </section>

        <section className="grid gap-6 lg:grid-cols-[1fr_1fr]">
          <Card
            className="border border-white/10 bg-slate-950/70 text-white shadow-2xl shadow-slate-950/30"
            title="Bridge Transcript"
            description="Recent bridge events, dispatch results, and websocket signals."
            actions={<Radio className="h-4 w-4 text-emerald-300" />}
          >
            <div className="max-h-[26rem] space-y-3 overflow-y-auto pr-1">
              {recentEvents.length === 0 ? (
                <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4 text-sm text-slate-500">
                  Waiting for websocket events.
                </div>
              ) : (
                recentEvents.map((event, index) => (
                  <div
                    key={`${event.timestamp_ms ?? index}-${index}`}
                    className="rounded-2xl border border-white/10 bg-white/[0.04] p-4"
                  >
                    <div className="mb-2 flex items-center justify-between gap-3">
                      <span
                        className={`rounded-full border px-2 py-1 text-[10px] font-bold uppercase tracking-[0.18em] ${eventBadgeClass(event.event)}`}
                      >
                        {event.event}
                      </span>
                      <span className="text-[10px] text-slate-600">{event.source ?? 'bridge'}</span>
                    </div>
                    <p className="text-sm leading-6 text-slate-300">
                      {event.detail || formatEvent(event)}
                    </p>
                  </div>
                ))
              )}
            </div>
          </Card>

          <Card
            className="border border-white/10 bg-slate-950/70 text-white shadow-2xl shadow-slate-950/30"
            title="Console Log"
            description="Operator notes, probes, and command acknowledgments."
            actions={<Gauge className="h-4 w-4 text-cyan-300" />}
          >
            <div className="max-h-[26rem] space-y-3 overflow-y-auto pr-1">
              {consoleFeed.map((entry, index) => (
                <div
                  key={`${entry.stamp}-${index}`}
                  className="rounded-2xl border border-white/10 bg-black/30 p-3"
                >
                  <div className="mb-1 flex items-center justify-between gap-3">
                    <span
                      className={`rounded-full border px-2 py-1 text-[10px] font-bold uppercase tracking-[0.18em] ${
                        entry.kind === 'error'
                          ? 'border-rose-400/30 bg-rose-400/10 text-rose-200'
                          : entry.kind === 'bridge'
                            ? 'border-emerald-400/30 bg-emerald-400/10 text-emerald-200'
                            : entry.kind === 'command'
                              ? 'border-cyan-400/30 bg-cyan-400/10 text-cyan-200'
                              : 'border-white/10 bg-white/[0.04] text-slate-200'
                      }`}
                    >
                      {entry.kind}
                    </span>
                    <span className="text-[10px] text-slate-600">{entry.stamp}</span>
                  </div>
                  <p className="whitespace-pre-wrap text-sm leading-6 text-slate-300">
                    {entry.text}
                  </p>
                </div>
              ))}
            </div>
          </Card>
        </section>

        <section className="rounded-[2rem] border border-white/10 bg-black/30 p-5 backdrop-blur">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-[0.34em] text-slate-500">Bridge Summary</p>
              <h2 className="text-2xl font-black">Operational Readiness</h2>
            </div>
            <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate-300">
              <Circle
                className={`h-3 w-3 ${isConnected ? 'fill-emerald-300 text-emerald-300' : 'fill-rose-300 text-rose-300'}`}
              />
              {isConnected ? 'websocket linked' : 'websocket offline'}
            </div>
          </div>

          <div className="mt-5 grid gap-3 md:grid-cols-3">
            <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
              <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Gate</p>
              <p className="mt-2 text-lg font-black">{bridgeStatus?.gate ?? 'offline'}</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
              <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Current User</p>
              <p className="mt-2 text-lg font-black">{bridgeStatus?.current_user ?? 'unknown'}</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-4">
              <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Cartridges</p>
              <p className="mt-2 text-lg font-black">
                {bridgeStatus?.cartridges?.length ?? 0} live
              </p>
            </div>
          </div>

          <div className="mt-4 rounded-2xl border border-white/10 bg-white/[0.03] p-4 text-sm text-slate-400">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-mono text-cyan-200">{runtimeConfig.bifrost.statusUrl}</span>
              <ArrowRight className="h-3 w-3 text-slate-500" />
              <span>{runtimeConfig.bifrost.dispatchUrl}</span>
              <ArrowRight className="h-3 w-3 text-slate-500" />
              <span>{runtimeConfig.bifrost.websocketUrl}</span>
            </div>
            <p className="mt-3 text-xs leading-5 text-slate-500">
              This surface is live when the Bifrost bridge answers, websocket events are flowing,
              and route probes remain responsive.
            </p>
            {bridgeError && (
              <div className="mt-4 rounded-2xl border border-rose-400/20 bg-rose-400/10 p-3 text-sm text-rose-200">
                {bridgeError}
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
