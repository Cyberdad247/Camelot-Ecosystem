import React, { useState } from 'react';
import { ShieldCheck, ShieldAlert, Skull, Zap } from 'lucide-react';

interface NodeState {
  id: string;
  role: string;
  trustBand: 'healthy' | 'observed' | 'suspect' | 'soft_quarantine' | 'hard_quarantine' | 'ragnarok';
  cryptoStatus: 'ML-KEM-768-LOCKED';
}

export const HeimdallSecurityGrid: React.FC = () => {
  const [nodes, setNodes] = useState<NodeState[]>([
    { id: "NODE_EXEC_ANDRE", role: "EXECUTIVE", trustBand: "healthy", cryptoStatus: "ML-KEM-768-LOCKED" },
    { id: "NODE_STAFF_001", role: "STAFF", trustBand: "observed", cryptoStatus: "ML-KEM-768-LOCKED" },
    { id: "NODE_STAFF_004", role: "STAFF", trustBand: "suspect", cryptoStatus: "ML-KEM-768-LOCKED" }
  ]);

  const executeRagnarok = (nodeId: string) => {
    console.warn(`[HEIMDALL]: ⚡ CRITICAL QUEUE BYPASS INITIATED. SIGNATURE VERIFIED.`);
    console.error(`[RAGNAROK]: ISOLATING NODE ${nodeId}. ALL SESSIONS REVOKED.`);
    setNodes(prev => prev.map(n => n.id === nodeId ? { ...n, trustBand: 'ragnarok' } : n));
  };

  const getStatusColor = (state: string) => {
    switch(state) {
      case 'healthy': return 'text-green-400 border-green-900';
      case 'observed': return 'text-blue-400 border-blue-900';
      case 'suspect': return 'text-yellow-400 border-yellow-900';
      case 'soft_quarantine': return 'text-orange-500 border-orange-900';
      case 'hard_quarantine': return 'text-red-500 border-red-900';
      case 'ragnarok': return 'text-red-700 border-red-900 bg-[#1A0505]';
      default: return 'text-gray-400';
    }
  };

  return (
    <div className="bg-[#050507] min-h-screen p-8 font-mono text-white">
      <header className="mb-8 flex justify-between border-b border-[#D4AF37] pb-4">
        <h2 className="text-[#D4AF37] text-2xl tracking-widest flex items-center gap-3 font-bold">
          <ShieldAlert /> PHASE J: HEIMDALL AEGIS
        </h2>
        <div className="text-xs text-[#9D4EDD] uppercase animate-pulse flex items-center gap-2">
          <Zap size={14} /> POST-QUANTUM MESH ACTIVE
        </div>
      </header>

      <div className="grid grid-cols-3 gap-6">
        {nodes.map(node => (
          <div key={node.id} className={`border p-4 transition-all ${getStatusColor(node.trustBand)}`}>
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="font-bold text-sm tracking-wide">{node.id}</h3>
                <span className="text-[10px] uppercase opacity-70">{node.role}</span>
              </div>
              {node.trustBand === 'healthy' ? <ShieldCheck size={20} className="text-green-400" /> : 
               node.trustBand === 'ragnarok' ? <Skull size={20} className="text-red-700" /> : 
               <ShieldAlert size={20} />}
            </div>
            
            <div className="text-[10px] mb-4">
              <div>STATUS: {node.trustBand.toUpperCase()}</div>
              <div>CRYPTO: {node.cryptoStatus}</div>
            </div>

            {node.trustBand !== 'ragnarok' && (
              <button 
                onClick={() => executeRagnarok(node.id)}
                className="w-full py-2 bg-red-900/20 hover:bg-red-900/60 text-red-400 text-xs border border-red-900 transition-colors uppercase tracking-widest"
              >
                Execute Ragnarok
              </button>
            )}
            {node.trustBand === 'ragnarok' && (
              <div className="w-full py-2 bg-[#1A0505] text-red-900 text-xs text-center border border-red-900 uppercase tracking-widest font-bold">
                ISOLATING SEQUENCE COMPLETE
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
