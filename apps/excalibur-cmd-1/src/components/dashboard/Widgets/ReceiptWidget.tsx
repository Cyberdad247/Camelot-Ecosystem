import { useEcosystemStore } from '../../../state/useEcosystemStore';
import { Receipt, ExternalLink, ShieldCheck } from 'lucide-react';

export function ReceiptWidget() {
  const { receipts } = useEcosystemStore();

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between border-b border-purple-500/30 pb-2">
        <div className="flex items-center gap-2">
          <Receipt className="w-4 h-4 text-[#D4AF37]" />
          <h4 className="font-['Cinzel'] font-bold text-xs sm:text-sm text-[#F1EFF4]">
            SOVEREIGN TRANSACTION RECEIPTS
          </h4>
        </div>
        <span className="text-[10px] font-mono text-[#D4AF37] border border-[#D4AF37]/40 px-2 py-0.5 rounded">
          LEDGER SYNC
        </span>
      </div>

      <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
        {receipts.map((rec) => (
          <div
            key={rec.id}
            className="p-2.5 bg-black/70 border border-[#4B0082]/60 rounded-lg flex items-center justify-between text-xs font-['JetBrains_Mono']"
          >
            <div className="space-y-0.5">
              <div className="text-[#F1EFF4] font-bold font-['Spectral']">{rec.item}</div>
              <div className="text-[10px] text-white/50 flex items-center gap-2">
                <span>{rec.date}</span>
                <span className="text-purple-300">ID: {rec.id}</span>
              </div>
            </div>

            <div className="text-right space-y-0.5">
              <div className="text-[#D4AF37] font-bold">{rec.amount}</div>
              <div className="text-[9px] text-emerald-400 flex items-center gap-1 justify-end">
                <ShieldCheck className="w-3 h-3" />
                <span>{rec.seal}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
