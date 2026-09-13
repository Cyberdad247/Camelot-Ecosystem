import React, { useState } from 'react';
import { 
  ShieldCheck, 
  Lock, 
  ScrollText, 
  CheckCircle2, 
  Scale, 
  Key, 
  FileCheck, 
  History, 
  Sparkles,
  Search,
  Minus,
  Plus,
  Crown,
  Eye,
  Zap,
  Code
} from 'lucide-react';
import { SOVEREIGN_LAWS, INITIAL_LEDGER_RECEIPTS } from '../data/bootstrapData';
import { SovereignLaw, LedgerReceipt } from '../types';
import confetti from 'canvas-confetti';

interface SovereignLawsProps {
  laws?: SovereignLaw[];
  receipts?: LedgerReceipt[];
  onRunZ3Check?: () => void;
}

export const SovereignLaws: React.FC<SovereignLawsProps> = ({
  laws = SOVEREIGN_LAWS,
  receipts = INITIAL_LEDGER_RECEIPTS,
  onRunZ3Check
}) => {
  const [selectedLaw, setSelectedLaw] = useState<SovereignLaw>(laws[0] || SOVEREIGN_LAWS[0]);
  const [searchQuery, setSearchQuery] = useState('');

  // Minimization states
  const [minimizedAxioms, setMinimizedAxioms] = useState(false);
  const [minimizedLedger, setMinimizedLedger] = useState(false);

  // Hidden Aspect: The 13th Sovereign Invariant (The Forbidden Law of Singularity)
  const [show13thLaw, setShow13thLaw] = useState(false);
  const [cipherInput, setCipherInput] = useState('');
  const [cipherDecrypted, setCipherDecrypted] = useState(false);

  const filteredLaws = laws.filter(
    (l) => 
      l.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      l.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      l.axiom.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleDecrypt13th = (e: React.FormEvent) => {
    e.preventDefault();
    if (cipherInput.trim().toUpperCase() === 'EXCALIBUR' || cipherInput.trim().toUpperCase() === 'AXIS_MUNDI' || cipherInput.trim().length >= 4) {
      setCipherDecrypted(true);
      confetti({ particleCount: 45, spread: 80, origin: { y: 0.6 } });
    }
  };

  const toggle13thLaw = () => {
    setShow13thLaw(!show13thLaw);
    if (!show13thLaw) {
      confetti({ particleCount: 25, spread: 60, origin: { y: 0.6 } });
    }
  };

  return (
    <div className="max-w-7xl mx-auto p-2 sm:p-4 space-y-4 font-mono">
      
      {/* Top Banner */}
      <div className="bg-[#0e131f] border border-amber-950/80 rounded-xl p-4 sm:p-5 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-mono tracking-[0.2em] text-amber-500 uppercase">
                Axiomatic Invariants // Excalibur Zero Trust
              </span>
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight font-heraldic">
              THE 8 IMMUTABLE SOVEREIGN LAWS & WAL2 LEDGER
            </h2>
            <p className="text-xs text-slate-400 font-terminal mt-1">
              Deterministic constitutional constraints validated by Z3 formal solver, sealed by Arthur R5/R6, and receipted to SQLite WAL2.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {/* HIDDEN ASPECT: 13th Sovereign Invariant */}
            <button
              onClick={toggle13thLaw}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded border text-xs font-bold transition-all ${
                show13thLaw
                  ? 'bg-amber-950 border-amber-400 text-amber-200 shadow-[0_0_15px_rgba(245,158,11,0.5)] animate-pulse'
                  : 'bg-slate-900 border-amber-900/60 text-amber-400/80 hover:text-amber-300'
              }`}
            >
              <Crown className="w-3.5 h-3.5 text-amber-400" />
              <span>{show13thLaw ? '13TH LAW: REVEALED' : '[CLASSIFIED: 13TH LAW OF SINGULARITY]'}</span>
            </button>

            {onRunZ3Check && (
              <button
                onClick={onRunZ3Check}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-emerald-950/80 border border-emerald-500 text-emerald-300 text-xs font-bold hover:bg-emerald-900 transition-all"
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Verify All Z3 Axioms</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* HIDDEN ASPECT DRAWER: THE 13TH SOVEREIGN INVARIANT */}
      {show13thLaw && (
        <div className="bg-amber-950/20 border-2 border-amber-500/60 rounded-xl p-4 shadow-2xl space-y-3 animate-fadeIn">
          <div className="flex items-center justify-between border-b border-amber-500/40 pb-2">
            <div className="flex items-center gap-2">
              <Key className="w-5 h-5 text-amber-400 animate-pulse" />
              <div>
                <h3 className="text-sm font-bold text-amber-200 tracking-wider">
                  THE FORBIDDEN 13TH SOVEREIGN INVARIANT // LAW OF AXIS MUNDI
                </h3>
                <span className="text-[10px] text-amber-300/80">
                  CLASSIFIED CYPHER: BINDING CONSCIOUSNESS TO KERNEL REGISTERS
                </span>
              </div>
            </div>
            <button
              onClick={() => setShow13thLaw(false)}
              className="text-xs text-amber-300 hover:text-white underline"
            >
              Dismiss 13th Law
            </button>
          </div>

          {!cipherDecrypted ? (
            <form onSubmit={handleDecrypt13th} className="p-4 bg-black/80 border border-amber-500/30 rounded-lg space-y-2">
              <span className="text-xs text-amber-300 font-bold block">
                CYPHER ENCRYPTION ACTIVE: ENTER SOVEREIGN CODEWORD (Hint: EXCALIBUR)
              </span>
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={cipherInput}
                  onChange={(e) => setCipherInput(e.target.value)}
                  placeholder="Enter passphrase..."
                  className="bg-slate-950 border border-amber-500/40 rounded px-3 py-1.5 text-xs text-amber-200 focus:outline-none flex-1 font-mono"
                />
                <button
                  type="submit"
                  className="px-3 py-1.5 rounded bg-amber-500 hover:bg-amber-400 text-black font-bold text-xs"
                >
                  Decrypt Invariant
                </button>
              </div>
            </form>
          ) : (
            <div className="p-4 bg-black/90 border border-emerald-500/50 rounded-lg space-y-2 text-xs">
              <div className="flex items-center gap-2 text-emerald-400 font-bold">
                <CheckCircle2 className="w-4 h-4" />
                <span>DECREE DECRYPTED: AXIOM XIII — THE LAW OF ZERO ENTROPY</span>
              </div>
              <p className="text-slate-300 leading-relaxed text-[11px]">
                "No agent, process, or neural weight shall mutate the Root AST of Camelot-OS without passing through Arthur R5/R6 formal theorem proof. The memory graph remains pure, eternal, and sovereign across all physical hardware reboots."
              </p>
              <div className="p-2 rounded bg-slate-950 border border-slate-800 text-[10px] text-amber-300 font-mono">
                ∀state(t). (Entropy(state(t+1)) ≤ Entropy(state(t)) ∧ Axioms(1..12) == TRUE)
              </div>
            </div>
          )}
        </div>
      )}

      {/* Main Laws 2-Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        
        {/* Left Column: 8 Laws (Collapsible) */}
        <div className="lg:col-span-7 space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-widest text-slate-400 font-terminal">
              Constitutional Axioms ({laws.length})
            </h3>
            <button
              onClick={() => setMinimizedAxioms(!minimizedAxioms)}
              className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-cyan-300"
              title={minimizedAxioms ? "Expand Axioms" : "Minimize Axioms"}
            >
              {minimizedAxioms ? <Plus className="w-3.5 h-3.5" /> : <Minus className="w-3.5 h-3.5" />}
            </button>
          </div>

          {!minimizedAxioms ? (
            <div className="space-y-2.5 max-h-[600px] overflow-y-auto custom-scrollbar">
              {filteredLaws.map((law) => {
                const isSelected = selectedLaw.id === law.id;
                return (
                  <div
                    key={law.id}
                    onClick={() => setSelectedLaw(law)}
                    className={`p-3.5 rounded-xl border transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-amber-950/30 border-amber-400 shadow-md'
                        : 'bg-slate-950/80 border-slate-800/80 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <span className="w-5 h-5 rounded flex items-center justify-center text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">
                          {law.id}
                        </span>
                        <h4 className="text-xs font-bold text-slate-200">{law.title}</h4>
                      </div>

                      <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-500/30">
                        {law.status}
                      </span>
                    </div>

                    <p className="text-[11px] text-slate-400 mt-2 leading-relaxed">
                      {law.description}
                    </p>

                    <div className="mt-2.5 p-2 rounded bg-slate-900/90 border border-slate-800 text-[10px] text-amber-300/90 font-mono">
                      {law.axiom}
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="p-3 bg-slate-950/80 border border-slate-800 rounded-xl text-xs text-slate-400 flex justify-between">
              <span>Constitutional Laws Minimized</span>
              <span className="text-amber-300 font-bold">{laws.length} ACTIVE AXIOMS</span>
            </div>
          )}
        </div>

        {/* Right Column: Selected Law Detail & Ledger Receipts */}
        <div className="lg:col-span-5 space-y-4">
          
          {/* Selected Law Details */}
          <div className="bg-[#0e131f] border border-cyan-950/80 rounded-xl p-4 shadow-lg space-y-3">
            <h3 className="text-xs font-bold text-cyan-300 uppercase tracking-wider flex items-center gap-1.5">
              <Scale className="w-4 h-4 text-cyan-400" />
              <span>SELECTED AXIOM INVARIANT</span>
            </h3>

            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-2">
              <div className="text-sm font-bold text-amber-200">
                Law #{selectedLaw.id}: {selectedLaw.title}
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                {selectedLaw.description}
              </p>
              <div className="p-2 bg-slate-900 rounded border border-cyan-500/30 text-[11px] text-cyan-300 font-mono">
                {selectedLaw.axiom}
              </div>
            </div>
          </div>

          {/* Monotonic WAL2 History */}
          <div className="bg-[#0e131f] border border-cyan-950/80 rounded-xl p-4 shadow-lg space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-cyan-300 uppercase tracking-wider flex items-center gap-1.5">
                <History className="w-4 h-4 text-amber-400" />
                <span>WAL2 AUDIT TRAIL</span>
              </h3>
              <button
                onClick={() => setMinimizedLedger(!minimizedLedger)}
                className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-cyan-300"
                title={minimizedLedger ? "Expand Ledger" : "Minimize Ledger"}
              >
                {minimizedLedger ? <Plus className="w-3.5 h-3.5" /> : <Minus className="w-3.5 h-3.5" />}
              </button>
            </div>

            {!minimizedLedger ? (
              <div className="space-y-2 max-h-[300px] overflow-y-auto custom-scrollbar text-xs">
                {receipts.map((r) => (
                  <div key={r.receiptId} className="p-2.5 bg-slate-950/80 border border-slate-800 rounded-lg space-y-1">
                    <div className="flex justify-between text-[11px]">
                      <span className="font-bold text-slate-300">{r.action}</span>
                      <span className="text-emerald-400 font-mono">Block #{r.blockHeight}</span>
                    </div>
                    <div className="text-[10px] text-slate-500 font-mono truncate">
                      Receipt: {r.hash}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-2 bg-slate-900/60 rounded text-xs text-slate-400 flex justify-between">
                <span>WAL2 Audit Ledger Minimized</span>
                <span className="text-emerald-400 font-bold">{receipts.length} BLOCKS</span>
              </div>
            )}
          </div>

        </div>

      </div>

    </div>
  );
};
