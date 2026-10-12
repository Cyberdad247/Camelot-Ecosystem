import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  Compass,
  Layers,
  Box,
  Cpu,
  Radio,
  Sparkles,
  Globe,
  Network,
  FileCode,
  Terminal as TerminalIcon,
  Users,
  ShieldCheck,
  Scale,
  LucideIcon,
  ChevronDown,
  LayoutGrid,
  Search,
  Check,
  Headphones
} from 'lucide-react';
import { ActiveTab, ThemeMode } from '../types';

export interface NavItem {
  id: ActiveTab;
  label: string;
  shortLabel?: string;
  icon: LucideIcon;
  badge?: string;
  category: 'gateway' | 'core' | 'intelligence' | 'governance' | 'dev';
  description: string;
  accentColor: string;
  darkActiveStyles: {
    border: string;
    text: string;
    bg: string;
    glow: string;
    badgeBg: string;
    badgeText: string;
    badgeBorder: string;
  };
  lightActiveStyles: {
    border: string;
    text: string;
    bg: string;
    badgeBg: string;
    badgeText: string;
    badgeBorder: string;
  };
}

export const NAV_ITEMS: NavItem[] = [
  {
    id: 'gateway',
    label: 'VSP Gateway',
    shortLabel: 'Gateway',
    icon: Compass,
    badge: 'ZERO-UI',
    category: 'gateway',
    description: 'Arthurian Cyber Citadel & Zero-UI Neurosymbolic Router',
    accentColor: '#00E5FF',
    darkActiveStyles: {
      border: 'border-cyan-400',
      text: 'text-cyan-300',
      bg: 'bg-cyan-950/80',
      glow: 'shadow-[0_0_20px_rgba(0,229,255,0.3)]',
      badgeBg: 'bg-cyan-500/25',
      badgeText: 'text-cyan-200',
      badgeBorder: 'border-cyan-400/60'
    },
    lightActiveStyles: {
      border: 'border-cyan-600',
      text: 'text-cyan-900',
      bg: 'bg-cyan-100',
      badgeBg: 'bg-cyan-200',
      badgeText: 'text-cyan-900',
      badgeBorder: 'border-cyan-400'
    }
  },
  {
    id: 'round-table',
    label: 'Round Table Grid',
    shortLabel: '12-Col Grid',
    icon: Users,
    badge: '12-COL A2UI',
    category: 'core',
    description: '12-Column Sovereign Grid Cockpit (Boris, Codex, Helio, Octavian, Merlin & Anya)',
    accentColor: '#00E5FF',
    darkActiveStyles: {
      border: 'border-cyan-400',
      text: 'text-cyan-300',
      bg: 'bg-cyan-950/70',
      glow: 'shadow-[0_0_18px_rgba(0,229,255,0.25)]',
      badgeBg: 'bg-cyan-500/20',
      badgeText: 'text-cyan-300',
      badgeBorder: 'border-cyan-500/40'
    },
    lightActiveStyles: {
      border: 'border-cyan-600',
      text: 'text-cyan-900',
      bg: 'bg-cyan-100',
      badgeBg: 'bg-cyan-200',
      badgeText: 'text-cyan-900',
      badgeBorder: 'border-cyan-300'
    }
  },
  {
    id: 'command-center',
    label: 'Command Center',
    shortLabel: 'Overview',
    icon: Layers,
    badge: 'ThreeUI+Voice',
    category: 'core',
    description: 'Central Multi-Split Switchboard, Live Telemetry & Dev Deck',
    accentColor: '#00E5FF',
    darkActiveStyles: {
      border: 'border-cyan-400',
      text: 'text-cyan-300',
      bg: 'bg-cyan-950/60',
      glow: 'shadow-[0_0_15px_rgba(0,229,255,0.2)]',
      badgeBg: 'bg-cyan-500/20',
      badgeText: 'text-cyan-300',
      badgeBorder: 'border-cyan-500/40'
    },
    lightActiveStyles: {
      border: 'border-cyan-600',
      text: 'text-cyan-800',
      bg: 'bg-cyan-100',
      badgeBg: 'bg-cyan-200',
      badgeText: 'text-cyan-900',
      badgeBorder: 'border-cyan-300'
    }
  },
  {
    id: 'cartridge-matrix',
    label: 'Cartridge Matrix',
    shortLabel: 'Matrix',
    icon: Box,
    badge: 'HOT-SWAP',
    category: 'core',
    description: 'Hot-Swappable Dioxus/WASM Micro-Frontends & Live Sandboxes',
    accentColor: '#F472B6',
    darkActiveStyles: {
      border: 'border-pink-400',
      text: 'text-pink-300',
      bg: 'bg-pink-950/60',
      glow: 'shadow-[0_0_15px_rgba(244,114,182,0.25)]',
      badgeBg: 'bg-pink-500/20',
      badgeText: 'text-pink-300',
      badgeBorder: 'border-pink-500/40'
    },
    lightActiveStyles: {
      border: 'border-pink-600',
      text: 'text-pink-800',
      bg: 'bg-pink-100',
      badgeBg: 'bg-pink-200',
      badgeText: 'text-pink-900',
      badgeBorder: 'border-pink-300'
    }
  },
  {
    id: 'digital-factory',
    label: 'Digital Factory',
    shortLabel: 'Factory',
    icon: Cpu,
    badge: 'BLAST V4',
    category: 'core',
    description: 'Autonomous Product Pipeline, 7-Gate Grill & Kinetic Injection',
    accentColor: '#F59E0B',
    darkActiveStyles: {
      border: 'border-amber-400',
      text: 'text-amber-300',
      bg: 'bg-amber-950/50',
      glow: 'shadow-[0_0_15px_rgba(245,158,11,0.2)]',
      badgeBg: 'bg-amber-500/20',
      badgeText: 'text-amber-300',
      badgeBorder: 'border-amber-500/40'
    },
    lightActiveStyles: {
      border: 'border-amber-600',
      text: 'text-amber-800',
      bg: 'bg-amber-100',
      badgeBg: 'bg-amber-200',
      badgeText: 'text-amber-900',
      badgeBorder: 'border-amber-300'
    }
  },
  {
    id: 'multivoice',
    label: 'Multi-Voice Router',
    shortLabel: 'Voices',
    icon: Radio,
    badge: 'VOCODER',
    category: 'intelligence',
    description: '8 Sovereign Knight Neural Vocoders & Speech Synthesis Multiplex',
    accentColor: '#A855F7',
    darkActiveStyles: {
      border: 'border-purple-400',
      text: 'text-purple-300',
      bg: 'bg-purple-950/60',
      glow: 'shadow-[0_0_15px_rgba(168,85,247,0.25)]',
      badgeBg: 'bg-purple-500/20',
      badgeText: 'text-purple-300',
      badgeBorder: 'border-purple-500/40'
    },
    lightActiveStyles: {
      border: 'border-purple-600',
      text: 'text-purple-800',
      bg: 'bg-purple-100',
      badgeBg: 'bg-purple-200',
      badgeText: 'text-purple-900',
      badgeBorder: 'border-purple-300'
    }
  },
  {
    id: 'audio-workbench',
    label: 'Kickbox Audio Workbench',
    shortLabel: 'Kickbox 3D',
    icon: Headphones,
    badge: 'WASM32-SIMD',
    category: 'intelligence',
    description: 'Kickbox 3D-to-2D Spatial DSP Canvas & Zero-GC Ring Buffers',
    accentColor: '#9D4EDD',
    darkActiveStyles: {
      border: 'border-purple-400',
      text: 'text-purple-300',
      bg: 'bg-purple-950/60',
      glow: 'shadow-[0_0_15px_rgba(157,78,221,0.25)]',
      badgeBg: 'bg-purple-500/20',
      badgeText: 'text-purple-300',
      badgeBorder: 'border-purple-500/40'
    },
    lightActiveStyles: {
      border: 'border-purple-600',
      text: 'text-purple-900',
      bg: 'bg-purple-100',
      badgeBg: 'bg-purple-200',
      badgeText: 'text-purple-900',
      badgeBorder: 'border-purple-300'
    }
  },
  {
    id: 'spatial-hud',
    label: 'Holographic Spatial HUD',
    shortLabel: '3D HUD',
    icon: Sparkles,
    badge: '3D AVATAR',
    category: 'intelligence',
    description: '3D Knight Avatars, WebGL Substrate & Spatial Audio Lattice',
    accentColor: '#00E5FF',
    darkActiveStyles: {
      border: 'border-cyan-400',
      text: 'text-cyan-300',
      bg: 'bg-cyan-950/50',
      glow: 'shadow-[0_0_15px_rgba(0,229,255,0.2)]',
      badgeBg: 'bg-cyan-500/20',
      badgeText: 'text-cyan-300',
      badgeBorder: 'border-cyan-500/30'
    },
    lightActiveStyles: {
      border: 'border-cyan-600',
      text: 'text-cyan-800',
      bg: 'bg-cyan-100',
      badgeBg: 'bg-cyan-200',
      badgeText: 'text-cyan-900',
      badgeBorder: 'border-cyan-300'
    }
  },
  {
    id: 'htmx',
    label: 'HTMX Command Center',
    shortLabel: 'HTMX',
    icon: Globe,
    badge: 'Go+SSE',
    category: 'dev',
    description: 'Go Backend SSE Streams, Real-Time DOM Fragments & Live Audit',
    accentColor: '#FBBF24',
    darkActiveStyles: {
      border: 'border-amber-400',
      text: 'text-amber-300',
      bg: 'bg-purple-950/40',
      glow: 'shadow-[0_0_15px_rgba(251,191,36,0.2)]',
      badgeBg: 'bg-amber-500/20',
      badgeText: 'text-amber-300',
      badgeBorder: 'border-amber-500/30'
    },
    lightActiveStyles: {
      border: 'border-amber-600',
      text: 'text-amber-900',
      bg: 'bg-amber-100',
      badgeBg: 'bg-amber-200',
      badgeText: 'text-amber-900',
      badgeBorder: 'border-amber-300'
    }
  },
  {
    id: 'lattice',
    label: '24D Swarm Lattice',
    shortLabel: 'Lattice',
    icon: Network,
    badge: 'DAG',
    category: 'intelligence',
    description: 'Real-time DAG State Graph, Bottleneck Triaging & Flow Vectors',
    accentColor: '#38BDF8',
    darkActiveStyles: {
      border: 'border-sky-400',
      text: 'text-sky-300',
      bg: 'bg-sky-950/40',
      glow: 'shadow-[0_0_15px_rgba(56,189,248,0.2)]',
      badgeBg: 'bg-sky-500/20',
      badgeText: 'text-sky-300',
      badgeBorder: 'border-sky-500/30'
    },
    lightActiveStyles: {
      border: 'border-sky-600',
      text: 'text-sky-900',
      bg: 'bg-sky-100',
      badgeBg: 'bg-sky-200',
      badgeText: 'text-sky-900',
      badgeBorder: 'border-sky-300'
    }
  },
  {
    id: 'vfs',
    label: 'VFS Master Matrix',
    shortLabel: 'VFS Explorer',
    icon: FileCode,
    badge: 'DYNAMIC_VFS_COUNT',
    category: 'dev',
    description: 'Master Scaffold Files, Dioxus Components, Contracts & Rust Specs',
    accentColor: '#2DD4BF',
    darkActiveStyles: {
      border: 'border-teal-400',
      text: 'text-teal-200',
      bg: 'bg-teal-950/40',
      glow: 'shadow-[0_0_15px_rgba(45,212,191,0.2)]',
      badgeBg: 'bg-neutral-800',
      badgeText: 'text-neutral-300',
      badgeBorder: 'border-neutral-700'
    },
    lightActiveStyles: {
      border: 'border-teal-600',
      text: 'text-teal-950',
      bg: 'bg-teal-50',
      badgeBg: 'bg-slate-300',
      badgeText: 'text-slate-800',
      badgeBorder: 'border-slate-400'
    }
  },
  {
    id: 'terminal',
    label: 'HiveIDE Living Terminal',
    shortLabel: 'Terminal',
    icon: TerminalIcon,
    badge: 'WASMTIME',
    category: 'dev',
    description: 'Direct DAG Execution, SQLite WAL2 Stream & Wasmtime Host CLI',
    accentColor: '#34D399',
    darkActiveStyles: {
      border: 'border-emerald-400',
      text: 'text-emerald-300',
      bg: 'bg-emerald-950/40',
      glow: 'shadow-[0_0_15px_rgba(52,211,153,0.2)]',
      badgeBg: 'bg-emerald-500/20',
      badgeText: 'text-emerald-300',
      badgeBorder: 'border-emerald-500/30'
    },
    lightActiveStyles: {
      border: 'border-emerald-600',
      text: 'text-emerald-900',
      bg: 'bg-emerald-100',
      badgeBg: 'bg-emerald-200',
      badgeText: 'text-emerald-900',
      badgeBorder: 'border-emerald-300'
    }
  },
  {
    id: 'knights',
    label: '25-Knight Roster',
    shortLabel: 'Knights',
    icon: Users,
    badge: '25',
    category: 'governance',
    description: 'Round Table Knights, Memory Quota & Real-time Division Load',
    accentColor: '#60A5FA',
    darkActiveStyles: {
      border: 'border-blue-400',
      text: 'text-blue-200',
      bg: 'bg-blue-950/40',
      glow: 'shadow-[0_0_15px_rgba(96,165,250,0.2)]',
      badgeBg: 'bg-neutral-800',
      badgeText: 'text-neutral-300',
      badgeBorder: 'border-neutral-700'
    },
    lightActiveStyles: {
      border: 'border-blue-600',
      text: 'text-blue-950',
      bg: 'bg-blue-50',
      badgeBg: 'bg-slate-300',
      badgeText: 'text-slate-800',
      badgeBorder: 'border-slate-400'
    }
  },
  {
    id: 'contracts',
    label: 'Contracts & Gideon Vault',
    shortLabel: 'Contracts',
    icon: ShieldCheck,
    badge: 'Z3 PROOF',
    category: 'governance',
    description: 'MsgPack Schemas, AST Integrity & Formal Mathematical Proofs',
    accentColor: '#10B981',
    darkActiveStyles: {
      border: 'border-emerald-400',
      text: 'text-emerald-300',
      bg: 'bg-emerald-950/30',
      glow: 'shadow-[0_0_15px_rgba(16,185,129,0.2)]',
      badgeBg: 'bg-emerald-500/20',
      badgeText: 'text-emerald-300',
      badgeBorder: 'border-emerald-500/30'
    },
    lightActiveStyles: {
      border: 'border-emerald-600',
      text: 'text-emerald-950',
      bg: 'bg-emerald-50',
      badgeBg: 'bg-emerald-200',
      badgeText: 'text-emerald-900',
      badgeBorder: 'border-emerald-300'
    }
  },
  {
    id: 'shadow-gauntlet',
    label: 'Gideon Shadow Gauntlet',
    shortLabel: 'Z3 Gauntlet',
    icon: ShieldCheck,
    badge: 'Z3 PROOFS',
    category: 'governance',
    description: 'Shadow Micro-VM TDD Gauntlet & Z3 Neurosymbolic SAT Invariants',
    accentColor: '#10B981',
    darkActiveStyles: {
      border: 'border-emerald-400',
      text: 'text-emerald-300',
      bg: 'bg-emerald-950/40',
      glow: 'shadow-[0_0_18px_rgba(16,185,129,0.25)]',
      badgeBg: 'bg-emerald-500/20',
      badgeText: 'text-emerald-300',
      badgeBorder: 'border-emerald-500/40'
    },
    lightActiveStyles: {
      border: 'border-emerald-600',
      text: 'text-emerald-950',
      bg: 'bg-emerald-50',
      badgeBg: 'bg-emerald-200',
      badgeText: 'text-emerald-900',
      badgeBorder: 'border-emerald-300'
    }
  },
  {
    id: 'constitution',
    label: 'Constitutional Laws',
    shortLabel: 'Constitution',
    icon: Scale,
    badge: 'APEE v7.0',
    category: 'governance',
    description: 'Anya First Law, Human-In-The-Loop Authorizations & Sandboxes',
    accentColor: '#FB7185',
    darkActiveStyles: {
      border: 'border-rose-400',
      text: 'text-rose-300',
      bg: 'bg-rose-950/30',
      glow: 'shadow-[0_0_15px_rgba(251,113,133,0.2)]',
      badgeBg: 'bg-rose-500/20',
      badgeText: 'text-rose-300',
      badgeBorder: 'border-rose-500/30'
    },
    lightActiveStyles: {
      border: 'border-rose-600',
      text: 'text-rose-950',
      bg: 'bg-rose-50',
      badgeBg: 'bg-rose-200',
      badgeText: 'text-rose-900',
      badgeBorder: 'border-rose-300'
    }
  }
];

export interface NavigationMenuProps {
  activeTab: ActiveTab;
  onSelectTab: (tab: ActiveTab) => void;
  theme?: ThemeMode;
  vfsFileCount?: number;
  className?: string;
}

export const NavigationMenu: React.FC<NavigationMenuProps> = ({
  activeTab,
  onSelectTab,
  theme = 'dark',
  vfsFileCount = 20,
  className = ''
}) => {
  const isDark = theme === 'dark';
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [filterQuery, setFilterQuery] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false);
      }
    };
    if (dropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [dropdownOpen]);

  const currentItem = NAV_ITEMS.find(item => item.id === activeTab) || NAV_ITEMS[0];

  const filteredItems = NAV_ITEMS.filter(item =>
    item.label.toLowerCase().includes(filterQuery.toLowerCase()) ||
    item.description.toLowerCase().includes(filterQuery.toLowerCase()) ||
    item.category.toLowerCase().includes(filterQuery.toLowerCase())
  );

  return (
    <nav
      id="unified-navigation-menu"
      className={`relative px-4 sm:px-6 flex items-center justify-between border-t ${
        isDark ? 'border-neutral-800/80 bg-neutral-950/90' : 'border-slate-300 bg-slate-200/50'
      } font-medium text-sm transition-colors select-none ${className}`}
    >
      {/* Scrollable Tab Strip */}
      <div className="flex space-x-1 overflow-x-auto scrollbar-none py-0.5 flex-1 pr-2">
        {NAV_ITEMS.map((item) => {
          const isActive = activeTab === item.id;
          const Icon = item.icon;
          const badgeText = item.id === 'vfs' ? `${vfsFileCount}` : item.badge;

          let tabClasses = 'px-3.5 py-2.5 border-b-2 flex items-center space-x-2 transition-all whitespace-nowrap text-xs sm:text-sm cursor-pointer ';

          if (isActive) {
            if (isDark) {
              tabClasses += `${item.darkActiveStyles.border} ${item.darkActiveStyles.text} ${item.darkActiveStyles.bg} font-bold ${item.darkActiveStyles.glow}`;
            } else {
              tabClasses += `${item.lightActiveStyles.border} ${item.lightActiveStyles.text} ${item.lightActiveStyles.bg} font-bold`;
            }
          } else {
            if (isDark) {
              tabClasses += 'border-transparent text-neutral-400 hover:text-neutral-200 hover:bg-neutral-900/40';
            } else {
              tabClasses += 'border-transparent text-slate-600 hover:text-slate-900 hover:bg-slate-300/40';
            }
          }

          return (
            <button
              key={item.id}
              id={`nav-tab-${item.id}`}
              onClick={() => onSelectTab(item.id)}
              className={tabClasses}
              title={item.description}
            >
              <Icon
                className={`w-4 h-4 transition-transform duration-200 ${
                  isActive ? 'scale-110' : 'opacity-70 group-hover:opacity-100'
                } ${item.id === 'gateway' && isActive ? 'animate-spin' : ''}`}
                style={item.id === 'gateway' ? { animationDuration: '30s' } : undefined}
              />
              <span>{item.label}</span>
              {badgeText && (
                <span
                  className={`ml-1 px-1.5 py-0.2 text-[10px] rounded font-mono font-bold border transition-colors ${
                    isActive
                      ? isDark
                        ? `${item.darkActiveStyles.badgeBg} ${item.darkActiveStyles.badgeText} ${item.darkActiveStyles.badgeBorder}`
                        : `${item.lightActiveStyles.badgeBg} ${item.lightActiveStyles.badgeText} ${item.lightActiveStyles.badgeBorder}`
                      : isDark
                      ? 'bg-neutral-900 text-neutral-500 border-neutral-800'
                      : 'bg-slate-300/60 text-slate-600 border-slate-400/50'
                  }`}
                >
                  {badgeText}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Quick Jump / Switcher Dropdown Button */}
      <div className="relative flex-shrink-0 py-1" ref={dropdownRef}>
        <button
          id="nav-quick-jump-trigger"
          onClick={() => {
            setDropdownOpen(!dropdownOpen);
            setFilterQuery('');
          }}
          className={`px-2.5 py-1.5 rounded-lg border text-xs font-mono font-semibold transition-all flex items-center space-x-1.5 cursor-pointer active:scale-95 ${
            dropdownOpen
              ? isDark
                ? 'bg-cyan-950/80 border-cyan-400 text-cyan-300 shadow-[0_0_12px_rgba(0,229,255,0.3)]'
                : 'bg-cyan-100 border-cyan-600 text-cyan-900 shadow-sm'
              : isDark
              ? 'bg-neutral-900/90 hover:bg-neutral-800 text-neutral-300 border-neutral-800 hover:border-neutral-700'
              : 'bg-white hover:bg-slate-100 text-slate-700 border-slate-300 shadow-sm'
          }`}
          title="Open Quick Switcher & Subsystem Matrix"
        >
          <LayoutGrid className="w-3.5 h-3.5 text-amber-400" />
          <span className="hidden md:inline font-mono">NEXUS</span>
          <ChevronDown className={`w-3 h-3 transition-transform duration-200 ${dropdownOpen ? 'rotate-180' : ''}`} />
        </button>

        {/* Dropdown Matrix Overlay */}
        <AnimatePresence>
          {dropdownOpen && (
            <motion.div
              id="nav-quick-jump-menu"
              initial={{ opacity: 0, y: 8, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 6, scale: 0.95 }}
              transition={{ duration: 0.15, ease: 'easeOut' }}
              className={`absolute right-0 top-full mt-1.5 w-80 sm:w-96 rounded-xl border shadow-2xl z-50 overflow-hidden backdrop-blur-xl ${
                isDark
                  ? 'bg-neutral-950/95 border-neutral-800 text-neutral-100 shadow-[0_10px_35px_rgba(0,0,0,0.8)]'
                  : 'bg-white/95 border-slate-300 text-slate-900 shadow-xl'
              }`}
            >
              {/* Search Filter Header */}
              <div className={`p-2.5 border-b ${isDark ? 'border-neutral-800/80 bg-neutral-900/60' : 'border-slate-200 bg-slate-50'}`}>
                <div className="relative flex items-center">
                  <Search className="w-3.5 h-3.5 text-neutral-400 absolute left-2.5" />
                  <input
                    type="text"
                    value={filterQuery}
                    onChange={(e) => setFilterQuery(e.target.value)}
                    placeholder="Search subsystem, gateway or cartridge..."
                    className={`w-full text-xs font-mono pl-8 pr-3 py-1.5 rounded-lg border outline-none transition-all ${
                      isDark
                        ? 'bg-neutral-950 border-neutral-800 text-white placeholder-neutral-500 focus:border-cyan-400'
                        : 'bg-white border-slate-300 text-slate-900 placeholder-slate-400 focus:border-cyan-600'
                    }`}
                    autoFocus
                  />
                </div>
              </div>

              {/* Grouped Links List */}
              <div className="max-h-80 overflow-y-auto p-1.5 space-y-1">
                {filteredItems.length === 0 ? (
                  <div className="p-4 text-center text-xs font-mono text-neutral-500">
                    No matching subsystems found.
                  </div>
                ) : (
                  filteredItems.map((item) => {
                    const isCurrent = item.id === activeTab;
                    const Icon = item.icon;
                    return (
                      <button
                        key={item.id}
                        id={`quick-nav-${item.id}`}
                        onClick={() => {
                          onSelectTab(item.id);
                          setDropdownOpen(false);
                        }}
                        className={`w-full text-left p-2 rounded-lg flex items-center justify-between transition-all group cursor-pointer ${
                          isCurrent
                            ? isDark
                              ? 'bg-cyan-950/60 border border-cyan-500/40 text-white'
                              : 'bg-cyan-50 border border-cyan-300 text-cyan-950'
                            : isDark
                            ? 'hover:bg-neutral-900 border border-transparent text-neutral-300 hover:text-white'
                            : 'hover:bg-slate-100 border border-transparent text-slate-700 hover:text-slate-950'
                        }`}
                      >
                        <div className="flex items-center space-x-2.5 min-w-0">
                          <div
                            className={`p-1.5 rounded-md border flex-shrink-0 ${
                              isDark ? 'bg-neutral-900 border-neutral-800' : 'bg-white border-slate-200'
                            }`}
                          >
                            <Icon className="w-3.5 h-3.5" style={{ color: item.accentColor }} />
                          </div>
                          <div className="min-w-0">
                            <div className="flex items-center space-x-1.5">
                              <span className="text-xs font-semibold truncate">{item.label}</span>
                              <span className="text-[9px] font-mono uppercase px-1 py-0.2 rounded opacity-70 border border-current">
                                {item.category}
                              </span>
                            </div>
                            <p className="text-[10px] text-neutral-400 truncate max-w-[220px]">
                              {item.description}
                            </p>
                          </div>
                        </div>

                        {isCurrent ? (
                          <Check className="w-4 h-4 text-cyan-400 flex-shrink-0 ml-2" />
                        ) : (
                          <span className="text-[10px] font-mono text-neutral-500 opacity-0 group-hover:opacity-100 transition-opacity">
                            GO ➔
                          </span>
                        )}
                      </button>
                    );
                  })
                )}
              </div>

              {/* Footer Status */}
              <div className={`px-3 py-2 border-t text-[10px] font-mono flex items-center justify-between ${
                isDark ? 'border-neutral-800/80 bg-neutral-900/80 text-neutral-400' : 'border-slate-200 bg-slate-100 text-slate-600'
              }`}>
                <span>Total Subsystems: {NAV_ITEMS.length}</span>
                <span className="text-cyan-400 font-semibold">Active: {currentItem.shortLabel || currentItem.label}</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </nav>
  );
};

export default NavigationMenu;
