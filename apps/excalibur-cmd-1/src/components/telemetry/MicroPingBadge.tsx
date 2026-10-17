import React from 'react';
import { cn } from '../../lib/utils';
import { Radio } from 'lucide-react';

export interface MicroPingBadgeProps {
  nodeName: string;
  ip?: string;
  latencyMs: number;
  status?: 'nominal' | 'degraded' | 'offline';
  className?: string;
}

export const MicroPingBadge: React.FC<MicroPingBadgeProps> = ({
  nodeName,
  ip,
  latencyMs,
  status = 'nominal',
  className,
}) => {
  let dotColor = 'bg-[#10B981]';
  let textColor = 'text-[#10B981]';
  let glowColor = 'shadow-[0_0_8px_rgba(16,185,129,0.5)]';

  if (status === 'offline' || latencyMs < 0) {
    dotColor = 'bg-[#DE4258]';
    textColor = 'text-[#DE4258]';
    glowColor = 'shadow-[0_0_8px_rgba(222,66,88,0.5)]';
  } else if (status === 'degraded' || latencyMs > 80) {
    dotColor = 'bg-[#F59E0B]';
    textColor = 'text-[#F59E0B]';
    glowColor = 'shadow-[0_0_8px_rgba(245,158,11,0.5)]';
  }

  return (
    <div
      className={cn(
        'inline-flex items-center gap-1.5 px-2 py-0.5 rounded border border-white/10 bg-[#050510]/80 backdrop-blur-sm font-mono text-[10px] select-none',
        className
      )}
      title={ip ? `${nodeName} (${ip}) - Latency: ${latencyMs}ms` : `${nodeName} - Latency: ${latencyMs}ms`}
    >
      <Radio className="w-3 h-3 text-[#D4AF37]/80 shrink-0" />
      <span className="text-[#F1EFF4]/80 font-medium truncate max-w-[85px]">{nodeName}</span>
      <span className={cn('w-1.5 h-1.5 rounded-full shrink-0 animate-pulse', dotColor, glowColor)} />
      <span className={cn('font-bold', textColor)}>
        {latencyMs >= 0 ? `${latencyMs}ms` : 'OFFLINE'}
      </span>
    </div>
  );
};
