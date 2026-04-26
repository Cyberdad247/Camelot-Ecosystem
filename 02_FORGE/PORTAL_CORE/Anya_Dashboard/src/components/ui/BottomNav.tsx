import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutGrid, Globe, Brain, Map } from 'lucide-react';

export default function BottomNav() {
  const navItems = [
    { path: '/anyas-link', icon: Globe, label: 'Link' },
    { path: '/brain', icon: Brain, label: 'Brain' },
    { path: '/openviking', icon: Map, label: 'Viking' },
    { path: '/swarm', icon: LayoutGrid, label: 'Swarm' }, 
  ];

  return (
    <nav className="z-50 shrink-0 border-t border-slate-800 bg-slate-950/90 pb-[env(safe-area-inset-bottom)] backdrop-blur-lg">
      <div className="flex justify-around items-center h-16">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex flex-col items-center justify-center w-full h-full gap-1 transition-colors ${
                isActive ? 'text-blue-500' : 'text-slate-500 hover:text-slate-300'
              }`
            }
          >
            <item.icon size={24} />
            <span className="text-[10px] font-medium">{item.label}</span>
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
