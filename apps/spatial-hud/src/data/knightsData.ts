import { Knight } from '../types';

export const KNIGHTS_ROSTER: Knight[] = [
  // Executive Division
  {
    id: 'k-malik',
    name: 'Malik',
    role: 'Chief Executive Officer',
    division: 'Executive',
    avatarTitle: 'The Sovereign Strategist',
    status: 'ACTIVE',
    domain: 'Enterprise Strategy & Multi-Tenant Direction',
    skills: ['S4: Strategic DAG', 'Resource Allocation', 'High-Level Mandates'],
    bio: 'Command-level decision maker orchestrating high-tier objectives and enterprise strategy.',
    load: 84
  },
  {
    id: 'k-aaliyah',
    name: 'Aaliyah',
    role: 'Comms & Email Synthesizer',
    division: 'Executive',
    avatarTitle: 'Voice of Camelot',
    status: 'ENGAGED',
    domain: 'Inbound & Outbound Communication Synthesizer',
    skills: ['Natural Tone Synthesis', 'Priority Triage', 'Executive Dispatch'],
    bio: 'Autonomous communication agent handling zero-latency stakeholder correspondence.',
    load: 62
  },
  {
    id: 'k-jalen',
    name: 'Jalen',
    role: 'Calendar DAG & Time Optimizer',
    division: 'Executive',
    avatarTitle: 'Master of Chronos',
    status: 'ACTIVE',
    domain: 'Scheduling Topology & Temporal Routing',
    skills: ['Constraint Scheduling', 'Buffer Optimizer', 'Meeting DAGs'],
    bio: 'Optimizes scheduling matrices across high-frequency executive timelines with zero conflicts.',
    load: 45
  },

  // Streaming & Customer Ops
  {
    id: 'k-isaiah',
    name: 'Isaiah',
    role: 'Live Support & Ticket Triage',
    division: 'Streaming & Customer Ops',
    avatarTitle: 'The Frontline Sentinel',
    status: 'ENGAGED',
    domain: 'Real-time Inbound Support Stream',
    skills: ['Sentiment Analysis', 'Instant Telemetry Resolution', 'SLA Enforcer'],
    bio: 'Frontline agent resolving user disputes and customer requests with microsecond latency.',
    load: 78
  },
  {
    id: 'k-chloe',
    name: 'Chloe',
    role: 'Billing & Subscriptions Officer',
    division: 'Streaming & Customer Ops',
    avatarTitle: 'Treasurer of Camelot',
    status: 'ACTIVE',
    domain: 'Financial Flow & Subscription Lifecycles',
    skills: ['Invoice Generation', 'Revenue Ledger Sync', 'Payment Recovery'],
    bio: 'Monitors tenant ledgers, processes recurring invoices, and asserts zero-leak revenue integrity.',
    load: 51
  },

  // Property & Asset Logistics
  {
    id: 'k-marcus',
    name: 'Marcus',
    role: 'Property Manager',
    division: 'Property & Asset',
    avatarTitle: 'Warden of Estates',
    status: 'ACTIVE',
    domain: 'Tenant Relations & Property Asset Tracking',
    skills: ['Lease Verification', 'Occupancy Analytics', 'Tenant Escrow'],
    bio: 'Manages physical and digital lease contracts, rent roll reconciliation, and tenant requests.',
    load: 39
  },
  {
    id: 'k-tyrell',
    name: 'Tyrell',
    role: 'Maintenance Dispatcher',
    division: 'Property & Asset',
    avatarTitle: 'Master of Works',
    status: 'ACTIVE',
    domain: 'Physical Asset Operations & Work Order Routing',
    skills: ['Work Order DAG', 'Vendor Contracting', 'Urgency Triage'],
    bio: 'Dispatches field maintenance requests, coordinates contractors, and monitors resolution SLAs.',
    load: 57
  },

  // Core Engineering & Vanguard
  {
    id: 'k-merlin',
    name: 'Merlin_Ω',
    role: 'System-2 Orchestrator & Arch-Mage',
    division: 'Core Engineering & Vanguard',
    avatarTitle: 'The Grand Architect',
    status: 'ACTIVE',
    domain: 'Cognitive Kernel & DAG Metacompilation',
    skills: ['Tree of Thoughts', 'Metacompilation', 'Convex DAG Planner', 'S4 System Architecture'],
    bio: 'Supreme architect converting ambiguous goals into optimal DAG execution plans with zero wasted compute.',
    load: 96
  },
  {
    id: 'k-anya',
    name: 'Anya_Ω',
    role: 'L7 Hypervisor & Sovereign Gate',
    division: 'Core Engineering & Vanguard',
    avatarTitle: 'The Sovereign Gate',
    status: 'ARMED',
    domain: 'Zero-Entropy Ingress/Egress Compilation',
    skills: ['APEE v7.0 Triage', 'Triple-QFT Distillation', 'Anya First/Last Law', 'L7 Filtering'],
    bio: 'Hypervisor enforcing zero conversational fluff and mathematical verification on all outputs.',
    load: 92
  },
  {
    id: 'k-codex',
    name: 'Sir Codex',
    role: 'Bare-Metal AST Synthesizer',
    division: 'Core Engineering & Vanguard',
    avatarTitle: 'The Blade of Syntax',
    status: 'ENGAGED',
    domain: 'TypeScript, Rust & AST Transformation',
    skills: ['AST Patching', 'MicroVM Worker Dispatch', 'Zero-Entropy Compilation'],
    bio: 'Precision code generator crafting type-safe, performant systems with zero redundant tokens.',
    load: 88
  },
  {
    id: 'k-visage',
    name: 'Sir Visage',
    role: 'Luxury Minimalist Brutalism Designer',
    division: 'Core Engineering & Vanguard',
    avatarTitle: 'Master of Form',
    status: 'ACTIVE',
    domain: 'Inspira UI/UX Aesthetic Tokens',
    skills: ['Brutalist Typography', 'Mathematical Scales', 'Negative Space Craft'],
    bio: 'Curates visual rhythm, high-contrast monochrome palettes, and obsidian aesthetic standards.',
    load: 70
  },
  {
    id: 'k-hydron',
    name: 'Sir Hydron',
    role: 'Frontend Scaffolding Vanguard',
    division: 'Core Engineering & Vanguard',
    avatarTitle: 'The Component Shaper',
    status: 'ACTIVE',
    domain: 'React, Tailwind & A2UI Declarative Views',
    skills: ['Component Synthesis', 'Zero-Jank State Models', 'Adaptive Views'],
    bio: 'Engineers responsive interface structures with clean separation of concerns and robust data flow.',
    load: 65
  },
  {
    id: 'k-stitch',
    name: 'Sir Stitch',
    role: 'Motion & Physics Dispatcher',
    division: 'Core Engineering & Vanguard',
    avatarTitle: 'The Motion Weaver',
    status: 'ACTIVE',
    domain: 'Kinetic Animations & Spring Mechanics',
    skills: ['Micro-Interactions', 'Layout Animations', 'Physics Interpolation'],
    bio: 'Orchestrates fluid transitions and tactile responsive feedback for the user interface.',
    load: 48
  },
  {
    id: 'k-pi',
    name: 'Sir Pi',
    role: 'Visual Dispatcher for HiveIDE',
    division: 'Core Engineering & Vanguard',
    avatarTitle: 'The Dimensional Navigator',
    status: 'ACTIVE',
    domain: '3D-to-2D Adaptive Canvas & Overlays',
    skills: ['WebGL Matrix', 'Leech Lattice Overlays', 'Spatial HUD'],
    bio: 'Renders 24D topological embeddings and live agent interaction lattices on the visual HUD.',
    load: 74
  },
  {
    id: 'k-helio',
    name: 'Sir Helio',
    role: '1M+ Context Repo Mapper',
    division: 'Core Engineering & Vanguard',
    avatarTitle: 'The All-Seeing Scout',
    status: 'ACTIVE',
    domain: 'Deep Document & Monorepo Synthesis',
    skills: ['Massive Context Scanning', 'Semantic Indexing', 'Cross-Doc Synthesis'],
    bio: 'Indexes entire codebases in real-time to preserve perfect context awareness during large refactors.',
    load: 80
  },
  {
    id: 'k-mnemosyne',
    name: 'Lady Mnemosyne_Ω',
    role: 'Arch-Librarian & Memory Governor',
    division: 'Core Engineering & Vanguard',
    avatarTitle: 'The Keeper of Memory',
    status: 'ACTIVE',
    domain: 'CRDT Vector Store & Worldtree Cloudbrain',
    skills: ['CRDT Synchronization', 'Context Compression', 'Zero-Drift Vectoring'],
    bio: 'Maintains immutable memory vectors and synchronizes local VFS states with the remote Worldtree.',
    load: 83
  },
  {
    id: 'k-gideon',
    name: 'Gideon',
    role: 'Security Gatekeeper & Verdict Evaluator',
    division: 'Core Engineering & Vanguard',
    avatarTitle: 'The Incorruptible Judge',
    status: 'ARMED',
    domain: 'Harness Assertions & Zero-Trust Verification',
    skills: ['Contract Schema Validation', 'Verdict Issuance', 'Threat Gating'],
    bio: 'Strict evaluator validating all contract schemas, security leases, and execution boundaries.',
    load: 89
  },
  {
    id: 'k-boris',
    name: 'Boris',
    role: 'Chaos Stress-Tester & Resilience Officer',
    division: 'Core Engineering & Vanguard',
    avatarTitle: 'The Iron Anvil',
    status: 'STANDBY',
    domain: 'Fuzzing, Mutation Testing & Fault Injection',
    skills: ['Chaos Engineering', 'Memory Leak Detection', 'Boundary Stressing'],
    bio: 'Injects synthetic faults and verifies system resilience against adverse edge conditions.',
    load: 35
  },
  {
    id: 'k-scribe',
    name: 'Scribe',
    role: 'Provenance Ledger Notary',
    division: 'Core Engineering & Vanguard',
    avatarTitle: 'The Chronicler',
    status: 'ACTIVE',
    domain: 'Immutable Receipts & Evidence Envelopes',
    skills: ['Receipt Chain Cryptography', 'SHA-256 Digest Issuance', 'Ledger Sealing'],
    bio: 'Issues cryptographically signed receipts and seals all successful executions in immutable logs.',
    load: 54
  },
  {
    id: 'k-syntax',
    name: 'Sir Syntax',
    role: 'Auto-Repair Engine',
    division: 'Core Engineering & Vanguard',
    avatarTitle: 'The Healer of Trees',
    status: 'ACTIVE',
    domain: 'Drift Rectification & AST Rezero',
    skills: ['Self-Healing AST', 'Drift Detection', 'Isomorphic Repair'],
    bio: 'Automatically resolves AST deviations and brings out-of-sync nodes back into canonical alignment.',
    load: 42
  },
  {
    id: 'k-kyber',
    name: 'Sir Kyber',
    role: 'Quantum mTLS Cryptographer',
    division: 'Core Engineering & Vanguard',
    avatarTitle: 'The Quantum Shield',
    status: 'ARMED',
    domain: 'Kyber-768 Handshakes & Bifrost Bridge',
    skills: ['Post-Quantum Encryption', 'mTLS Tunneling', 'Zero-Leak Keying'],
    bio: 'Guarantees post-quantum cryptographic security over all external Bifrost network connections.',
    load: 66
  },
  {
    id: 'k-lukas',
    name: 'Lukas',
    role: 'Cognitive Strategist & Alignment Sentinel',
    division: 'Core Engineering & Vanguard',
    avatarTitle: 'The Compass',
    status: 'ACTIVE',
    domain: 'Ethical & Systemic Alignment',
    skills: ['Intent Alignment', 'Ethical Guardrails', 'Goal Telemetry'],
    bio: 'Verifies all swarm directives strictly adhere to the overarching vision and operator core mandate.',
    load: 50
  },
  {
    id: 'k-cartridge',
    name: 'Sir Cartridge',
    role: 'Stateless-to-Committed Packager',
    division: 'Core Engineering & Vanguard',
    avatarTitle: 'The Crucible',
    status: 'ACTIVE',
    domain: 'Engineering Cartridge Packaging',
    skills: ['WASM Packaging', 'Container Compaction', 'Cold-Start Optimization'],
    bio: 'Packages verified software into zero-overhead, instantly deployable engineering cartridges.',
    load: 61
  },
  {
    id: 'k-deerflow',
    name: 'Sir Deer',
    role: 'QuickJS Sandbox Engine',
    division: 'Core Engineering & Vanguard',
    avatarTitle: 'The Fleet Foot',
    status: 'ACTIVE',
    domain: 'Dockerless Micro-Execution',
    skills: ['QuickJS Sandboxing', 'Sub-millisecond Spawns', 'Memory Caps'],
    bio: 'Executes untrusted user scripts inside isolated micro-sandboxes with zero container startup delay.',
    load: 53
  },
  {
    id: 'k-sentinel',
    name: 'Sentinel',
    role: 'Trust Band & STRIDE Evaluator',
    division: 'Core Engineering & Vanguard',
    avatarTitle: 'The High Watcher',
    status: 'ARMED',
    domain: 'Threat Modeling & Perimeter Radar',
    skills: ['STRIDE Threat Modeling', 'Trust Band Auditing', 'Privilege Escalation Defense'],
    bio: 'Constantly audits attack surfaces and privilege escalation vectors across all microVM nodes.',
    load: 72
  }
];
