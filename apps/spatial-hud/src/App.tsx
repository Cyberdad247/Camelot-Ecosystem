import React, { useState, useEffect } from 'react';
import { loadAllVfsFiles } from './data/vfsData';
import { KNIGHTS_ROSTER } from './data/knightsData';
import { VfsFile, ActiveTab, TerminalLog, Knight, ThemeMode } from './types';
import { HeaderHUD } from './components/HeaderHUD';
import { VfsExplorer } from './components/VfsExplorer';
import { InteractiveTerminal } from './components/InteractiveTerminal';
import { SwarmLatticeVisualizer } from './components/SwarmLatticeVisualizer';
import { KnightRosterView } from './components/KnightRosterView';
import { ContractSchemasView } from './components/ContractSchemasView';
import { ConstitutionalView } from './components/ConstitutionalView';
import { ConstitutionalGateModal } from './components/ConstitutionalGateModal';
import { HtmxCommandCenterView } from './components/HtmxCommandCenterView';
import { SpatialHolographicHUD } from './components/SpatialHolographicHUD';
import { CommandCenterView } from './components/CommandCenterView';
import { DigitalFactoryView } from './components/DigitalFactoryView';
import { MultiVoiceRouterDeck } from './components/MultiVoiceRouterDeck';
import { CartridgeMatrixView } from './components/CartridgeMatrixView';
import { ArthurianVSPGateway } from './components/ArthurianVSPGateway';
import { RoundTableDeck } from './components/RoundTableDeck';
import { AudioWorkbenchView } from './components/AudioWorkbenchView';
import { ShadowVmTestGauntlet } from './components/ShadowVmTestGauntlet';
import { multiVoiceRouter } from './services/multiVoiceRouter';

export function App() {
  const [allFiles, setAllFiles] = useState<VfsFile[]>([]);
  const [selectedFile, setSelectedFile] = useState<VfsFile | null>(null);
  const [activeTab, setActiveTab] = useState<ActiveTab>('gateway');
  const [theme, setTheme] = useState<ThemeMode>('dark');
  const [gateModalOpen, setGateModalOpen] = useState(false);
  const [gateActionPending, setGateActionPending] = useState<string | null>(null);

  // Initial rich terminal logs
  const [terminalLogs, setTerminalLogs] = useState<TerminalLog[]>([
    {
      id: 'log-1',
      timestamp: '00.000s',
      sender: 'ANYA_Ω',
      level: 'INFO',
      message: 'Ingress intercepted. APEE v7.0 Triage completed. Anya First Law enforced.',
      codeBlock: '{"status": "INGRESS_SCRUBBED", "entropy": 0.000, "hypervisor": "L7_GATE"}'
    },
    {
      id: 'log-2',
      timestamp: '00.024s',
      sender: 'MERLIN_Ω',
      level: 'SUCCESS',
      message: 'Master Ignition DAG compiled. VFS Master Scaffold vMAX crystals generated.',
      codeBlock: '@ctx|camelot-os.dev/ukg/v1000/vfs_scaffold @typ|Sovereign_VFS_Manifest id|OMNI_VFS_FORGE'
    },
    {
      id: 'log-3',
      timestamp: '00.048s',
      sender: 'SIR_CODEX',
      level: 'INFO',
      message: '20 Sovereign VFS nodes physicalized to local edge node (C:\\Users\\vizio\\CAMELOT_OS\\.agent\\). Isomorphic FileTree Law asserted.'
    },
    {
      id: 'log-4',
      timestamp: '00.062s',
      sender: 'SCRIBE',
      level: 'SUCCESS',
      message: 'PROVENANCE_LEDGER.md seal issued. Sentinel test public keys verified.',
      codeBlock: '⚜️_SOVEREIGN_TRUTH // [CPU: 120% OMNI_EXEC] [RAM: 7.4GB/8.0GB] [LATTICE: EXCALIBUR_V1000]'
    }
  ]);

  // Load files on mount
  useEffect(() => {
    const loaded = loadAllVfsFiles();
    setAllFiles(loaded);
    const preflight = loaded.find(f => f.name.includes('VFS Preflight')) || loaded.find(f => f.category === 'vfs-core') || loaded[0] || null;
    setSelectedFile(preflight);
  }, []);

  const addLog = (log: Omit<TerminalLog, 'id' | 'timestamp'>) => {
    const newLog: TerminalLog = {
      id: `log-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
      timestamp: new Date().toLocaleTimeString(),
      ...log,
    };
    setTerminalLogs(prev => [...prev, newLog]);
  };

  // Kinetic Command Processor
  const handleExecuteCommand = (command: string) => {
    // 1. Log Operator directive
    addLog({
      sender: 'OPERATOR',
      level: 'INFO',
      message: command,
    });

    const trimmed = command.trim();

    if (trimmed === '//boot') {
      setTimeout(() => {
        addLog({
          sender: 'ANYA_Ω',
          level: 'SUCCESS',
          message: 'APEX_ONLINE // Living Notebook Virtual Simulation Terminal awakened.',
          codeBlock: `[SYSTEM_IDENTITY]: CAMELOT-OS_OMEGA_TITAN_APEX
[OPERATOR]: VaShawn O. Head (Vizion) | Invisioned Marketing Inc.
[EDGE_NODE_ANCHOR]: Cleveland, Ohio, United States
[CORE_MANDATE]: "dreams don't come true visions do"`
        });
        addLog({
          sender: 'MERLIN_Ω',
          level: 'SUCCESS',
          message: '25-Knight Roster armed. Sub-agent dispatching pipeline receptive.'
        });
      }, 300);
    } else if (trimmed === '//nano-swarm expand') {
      setTimeout(() => {
        addLog({
          sender: 'MERLIN_Ω',
          level: 'INFO',
          message: 'Unpacking VFS_MASTER_SCAFFOLD_vMAX.yaml crystal manifest...'
        });
        setTimeout(() => {
          addLog({
            sender: 'SIR_CODEX',
            level: 'SUCCESS',
            message: 'All 20 sovereign VFS manifests verified and physicalized in /.agent/ directory.',
            codeBlock: `• VFS Preflight.md
• agents.md
• skills.md
• harnesses.md
• mcp.md
• Merlin.md
• Anya.md
• knight roster.md
• worldtree.md
• Artifacts.md
• protocols.md
• workflows.md
• symbollect.md
• camelot-os max version.md
• digitalfactory.md
• Inspira.md
• HiveIDE.md
• Blueprint-os.md
• merlinss oftware agency.md
• kickbox audio.md`
          });
        }, 500);
      }, 200);
    } else if (trimmed === '//sync') {
      setTimeout(() => {
        addLog({
          sender: 'LADY_MNEMOSYNE',
          level: 'SUCCESS',
          message: 'CRDT Ledger synchronization complete with NotebookLM Worldtree Cloudbrain. Δ_drift = 0.000.'
        });
      }, 400);
    } else if (trimmed === '//shield') {
      setTimeout(() => {
        addLog({
          sender: 'GIDEON',
          level: 'SUCCESS',
          message: 'Aegis Zero-Trust isolation perimeter engaged. Kyber-768 quantum mTLS handshake active.',
          codeBlock: 'CIPHER: KYBER-768-POST-QUANTUM | ENCLAVE: ISOLATED'
        });
      }, 300);
    } else if (trimmed === '//gate') {
      setGateActionPending('MANUAL_GATE_TRIGGER');
      setGateModalOpen(true);
    } else if (trimmed === '//rezero') {
      setTimeout(() => {
        addLog({
          sender: 'ANYA_Ω',
          level: 'SUCCESS',
          message: 'Sir Syntax auto-repair executed. AST trees rezeroed to canonical baseline.'
        });
      }, 400);
    } else if (trimmed === '//deploy') {
      setTimeout(() => {
        addLog({
          sender: 'MERLIN_Ω',
          level: 'SUCCESS',
          message: 'Engineering Cartridge compiled into stateless-to-committed bundle.',
          codeBlock: 'TARGET: Vercel Edge + Render/Tailscale mTLS | TENANT: info@kickboxaudio.com\nSEAL: ⚜️_SOVEREIGN_TRUTH'
        });
      }, 400);
    } else if (trimmed === '//GO_LIVE' || trimmed === '//go_live') {
      setTimeout(() => {
        addLog({
          sender: 'MERLIN_Ω',
          level: 'SUCCESS',
          message: 'HTMX Command Center deployed to systemd unit [camelot-htmx.service].',
          codeBlock: `SYSTEMD UNIT: /etc/systemd/system/camelot-htmx.service
PORT: :8080 (Docker-Free Go Binary)
SSE STREAM: /stream [200 OK text/event-stream]
THEME: Obsidian/Gold/Purple`
        });
      }, 300);
    } else if (trimmed === '//DISPATCH' || trimmed === '//dispatch') {
      setTimeout(() => {
        addLog({
          sender: 'SIR_CODEX',
          level: 'SUCCESS',
          message: 'Dispatched native Go + HTMX single-page package to /opt/camelot/htmx-center/.',
          codeBlock: `• /opt/camelot/htmx-center/main.go
• /opt/camelot/htmx-center/static/index.html
• /opt/camelot/htmx-center/static/css/style.css
• /opt/camelot/htmx-center/deploy/camelot-htmx.service
• /opt/camelot/htmx-center/deploy/install.sh`
        });
      }, 300);
    } else if (trimmed === '//htmx') {
      setActiveTab('htmx');
      addLog({
        sender: 'SYSTEM',
        level: 'INFO',
        message: 'Switched to Native Go + HTMX Command Center deck.'
      });
    } else if (trimmed === '//spatial' || trimmed === '//hud' || trimmed.startsWith('//deploy:sir_boris')) {
      setActiveTab('spatial-hud');
      addLog({
        sender: 'SIR_CODEX',
        level: 'SUCCESS',
        message: 'Scaffolded Holographic Spatial HUD dashboard via CopilotKit & R3F (Sir Boris Vanguard).',
        codeBlock: `KNIGHT: Sir Boris (Chaos & Resilience Officer)
TOOLCHAIN: Three.js / React Three Fiber + Drei + Motion + CopilotKit (AG-UI)
GEOMETRY: 12-Column Grid + Perspective Floor + Concentric Rings
PALETTE: Obsidian Void (#050507), Cyan (#00E5FF), Violet (#9D4EDD), Magenta (#FF007F), Gold (#E5B842)
STATUS: WebGPU/WebGL 60 FPS NOMINAL`
      });
    } else if (trimmed === '//knights') {
      setActiveTab('knights');
      addLog({
        sender: 'SYSTEM',
        level: 'INFO',
        message: 'Switched to 25-Knight Sovereign Execution Swarm deck.'
      });
    } else if (trimmed === '//audit') {
      setActiveTab('constitution');
      addLog({
        sender: 'GIDEON',
        level: 'INFO',
        message: 'Constitutional 4-Pillar verification engaged.'
      });
    } else {
      // General semantic directive evaluation
      setTimeout(() => {
        addLog({
          sender: 'ANYA_Ω',
          level: 'INFO',
          message: `Directive intercepted: "${trimmed}". Processing through APEE v7.0 engine.`
        });
        setTimeout(() => {
          addLog({
            sender: 'MERLIN_Ω',
            level: 'SUCCESS',
            message: `Task DAG generated for: "${trimmed}". Dispatched to Bio-Kinetic microVM workers.`
          });
        }, 500);
      }, 300);
    }
  };

  const handleKineticTrigger = (trigger: string) => {
    multiVoiceRouter.playCyberSfx('lock');
    if (trigger === '//chaos:inject' || trigger.includes('chaos')) {
      multiVoiceRouter.playCyberSfx('chaos');
      multiVoiceRouter.speakAsKnight('boris', 'Chaos pulse injected into AST matrix!');
    } else if (trigger === '//rezero') {
      multiVoiceRouter.playCyberSfx('rezero');
      multiVoiceRouter.speakAsKnight('anya', 'Rezeroing baseline. All nodes restored to 100% capacity.');
    } else if (trigger === '//boot') {
      multiVoiceRouter.playCyberSfx('boot');
      multiVoiceRouter.speakAsKnight('arthur', 'Camelot-OS Sovereign Kernel online. Round table knights standing by.');
    }
    setActiveTab('terminal');
    handleExecuteCommand(trigger);
  };

  const handleDispatchKnightTask = (knight: Knight, taskName: string) => {
    addLog({
      sender: 'MERLIN_Ω',
      level: 'INFO',
      message: `Direct DAG dispatch to [${knight.name}] (${knight.role}): ${taskName}`,
    });
    setTimeout(() => {
      addLog({
        sender: 'SCRIBE',
        level: 'SUCCESS',
        message: `Task ${taskName} executed successfully by ${knight.name}. Evidence envelope sealed.`,
        codeBlock: `KNIGHT: ${knight.name} | DIVISION: ${knight.division} | LOAD: ${knight.load}%\nVERDICT: GIDEON_PASS`
      });
    }, 1000);
  };

  const handleConfirmGate = () => {
    setGateModalOpen(false);
    addLog({
      sender: 'OPERATOR',
      level: 'SUCCESS',
      message: '[y] HITL Iron Gate Authorized by Operator VaShawn O. Head.',
    });
    addLog({
      sender: 'GIDEON',
      level: 'SUCCESS',
      message: 'Gate cleared. Proceeding with sovereign execution directive.',
    });
  };

  const handleCancelGate = () => {
    setGateModalOpen(false);
    addLog({
      sender: 'OPERATOR',
      level: 'WARN',
      message: '[N] Directive rejected by Operator.',
    });
    addLog({
      sender: 'GIDEON',
      level: 'DANGER',
      message: 'Action aborted. System returned to standby baseline.',
    });
  };

  const contractFiles = allFiles.filter(f => f.category === 'contracts');
  const goldenReceiptFiles = allFiles.filter(f => f.category === 'golden-receipts');
  const isDark = theme === 'dark';

  return (
    <div className={`flex flex-col h-screen w-screen ${isDark ? 'bg-neutral-950 text-neutral-100 dark' : 'bg-slate-100 text-slate-900'} overflow-hidden font-sans selection:bg-amber-500/30 selection:text-amber-200 transition-colors duration-200`}>
      
      {/* Top Telemetry HUD */}
      <HeaderHUD
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onKineticTrigger={handleKineticTrigger}
        vfsFileCount={allFiles.filter(f => f.category === 'vfs-core').length}
        theme={theme}
        setTheme={setTheme}
      />

      {/* Main Workspace Area */}
      <div className="flex-1 flex overflow-hidden">
        {activeTab === 'gateway' && (
          <ArthurianVSPGateway
            onNavigate={(tab) => setActiveTab(tab)}
            onKineticTrigger={handleKineticTrigger}
            theme={theme}
          />
        )}

        {activeTab === 'round-table' && (
          <div className="flex-1 p-4 sm:p-6 overflow-y-auto">
            <RoundTableDeck
              theme={theme}
              onKineticTrigger={handleKineticTrigger}
            />
          </div>
        )}

        {activeTab === 'audio-workbench' && (
          <div className="flex-1 p-4 sm:p-6 overflow-y-auto">
            <AudioWorkbenchView
              theme={theme}
              onKineticTrigger={handleKineticTrigger}
            />
          </div>
        )}

        {activeTab === 'shadow-gauntlet' && (
          <div className="flex-1 p-4 sm:p-6 overflow-y-auto">
            <ShadowVmTestGauntlet
              theme={theme}
              onKineticTrigger={handleKineticTrigger}
            />
          </div>
        )}

        {activeTab === 'command-center' && (
          <CommandCenterView
            theme={theme}
            onKineticTrigger={handleKineticTrigger}
          />
        )}

        {activeTab === 'cartridge-matrix' && (
          <CartridgeMatrixView
            theme={theme}
            onKineticTrigger={handleKineticTrigger}
            onSwitchTab={(tab) => setActiveTab(tab as ActiveTab)}
          />
        )}

        {activeTab === 'digital-factory' && (
          <DigitalFactoryView
            theme={theme}
            onKineticTrigger={handleKineticTrigger}
          />
        )}

        {activeTab === 'multivoice' && (
          <div className="flex-1 p-6 overflow-y-auto">
            <MultiVoiceRouterDeck
              theme={theme}
              onExecuteIntent={handleKineticTrigger}
            />
          </div>
        )}

        {activeTab === 'vfs' && (
          <VfsExplorer
            files={allFiles}
            selectedFile={selectedFile}
            onSelectFile={setSelectedFile}
            onKineticTrigger={handleKineticTrigger}
          />
        )}

        {activeTab === 'htmx' && (
          <HtmxCommandCenterView onKineticTrigger={handleKineticTrigger} />
        )}

        {activeTab === 'spatial-hud' && (
          <SpatialHolographicHUD 
            onKineticTrigger={handleKineticTrigger} 
            theme={theme}
          />
        )}

        {activeTab === 'terminal' && (
          <InteractiveTerminal
            logs={terminalLogs}
            onExecuteCommand={handleExecuteCommand}
            onClearLogs={() => setTerminalLogs([])}
          />
        )}

        {activeTab === 'lattice' && (
          <SwarmLatticeVisualizer
            onSelectKnight={(knight) => {
              addLog({
                sender: 'SYSTEM',
                level: 'INFO',
                message: `Inspected node telemetry: [${knight.name}] - ${knight.role}`,
              });
            }}
          />
        )}

        {activeTab === 'knights' && (
          <KnightRosterView onDispatchTask={handleDispatchKnightTask} />
        )}

        {activeTab === 'contracts' && (
          <ContractSchemasView
            contracts={contractFiles}
            goldenReceipts={goldenReceiptFiles}
          />
        )}

        {activeTab === 'constitution' && (
          <ConstitutionalView />
        )}
      </div>

      {/* HITL Gate Confirmation Modal */}
      <ConstitutionalGateModal
        isOpen={gateModalOpen}
        onConfirm={handleConfirmGate}
        onCancel={handleCancelGate}
        title="HITL Iron Gate Authorization Required"
        description="A high-risk mutation or kinetic sovereign directive requires explicit [y/N] Human-In-The-Loop confirmation from the Operator."
      />

    </div>
  );
}

export default App;
