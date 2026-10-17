import { useEffect } from 'react';
import { Shield, Layers, Building2, Factory, Disc, Lock, Smartphone } from 'lucide-react';
import { CartridgeId, CartridgeMetadata } from '../types';
import { cn } from '../lib/utils';
import { triggerHaptic } from '../lib/haptics';

interface Props {
  activeCartridge: CartridgeId;
  onSelectCartridge: (id: CartridgeId) => void;
  onLockVault: () => void;
  leaseId: string | null;
  operator: string;
}

export const CARTRIDGES: CartridgeMetadata[] = [
  {
    id: 'ecosystem-pwa',
    code: 'PWA SHELL',
    name: 'PWA Ecosystem // S26 Edge',
    tagline: 'S26 Edge Mobile Shell, Vault & Guild',
    type: 'PWA_ECOSYSTEM',
    risk: 'R0',
    status: 'ACTIVE',
    category: 'Ecosystem Shell',
    description: 'Mobile-first Windows-like dashboard, Cartridge Vault hotswap, Marketplace, Guild contracts, and OCEAN customizer.',
    capabilities: ['s26_edge_shell', 'hotswap_vault', 'marketplace', 'guild_board', 'ocean_customizer']
  },
  {
    id: 'excalibur-ecc',
    code: 'CARTRIDGE 00',
    name: 'Excalibur Command Center',
    tagline: 'Digital Throne Room & Node Telemetry',
    type: 'CONTROL_PLANE',
    risk: 'R5',
    status: 'ACTIVE',
    category: 'Sovereign Core',
    description: 'Converged Node Inventory, Holographic Globe 2D, Alfred Audio Engine, and Sovereign Directives.',
    capabilities: ['telemetry_stream', 'node_registry', 'alfred_wasm', 'sovereign_dag']
  },
  {
    id: 'kba-executive',
    code: 'CARTRIDGE 01',
    name: 'KBA Executive',
    tagline: 'Knowledge Base & Sovereign Governance',
    type: 'STRATEGIC_OS',
    risk: 'R4',
    status: 'UNLOCKED',
    category: 'Governance',
    description: 'Executive Strategy, S-Corp Operating Directives, Cuyahoga County jurisdiction compliance, and GraphRAG knowledge base.',
    capabilities: ['graphrag_mempalace', 'z3_prover', 'governance_ledger', 'sovereign_runes']
  },
  {
    id: 'digital-factory',
    code: 'CARTRIDGE 02',
    name: 'Digital Factory',
    tagline: 'Invisioned Marketing & Head Artworks',
    type: 'REVENUE_ENGINE',
    risk: 'R3',
    status: 'UNLOCKED',
    category: 'Commercial Engines',
    description: 'The Midas Loop inbound lead engine, Firecrawl data pipelines, and Head Artworks physical artisan e-commerce matrix.',
    capabilities: ['midas_loop', 'firecrawl_scraper', 'artisan_listings', 's_corp_operations']
  },
  {
    id: '1vizion-rcrds',
    code: 'CARTRIDGE 03',
    name: '1VIZION RCRDS',
    tagline: 'Audio Physics & Distribution Matrix',
    type: 'DISTRIBUTION_PIPELINE',
    risk: 'R3',
    status: 'UNLOCKED',
    category: 'Audio & Media',
    description: 'Automated UPC/ISRC binding, 3000x3000px artwork verification, Records Unchained 71228 sealing, and AI audio synthesis.',
    capabilities: ['isrc_upc_binding', 'artwork_verification_3000px', 'records_unchained_71228', 'dsp_audio_physics']
  }
];

export function TenantCarousel({
  activeCartridge,
  onSelectCartridge,
  onLockVault,
  leaseId,
  operator
}: Props) {
  // Global Hotkeys: Number keys 1-5 switch cartridges
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger if user is typing in an input
      if (['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement)?.tagName)) {
        return;
      }
      const keyNum = parseInt(e.key, 10);
      if (keyNum >= 1 && keyNum <= CARTRIDGES.length) {
        const target = CARTRIDGES[keyNum - 1];
        if (target && target.id !== activeCartridge) {
          triggerHaptic('tap');
          onSelectCartridge(target.id);
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeCartridge, onSelectCartridge]);

  const handleSelect = (id: CartridgeId) => {
    triggerHaptic('tap');
    onSelectCartridge(id);
  };

  const handleLock = () => {
    triggerHaptic('heavy');
    onLockVault();
  };

  return (
    <nav
      aria-label="Tenant Cartridge Carousel"
      className="w-full border-b border-[#D4AF37]/30 bg-[#050510]/95 backdrop-blur-md px-2 sm:px-6 py-2 flex flex-col md:flex-row items-center justify-between gap-2.5 z-30"
    >
      {/* Left: Tenant Carousel Pills */}
      <div className="flex items-center gap-1.5 sm:gap-2 overflow-x-auto w-full md:w-auto pb-1 md:pb-0 scrollbar-none">
        <div className="hidden lg:flex items-center gap-1.5 text-xs font-['Cinzel'] font-bold text-[#D4AF37] pr-2 border-r border-[#4B0082]">
          <Layers className="w-4 h-4 text-[#D4AF37]" />
          <span>CAROUSEL</span>
        </div>

        {CARTRIDGES.map((cartridge, idx) => {
          const isActive = activeCartridge === cartridge.id;
          return (
            <button
              key={cartridge.id}
              onClick={() => handleSelect(cartridge.id)}
              aria-current={isActive ? 'page' : undefined}
              className={cn(
                "px-3 sm:px-3.5 py-2 text-xs font-['Cinzel'] tracking-wider flex items-center gap-2 whitespace-nowrap transition-all border rounded-md min-h-[44px] cursor-pointer",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#D4AF37]",
                isActive
                  ? "bg-[#D4AF37]/20 border-[#D4AF37] text-[#D4AF37] font-bold shadow-[0_0_15px_rgba(212,175,55,0.4)]"
                  : "bg-black/40 border-[#4B0082]/60 text-[#F1EFF4]/70 hover:text-[#F1EFF4] hover:border-[#D4AF37]/40"
              )}
            >
              <span className="text-[10px] font-mono text-[#D4AF37]/70 font-bold">[{idx + 1}]</span>
              {cartridge.id === 'ecosystem-pwa' && <Smartphone className="w-3.5 h-3.5 text-purple-400" />}
              {cartridge.id === 'excalibur-ecc' && <Shield className="w-3.5 h-3.5 text-[#D4AF37]" />}
              {cartridge.id === 'kba-executive' && <Building2 className="w-3.5 h-3.5 text-[#9D4EDD]" />}
              {cartridge.id === 'digital-factory' && <Factory className="w-3.5 h-3.5 text-[#E5B842]" />}
              {cartridge.id === '1vizion-rcrds' && <Disc className="w-3.5 h-3.5 text-[#4CC9F0]" />}
              <span>{cartridge.name}</span>
              <span className="text-[9px] font-['JetBrains_Mono'] opacity-60">[{cartridge.risk}]</span>
            </button>
          );
        })}
      </div>

      {/* Right: Lease Token & Lock Sovereign Vault */}
      <div className="flex items-center gap-2 sm:gap-3 self-end md:self-auto w-full md:w-auto justify-between md:justify-end">
        <div className="text-[10px] font-['JetBrains_Mono'] text-[#F1EFF4]/70 hidden sm:block">
          <span className="text-[#D4AF37]">OPERATOR:</span> {operator}
          <span className="mx-2 text-[#4B0082]">|</span>
          <span className="text-[#10B981]">LEASE:</span> {leaseId ? leaseId.substring(0, 18) : 'ACTIVE'}...
        </div>

        <button
          onClick={handleLock}
          className="px-3.5 py-2 border border-[#DE4258]/60 bg-[#DE4258]/15 text-[#DE4258] hover:bg-[#DE4258]/30 hover:border-[#DE4258] font-['Cinzel'] text-xs font-bold tracking-widest flex items-center gap-1.5 transition-all min-h-[44px] rounded-md cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#DE4258]"
          title="Lock Tenant Carousel and re-engage Excalibur Bio-Auth Gate"
        >
          <Lock className="w-3.5 h-3.5" />
          <span>SEAL VAULT</span>
        </button>
      </div>
    </nav>
  );
}
