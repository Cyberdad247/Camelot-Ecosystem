import { useEcosystemStore } from '../../state/useEcosystemStore';
import { CartridgeItem } from './CartridgeItem';
import { GlassPanel } from '../ui/GlassPanel';
import { HardDrive, RefreshCw, Cpu, CheckCircle2 } from 'lucide-react';

export function CartridgeVault() {
  const { installedCartridges, activeCartridges, toggleCartridge } = useEcosystemStore();
  const ownedCartridges = installedCartridges.filter((c) => c.status === 'installed');

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#4B0082] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <HardDrive className="w-5 h-5 text-[#D4AF37]" />
            <h2 className="text-xl sm:text-2xl font-['Cinzel'] font-bold text-[#D4AF37]">
              Sovereign Cartridge Vault & Hotswap
            </h2>
          </div>
          <p className="text-xs font-['Spectral'] text-[#F1EFF4]/70 mt-1">
            Zero-Docker microVM memory slabs. Mount or unmount cartridges dynamically to optimize 4GB RAM ceiling.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="px-3 py-1.5 border border-[#4B0082] bg-black/60 rounded text-xs font-['JetBrains_Mono'] text-emerald-400 flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5" />
            <span>ACTIVE: {activeCartridges.length} / {ownedCartridges.length}</span>
          </div>
        </div>
      </div>

      {/* Grid of owned cartridges */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {ownedCartridges.map((cartridge) => (
          <CartridgeItem
            key={cartridge.id}
            cartridge={cartridge}
            isActive={activeCartridges.includes(cartridge.id)}
            onToggleActive={(id) => toggleCartridge(id)}
          />
        ))}
      </div>

      {/* Memory Boundary Telemetry */}
      <GlassPanel glow="gold" density="compact" className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-2 text-xs font-['JetBrains_Mono'] text-[#F1EFF4]/80">
          <CheckCircle2 className="w-4 h-4 text-[#D4AF37]" />
          <span>VFS MicroVM Backplane: MADV_DONTNEED garbage collection enforced upon cartridge unmount.</span>
        </div>
        <span className="text-[10px] font-['JetBrains_Mono'] text-purple-300 font-bold border border-purple-500/40 px-2 py-0.5 rounded">
          CGROUP 4096MB STRICT
        </span>
      </GlassPanel>
    </div>
  );
}
