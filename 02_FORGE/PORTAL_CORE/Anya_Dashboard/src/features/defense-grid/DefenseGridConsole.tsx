import React, { useMemo, useState } from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  ClipboardCheck,
  Lock,
  Radio,
  RefreshCw,
  Send,
  ShieldAlert,
  ShieldCheck,
  TerminalSquare,
} from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { runtimeConfig } from '@/config/runtime';
import { bifrostFetch } from '@/lib/bifrostClient';
import { cn } from '@/lib/utils';

type ConsoleKind = 'system' | 'command' | 'bridge' | 'warn' | 'error';
type GuardState = 'green' | 'amber' | 'red' | 'checking';

interface ConsoleLine {
  kind: ConsoleKind;
  text: string;
  stamp: string;
}

interface GridSubsystem {
  id: string;
  label: string;
  owner: string;
  state: GuardState;
  detail: string;
}

interface QuickCommand {
  label: string;
  command: string;
  intent: string;
  icon: React.ElementType;
  risk: 'low' | 'medium' | 'high';
}

const SUBSYSTEMS: GridSubsystem[] = [
  {
    id: 'rotel',
    label: 'Rotel Telemetry',
    owner: 'Sir Kronos',
    state: 'green',
    detail: 'Memory and process vitals ready for scan.',
  },
  {
    id: 'sentinel',
    label: 'Sentinel Audit',
    owner: 'Sir Sentinel',
    state: 'green',
    detail: 'Integrity audit available through AEGIS pulse.',
  },
  {
    id: 'octavian',
    label: 'Octavian Triage',
    owner: 'Sir Octavian',
    state: 'amber',
    detail: 'Lockdown is guarded and requires explicit confirmation.',
  },
  {
    id: 'castor',
    label: 'Castor Repair',
    owner: 'Sir Castor',
    state: 'green',
    detail: 'Low-risk repair commands route through defensive dispatch.',
  },
];

const QUICK_COMMANDS: QuickCommand[] = [
  {
    label: 'Refresh Grid',
    command: 'status',
    intent: 'Defense Grid status check from user console',
    icon: RefreshCw,
    risk: 'low',
  },
  {
    label: 'Run Pulse',
    command: 'pulse',
    intent: 'Run Defense Grid AEGIS pulse and summarize vitals, drift, and triage',
    icon: Radio,
    risk: 'low',
  },
  {
    label: 'Sentinel Audit',
    command: 'audit',
    intent: 'Run Sir Sentinel defensive audit and return operator-safe findings',
    icon: ClipboardCheck,
    risk: 'medium',
  },
  {
    label: 'Safe Repair',
    command: 'repair',
    intent: 'Ask Sir Castor for low-risk defensive repair recommendations without destructive actions',
    icon: CheckCircle2,
    risk: 'medium',
  },
];

function stamp() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function stateClass(state: GuardState) {
  if (state === 'green') return 'border-emerald-400/30 bg-emerald-400/10 text-emerald-200';
  if (state === 'amber') return 'border-amber-400/30 bg-amber-400/10 text-amber-200';
  if (state === 'checking') return 'border-cyan-400/30 bg-cyan-400/10 text-cyan-200';
  return 'border-rose-400/30 bg-rose-400/10 text-rose-200';
}

function lineClass(kind: ConsoleKind) {
  if (kind === 'error') return 'border-rose-400/30 bg-rose-400/10 text-rose-100';
  if (kind === 'warn') return 'border-amber-400/30 bg-amber-400/10 text-amber-100';
  if (kind === 'bridge') return 'border-cyan-400/30 bg-cyan-400/10 text-cyan-100';
  if (kind === 'command') return 'border-violet-400/30 bg-violet-400/10 text-violet-100';
  return 'border-white/10 bg-white/[0.04] text-slate-200';
}

async function dispatchDefenseIntent(intent: string) {
  const response = await bifrostFetch(runtimeConfig.bifrost.dispatchUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      intent,
      cartridge: 'ENGINEER',
      preferred_knight: 'sir_octavian',
      execution_target: 'defense_grid',
      metadata: {
        source: 'defense_grid_console',
        surface: 'anya_dashboard',
        guardrail: 'operator_console',
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

export default function DefenseGridConsole() {
  const [lines, setLines] = useState<ConsoleLine[]>([
    {
      kind: 'system',
      text: 'Defense Grid console armed. Low-risk commands can run directly; lockdown requires typed confirmation.',
      stamp: stamp(),
    },
  ]);
  const [command, setCommand] = useState('status');
  const [busy, setBusy] = useState(false);
  const [lockdownArmed, setLockdownArmed] = useState(false);
  const [lastAction, setLastAction] = useState('awaiting operator');

  const threatState = useMemo(() => {
    if (lines.some((line) => line.kind === 'error')) return 'amber';
    if (busy) return 'checking';
    return 'green';
  }, [busy, lines]);

  function push(kind: ConsoleKind, text: string) {
    setLines((current) => [...current.slice(-23), { kind, text, stamp: stamp() }]);
  }

  async function runIntent(label: string, intent: string) {
    setBusy(true);
    setLastAction(label);
    try {
      const payload = await dispatchDefenseIntent(intent);
      const summary =
        payload?.response ||
        payload?.payload?.result?.brief ||
        payload?.payload?.status ||
        payload?.payload?.status_text ||
        'Defense Grid dispatch accepted.';
      push('bridge', summary);
    } catch (error) {
      push('error', `Bifrost dispatch failed: ${error instanceof Error ? error.message : 'unknown error'}`);
    } finally {
      setBusy(false);
    }
  }

  async function execute(rawCommand: string) {
    const clean = rawCommand.trim();
    if (!clean || busy) return;

    push('command', `> ${clean}`);
    setCommand('');

    const lower = clean.toLowerCase();

    if (lower === 'clear') {
      setLines([{ kind: 'system', text: 'Console cleared.', stamp: stamp() }]);
      return;
    }

    if (lower === 'help') {
      push('system', 'Commands: status, pulse, audit, repair, lockdown, confirm lockdown, clear.');
      return;
    }

    if (lower === 'lockdown') {
      setLockdownArmed(true);
      push('warn', 'Lockdown is high-risk. Type confirm lockdown to dispatch Sir Octavian.');
      return;
    }

    if (lower === 'confirm lockdown') {
      if (!lockdownArmed) {
        push('error', 'Lockdown is not armed. Run lockdown first.');
        return;
      }
      setLockdownArmed(false);
      await runIntent('lockdown', 'Defense Grid high-risk lockdown request from user console; require Iron Gate approval before execution');
      return;
    }

    const quick = QUICK_COMMANDS.find((item) => item.command === lower);
    if (quick) {
      await runIntent(quick.command, quick.intent);
      return;
    }

    await runIntent('custom', `Defense Grid operator console command: ${clean}`);
  }

  return (
    <div className="min-h-full bg-[#06080d] p-4 text-slate-100 md:p-6">
      <div className="mx-auto flex max-w-7xl flex-col gap-5">
        <header className="grid gap-4 xl:grid-cols-[1.25fr_0.75fr]">
          <section className="rounded-xl border border-slate-800 bg-slate-950/80 p-5 shadow-xl shadow-black/20">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div className="flex items-start gap-3">
                <div className="grid h-11 w-11 shrink-0 place-items-center rounded-lg bg-emerald-400 text-slate-950">
                  <ShieldCheck className="h-6 w-6" />
                </div>
                <div>
                  <h1 className="text-2xl font-black tracking-tight text-white">Defense Grid Console</h1>
                  <p className="mt-1 max-w-2xl text-sm leading-6 text-slate-400">
                    Operator console for AEGIS pulse, Sentinel audit, Octavian triage, and guarded repair dispatch.
                  </p>
                </div>
              </div>
              <div className={cn('rounded-full border px-3 py-1.5 text-xs font-bold uppercase tracking-[0.16em]', stateClass(threatState))}>
                {threatState === 'green' ? 'guard green' : threatState}
              </div>
            </div>

            <div className="mt-5 grid gap-3 md:grid-cols-4">
              {SUBSYSTEMS.map((system) => (
                <div key={system.id} className="rounded-lg border border-slate-800 bg-slate-900/70 p-3">
                  <div className="mb-3 flex items-center justify-between gap-2">
                    <p className="text-xs font-bold uppercase tracking-[0.14em] text-slate-500">{system.owner}</p>
                    <span className={cn('rounded-full border px-2 py-1 text-[10px] font-bold uppercase', stateClass(system.state))}>
                      {system.state}
                    </span>
                  </div>
                  <p className="text-sm font-semibold text-slate-100">{system.label}</p>
                  <p className="mt-2 min-h-[2.5rem] text-xs leading-5 text-slate-500">{system.detail}</p>
                </div>
              ))}
            </div>
          </section>

          <aside className="rounded-xl border border-slate-800 bg-slate-950/80 p-5">
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">Console State</p>
            <div className="mt-4 grid gap-3">
              <div className="flex items-center justify-between rounded-lg bg-slate-900/70 px-3 py-2">
                <span className="text-sm text-slate-400">Dispatch target</span>
                <span className="font-mono text-sm text-emerald-200">defense_grid</span>
              </div>
              <div className="flex items-center justify-between rounded-lg bg-slate-900/70 px-3 py-2">
                <span className="text-sm text-slate-400">Bridge</span>
                <span className="truncate pl-3 font-mono text-xs text-cyan-200">{runtimeConfig.bifrost.dispatchUrl}</span>
              </div>
              <div className="flex items-center justify-between rounded-lg bg-slate-900/70 px-3 py-2">
                <span className="text-sm text-slate-400">Last action</span>
                <span className="text-sm font-semibold text-slate-100">{lastAction}</span>
              </div>
              {lockdownArmed && (
                <div className="rounded-lg border border-amber-400/30 bg-amber-400/10 p-3 text-sm leading-6 text-amber-100">
                  Lockdown armed. Type <span className="font-mono font-bold">confirm lockdown</span> to continue.
                </div>
              )}
            </div>
          </aside>
        </header>

        <section className="grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
          <Card
            className="border-slate-800 bg-slate-950/80 text-slate-100"
            title="Defensive Actions"
            description="Run low-risk commands immediately. High-risk actions are confirmation-gated."
            actions={<ShieldAlert className="h-4 w-4 text-amber-300" />}
          >
            <div className="grid gap-3 sm:grid-cols-2">
              {QUICK_COMMANDS.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.command}
                    onClick={() => void execute(item.command)}
                    className="flex min-h-[5.5rem] items-start justify-between gap-3 rounded-lg border border-slate-800 bg-slate-900/70 p-4 text-left transition hover:border-emerald-300/40 hover:bg-emerald-300/10"
                  >
                    <span>
                      <span className="block text-sm font-bold text-white">{item.label}</span>
                      <span className="mt-1 block text-xs uppercase tracking-[0.14em] text-slate-500">{item.risk} risk</span>
                    </span>
                    <Icon className="h-5 w-5 shrink-0 text-emerald-300" />
                  </button>
                );
              })}
              <button
                onClick={() => void execute('lockdown')}
                className="flex min-h-[5.5rem] items-start justify-between gap-3 rounded-lg border border-amber-400/30 bg-amber-400/10 p-4 text-left transition hover:bg-amber-400/15"
              >
                <span>
                  <span className="block text-sm font-bold text-amber-100">Arm Lockdown</span>
                  <span className="mt-1 block text-xs uppercase tracking-[0.14em] text-amber-300">high risk</span>
                </span>
                <Lock className="h-5 w-5 shrink-0 text-amber-300" />
              </button>
              <button
                onClick={() => void execute('help')}
                className="flex min-h-[5.5rem] items-start justify-between gap-3 rounded-lg border border-slate-800 bg-slate-900/70 p-4 text-left transition hover:border-cyan-300/40 hover:bg-cyan-300/10"
              >
                <span>
                  <span className="block text-sm font-bold text-white">Command Help</span>
                  <span className="mt-1 block text-xs uppercase tracking-[0.14em] text-slate-500">local</span>
                </span>
                <AlertTriangle className="h-5 w-5 shrink-0 text-cyan-300" />
              </button>
            </div>
          </Card>

          <Card
            className="border-slate-800 bg-slate-950/80 text-slate-100"
            title="User Console"
            description="Dispatch a Defense Grid intent or run a local console command."
            actions={<TerminalSquare className="h-4 w-4 text-cyan-300" />}
          >
            <div className="rounded-lg border border-slate-800 bg-black/45 p-3 font-mono">
              <div className="mb-2 text-[10px] uppercase tracking-[0.18em] text-slate-500">operator@camelot / defense-grid</div>
              <textarea
                value={command}
                onChange={(event) => setCommand(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault();
                    void execute(command);
                  }
                }}
                className="min-h-28 w-full resize-none rounded-lg border border-slate-800 bg-slate-950 p-3 text-sm leading-6 text-slate-100 outline-none placeholder:text-slate-600 focus:border-cyan-300"
                placeholder="status | pulse | audit | repair | lockdown | confirm lockdown | clear"
              />
              <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
                <p className="text-xs leading-5 text-slate-500">Press Enter to run. Shift+Enter adds a line.</p>
                <button
                  onClick={() => void execute(command)}
                  disabled={busy || !command.trim()}
                  className="inline-flex items-center gap-2 rounded-lg bg-emerald-300 px-4 py-2 text-xs font-black uppercase tracking-[0.16em] text-slate-950 transition hover:bg-emerald-200 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  {busy ? 'Dispatching' : 'Run'}
                  <Send className="h-4 w-4" />
                </button>
              </div>
            </div>
          </Card>
        </section>

        <Card
          className="border-slate-800 bg-slate-950/80 text-slate-100"
          title="Console Transcript"
          description="Operator commands, dispatch acknowledgments, and guardrail warnings."
          actions={<Radio className="h-4 w-4 text-emerald-300" />}
        >
          <div className="grid max-h-[28rem] gap-2 overflow-y-auto pr-1">
            {lines.map((line, index) => (
              <div key={`${line.stamp}-${index}`} className={cn('rounded-lg border p-3', lineClass(line.kind))}>
                <div className="mb-1 flex items-center justify-between gap-3">
                  <span className="text-[10px] font-bold uppercase tracking-[0.16em]">{line.kind}</span>
                  <span className="text-[10px] opacity-70">{line.stamp}</span>
                </div>
                <p className="whitespace-pre-wrap text-sm leading-6">{line.text}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
