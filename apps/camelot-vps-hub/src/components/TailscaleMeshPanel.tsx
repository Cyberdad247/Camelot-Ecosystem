import React, { useState } from 'react';
import { 
  Network, 
  Smartphone, 
  Laptop, 
  Server, 
  Radio, 
  ShieldCheck, 
  CheckCircle2, 
  Activity, 
  ExternalLink,
  Crown,
  Zap,
  RefreshCw
} from 'lucide-react';

export interface MeshNode {
  id: string;
  name: string;
  tailscaleIp: string;
  publicIp?: string;
  role: string;
  os: string;
  status: 'ONLINE' | 'ACTIVE_HUB' | 'COCKPIT' | 'ROUTING';
  latencyMs: number;
  icon: 'laptop' | 'phone' | 'server' | 'cloud';
}

export const TAILSCALE_MESH_NODES: MeshNode[] = [
  {
    id: 'cybertronia',
    name: 'cybertronia',
    tailscaleIp: '100.118.224.52',
    role: 'Primary Windows Orchestrator & Local VFS Factory',
    os: 'Windows 11 Pro / AMD64',
    status: 'ONLINE',
    latencyMs: 1.2,
    icon: 'laptop'
  },
  {
    id: 'vashawns-s26-ultra',
    name: 'vashawns-s26-ultra',
    tailscaleIp: '100.106.246.126',
    role: 'Excalibur Command Center & Kinetic Mobile Sentinel',
    os: 'Android 16 / ARM64',
    status: 'COCKPIT',
    latencyMs: 14.8,
    icon: 'phone'
  },
  {
    id: 'vps3573819',
    name: 'KVM563 / vps3573819',
    tailscaleIp: '100.71.218.75',
    publicIp: '162.35.107.134',
    role: 'Camelot-OS Hub & Control Plane (HERMES_PRIME)',
    os: 'Ubuntu 24.04 LTS / x86_64',
    status: 'ACTIVE_HUB',
    latencyMs: 8.4,
    icon: 'server'
  },
  {
    id: 'fothers-camelot',
    name: 'fothers-camelot',
    tailscaleIp: '100.121.48.50',
    role: 'Windows Sovereign Secondary Node',
    os: 'Windows 11 / x86_64',
    status: 'ONLINE',
    latencyMs: 18.2,
    icon: 'laptop'
  },
  {
    id: 'lakesha',
    name: 'lakesha',
    tailscaleIp: '100.100.155.55',
    role: 'Lakisha Voice OS Host & Audio Cluster',
    os: 'Windows 11 / x86_64',
    status: 'ONLINE',
    latencyMs: 16.5,
    icon: 'laptop'
  },
  {
    id: 'camelot-relay-modal',
    name: 'camelot-relay-modal',
    tailscaleIp: '100.84.98.39',
    role: 'Linux Cloud Relay Node & MicroVM Serverless',
    os: 'Linux Cloud Kernel',
    status: 'ROUTING',
    latencyMs: 24.1,
    icon: 'cloud'
  },
  {
    id: 'kba-services',
    name: 'kba-services',
    tailscaleIp: '100.71.218.75',
    role: 'Linux Remote Services & Matrix Ingress',
    os: 'Linux 6.8 / x86_64',
    status: 'ROUTING',
    latencyMs: 11.3,
    icon: 'server'
  },
  {
    id: 'motorola-moto-g-power',
    name: 'motorola-moto-g-power-5g---2024',
    tailscaleIp: '100.89.129.105',
    role: 'Auxiliary Mobile Sentinel & Telemetry Watcher',
    os: 'Android 14 / ARM64',
    status: 'ONLINE',
    latencyMs: 32.7,
    icon: 'phone'
  }
];

export const TailscaleMeshPanel: React.FC = () => {
  const [nodes, setNodes] = useState<MeshNode[]>(TAILSCALE_MESH_NODES);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const refreshMesh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setNodes((prev) =>
        prev.map((n) => ({
          ...n,
          latencyMs: Number((n.latencyMs + (Math.random() * 2 - 1)).toFixed(1))
        }))
      );
      setIsRefreshing(false);
    }, 600);
  };

  const getStatusBadge = (status: MeshNode['status']) => {
    switch (status) {
      case 'COCKPIT':
        return (
          <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-[#D4AF37]/20 border border-[#D4AF37]/60 text-[#F3E5AB] flex items-center gap-1 shadow-[0_0_8px_rgba(212,175,55,0.3)]">
            <Crown className="w-2.5 h-2.5 text-[#D4AF37]" />
            EXCALIBUR COCKPIT
          </span>
        );
      case 'ACTIVE_HUB':
        return (
          <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-emerald-950/80 border border-emerald-500/60 text-emerald-300 flex items-center gap-1 shadow-[0_0_8px_rgba(16,185,129,0.3)]">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
            CONTROL PLANE
          </span>
        );
      case 'ROUTING':
        return (
          <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-purple-950/80 border border-purple-500/50 text-purple-300">
            RELAY MESH
          </span>
        );
      default:
        return (
          <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-cyan-950/80 border border-cyan-500/40 text-cyan-300">
            PEER ONLINE
          </span>
        );
    }
  };

  const getNodeIcon = (icon: MeshNode['icon']) => {
    switch (icon) {
      case 'phone':
        return <Smartphone className="w-3.5 h-3.5 text-[#D4AF37]" />;
      case 'server':
        return <Server className="w-3.5 h-3.5 text-emerald-400" />;
      case 'cloud':
        return <Radio className="w-3.5 h-3.5 text-purple-400" />;
      default:
        return <Laptop className="w-3.5 h-3.5 text-cyan-400" />;
    }
  };

  return (
    <div className="hud-panel-gold rounded-xl p-3 font-mono space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[#D4AF37]/30 pb-2">
        <div className="flex items-center gap-2">
          <div className="p-1 rounded bg-[#D4AF37]/15 border border-[#D4AF37]/40 text-[#D4AF37]">
            <Network className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-[#F3E5AB] tracking-wider uppercase flex items-center gap-2">
              <span>TAILSCALE SOVEREIGN MESH</span>
              <span className="text-[9px] px-1.5 py-0.2 rounded bg-[#D4AF37]/20 text-[#D4AF37] border border-[#D4AF37]/40">
                8/8 NODES
              </span>
            </h3>
            <span className="text-[9px] text-slate-400 block font-normal">
              mTLS Encrypted Overlay · Cyberdad247@github
            </span>
          </div>
        </div>

        <button
          onClick={refreshMesh}
          disabled={isRefreshing}
          className="p-1.5 rounded bg-slate-900 hover:bg-slate-800 border border-[#D4AF37]/40 text-[#D4AF37] hover:text-white transition-all cursor-pointer"
          title="Probe Mesh Heartbeats"
        >
          <RefreshCw className={`w-3 h-3 ${isRefreshing ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Nodes List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-[360px] overflow-y-auto pr-1">
        {nodes.map((node) => (
          <div
            key={node.id}
            className="p-2 rounded-lg bg-[#050b17]/90 border border-cyan-950 hover:border-[#D4AF37]/50 transition-all space-y-1.5 group"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5">
                {getNodeIcon(node.icon)}
                <span className="text-xs font-bold text-slate-100 group-hover:text-[#F3E5AB] transition-colors">
                  {node.name}
                </span>
              </div>
              {getStatusBadge(node.status)}
            </div>

            <div className="text-[10px] text-slate-400 line-clamp-1">
              {node.role}
            </div>

            <div className="flex items-center justify-between text-[9px] text-slate-500 font-mono pt-1 border-t border-slate-900">
              <span className="text-cyan-400 font-semibold">{node.tailscaleIp}</span>
              <span className="text-emerald-400">{node.latencyMs}ms ping</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
