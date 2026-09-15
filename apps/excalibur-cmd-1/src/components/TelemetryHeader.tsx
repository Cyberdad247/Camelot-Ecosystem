import { Shield, Clock, Activity, Cpu, HardDrive } from 'lucide-react';
import { useEffect, useState } from 'react';
import { TelemetryData } from '../types';

export function TelemetryHeader({ telemetry }: { telemetry: TelemetryData | null }) {
  const [time, setTime] = useState(new Date().toLocaleTimeString());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date().toLocaleTimeString()), 1000);
    return () => clearInterval(timer);
  }, []);

  const ramUsageGB = telemetry ? (telemetry.ramUsageMB / 1024).toFixed(2) : '1.14';
  const ramPercent = telemetry ? telemetry.ramPercent : 28.5;
  const isHighRam = ramPercent > 75;

  return (
    <header className="h-16 border-b border-[#D4AF37] bg-[#050510]/90 backdrop-blur-md sticky top-0 z-50 flex items-center justify-between px-3 sm:px-6 relative shadow-[0_4px_20px_rgba(75,0,130,0.4)]">
      {/* Angular corner clip-path decoration */}
      <div className="absolute bottom-0 left-0 w-8 h-1 bg-[#D4AF37]" />
      <div className="absolute bottom-0 right-0 w-8 h-1 bg-[#D4AF37]" />

      <div className="flex items-center gap-2 sm:gap-6">
        <div className="flex items-center gap-2">
          <Shield className="w-6 h-6 text-[#D4AF37] drop-shadow-[0_0_8px_rgba(212,175,55,0.5)]" />
          <div className="flex flex-col">
            <span className="text-[#D4AF37] font-['Cinzel'] font-black tracking-[0.2em] text-sm sm:text-lg leading-tight">
              MR. WEALTH
            </span>
            <span className="text-[#F1EFF4] font-['Cinzel'] tracking-[0.3em] text-[10px] opacity-80 leading-tight">
              VIZION SKY
            </span>
          </div>
        </div>
        <div className="h-6 w-px bg-[#4B0082]" />
        <span className="text-[10px] sm:text-[11px] text-[#D4AF37] font-['JetBrains_Mono'] border border-[#D4AF37]/50 px-2 py-0.5 rounded-none uppercase flex items-center gap-2 shadow-[0_0_10px_rgba(212,175,55,0.2)] bg-[#D4AF37]/10 font-bold">
          <div className="w-2 h-2 bg-[#D4AF37] animate-pulse drop-shadow-[0_0_5px_#D4AF37]" />
          CONVERGED
        </span>

        {/* 4GB Strict Boundary Pill */}
        <span className="hidden sm:inline-flex items-center gap-1.5 text-[10px] font-['JetBrains_Mono'] border border-[#4B0082] px-2 py-0.5 bg-black/60 text-[#F1EFF4]/80">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
          4GB RAM STRICT
        </span>
      </div>

      <div className="flex items-center gap-4 sm:gap-6 text-xs font-['JetBrains_Mono'] text-[#F1EFF4]/80">
        {/* RAM Telemetry Gauge */}
        <div className="flex items-center gap-2 border border-[#4B0082]/60 px-2.5 py-1 bg-black/40">
          <HardDrive className={`w-3.5 h-3.5 ${isHighRam ? 'text-amber-400 animate-pulse' : 'text-[#D4AF37]'}`} />
          <div className="flex flex-col">
            <div className="flex items-center gap-1.5 text-[11px]">
              <span className="text-[#D4AF37] font-bold">RAM:</span>
              <span className={isHighRam ? 'text-amber-300 font-bold' : 'text-[#F1EFF4]'}>
                {ramUsageGB}GB / 4.0GB
              </span>
              <span className="text-[10px] opacity-70">({ramPercent}%)</span>
            </div>
            {/* Miniature progress meter */}
            <div className="w-24 sm:w-28 h-1 bg-white/10 mt-0.5 overflow-hidden">
              <div
                className={`h-full transition-all duration-500 ${isHighRam ? 'bg-amber-400' : 'bg-[#D4AF37]'}`}
                style={{ width: `${Math.min(100, ramPercent)}%` }}
              />
            </div>
          </div>
        </div>

        {telemetry && (
          <div className="hidden lg:flex items-center gap-4">
            <div className="flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-[#D4AF37]" />
              LOAD: {telemetry.globalLoad.toFixed(1)}%
            </div>
            <div className="flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-[#D4AF37]" />
              LEASES: {telemetry.activeLeases}
            </div>
          </div>
        )}

        <div className="flex items-center gap-1.5 text-[#F1EFF4] text-xs opacity-90">
          <Clock className="w-3.5 h-3.5 text-[#D4AF37]" />
          {time}
        </div>
      </div>
    </header>
  );
}
