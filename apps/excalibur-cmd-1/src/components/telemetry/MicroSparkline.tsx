import React from 'react';
import { cn } from '../../lib/utils';

export interface MicroSparklineProps {
  data: number[];
  color?: 'gold' | 'cyan' | 'purple' | 'emerald' | 'garnet';
  height?: number;
  width?: number | string;
  strokeWidth?: number;
  fill?: boolean;
  className?: string;
  showBeacon?: boolean;
}

export const MicroSparkline: React.FC<MicroSparklineProps> = ({
  data,
  color = 'gold',
  height = 24,
  width = 64,
  strokeWidth = 1.5,
  fill = true,
  className,
  showBeacon = true,
}) => {
  if (!data || data.length === 0) {
    return <div className={cn('h-6 w-16 bg-white/5 rounded', className)} />;
  }

  const colorMap = {
    gold: {
      stroke: '#D4AF37',
      glow: 'rgba(212, 175, 55, 0.4)',
      fillStart: 'rgba(212, 175, 55, 0.25)',
      fillEnd: 'rgba(212, 175, 55, 0.0)',
    },
    cyan: {
      stroke: '#00F0FF',
      glow: 'rgba(0, 240, 255, 0.4)',
      fillStart: 'rgba(0, 240, 255, 0.25)',
      fillEnd: 'rgba(0, 240, 255, 0.0)',
    },
    purple: {
      stroke: '#9D4EDD',
      glow: 'rgba(157, 78, 221, 0.4)',
      fillStart: 'rgba(157, 78, 221, 0.25)',
      fillEnd: 'rgba(157, 78, 221, 0.0)',
    },
    emerald: {
      stroke: '#10B981',
      glow: 'rgba(16, 185, 129, 0.4)',
      fillStart: 'rgba(16, 185, 129, 0.25)',
      fillEnd: 'rgba(16, 185, 129, 0.0)',
    },
    garnet: {
      stroke: '#DE4258',
      glow: 'rgba(222, 66, 88, 0.4)',
      fillStart: 'rgba(222, 66, 88, 0.25)',
      fillEnd: 'rgba(222, 66, 88, 0.0)',
    },
  };

  const scheme = colorMap[color] || colorMap.gold;
  const minVal = Math.min(...data);
  const maxVal = Math.max(...data);
  const range = maxVal - minVal === 0 ? 1 : maxVal - minVal;

  const viewBoxWidth = 100;
  const viewBoxHeight = 40;
  const padding = 4;

  const points = data.map((val, idx) => {
    const x = padding + (idx / Math.max(1, data.length - 1)) * (viewBoxWidth - padding * 2);
    const normalizedY = (val - minVal) / range;
    const y = viewBoxHeight - padding - normalizedY * (viewBoxHeight - padding * 2);
    return { x, y };
  });

  const linePath = points.reduce((acc, pt, idx) => {
    return idx === 0 ? `M ${pt.x} ${pt.y}` : `${acc} L ${pt.x} ${pt.y}`;
  }, '');

  const areaPath = `${linePath} L ${points[points.length - 1].x} ${viewBoxHeight} L ${points[0].x} ${viewBoxHeight} Z`;
  const lastPoint = points[points.length - 1];
  const gradientId = `spark-grad-${color}-${Math.random().toString(36).substring(2, 7)}`;

  return (
    <div
      className={cn('inline-flex items-center justify-center shrink-0 overflow-hidden', className)}
      style={{ height, width }}
    >
      <svg
        viewBox={`0 0 ${viewBoxWidth} ${viewBoxHeight}`}
        className="w-full h-full overflow-visible"
        preserveAspectRatio="none"
        role="img"
        aria-label={`Micro telemetry trend chart. Current value: ${data[data.length - 1]}`}
      >
        <defs>
          <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={scheme.fillStart} />
            <stop offset="100%" stopColor={scheme.fillEnd} />
          </linearGradient>
          <filter id={`glow-${gradientId}`} x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="0" stdDeviation="1.5" floodColor={scheme.glow} />
          </filter>
        </defs>

        {fill && <path d={areaPath} fill={`url(#${gradientId})`} />}

        <path
          d={linePath}
          fill="none"
          stroke={scheme.stroke}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeLinejoin="round"
          filter={`url(#glow-${gradientId})`}
        />

        {showBeacon && lastPoint && (
          <circle
            cx={lastPoint.x}
            cy={lastPoint.y}
            r="3"
            fill={scheme.stroke}
            className="animate-pulse"
          />
        )}
      </svg>
    </div>
  );
};
