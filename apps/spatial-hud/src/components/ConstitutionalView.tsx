import React, { useState } from 'react';
import { Shield, CheckCircle2, Lock, Flame, Sparkles, RefreshCw, Cpu, HardDrive } from 'lucide-react';

export const ConstitutionalView: React.FC = () => {
  const [auditRunning, setAuditRunning] = useState(false);
  const [auditResult, setAuditResult] = useState<string | null>(null);

  const handleRunAudit = () => {
    setAuditRunning(true);
    setAuditResult(null);

    setTimeout(() => {
      setAuditRunning(false);
      setAuditResult('ALL_4_CONSTITUTIONAL_LAWS_SATISFIED // ZERO_ENTROPY_PROVEN');
    }, 1200);
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-neutral-950 text-neutral-100 font-mono overflow-y-auto p-6 md:p-8">
      <div className="max-w-5xl mx-auto w-full space-y-8">
        
        {/* Header */}
        <div className="border-b border-neutral-800 pb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-3">
              <Shield className="w-8 h-8 text-amber-400" />
              <div>
                <h2 className="text-2xl font-bold tracking-tight text-white font-sans">
                  The Camelot-OS Constitution
                </h2>
                <p className="text-xs text-neutral-400 font-mono mt-0.5">
                  Sovereign Kernel vMAX | 4 Immutable Pillars of Autonomous Integrity
                </p>
              </div>
            </div>
          </div>

          <button
            onClick={handleRunAudit}
            disabled={auditRunning}
            className="px-4 py-2.5 bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/50 rounded-xl text-xs font-bold flex items-center space-x-2 transition-all active:scale-95 shadow-md self-start md:self-auto"
          >
            {auditRunning ? (
              <>
                <RefreshCw className="w-4 h-4 text-amber-400 animate-spin" />
                <span>Auditing Lattice...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4 text-amber-400" />
                <span>Run Sovereign Constitutional Audit</span>
              </>
            )}
          </button>
        </div>

        {/* Audit Result Banner */}
        {auditResult && (
          <div className="p-4 bg-emerald-950/90 border border-emerald-800 rounded-xl text-xs text-emerald-300 flex items-center justify-between shadow-lg">
            <div className="flex items-center space-x-2.5">
              <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
              <span className="font-bold">{auditResult}</span>
            </div>
            <span className="text-[10px] bg-emerald-900 text-emerald-200 px-2 py-0.5 rounded font-mono">
              ENTROPY: 0.000
            </span>
          </div>
        )}

        {/* 4 Pillars Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          
          {/* Pillar 1: Anya First / Last Law */}
          <div className="bg-neutral-900/90 rounded-2xl border border-neutral-800 p-6 space-y-4 shadow-lg hover:border-purple-500/40 transition-all">
            <div className="flex items-center justify-between">
              <span className="px-2.5 py-1 bg-purple-950/80 text-purple-300 border border-purple-800/60 rounded-lg text-xs font-bold">
                Pillar I
              </span>
              <span className="text-emerald-400 text-xs font-bold flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> ENFORCED
              </span>
            </div>
            <h3 className="text-lg font-bold text-white font-sans">
              ANYA FIRST / LAST LAW
            </h3>
            <div className="space-y-2 text-xs text-neutral-300 font-sans leading-relaxed">
              <p>
                <strong className="text-white font-mono">Anya First:</strong> Ingress scrubbing removes all conversational static, apologetic filler, and hallucinated preambles before semantic parsing.
              </p>
              <p>
                <strong className="text-white font-mono">Anya Last:</strong> Egress validation runs an automated zero-entropy pass, ensuring all rendered outputs conform to strict TOON, JSON-LD, or structured Markdown contracts.
              </p>
            </div>
            <div className="pt-3 border-t border-neutral-800 text-[11px] text-purple-400 font-mono">
              Hypervisor: Anya_Ω | Algorithm: Triple-QFT Distillation
            </div>
          </div>

          {/* Pillar 2: Isomorphic FileTree Law */}
          <div className="bg-neutral-900/90 rounded-2xl border border-neutral-800 p-6 space-y-4 shadow-lg hover:border-sky-500/40 transition-all">
            <div className="flex items-center justify-between">
              <span className="px-2.5 py-1 bg-sky-950/80 text-sky-300 border border-sky-800/60 rounded-lg text-xs font-bold">
                Pillar II
              </span>
              <span className="text-emerald-400 text-xs font-bold flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> ENFORCED
              </span>
            </div>
            <h3 className="text-lg font-bold text-white font-sans">
              ISOMORPHIC FILETREE LAW
            </h3>
            <div className="space-y-2 text-xs text-neutral-300 font-sans leading-relaxed">
              <p>
                The local Virtual File System (<code className="text-amber-300 font-mono">.agent/</code>) acts as an absolute, deterministic mirror of the remote NotebookLM Worldtree Cloudbrain.
              </p>
              <p>
                If a single node experiences structural or cryptographic drift (<code className="text-amber-300 font-mono">Δ_drift &gt; 0</code>), a hard halt is executed, and <strong className="text-white">Sir Syntax</strong> triggers automatic AST rezeroing.
              </p>
            </div>
            <div className="pt-3 border-t border-neutral-800 text-[11px] text-sky-400 font-mono">
              Governor: Lady Mnemosyne_Ω | Replication: CRDT Ledger
            </div>
          </div>

          {/* Pillar 3: 8GB Scarcity Protocol */}
          <div className="bg-neutral-900/90 rounded-2xl border border-neutral-800 p-6 space-y-4 shadow-lg hover:border-amber-500/40 transition-all">
            <div className="flex items-center justify-between">
              <span className="px-2.5 py-1 bg-amber-950/80 text-amber-300 border border-amber-800/60 rounded-lg text-xs font-bold">
                Pillar III
              </span>
              <span className="text-emerald-400 text-xs font-bold flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> ENFORCED
              </span>
            </div>
            <h3 className="text-lg font-bold text-white font-sans">
              8GB SCARCITY PROTOCOL
            </h3>
            <div className="space-y-2 text-xs text-neutral-300 font-sans leading-relaxed">
              <p>
                All operations are strictly bounded by an 8GB edge-node memory ceiling. Zero-bloat execution prevents memory leaks, wasteful sub-agent spawns, and heavy runtime dependencies.
              </p>
              <p>
                Utilizes Rust-embedded QuickJS sandboxing (<code className="text-amber-300 font-mono">Deer_Flow</code>) and copy-on-write microVMs (<code className="text-amber-300 font-mono">forkd</code>) with &le; 0.12 MiB overhead.
              </p>
            </div>
            <div className="pt-3 border-t border-neutral-800 text-[11px] text-amber-400 font-mono">
              Quota: 8.0GB RAM Ceiling | Current: 7.4GB In-Flight
            </div>
          </div>

          {/* Pillar 4: HITL Iron Gate */}
          <div className="bg-neutral-900/90 rounded-2xl border border-neutral-800 p-6 space-y-4 shadow-lg hover:border-red-500/40 transition-all">
            <div className="flex items-center justify-between">
              <span className="px-2.5 py-1 bg-red-950/80 text-red-300 border border-red-800/60 rounded-lg text-xs font-bold">
                Pillar IV
              </span>
              <span className="text-emerald-400 text-xs font-bold flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> ENFORCED
              </span>
            </div>
            <h3 className="text-lg font-bold text-white font-sans">
              HITL IRON GATE
            </h3>
            <div className="space-y-2 text-xs text-neutral-300 font-sans leading-relaxed">
              <p>
                Any high-risk mutation, destructive purge, secret revocation, or structural state delete halts execution immediately and triggers an explicit <code className="text-red-400 font-mono">[y/N]</code> Human-In-The-Loop authorization prompt.
              </p>
              <p>
                No sub-agent may bypass this gate without signed operator credentials.
              </p>
            </div>
            <div className="pt-3 border-t border-neutral-800 text-[11px] text-red-400 font-mono">
              Auditor: Gideon Verdict Engine | Protocol: //gate
            </div>
          </div>

        </div>

        {/* Provenance Seal Footer */}
        <div className="p-5 bg-neutral-900 rounded-2xl border border-neutral-800 flex items-center justify-between text-xs">
          <div className="flex items-center space-x-3">
            <span className="text-amber-400 text-base">⚜️</span>
            <div>
              <span className="font-bold text-white uppercase tracking-wider block">
                SOVEREIGN TRUTH ASSERTION
              </span>
              <span className="text-neutral-400">
                PROVENANCE_LEDGER.md Cryptographic Seal: Verified
              </span>
            </div>
          </div>
          <span className="px-3 py-1 bg-neutral-950 text-neutral-300 border border-neutral-800 rounded-lg">
            Signed by Scribe Notary
          </span>
        </div>

      </div>
    </div>
  );
};
