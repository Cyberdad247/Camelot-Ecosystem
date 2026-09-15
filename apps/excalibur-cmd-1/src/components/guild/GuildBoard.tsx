import { useState } from 'react';
import { useEcosystemStore } from '../../state/useEcosystemStore';
import { GlassPanel } from '../ui/GlassPanel';
import { Scroll, Award, Clock, ArrowRight, ShieldCheck, CheckCircle2 } from 'lucide-react';

export function GuildBoard() {
  const { activeContracts, claimContract } = useEcosystemStore();
  const [claimedNotice, setClaimedNotice] = useState<string | null>(null);

  const handleClaim = (id: string) => {
    claimContract(id);
    setClaimedNotice(id);
    setTimeout(() => setClaimedNotice(null), 3000);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#4B0082] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <Scroll className="w-5 h-5 text-[#D4AF37]" />
            <h2 className="text-xl sm:text-2xl font-['Cinzel'] font-bold text-[#D4AF37]">
              Round Table Guild Board
            </h2>
          </div>
          <p className="text-xs font-['Spectral'] text-[#F1EFF4]/70 mt-1">
            Mercenary contracts, neurosymbolic verification bounties, and autonomous task DAGs.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[10px] font-['JetBrains_Mono'] px-2.5 py-1 border border-[#D4AF37] bg-black/60 text-[#D4AF37] rounded">
            TOTAL ESCROW: 12,550 USDC
          </span>
        </div>
      </div>

      {claimedNotice && (
        <div className="p-3 bg-purple-950/50 border border-purple-400 rounded-lg text-xs font-['JetBrains_Mono'] text-purple-200 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-[#D4AF37]" />
            <span>Contract {claimedNotice} bound to sovereign execution DAG. Sir Boris & Sir Codex dispatched.</span>
          </div>
          <span className="text-[10px] bg-purple-900/60 px-2 py-0.5 rounded">IN KINETIC QUEUE</span>
        </div>
      )}

      {/* Contracts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {activeContracts.map((contract) => (
          <GlassPanel
            key={contract.id}
            glow={contract.status === 'CLAIMED' ? 'purple' : 'gold'}
            className="flex flex-col justify-between"
          >
            <div className="space-y-3">
              <div className="flex items-start justify-between gap-2">
                <span className="text-[10px] font-['JetBrains_Mono'] px-2 py-0.5 border border-[#4B0082] bg-black/60 text-purple-300 rounded font-bold">
                  {contract.id}
                </span>
                <span className="text-sm font-['JetBrains_Mono'] font-bold text-[#D4AF37] bg-black/80 px-2 py-0.5 border border-[#D4AF37]/50 rounded">
                  {contract.payout}
                </span>
              </div>

              <h3 className="font-['Cinzel'] font-bold text-sm sm:text-base text-[#F1EFF4] leading-snug">
                {contract.title}
              </h3>

              <div className="flex items-center justify-between text-[11px] font-['JetBrains_Mono'] text-[#F1EFF4]/60 pt-1">
                <span className="text-[#D4AF37]">{contract.sponsor}</span>
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3 text-[#D4AF37]" />
                  {contract.timeEstimate}
                </span>
              </div>

              {/* DAG steps */}
              <div className="pt-2 border-t border-white/5 space-y-1.5">
                <span className="text-[9px] font-['JetBrains_Mono'] text-white/40 uppercase block">
                  TASK DAG BREAKDOWN
                </span>
                {contract.dagSteps.map((step, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-xs font-['Spectral'] text-[#F1EFF4]/80">
                    <span className="w-4 h-4 rounded-full bg-[#4B0082]/60 text-[9px] font-mono flex items-center justify-center text-[#D4AF37]">
                      {idx + 1}
                    </span>
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-5 pt-3 border-t border-white/5">
              {contract.status === 'CLAIMED' ? (
                <div className="w-full py-2 bg-purple-950/80 border border-purple-500/80 text-purple-200 text-xs font-['Cinzel'] font-bold rounded flex items-center justify-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  <span>CONTRACT CLAIMED & RUNNING</span>
                </div>
              ) : (
                <button
                  type="button"
                  onClick={() => handleClaim(contract.id)}
                  className="w-full py-2.5 bg-[#D4AF37] hover:bg-[#F1EFF4] text-black text-xs font-['Cinzel'] font-bold rounded tracking-wider transition-all shadow-[0_0_15px_rgba(212,175,55,0.3)] flex items-center justify-center gap-2"
                >
                  <Award className="w-3.5 h-3.5" />
                  <span>CLAIM CONTRACT & FORGE DAG</span>
                </button>
              )}
            </div>
          </GlassPanel>
        ))}
      </div>
    </div>
  );
}
