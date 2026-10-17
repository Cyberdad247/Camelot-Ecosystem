import React from 'react';
import { cn } from '../../lib/utils';

export interface MetricStatProps extends React.HTMLAttributes<HTMLDivElement> {
  label: string;
  value: number | string;
  unit?: string;
  ceiling?: number;
  delta?: number;
  warningThreshold?: number; // e.g. 80
  criticalThreshold?: number; // e.g. 90
}

export const MetricStat = ({
  label,
  value,
  unit,
  ceiling,
  delta,
  warningThreshold = 80,
  criticalThreshold = 90,
  className,
  ...props
}: MetricStatProps) => {
  const numericVal = typeof value === 'number' ? value : parseFloat(value);
  const percentage =
    ceiling && !isNaN(numericVal) && ceiling > 0 ? (numericVal / ceiling) * 100 : null;

  let valueColor = 'text-[#F1EFF4]';
  if (percentage !== null) {
    if (percentage >= criticalThreshold) {
      valueColor = 'text-[#DE4258] animate-pulse';
    } else if (percentage >= warningThreshold) {
      valueColor = 'text-[#F59E0B]';
    } else {
      valueColor = 'text-[#D4AF37]';
    }
  }

  return (
    <div
      className={cn(
        'flex flex-col p-2.5 rounded-lg border border-white/10 bg-[#050510]/60 backdrop-blur-md',
        className
      )}
      {...props}
    >
      <div className="flex items-center justify-between gap-2 text-xs font-mono uppercase text-[#9E9AA7]">
        <span className="truncate">{label}</span>
        {delta !== undefined && (
          <span
            className={cn(
              'text-[10px] font-bold',
              delta > 0 ? 'text-[#10B981]' : delta < 0 ? 'text-[#DE4258]' : 'text-[#9E9AA7]'
            )}
          >
            {delta > 0 ? `+${delta}%` : `${delta}%`}
          </span>
        )}
      </div>

      <div className="flex items-baseline gap-1 mt-1 font-mono">
        <span className={cn('text-lg sm:text-xl font-bold tracking-tight', valueColor)}>
          {value}
        </span>
        {unit && <span className="text-xs text-[#9E9AA7] font-normal">{unit}</span>}
        {ceiling !== undefined && (
          <span className="text-[10px] text-[#9E9AA7]/60 ml-auto font-mono">
            / {ceiling} {unit}
          </span>
        )}
      </div>

      {percentage !== null && (
        <div className="w-full h-1 bg-white/10 rounded-full mt-2 overflow-hidden">
          <div
            className={cn(
              'h-full transition-all duration-300 rounded-full',
              percentage >= criticalThreshold
                ? 'bg-[#DE4258]'
                : percentage >= warningThreshold
                ? 'bg-[#F59E0B]'
                : 'bg-[#D4AF37]'
            )}
            style={{ width: `${Math.min(100, Math.max(0, percentage))}%` }}
          />
        </div>
      )}
    </div>
  );
};
