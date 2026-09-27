import { Activity, Server } from 'lucide-react';
import { useEffect, useState } from 'react';

export default function RotelMonitor() {
  const [metrics, setMetrics] = useState({ cpu: 12, ram: 44, active_traces: 0 });
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    // Simulate Telemetry Data Stream (until WebSocket is live)
    const interval = setInterval(() => {
      setMetrics((prev) => ({
        cpu: Math.min(100, Math.max(0, prev.cpu + (Math.random() * 10 - 5))),
        ram: Math.min(100, Math.max(0, prev.ram + (Math.random() * 5 - 2.5))),
        active_traces: Math.floor(Math.random() * 50),
      }));

      const newLog = `[ROTEL] TRACE_ID: ${Math.random().toString(36).substring(7)} | LATENCY: ${(Math.random() * 10).toFixed(2)}ms`;
      setLogs((prev) => [newLog, ...prev].slice(0, 10));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-black border border-green-800 rounded-lg p-4 font-mono shadow-lg relative overflow-hidden">
      <div className="absolute top-0 right-0 p-2 opacity-20">
        <Activity size={48} className="text-green-500 animate-pulse" />
      </div>

      <h3 className="text-green-500 font-bold mb-4 flex items-center gap-2 border-b border-green-900 pb-2">
        <Server size={16} /> KINETIC_TELEMETRY [ROTEL]
      </h3>

      <div className="grid grid-cols-3 gap-2 mb-4 text-xs">
        <div className="bg-green-900/20 p-2 rounded border border-green-900/50">
          <div className="text-green-700">CPU LOAD</div>
          <div className="text-xl font-bold text-green-400">{metrics.cpu.toFixed(1)}%</div>
        </div>
        <div className="bg-green-900/20 p-2 rounded border border-green-900/50">
          <div className="text-green-700">RAM USAGE</div>
          <div className="text-xl font-bold text-green-400">{metrics.ram.toFixed(1)}%</div>
        </div>
        <div className="bg-green-900/20 p-2 rounded border border-green-900/50">
          <div className="text-green-700">TRACES</div>
          <div className="text-xl font-bold text-green-400">{metrics.active_traces}</div>
        </div>
      </div>

      <div className="bg-black/50 p-2 rounded border border-green-900/30 h-32 overflow-hidden relative">
        <div className="absolute top-0 right-1 text-[8px] text-green-800">LIVE FEED</div>
        <div className="space-y-1">
          {logs.map((log, i) => (
            <div
              key={i}
              className="text-[10px] text-green-600 truncate opacity-80 hover:opacity-100 transition-opacity"
            >
              {log}
            </div>
          ))}
        </div>
        {/* Scanline overlay */}
        <div className="absolute inset-0 pointer-events-none bg-scanline opacity-10"></div>
      </div>
    </div>
  );
}
