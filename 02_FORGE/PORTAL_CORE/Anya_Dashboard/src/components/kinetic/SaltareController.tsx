import React, { useState } from 'react';
import { Shield, Globe, Cpu, Zap, Lock, Activity } from 'lucide-react';
import { runtimeConfig } from '@/config/runtime';

const KINETIC_TOKEN = runtimeConfig.saltare.token;
const SALTARE_ROUTE_URL = runtimeConfig.saltare.routeUrl;

interface RouteResponse {
    knight_id: string;
    engine: string;
    weight: number;
    score: number;
    reason: string;
    privacy_override: boolean;
    tensor: {
        velocity: number;
        magnitude: number;
        privacy: number;
        environment: number;
    };
}

export default function SaltareController() {
    const [executing, setExecuting] = useState<string | null>(null);
    const [decision, setDecision] = useState<RouteResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    const routeIntent = async (intent: string) => {
        setExecuting(intent);
        setDecision(null);
        setError(null);

        try {
            const res = await fetch(SALTARE_ROUTE_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': KINETIC_TOKEN
                },
                body: JSON.stringify({
                    intent: intent,
                    velocity: 0.5,
                    magnitude: 0.5,
                    privacy: intent.includes("secret") ? 0.9 : 0.1
                })
            });

            if (!res.ok) throw new Error(`Gateway Error: ${res.status}`);

            const data: RouteResponse = await res.json();
            setDecision(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : "CONNECTION_LOST");
        } finally {
            setExecuting(null);
        }
    };

    return (
        <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-4 font-mono shadow-lg h-full flex flex-col">
            <h3 className="text-blue-500 text-[10px] font-bold mb-4 flex items-center gap-2 border-b border-blue-900/30 pb-2 uppercase tracking-widest">
                <Cpu size={12} /> SALTARE_GATEWAY [DECISION_LOGIC]
            </h3>

            <div className="grid grid-cols-2 gap-3 mb-4">
                <button
                    onClick={() => routeIntent('Perform a full security audit with Trivy')}
                    disabled={!!executing}
                    className="p-3 bg-blue-900/10 border border-blue-900/20 rounded-xl hover:bg-blue-900/20 transition-all flex flex-col items-center justify-center gap-2 group disabled:opacity-50"
                >
                    <Shield size={18} className="text-blue-400 group-hover:text-blue-300" />
                    <span className="text-[9px] text-blue-500 uppercase font-bold">Security</span>
                </button>

                <button
                    onClick={() => routeIntent('Establish a secret local connection')}
                    disabled={!!executing}
                    className="p-3 bg-purple-900/10 border border-purple-900/20 rounded-xl hover:bg-purple-900/20 transition-all flex flex-col items-center justify-center gap-2 group disabled:opacity-50"
                >
                    <Lock size={18} className="text-purple-400 group-hover:text-purple-300" />
                    <span className="text-[9px] text-purple-500 uppercase font-bold">Privacy</span>
                </button>
            </div>

            <div className="bg-black/40 rounded-xl border border-blue-900/10 p-3 flex-1 overflow-y-auto text-[9px] font-mono relative">
                {executing && (
                    <div className="flex items-center gap-2 text-yellow-500 animate-pulse uppercase">
                        <Zap size={10} /> Routing: {executing}...
                    </div>
                )}

                {decision && (
                    <div className="space-y-3">
                        <div className="flex justify-between items-start">
                            <div className="text-blue-400 font-bold text-[11px] uppercase">
                                Selected: {decision.knight_id}
                            </div>
                            <div className="text-[8px] bg-blue-900/30 px-2 py-0.5 rounded border border-blue-800 text-blue-300">
                                SCORE: {decision.score.toFixed(4)}
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-2 text-[8px] text-slate-500">
                            <div className="flex justify-between border-b border-white/5 pb-1">
                                <span>VELOCITY</span>
                                <span className="text-blue-700">{(decision.tensor.velocity * 100).toFixed(0)}%</span>
                            </div>
                            <div className="flex justify-between border-b border-white/5 pb-1">
                                <span>MAGNITUDE</span>
                                <span className="text-blue-700">{(decision.tensor.magnitude * 100).toFixed(0)}%</span>
                            </div>
                            <div className="flex justify-between border-b border-white/5 pb-1">
                                <span>PRIVACY</span>
                                <span className="text-blue-700">{(decision.tensor.privacy * 100).toFixed(0)}%</span>
                            </div>
                            <div className="flex justify-between border-b border-white/5 pb-1">
                                <span>WEIGHT</span>
                                <span className="text-blue-700">{(decision.weight * 100).toFixed(0)}%</span>
                            </div>
                        </div>

                        <div className="text-emerald-500/70 italic leading-relaxed">
                            {`// Rationale: ${decision.reason}`}
                        </div>

                        {decision.privacy_override && (
                            <div className="mt-2 p-1.5 bg-red-900/20 border border-red-900/40 rounded text-red-400 flex items-center gap-2 uppercase font-black text-[7px]">
                                <Shield size={8} /> Titanium Law: Privacy Override Active
                            </div>
                        )}
                    </div>
                )}

                {error && <div className="text-red-500 uppercase">❌ {error}</div>}

                {!executing && !decision && !error && (
                    <div className="h-full flex items-center justify-center text-slate-700 italic gap-2">
                        <Activity size={10} /> Awaiting Intent Dispatch...
                    </div>
                )}
            </div>
        </div>
    );
}
