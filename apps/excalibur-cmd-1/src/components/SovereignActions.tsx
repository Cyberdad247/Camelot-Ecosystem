import { NodeRecord } from '../types';
import { Plus, Minus, CheckCircle } from 'lucide-react';
import { useState } from 'react';
import { TacticalButton } from './ui/TacticalButton';
import { BadgeGlyph, SystemStatusType } from './ui/BadgeGlyph';
import { triggerHaptic } from '../lib/haptics';

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
      <section
        aria-label="Sovereign Directives"
        className="flex flex-col h-full border border-[#D4AF37]/30 bg-[#050510]/60 rounded-xl p-4 relative backdrop-blur-xl"
      >
        <div className="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-[#D4AF37]/50 rounded-tr-sm" />
        <h2 className="text-sm font-['Cinzel'] text-[#D4AF37] uppercase opacity-60 font-bold">
          Sovereign Directives
        </h2>
        <div className="flex-1 flex items-center justify-center text-xs font-mono text-[#F1EFF4]/40 tracking-widest">
          AWAITING NODE SELECTION
        </div>
      </section>
    );
  }

  const handleAction = async (action: string) => {
    setLoadingAction(action);
    triggerHaptic(action === 'eject' ? 'warning' : 'tap');
    try {
      await onAction(node.id, action);
      triggerHaptic('success');
    } catch {
      triggerHaptic('error');
    } finally {
      setLoadingAction(null);
    }
  };

  const mapNodeStatusToBadge = (status: NodeRecord['status']): SystemStatusType => {
    switch (status) {
      case 'online':
      case 'ACTIVE':
        return 'ONLINE';
      case 'syncing':
        return 'SYNCING';
      case 'isolated':
        return 'AIRGAP';
      default:
        return 'OFFLINE';
    }
  };

  return (
    <section
      aria-label="Sovereign Directives Panel"
      className="flex flex-col h-full border border-[#D4AF37]/60 bg-[#050510]/85 rounded-xl overflow-hidden shadow-[0_0_25px_rgba(75,0,130,0.4)] relative backdrop-blur-xl"
    >
      <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-[#D4AF37] rounded-tr-sm" />
      <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-[#D4AF37] rounded-bl-sm" />

      <div className="p-4 border-b border-[#4B0082]/60 flex items-center justify-between">
        <div>
          <h2 className="text-sm font-['Cinzel'] text-[#D4AF37] tracking-[0.1em] uppercase font-bold">
            SOVEREIGN DIRECTIVES
          </h2>
          <span className="text-[10px] text-[#F1EFF4]/70 font-mono">Target: {node.name}</span>
        </div>
        <BadgeGlyph status={mapNodeStatusToBadge(node.status)} size="sm" />
      </div>
      
      <div className="flex-1 p-4 sm:p-5 flex flex-col gap-3 justify-center">
        <TacticalButton 
          variant="gold"
          size="md"
          loading={loadingAction === 'insert'}
          disabled={loadingAction !== null}
          onClick={() => handleAction('insert')}
          icon={<Plus className="w-4 h-4" />}
          className="w-full text-xs font-['Cinzel'] tracking-[0.15em]"
        >
          Insert Node
        </TacticalButton>

        <TacticalButton 
          variant="danger"
          size="md"
          loading={loadingAction === 'eject'}
          disabled={loadingAction !== null}
          onClick={() => handleAction('eject')}
          icon={<Minus className="w-4 h-4" />}
          className="w-full text-xs font-['Cinzel'] tracking-[0.15em]"
        >
          Eject Node
        </TacticalButton>
        
        <TacticalButton 
          variant="purple"
          size="md"
          loading={loadingAction === 'approve'}
          disabled={loadingAction !== null}
          onClick={() => handleAction('approve')}
          icon={<CheckCircle className="w-4 h-4 text-[#D4AF37]" />}
          className="w-full text-xs font-['Cinzel'] tracking-[0.15em]"
        >
          Approve Node
        </TacticalButton>

        <div className="mt-auto bg-black/60 border border-[#D4AF37]/30 p-3 rounded-lg text-[11px] font-mono text-[#F1EFF4]/75 leading-relaxed backdrop-blur-sm shadow-inner">
          <div className="flex justify-between py-0.5">
            <span className="text-[#9E9AA7]">ID:</span>
            <span className="text-[#D4AF37] font-semibold">{node.id}</span>
          </div>
          <div className="flex justify-between py-0.5">
            <span className="text-[#9E9AA7]">LOAD:</span>
            <span className="text-[#F1EFF4] font-semibold">{node.load}%</span>
          </div>
          <div className="flex justify-between py-0.5">
            <span className="text-[#9E9AA7]">COORDINATES:</span>
            <span className="text-[#D4AF37]">
              {node.coordinates ? `X:${node.coordinates.x} Y:${node.coordinates.y}` : 'N/A'}
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}
