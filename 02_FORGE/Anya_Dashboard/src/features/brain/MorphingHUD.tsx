import React, { useState, useEffect, useRef } from 'react';
import { Card } from '@/components/ui/Card';
import { Send, Mic, MicOff, Shield, Zap, Terminal, User, Sparkles } from 'lucide-react';
import QuantumScene from '@/components/engine/Scene';
import { useEngineStore } from './engineStore';

// 🛡️ Personas & Vibe Logic
type PersonaType = 'Anya_Ω' | 'Merlin_Ω' | 'Lukas_Ω' | 'Sentinel_Ω';

interface PersonaState {
    id: string;
    color: string;
    glow: string;
    asset: string;
    tagline: string;
}

const PERSONAS: Record<PersonaType, PersonaState> = {
    'Anya_Ω': { id: 'Anya', color: '#06b6d4', glow: 'shadow-cyan-500/50', asset: '🎭', tagline: 'Interface Sovereign' },
    'Merlin_Ω': { id: 'Merlin', color: '#8b5cf6', glow: 'shadow-purple-500/50', asset: '🧙‍♂️', tagline: 'Neural Conductor' },
    'Lukas_Ω': { id: 'Lukas', color: '#f59e0b', glow: 'shadow-orange-500/50', asset: '💻', tagline: 'Kinetic Baron' },
    'Sentinel_Ω': { id: 'Sentinel', color: '#10b981', glow: 'shadow-emerald-500/50', asset: '🛡️', tagline: 'Security Guardian' }
};

interface Message {
    role: 'user' | 'assistant';
    content: string;
    persona?: PersonaType;
}

export default function MorphingHUD() {
    const [query, setQuery] = useState('');
    const [messages, setMessages] = useState<Message[]>([]);
    const [loading, setLoading] = useState(false);
    const [activePersona, setActivePersona] = useState<PersonaType>('Anya_Ω');
    const [vocalCue, setVocalCue] = useState('System Online');
    const [isListening, setIsListening] = useState(false);
    
    const scrollRef = useRef<HTMLDivElement>(null);
    const state = PERSONAS[activePersona];

    // Auto-scroll chat
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, loading]);

    const handleSend = async () => {
        if (!query.trim()) return;

        const userMsg: Message = { role: 'user', content: query };
        setMessages(prev => [...prev, userMsg]);
        setQuery('');
        setLoading(true);

        // Simulation logic for persona handoffs
        if (query.toLowerCase().includes('switch to merlin')) {
            setTimeout(() => {
                setActivePersona('Merlin_Ω');
                setVocalCue('Channeling the Neural Stack...');
                setMessages(prev => [...prev, { role: 'assistant', content: 'Merlin Online. Awaiting architecture directive.', persona: 'Merlin_Ω' }]);
                setLoading(false);
            }, 800);
            return;
        }

        try {
            const response = await fetch('http://localhost:8001/agent/dispatch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-camelot-token': 'merlin-v100-dev'
                },
                body: JSON.stringify({
                    agent_id: activePersona.replace('_Ω', '').toUpperCase(),
                    intent: query
                })
            });

            const data = await response.json();
            
            if (data.status === 'COMPLETED') {
                const aiMsg: Message = { 
                    role: 'assistant', 
                    content: data.response,
                    persona: activePersona 
                };
                setMessages(prev => [...prev, aiMsg]);
            } else {
                throw new Error(data.error || 'Failed to get response');
            }
        } catch (err) {
            setMessages(prev => [...prev, { role: 'assistant', content: "⚠️ Connection to Kernel severed." }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-screen w-screen bg-black font-sans text-slate-200 p-2 lg:p-6 overflow-hidden">
            {/* TOP BAR: Status & Personas */}
            <div className="flex items-center justify-between mb-4 px-2">
                <div className="flex items-center gap-3">
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center text-2xl bg-slate-900 border-2 transition-all duration-500 ${state.glow}`} style={{ borderColor: state.color }}>
                        {state.asset}
                    </div>
                    <div>
                        <h1 className="text-lg font-bold tracking-tighter leading-none" style={{ color: state.color }}>{activePersona}</h1>
                        <p className="text-[10px] uppercase tracking-widest opacity-50">{state.tagline}</p>
                    </div>
                </div>
                
                <div className="flex gap-2">
                    <div className="hidden md:flex gap-1 mr-4">
                        {(Object.keys(PERSONAS) as PersonaType[]).map(p => (
                            <button 
                                key={p} 
                                onClick={() => setActivePersona(p)}
                                className={`w-2 h-2 rounded-full transition-all ${activePersona === p ? 'scale-150' : 'opacity-20'}`}
                                style={{ backgroundColor: PERSONAS[p].color }}
                            />
                        ))}
                    </div>
                    <div className="flex items-center gap-2 bg-slate-900/80 backdrop-blur px-3 py-1 rounded-full border border-slate-800">
                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                        <span className="text-[10px] font-mono text-emerald-500">KERNEL_V202_ACTIVE</span>
                    </div>
                </div>
            </div>

            <div className="flex flex-1 gap-4 overflow-hidden">
                {/* LEFT: 3D Visualization */}
                <div className="hidden lg:block w-3/5 rounded-3xl overflow-hidden border border-slate-800/50 relative group">
                    <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/40 z-10 pointer-events-none" />
                    <QuantumScene />
                    
                    {/* Overlay Metadata */}
                    <div className="absolute bottom-6 left-6 z-20 space-y-2">
                        <div className="flex items-center gap-2 bg-black/60 backdrop-blur-xl p-3 rounded-2xl border border-white/5 shadow-2xl">
                            <Zap size={16} className="text-yellow-400" />
                            <div className="font-mono text-[10px]">
                                <p className="text-white/40 leading-none mb-1">KINETIC PRESSURE</p>
                                <p className="text-white font-bold">0.84 Giga-Ops</p>
                            </div>
                        </div>
                    </div>

                    <div className="absolute top-6 right-6 z-20">
                        <button className="p-3 rounded-2xl bg-white/5 backdrop-blur hover:bg-white/10 border border-white/10 transition-all">
                            <Sparkles size={18} style={{ color: state.color }} />
                        </button>
                    </div>
                </div>

                {/* RIGHT: Intelligence Interface */}
                <div className="flex-1 flex flex-col gap-4">
                    {/* Vocal Cue Terminal */}
                    <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-3 font-mono text-[11px] relative overflow-hidden">
                        <div className="absolute top-0 left-0 w-1 h-full" style={{ backgroundColor: state.color }} />
                        <div className="flex items-center gap-2 text-slate-500 mb-1">
                            <Terminal size={12} />
                            <span>VOCAL_CUE_STREAM</span>
                        </div>
                        <p className="text-slate-300 italic">"{vocalCue}"</p>
                    </div>

                    {/* Chat Area */}
                    <Card className="flex-1 flex flex-col bg-slate-900/20 backdrop-blur-md border-slate-800/50 shadow-none overflow-hidden rounded-3xl" title="">
                        <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-hide">
                            {messages.length === 0 && (
                                <div className="h-full flex flex-col items-center justify-center text-center p-8 opacity-20">
                                    <User size={48} className="mb-4" />
                                    <p className="text-sm">Awaiting Sovereigns Directive...</p>
                                </div>
                            )}
                            {messages.map((m, i) => (
                                <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                    <div className={`relative max-w-[85%] rounded-2xl px-4 py-2.5 text-sm ${
                                        m.role === 'user' 
                                        ? 'bg-slate-100 text-slate-950 font-medium' 
                                        : 'bg-slate-800/80 text-slate-100 border border-slate-700'
                                    }`}>
                                        {m.persona && (
                                            <span className="absolute -top-5 left-0 text-[9px] font-bold uppercase opacity-40" style={{ color: PERSONAS[m.persona].color }}>
                                                {PERSONAS[m.persona].id}
                                            </span>
                                        )}
                                        {m.content}
                                    </div>
                                </div>
                            ))}
                            {loading && (
                                <div className="flex justify-start">
                                    <div className="bg-slate-800/40 rounded-2xl px-4 py-2 flex gap-1">
                                        <div className="w-1.5 h-1.5 rounded-full bg-slate-500 animate-bounce" />
                                        <div className="w-1.5 h-1.5 rounded-full bg-slate-500 animate-bounce [animation-delay:0.2s]" />
                                        <div className="w-1.5 h-1.5 rounded-full bg-slate-500 animate-bounce [animation-delay:0.4s]" />
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Input Area */}
                        <div className="p-4 bg-slate-950/50 border-t border-slate-800/50">
                            <div className="flex gap-2 items-center">
                                <button 
                                    onClick={() => setIsListening(!isListening)}
                                    className={`p-3 rounded-2xl transition-all ${isListening ? 'bg-red-500 text-white animate-pulse' : 'bg-slate-800 text-slate-400 hover:bg-slate-700'}`}
                                >
                                    {isListening ? <MicOff size={20} /> : <Mic size={20} />}
                                </button>
                                
                                <input
                                    className="flex-1 bg-transparent border-none focus:ring-0 text-sm py-3 px-2 placeholder:text-slate-600"
                                    placeholder={`Message ${state.id}...`}
                                    value={query}
                                    onChange={(e) => setQuery(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                                />

                                <button 
                                    onClick={handleSend} 
                                    disabled={!query.trim()}
                                    className={`p-3 rounded-2xl transition-all ${query.trim() ? 'bg-white text-black shadow-xl shadow-white/10' : 'bg-slate-800 text-slate-600 opacity-50'}`}
                                >
                                    <Send size={20} />
                                </button>
                            </div>
                        </div>
                    </Card>
                </div>
            </div>
        </div>
    );
}
