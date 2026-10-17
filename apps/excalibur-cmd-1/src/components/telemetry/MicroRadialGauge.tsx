import React from 'react';
import { cn } from '../../lib/utils';

export interface MicroRadialGaugeProps {
  value: number;
  ceiling: number;
  label?: string;
  unit?: string;
  size?: 'sm' | 'md' | 'lg';
  warningThreshold?: number; // default 75%
  criticalThreshold?: number; // default 90%
  className?: string;
  showLabel?: boolean;
}

export const MicroRadialGauge: React.FC<MicroRadialGaugeProps> = ({
  value,
  ceiling,
  label,
  unit = '%',
  size = 'md',
  warningThreshold = 75,
  criticalThreshold = 90,
  className,
  showLabel = true,
}) => {
  const percentage = Math.min(100, Math.max(0, (value / ceiling) * 100));

  const sizeConfig = {
    sm: { dimension: 40, strokeWidth: 3.5, fontSize: 'text-[9px]', radius: 15 },
    md: { dimension: 52, strokeWidth: 4.5, fontSize: 'text-[11px]', radius: 20 },
    lg: { dimension: 68, strokeWidth: 6, fontSize: 'text-xs', radius: 26 },
  };

  const { dimension, strokeWidth, fontSize, radius } = sizeConfig[size];
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  let strokeColor = '#D4AF37';
  let glowColor = 'rgba(212, 175, 55, 0.4)';
  if (percentage >= criticalThreshold) {
    strokeColor = '#DE4258';
    glowColor = 'rgba(222, 66, 88, 0.5)';
  } else if (percentage >= warningThreshold) {
    strokeColor = '#F59E0B';
    glowColor = 'rgba(245, 158, 11, 0.5)';
  }

  const centerVal = unit === '%' ? Math.round(percentage) : Math.round(value);

  return (
    <div
      className={cn('inline-flex flex-col items-center justify-center shrink-0 select-none', className)}
      role="progressbar"
      aria-valuenow={Math.round(value)}
      aria-valuemin={0}
      aria-valuemax={ceiling}
      aria-label={`${label ? `${label}: ` : ''}${Math.round(percentage)}%`}
    >
      <div className="relative flex items-center justify-center" style={{ width: dimension, height: dimension }}>
        <svg width={dimension} height={dimension} className="rotate-[-90deg]">
          {/* Background Track */}
          <circle
            cx={dimension / 2}
            cy={dimension / 2}
            r={radius}
            fill="transparent"
            stroke="rgba(241, 239, 244, 0.1)"
            strokeWidth={strokeWidth}
          />

          {/* Active Value Arc */}
          <circle
            cx={dimension / 2}
            cy={dimension / 2}
            r={radius}
            fill="transparent"
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-500 ease-out"
            style={{
              filter: `drop-shadow(0 0 4px ${glowColor})`,
            }}
          />
        </svg>

        {/* Center Readout */}
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={cn('font-mono font-bold tracking-tight', fontSize)} style={{ color: strokeColor }}>
            {centerVal}
            <span className="text-[8px] opacity-70 font-normal">{unit === '%' ? '%' : ''}</span>
          </span>
        </div>
      </div>

      {showLabel && label && (
        <span className="text-[9px] font-mono uppercase tracking-wider text-[#9E9AA7] mt-1 text-center truncate max-w-[80px]">
          {label}
        </span>
      )}
    </div>
  );
};
