import { NodeRecord } from '../types';
import { Plus, Minus, CheckCircle } from 'lucide-react';
import { useState } from 'react';

export function SovereignActions({ 
  node, 
  onAction 
}: { 
  node: NodeRecord | null,
  onAction: (id: string, action: string) => Promise<void>
}) {
  const [loadingAction, setLoadingAction] = useState<string | null>(null);

  if (!node) {
    return (
      <section className="flex flex-col h-full border border-[#D4AF37]/30 bg-[#050510]/50 rounded-none p-4 relative">
         <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-[#D4AF37]/50" />
         <h2 className="text-sm font-['Cinzel'] text-[#D4AF37] uppercase opacity-50 font-bold">Sovereign Directives</h2>
         <div className="flex-1 flex items-center justify-center text-xs font-['JetBrains_Mono'] text-[#F1EFF4]/30 tracking-widest">
           AWAITING NODE SELECTION
         </div>
      </section>
    );
  }

  const handleAction = async (action: string) => {
    setLoadingAction(action);
    await onAction(node.id, action);
    setLoadingAction(null);
  };

  return (
    <section className="flex flex-col h-full border border-[#D4AF37]/60 bg-[#050510] rounded-none overflow-hidden shadow-[0_0_20px_rgba(75,0,130,0.4)] relative">
      <div className="absolute top-0 right-0 w-6 h-6 border-t-2 border-r-2 border-[#D4AF37]" />
      <div className="absolute bottom-0 left-0 w-6 h-6 border-b-2 border-l-2 border-[#D4AF37]" />

      <div className="p-4 border-b border-[#4B0082]">
        <h2 className="text-sm font-['Cinzel'] text-[#D4AF37] tracking-[0.1em] uppercase font-bold flex flex-col gap-1">
          SOVEREIGN DIRECTIVES
          <span className="text-[10px] text-[#F1EFF4]/60 font-['JetBrains_Mono'] tracking-normal">Target: {node.name}</span>
        </h2>
      </div>
      
      <div className="flex-1 p-5 flex flex-col gap-4 justify-center">
        <button 
          onClick={() => handleAction('insert')}
          disabled={loadingAction !== null}
          className="min-h-[44px] flex items-center justify-center gap-3 w-full py-3 rounded-none bg-[#D4AF37]/10 text-[#D4AF37] border border-[#D4AF37] hover:bg-[#D4AF37]/20 transition-all disabled:opacity-50 hover:shadow-[0_0_15px_rgba(212,175,55,0.4)] group"
        >
          <Plus className="w-5 h-5 group-hover:scale-110 transition-transform" />
          <span className="font-['Cinzel'] font-bold text-sm tracking-[0.2em] uppercase">Insert Node</span>
        </button>

        <button 
          onClick={() => handleAction('eject')}
          disabled={loadingAction !== null}
          className="min-h-[44px] flex items-center justify-center gap-3 w-full py-3 rounded-none bg-red-900/20 text-red-400 border border-red-900 hover:bg-red-900/40 hover:border-red-500 transition-all disabled:opacity-50"
        >
          <Minus className="w-5 h-5" />
          <span className="font-['Cinzel'] font-bold text-sm tracking-[0.2em] uppercase">Eject Node</span>
        </button>
        
        <button 
          onClick={() => handleAction('approve')}
          disabled={loadingAction !== null}
          className="min-h-[44px] flex items-center justify-center gap-3 w-full py-3 rounded-none bg-[#4B0082]/20 text-[#F1EFF4] border border-[#4B0082] hover:bg-[#4B0082]/40 hover:border-[#D4AF37]/50 transition-all disabled:opacity-50"
        >
          <CheckCircle className="w-5 h-5" />
          <span className="font-['Cinzel'] font-bold text-sm tracking-[0.2em] uppercase">Approve</span>
        </button>

        <div className="mt-auto bg-black/60 border border-[#D4AF37]/30 p-3 text-[11px] font-['JetBrains_Mono'] text-[#F1EFF4]/70 leading-relaxed backdrop-blur-sm shadow-inner">
          <div className="flex justify-between"><span>ID:</span> <span className="text-[#D4AF37]">{node.id}</span></div>
          <div className="flex justify-between"><span>STATUS:</span> <span className="text-[#D4AF37]">{node.status}</span></div>
          <div className="flex justify-between"><span>COORDS:</span> <span className="text-[#D4AF37]">{node.coordinates ? `X:${node.coordinates.x} Y:${node.coordinates.y}` : 'N/A'}</span></div>
        </div>
      </div>
    </section>
  );
}
