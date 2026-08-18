import EventFeed from '@/components/ui/EventFeed';
import { runtimeConfig } from '@/config/runtime';
import { useAnyaSocket } from '@/features/brain/useAnyaSocket';
import { bifrostFetch } from '@/lib/bifrostClient';
import { cn } from '@/lib/utils';
import type { CartridgeMeta } from '@/types/camelot';
import { ArrowUpRight, Copy, Loader2, Send } from 'lucide-react';
import type React from 'react';
import { Suspense, lazy, useState } from 'react';
import { Navigate, useParams } from 'react-router-dom';
import { CARTRIDGE_BY_SLUG } from './registry';

const DECKS: Record<string, React.LazyExoticComponent<(props: DeckProps) => React.ReactElement>> = {
  cognitive: lazy(() => import('./decks/CognitiveDeck')),
  engineer: lazy(() => import('./decks/EngineerDeck')),
  research: lazy(() => import('./decks/ResearchDeck')),
  creative: lazy(() => import('./decks/CreativeDeck')),
  marketing: lazy(() => import('./decks/MarketingDeck')),
  legal: lazy(() => import('./decks/LegalDeck')),
  brainstorm: lazy(() => import('./decks/BrainstormDeck')),
  critical: lazy(() => import('./decks/CriticalDeck')),
};

export interface DeckProps {
  cartridge: CartridgeMeta;
  onDispatch: (intent: string, params: Record<string, unknown>) => Promise<void>;
  dispatching: boolean;
  lastResult: string | null;
}

export default function CartridgeDeck() {
  const { id } = useParams<{ id: string }>();
  const cartridge = id ? CARTRIDGE_BY_SLUG[id] : null;
  const [dispatching, setDispatching] = useState(false);
  const [lastResult, setLastResult] = useState<string | null>(null);
  const [lastMeta, setLastMeta] = useState<{
    knight?: string;
    model?: string;
    latency_ms?: number;
  } | null>(null);
  const { events, isConnected } = useAnyaSocket();

  if (!cartridge) return <Navigate to="/" replace />;

  const Deck = DECKS[cartridge.slug];
  const Icon = cartridge.icon;

  const handleDispatch = async (intent: string, params: Record<string, unknown>) => {
    if (!intent.trim() || dispatching) return;
    setDispatching(true);
    setLastResult(null);
    try {
      // Primary: dashboard-native dispatch (real LLM via CLIProxy)
      const primaryRes = await fetch('/api/cartridge/dispatch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ intent, cartridge: cartridge.id, params }),
      });
      if (primaryRes.ok) {
        const data = await primaryRes.json().catch(() => ({}));
        if (data.response && !data.error) {
          setLastResult(data.response);
          setLastMeta({ knight: data.knight, model: data.model, latency_ms: data.latency_ms });
          return;
        }
        if (data.error) {
          setLastResult(`[${data.cartridge ?? cartridge.id}] ${data.error}`);
          return;
        }
      }

      // Fallback: Morgana Bridge
      const res = await bifrostFetch(runtimeConfig.bifrost.dispatchUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ intent, cartridge: cartridge.id, params }),
      });
      if (res.ok) {
        const data = await res.json().catch(() => ({}));
        setLastResult(data.result ?? data.synthesis ?? data.response ?? '(awaiting stream…)');
      } else {
        setLastResult(`Error ${res.status}: ${res.statusText}`);
      }
    } catch {
      setLastResult(
        'Dispatch unreachable — ensure dashboard server and morgana_bridge are running',
      );
    } finally {
      setDispatching(false);
    }
  };

  return (
    <div className="min-h-full flex flex-col">
      {/* Cartridge header band */}
      <div
        className={cn(
          'border-b px-6 py-4 flex items-center gap-4',
          cartridge.borderClass,
          cartridge.bgClass,
        )}
      >
        <div
          className="flex h-10 w-10 items-center justify-center rounded-xl border"
          style={{
            borderColor: cartridge.accentHex + '60',
            backgroundColor: cartridge.accentHex + '15',
          }}
        >
          <Icon className={cn('h-5 w-5', cartridge.textClass)} />
        </div>
        <div>
          <h1 className={cn('text-xl font-black', cartridge.textClass)}>
            {cartridge.label} Command Deck
          </h1>
          <p className="text-xs text-slate-500">
            {cartridge.knight} · {cartridge.description}
          </p>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <span
            className={cn(
              'rounded-full border px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-widest',
              cartridge.textClass,
              cartridge.borderClass,
            )}
          >
            {cartridge.id}
          </span>
        </div>
      </div>

      {/* Body */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-0 overflow-hidden">
        {/* Left: Deck-specific controls */}
        <div className="lg:col-span-2 border-r border-slate-800/50 overflow-y-auto p-6">
          <Suspense
            fallback={
              <div className="flex items-center justify-center py-20">
                <Loader2 className="h-6 w-6 animate-spin text-slate-600" />
              </div>
            }
          >
            {Deck && (
              <Deck
                cartridge={cartridge}
                onDispatch={handleDispatch}
                dispatching={dispatching}
                lastResult={lastResult}
              />
            )}
          </Suspense>
        </div>

        {/* Right: Stream + result */}
        <div className="flex flex-col overflow-hidden p-4 gap-4">
          {/* Result panel */}
          {(lastResult || dispatching) && (
            <div
              className={cn(
                'rounded-xl border p-4 space-y-2',
                cartridge.borderClass,
                cartridge.bgClass,
              )}
            >
              <div className="flex items-center gap-2">
                {dispatching ? (
                  <Loader2 className={cn('h-4 w-4 animate-spin', cartridge.textClass)} />
                ) : (
                  <ArrowUpRight className={cn('h-4 w-4', cartridge.textClass)} />
                )}
                <span
                  className={cn(
                    'text-xs font-semibold uppercase tracking-widest',
                    cartridge.textClass,
                  )}
                >
                  {dispatching
                    ? 'Dispatching…'
                    : `${lastMeta?.knight ?? cartridge.knight} Response`}
                </span>
                {lastResult && (
                  <button
                    onClick={() => navigator.clipboard.writeText(lastResult)}
                    className="ml-auto text-slate-600 hover:text-slate-400"
                  >
                    <Copy className="h-3.5 w-3.5" />
                  </button>
                )}
              </div>
              {lastMeta && !dispatching && (
                <div className="flex items-center gap-2 text-[10px] text-slate-500 font-mono">
                  {lastMeta.model && <span>{lastMeta.model}</span>}
                  {lastMeta.latency_ms && <span>· {lastMeta.latency_ms}ms</span>}
                </div>
              )}
              {lastResult && (
                <p className="text-sm text-slate-200 leading-relaxed whitespace-pre-wrap max-h-64 overflow-y-auto">
                  {lastResult}
                </p>
              )}
            </div>
          )}

          {/* Live feed */}
          <div className="flex-1 rounded-xl border border-slate-800 bg-slate-900/30 p-3 overflow-hidden min-h-[200px]">
            <EventFeed
              events={events}
              isConnected={isConnected}
              maxRows={40}
              filterSource={cartridge.id.toLowerCase()}
              className="h-full"
              compact
            />
          </div>
        </div>
      </div>
    </div>
  );
}
