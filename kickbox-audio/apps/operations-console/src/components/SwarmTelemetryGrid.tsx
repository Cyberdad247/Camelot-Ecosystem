import React, { useEffect, useState } from 'react';
import { Activity, Terminal, ShieldAlert } from 'lucide-react';

export const SwarmTelemetryGrid: React.FC = () => {
  const [ledgerLogs, setLedgerLogs] = useState<string[]>([]);
  const [syncLogs, setSyncLogs] = useState<string[]>([]);

  useEffect(() => {
    const handleWasmEvent = (e: any) => {
      if (e.detail.source === 'LEDGER_PILL') {
        setLedgerLogs(prev => [...prev.slice(-10), `[${new Date().toISOString()}] ${e.detail.msg}`]);
      }
      if (e.detail.source === 'CRDT_SYNC_WORKER') {
        setSyncLogs(prev => [...prev.slice(-10), `[${new Date().toISOString()}] ${e.detail.msg}`]);
      }
    };
    window.addEventListener('WASM_TELEMETRY', handleWasmEvent);
    return () => window.removeEventListener('WASM_TELEMETRY', handleWasmEvent);
  }, []);

  return (
    <div className="bg-[#050507] min-h-screen p-6 font-mono text-white">
      <header className="mb-6 flex justify-between border-b border-[#D4AF37] pb-4">
        <h2 className="text-[#D4AF37] text-2xl tracking-widest flex items-center gap-3">
          <Activity /> PHASE H: OMNI-OBSERVABILITY
        </h2>
        <div className="text-xs text-[#9D4EDD] uppercase animate-pulse">
          HERMES_PRIME // MGV LOOP ACTIVE
        </div>
      </header>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="border border-[#333] bg-[#0D0D11] p-4 h-64 overflow-y-auto">
          <h3 className="text-[#D4AF37] text-sm border-b border-[#333] pb-2 mb-2 flex items-center gap-2">
            <Terminal size={14}/> LEDGER_PILL_EXECUTION
          </h3>
          {ledgerLogs.map((log, i) => (
            <div key={i} className="text-[10px] text-green-400 mb-1">{log}</div>
          ))}
          {ledgerLogs.length === 0 && <div className="text-[10px] text-gray-600 italic">Awaiting WASM telemetry...</div>}
        </div>

        <div className="border border-[#333] bg-[#0D0D11] p-4 h-64 overflow-y-auto">
          <h3 className="text-[#9D4EDD] text-sm border-b border-[#333] pb-2 mb-2 flex items-center gap-2">
            <Activity size={14}/> CRDT_SYNC_WORKER
          </h3>
          {syncLogs.map((log, i) => (
            <div key={i} className="text-[10px] text-blue-400 mb-1">{log}</div>
          ))}
          {syncLogs.length === 0 && <div className="text-[10px] text-gray-600 italic">Awaiting sync heartbeat...</div>}
        </div>
        
        <div className="border border-[#333] bg-[#0D0D11] p-4 h-64 overflow-y-auto opacity-50 hover:opacity-100 transition-opacity">
           <h3 className="text-blue-500 text-sm border-b border-[#333] pb-2 mb-2 flex items-center gap-2">
            <ShieldAlert size={14}/> COMMS_PILL_DISPATCH
          </h3>
          <div className="text-[10px] text-gray-600 italic">Standby...</div>
        </div>

        <div className="border border-[#333] bg-[#0D0D11] p-4 h-64 overflow-y-auto opacity-50 hover:opacity-100 transition-opacity">
           <h3 className="text-yellow-500 text-sm border-b border-[#333] pb-2 mb-2 flex items-center gap-2">
            <Terminal size={14}/> SUPPORT_PILL_VECTORS
          </h3>
          <div className="text-[10px] text-gray-600 italic">Standby...</div>
        </div>
      </div>
    </div>
  );
};
