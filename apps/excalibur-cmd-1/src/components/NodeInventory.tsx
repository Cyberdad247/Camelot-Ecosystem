import { NodeRecord } from '../types';
import { cn } from '../lib/utils';
import { BadgeGlyph, SystemStatusType } from './ui/BadgeGlyph';
import { triggerHaptic } from '../lib/haptics';

export function NodeInventory({
  nodes,
  selectedId,
  onSelect
}: {
  nodes: NodeRecord[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}) {
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

  const handleSelectNode = (id: string) => {
    triggerHaptic('tap');
    onSelect(id);
  };

  return (
    <section
      aria-label="Node Inventory"
      className="flex flex-col h-full border border-[#D4AF37]/40 bg-[#050510]/85 rounded-xl overflow-hidden shadow-[0_0_20px_rgba(75,0,130,0.3)] relative backdrop-blur-xl"
    >
      <div className="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-[#D4AF37] rounded-tl-sm" />
      <div className="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-[#D4AF37] rounded-br-sm" />
      
      <div className="p-4 border-b border-[#4B0082]/60 bg-[#050510]">
        <h2 className="text-sm font-['Cinzel'] text-[#D4AF37] tracking-[0.1em] uppercase font-bold">
          Node Inventory
        </h2>
      </div>
      
      <div
        role="listbox"
        aria-label="Active Camelot Nodes"
        className="flex-1 overflow-y-auto p-3 space-y-2.5"
      >
        {nodes.map(node => {
          const isSelected = selectedId === node.id;
          return (
            <button
              key={node.id}
              role="option"
              aria-selected={isSelected}
              onClick={() => handleSelectNode(node.id)}
              className={cn(
                "w-full text-left p-3 border rounded-lg transition-all duration-200 min-h-[44px] relative group overflow-hidden cursor-pointer",
                "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#D4AF37]",
                isSelected 
                  ? "border-[#D4AF37] bg-[#D4AF37]/15 shadow-[0_0_15px_rgba(212,175,55,0.25)]" 
                  : "border-[#4B0082]/50 bg-black/40 hover:border-[#D4AF37]/50 hover:bg-[#4B0082]/20"
              )}
            >
              <div className="flex items-center justify-between mb-2">
                <span className={cn(
                  "font-['Cinzel'] font-bold text-sm tracking-wide",
                  isSelected ? "text-[#D4AF37]" : "text-[#F1EFF4]"
                )}>
                  {node.name}
                </span>
                
                <BadgeGlyph status={mapNodeStatusToBadge(node.status)} size="sm" />
              </div>
              
              <div className="flex items-center justify-between text-[11px] font-mono text-[#F1EFF4]/70">
                <span className="text-[#9E9AA7]">{node.ip}</span>
                <span className={cn(
                  "font-semibold",
                  node.load > 75 ? "text-[#DE4258]" : "text-[#10B981]"
                )}>
                  LOAD: {node.load}%
                </span>
              </div>
            </button>
          );
        })}
        {nodes.length === 0 && (
          <div className="text-center p-6 text-xs font-mono text-[#F1EFF4]/50">
            Awaiting Merlin_Ω DAG node streams...
          </div>
        )}
      </div>
    </section>
  );
}
