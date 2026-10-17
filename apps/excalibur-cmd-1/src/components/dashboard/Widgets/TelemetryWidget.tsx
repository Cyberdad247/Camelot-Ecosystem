import { useState, useEffect } from 'react';
import { Activity, ShieldCheck, HardDrive } from 'lucide-react';
import { BadgeGlyph } from '../../ui/BadgeGlyph';
import { MetricStat } from '../../ui/MetricStat';

export function TelemetryWidget() {
  const [ramUsageMb, setRamUsageMb] = useState(1480);
  const [nodesActive] = useState(7);
  const cgroupLimit = 4096; // 4GB Strict hardware boundary
  const [cpuLoad, setCpuLoad] = useState(24);

  useEffect(() => {
    const interval = setInterval(() => {
      setRamUsageMb((prev) => {
        const delta = Math.floor(Math.random() * 20) - 10;
        return Math.min(3800, Math.max(1200, prev + delta));
      });
      setCpuLoad(Math.floor(Math.random() * 15) + 18);
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  const ramPercentage = Math.round((ramUsageMb / cgroupLimit) * 100);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between border-b border-[#D4AF37]/30 pb-2">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-[#D4AF37]" />
          <h4 className="font-['Cinzel'] font-bold text-xs sm:text-sm text-[#D4AF37]">
            HARDWARE SCARCITY TELEMETRY
          </h4>
        </div>
        <BadgeGlyph status="ONLINE" label="NOMINAL" size="sm" />
      </div>

      <div className="space-y-2">
        <MetricStat
          label="RAM WORKING SET"
          value={ramUsageMb}
          unit="MB"
          ceiling={cgroupLimit}
          delta={ramPercentage > 50 ? 2 : -1}
          warningThreshold={75}
          criticalThreshold={90}
        />
      </div>

      <div className="grid grid-cols-2 gap-2 pt-1 font-mono text-xs">
        <MetricStat
          label="CPU LOAD"
          value={cpuLoad}
          unit="%"
          ceiling={100}
        />
        <div className="flex flex-col justify-center p-2.5 rounded-lg border border-white/10 bg-[#050510]/60 backdrop-blur-md">
          <span className="text-[10px] text-[#9E9AA7] uppercase">ACTIVE NODES</span>
          <span className="text-base font-bold text-[#9D4EDD] mt-0.5">
            {nodesActive} MicroVMs
          </span>
        </div>
      </div>

      <div className="text-[10px] font-mono text-[#F1EFF4]/70 flex items-center gap-1.5 pt-1">
        <ShieldCheck className="w-3.5 h-3.5 text-[#D4AF37]" />
        <span>CGROUP BOUNDARY ENFORCED: Zero-Docker WASM / Unikernels only</span>
      </div>
    </div>
  );
}
