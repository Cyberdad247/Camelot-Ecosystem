import React from 'react';
import { NavLink } from 'react-router-dom';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard, BrainCircuit, FlaskConical, Map, LayoutGrid,
  Globe, ChevronDown, Sword, Wifi, WifiOff, ShieldCheck,
} from 'lucide-react';
import { CARTRIDGES } from '@/features/cartridges/registry';
import { useAnyaSocket } from '@/features/brain/useAnyaSocket';

const navLinkBase =
  'flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition-colors duration-150';
const navActive =
  'bg-fuchsia-950/60 text-fuchsia-200 font-semibold border border-fuchsia-500/30';
const navIdle =
  'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50';

function SideLink({
  to, icon: Icon, label, end = false,
}: { to: string; icon: React.ElementType; label: string; end?: boolean }) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) => cn(navLinkBase, isActive ? navActive : navIdle)}
    >
      <Icon className="h-4 w-4 shrink-0" />
      <span>{label}</span>
    </NavLink>
  );
}

interface SidebarProps {
  collapsed: boolean;
}

export default function Sidebar({ collapsed }: SidebarProps) {
  const { isConnected } = useAnyaSocket();

  return (
    <aside
      className={cn(
        'flex h-full flex-col border-r border-slate-800/60 bg-[#07030d] transition-all duration-200',
        collapsed ? 'w-0 overflow-hidden' : 'w-60',
      )}
    >
      {/* Logo */}
      <div className="flex items-center gap-2 border-b border-slate-800/60 px-4 py-3.5">
        <Sword className="h-5 w-5 shrink-0 text-fuchsia-400" />
        <div className="min-w-0">
          <p className="text-xs font-black uppercase tracking-[0.2em] text-fuchsia-300">Camelot</p>
          <p className="text-[10px] text-slate-500 tracking-widest">APEX OS v400</p>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto px-2 py-3 space-y-0.5">
        {/* Core */}
        <SideLink to="/" icon={LayoutDashboard} label="System Hub" end />
        <SideLink to="/alex" icon={BrainCircuit} label="SIR_ALEX — Tasks" />
        <SideLink to="/research" icon={FlaskConical} label="Research Dept." />

        {/* Cartridges */}
        <div className="pt-3 pb-1 px-3">
          <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-600 flex items-center gap-1">
            <ChevronDown className="h-3 w-3" /> Cartridges
          </p>
        </div>
        {CARTRIDGES.map((c) => {
          const Icon = c.icon;
          return (
            <NavLink
              key={c.id}
              to={`/cartridge/${c.slug}`}
              className={({ isActive }) =>
                cn(navLinkBase, isActive ? navActive : navIdle)
              }
            >
              <Icon className={cn('h-4 w-4 shrink-0', c.textClass)} />
              <span>{c.label}</span>
              <span className="ml-auto text-[10px] text-slate-600">{c.knight}</span>
            </NavLink>
          );
        })}

        {/* System */}
        <div className="pt-3 pb-1 px-3">
          <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-600 flex items-center gap-1">
            <ChevronDown className="h-3 w-3" /> System
          </p>
        </div>
        <SideLink to="/openviking" icon={Map} label="Viking Map" />
        <SideLink to="/defense-grid" icon={ShieldCheck} label="Defense Grid" />
        <SideLink to="/swarm" icon={LayoutGrid} label="Swarm Monitor" />
        <SideLink to="/anyas-link" icon={Globe} label="Anya's Link" />
      </nav>

      {/* Status footer */}
      <div className="border-t border-slate-800/60 px-4 py-2.5 flex items-center gap-2">
        {isConnected
          ? <Wifi className="h-3.5 w-3.5 text-emerald-400" />
          : <WifiOff className="h-3.5 w-3.5 text-red-500" />
        }
        <span className="text-[10px] text-slate-500">
          {isConnected ? 'Bifrost LIVE' : 'Bifrost DARK'}
        </span>
      </div>
    </aside>
  );
}
