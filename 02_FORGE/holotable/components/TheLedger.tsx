'use client';

import { useEffect, useState, useRef } from 'react';
import { api } from '@/lib/api';
import { Terminal, AlertTriangle, CheckCircle } from 'lucide-react';

export default function TheLedger() {
  const [lines, setLines] = useState<string[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const interval = setInterval(async () => {
      const data = await api.getLedger(50); // Get last 50 lines
      if (data.lines) setLines(data.lines);
    }, 2000); // Fast poll for live feel
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // Auto-scroll to bottom
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [lines]);

  const getLinestyle = (line: string) => {
    if (line.includes('ERROR') || line.includes('FATAL') || line.includes('CAUSALITY BREACH'))
      return 'text-red-500 font-bold';
    if (line.includes('WARN') || line.includes('Omega_CONFIRM')) return 'text-yellow-500';
    if (line.includes('SUCCESS') || line.includes('RADIANT')) return 'text-green-500';
    if (line.includes('Omega_')) return 'text-purple-400'; // Oracle Command
    return 'text-slate-400';
  };

  return (
    <div className="glass-panel p-4 rounded-xl h-full flex flex-col">
      <h2 className="text-xl font-mono font-bold text-accent mb-2 flex items-center gap-2">
        <Terminal className="w-5 h-5" /> PROVENANCE LEDGER
      </h2>

      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto font-mono text-xs space-y-1 pr-2 max-h-[300px] scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent"
      >
        {lines.map((line, i) => (
          <div key={i} className={`break-all ${getLinestyle(line)}`}>
            {line}
          </div>
        ))}
        {lines.length === 0 && <div className="text-slate-600">Initializing Uplink...</div>}
      </div>
    </div>
  );
}
