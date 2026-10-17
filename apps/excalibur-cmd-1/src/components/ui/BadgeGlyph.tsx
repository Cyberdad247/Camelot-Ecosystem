import React from 'react';
import { cn } from '../../lib/utils';

export type SystemStatusType =
  | 'ONLINE'
  | 'OFFLINE'
  | 'SYNCING'
  | 'AIRGAP'
  | 'DEGRADED'
  | 'ACTIVE'
  | 'SEALED'
  | 'LOCKED';

export interface BadgeGlyphProps extends React.HTMLAttributes<HTMLSpanElement> {
  status: SystemStatusType;
  label?: string;
  glyph?: string;
  pulse?: boolean;
  size?: 'sm' | 'md';
}

export const BadgeGlyph = ({
  status,
  label,
  glyph,
  pulse = true,
  size = 'md',
  className,
  ...props
}: BadgeGlyphProps) => {
  const statusConfig: Record<
    SystemStatusType,
    { color: string; border: string; bg: string; defaultGlyph: string; text: string }
  > = {
    ONLINE: {
      color: 'text-[#10B981]',
      border: 'border-[#10B981]/40',
      bg: 'bg-[#10B981]/10',
      defaultGlyph: '⚡',
      text: 'ONLINE',
    },
    ACTIVE: {
      color: 'text-[#D4AF37]',
      border: 'border-[#D4AF37]/50',
      bg: 'bg-[#D4AF37]/10',
      defaultGlyph: '⚜️',
      text: 'ACTIVE',
    },
    SYNCING: {
      color: 'text-[#00F0FF]',
      border: 'border-[#00F0FF]/40',
      bg: 'bg-[#00F0FF]/10',
      defaultGlyph: '🔄',
      text: 'SYNCING',
    },
    AIRGAP: {
      color: 'text-[#9D4EDD]',
      border: 'border-[#9D4EDD]/40',
      bg: 'bg-[#4B0082]/20',
      defaultGlyph: '🛡️',
      text: 'AIR-GAPPED',
    },
    SEALED: {
      color: 'text-[#D4AF37]',
      border: 'border-[#D4AF37]/60',
      bg: 'bg-[#D4AF37]/15',
      defaultGlyph: '🔒',
      text: 'SEALED',
    },
    DEGRADED: {
      color: 'text-[#F59E0B]',
      border: 'border-[#F59E0B]/40',
      bg: 'bg-[#F59E0B]/10',
      defaultGlyph: '⚠️',
      text: 'DEGRADED',
    },
    OFFLINE: {
      color: 'text-[#9E9AA7]',
      border: 'border-white/10',
      bg: 'bg-white/5',
      defaultGlyph: '⚪',
      text: 'OFFLINE',
    },
    LOCKED: {
      color: 'text-[#DE4258]',
      border: 'border-[#DE4258]/50',
      bg: 'bg-[#DE4258]/10',
      defaultGlyph: '🛑',
      text: 'LOCKED',
    },
  };

  const config = statusConfig[status] || statusConfig.OFFLINE;
  const displayGlyph = glyph ?? config.defaultGlyph;
  const displayText = label ?? config.text;

  return (
    <span
      className={cn(
        'inline-flex items-center font-mono uppercase tracking-wider rounded border font-semibold select-none',
        config.bg,
        config.border,
        config.color,
        size === 'sm' ? 'px-2 py-0.5 text-[10px] gap-1' : 'px-2.5 py-1 text-xs gap-1.5',
        className
      )}
      {...props}
    >
      <span
        className={cn(
          'inline-block shrink-0',
          pulse && status === 'ONLINE' && 'animate-pulse'
        )}
      >
        {displayGlyph}
      </span>
      <span>{displayText}</span>
    </span>
  );
};
