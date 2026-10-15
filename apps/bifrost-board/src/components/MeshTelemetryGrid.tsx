import React, { useState } from 'react';
import { 
  Network, 
  Radio, 
  ShieldCheck, 
  Cpu, 
  Server, 
  Smartphone, 
  Laptop, 
  RefreshCw, 
  Lock, 
  Activity,
  CheckCircle2,
  Clock
} from 'lucide-react';

export interface MeshNodeItem {
  ip: string;
  hostname: string;
  knight: string;
  role: string;
  online: boolean;
  latencyRttMs: number | null;
  warpKeypass: 'ACTIVE' | 'PENDING';
  tier: 'NODE' | 'SERVER';
  maxRamMb: number;
  activeRamMb: number;
  ramGovernance: 'PASS' | 'VIOLATION';
}

const INITIAL_NODES: MeshNodeItem[] = [
  {
    ip: '100.118.224.52',
    hostname: 'Cybertronia',
    knight: 'SIR_HELIOS',
    role: 'Primary Orchestrator & Local Root',
    online: true,
    latencyRttMs: 0.15,
    warpKeypass: 'ACTIVE',
    tier: 'NODE',
    maxRamMb: 4096,
    activeRamMb: 61.4,
    ramGovernance: 'PASS',
  },
  {
    ip: '100.106.246.126',
    hostname: "VaShawn's S26 Ultra",
    knight: 'SIR_HELIO',
    role: 'Excalibur Mobile Command (AMOLED 120Hz)',
    online: true,
    latencyRttMs: 53.0,
    warpKeypass: 'ACTIVE',
    tier: 'NODE',
    maxRamMb: 4096,
    activeRamMb: 65.0,
    ramGovernance: 'PASS',
  },
  {
    ip: '100.110.180.18',
    hostname: 'vps-camelot-hub',
    knight: 'HERMES_PRIME',
    role: 'Camelot-OS Hub & Control Plane',
    online: true,
    latencyRttMs: 23.0,
    warpKeypass: 'ACTIVE',
    tier: 'SERVER',
    maxRamMb: 8192,
    activeRamMb: 240.0,
    ramGovernance: 'PASS',
  },
  {
    ip: '100.121.48.50',
    hostname: 'Camelot-97NCQP3',
    knight: 'SIR_CODEX',
    role: 'Windows Sovereign Secondary Node',
    online: false,
    latencyRttMs: null,
    warpKeypass: 'ACTIVE',
    tier: 'NODE',
    maxRamMb: 4096,
    activeRamMb: 65.0,
    ramGovernance: 'PASS',
  },
  {
    ip: '100.100.155.55',
    hostname: 'Lakesha',
    knight: 'LAKESHA_VOICE',
    role: 'Lakisha Voice OS Secondary Node',
    online: false,
    latencyRttMs: null,
    warpKeypass: 'PENDING',
    tier: 'NODE',
    maxRamMb: 4096,
    activeRamMb: 65.0,
    ramGovernance: 'PASS',
  },
  {
    ip: '100.113.101.43',
    hostname: 'MacBook Pro (3)',
    knight: 'SIR_BORIS',
    role: 'Crucible & UI Architecture Node',
    online: false,
    latencyRttMs: null,
    warpKeypass: 'ACTIVE',
    tier: 'NODE',
    maxRamMb: 4096,
    activeRamMb: 65.0,
    ramGovernance: 'PASS',
  },
  {
    ip: '100.89.129.105',
    hostname: 'moto g power 5G - 2024',
    knight: 'AUX_SENTINEL',
    role: 'Auxiliary Mobile Sentinel',
    online: false,
    latencyRttMs: null,
    warpKeypass: 'PENDING',
    tier: 'NODE',
    maxRamMb: 4096,
    activeRamMb: 65.0,
    ramGovernance: 'PASS',
  },
];

export default function MeshTelemetryGrid() {
  const [nodes, setNodes] = useState<MeshNodeItem[]>(INITIAL_NODES);
  const [isProbing, setIsProbing] = useState<boolean>(false);
  const [lastProbed, setLastProbed] = useState<string>('Just now');

  const onlineCount = nodes.filter((n) => n.online).length;

  const handleProbeMesh = () => {
    setIsProbing(true);
    setTimeout(() => {
      // Simulate live RTT jitter
      setNodes((prev) =>
        prev.map((n) => {
          if (!n.online) return n;
          const jitter = Math.round((Math.random() * 6 - 3) * 10) / 10;
          return {
            ...n,
            latencyRttMs: n.latencyRttMs ? Math.max(0.1, Math.round((n.latencyRttMs + jitter) * 10) / 10) : n.latencyRttMs,
          };
        })
      );
      setIsProbing(false);
      setLastProbed(new Date().toLocaleTimeString());
    }, 450);
  };

  const getNodeIcon = (hostname: string, tier: string) => {
    if (tier === 'SERVER') return <Server className="h-4 w-4 text-camelot-violet" />;
    if (hostname.toLowerCase().includes('s26') || hostname.toLowerCase().includes('moto')) {
      return <Smartphone className="h-4 w-4 text-camelot-gold" />;
    }
    if (hostname.toLowerCase().includes('macbook')) {
      return <Laptop className="h-4 w-4 text-camelot-cyan" />;
    }
    return <Network className="h-4 w-4 text-green-400" />;
  };

  return (
    <div className="border border-camelot-gold/30 bg-obsidian-smoke/70 rounded-lg p-5 backdrop-blur shadow-2xl space-y-4">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between border-b border-gray-800 pb-3 gap-3">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-camelot-cyan/10 border border-camelot-cyan/40 text-camelot-cyan">
            <Radio className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold tracking-wider text-camelot-gold uppercase">
                Fleet Mesh & Warp-Gate Cockpit
              </h2>
              <span className="px-2 py-0.5 text-[10px] font-mono bg-emerald-950/60 text-emerald-400 border border-emerald-500/40 rounded">
                {onlineCount} / {nodes.length} ONLINE
              </span>
            </div>
            <p className="text-xs text-gray-400 font-mono">
              Tailscale WireGuard Mesh • Global Law 03 Enforced • Updated: <span className="text-camelot-cyan">{lastProbed}</span>
            </p>
          </div>
        </div>

        {/* Action Button */}
        <button
          onClick={handleProbeMesh}
          disabled={isProbing}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-black/60 hover:bg-black border border-camelot-cyan/40 hover:border-camelot-cyan text-camelot-cyan rounded font-mono text-xs transition-all shadow"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isProbing ? 'animate-spin' : ''}`} />
          <span>{isProbing ? 'PROBING...' : 'PROBE MESH'}</span>
        </button>
      </div>

      {/* Node Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {nodes.map((node) => (
          <div
            key={node.ip}
            className={`p-3 rounded border font-mono text-xs space-y-2 transition-all ${
              node.online
                ? 'bg-black/50 border-camelot-gold/30 hover:border-camelot-gold/60'
                : 'bg-black/30 border-gray-800/80 opacity-70'
            }`}
          >
            {/* Top row: Hostname & Online Badge */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {getNodeIcon(node.hostname, node.tier)}
                <span className="font-bold text-gray-200 truncate max-w-[130px]" title={node.hostname}>
                  {node.hostname}
                </span>
              </div>
              <span
                className={`text-[9px] font-bold px-1.5 py-0.5 rounded flex items-center gap-1 ${
                  node.online
                    ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-500/40'
                    : 'bg-gray-900 text-gray-500 border border-gray-700'
                }`}
              >
                <span className={`w-1.5 h-1.5 rounded-full ${node.online ? 'bg-emerald-400 animate-pulse' : 'bg-gray-600'}`} />
                {node.online ? 'ONLINE' : 'STANDBY'}
              </span>
            </div>

            {/* IP and Knight */}
            <div className="flex justify-between items-center text-[11px] text-gray-400 border-b border-gray-800/60 pb-1.5">
              <span className="text-camelot-cyan select-all">{node.ip}</span>
              <span className="text-camelot-violet font-semibold">{node.knight}</span>
            </div>

            {/* Metrics */}
            <div className="grid grid-cols-2 gap-2 text-[10px]">
              <div>
                <span className="text-gray-500 block text-[9px]">RTT LATENCY</span>
                <span className={`font-bold ${node.latencyRttMs !== null ? 'text-green-400' : 'text-gray-600'}`}>
                  {node.latencyRttMs !== null ? `${node.latencyRttMs} ms` : '—'}
                </span>
              </div>
              <div>
                <span className="text-gray-500 block text-[9px]">WARP KEYPASS</span>
                <span className={`font-bold flex items-center gap-1 ${node.warpKeypass === 'ACTIVE' ? 'text-emerald-400' : 'text-amber-400'}`}>
                  <Lock className="h-2.5 w-2.5" />
                  {node.warpKeypass}
                </span>
              </div>
            </div>

            {/* RAM Governance */}
            <div className="flex justify-between items-center pt-1 border-t border-gray-800/60 text-[10px]">
              <span className="text-gray-500">
                {node.tier === 'SERVER' ? 'SERVER (8GB CAP)' : 'NODE (4GB CAP)'}
              </span>
              <span className="text-green-400 font-bold flex items-center gap-1">
                <CheckCircle2 className="h-3 w-3" />
                {node.activeRamMb} MB / {node.maxRamMb} MB
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
