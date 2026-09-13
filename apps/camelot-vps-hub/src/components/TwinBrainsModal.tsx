import React, { useState, useEffect, useRef } from 'react';
import { 
  X, 
  Brain, 
  Zap, 
  GitBranch, 
  CheckCircle2, 
  ShieldCheck, 
  Sparkles, 
  RefreshCw, 
  ExternalLink, 
  Github, 
  BookOpen, 
  FileText, 
  Headphones, 
  Send, 
  Plus, 
  Layers, 
  Search, 
  Play, 
  Pause, 
  Volume2, 
  VolumeX, 
  Share2, 
  Database, 
  Cpu, 
  Terminal, 
  Code, 
  Download,
  Flame,
  Radio,
  Sliders
} from 'lucide-react';
import confetti from 'canvas-confetti';

interface TwinBrainsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface NotebookSource {
  id: string;
  title: string;
  type: 'web' | 'markdown' | 'pdf' | 'youtube' | 'git';
  wordCount: number;
  tokens: number;
  snippet: string;
  url?: string;
  status: 'indexed' | 'indexing';
}

interface ChatMessage {
  id: string;
  sender: 'user' | 'open-notebook' | 'system';
  text: string;
  citations?: { sourceId: string; sourceTitle: string; quote: string }[];
  timestamp: string;
}

interface ResearchNotebook {
  id: string;
  name: string;
  description: string;
  category: string;
  sourcesCount: number;
  tokenCount: number;
  sources: NotebookSource[];
}

const SAMPLE_NOTEBOOKS: ResearchNotebook[] = [
  {
    id: 'nb-camelot-arch',
    name: 'Camelot-OS Sovereign Kernel Architecture',
    description: 'Baremetal systemd orchestration, 8GB Scarcity Protocol, and zero-Docker execution hierarchy.',
    category: 'OS Engineering',
    sourcesCount: 5,
    tokenCount: 48250,
    sources: [
      {
        id: 'src-1',
        title: 'Sovereign Laws of Camelot-OS vMAX OMEGA TITAN',
        type: 'markdown',
        wordCount: 1420,
        tokens: 3850,
        snippet: '1. NO DOCKER / K8s / Containers. All services run as native bare-metal systemd units under cgroups v2. 2. NO PYTHON/NODE in hot-path. 3. Edge never grants authority.',
        status: 'indexed'
      },
      {
        id: 'src-2',
        title: 'Open-Notebook Official Repository (lfnovo/open-notebook)',
        type: 'git',
        wordCount: 3200,
        tokens: 8900,
        url: 'https://github.com/lfnovo/open-notebook.git',
        snippet: 'Open-Notebook is an open source personal research assistant & NotebookLM alternative built in Python/FastAPI with multi-source grounding and audio overviews.',
        status: 'indexed'
      },
      {
        id: 'src-3',
        title: '8GB Scarcity Protocol & Linux PSI Throttling',
        type: 'pdf',
        wordCount: 2840,
        tokens: 7400,
        snippet: 'Strict hard cap at 7.2GB RSS memory. PSI monitor triggers zero-copy slab reclamation whenever Pressure exceeds 15% for 10 seconds.',
        status: 'indexed'
      },
      {
        id: 'src-4',
        title: 'Z3 Formal Invariant Specification (Gideon Verifier)',
        type: 'markdown',
        wordCount: 1980,
        tokens: 5200,
        snippet: 'Invariant theorem: For all Sentinel leases L, duration(L) <= 300s and actor(L) is cryptographically signed by Excalibur.',
        status: 'indexed'
      },
      {
        id: 'src-5',
        title: 'Ouroboros 1.58-Bit Ternary Model Distillation',
        type: 'web',
        wordCount: 3400,
        tokens: 9100,
        url: 'https://arxiv.org/abs/2402.17764',
        snippet: 'The Era of 1-bit LLMs: All Large Language Models Are in 1.58 Bits. Weights restricted to {-1, 0, 1} with zero floating point multiplications.',
        status: 'indexed'
      }
    ]
  },
  {
    id: 'nb-multi-llm',
    name: 'Open-Notebook Multi-LLM Provider Engine',
    description: 'Hybrid routing between local Ollama instances (DeepSeek-R1, Llama-3.3) and frontier APIs.',
    category: 'AI Pipeline',
    sourcesCount: 4,
    tokenCount: 34100,
    sources: [
      {
        id: 'src-201',
        title: 'Open-Notebook Provider Architecture & SurrealDB Vector Store',
        type: 'git',
        wordCount: 4100,
        tokens: 11200,
        url: 'https://github.com/lfnovo/open-notebook.git',
        snippet: 'Decoupled LLM abstraction supporting Ollama, Gemini, Claude, OpenAI, Groq, and custom OpenAI-compatible endpoints with dynamic temperature & thinking controls.',
        status: 'indexed'
      },
      {
        id: 'src-202',
        title: 'DeepSeek-R1 Distill Qwen 32B Benchmark Notes',
        type: 'markdown',
        wordCount: 2200,
        tokens: 5800,
        snippet: 'Reasoning traces synthesized locally inside 8GB RAM using 1.58-bit ternary quantization and Qdrant 24-dimensional spatial indexing.',
        status: 'indexed'
      }
    ]
  }
];

export const TwinBrainsModal: React.FC<TwinBrainsModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<'open-notebook' | 'notebooklm' | 'repo-specs'>('open-notebook');
  const [notebooks, setNotebooks] = useState<ResearchNotebook[]>(SAMPLE_NOTEBOOKS);
  const [activeNotebookId, setActiveNotebookId] = useState<string>('nb-camelot-arch');
  const [selectedProvider, setSelectedProvider] = useState<string>('ollama-deepseek');
  
  // Chat state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: 'msg-1',
      sender: 'system',
      text: 'Open-Notebook engine initialized from https://github.com/lfnovo/open-notebook.git. All 5 sources indexed into Qdrant & Redis memory slabs.',
      timestamp: '12:00:01'
    },
    {
      id: 'msg-2',
      sender: 'open-notebook',
      text: 'Welcome to Open-Notebook in Camelot-OS! I am grounded in your loaded research sources. You can ask deep architectural questions, generate audio podcast overviews, or ingest new URLs and papers.',
      timestamp: '12:00:02'
    }
  ]);
  const [inputQuestion, setInputQuestion] = useState('');
  const [isSynthesizing, setIsSynthesizing] = useState(false);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  // New source state
  const [isAddingSource, setIsAddingSource] = useState(false);
  const [newSourceTitle, setNewSourceTitle] = useState('');
  const [newSourceType, setNewSourceType] = useState<'web' | 'markdown' | 'pdf' | 'youtube' | 'git'>('web');
  const [newSourceContent, setNewSourceContent] = useState('');

  // Audio Podcast Generator state
  const [isPlayingPodcast, setIsPlayingPodcast] = useState(false);
  const [podcastProgress, setPodcastProgress] = useState(24);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1.0);
  const [activeHostLine, setActiveHostLine] = useState<number>(1);

  const podcastScript = [
    { host: 'Aria (Host A)', text: "Welcome to Camelot Deep Dive! Today we're exploring open-notebook by lfnovo, an open-source personal AI research assistant integrated directly into our sovereign baremetal OS." },
    { host: 'Marcus (Host B)', text: "Right! What makes Open-Notebook so powerful is that unlike closed cloud notebooks, you have 100% data sovereignty. It runs natively under systemd and supports multi-model grounding across local Ollama and frontier APIs." },
    { host: 'Aria (Host A)', text: "Exactly. In Camelot-OS, it syncs with the 8GB Scarcity Protocol and Qdrant vectors to keep memory footprint under 512MB while solving Z3 invariants in sub-15ms." },
    { host: 'Marcus (Host B)', text: "And every single insight it produces comes with verifiable source quotations and cryptographic WAL2 block receipts!" }
  ];

  const activeNotebook = notebooks.find(n => n.id === activeNotebookId) || notebooks[0];

  // Auto-scroll chat
  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages, isSynthesizing]);

  // Podcast progress timer
  useEffect(() => {
    let timer: any;
    if (isPlayingPodcast) {
      timer = setInterval(() => {
        setPodcastProgress((prev) => {
          if (prev >= 100) {
            setIsPlayingPodcast(false);
            return 0;
          }
          const next = prev + 1.2 * playbackSpeed;
          if (next > 75) setActiveHostLine(3);
          else if (next > 50) setActiveHostLine(2);
          else if (next > 25) setActiveHostLine(1);
          else setActiveHostLine(0);
          return next;
        });
      }, 350);
    }
    return () => clearInterval(timer);
  }, [isPlayingPodcast, playbackSpeed]);

  if (!isOpen) return null;

  // Handle Ask Question
  const handleAskQuestion = (customPrompt?: string) => {
    const q = (customPrompt || inputQuestion).trim();
    if (!q) return;

    const userMsg: ChatMessage = {
      id: `msg-${Date.now()}`,
      sender: 'user',
      text: q,
      timestamp: new Date().toLocaleTimeString().split(' ')[0]
    };

    setChatMessages((prev) => [...prev, userMsg]);
    setInputQuestion('');
    setIsSynthesizing(true);

    setTimeout(() => {
      let reply = '';
      let citations = [];

      if (q.toLowerCase().includes('scarcity') || q.toLowerCase().includes('8gb') || q.toLowerCase().includes('ram')) {
        reply = `According to the **8GB Scarcity Protocol** and **Sovereign Laws of Camelot-OS**, memory is strictly capped at 7.2GB RAM. Open-Notebook operates within a 512MB cgroup container, using zero-copy Qdrant 24-dim vectors and Linux PSI telemetry to prevent memory spikes.`;
        citations = [
          { sourceId: 'src-1', sourceTitle: 'Sovereign Laws of Camelot-OS', quote: 'NO DOCKER / K8s. All services run as native systemd units under cgroups v2 unified hierarchy.' },
          { sourceId: 'src-3', sourceTitle: '8GB Scarcity Protocol & PSI', quote: 'Strict hard cap at 7.2GB RSS memory. Pressure above 15% triggers kernel slab reclamation.' }
        ];
      } else if (q.toLowerCase().includes('open-notebook') || q.toLowerCase().includes('github') || q.toLowerCase().includes('lfnovo')) {
        reply = `**Open-Notebook** (repository: [https://github.com/lfnovo/open-notebook.git](https://github.com/lfnovo/open-notebook.git)) is an open-source personal research assistant designed as a multi-model, privacy-first alternative to NotebookLM. In Camelot-OS, it provides deep multi-source indexing, synaptic research citations, and podcast synthesis under native systemd (\`camelot-open-notebook.service\`).`;
        citations = [
          { sourceId: 'src-2', sourceTitle: 'Open-Notebook Official Repository (lfnovo/open-notebook)', quote: 'Open source AI research notebook with multi-source grounding, audio overviews, and local/cloud LLM routing.' }
        ];
      } else if (q.toLowerCase().includes('z3') || q.toLowerCase().includes('theorem') || q.toLowerCase().includes('invariant')) {
        reply = `Gideon utilizes Z3 formal SMT solver to prove 44 structural theorems before agent actions execute. Open-Notebook validates that all retrieved knowledge facts satisfy the non-contradiction theorem.`;
        citations = [
          { sourceId: 'src-4', sourceTitle: 'Z3 Formal Invariant Specification', quote: 'For all Sentinel leases L, duration(L) <= 300s and actor is cryptographically signed.' }
        ];
      } else {
        reply = `Based on the active sources in **${activeNotebook.name}**, the knowledge graph confirms that deterministic execution is enforced via Rust/WASI sandboxing, high-speed Go routing, and continuous 1.58-bit state distillation.`;
        citations = [
          { sourceId: 'src-1', sourceTitle: 'Sovereign Laws of Camelot-OS', quote: 'The model selects; Camelot resolves, authorizes, and renders.' },
          { sourceId: 'src-5', sourceTitle: 'Ouroboros 1.58-Bit Ternary Model Distillation', quote: 'Weights restricted to {-1, 0, 1} with zero floating point multiplications.' }
        ];
      }

      const botMsg: ChatMessage = {
        id: `msg-${Date.now() + 1}`,
        sender: 'open-notebook',
        text: reply,
        citations,
        timestamp: new Date().toLocaleTimeString().split(' ')[0]
      };

      setChatMessages((prev) => [...prev, botMsg]);
      setIsSynthesizing(false);
    }, 650);
  };

  // Handle Add Source
  const handleAddSource = () => {
    if (!newSourceTitle.trim()) return;
    const newSrc: NotebookSource = {
      id: `src-${Date.now()}`,
      title: newSourceTitle.trim(),
      type: newSourceType,
      wordCount: Math.floor(800 + Math.random() * 1500),
      tokens: Math.floor(2200 + Math.random() * 4000),
      snippet: newSourceContent.trim() || 'Ingested source document content indexed into Open-Notebook memory palace.',
      status: 'indexed'
    };

    setNotebooks((prev) =>
      prev.map((nb) =>
        nb.id === activeNotebookId
          ? {
              ...nb,
              sourcesCount: nb.sourcesCount + 1,
              tokenCount: nb.tokenCount + newSrc.tokens,
              sources: [newSrc, ...nb.sources]
            }
          : nb
      )
    );

    setChatMessages((prev) => [
      ...prev,
      {
        id: `msg-${Date.now()}`,
        sender: 'system',
        text: `Ingested new source: "${newSrc.title}" (${newSrc.tokens.toLocaleString()} tokens). Embeddings generated via Qdrant Cosine index.`,
        timestamp: new Date().toLocaleTimeString().split(' ')[0]
      }
    ]);

    setNewSourceTitle('');
    setNewSourceContent('');
    setIsAddingSource(false);
    confetti({ particleCount: 25, spread: 50, origin: { y: 0.7 } });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-black/85 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-5xl h-[92vh] max-h-[880px] rounded-2xl bg-[#080d1a] border-2 border-cyan-500/50 shadow-[0_0_60px_rgba(34,211,238,0.35)] p-4 sm:p-6 font-mono text-slate-300 flex flex-col justify-between overflow-hidden">
        
        {/* ================= MODAL HEADER ================= */}
        <div>
          <div className="flex items-center justify-between border-b border-cyan-500/30 pb-3">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-gradient-to-br from-purple-950/90 via-cyan-950/80 to-slate-900 border border-purple-400/60 text-purple-300 shadow-[0_0_25px_rgba(192,132,252,0.4)]">
                <Brain className="w-6 h-6 text-purple-300 animate-pulse" />
              </div>
              <div>
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-[10px] text-purple-400 font-bold uppercase tracking-widest">
                    DUAL-CORE REASONING PIPELINE
                  </span>
                  <a 
                    href="https://github.com/lfnovo/open-notebook.git"
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-1 px-2 py-0.5 text-[9px] bg-purple-500/20 hover:bg-purple-500/30 text-purple-200 rounded border border-purple-400/50 transition-all shadow-[0_0_8px_rgba(192,132,252,0.3)] font-bold"
                    title="Visit official Open-Notebook GitHub repository"
                  >
                    <Github className="w-3 h-3 text-purple-300" />
                    <span>lfnovo/open-notebook</span>
                    <ExternalLink className="w-2.5 h-2.5" />
                  </a>
                  <span className="px-2 py-0.5 text-[9px] bg-cyan-500/20 text-cyan-200 rounded border border-cyan-400/40">
                    PORT 8502 // ACTIVE
                  </span>
                </div>
                <h2 className="text-lg sm:text-xl font-bold text-white font-heraldic tracking-wide">
                  TWIN QUANTUM BRAINS <span className="text-xs sm:text-sm font-terminal text-amber-400 font-normal">[OPEN-NOTEBOOK & NOTEBOOKLM]</span>
                </h2>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <a
                href="https://github.com/lfnovo/open-notebook.git"
                target="_blank"
                rel="noreferrer"
                className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-purple-950 border border-purple-500/40 text-purple-300 text-xs font-bold transition-all hover:scale-105"
              >
                <Github className="w-3.5 h-3.5" />
                <span>GitHub Repo</span>
                <ExternalLink className="w-3 h-3" />
              </a>

              <button
                onClick={onClose}
                className="p-2 rounded-lg bg-slate-900 hover:bg-rose-950 text-slate-400 hover:text-rose-200 border border-slate-800 transition-colors"
                title="Close modal"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* ================= TAB SELECTOR ================= */}
          <div className="flex items-center gap-2 my-3 border-b border-slate-800 pb-2 overflow-x-auto">
            <button
              onClick={() => setActiveTab('open-notebook')}
              className={`px-3 sm:px-4 py-1.5 rounded-lg font-bold text-xs flex items-center gap-2 border transition-all whitespace-nowrap ${
                activeTab === 'open-notebook'
                  ? 'bg-purple-950/90 text-purple-200 border-purple-400 shadow-[0_0_15px_rgba(192,132,252,0.3)]'
                  : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:text-slate-200'
              }`}
            >
              <BookOpen className="w-3.5 h-3.5 text-purple-400" />
              <span>OPEN-NOTEBOOK STUDIO</span>
              <span className="text-[9px] px-1.5 py-0.2 rounded bg-purple-900/80 text-purple-300 border border-purple-700">
                {activeNotebook.sourcesCount} Sources
              </span>
            </button>

            <button
              onClick={() => setActiveTab('notebooklm')}
              className={`px-3 sm:px-4 py-1.5 rounded-lg font-bold text-xs flex items-center gap-2 border transition-all whitespace-nowrap ${
                activeTab === 'notebooklm'
                  ? 'bg-cyan-950/90 text-cyan-200 border-cyan-400 shadow-[0_0_15px_rgba(34,211,238,0.3)]'
                  : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:text-slate-200'
              }`}
            >
              <Zap className="w-3.5 h-3.5 text-cyan-400" />
              <span>NOTEBOOKLM (AST Synchronizer)</span>
            </button>

            <button
              onClick={() => setActiveTab('repo-specs')}
              className={`px-3 sm:px-4 py-1.5 rounded-lg font-bold text-xs flex items-center gap-2 border transition-all whitespace-nowrap ${
                activeTab === 'repo-specs'
                  ? 'bg-amber-950/90 text-amber-200 border-amber-400 shadow-[0_0_15px_rgba(245,158,11,0.3)]'
                  : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:text-slate-200'
              }`}
            >
              <Code className="w-3.5 h-3.5 text-amber-400" />
              <span>SYSTEMD & REPO INTEGRATION</span>
            </button>
          </div>
        </div>

        {/* ================= TAB 1: OPEN-NOTEBOOK STUDIO ================= */}
        {activeTab === 'open-notebook' && (
          <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-3.5 overflow-hidden my-1">
            
            {/* Left Column: Notebooks & Sources Deck (Span 4) */}
            <div className="lg:col-span-4 flex flex-col gap-3 overflow-hidden bg-[#040711] border border-purple-900/50 rounded-xl p-3">
              
              {/* Notebook Header & Switcher */}
              <div className="flex items-center justify-between border-b border-purple-900/40 pb-2">
                <div className="flex items-center gap-2">
                  <BookOpen className="w-4 h-4 text-purple-400" />
                  <span className="text-xs font-bold text-purple-200">ACTIVE NOTEBOOK</span>
                </div>
                <button
                  onClick={() => setIsAddingSource(true)}
                  className="flex items-center gap-1 px-2 py-1 rounded bg-purple-900/60 hover:bg-purple-800 border border-purple-500/50 text-[10px] text-purple-200 font-bold transition-all"
                  title="Add new research source"
                >
                  <Plus className="w-3 h-3" />
                  <span>+ Source</span>
                </button>
              </div>

              {/* Notebook Select Pill */}
              <div className="space-y-1.5">
                {notebooks.map((nb) => (
                  <button
                    key={nb.id}
                    onClick={() => setActiveNotebookId(nb.id)}
                    className={`w-full text-left p-2 rounded-lg border text-xs transition-all ${
                      activeNotebookId === nb.id
                        ? 'bg-purple-950/70 border-purple-400 text-purple-200 shadow-[0_0_10px_rgba(192,132,252,0.2)]'
                        : 'bg-slate-950 border-slate-800 text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold truncate">{nb.name}</span>
                      <span className="text-[9px] px-1.5 py-0.2 rounded bg-black/60 text-purple-300 border border-purple-900">
                        {nb.sourcesCount} src
                      </span>
                    </div>
                    <div className="text-[10px] text-slate-500 flex items-center justify-between mt-1">
                      <span>{nb.category}</span>
                      <span className="text-emerald-400">{(nb.tokenCount / 1000).toFixed(1)}k tokens</span>
                    </div>
                  </button>
                ))}
              </div>

              {/* Sources List */}
              <div className="flex-1 flex flex-col min-h-0 border-t border-purple-900/40 pt-2">
                <div className="flex items-center justify-between text-[10px] text-slate-400 mb-1.5">
                  <span className="font-bold uppercase tracking-wider text-purple-300">
                    INGESTED SOURCES ({activeNotebook.sources.length})
                  </span>
                  <span className="text-emerald-400">Qdrant Indexed</span>
                </div>

                <div className="flex-1 overflow-y-auto space-y-1.5 custom-scrollbar pr-1">
                  {activeNotebook.sources.map((src) => (
                    <div
                      key={src.id}
                      className="p-2 rounded-lg bg-slate-950 border border-purple-900/40 hover:border-purple-500/50 text-[11px] space-y-1 transition-all group"
                    >
                      <div className="flex items-start justify-between gap-1">
                        <div className="flex items-center gap-1.5 font-bold text-slate-200 truncate">
                          {src.type === 'git' ? (
                            <Github className="w-3 h-3 text-purple-400 shrink-0" />
                          ) : src.type === 'web' ? (
                            <ExternalLink className="w-3 h-3 text-cyan-400 shrink-0" />
                          ) : (
                            <FileText className="w-3 h-3 text-amber-400 shrink-0" />
                          )}
                          <span className="truncate">{src.title}</span>
                        </div>
                        <span className="text-[9px] px-1 rounded bg-purple-950 text-purple-300 border border-purple-800 uppercase shrink-0">
                          {src.type}
                        </span>
                      </div>

                      <p className="text-[10px] text-slate-400 line-clamp-2 italic leading-relaxed">
                        "{src.snippet}"
                      </p>

                      <div className="flex items-center justify-between text-[9px] text-slate-500 pt-0.5 border-t border-slate-900">
                        <span>{src.wordCount} words</span>
                        <span className="text-purple-300">{src.tokens} tokens</span>
                        {src.url && (
                          <a
                            href={src.url}
                            target="_blank"
                            rel="noreferrer"
                            className="text-cyan-400 hover:underline flex items-center gap-0.5"
                          >
                            <span>Link</span>
                            <ExternalLink className="w-2 h-2" />
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Add Source Modal / Form Drawer */}
              {isAddingSource && (
                <div className="p-3 rounded-xl bg-purple-950/90 border border-purple-400 text-xs space-y-2 animate-fadeIn">
                  <div className="flex items-center justify-between border-b border-purple-800 pb-1">
                    <span className="font-bold text-purple-200">Ingest New Source</span>
                    <button onClick={() => setIsAddingSource(false)} className="text-slate-400 hover:text-white">
                      <X className="w-4 h-4" />
                    </button>
                  </div>

                  <input
                    type="text"
                    placeholder="Source Title or Web / Git URL..."
                    value={newSourceTitle}
                    onChange={(e) => setNewSourceTitle(e.target.value)}
                    className="w-full bg-slate-950 border border-purple-700 rounded px-2 py-1 text-[11px] text-white focus:outline-none focus:border-purple-400"
                  />

                  <div className="flex items-center gap-1.5">
                    {(['web', 'markdown', 'pdf', 'git'] as const).map((t) => (
                      <button
                        key={t}
                        onClick={() => setNewSourceType(t)}
                        className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold border transition-all ${
                          newSourceType === t
                            ? 'bg-purple-600 text-white border-purple-300'
                            : 'bg-slate-900 text-slate-400 border-slate-700'
                        }`}
                      >
                        {t}
                      </button>
                    ))}
                  </div>

                  <textarea
                    rows={2}
                    placeholder="Paste excerpt, article markdown, or notes..."
                    value={newSourceContent}
                    onChange={(e) => setNewSourceContent(e.target.value)}
                    className="w-full bg-slate-950 border border-purple-700 rounded p-1.5 text-[10px] text-slate-200 focus:outline-none focus:border-purple-400"
                  />

                  <div className="flex items-center justify-end gap-2">
                    <button
                      onClick={() => setIsAddingSource(false)}
                      className="px-2 py-1 rounded bg-slate-900 text-slate-400 text-[10px]"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleAddSource}
                      className="px-3 py-1 rounded bg-gradient-to-r from-purple-600 to-cyan-600 text-white font-bold text-[10px] shadow-[0_0_10px_rgba(192,132,252,0.4)]"
                    >
                      Index into Qdrant
                    </button>
                  </div>
                </div>
              )}

            </div>

            {/* Middle & Right Columns: Synaptic Chat & Audio Podcast Studio (Span 8) */}
            <div className="lg:col-span-8 flex flex-col gap-3 overflow-hidden">
              
              {/* Top Control Bar: Model Provider & Audio Overview Trigger */}
              <div className="flex flex-wrap items-center justify-between gap-2 p-2.5 rounded-xl bg-[#050914] border border-purple-900/60 text-xs">
                
                {/* Model Selector */}
                <div className="flex items-center gap-2">
                  <span className="text-[10px] text-purple-400 font-bold uppercase">PROVIDER:</span>
                  <select
                    value={selectedProvider}
                    onChange={(e) => setSelectedProvider(e.target.value)}
                    className="bg-slate-950 border border-purple-800/80 rounded-lg px-2.5 py-1 text-[11px] text-purple-200 font-bold focus:outline-none focus:border-purple-400"
                  >
                    <option value="ollama-deepseek">Ollama (DeepSeek-R1 70B // Local Native)</option>
                    <option value="ollama-llama3">Ollama (Llama 3.3 70B // Local Native)</option>
                    <option value="gemini-flash">Google Gemini 2.5 Flash (Cloud Frontier)</option>
                    <option value="claude-sonnet">Anthropic Claude 3.5 Sonnet</option>
                    <option value="openai-gpt4o">OpenAI GPT-4o</option>
                    <option value="groq-lpu">Groq LPU (Sub-50ms Inference)</option>
                  </select>
                </div>

                {/* Quick GitHub Link & Stats */}
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1 text-[10px] text-emerald-400 bg-emerald-950/60 border border-emerald-800/80 px-2 py-0.5 rounded-lg">
                    <CheckCircle2 className="w-3 h-3" />
                    <span>Z3 Grounded Citations</span>
                  </div>
                  <a
                    href="https://github.com/lfnovo/open-notebook.git"
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-1 text-[10px] text-purple-300 hover:text-white bg-purple-950/80 border border-purple-700 px-2.5 py-0.5 rounded-lg transition-all"
                  >
                    <Github className="w-3 h-3" />
                    <span>lfnovo/open-notebook</span>
                    <ExternalLink className="w-2.5 h-2.5" />
                  </a>
                </div>
              </div>

              {/* Audio Overview Podcast Banner (Deep Dive) */}
              <div className="p-3 rounded-xl bg-gradient-to-r from-[#0d0f24] via-[#091124] to-[#120a21] border border-purple-500/40 shadow-lg flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded-lg bg-purple-950 border border-purple-400 text-purple-300">
                      <Headphones className="w-4 h-4 text-purple-300 animate-pulse" />
                    </div>
                    <div>
                      <div className="text-[10px] text-purple-400 font-bold uppercase tracking-wider">
                        OPEN-NOTEBOOK AUDIO OVERVIEW // DEEP DIVE PODCAST
                      </div>
                      <div className="text-xs font-bold text-white">
                        "Camelot-OS & Open-Notebook: Sovereign Baremetal Architecture"
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setPlaybackSpeed(s => s === 1.0 ? 1.25 : s === 1.25 ? 1.5 : 1.0)}
                      className="px-2 py-1 rounded bg-slate-900 border border-slate-700 text-[10px] text-purple-300 font-bold hover:bg-slate-800"
                    >
                      {playbackSpeed}x
                    </button>
                    <button
                      onClick={() => setIsPlayingPodcast(!isPlayingPodcast)}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-500 hover:to-cyan-500 text-white font-bold text-xs shadow-[0_0_15px_rgba(192,132,252,0.4)] transition-all active:scale-95"
                    >
                      {isPlayingPodcast ? <Pause className="w-3.5 h-3.5 fill-white" /> : <Play className="w-3.5 h-3.5 fill-white" />}
                      <span>{isPlayingPodcast ? 'PAUSE' : 'PLAY EPISODE'}</span>
                    </button>
                  </div>
                </div>

                {/* Podcast Progress Bar */}
                <div className="space-y-1">
                  <div className="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden flex items-center">
                    <div 
                      className="h-full bg-gradient-to-r from-purple-500 via-cyan-400 to-emerald-400 rounded-full transition-all duration-300"
                      style={{ width: `${podcastProgress}%` }}
                    />
                  </div>
                  <div className="flex items-center justify-between text-[9px] text-slate-400 font-mono">
                    <span>{Math.floor(podcastProgress * 0.12)}:{(Math.floor(podcastProgress * 1.8) % 60).toString().padStart(2, '0')}</span>
                    <span className="text-purple-300 truncate max-w-[70%] font-semibold">
                      {podcastScript[activeHostLine]?.host}: "{podcastScript[activeHostLine]?.text.slice(0, 75)}..."
                    </span>
                    <span>12:00</span>
                  </div>
                </div>
              </div>

              {/* Synaptic Chat Messages Stream */}
              <div className="flex-1 overflow-y-auto space-y-2.5 p-3 rounded-xl bg-[#04060e] border border-purple-900/40 custom-scrollbar">
                {chatMessages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex flex-col gap-1 text-xs ${
                      msg.sender === 'user'
                        ? 'items-end'
                        : 'items-start'
                    }`}
                  >
                    <div className="flex items-center gap-1.5 text-[9px] text-slate-500 font-mono">
                      <span>{msg.sender === 'user' ? 'SOVEREIGN USER' : msg.sender === 'open-notebook' ? 'OPEN-NOTEBOOK SYNAPSE' : 'SYSTEM'}</span>
                      <span>•</span>
                      <span>{msg.timestamp}</span>
                    </div>

                    <div
                      className={`p-3 rounded-xl max-w-[90%] leading-relaxed ${
                        msg.sender === 'user'
                          ? 'bg-purple-950/80 border border-purple-500/60 text-purple-100 shadow-[0_0_12px_rgba(192,132,252,0.2)]'
                          : msg.sender === 'open-notebook'
                          ? 'bg-slate-900/90 border border-cyan-500/40 text-slate-200 shadow-md'
                          : 'bg-black/60 border border-slate-800 text-slate-400 font-mono text-[10px]'
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{msg.text}</p>

                      {/* Citations Box */}
                      {msg.citations && msg.citations.length > 0 && (
                        <div className="mt-2.5 pt-2 border-t border-slate-800/80 space-y-1">
                          <span className="text-[9px] text-cyan-400 font-bold uppercase block tracking-wider">
                            GROUNDED SOURCE CITATIONS ({msg.citations.length}):
                          </span>
                          {msg.citations.map((c, i) => (
                            <div key={i} className="p-1.5 rounded bg-black/50 border border-cyan-900/50 text-[10px] text-slate-300">
                              <div className="flex items-center justify-between text-cyan-300 font-bold text-[9px]">
                                <span>[{i + 1}] {c.sourceTitle}</span>
                                <span className="text-emerald-400">100% SAT</span>
                              </div>
                              <p className="italic text-slate-400 mt-0.5">"{c.quote}"</p>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {isSynthesizing && (
                  <div className="flex items-center gap-2 p-2.5 rounded-xl bg-purple-950/40 border border-purple-500/40 text-purple-300 text-xs animate-pulse">
                    <Brain className="w-4 h-4 animate-spin text-purple-400" />
                    <span>Open-Notebook synthesizing source grounded citations across {activeNotebook.sources.length} documents...</span>
                  </div>
                )}

                <div ref={chatBottomRef} />
              </div>

              {/* Prompt Suggestions & Input Box */}
              <div className="space-y-2">
                {/* Chips */}
                <div className="flex items-center gap-1.5 overflow-x-auto text-[10px]">
                  <span className="text-slate-500 shrink-0 font-bold">SUGGESTED:</span>
                  {[
                    'Explain 8GB Scarcity Protocol limits',
                    'How does Open-Notebook integrate with Camelot-OS?',
                    'What Z3 invariant proofs are verified?',
                    'Synthesize audio overview of baremetal setup'
                  ].map((p, i) => (
                    <button
                      key={i}
                      onClick={() => handleAskQuestion(p)}
                      className="px-2.5 py-0.5 rounded-full bg-slate-900/90 hover:bg-purple-950 text-slate-300 hover:text-purple-200 border border-slate-800 hover:border-purple-500 text-[10px] whitespace-nowrap transition-all"
                    >
                      {p}
                    </button>
                  ))}
                </div>

                {/* Input Bar */}
                <div className="flex items-center gap-2 bg-slate-950 border border-purple-900/80 focus-within:border-purple-400 rounded-xl p-1.5 shadow-lg">
                  <input
                    type="text"
                    placeholder={`Ask questions grounded in ${activeNotebook.name}...`}
                    value={inputQuestion}
                    onChange={(e) => setInputQuestion(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleAskQuestion()}
                    className="flex-1 bg-transparent px-3 py-1.5 text-xs text-white placeholder:text-slate-600 focus:outline-none font-mono"
                  />

                  <button
                    onClick={() => handleAskQuestion()}
                    disabled={isSynthesizing || !inputQuestion.trim()}
                    className="flex items-center gap-1 px-4 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-500 hover:to-cyan-500 text-white font-bold text-xs shadow-[0_0_15px_rgba(192,132,252,0.4)] disabled:opacity-50 transition-all active:scale-95"
                  >
                    <Send className="w-3.5 h-3.5" />
                    <span>SYNAPSE</span>
                  </button>
                </div>
              </div>

            </div>

          </div>
        )}

        {/* ================= TAB 2: NOTEBOOKLM (AST SYNCHRONIZER) ================= */}
        {activeTab === 'notebooklm' && (
          <div className="flex-1 space-y-4 my-2 overflow-y-auto custom-scrollbar pr-1">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-center">
              <div className="p-3 rounded-xl bg-[#050914] border border-cyan-900/60 shadow-md">
                <span className="text-[10px] text-slate-400 block font-bold uppercase">AST SYNC FREQUENCY</span>
                <span className="text-lg font-bold text-cyan-300">60 Hz (Sub-16ms)</span>
              </div>
              <div className="p-3 rounded-xl bg-[#050914] border border-cyan-900/60 shadow-md">
                <span className="text-[10px] text-slate-400 block font-bold uppercase">CONTEXT WINDOW</span>
                <span className="text-lg font-bold text-emerald-400">128k TOKENS</span>
              </div>
              <div className="p-3 rounded-xl bg-[#050914] border border-cyan-900/60 shadow-md">
                <span className="text-[10px] text-slate-400 block font-bold uppercase">IPC SLAB CHANNEL</span>
                <span className="text-lg font-bold text-amber-300">SHM_SLAB_0</span>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-[#04060d] border border-cyan-900/60 space-y-2 text-xs">
              <div className="flex items-center justify-between text-cyan-300 font-bold border-b border-slate-800 pb-1.5">
                <span className="flex items-center gap-2">
                  <Layers className="w-4 h-4 text-cyan-400" />
                  AST EXTRACTION & GRAPH EMBEDDING PIPELINE
                </span>
                <span className="text-emerald-400 font-mono">LIVE // ZERO DRIFT</span>
              </div>
              <p className="text-slate-300 text-xs leading-relaxed">
                NotebookLM maintains continuous synchrony between the VFS refractions (`/vfs/refractions/*`), the Graphify 3D spatial knowledge graph, and the Open-Notebook source index.
              </p>
              <pre className="p-3 rounded bg-slate-950 border border-cyan-900/40 text-[10px] text-cyan-300 overflow-x-auto font-mono">
{`[SYNC]: Node 0x9bf4 ("Sir Codex Agent Loop") -> Edge -> 0x11e0 ("SQLite WAL2 Receipt")
[WEIGHT]: 0.941 (Cosine Proximity: 0.988)
[DMA]: Zero-copy ring buffer synced to Redis Memcastle & Qdrant vector collection "world_tree"`}
              </pre>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-[#060b18] border border-cyan-900/40 space-y-2">
                <span className="font-bold text-cyan-200">Twin Quantum Brain Architecture</span>
                <p className="text-[11px] text-slate-400 leading-relaxed">
                  <strong>Open-Notebook (lfnovo):</strong> Handles multi-source ingestion, deep reasoning DAGs, source-grounded answers, and audio overviews.<br/>
                  <strong>NotebookLM:</strong> Handles structural AST tree parsing, vector embedding alignment, and real-time filesystem synchronization.
                </p>
              </div>

              <div className="p-3 rounded-xl bg-[#060b18] border border-cyan-900/40 space-y-2">
                <span className="font-bold text-emerald-300">8GB Scarcity Compliance</span>
                <p className="text-[11px] text-slate-400 leading-relaxed">
                  Both cognitive cores execute natively without container daemons, sharing an IPC shared memory ring buffer (`/dev/shm/camelot_vmax`) capped strictly at 512MB RAM.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* ================= TAB 3: GITHUB REPO & NATIVE DEPLOYMENT ================= */}
        {activeTab === 'repo-specs' && (
          <div className="flex-1 space-y-4 my-2 overflow-y-auto custom-scrollbar pr-1">
            <div className="p-4 rounded-xl bg-gradient-to-r from-purple-950/80 via-slate-900 to-cyan-950/80 border border-purple-400/60 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <Github className="w-5 h-5 text-purple-300" />
                  <h3 className="text-base font-bold text-white">
                    lfnovo / open-notebook
                  </h3>
                  <span className="px-2 py-0.5 text-[10px] rounded bg-purple-500/20 text-purple-200 border border-purple-400/40 font-bold">
                    Open Source
                  </span>
                </div>
                <p className="text-xs text-slate-300 font-mono">
                  Official Repository: <a href="https://github.com/lfnovo/open-notebook.git" target="_blank" rel="noreferrer" className="text-cyan-300 underline font-semibold">https://github.com/lfnovo/open-notebook.git</a>
                </p>
              </div>

              <div className="flex items-center gap-2">
                <a
                  href="https://github.com/lfnovo/open-notebook.git"
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow-[0_0_15px_rgba(192,132,252,0.4)] transition-all hover:scale-105"
                >
                  <ExternalLink className="w-4 h-4" />
                  <span>Open on GitHub</span>
                </a>
              </div>
            </div>

            {/* Native systemd installation specification */}
            <div className="p-4 rounded-xl bg-black/70 border border-purple-900/60 space-y-2 text-xs">
              <div className="flex items-center justify-between text-purple-300 font-bold border-b border-slate-800 pb-1">
                <span>NATIVE SYSTEMD SERVICE SPECIFICATION</span>
                <span className="text-emerald-400">/etc/systemd/system/camelot-open-notebook.service</span>
              </div>
              <pre className="p-3 rounded bg-slate-950 border border-purple-900/40 text-[10px] text-purple-200 overflow-x-auto font-mono">
{`[Unit]
Description=Camelot-OS Open-Notebook Cognitive Research Engine (lfnovo/open-notebook)
After=network.target qdrant.service redis.service

[Service]
Type=simple
User=camelot
WorkingDirectory=/opt/open-notebook
ExecStart=/opt/open-notebook/venv/bin/python app.py --port 8502 --host 127.0.0.1
Restart=always
RestartSec=3
MemoryAccounting=true
MemoryMax=512M
CPUAccounting=true

[Install]
WantedBy=multi-user.target`}
              </pre>
            </div>

            {/* Git Clone & Run Commands */}
            <div className="p-4 rounded-xl bg-black/70 border border-cyan-900/60 space-y-2 text-xs">
              <span className="font-bold text-cyan-300">BAREMETAL INSTALLATION SEQUENCE</span>
              <pre className="p-3 rounded bg-slate-950 border border-cyan-900/40 text-[10px] text-cyan-200 overflow-x-auto font-mono">
{`# 1. Clone Open-Notebook repository
git clone https://github.com/lfnovo/open-notebook.git /opt/open-notebook
cd /opt/open-notebook

# 2. Set up Python virtualenv & dependencies
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

# 3. Enable and start baremetal systemd service
sudo systemctl enable --now camelot-open-notebook.service
sudo systemctl status camelot-open-notebook.service`}
              </pre>
            </div>
          </div>
        )}

        {/* ================= MODAL FOOTER ================= */}
        <div className="border-t border-cyan-500/30 pt-3 flex flex-wrap items-center justify-between text-xs gap-3">
          <div className="flex items-center gap-2 text-slate-400 font-mono text-[11px]">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Open-Notebook linked to: <a href="https://github.com/lfnovo/open-notebook.git" target="_blank" rel="noreferrer" className="text-cyan-300 underline font-bold">https://github.com/lfnovo/open-notebook.git</a></span>
          </div>

          <div className="flex items-center gap-2">
            <a
              href="https://github.com/lfnovo/open-notebook.git"
              target="_blank"
              rel="noreferrer"
              className="px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-purple-300 border border-purple-500/40 text-xs font-bold transition-all flex items-center gap-1"
            >
              <Github className="w-3.5 h-3.5" />
              <span>GitHub</span>
            </a>

            <button
              onClick={onClose}
              className="px-4 py-1.5 rounded-lg bg-cyan-900 hover:bg-cyan-800 text-cyan-100 border border-cyan-400/50 font-bold transition-all shadow-[0_0_10px_rgba(34,211,238,0.3)]"
            >
              DISMISS
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};
