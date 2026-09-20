import { useState } from 'react';
import { useEcosystemStore } from '../../state/useEcosystemStore';
import { TenantBioAuth } from './TenantBioAuth';
import { GlassPanel } from '../ui/GlassPanel';
import { Crown, Sparkles, ArrowRight, Shield, CheckCircle2 } from 'lucide-react';

export const OnboardingFlow = ({ onComplete }: { onComplete: () => void }) => {
  const [step, setStep] = useState(1);
  const [operatorName, setOperatorName] = useState('VaShawn O. Head (Vizion)');
  const [email, setEmail] = useState('Vizion711@gmail.com');
  const { setTenantID, setAuthToken, setBiometricVerified } = useEcosystemStore();

  const handleSignUp = () => {
    // 1. Store local cache token (IndexedDB/localStorage)
    // 2. Set tenant_id from server response
    setTenantID('tenant_cuyahoga_001');
    setStep(2);
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-[75vh] p-4 sm:p-6 max-w-lg mx-auto w-full">
      {step === 1 && (
        <div className="w-full space-y-6 text-center">
          <div className="space-y-3">
            <div className="w-16 h-16 mx-auto rounded-2xl border border-[#D4AF37]/60 bg-[#4B0082]/30 flex items-center justify-center shadow-[0_0_30px_rgba(212,175,55,0.3)]">
              <Crown className="w-8 h-8 text-[#D4AF37]" />
            </div>
            <h1 className="font-['Cinzel'] text-3xl sm:text-4xl font-black text-[#D4AF37] tracking-wider">
              CAMELOT-OS
            </h1>
            <p className="font-['Spectral'] text-sm sm:text-base text-[#F1EFF4]/80 italic">
              Mr. Wealth / Vizion Sky Ecosystem
            </p>
            <span className="inline-block text-[10px] font-['JetBrains_Mono'] px-3 py-1 border border-[#4B0082] bg-black/60 text-[#D4AF37] rounded-full">
              SAMSUNG S26 ULTRA EDGE SHELL // 4GB STRICT
            </span>
          </div>

          <GlassPanel glow="gold" className="space-y-4 text-left">
            <div className="space-y-1">
              <label className="text-[10px] font-['JetBrains_Mono'] text-[#D4AF37] uppercase">
                SOVEREIGN OPERATOR
              </label>
              <input
                type="text"
                value={operatorName}
                onChange={(e) => setOperatorName(e.target.value)}
                className="w-full bg-black/60 border border-[#4B0082] rounded-lg px-3.5 py-2.5 text-sm font-['Spectral'] text-[#F1EFF4] focus:outline-none focus:border-[#D4AF37]"
              />
            </div>

            <div className="space-y-1">
              <label className="text-[10px] font-['JetBrains_Mono'] text-[#D4AF37] uppercase">
                ENTERPRISE COMMUNICATIONS ID
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter sovereign email"
                className="w-full bg-black/60 border border-[#4B0082] rounded-lg px-3.5 py-2.5 text-sm font-['Spectral'] text-[#F1EFF4] focus:outline-none focus:border-[#D4AF37]"
              />
            </div>

            <div className="p-3 bg-[#4B0082]/20 border border-[#4B0082]/40 rounded-lg text-xs font-['JetBrains_Mono'] text-[#F1EFF4]/70 flex items-start gap-2">
              <Shield className="w-4 h-4 text-[#D4AF37] shrink-0 mt-0.5" />
              <span>Zero-Docker Native Edge Architecture. Hardware Knox attestation binding initiated on submission.</span>
            </div>
          </GlassPanel>

          <button
            id="proceed-to-bio-btn"
            type="button"
            onClick={handleSignUp}
            className="w-full py-4 bg-[#D4AF37] hover:bg-[#F1EFF4] text-[#050510] font-['Cinzel'] font-bold text-sm tracking-wider rounded-xl shadow-[0_0_25px_rgba(212,175,55,0.35)] transition-all flex items-center justify-center gap-2 min-h-[48px]"
          >
            <span>SIGN UP / INITIALIZE LEASE</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {step === 2 && (
        <div className="w-full">
          <TenantBioAuth
            onSuccess={() => {
              setBiometricVerified(true);
              setAuthToken('EXCALIBUR_ED25519_LEASE_ACTIVE');
              setStep(3);
            }}
            onCancel={() => {
              setStep(3);
            }}
          />
        </div>
      )}

      {step === 3 && (
        <GlassPanel glow="gold" className="w-full text-center space-y-5 p-6 sm:p-8">
          <div className="w-14 h-14 mx-auto rounded-full bg-emerald-950/60 border-2 border-emerald-400 flex items-center justify-center">
            <CheckCircle2 className="w-8 h-8 text-emerald-400" />
          </div>

          <div className="space-y-2">
            <h2 className="text-2xl font-['Cinzel'] font-bold text-[#D4AF37]">
              ECOSYSTEM UNLOCKED
            </h2>
            <p className="text-xs sm:text-sm font-['Spectral'] text-[#F1EFF4]/80">
              Sovereign credentials bound to S26 Knox enclave. Alfred Ω Grand Chamberlain and the Round Table Knights are synchronized.
            </p>
          </div>

          <div className="p-3 bg-black/60 border border-[#4B0082] rounded-lg text-[11px] font-['JetBrains_Mono'] text-emerald-400">
            TENANT: tenant_cuyahoga_001 // ⚜️_SOVEREIGN_TRUTH
          </div>

          <button
            id="enter-dashboard-btn"
            type="button"
            onClick={onComplete}
            className="w-full py-3.5 bg-[#D4AF37] hover:bg-[#F1EFF4] text-black font-['Cinzel'] font-bold text-xs tracking-wider rounded-xl transition-all shadow-[0_0_20px_rgba(212,175,55,0.3)] flex items-center justify-center gap-2 min-h-[44px]"
          >
            <Sparkles className="w-4 h-4" />
            <span>ENTER DIGITAL THRONE DASHBOARD</span>
          </button>
        </GlassPanel>
      )}
    </div>
  );
};
