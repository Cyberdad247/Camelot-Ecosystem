import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface KnightPersonality {
  id: string;
  name: string;
  title: string;
  avatar: string;
  role: string;
  domain: string;
  oceanScores: {
    openness: number;
    conscientiousness: number;
    extraversion: number;
    agreeableness: number;
    neuroticism: number;
  };
  quote: string;
}

export interface CartridgeMetadata {
  id: string;
  name: string;
  category: string;
  price: string;
  status: 'installed' | 'available' | 'locked';
  version: string;
  description: string;
  ramFootprint: string;
  author: string;
}

export interface GuildContract {
  id: string;
  title: string;
  payout: string;
  difficulty: 'Sovereign' | 'Knight-Tier' | 'Arch-Sage';
  timeEstimate: string;
  status: 'OPEN' | 'CLAIMED' | 'SEALED';
  sponsor: string;
  dagSteps: string[];
}

interface EcosystemState {
  tenantID: string | null;
  authToken: string | null;
  selectedKnight: string;
  activeCartridges: string[];
  installedCartridges: CartridgeMetadata[];
  deviceMode: 'desktop' | 'mobile_s26';
  activeView: 'dashboard' | 'vault' | 'marketplace' | 'guild' | 'knights' | 'onboarding' | 'auth';
  wakeWordActive: boolean;
  lastVoiceTranscript: string;
  biometricVerified: boolean;
  activeContracts: GuildContract[];
  receipts: Array<{ id: string; item: string; amount: string; date: string; seal: string }>;

  setTenantID: (id: string | null) => void;
  setAuthToken: (token: string | null) => void;
  setSelectedKnight: (knight: string) => void;
  toggleCartridge: (id: string) => void;
  installCartridge: (id: string) => void;
  uninstallCartridge: (id: string) => void;
  setDeviceMode: (mode: 'desktop' | 'mobile_s26') => void;
  setActiveView: (view: EcosystemState['activeView']) => void;
  setWakeWordActive: (active: boolean) => void;
  setLastVoiceTranscript: (transcript: string) => void;
  setBiometricVerified: (verified: boolean) => void;
  claimContract: (contractId: string) => void;
  addReceipt: (receipt: { id: string; item: string; amount: string; date: string; seal: string }) => void;
  resetAuth: () => void;
}

export const INITIAL_KNIGHTS: KnightPersonality[] = [
  {
    id: 'alfred',
    name: 'Alfred Ω',
    title: 'Sovereign Grand Chamberlain & Audio Physics Engine',
    avatar: '🎙️',
    role: 'Primary Synthesizer',
    domain: 'Real-Time Voice, Memory Recall, Security Gating',
    oceanScores: { openness: 92, conscientiousness: 98, extraversion: 65, agreeableness: 88, neuroticism: 12 },
    quote: 'Always at your service, Sovereign. The audio physics lattices remain pure.'
  },
  {
    id: 'anya',
    name: 'Anya Ω 🎭',
    title: 'Gatekeeper & Cognitive Visor',
    avatar: '🎭',
    role: 'Security Hypervisor',
    domain: 'ANYA_IS_THE_GATE, Biometrics, Zero-Trust Intercepts',
    oceanScores: { openness: 85, conscientiousness: 96, extraversion: 78, agreeableness: 70, neuroticism: 18 },
    quote: 'The gate is absolute. No synthetic impersonation shall cross the threshold.'
  },
  {
    id: 'merlin',
    name: 'Merlin Ω 🧠',
    title: 'Chief Arch-Strategist & Task DAG Decomposer',
    avatar: '🧠',
    role: 'DAG Orchestrator',
    domain: 'GraphRAG MemPalace, Kinetic Task Queues, 1.58b Ouroboros',
    oceanScores: { openness: 99, conscientiousness: 94, extraversion: 40, agreeableness: 82, neuroticism: 8 },
    quote: 'Decomposing complex commercial intent into mathematically verified DAG steps.'
  },
  {
    id: 'boris',
    name: 'Sir Boris ⚔️',
    title: 'Vanguard UI/UX & Grid Architect',
    avatar: '⚔️',
    role: 'Interface Sovereign',
    domain: 'Obsidian/Gold/Purple Rhythms, S26 Edge Layouts, Mobile Ergonomics',
    oceanScores: { openness: 78, conscientiousness: 90, extraversion: 85, agreeableness: 75, neuroticism: 15 },
    quote: 'The visual rhythm must cut like Valyrian steel. Zero UI slop.'
  },
  {
    id: 'codex',
    name: 'Sir Codex 🛠️',
    title: 'WASM32 Zero-Copy & Rust Engine Master',
    avatar: '🛠️',
    role: 'Low-Level Enforcer',
    domain: 'WASM32 Scorpion Sting, 4GB Memory Boundary, DuckDB-WASM Slabs',
    oceanScores: { openness: 80, conscientiousness: 99, extraversion: 30, agreeableness: 80, neuroticism: 5 },
    quote: 'Zero copy, zero leak, strictly bounded under 4GB cgroup.'
  }
];

export const INITIAL_CARTRIDGES: CartridgeMetadata[] = [
  {
    id: 'excalibur-ecc',
    name: 'Excalibur Digital Throne',
    category: 'Sovereign Kernel',
    price: 'CORE',
    status: 'installed',
    version: 'v1000-EXCALIBUR',
    description: 'Holographic Globe, Global Node Inventory, 4GB Telemetry and Sovereign Identity Visor.',
    ramFootprint: '18.4 MB',
    author: 'Invisioned Marketing Inc.'
  },
  {
    id: 'kba-executive',
    name: 'KBA Executive (Cartridge 01)',
    category: 'Corporate Strategy',
    price: '$2,450 / mo',
    status: 'installed',
    version: 'v2.4-Sovereign',
    description: 'Paladin Octem Z3 Prover, S-Corp Tax Allocation, and Strategic Governance DAGs.',
    ramFootprint: '14.2 MB',
    author: 'Invisioned Marketing Inc.'
  },
  {
    id: 'digital-factory',
    name: 'Digital Factory (Cartridge 02)',
    category: 'Commerce & Data',
    price: '$1,800 / mo',
    status: 'installed',
    version: 'v3.1-WASM',
    description: 'DuckDB-WASM Columnar Lakehouse, SQL Terminal, and Midas Loop lead generation.',
    ramFootprint: '22.1 MB',
    author: 'Invisioned Marketing Inc.'
  },
  {
    id: '1vizion-rcrds',
    name: '1VIZION RCRDS (Cartridge 03)',
    category: 'Audio Physics',
    price: '$950 / mo',
    status: 'installed',
    version: 'v4.0-EBU',
    description: 'EBU R128 Broadcast Loudness Metering (-14 LUFS), 3000x3000px artwork validation & ISRC binding.',
    ramFootprint: '16.5 MB',
    author: '1VIZION RCRDS ⨷'
  },
  {
    id: 'artisan-goods',
    name: 'Head Artworks Emporium',
    category: 'Physical Artisanship',
    price: '$450.00',
    status: 'available',
    version: 'v1.2-Obsidian',
    description: 'Direct S26 e-commerce bridge for luxury handcrafted physical artisan artifacts and seals.',
    ramFootprint: '9.8 MB',
    author: 'Head Artworks LLC'
  },
  {
    id: 'midas-crawler',
    name: 'Midas Deep Firecrawl Pro',
    category: 'Intelligence Scraping',
    price: '$1,200 / mo',
    status: 'available',
    version: 'v5.0-Omni',
    description: 'Autonomous multi-source lead synthesis with real-time enterprise egress audit generation.',
    ramFootprint: '19.0 MB',
    author: 'Invisioned Marketing Inc.'
  }
];

export const INITIAL_CONTRACTS: GuildContract[] = [
  {
    id: 'CON-711',
    title: 'Cuyahoga County Enterprise Egress Audit',
    payout: '4,500 USDC',
    difficulty: 'Sovereign',
    timeEstimate: '3h 15m',
    status: 'OPEN',
    sponsor: 'Invisioned Marketing Inc.',
    dagSteps: ['Ingest network topology', 'Audit 40% egress waste', 'Generate executive pitch', 'Seal with ⚜️_SOVEREIGN_TRUTH']
  },
  {
    id: 'CON-712',
    title: 'Dolby Atmos Master Transcode & 3000px Seal',
    payout: '1,850 USDC',
    difficulty: 'Knight-Tier',
    timeEstimate: '45m',
    status: 'OPEN',
    sponsor: '1VIZION RCRDS ⨷',
    dagSteps: ['Validate -14 LUFS', 'Verify 3000x3000px 300DPI artwork', 'Embed ISRC / Records Unchained 71228']
  },
  {
    id: 'CON-713',
    title: 'Z3 SMT Invariant Verification for Micro-Unikernel',
    payout: '6,200 USDC',
    difficulty: 'Arch-Sage',
    timeEstimate: '5h 00m',
    status: 'OPEN',
    sponsor: 'Camelot Sovereign UKG',
    dagSteps: ['Formulate memory bounds assertions', 'Run Z3 neurosymbolic solver', 'Enforce 4GB ceiling in cgroup']
  }
];

export const useEcosystemStore = create<EcosystemState>()(
  persist(
    (set, get) => ({
      tenantID: 'tenant_sovereign_001',
      authToken: 'EXCALIBUR_ED25519_VALIDATED_SESSION',
      selectedKnight: 'alfred',
      activeCartridges: ['excalibur-ecc', 'kba-executive', 'digital-factory', '1vizion-rcrds'],
      installedCartridges: INITIAL_CARTRIDGES,
      deviceMode: 'desktop',
      activeView: 'dashboard',
      wakeWordActive: false,
      lastVoiceTranscript: 'Hey Alfred, system status nominal. All Knights at attention.',
      biometricVerified: true,
      activeContracts: INITIAL_CONTRACTS,
      receipts: [
        { id: 'REC-901', item: '1VIZION RCRDS Distribution License', amount: '$950.00', date: '2026-09-08', seal: '71228-SEALED' },
        { id: 'REC-902', item: 'DuckDB-WASM S-Corp MicroVM Node', amount: '$420.00', date: '2026-09-07', seal: 'VAULT-VERIFIED' },
        { id: 'REC-903', item: 'Head Artworks Obsidian Sigil Masterpiece', amount: '$450.00', date: '2026-09-05', seal: 'PROVENANCE-ANCHOR' }
      ],

      setTenantID: (id) => set({ tenantID: id }),
      setAuthToken: (token) => set({ authToken: token }),
      setSelectedKnight: (knight) => set({ selectedKnight: knight }),
      toggleCartridge: (id) => {
        const current = get().activeCartridges;
        if (current.includes(id)) {
          set({ activeCartridges: current.filter((c) => c !== id) });
        } else {
          set({ activeCartridges: [...current, id] });
        }
      },
      installCartridge: (id) => {
        const installed = get().installedCartridges.map((cart) =>
          cart.id === id ? { ...cart, status: 'installed' as const } : cart
        );
        const currentActive = get().activeCartridges;
        set({
          installedCartridges: installed,
          activeCartridges: currentActive.includes(id) ? currentActive : [...currentActive, id]
        });
      },
      uninstallCartridge: (id) => {
        const installed = get().installedCartridges.map((cart) =>
          cart.id === id ? { ...cart, status: 'available' as const } : cart
        );
        set({
          installedCartridges: installed,
          activeCartridges: get().activeCartridges.filter((c) => c !== id)
        });
      },
      setDeviceMode: (mode) => set({ deviceMode: mode }),
      setActiveView: (view) => set({ activeView: view }),
      setWakeWordActive: (active) => set({ wakeWordActive: active }),
      setLastVoiceTranscript: (transcript) => set({ lastVoiceTranscript: transcript }),
      setBiometricVerified: (verified) => set({ biometricVerified: verified }),
      claimContract: (contractId) => {
        set({
          activeContracts: get().activeContracts.map((c) =>
            c.id === contractId ? { ...c, status: 'CLAIMED' as const } : c
          )
        });
      },
      addReceipt: (receipt) => set({ receipts: [receipt, ...get().receipts] }),
      resetAuth: () => set({ authToken: null, biometricVerified: false, tenantID: null, activeView: 'onboarding' })
    }),
    { name: 'camelot-ecosystem-store' }
  )
);
