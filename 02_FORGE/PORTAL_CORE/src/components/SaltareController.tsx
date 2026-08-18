import { Cpu, Globe, Shield } from 'lucide-react';
import { useState } from 'react';

export default function SaltareController() {
  const [executing, setExecuting] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<string | null>(null);

  const executeTool = async (tool: string, _args: any) => {
    setExecuting(tool);
    setLastResult(null);

    // Route through Morgana -> Saltare
    try {
      const res = await fetch('http://localhost:8001/agent/dispatch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          intent: `execute ${tool}`, // Simple keyword intent for now, or explicit protocol if Morgana supports it
          // Ideally we'd send structured command, but Morgana parses intent.
          // Let's use the keywords we added to Morgana Router: "audit" -> TRIVY, "fix" -> BIOME, "rustdesk" -> REMOTE
        }),
      });
      const data = await res.json();
      setLastResult(data.response);
    } catch (err) {
      setLastResult('EXECUTION_FAILED: ' + String(err));
    } finally {
      setExecuting(null);
    }
  };

  return (
    <div className="bg-black border border-green-800 rounded-lg p-4 font-mono shadow-lg h-full flex flex-col">
      <h3 className="text-green-500 font-bold mb-4 flex items-center gap-2 border-b border-green-900 pb-2">
        <Cpu size={16} /> SALTARE_GATEWAY [COMMAND]
      </h3>

      <div className="grid grid-cols-2 gap-3 mb-4 flex-1">
        <button
          onClick={() => executeTool('trivy', {})}
          disabled={!!executing}
          className="p-3 bg-green-900/20 border border-green-900/50 rounded hover:bg-green-900/40 transition-all flex flex-col items-center justify-center gap-2 group disabled:opacity-50"
        >
          <Shield size={20} className="text-green-400 group-hover:text-green-300" />
          <span className="text-xs text-green-500">KINETIC AUDIT</span>
          <span className="text-[8px] text-green-700">TRIVY SCAN</span>
        </button>

        <button
          onClick={() => executeTool('rustdesk', {})}
          disabled={!!executing}
          className="p-3 bg-blue-900/20 border border-blue-900/50 rounded hover:bg-blue-900/40 transition-all flex flex-col items-center justify-center gap-2 group disabled:opacity-50"
        >
          <Globe size={20} className="text-blue-400 group-hover:text-blue-300" />
          <span className="text-xs text-blue-500">REMOTE LINK</span>
          <span className="text-[8px] text-blue-700">RUSTDESK</span>
        </button>
      </div>

      <div className="bg-black/80 rounded border border-green-900/30 p-2 h-24 overflow-y-auto text-[10px] font-mono">
        {executing && <div className="text-yellow-500 animate-pulse">Running {executing}...</div>}
        {lastResult && <div className="whitespace-pre-wrap text-green-400">{lastResult}</div>}
        {!executing && !lastResult && (
          <div className="text-green-900 italic">Ready for command inputs...</div>
        )}
      </div>
    </div>
  );
}
