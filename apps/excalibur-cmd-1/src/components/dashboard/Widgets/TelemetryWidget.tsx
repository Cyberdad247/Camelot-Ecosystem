import { useState, useEffect } from 'react';
import { Cpu, Activity, ShieldCheck, Zap, Server } from 'lucide-react';

export function TelemetryWidget() {
  const [ramUsageMb, setRamUsageMb] = useState(1480);
  const [nodesActive, setNodesActive] = useState(7);
  const [cgroupLimit] = useState(4096); // 4GB Strict hardware boundary
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
        <span className="text-[10px] font-mono px-2 py-0.5 border border-emerald-500/50 text-emerald-400 bg-emerald-950/30 rounded">
          NOMINAL
        </span>
      </div>

      <div className="space-y-2">
        <div className="flex justify-between text-xs font-['JetBrains_Mono']">
          <span className="text-[#F1EFF4]/70 flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-[#D4AF37]" />
            RAM (4GB HARD CEILING)
          </span>
          <span className="font-bold text-[#D4AF37]">
            {ramUsageMb} MB / {cgroupLimit} MB ({ramPercentage}%)
          </span>
        </div>

        {/* Progress bar */}
        <div className="w-full bg-black/80 h-2.5 rounded-full overflow-hidden border border-[#4B0082]/60 p-[1px]">
          <div
            className="h-full bg-gradient-to-r from-emerald-500 via-[#D4AF37] to-amber-500 rounded-full transition-all duration-500"
            style={{ width: `${ramPercentage}%` }}
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2 pt-2 text-[11px] font-['JetBrains_Mono']">
        <div className="p-2 bg-black/60 border border-white/5 rounded flex items-center justify-between">
          <span className="text-white/50">CPU LOAD:</span>
          <span className="text-emerald-400 font-bold">{cpuLoad}%</span>
        </div>
        <div className="p-2 bg-black/60 border border-white/5 rounded flex items-center justify-between">
          <span className="text-white/50">ACTIVE NODES:</span>
          <span className="text-purple-300 font-bold">{nodesActive} MicroVMs</span>
        </div>
      </div>

      <div className="text-[10px] font-['JetBrains_Mono'] text-[#F1EFF4]/60 flex items-center gap-1.5 pt-1">
        <ShieldCheck className="w-3 h-3 text-[#D4AF37]" />
        <span>CGROUP BOUNDARY ENFORCED: Zero-Docker WASM / Unikernels only</span>
      </div>
    </div>
  );
}
