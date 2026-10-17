import React, { useState, useEffect } from 'react';
import { cn } from '../../lib/utils';
import { TelemetryData } from '../../types';
import { MicroSparkline } from './MicroSparkline';
import { MicroRadialGauge } from './MicroRadialGauge';
import { MicroPingBadge } from './MicroPingBadge';
import { MicroFPSMeter } from './MicroFPSMeter';
import { ArrowUpRight, Cpu } from 'lucide-react';

export interface MicroTelemetryStripProps {
  telemetry?: TelemetryData | null;
  className?: string;
  variant?: 'compact' | 'full';
}

export const MicroTelemetryStrip: React.FC<MicroTelemetryStripProps> = ({
  telemetry,
  className,
  variant = 'full',
}) => {
  const [ramHistory, setRamHistory] = useState<number[]>([1200, 1250, 1310, 1280, 1340, 1420]);

  useEffect(() => {
    if (telemetry?.ramUsageMB) {
      setRamHistory((prev) => {
        const next = [...prev.slice(-9), telemetry.ramUsageMB];
        return next;
      });
    }
  }, [telemetry?.ramUsageMB]);

  const ramUsed = telemetry?.ramUsageMB || 1420;
  const ramCeiling = telemetry?.ramCeilingMB || 4096;
  const ramPercent = telemetry?.ramPercent || Math.round((ramUsed / ramCeiling) * 100);
  const cpuLoad = telemetry?.globalLoad || 24;
  const egress = telemetry?.networkEgress || 142.5;

  return (
    <div
      className={cn(
        'flex items-center gap-2 sm:gap-4 p-2 rounded-lg border border-[#D4AF37]/30 bg-[#050510]/90 backdrop-blur-xl font-mono text-xs select-none shadow-[0_0_20px_rgba(75,0,130,0.25)] overflow-x-auto scrollbar-none',
        className
      )}
    >
      {/* 1. Micro Radial Gauge (RAM Scarcity) */}
      <div className="flex items-center gap-2 pr-2 sm:pr-3 border-r border-[#4B0082]/60 shrink-0">
        <MicroRadialGauge
          value={ramUsed}
          ceiling={ramCeiling}
          unit="MB"
          size="sm"
          showLabel={false}
        />
        <div className="flex flex-col">
          <span className="text-[9px] uppercase tracking-wider text-[#9E9AA7]">RAM SCARCITY</span>
          <span className="text-xs font-bold text-[#D4AF37]">
            {ramUsed} <span className="text-[10px] text-[#9E9AA7]/80">/ {ramCeiling}MB</span>
          </span>
        </div>
      </div>

      {/* 2. Micro Sparkline (RAM Trend) */}
      <div className="hidden md:flex flex-col justify-center px-1 shrink-0">
        <div className="flex items-center justify-between text-[9px] text-[#9E9AA7] mb-0.5">
          <span>MEM TREND</span>
          <span className="text-[#00F0FF] font-bold">{ramPercent}%</span>
        </div>
        <MicroSparkline data={ramHistory} color="gold" width={72} height={20} />
      </div>

      {/* 3. CPU Global Load */}
      <div className="flex items-center gap-1.5 px-2 border-r border-[#4B0082]/60 shrink-0">
        <Cpu className="w-3.5 h-3.5 text-[#00F0FF]" />
        <div className="flex flex-col">
          <span className="text-[9px] uppercase text-[#9E9AA7]">CPU</span>
          <span className="text-xs font-bold text-[#F1EFF4]">{cpuLoad}%</span>
        </div>
      </div>

      {/* 4. Network Egress */}
      <div className="hidden sm:flex items-center gap-1.5 px-2 border-r border-[#4B0082]/60 shrink-0">
        <ArrowUpRight className="w-3.5 h-3.5 text-[#10B981]" />
        <div className="flex flex-col">
          <span className="text-[9px] uppercase text-[#9E9AA7]">EGRESS</span>
          <span className="text-xs font-bold text-[#10B981]">{egress} <span className="text-[9px]">KB/s</span></span>
        </div>
      </div>

      {/* 5. Mobile Edge Mesh Link */}
      <div className="shrink-0">
        <MicroPingBadge nodeName="S26-ULTRA" latencyMs={18} status="nominal" />
      </div>

      {/* 6. Client 120Hz FPS */}
      {variant === 'full' && (
        <div className="hidden lg:flex shrink-0 ml-auto">
          <MicroFPSMeter targetFps={120} />
        </div>
      )}
    </div>
  );
};
