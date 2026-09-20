import { useState } from 'react';
import { useEcosystemStore, INITIAL_KNIGHTS, KnightPersonality } from '../../state/useEcosystemStore';
import { KnightCard } from './KnightCard';
import { GlassPanel } from '../ui/GlassPanel';
import { Sliders, Sparkles, Volume2, Shield, RotateCcw, Check } from 'lucide-react';

export function KnightCustomizer() {
  const { selectedKnight, setSelectedKnight } = useEcosystemStore();
  const [knights, setKnights] = useState<KnightPersonality[]>(INITIAL_KNIGHTS);
  const activeKnight = knights.find((k) => k.id === selectedKnight) || knights[0];

  const handleSliderChange = (trait: keyof KnightPersonality['oceanScores'], value: number) => {
    setKnights((prev) =>
      prev.map((k) =>
        k.id === activeKnight.id
          ? {
              ...k,
              oceanScores: {
                ...k.oceanScores,
                [trait]: value
              }
            }
          : k
      )
    );
  };

  const [savedNotice, setSavedNotice] = useState(false);
  const handleSaveTuning = () => {
    setSavedNotice(true);
    setTimeout(() => setSavedNotice(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#4B0082] pb-4">
        <div>
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-[#D4AF37]" />
            <h2 className="text-xl sm:text-2xl font-['Cinzel'] font-bold text-[#D4AF37]">
              Round Table Knights & OCEAN Customizer
            </h2>
          </div>
          <p className="text-xs font-['Spectral'] text-[#F1EFF4]/70 mt-1">
            Tune cognitive OCEAN dimensions and bind real-time voice synthesizer personas.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[10px] font-['JetBrains_Mono'] px-2.5 py-1 border border-[#D4AF37] bg-black/60 text-[#D4AF37] rounded">
            ACTIVE: {activeKnight.name.toUpperCase()}
          </span>
        </div>
      </div>

      {/* Knight Avatar Selection Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {knights.map((knight) => (
          <KnightCard
            key={knight.id}
            knight={knight}
            isSelected={knight.id === selectedKnight}
            onSelect={(id) => setSelectedKnight(id)}
          />
        ))}
      </div>

      {/* OCEAN Tuning Console */}
      <GlassPanel glow="purple" className="space-y-5 p-5 sm:p-6">
        <div className="flex items-center justify-between border-b border-[#4B0082]/60 pb-3 flex-wrap gap-2">
          <div className="flex items-center gap-2">
            <Sliders className="w-5 h-5 text-[#D4AF37]" />
            <h3 className="font-['Cinzel'] font-bold text-base text-[#F1EFF4]">
              Cognitive Trait Matrix // {activeKnight.name}
            </h3>
          </div>
          <span className="text-[10px] font-['JetBrains_Mono'] text-purple-300 border border-purple-500/40 bg-purple-950/40 px-2 py-0.5 rounded">
            OUROBOROS 1.58b RECURRENCE WEIGHTS
          </span>
        </div>

        {/* Sliders Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Openness */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-['JetBrains_Mono']">
              <span className="text-[#D4AF37] font-bold">Openness to Experience</span>
              <span className="text-emerald-400 font-bold">{activeKnight.oceanScores.openness} / 100</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={activeKnight.oceanScores.openness}
              onChange={(e) => handleSliderChange('openness', Number(e.target.value))}
              className="w-full accent-[#D4AF37] cursor-pointer"
            />
            <p className="text-[11px] font-['Spectral'] text-[#F1EFF4]/60">
              Affects speculative architectural proposals, GraphRAG memory queries, and novel prompt synthesis.
            </p>
          </div>

          {/* Conscientiousness */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-['JetBrains_Mono']">
              <span className="text-[#D4AF37] font-bold">Conscientiousness & Rigor</span>
              <span className="text-emerald-400 font-bold">{activeKnight.oceanScores.conscientiousness} / 100</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={activeKnight.oceanScores.conscientiousness}
              onChange={(e) => handleSliderChange('conscientiousness', Number(e.target.value))}
              className="w-full accent-[#D4AF37] cursor-pointer"
            />
            <p className="text-[11px] font-['Spectral'] text-[#F1EFF4]/60">
              Enforces strict 4GB RAM ceiling, Z3 SMT solver verification, and zero tolerance for syntax flaws.
            </p>
          </div>

          {/* Extraversion */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-['JetBrains_Mono']">
              <span className="text-[#D4AF37] font-bold">Extraversion (Voice Verbosity)</span>
              <span className="text-emerald-400 font-bold">{activeKnight.oceanScores.extraversion} / 100</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={activeKnight.oceanScores.extraversion}
              onChange={(e) => handleSliderChange('extraversion', Number(e.target.value))}
              className="w-full accent-[#D4AF37] cursor-pointer"
            />
            <p className="text-[11px] font-['Spectral'] text-[#F1EFF4]/60">
              Controls Alfred voice response cadence and proactive audio prompt generation.
            </p>
          </div>

          {/* Agreeableness */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-['JetBrains_Mono']">
              <span className="text-[#D4AF37] font-bold">Agreeableness & Protocol Harmony</span>
              <span className="text-emerald-400 font-bold">{activeKnight.oceanScores.agreeableness} / 100</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={activeKnight.oceanScores.agreeableness}
              onChange={(e) => handleSliderChange('agreeableness', Number(e.target.value))}
              className="w-full accent-[#D4AF37] cursor-pointer"
            />
            <p className="text-[11px] font-['Spectral'] text-[#F1EFF4]/60">
              Balances defensive firewall warnings against automated task dispatch approvals.
            </p>
          </div>

          {/* Neuroticism */}
          <div className="space-y-2 md:col-span-2">
            <div className="flex justify-between text-xs font-['JetBrains_Mono']">
              <span className="text-[#D4AF37] font-bold">Neuroticism (Security Alert Sensitivity)</span>
              <span className="text-emerald-400 font-bold">{activeKnight.oceanScores.neuroticism} / 100</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={activeKnight.oceanScores.neuroticism}
              onChange={(e) => handleSliderChange('neuroticism', Number(e.target.value))}
              className="w-full accent-[#D4AF37] cursor-pointer"
            />
            <p className="text-[11px] font-['Spectral'] text-[#F1EFF4]/60">
              Sensitivity to memory leaks, out-of-bounds execution, and unverified inbound network telemetry.
            </p>
          </div>
        </div>

        {/* Actions bar */}
        <div className="flex items-center justify-between pt-4 border-t border-[#4B0082]/60 flex-wrap gap-3">
          <button
            type="button"
            onClick={() => setKnights(INITIAL_KNIGHTS)}
            className="px-4 py-2 border border-[#4B0082] text-xs font-['Cinzel'] text-[#F1EFF4]/70 hover:text-[#F1EFF4] rounded flex items-center gap-1.5 transition-all"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            RESET DEFAULTS
          </button>

          <button
            type="button"
            onClick={handleSaveTuning}
            className="px-6 py-2.5 bg-[#D4AF37] hover:bg-[#F1EFF4] text-black text-xs font-['Cinzel'] font-bold rounded shadow-[0_0_15px_rgba(212,175,55,0.3)] transition-all flex items-center gap-2"
          >
            {savedNotice ? (
              <>
                <Check className="w-4 h-4" />
                <span>SAVED & SYNCHRONIZED</span>
              </>
            ) : (
              <>
                <Volume2 className="w-4 h-4" />
                <span>SAVE COGNITIVE LATTICE</span>
              </>
            )}
          </button>
        </div>
      </GlassPanel>
    </div>
  );
}
