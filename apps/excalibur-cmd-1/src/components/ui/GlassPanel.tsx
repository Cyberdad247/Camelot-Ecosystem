import React from 'react';
import { cn } from '../../lib/utils';

export interface GlassPanelProps extends React.HTMLAttributes<HTMLDivElement> {
  glow?: 'gold' | 'purple' | 'none' | 'cyan';
  density?: 'compact' | 'standard' | 'spacious';
  tier?: 'ground' | 'sovereign' | 'visor';
  cornerAccents?: boolean;
}

export const GlassPanel = ({
  children,
  className,
  glow = 'none',
  density = 'standard',
  tier,
  cornerAccents = true,
  ...props
}: GlassPanelProps) => {
  const densityStyles = {
    compact: 'p-3',
    standard: 'p-4 sm:p-5',
    spacious: 'p-6 sm:p-8',
  };

  const tierStyles = {
    ground: 'glass-panel-ground',
    sovereign: 'glass-panel-sovereign',
    visor: 'glass-panel-visor',
  };

  const glowStyles = {
    gold: 'shadow-[0_0_25px_rgba(212,175,55,0.25)] border-[#D4AF37]/50 bg-[#050510]/80',
    purple: 'shadow-[0_0_25px_rgba(75,0,130,0.35)] border-[#4B0082]/60 bg-[#050510]/80',
    cyan: 'shadow-[0_0_25px_rgba(0,240,255,0.25)] border-[#00F0FF]/40 bg-[#050510]/80',
    none: 'border-white/10 bg-[#050510]/70 shadow-[0_8px_32px_rgba(0,0,0,0.5)]',
  };

  return (
    <div
      className={cn(
        'relative rounded-xl border backdrop-blur-xl transition-all duration-300',
        densityStyles[density],
        tier ? tierStyles[tier] : glowStyles[glow],
        className
      )}
      {...props}
    >
      {/* Corner accent decorations for sovereign styling */}
      {cornerAccents && (
        <>
          <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-[#D4AF37]/50 pointer-events-none rounded-tl-sm" />
          <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-[#D4AF37]/50 pointer-events-none rounded-tr-sm" />
          <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-[#D4AF37]/50 pointer-events-none rounded-bl-sm" />
          <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-[#D4AF37]/50 pointer-events-none rounded-br-sm" />
        </>
      )}
      {children}
    </div>
  );
};
