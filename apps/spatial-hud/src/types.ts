export interface VfsFile {
  path: string;
  name: string;
  domain: string;
  category: 'vfs-core' | 'docs' | 'contracts' | 'golden-receipts' | 'htmx-center';
  content: string;
  description?: string;
  isMarkdown: boolean;
  parsed?: any;
  sha256?: string;
}

export interface Knight {
  id: string;
  name: string;
  role: string;
  division: 'Executive' | 'Streaming & Customer Ops' | 'Property & Asset' | 'Core Engineering & Vanguard';
  avatarTitle: string;
  status: 'ACTIVE' | 'STANDBY' | 'ENGAGED' | 'ARMED';
  domain: string;
  skills: string[];
  bio: string;
  load: number;
}

export interface TerminalLog {
  id: string;
  timestamp: string;
  sender: 'ANYA_Ω' | 'MERLIN_Ω' | 'SIR_CODEX' | 'LADY_MNEMOSYNE' | 'OPERATOR' | 'SYSTEM' | 'GIDEON' | 'SCRIBE';
  level: 'INFO' | 'SUCCESS' | 'WARN' | 'DANGER' | 'TRACE';
  message: string;
  codeBlock?: string;
  metadata?: Record<string, any>;
}

export type ActiveTab = 
  | 'gateway' 
  | 'round-table'
  | 'audio-workbench'
  | 'shadow-gauntlet'
  | 'command-center' 
  | 'cartridge-matrix' 
  | 'digital-factory' 
  | 'multivoice' 
  | 'spatial-hud' 
  | 'vfs' 
  | 'terminal' 
  | 'htmx' 
  | 'lattice' 
  | 'knights' 
  | 'contracts' 
  | 'constitution';

export type ThemeMode = 'dark' | 'light';

export interface SovereignCartridge {
  id: string;
  code: string;
  name: string;
  version: string;
  themeIdentified: string;
  mantraCrystal: string;
  leadKnights: string[];
  division: 'Executive' | 'Core Engineering & Vanguard' | 'Streaming & Customer Ops' | 'Property & Asset';
  targetLatencyMs: number;
  memoryFootprintMb: number;
  memoryRecurrence: string;
  topologicalValidator: string;
  qftCompressionFactor: number;
  color: string;
  status: 'ENGAGED' | 'STANDBY' | 'EJECTED' | 'TRANSFIGURING';
  payloadSchema: Record<string, any>;
  description: string;
}
