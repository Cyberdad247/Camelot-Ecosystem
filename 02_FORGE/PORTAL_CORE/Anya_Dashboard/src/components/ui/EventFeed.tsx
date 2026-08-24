import React from 'react';
import { Radio } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { AnyaSocketEvent } from '@/features/brain/useAnyaSocket';

interface EventFeedProps {
  events: AnyaSocketEvent[];
  isConnected: boolean;
  maxRows?: number;
  filterSource?: string;
  className?: string;
  compact?: boolean;
}

function eventColor(event: string) {
  if (event.includes('error') || event.includes('fail')) return 'text-red-400';
  if (event.includes('complete') || event.includes('done') || event.includes('success')) return 'text-emerald-400';
  if (event.includes('dispatch') || event.includes('route')) return 'text-blue-400';
  if (event.includes('research') || event.includes('chimera')) return 'text-blue-300';
  return 'text-slate-300';
}

function formatStamp(ts?: number) {
  if (!ts) return '';
  return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

export default function EventFeed({
  events,
  isConnected,
  maxRows = 20,
  filterSource,
  className,
  compact = false,
}: EventFeedProps) {
  const filtered = filterSource
    ? events.filter((e) => e.source?.toLowerCase().includes(filterSource.toLowerCase()))
    : events;
  const visible = filtered.slice(-maxRows).reverse();

  return (
    <div className={cn('flex flex-col', className)}>
      <div className="mb-2 flex items-center gap-2">
        <Radio className="h-3 w-3 text-fuchsia-400" />
        <span className="text-xs font-semibold uppercase tracking-widest text-slate-400">
          Live Feed
        </span>
        <span
          className={cn(
            'ml-auto h-2 w-2 rounded-full',
            isConnected ? 'bg-emerald-400 shadow-[0_0_6px_#34d399]' : 'bg-red-500',
          )}
        />
        <span className="text-[10px] text-slate-500">{isConnected ? 'WS LIVE' : 'WS DARK'}</span>
      </div>

      <div className="flex-1 overflow-y-auto">
        {visible.length === 0 ? (
          <p className="text-xs text-slate-600 italic">No events yet — dispatch an intent to see output here.</p>
        ) : (
          <ul className="space-y-0.5">
            {visible.map((ev, i) => (
              <li key={i} className={cn('flex gap-2 font-mono', compact ? 'text-[10px]' : 'text-xs')}>
                <span className="shrink-0 text-slate-600">{formatStamp(ev.timestamp_ms)}</span>
                {ev.source && (
                  <span className="shrink-0 text-fuchsia-500/70">[{ev.source}]</span>
                )}
                <span className={cn('min-w-0 truncate', eventColor(ev.event ?? ''))}>
                  {ev.event}
                  {ev.detail ? ` — ${ev.detail}` : ''}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
