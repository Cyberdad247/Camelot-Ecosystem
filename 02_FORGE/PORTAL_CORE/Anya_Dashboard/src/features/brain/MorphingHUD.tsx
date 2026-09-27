import { runtimeConfig } from '@/config/runtime';
import { bifrostFetch, bifrostWebSocketUrl } from '@/lib/bifrostClient';
import {
  Activity,
  ArrowRight,
  Brain,
  Cable,
  CheckCircle2,
  Cpu,
  Database,
  Gavel,
  Lightbulb,
  Megaphone,
  PenTool,
  Radio,
  Scale,
  Search,
  Shield,
  TerminalSquare,
  Zap,
} from 'lucide-react';
import type React from 'react';
import { useEffect, useMemo, useState } from 'react';
import { type AnyaSocketEvent, useAnyaSocket } from './useAnyaSocket';

const DISPATCH_URL = runtimeConfig.bifrost.dispatchUrl;
const BIFROST_STATUS_URL = runtimeConfig.bifrost.statusUrl;

type CartridgeId =
  | 'COGNITIVE'
  | 'ENGINEER'
  | 'RESEARCH'
  | 'CREATIVE'
  | 'MARKETING'
  | 'LEGAL'
  | 'BRAINSTORM'
  | 'CRITICAL_THINKING';

interface BifrostStatus {
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

interface Message {
  role: 'user' | 'system' | 'bridge';
  text: string;
  stamp: string;
}

const cartridges: Array<{
  id: CartridgeId;
  label: string;
  helm: string;
  description: string;
  icon: React.ElementType;
}> = [
  {
    id: 'COGNITIVE',
    label: 'Cognitive',
    helm: 'Sir Alex + Sir Link',
    description: 'Grand orchestration, route governance, UI to terminal handoff.',
    icon: Brain,
  },
  {
    id: 'ENGINEER',
    label: 'Engineer',
    helm: 'Anya + Merlin',
    description: 'Build, verify, and harden code paths through Bifrost.',
    icon: Cpu,
  },
  {
    id: 'RESEARCH',
    label: 'Research',
    helm: 'Merlin',
    description: 'NotebookLM short-term memory and cloud brain lookup.',
    icon: Search,
  },
  {
    id: 'CREATIVE',
    label: 'Creative',
    helm: 'Anya',
    description: 'Interface, story, voice, product language, and visual direction.',
    icon: PenTool,
  },
  {
    id: 'MARKETING',
    label: 'Marketing',
    helm: 'Sir Link',
    description: 'Funnels, positioning, content systems, and delivery loops.',
    icon: Megaphone,
  },
  {
    id: 'LEGAL',
    label: 'Legal',
    helm: 'Sentinel',
    description: 'Risk review, compliance posture, and gated execution.',
    icon: Scale,
  },
  {
    id: 'BRAINSTORM',
    label: 'Brainstorm',
    helm: 'Anya',
    description: 'Idea generation, option trees, and divergent strategy.',
    icon: Lightbulb,
  },
  {
    id: 'CRITICAL_THINKING',
    label: 'Critical',
    helm: 'Sir Alex',
    description: 'Scorpion Sting review, tradeoffs, and failure-mode pressure tests.',
    icon: Gavel,
  },
];

function timestamp() {
  return new Date().toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

function cartridgeForIntent(intent: string, selected: CartridgeId): CartridgeId {
  const text = intent.toLowerCase();
  if (
    text.includes('build') ||
    text.includes('fix') ||
    text.includes('implement') ||
    text.includes('code')
  )
    return 'ENGINEER';
  if (text.includes('research') || text.includes('source') || text.includes('compare'))
    return 'RESEARCH';
  if (text.includes('campaign') || text.includes('funnel') || text.includes('market'))
    return 'MARKETING';
  if (text.includes('legal') || text.includes('risk') || text.includes('contract')) return 'LEGAL';
  if (text.includes('brainstorm') || text.includes('ideas')) return 'BRAINSTORM';
  if (text.includes('critique') || text.includes('audit') || text.includes('pressure'))
    return 'CRITICAL_THINKING';
  return selected;
}

function knightFor(cartridge: CartridgeId) {
  if (cartridge === 'COGNITIVE' || cartridge === 'CRITICAL_THINKING') return 'sir_alex';
  if (cartridge === 'MARKETING') return 'sir_link';
  if (cartridge === 'ENGINEER') return 'anya_merlin';
  if (cartridge === 'LEGAL') return 'sentinel';
  return 'merlin';
}

function eventLine(event: AnyaSocketEvent) {
  return `${event.event} :: ${event.source ?? 'bridge'}${event.detail ? ` :: ${event.detail}` : ''}`;
}

function toneClass(tone: string) {
  if (tone === 'emerald') return 'text-emerald-300';
  if (tone === 'cyan') return 'text-cyan-300';
  if (tone === 'blue') return 'text-blue-300';
  if (tone === 'violet') return 'text-violet-300';
  return 'text-amber-300';
}

export default function MorphingHUD() {
  const [status, setStatus] = useState<BifrostStatus | null>(null);
  const [statusError, setStatusError] = useState('');
  const [selectedCartridge, setSelectedCartridge] = useState<CartridgeId>('ENGINEER');
  const [intent, setIntent] = useState('Overhaul Anya dashboard and sync through Bifrost');
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'system',
      text: 'Anya interface online. Awaiting Bifrost bridge synchronization.',
      stamp: timestamp(),
    },
  ]);
  const [isDispatching, setIsDispatching] = useState(false);
  const { isConnected, events, latestEvent } = useAnyaSocket(bifrostWebSocketUrl());

  useEffect(() => {
    let cancelled = false;

    async function loadStatus() {
      try {
        const response = await bifrostFetch(BIFROST_STATUS_URL);
        if (!response.ok) throw new Error(`status ${response.status}`);
        const data = (await response.json()) as BifrostStatus;
        if (!cancelled) {
          setStatus(data);
          setStatusError('');
        }
      } catch (error) {
        if (!cancelled) {
          setStatus(null);
          setStatusError(error instanceof Error ? error.message : 'Bifrost status unavailable');
        }
      }
    }

    loadStatus();
    const timer = window.setInterval(loadStatus, 5000);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, []);

  useEffect(() => {
    if (!latestEvent) return;
    setMessages((current) => [
      ...current.slice(-11),
      {
        role: 'bridge',
        text: eventLine(latestEvent),
        stamp: timestamp(),
      },
    ]);
  }, [latestEvent]);

  const activeCartridge = useMemo(
    () => cartridges.find((cartridge) => cartridge.id === selectedCartridge) ?? cartridges[0],
    [selectedCartridge],
  );

  async function dispatchIntent() {
    const cleanIntent = intent.trim();
    if (!cleanIntent || isDispatching) return;

    const cartridge = cartridgeForIntent(cleanIntent, selectedCartridge);
    const preferredKnight = knightFor(cartridge);

    setIsDispatching(true);
    setMessages((current) => [
      ...current.slice(-11),
      {
        role: 'user',
        text: cleanIntent,
        stamp: timestamp(),
      },
    ]);

    try {
      const response = await bifrostFetch(DISPATCH_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          intent: cleanIntent,
          cartridge,
          preferred_knight: preferredKnight,
          execution_target: 'bifrost_bridge',
          metadata: {
            source: 'anya_dashboard',
            bridge: 'bifrost',
            helm: 'anya_merlin',
          },
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data?.error || `dispatch ${response.status}`);
      setMessages((current) => [
        ...current.slice(-11),
        {
          role: 'system',
          text: `${data.source ?? 'LOCAL'} :: ${data.response ?? 'Dispatch accepted.'}`,
          stamp: timestamp(),
        },
      ]);
    } catch (error) {
      setMessages((current) => [
        ...current.slice(-11),
        {
          role: 'system',
          text: `Dispatch failed: ${error instanceof Error ? error.message : 'unknown bridge error'}`,
          stamp: timestamp(),
        },
      ]);
    } finally {
      setIsDispatching(false);
    }
  }

  const healthCards = [
    {
      label: 'Bifrost Gate',
      value: status?.gate ?? 'offline',
      detail: status
        ? `${status.current_user}@${status.hostname}`
        : statusError || 'No bridge response',
      icon: Shield,
      tone: status ? 'emerald' : 'amber',
    },
    {
      label: 'Websocket',
      value: isConnected ? 'linked' : 'offline',
      detail: bifrostWebSocketUrl(),
      icon: Radio,
      tone: isConnected ? 'cyan' : 'amber',
    },
    {
      label: 'Long Brain',
      value: 'excalibur',
      detail: 'Long-term agentic brain routed by Bifrost',
      icon: Database,
      tone: 'blue',
    },
    {
      label: 'Short Brain',
      value: 'notebooklm',
      detail: 'Living notebooks for short-term context',
      icon: Activity,
      tone: 'violet',
    },
  ];

  // PROACTIVE UX: Anticipatory Action System
  const proactiveHints = useMemo(() => {
    if (!status) return [];
    const hints = [];
    if (!status.token_present) hints.push('Generate Bifrost Token');
    if (status.gate === 'local-user-mismatch') hints.push('Switch to Sovereign Owner');
    if (latestEvent?.event.includes('fail')) hints.push('Run System Self-Heal');
    return hints;
  }, [status, latestEvent]);

  return (
    <div className="min-h-screen overflow-y-auto bg-[#080a0d] text-slate-100 selection:bg-cyan-500/30">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_20%_0%,rgba(14,165,233,0.22),transparent_32%),radial-gradient(circle_at_80%_12%,rgba(245,158,11,0.16),transparent_30%),linear-gradient(135deg,rgba(15,23,42,0.65),rgba(2,6,23,0.95))]" />

      <main className="relative mx-auto flex min-h-screen max-w-7xl flex-col gap-6 px-4 pb-28 pt-5 lg:px-8">
        {/* S26 Matrix Overlay - Responsive Brutalist Layer */}
        <div className="pointer-events-none absolute top-4 right-4 flex flex-col items-end gap-1 opacity-20 font-mono text-[10px] text-cyan-500 md:opacity-40">
          <span>EDGE_NODE :: SM-S26-ULTRA</span>
          <span>DISP_MODE :: MATRIX_OF_LEADERSHIP</span>
          <span>SEC_STAT :: ARMED</span>
        </div>

        <header className="grid gap-4 lg:grid-cols-[1.35fr_0.65fr]">
          <section
            className="rounded-[2rem] border border-white/10 bg-black/35 p-6 shadow-2xl shadow-cyan-950/30 backdrop-blur"
            aria-labelledby="bridge-title"
          >
            <div className="mb-8 flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="grid h-12 w-12 place-items-center rounded-2xl bg-cyan-400 text-xl font-black text-slate-950 shadow-lg shadow-cyan-500/30">
                  A
                </div>
                <div>
                  <p className="text-xs uppercase tracking-[0.38em] text-cyan-300">
                    Anya Interface
                  </p>
                  <h1 id="bridge-title" className="text-3xl font-black tracking-tight md:text-5xl">
                    Camelot Command Bridge
                  </h1>
                </div>
              </div>
              <div className="rounded-full border border-cyan-300/30 bg-cyan-300/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.25em] text-cyan-200">
                Bifrost Sync
              </div>
            </div>

            <div className="grid gap-3 md:grid-cols-4">
              {healthCards.map((card) => {
                const Icon = card.icon;
                return (
                  <div
                    key={card.label}
                    className="rounded-2xl border border-white/10 bg-white/[0.04] p-4"
                    role="status"
                    aria-label={`${card.label}: ${card.value}`}
                  >
                    <div className="mb-4 flex items-center justify-between">
                      <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                        {card.label}
                      </p>
                      <Icon className={`h-4 w-4 ${toneClass(card.tone)}`} aria-hidden="true" />
                    </div>
                    <p className="text-2xl font-black lowercase">{card.value}</p>
                    <p className="mt-2 min-h-[2.5rem] text-xs leading-5 text-slate-400">
                      {card.detail}
                    </p>
                  </div>
                );
              })}
            </div>
          </section>

          <aside
            className="rounded-[2rem] border border-amber-300/20 bg-amber-300/[0.06] p-6 backdrop-blur"
            aria-label="Helm Status"
          >
            <p className="text-xs uppercase tracking-[0.34em] text-amber-200">Helm</p>
            <div className="mt-5 space-y-4">
              <div className="rounded-2xl bg-black/30 p-4">
                <p className="text-sm text-slate-400">Operator</p>
                <p className="text-2xl font-black">Anya + Merlin</p>
              </div>
              <div className="rounded-2xl bg-black/30 p-4">
                <p className="text-sm text-slate-400">Cognitive Cartridge</p>
                <p className="text-2xl font-black">{status?.cognitive_helm ?? 'sir_alex'}</p>
              </div>
              <div className="rounded-2xl bg-black/30 p-4">
                <p className="text-sm text-slate-400">Bridge Knight</p>
                <p className="text-2xl font-black">{status?.bridge_knight ?? 'sir_link'}</p>
              </div>
            </div>
          </aside>
        </header>

        <section className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
          <div className="rounded-[2rem] border border-white/10 bg-slate-950/70 p-5 backdrop-blur">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.34em] text-slate-500">Cartridges</p>
                <h2 className="text-2xl font-black">Mode Router</h2>
              </div>
              <Zap className="text-amber-300" />
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              {cartridges.map((cartridge) => {
                const Icon = cartridge.icon;
                const selected = selectedCartridge === cartridge.id;
                return (
                  <button
                    key={cartridge.id}
                    onClick={() => setSelectedCartridge(cartridge.id)}
                    aria-pressed={selected}
                    aria-label={`Select ${cartridge.label} cartridge`}
                    className={`group rounded-2xl border p-4 text-left transition ${
                      selected
                        ? 'border-cyan-300 bg-cyan-300/10 shadow-lg shadow-cyan-950/40'
                        : 'border-white/10 bg-white/[0.03] hover:border-white/25 hover:bg-white/[0.06]'
                    }`}
                  >
                    <div className="mb-3 flex items-center justify-between">
                      <Icon
                        className={selected ? 'text-cyan-200' : 'text-slate-400'}
                        aria-hidden="true"
                      />
                      {selected && <CheckCircle2 className="h-4 w-4 text-cyan-200" />}
                    </div>
                    <p className="font-black">{cartridge.label}</p>
                    <p className="mt-1 text-xs uppercase tracking-[0.2em] text-slate-500">
                      {cartridge.helm}
                    </p>
                    <p className="mt-3 text-xs leading-5 text-slate-400">{cartridge.description}</p>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="flex flex-col rounded-[2rem] border border-white/10 bg-black/45 p-5 backdrop-blur">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.34em] text-slate-500">Dispatch</p>
                <h2 className="text-2xl font-black">Bifrost Command Line</h2>
              </div>
              <TerminalSquare className="text-cyan-300" />
            </div>

            <div className="mb-4 rounded-2xl border border-white/10 bg-white/[0.04] p-4">
              {/* Proactive UX Hints */}
              {proactiveHints.length > 0 && (
                <div className="mb-4 flex flex-wrap gap-2 animate-in fade-in slide-in-from-top-2 duration-500">
                  {proactiveHints.map((hint) => (
                    <button
                      key={hint}
                      onClick={() => setIntent(hint)}
                      className="rounded-lg bg-cyan-500/20 border border-cyan-500/40 px-2 py-1 text-[10px] font-bold text-cyan-300 hover:bg-cyan-500/40 transition-colors"
                      aria-label={`Proactive hint: ${hint}`}
                    >
                      💡 {hint}
                    </button>
                  ))}
                </div>
              )}

              <div className="flex flex-wrap items-center gap-2 text-xs uppercase tracking-[0.2em] text-slate-500">
                <span>{activeCartridge.label}</span>
                <ArrowRight className="h-3 w-3" />
                <span>{knightFor(activeCartridge.id)}</span>
                <ArrowRight className="h-3 w-3" />
                <span>Bifrost</span>
              </div>
              <textarea
                value={intent}
                onChange={(event) => setIntent(event.target.value)}
                aria-label="Input intent for Bifrost routing"
                className="mt-4 min-h-32 w-full resize-none rounded-2xl border border-white/10 bg-slate-950/80 p-4 text-sm leading-6 text-slate-100 outline-none transition placeholder:text-slate-600 focus:border-cyan-300"
                placeholder="Type the command for Anya to route through Bifrost..."
              />
              <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
                <p className="text-xs text-slate-500">
                  Auto-detects cartridge keywords, but keeps your selected mode as fallback.
                </p>
                <button
                  onClick={dispatchIntent}
                  disabled={isDispatching || !intent.trim()}
                  className="rounded-full bg-cyan-300 px-5 py-3 text-sm font-black uppercase tracking-[0.18em] text-slate-950 transition hover:bg-cyan-200 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  {isDispatching ? 'Routing...' : 'Dispatch'}
                </button>
              </div>
            </div>

            <div className="grid flex-1 gap-4 lg:grid-cols-2">
              <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-4">
                <div className="mb-3 flex items-center gap-2">
                  <Cable className="h-4 w-4 text-cyan-300" />
                  <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Conversation</p>
                </div>
                <div className="max-h-72 space-y-3 overflow-y-auto pr-1">
                  {messages.map((message, index) => (
                    <div
                      key={`${message.stamp}-${index}`}
                      className="rounded-xl bg-white/[0.04] p-3"
                    >
                      <div className="mb-1 flex items-center justify-between gap-3">
                        <span className="text-xs font-bold uppercase tracking-[0.2em] text-cyan-200">
                          {message.role}
                        </span>
                        <span className="text-[10px] text-slate-600">{message.stamp}</span>
                      </div>
                      <p className="whitespace-pre-wrap text-sm leading-6 text-slate-300">
                        {message.text}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-2xl border border-white/10 bg-slate-950/70 p-4">
                <div className="mb-3 flex items-center gap-2">
                  <Radio className="h-4 w-4 text-emerald-300" />
                  <p className="text-xs uppercase tracking-[0.28em] text-slate-500">
                    Live Bridge Events
                  </p>
                </div>
                <div className="max-h-72 space-y-2 overflow-y-auto pr-1 font-mono text-xs">
                  {events.length === 0 ? (
                    <p className="rounded-xl bg-white/[0.04] p-3 text-slate-500">
                      Waiting for websocket events...
                    </p>
                  ) : (
                    events
                      .slice()
                      .reverse()
                      .map((event, index) => (
                        <div
                          key={`${event.timestamp_ms ?? index}-${index}`}
                          className="rounded-xl border border-white/10 bg-black/30 p-3"
                        >
                          <p className="text-cyan-200">{event.event}</p>
                          <p className="mt-1 text-slate-500">{event.source ?? 'bridge'}</p>
                          {event.detail && (
                            <p className="mt-2 leading-5 text-slate-300">{event.detail}</p>
                          )}
                        </div>
                      ))
                  )}
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
