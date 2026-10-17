import React from 'react';
import { cn } from '../../lib/utils';
import { triggerHaptic, HapticPattern } from '../../lib/haptics';

export interface TacticalButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'gold' | 'purple' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  haptic?: HapticPattern | false;
  icon?: React.ReactNode;
  loading?: boolean;
}

export const TacticalButton = React.forwardRef<HTMLButtonElement, TacticalButtonProps>(
  (
    {
      children,
      className,
      variant = 'gold',
      size = 'md',
      haptic = 'tap',
      icon,
      loading = false,
      disabled,
      onClick,
      ...props
    },
    ref
  ) => {
    const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
      if (disabled || loading) return;
      if (haptic !== false) {
        triggerHaptic(haptic);
      }
      onClick?.(e);
    };

    const variantStyles = {
      gold: 'bg-[#050510]/85 border-[#D4AF37]/50 text-[#F1EFF4] hover:border-[#D4AF37] hover:bg-[#D4AF37]/15 shadow-[0_0_15px_rgba(212,175,55,0.15)] active:scale-[0.98]',
      purple: 'bg-[#050510]/85 border-[#9D4EDD]/50 text-[#F1EFF4] hover:border-[#9D4EDD] hover:bg-[#4B0082]/30 shadow-[0_0_15px_rgba(157,78,221,0.2)] active:scale-[0.98]',
      ghost: 'bg-transparent border-white/10 text-[#F1EFF4]/80 hover:text-white hover:border-white/30 hover:bg-white/5 active:scale-[0.98]',
      danger: 'bg-[#DE4258]/10 border-[#DE4258]/50 text-[#DE4258] hover:border-[#DE4258] hover:bg-[#DE4258]/25 shadow-[0_0_15px_rgba(222,66,88,0.2)] active:scale-[0.98]',
    };

    const sizeStyles = {
      sm: 'text-xs py-1.5 px-3 min-h-[36px] gap-1.5',
      md: 'text-sm py-2.5 px-4 min-h-[44px] gap-2',
      lg: 'text-base py-3 px-6 min-h-[50px] gap-2.5',
    };

    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        onClick={handleClick}
        className={cn(
          'relative inline-flex items-center justify-center font-mono font-medium uppercase tracking-wider',
          'border rounded-lg transition-all duration-150 select-none cursor-pointer',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#D4AF37] focus-visible:ring-offset-2 focus-visible:ring-offset-[#050510]',
          'disabled:opacity-40 disabled:cursor-not-allowed disabled:active:scale-100',
          variantStyles[variant],
          sizeStyles[size],
          className
        )}
        {...props}
      >
        {/* Tactical Corner Accents */}
        <span className="absolute top-0 left-0 w-1.5 h-1.5 border-t border-l border-[#D4AF37]/60 pointer-events-none rounded-tl-sm" />
        <span className="absolute bottom-0 right-0 w-1.5 h-1.5 border-b border-r border-[#D4AF37]/60 pointer-events-none rounded-br-sm" />

        {loading ? (
          <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
        ) : (
          icon && <span className="shrink-0">{icon}</span>
        )}
        <span>{children}</span>
      </button>
    );
  }
);

TacticalButton.displayName = 'TacticalButton';
