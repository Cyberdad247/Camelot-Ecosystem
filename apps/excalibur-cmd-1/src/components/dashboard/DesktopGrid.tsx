import { useEcosystemStore } from '../../state/useEcosystemStore';
import { CartridgeVault } from '../cartridges/CartridgeVault';
import { Marketplace } from '../cartridges/Marketplace';
import { GuildBoard } from '../guild/GuildBoard';
import { KnightCustomizer } from '../knights/KnightCustomizer';
import { TelemetryWidget } from './Widgets/TelemetryWidget';
import { ReceiptWidget } from './Widgets/ReceiptWidget';
import { CommandBar } from './CommandBar';
import { GlassPanel } from '../ui/GlassPanel';
import { HardDrive, ShoppingBag, Scroll, Users, LayoutDashboard, Smartphone, Monitor } from 'lucide-react';

export const DesktopGrid = () => {
  const { activeView, setActiveView, deviceMode, setDeviceMode } = useEcosystemStore();

  return (
    <div className="space-y-6">
      {/* Ecosystem Top Navigation Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 border-b border-[#4B0082]/60 pb-3">
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0">
          <button
            type="button"
            onClick={() => setActiveView('dashboard')}
            className={`px-3 py-1.5 rounded-lg text-xs font-['Cinzel'] font-bold flex items-center gap-1.5 transition-all whitespace-nowrap ${
              activeView === 'dashboard'
                ? 'bg-[#D4AF37] text-black shadow-[0_0_15px_rgba(212,175,55,0.4)]'
                : 'bg-black/60 border border-[#4B0082] text-[#F1EFF4]/80 hover:text-[#D4AF37]'
            }`}
          >
            <LayoutDashboard className="w-3.5 h-3.5" />
            <span>DESKTOP GRID</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveView('vault')}
            className={`px-3 py-1.5 rounded-lg text-xs font-['Cinzel'] font-bold flex items-center gap-1.5 transition-all whitespace-nowrap ${
              activeView === 'vault'
                ? 'bg-[#D4AF37] text-black shadow-[0_0_15px_rgba(212,175,55,0.4)]'
                : 'bg-black/60 border border-[#4B0082] text-[#F1EFF4]/80 hover:text-[#D4AF37]'
            }`}
          >
            <HardDrive className="w-3.5 h-3.5" />
            <span>CARTRIDGE VAULT</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveView('marketplace')}
            className={`px-3 py-1.5 rounded-lg text-xs font-['Cinzel'] font-bold flex items-center gap-1.5 transition-all whitespace-nowrap ${
              activeView === 'marketplace'
                ? 'bg-[#D4AF37] text-black shadow-[0_0_15px_rgba(212,175,55,0.4)]'
                : 'bg-black/60 border border-[#4B0082] text-[#F1EFF4]/80 hover:text-[#D4AF37]'
            }`}
          >
            <ShoppingBag className="w-3.5 h-3.5" />
            <span>MARKETPLACE</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveView('guild')}
            className={`px-3 py-1.5 rounded-lg text-xs font-['Cinzel'] font-bold flex items-center gap-1.5 transition-all whitespace-nowrap ${
              activeView === 'guild'
                ? 'bg-[#D4AF37] text-black shadow-[0_0_15px_rgba(212,175,55,0.4)]'
                : 'bg-black/60 border border-[#4B0082] text-[#F1EFF4]/80 hover:text-[#D4AF37]'
            }`}
          >
            <Scroll className="w-3.5 h-3.5" />
            <span>GUILD BOARD</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveView('knights')}
            className={`px-3 py-1.5 rounded-lg text-xs font-['Cinzel'] font-bold flex items-center gap-1.5 transition-all whitespace-nowrap ${
              activeView === 'knights'
                ? 'bg-[#D4AF37] text-black shadow-[0_0_15px_rgba(212,175,55,0.4)]'
                : 'bg-black/60 border border-[#4B0082] text-[#F1EFF4]/80 hover:text-[#D4AF37]'
            }`}
          >
            <Users className="w-3.5 h-3.5" />
            <span>KNIGHTS & OCEAN</span>
          </button>
        </div>

        {/* S26 Ultra Edge Aspect Ratio Switcher */}
        <div className="flex items-center gap-2 self-end sm:self-auto">
          <div className="text-[10px] font-mono text-[#F1EFF4]/50 hidden sm:inline">
            VIEWPORT:
          </div>
          <button
            type="button"
            onClick={() => setDeviceMode(deviceMode === 'desktop' ? 'mobile_s26' : 'desktop')}
            className="px-2.5 py-1 text-[11px] font-['JetBrains_Mono'] border border-[#4B0082] rounded bg-black/60 text-[#D4AF37] hover:border-[#D4AF37] flex items-center gap-1.5 transition-all"
            title="Toggle Samsung S26 Ultra (19.5:9 Edge ~480px Container) vs Desktop"
          >
            {deviceMode === 'mobile_s26' ? (
              <>
                <Smartphone className="w-3.5 h-3.5 text-purple-400" />
                <span>S26 EDGE (19.5:9)</span>
              </>
            ) : (
              <>
                <Monitor className="w-3.5 h-3.5 text-emerald-400" />
                <span>DESKTOP VIEW</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* View Switcher Container */}
      {activeView === 'vault' && <CartridgeVault />}
      {activeView === 'marketplace' && <Marketplace />}
      {activeView === 'guild' && <GuildBoard />}
      {activeView === 'knights' && <KnightCustomizer />}

      {activeView === 'dashboard' && (
        <div className="space-y-6">
          {/* Quick Apps Row */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <GlassPanel
              glow="gold"
              className="cursor-pointer hover:border-[#D4AF37] transition-all p-4"
              onClick={() => setActiveView('vault')}
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-black/80 border border-[#D4AF37]/50 flex items-center justify-center text-[#D4AF37]">
                  <HardDrive className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="font-['Cinzel'] font-bold text-sm text-[#F1EFF4]">Cartridge Vault</h4>
                  <p className="text-[11px] font-['Spectral'] text-[#F1EFF4]/60">Hotswap memory slabs</p>
                </div>
              </div>
            </GlassPanel>

            <GlassPanel
              glow="purple"
              className="cursor-pointer hover:border-purple-400 transition-all p-4"
              onClick={() => setActiveView('marketplace')}
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-black/80 border border-purple-500/50 flex items-center justify-center text-purple-300">
                  <ShoppingBag className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="font-['Cinzel'] font-bold text-sm text-[#F1EFF4]">Marketplace</h4>
                  <p className="text-[11px] font-['Spectral'] text-[#F1EFF4]/60">Acquire extensions</p>
                </div>
              </div>
            </GlassPanel>

            <GlassPanel
              glow="none"
              className="cursor-pointer hover:border-[#D4AF37] transition-all p-4"
              onClick={() => setActiveView('guild')}
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-black/80 border border-[#D4AF37]/30 flex items-center justify-center text-[#D4AF37]">
                  <Scroll className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="font-['Cinzel'] font-bold text-sm text-[#F1EFF4]">Guild Board</h4>
                  <p className="text-[11px] font-['Spectral'] text-[#F1EFF4]/60">Mercenary task DAGs</p>
                </div>
              </div>
            </GlassPanel>
          </div>

          {/* Desktop Widgets */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            <GlassPanel glow="gold">
              <TelemetryWidget />
            </GlassPanel>
            <GlassPanel glow="purple">
              <ReceiptWidget />
            </GlassPanel>
          </div>

          {/* Global Command Bar */}
          <CommandBar />
        </div>
      )}
    </div>
  );
};
