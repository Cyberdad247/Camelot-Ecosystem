import React, { useState, useEffect } from 'react';
import { Activity, Server } from 'lucide-react';
import { runtimeConfig, tokenizedUrl } from '@/config/runtime';

const ROTEL_STREAM_URL = tokenizedUrl(runtimeConfig.rotel.streamUrl, runtimeConfig.rotel.token);

interface LogEntry {
  level: string;
  message: string;
  component: string;
  timestamp?: string;
  metadata?: any;
}

export default function RotelMonitor() {
  const [metrics, setMetrics] = useState({ cpu: 12, ram: 44, active_traces: 0 });
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [status, setStatus] = useState('CONNECTING');

  useEffect(() => {
    const eventSource = new EventSource(ROTEL_STREAM_URL);

    eventSource.onopen = () => {
      setStatus('RADIANT');
      console.log('📡 [ROTEL] Connection Established.');
    };

    eventSource.onmessage = (event) => {
      try {
        const log: LogEntry = JSON.parse(event.data);
        setLogs((prev) => [log, ...prev].slice(0, 15));

        setMetrics((prev) => ({
          ...prev,
          active_traces: prev.active_traces + 1,
        }));
      } catch (e) {
        // Ignore ping
      }
    };

    eventSource.onerror = () => {
      setStatus('OFFLINE');
    };

    return () => {
      eventSource.close();
    };
  }, []);

  return (
    <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-4 font-mono shadow-lg relative overflow-hidden">
      <div className="absolute top-0 right-0 p-2 opacity-10">
        <Activity
          size={48}
          className={`text-emerald-500 ${status === 'RADIANT' ? 'animate-pulse' : ''}`}
        />
      </div>

      <h3 className="text-emerald-500 text-[10px] font-bold mb-4 flex items-center gap-2 border-b border-emerald-900/30 pb-2 uppercase tracking-widest">
        <Server size={12} /> KINETIC_TELEMETRY [ROTEL]
        <span
          className={`ml-auto text-[7px] px-1.5 py-0.5 rounded border ${status === 'RADIANT' ? 'border-emerald-500 text-emerald-500' : 'border-red-500 text-red-500'}`}
        >
          {status}
        </span>
      </h3>

      <div className="grid grid-cols-3 gap-2 mb-4 text-[9px]">
        <div className="bg-emerald-900/10 p-2 rounded-xl border border-emerald-900/20">
          <div className="text-emerald-700 mb-1 uppercase tracking-tighter">CPU LOAD</div>
          <div className="text-lg font-bold text-emerald-400">{metrics.cpu.toFixed(1)}%</div>
        </div>
        <div className="bg-emerald-900/10 p-2 rounded-xl border border-emerald-900/20">
          <div className="text-emerald-700 mb-1 uppercase tracking-tighter">RAM USAGE</div>
          <div className="text-lg font-bold text-emerald-400">{metrics.ram.toFixed(1)}%</div>
        </div>
        <div className="bg-emerald-900/10 p-2 rounded-xl border border-emerald-900/20">
          <div className="text-emerald-700 mb-1 uppercase tracking-tighter">SIGNALS</div>
          <div className="text-lg font-bold text-emerald-400">{metrics.active_traces}</div>
        </div>
      </div>

      <div className="bg-black/40 p-2 rounded-xl border border-emerald-900/10 h-32 overflow-hidden relative">
        <div className="absolute top-0 right-2 text-[7px] text-emerald-900 uppercase tracking-tighter">
          LIVE KINETIC FEED
        </div>
        <div className="space-y-1">
          {logs.map((log, i) => (
            <div key={i} className="text-[9px] text-emerald-600/80 truncate font-mono flex gap-2">
              <span className="text-emerald-900 font-bold shrink-0">
                [{log.component.toUpperCase()}]
              </span>
              <span
                className={
                  log.level === 'ERROR'
                    ? 'text-red-500'
                    : log.level === 'WARN'
                      ? 'text-yellow-500'
                      : ''
                }
              >
                {log.message}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
