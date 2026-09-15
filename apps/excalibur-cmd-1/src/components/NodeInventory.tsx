import { NodeRecord } from '../types';
import { cn } from '../lib/utils';
import { Server, Activity, AlertTriangle, ShieldOff } from 'lucide-react';

export function NodeInventory({
  nodes,
  selectedId,
  onSelect
}: {
  nodes: NodeRecord[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}) {
  return (
    <section className="flex flex-col h-full border border-[#D4AF37]/40 bg-[#050510]/80 rounded-none overflow-hidden shadow-[0_0_20px_rgba(75,0,130,0.3)] relative">
      <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-[#D4AF37]" />
      <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-[#D4AF37]" />
      
      <div className="p-4 border-b border-[#4B0082] bg-[#050510]">
        <h2 className="text-sm font-['Cinzel'] text-[#D4AF37] tracking-[0.1em] uppercase font-bold">Node Inventory</h2>
      </div>
      
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {nodes.map(node => (
          <button
            key={node.id}
            onClick={() => onSelect(node.id)}
            className={cn(
              "w-full text-left p-3 border rounded-none transition-all duration-300 min-h-[44px] relative group overflow-hidden",
              selectedId === node.id 
                ? "border-[#D4AF37] bg-[#D4AF37]/10 shadow-[inset_0_0_15px_rgba(212,175,55,0.1)]" 
                : "border-[#4B0082]/50 hover:border-[#D4AF37]/50 hover:bg-[#4B0082]/20"
            )}
          >
            <div className="flex items-center justify-between mb-2">
              <span className={cn(
                "font-['Cinzel'] font-bold text-sm tracking-wide",
                selectedId === node.id ? "text-[#D4AF37]" : "text-[#F1EFF4]"
              )}>{node.name}</span>
              
              <span className="flex items-center gap-1.5 text-[10px] font-['JetBrains_Mono'] bg-black/50 px-1.5 py-0.5 border border-[#D4AF37]/30 text-[#D4AF37]">
                 <div className="w-1.5 h-1.5 bg-[#D4AF37] animate-pulse drop-shadow-[0_0_5px_#D4AF37]" />
                 [{node.status}]
              </span>
            </div>
            
            <div className="flex items-center justify-between text-[11px] font-['JetBrains_Mono'] text-[#F1EFF4]/70">
              <span>{node.ip}</span>
              <span>L: {node.load}%</span>
            </div>
          </button>
        ))}
        {nodes.length === 0 && (
          <div className="text-center p-4 text-xs font-['JetBrains_Mono'] text-[#F1EFF4]/50">
            Awaiting Merlin_Ω DAG streams...
          </div>
        )}
      </div>
    </section>
  );
}
