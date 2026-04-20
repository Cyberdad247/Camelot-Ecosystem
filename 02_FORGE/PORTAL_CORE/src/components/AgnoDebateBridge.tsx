import React, { useState, useEffect } from 'react';

interface Persona {
    root: { id: string; mandate: string };
    branch: { tone: string; symbols: string };
    leaf: string[];
}

interface SessionResult {
    session_id: string;
    status: string;
    debate_summary: {
        context: any[];
        known_count: number;
        unknown_count: number;
    };
    experts: string[];
    kinetic_result: any;
}

const AgnoDebateBridge: React.FC = () => {
    const [objective, setObjective] = useState('');
    const [isLaboring, setIsLaboring] = useState(false);
    const [sessionResult, setSessionResult] = useState<SessionResult | null>(null);
    const [library, setLibrary] = useState<string[]>([]);
    const [error, setError] = useState<string | null>(null);

    const API_URL = 'http://localhost:18788';

    useEffect(() => {
        fetchLibrary();
    }, []);

    const fetchLibrary = async () => {
        try {
            const res = await fetch(`${API_URL}/vault/personas`);
            const data = await res.json();
            setLibrary(data.library_experts || []);
        } catch (err) {
            console.error('Failed to fetch persona library');
        }
    };

    const initiateSession = async () => {
        if (!objective) return;
        setIsLaboring(true);
        setError(null);
        try {
            const res = await fetch(`${API_URL}/session/start`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: json.stringify({ objective }),
            });
            if (!res.ok) throw new Error('Failed to initiate Agno session');
            const data = await res.json();
            setSessionResult(data);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsLaboring(false);
        }
    };

    return (
        <div className="flex flex-col h-full bg-black border border-green-900 rounded-lg overflow-hidden shadow-[0_0_20px_rgba(0,50,0,0.5)]">
            <div className="bg-green-900/20 px-4 py-2 border-b border-green-900 flex justify-between items-center">
                <h2 className="text-xs font-black tracking-widest text-green-400 uppercase">🧠 Agno Debate Bridge</h2>
                <div className="flex gap-1">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" title="Agno Online" />
                </div>
            </div>

            <div className="flex-1 p-4 overflow-y-auto space-y-4">
                {/* INPUT SECTION */}
                <div className="space-y-2">
                    <label className="text-[10px] text-green-700 uppercase tracking-tighter">Sovereign Directive:</label>
                    <div className="flex gap-2">
                        <input
                            type="text"
                            value={objective}
                            onChange={(e) => setObjective(e.target.value)}
                            placeholder="Enter objective for 5-Panel Debate..."
                            className="flex-1 bg-black border border-green-800 px-3 py-2 text-xs text-green-500 focus:outline-none focus:border-green-400 placeholder-green-900"
                        />
                        <button
                            onClick={initiateSession}
                            disabled={isLaboring}
                            className={`px-4 py-2 bg-green-900 text-black text-xs font-bold uppercase tracking-widest transition-all ${isLaboring ? 'opacity-50 cursor-not-allowed' : 'hover:bg-green-400 active:scale-95'}`}
                        >
                            {isLaboring ? 'Debating...' : 'Strike'}
                        </button>
                    </div>
                </div>

                {/* ERROR DISPLAY */}
                {error && (
                    <div className="p-2 border border-red-900 bg-red-900/10 text-red-500 text-[10px] uppercase">
                        CRITICAL_FAILURE: {error}
                    </div>
                )}

                {/* PERSONA LIBRARY DISPLAY */}
                {!sessionResult && library.length > 0 && (
                    <div className="space-y-2">
                        <span className="text-[10px] text-green-700 uppercase">Available Experts:</span>
                        <div className="flex flex-wrap gap-2">
                            {library.map((expert) => (
                                <div key={expert} className="px-2 py-1 border border-green-900 rounded text-[9px] text-green-600 hover:border-green-500 transition-colors">
                                    {expert}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* SESSION RESULTS */}
                {sessionResult && (
                    <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-500">
                        <div className="p-3 border border-green-800 bg-green-900/5 rounded">
                            <h3 className="text-[10px] text-green-400 font-bold mb-2">SESSION_ID: {sessionResult.session_id}</h3>
                            <div className="space-y-2">
                                <div className="flex justify-between text-[9px]">
                                    <span className="text-gray-500">EXPERTS ASSEMBLED:</span>
                                    <span className="text-green-500">{sessionResult.experts.length}</span>
                                </div>
                                <div className="flex flex-wrap gap-1">
                                    {sessionResult.experts.map((e) => (
                                        <span key={e} className="px-1 border border-green-700 text-[8px] text-green-700 bg-green-900/10 uppercase">{e}</span>
                                    ))}
                                </div>
                            </div>
                        </div>

                        <div className="space-y-1">
                            <span className="text-[10px] text-green-700 uppercase">Debate Summary (TOON):</span>
                            <div className="p-3 bg-black border border-green-900 font-mono text-[9px] text-green-500 leading-relaxed">
                                {`K:${sessionResult.debate_summary.known_count} U:${sessionResult.debate_summary.unknown_count} | [🎭🧠💻⚖️]`}
                            </div>
                        </div>

                        <div className="space-y-1">
                            <span className="text-[10px] text-green-700 uppercase">Kinetic Status:</span>
                            <div className={`p-2 border ${sessionResult.kinetic_result.status === 'ERROR' ? 'border-red-900 text-red-700' : 'border-green-800 text-green-600'} text-[10px] font-bold`}>
                                {sessionResult.kinetic_result.status || 'EXECUTED'}
                            </div>
                        </div>

                        <button
                            onClick={() => setSessionResult(null)}
                            className="w-full py-1 text-[8px] text-green-900 hover:text-green-500 uppercase tracking-widest"
                        >
                            Reset Session
                        </button>
                    </div>
                )}
            </div>

            <div className="bg-black p-2 border-t border-green-900">
                <div className="flex justify-between items-center text-[8px] text-gray-600 font-mono">
                    <span>AGNO_ENGINE_V2.0</span>
                    <span className="animate-pulse">ONLINE</span>
                </div>
            </div>
        </div>
    );
};

export default AgnoDebateBridge;
