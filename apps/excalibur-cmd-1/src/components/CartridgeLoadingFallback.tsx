import { Cpu, Shield, Loader2 } from 'lucide-react';

interface Props {
  cartridgeName?: string;
}

export function CartridgeLoadingFallback({ cartridgeName = 'SOVEREIGN CARTRIDGE' }: Props) {
  return (
    <div className="h-full w-full flex items-center justify-center p-6 bg-[#050510]">
      <div className="max-w-md w-full border border-[#D4AF37]/50 bg-black/80 p-6 shadow-[0_0_30px_rgba(75,0,130,0.5)] relative">
        {/* Angular corner accents */}
        <div className="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-[#D4AF37]" />
        <div className="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-[#D4AF37]" />
        <div className="absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 border-[#D4AF37]" />
        <div className="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-[#D4AF37]" />

        <div className="flex flex-col items-center text-center space-y-4">
          <div className="relative">
            <div className="w-14 h-14 border border-[#4B0082] rounded-full flex items-center justify-center bg-[#4B0082]/20">
              <Shield className="w-7 h-7 text-[#D4AF37] animate-pulse" />
            </div>
            <Loader2 className="w-16 h-16 text-[#D4AF37] animate-spin absolute -top-1 -left-1 opacity-60" />
          </div>

          <div className="space-y-1">
            <span className="text-[10px] font-['JetBrains_Mono'] text-[#D4AF37] tracking-widest uppercase block">
              DYNAMIC CODE SPLIT // ON-DEMAND HYDRATION
            </span>
            <h3 className="text-base font-['Cinzel'] font-bold text-[#F1EFF4]">
              MOUNTING {cartridgeName.toUpperCase()}
            </h3>
            <p className="text-xs font-['Spectral'] text-[#F1EFF4]/70">
              Streaming WASM/JS binary chunk into isolated VFS memory slab...
            </p>
          </div>

          {/* Memory budget status badge */}
          <div className="w-full border border-[#4B0082] bg-black/60 p-2.5 flex items-center justify-between text-[10px] font-['JetBrains_Mono'] text-[#F1EFF4]/80">
            <div className="flex items-center gap-1.5 text-emerald-400">
              <Cpu className="w-3.5 h-3.5" />
              <span>4GB RAM CEILING ENFORCED</span>
            </div>
            <span className="text-[#D4AF37]">MADV_DONTNEED</span>
          </div>

          {/* Dynamic loading bar */}
          <div className="w-full h-1 bg-white/10 overflow-hidden">
            <div className="h-full bg-gradient-to-r from-[#4B0082] via-[#D4AF37] to-[#4B0082] w-full animate-pulse" />
          </div>
        </div>
      </div>
    </div>
  );
}
