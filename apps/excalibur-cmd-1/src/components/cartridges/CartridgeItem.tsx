import { CartridgeMetadata, useEcosystemStore } from '../../state/useEcosystemStore';
import { GlassPanel } from '../ui/GlassPanel';
import { Cpu, Power, Check, Download, Layers } from 'lucide-react';

interface Props {
  cartridge: CartridgeMetadata;
  isActive: boolean;
  onToggleActive: (id: string) => void;
  onInstall?: (id: string) => void;
}

export function CartridgeItem({ cartridge, isActive, onToggleActive, onInstall }: Props) {
  const isInstalled = cartridge.status === 'installed';

  return (
    <GlassPanel
      glow={isActive ? 'gold' : isInstalled ? 'purple' : 'none'}
      className={`transition-all duration-300 flex flex-col justify-between ${
        isActive ? 'border-[#D4AF37] ring-1 ring-[#D4AF37]/40' : ''
      }`}
    >
      <div className="space-y-3">
        <div className="flex items-start justify-between gap-2">
          <div>
            <span className="text-[9px] font-['JetBrains_Mono'] px-2 py-0.5 rounded uppercase font-bold border border-[#4B0082] bg-black/60 text-[#D4AF37]">
              {cartridge.category}
            </span>
            <h3 className="font-['Cinzel'] font-bold text-sm sm:text-base text-[#F1EFF4] mt-1.5">
              {cartridge.name}
            </h3>
          </div>

          <span className="text-xs font-['JetBrains_Mono'] font-bold text-[#D4AF37] bg-black/70 px-2 py-1 border border-[#D4AF37]/40 rounded">
            {cartridge.price}
          </span>
        </div>

        <p className="text-xs font-['Spectral'] text-[#F1EFF4]/80 leading-relaxed line-clamp-2">
          {cartridge.description}
        </p>

        <div className="flex items-center justify-between text-[10px] font-['JetBrains_Mono'] text-[#F1EFF4]/60 pt-2 border-t border-white/5">
          <div className="flex items-center gap-1 text-emerald-400">
            <Cpu className="w-3 h-3" />
            <span>RAM: {cartridge.ramFootprint}</span>
          </div>
          <span className="text-purple-300">{cartridge.version}</span>
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-white/5">
        {isInstalled ? (
          <button
            type="button"
            onClick={() => onToggleActive(cartridge.id)}
            className={`w-full py-2 px-3 rounded text-xs font-['Cinzel'] font-bold tracking-wider transition-all flex items-center justify-center gap-2 ${
              isActive
                ? 'bg-[#D4AF37] text-black shadow-[0_0_15px_rgba(212,175,55,0.4)]'
                : 'bg-black/60 border border-[#4B0082] text-[#F1EFF4]/80 hover:border-[#D4AF37] hover:text-[#D4AF37]'
            }`}
          >
            <Power className="w-3.5 h-3.5" />
            <span>{isActive ? 'MOUNTED IN MEMORY (ACTIVE)' : 'HOTSWAP MOUNT'}</span>
          </button>
        ) : (
          <button
            type="button"
            onClick={() => onInstall && onInstall(cartridge.id)}
            className="w-full py-2 px-3 rounded text-xs font-['Cinzel'] font-bold tracking-wider bg-purple-950/60 border border-purple-500 hover:bg-purple-900 text-[#F1EFF4] transition-all flex items-center justify-center gap-2"
          >
            <Download className="w-3.5 h-3.5 text-[#D4AF37]" />
            <span>INSTALL CARTRIDGE</span>
          </button>
        )}
      </div>
    </GlassPanel>
  );
}
