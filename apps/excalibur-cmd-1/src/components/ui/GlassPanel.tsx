import React from 'react';
import { cn } from '../../lib/utils';

interface GlassPanelProps extends React.HTMLAttributes<HTMLDivElement> {
  glow?: 'gold' | 'purple' | 'none';
  density?: 'compact' | 'standard';
}

export const GlassPanel = ({
  children,
  className,
  glow = 'none',
  density = 'standard',
  ...props
}: GlassPanelProps) => {
  return (
    <div
      className={cn(
        'relative rounded-xl border backdrop-blur-xl transition-all duration-300',
        density === 'compact' ? 'p-3' : 'p-4 sm:p-5',
        glow === 'gold' && 'shadow-[0_0_25px_rgba(212,175,55,0.25)] border-[#D4AF37]/50 bg-[#050510]/80',
        glow === 'purple' && 'shadow-[0_0_25px_rgba(75,0,130,0.35)] border-[#4B0082]/60 bg-[#050510]/80',
        glow === 'none' && 'border-white/10 bg-[#050510]/70 shadow-[0_8px_32px_rgba(0,0,0,0.5)]',
        className
      )}
      {...props}
    >
      {/* Corner accent decorations for sovereign styling */}
      <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-[#D4AF37]/40 pointer-events-none rounded-tl-sm" />
      <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-[#D4AF37]/40 pointer-events-none rounded-tr-sm" />
      <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-[#D4AF37]/40 pointer-events-none rounded-bl-sm" />
      <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-[#D4AF37]/40 pointer-events-none rounded-br-sm" />
      {children}
    </div>
  );
};
