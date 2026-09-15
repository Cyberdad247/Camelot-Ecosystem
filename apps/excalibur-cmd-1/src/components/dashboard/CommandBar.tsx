import { useState } from 'react';
import { useEcosystemStore } from '../../state/useEcosystemStore';
import { Terminal, Send, Sparkles, Shield, RefreshCw } from 'lucide-react';
import { GlassPanel } from '../ui/GlassPanel';

export function CommandBar() {
  const [commandInput, setCommandInput] = useState('');
  const [lastOutput, setLastOutput] = useState<string | null>(
    '//FORGE_ECOSYSTEM_UI active. S26 Edge Enclave initialized under 4GB RAM ceiling.'
  );
  const [executing, setExecuting] = useState(false);
  const { setActiveView, setWakeWordActive, setLastVoiceTranscript } = useEcosystemStore();

  const handleExecute = (e: React.FormEvent) => {
    e.preventDefault();
    if (!commandInput.trim()) return;

    setExecuting(true);
    const cmd = commandInput.trim();

    setTimeout(() => {
      if (cmd === '🔄 //sync' || cmd.toLowerCase() === '//sync') {
        setLastOutput('[BRAINSYNC CRDT LEDGER] All nodes and MicroVMs synchronized to sovereign state.');
      } else if (cmd === '⚡ //evolve' || cmd.toLowerCase() === '//evolve') {
        setLastOutput('[DGM-H MUTATION LOOP] Triggered zero-copy neural layer optimization.');
      } else if (cmd === '🛠️ //forge' || cmd.toLowerCase() === '//forge') {
        setActiveView('guild');
        setLastOutput('[TASK DAG ORCHESTRATION] Swarm rapid development loop routed to Guild Board.');
      } else if (cmd.includes('Hey Alfred') || cmd.includes('alfred')) {
        setWakeWordActive(true);
        setLastVoiceTranscript(`Alfred: Executing order: "${cmd}"`);
        setLastOutput(`[ALFRED AUDIO DSP] Wake word captured: "${cmd}". Dispatching response.`);
      } else if (cmd.toLowerCase().includes('vault')) {
        setActiveView('vault');
        setLastOutput('[HOTSWAP VAULT] Navigated to Sovereign Cartridge Vault.');
      } else if (cmd.toLowerCase().includes('market')) {
        setActiveView('marketplace');
        setLastOutput('[MARKETPLACE] Opened Camelot Cartridge Marketplace.');
      } else if (cmd.toLowerCase().includes('knight')) {
        setActiveView('knights');
        setLastOutput('[KNIGHTS] Opened Round Table Cognitive OCEAN Customizer.');
      } else {
        setLastOutput(`[EXECUTED // ⚜️_SOVEREIGN_TRUTH]: Command "${cmd}" processed through Excalibur Zero-Trust Aegis.`);
      }
      setExecuting(false);
      setCommandInput('');
    }, 400);
  };

  return (
    <GlassPanel glow="gold" density="compact" className="space-y-2.5">
      <div className="flex items-center justify-between text-xs font-['Cinzel'] font-bold text-[#D4AF37]">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-[#D4AF37]" />
          <span>SOVEREIGN COMMAND RUNES // EXCALIBUR EXECUTION CLI</span>
        </div>
        <div className="flex items-center gap-1.5 text-[10px] font-mono text-purple-300">
          <button
            type="button"
            onClick={() => setCommandInput('🔄 //sync')}
            className="hover:text-[#D4AF37] px-1.5 py-0.5 border border-[#4B0082] rounded bg-black/50"
          >
            //sync
          </button>
          <button
            type="button"
            onClick={() => setCommandInput('⚡ //evolve')}
            className="hover:text-[#D4AF37] px-1.5 py-0.5 border border-[#4B0082] rounded bg-black/50"
          >
            //evolve
          </button>
          <button
            type="button"
            onClick={() => setCommandInput('🛠️ //forge')}
            className="hover:text-[#D4AF37] px-1.5 py-0.5 border border-[#4B0082] rounded bg-black/50"
          >
            //forge
          </button>
        </div>
      </div>

      <form onSubmit={handleExecute} className="flex gap-2">
        <div className="relative flex-1">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-xs font-mono text-[#D4AF37] select-none">
            &gt;
          </span>
          <input
            type="text"
            value={commandInput}
            onChange={(e) => setCommandInput(e.target.value)}
            placeholder="Type rune (e.g. 🔄 //sync, 🛠️ //forge, 'Hey Alfred status', 'vault')..."
            className="w-full pl-7 pr-3 py-2 bg-black/80 border border-[#4B0082] focus:border-[#D4AF37] text-xs font-['JetBrains_Mono'] text-[#F1EFF4] rounded-lg focus:outline-none"
          />
        </div>

        <button
          id="execute-command-rune-btn"
          type="submit"
          disabled={executing}
          className="px-4 py-2 bg-[#D4AF37] hover:bg-[#F1EFF4] text-black text-xs font-['Cinzel'] font-bold rounded-lg transition-all flex items-center gap-1.5 shadow-[0_0_15px_rgba(212,175,55,0.3)] shrink-0 min-h-[38px]"
        >
          {executing ? (
            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <>
              <Send className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">DISPATCH</span>
            </>
          )}
        </button>
      </form>

      {lastOutput && (
        <div className="p-2 bg-black/90 border border-purple-900/60 rounded text-[11px] font-['JetBrains_Mono'] text-emerald-400">
          {lastOutput}
        </div>
      )}
    </GlassPanel>
  );
}
