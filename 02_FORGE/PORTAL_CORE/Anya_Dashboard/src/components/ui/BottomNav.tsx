import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, BrainCircuit, FlaskConical, Zap, ShieldCheck, Settings2 } from 'lucide-react';

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Hub', end: true },
  { path: '/alex', icon: BrainCircuit, label: 'Alex' },
  { path: '/research', icon: FlaskConical, label: 'Research' },
  { path: '/dev', icon: Settings2, label: 'Dev' },
  { path: '/defense-grid', icon: ShieldCheck, label: 'Defense' },
  { path: '/cartridge/cognitive', icon: Zap, label: 'Cartridges' },
];

export default function BottomNav() {
  return (
    <nav className="z-50 shrink-0 border-t border-slate-800 bg-slate-950/95 pb-[env(safe-area-inset-bottom)] backdrop-blur-lg">
      <div className="flex justify-around items-center h-14">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.end}
            className={({ isActive }) =>
              `flex flex-col items-center justify-center w-full h-full gap-1 transition-colors ${
                isActive ? 'text-fuchsia-400' : 'text-slate-500 hover:text-slate-300'
              }`
            }
          >
            <item.icon size={20} />
            <span className="text-[10px] font-semibold">{item.label}</span>
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
