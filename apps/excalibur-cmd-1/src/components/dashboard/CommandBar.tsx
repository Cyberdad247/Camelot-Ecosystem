import { useState } from 'react';
import { useEcosystemStore } from '../../state/useEcosystemStore';
import { Terminal, Send, RefreshCw } from 'lucide-react';
import { GlassPanel } from '../ui/GlassPanel';
import { TacticalButton } from '../ui/TacticalButton';
import { CommandInput } from '../ui/CommandInput';

export function CommandBar() {
  const [commandInput, setCommandInput] = useState('');
  const [lastOutput, setLastOutput] = useState<string | null>(
    '//FORGE_ECOSYSTEM_UI active. S26 Edge Enclave initialized under 4GB RAM ceiling.'
  );
  const [executing, setExecuting] = useState(false);
  const { setActiveView, setWakeWordActive, setLastVoiceTranscript } = useEcosystemStore();

  const executeCommand = (cmd: string) => {
    if (!cmd.trim()) return;

    setExecuting(true);
    const cleanedCmd = cmd.trim();

    setTimeout(() => {
      if (cleanedCmd === '🔄 //sync' || cleanedCmd.toLowerCase() === '//sync') {
        setLastOutput('[BRAINSYNC CRDT LEDGER] All nodes and MicroVMs synchronized to sovereign state.');
      } else if (cleanedCmd === '⚡ //evolve' || cleanedCmd.toLowerCase() === '//evolve') {
        setLastOutput('[DGM-H MUTATION LOOP] Triggered zero-copy neural layer optimization.');
      } else if (cleanedCmd === '🛠️ //forge' || cleanedCmd.toLowerCase() === '//forge') {
        setActiveView('guild');
        setLastOutput('[TASK DAG ORCHESTRATION] Swarm rapid development loop routed to Guild Board.');
      } else if (cleanedCmd.includes('Hey Alfred') || cleanedCmd.includes('alfred')) {
        setWakeWordActive(true);
        setLastVoiceTranscript(`Alfred: Executing order: "${cleanedCmd}"`);
        setLastOutput(`[ALFRED AUDIO DSP] Wake word captured: "${cleanedCmd}". Dispatching response.`);
      } else if (cleanedCmd.toLowerCase().includes('vault')) {
        setActiveView('vault');
        setLastOutput('[HOTSWAP VAULT] Navigated to Sovereign Cartridge Vault.');
      } else if (cleanedCmd.toLowerCase().includes('market')) {
        setActiveView('marketplace');
        setLastOutput('[MARKETPLACE] Opened Camelot Cartridge Marketplace.');
      } else if (cleanedCmd.toLowerCase().includes('knight')) {
        setActiveView('knights');
        setLastOutput('[KNIGHTS] Opened Round Table Cognitive OCEAN Customizer.');
      } else {
        setLastOutput(`[EXECUTED // ⚜️_SOVEREIGN_TRUTH]: Command "${cleanedCmd}" processed through Excalibur Zero-Trust Aegis.`);
      }
      setExecuting(false);
      setCommandInput('');
    }, 350);
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    executeCommand(commandInput);
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
            onClick={() => executeCommand('🔄 //sync')}
            className="hover:text-[#D4AF37] px-2 py-0.5 border border-[#4B0082] rounded bg-black/50 cursor-pointer min-h-[28px]"
          >
            //sync
          </button>
          <button
            type="button"
            onClick={() => executeCommand('⚡ //evolve')}
            className="hover:text-[#D4AF37] px-2 py-0.5 border border-[#4B0082] rounded bg-black/50 cursor-pointer min-h-[28px]"
          >
            //evolve
          </button>
          <button
            type="button"
            onClick={() => executeCommand('🛠️ //forge')}
            className="hover:text-[#D4AF37] px-2 py-0.5 border border-[#4B0082] rounded bg-black/50 cursor-pointer min-h-[28px]"
          >
            //forge
          </button>
        </div>
      </div>

      <form onSubmit={handleFormSubmit} className="flex gap-2">
        <div className="flex-1">
          <CommandInput
            value={commandInput}
            onChange={setCommandInput}
            onSubmit={executeCommand}
            placeholder="Type rune (e.g. 🔄 //sync, 🛠️ //forge, //STATUS, 'Hey Alfred')..."
          />
        </div>

        <TacticalButton
          id="execute-command-rune-btn"
          type="submit"
          disabled={executing}
          variant="gold"
          size="md"
          loading={executing}
          icon={executing ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
          className="shrink-0"
        >
          <span className="hidden sm:inline">DISPATCH</span>
        </TacticalButton>
      </form>

      {lastOutput && (
        <div className="p-2.5 bg-black/90 border border-[#4B0082]/60 rounded-md text-[11px] font-mono text-[#10B981] shadow-inner">
          {lastOutput}
        </div>
      )}
    </GlassPanel>
  );
}
