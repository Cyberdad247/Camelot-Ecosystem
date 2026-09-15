import { KnightPersonality, useEcosystemStore } from '../../state/useEcosystemStore';
import { GlassPanel } from '../ui/GlassPanel';
import { Check, Shield } from 'lucide-react';

interface Props {
  knight: KnightPersonality;
  isSelected: boolean;
  onSelect: (id: string) => void;
}

export function KnightCard({ knight, isSelected, onSelect }: Props) {
  return (
    <GlassPanel
      glow={isSelected ? 'gold' : 'none'}
      className={`cursor-pointer transition-all duration-300 hover:scale-[1.02] flex flex-col justify-between ${
        isSelected ? 'border-[#D4AF37] ring-1 ring-[#D4AF37]/50' : 'hover:border-[#4B0082]'
      }`}
      onClick={() => onSelect(knight.id)}
    >
      <div className="space-y-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-black/80 border border-[#D4AF37]/40 flex items-center justify-center text-2xl shadow-[0_0_15px_rgba(212,175,55,0.2)]">
              {knight.avatar}
            </div>
            <div>
              <h3 className="font-['Cinzel'] font-bold text-sm text-[#D4AF37] flex items-center gap-1.5">
                {knight.name}
              </h3>
              <p className="text-[10px] font-['JetBrains_Mono'] text-[#F1EFF4]/60">
                {knight.role}
              </p>
            </div>
          </div>

          {isSelected && (
            <span className="w-6 h-6 rounded-full bg-[#D4AF37] text-black flex items-center justify-center shadow-[0_0_10px_rgba(212,175,55,0.6)]">
              <Check className="w-3.5 h-3.5 stroke-[3]" />
            </span>
          )}
        </div>

        <p className="text-xs font-['Spectral'] text-[#F1EFF4]/85 italic line-clamp-2">
          "{knight.quote}"
        </p>

        <div className="pt-2 border-t border-white/5 space-y-1">
          <div className="text-[10px] font-['JetBrains_Mono'] text-[#D4AF37]/80 flex items-center gap-1">
            <Shield className="w-3 h-3" />
            <span>DOMAIN: {knight.domain}</span>
          </div>

          {/* Mini OCEAN meters */}
          <div className="grid grid-cols-5 gap-1 pt-1 text-[9px] font-['JetBrains_Mono'] text-center">
            <div>
              <span className="text-white/40 block">O</span>
              <span className="text-emerald-400 font-bold">{knight.oceanScores.openness}</span>
            </div>
            <div>
              <span className="text-white/40 block">C</span>
              <span className="text-emerald-400 font-bold">{knight.oceanScores.conscientiousness}</span>
            </div>
            <div>
              <span className="text-white/40 block">E</span>
              <span className="text-emerald-400 font-bold">{knight.oceanScores.extraversion}</span>
            </div>
            <div>
              <span className="text-white/40 block">A</span>
              <span className="text-emerald-400 font-bold">{knight.oceanScores.agreeableness}</span>
            </div>
            <div>
              <span className="text-white/40 block">N</span>
              <span className="text-emerald-400 font-bold">{knight.oceanScores.neuroticism}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-4 pt-2 border-t border-white/5 flex justify-end">
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onSelect(knight.id);
          }}
          className={`w-full py-1.5 text-[10px] font-['Cinzel'] font-bold rounded tracking-wider uppercase transition-all ${
            isSelected
              ? 'bg-[#D4AF37] text-black'
              : 'border border-[#4B0082] text-[#F1EFF4] hover:border-[#D4AF37]'
          }`}
        >
          {isSelected ? 'ACTIVE SYNTHESIZER' : 'BIND COMPANION'}
        </button>
      </div>
    </GlassPanel>
  );
}
