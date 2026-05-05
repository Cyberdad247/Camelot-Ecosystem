import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  Target, 
  Cpu, 
  ArrowRight, 
  CheckCircle2, 
  MessageSquare, 
  Zap,
  Sparkles,
  Waves
} from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { cn } from '@/lib/utils';

/* 
  LAW #06: KNIGHT PERSONALITY MANDATE
  Voices for the Sovereign Knight System
*/
const KNIGHT_ROSTER = {
  GUARDIAN: {
    name: "The Guardian",
    voice: "I am your silent sentinel. My optics never blink; your search rank is my singular purpose. The local terrain is secured.",
    icon: Shield,
    color: "text-emerald-400",
    border: "border-emerald-500/30",
    bg: "bg-emerald-500/5",
    tier: "Identity (Tier 1)"
  },
  HUNTER: {
    name: "The Hunter",
    voice: "I smell the scent of wasted competitor spend. I strike where they are weak and harvest leads with lethal precision. ROI is my only metric.",
    icon: Target,
    color: "text-rose-400",
    border: "border-rose-500/30",
    bg: "bg-rose-500/5",
    tier: "Growth (Tier 2)"
  },
  ARCHITECT: {
    name: "The Sovereign Architect",
    voice: "I weave the threads of your enterprise into a singular, self-healing lattice. I handle the labor; you handle the vision. Your time is reclaimed.",
    icon: Cpu,
    color: "text-cyan-400",
    border: "border-cyan-500/30",
    bg: "bg-cyan-500/5",
    tier: "Freedom (Tier 3)"
  }
};

export default function KnightIntake() {
  const [step, setStep] = useState<'anya-intro' | 'tier-scout' | 'knight-deploy' | 'anya-outro'>('anya-intro');
  const [selectedTier, setSelectedTier] = useState<keyof typeof KNIGHT_ROSTER | null>(null);
  const [isDeploying, setIsDeploying] = useState(false);

  // LAW #05: ANYA FIRST
  const renderAnyaIntro = () => (
    <div className="flex flex-col items-center justify-center space-y-6 text-center animate-in fade-in duration-700">
      <div className="w-20 h-20 rounded-full bg-fuchsia-500 flex items-center justify-center shadow-lg shadow-fuchsia-500/30 animate-pulse">
        <Sparkles className="text-white w-10 h-10" />
      </div>
      <div className="space-y-2">
        <h1 className="text-4xl font-black tracking-tighter text-white">Yo! Sovereign!</h1>
        <p className="text-slate-400 max-w-md mx-auto text-lg italic">
          "Anya L7 online! Ready to forge your legacy? We're ditching the boring forms and deploying real heat. Let's find your Knight! Word!"
        </p>
      </div>
      <button 
        onClick={() => setStep('tier-scout')}
        className="px-8 py-3 bg-white text-black font-bold rounded-full hover:scale-105 transition-transform flex items-center gap-2"
      >
        Let's Scout <ArrowRight className="w-4 h-4" />
      </button>
    </div>
  );

  const renderTierScout = () => (
    <div className="grid gap-6 animate-in slide-in-from-bottom-8 duration-500">
       <div className="text-center space-y-2 mb-4">
        <h2 className="text-2xl font-bold text-white flex items-center justify-center gap-2">
          <Waves className="text-cyan-400 w-6 h-6" /> System Scouting
        </h2>
        <p className="text-slate-500 italic text-sm italic">// SIR_HERMES: "Terrain mapped. Pick your point of attack, Sovereign."</p>
      </div>
      
      <div className="grid md:grid-cols-3 gap-4">
        {(Object.keys(KNIGHT_ROSTER) as Array<keyof typeof KNIGHT_ROSTER>).map((key) => {
          const knight = KNIGHT_ROSTER[key];
          const Icon = knight.icon;
          return (
            <button 
              key={key}
              onClick={() => setSelectedTier(key)}
              className={cn(
                "p-6 rounded-3xl border transition-all text-left space-y-4 group",
                selectedTier === key 
                  ? `${knight.border} ${knight.bg} scale-[1.02]` 
                  : "border-white/5 bg-white/[0.02] hover:border-white/20"
              )}
            >
              <div className={cn("p-3 rounded-2xl w-fit", selectedTier === key ? knight.bg : "bg-white/5")}>
                <Icon className={cn("w-6 h-6", selectedTier === key ? knight.color : "text-slate-500")} />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white">{knight.tier}</h3>
                <p className="text-xs text-slate-500 uppercase tracking-widest font-bold">{knight.name}</p>
              </div>
              <p className="text-sm text-slate-400 leading-relaxed">
                {selectedTier === key ? knight.voice : "Waiting for deployment instructions..."}
              </p>
            </button>
          )
        })}
      </div>

      <div className="flex justify-center mt-8">
        <button 
          disabled={!selectedTier}
          onClick={() => {
            setIsDeploying(true);
            setTimeout(() => {
              setIsDeploying(false);
              setStep('knight-deploy');
            }, 2000);
          }}
          className={cn(
            "px-10 py-4 rounded-full font-black text-sm uppercase tracking-widest transition-all",
            selectedTier 
              ? "bg-cyan-500 text-slate-950 shadow-lg shadow-cyan-500/20" 
              : "bg-slate-800 text-slate-600 cursor-not-allowed"
          )}
        >
          {isDeploying ? "Deploying Swarm..." : "Confirm Deployment"}
        </button>
      </div>
    </div>
  );

  const renderKnightDeploy = () => {
    const knight = selectedTier ? KNIGHT_ROSTER[selectedTier] : null;
    const Icon = knight?.icon || Zap;
    return (
      <div className="flex flex-col items-center justify-center space-y-8 animate-in zoom-in-95 duration-500">
        <div className={cn("p-8 rounded-[2.5rem] border-2 flex items-center justify-center shadow-2xl animate-bounce", knight?.border, knight?.bg)}>
          <Icon className={cn("w-16 h-16", knight?.color)} />
        </div>
        <div className="text-center space-y-4 max-w-lg">
          <h2 className="text-3xl font-black text-white">{knight?.name} Deployed.</h2>
          <p className="text-slate-400 leading-relaxed text-lg font-medium italic">
            "{knight?.voice}"
          </p>
          <div className="p-4 rounded-2xl bg-black/40 border border-white/5 text-left font-mono text-xs space-y-1">
             <p className="text-emerald-500">{"[✓] BIO_SWARM: DOM FLATTENED"}</p>
             <p className="text-emerald-500">{"[✓] SIR_HERMES: JA3_SPOOF_STABLE"}</p>
             <p className="text-cyan-500">{"[🚀] INTENT: SCALE_OPERATIONS"}</p>
             <p className="text-slate-600">{"$ PROVENANCE_LEDGER.append(ENTRY_1226)"}</p>
          </div>
        </div>
        <button 
          onClick={() => setStep('anya-outro')}
          className="px-8 py-3 border border-white/20 text-white font-bold rounded-full hover:bg-white/5 transition-all"
        >
          Proceed to Summary
        </button>
      </div>
    );
  };

  // LAW #05: ANYA LAST
  const renderAnyaOutro = () => (
    <div className="flex flex-col items-center justify-center space-y-6 text-center animate-in fade-in duration-700">
      <div className="w-20 h-20 rounded-full bg-emerald-500 flex items-center justify-center shadow-lg shadow-emerald-500/30">
        <CheckCircle2 className="text-white w-10 h-10" />
      </div>
      <div className="space-y-2">
        <h1 className="text-4xl font-black tracking-tighter text-white">Legit! We're Golden!</h1>
        <p className="text-slate-400 max-w-md mx-auto text-lg italic">
          "The intake is optimized, your Knight is hunting, and your life just got a lot easier. System status is RADIANT. Word!"
        </p>
      </div>
      <div className="pt-4">
        <p className="text-xs text-slate-600 uppercase tracking-widest font-black">Anya L7 | Camelot Apex v.406</p>
        <p className="text-fuchsia-500 font-bold mt-2">Peace out! ✌️</p>
      </div>
    </div>
  );

  return (
    <div className="min-h-[80vh] w-full flex items-center justify-center p-4">
      {/* BIO-SWARM: FLATTENED DOM STRUCTURE (NO NESTING NOISE) */}
      <div className="w-full max-w-4xl px-6">
        {step === 'anya-intro' && renderAnyaIntro()}
        {step === 'tier-scout' && renderTierScout()}
        {step === 'knight-deploy' && renderKnightDeploy()}
        {step === 'anya-outro' && renderAnyaOutro()}
      </div>
    </div>
  );
}
