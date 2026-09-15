import { useState } from 'react';
import { useEcosystemStore } from '../../state/useEcosystemStore';
import { CartridgeItem } from './CartridgeItem';
import { ShoppingBag, Sparkles, Check, Search, ShieldCheck } from 'lucide-react';
import { GlassPanel } from '../ui/GlassPanel';

export function Marketplace() {
  const { installedCartridges, activeCartridges, toggleCartridge, installCartridge, addReceipt } = useEcosystemStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [justInstalled, setJustInstalled] = useState<string | null>(null);

  const filtered = installedCartridges.filter(
    (c) =>
      c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleInstall = (id: string) => {
    installCartridge(id);
    const cart = installedCartridges.find((c) => c.id === id);
    if (cart) {
      addReceipt({
        id: `REC-${Math.floor(Math.random() * 900 + 100)}`,
        item: `${cart.name} License`,
        amount: cart.price === 'CORE' ? '$0.00' : cart.price,
        date: new Date().toISOString().split('T')[0],
        seal: 'PROVENANCE-SEALED'
      });
    }
    setJustInstalled(id);
    setTimeout(() => setJustInstalled(null), 2500);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#4B0082] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <ShoppingBag className="w-5 h-5 text-[#D4AF37]" />
            <h2 className="text-xl sm:text-2xl font-['Cinzel'] font-bold text-[#D4AF37]">
              Sovereign Cartridge Marketplace
            </h2>
          </div>
          <p className="text-xs font-['Spectral'] text-[#F1EFF4]/70 mt-1">
            Install curated enterprise cartridges, AI distribution pipelines, and artisan commerce extensions.
          </p>
        </div>

        {/* Search */}
        <div className="relative w-full sm:w-64">
          <Search className="w-4 h-4 text-[#D4AF37] absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search cartridges..."
            className="w-full pl-9 pr-3 py-1.5 bg-black/60 border border-[#4B0082] rounded-lg text-xs font-['Spectral'] text-[#F1EFF4] focus:outline-none focus:border-[#D4AF37]"
          />
        </div>
      </div>

      {justInstalled && (
        <div className="p-3 bg-emerald-950/40 border border-emerald-500 rounded-lg text-xs font-['JetBrains_Mono'] text-emerald-300 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Cartridge installed to Local Edge VFS and cryptographic receipt generated!</span>
          </div>
          <span className="text-[10px] bg-emerald-900/60 px-2 py-0.5 rounded text-emerald-200">SEALED</span>
        </div>
      )}

      {/* Cartridge Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((cartridge) => (
          <CartridgeItem
            key={cartridge.id}
            cartridge={cartridge}
            isActive={activeCartridges.includes(cartridge.id)}
            onToggleActive={(id) => toggleCartridge(id)}
            onInstall={(id) => handleInstall(id)}
          />
        ))}
      </div>
    </div>
  );
}
