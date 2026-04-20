import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/Card';
import { Shield, Zap, Users, Monitor, Activity, Radio, Cpu } from 'lucide-react';

interface KnightStatus {
    id: string;
    role: string;
    status: 'IDLE' | 'ACTIVE' | 'ERROR';
    mission?: string;
    trustScore: number;
}

export default function SwarmMonitor() {
    const [knights, setKnights] = useState<KnightStatus[]>([
        { id: 'knight_scout_01', role: 'DISTILLER', status: 'ACTIVE', mission: 'Analyzing Market Trends', trustScore: 98 },
        { id: 'knight_shield_02', role: 'SENTRY', status: 'IDLE', trustScore: 100 },
        { id: 'knight_forge_01', role: 'SYNTH', status: 'ACTIVE', mission: 'Generating UI Artifacts', trustScore: 95 },
    ]);

    const [swarmHealth, setSwarmHealth] = useState(94);

    return (
        <div className="flex flex-col h-full bg-slate-950 text-white p-4 space-y-4">
            <header className="flex items-center justify-between mb-2">
                <div>
                    <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-600">
                        Swarm Monitor
                    </h1>
                    <p className="text-xs text-slate-500 uppercase tracking-widest">Anya Knight Cluster v1.0</p>
                </div>
                <div className="flex items-center gap-2 bg-slate-900 px-3 py-1 rounded-full border border-slate-800">
                    <Activity size={14} className="text-green-500 animate-pulse" />
                    <span className="text-sm font-mono">{swarmHealth}%</span>
                </div>
            </header>

            {/* Swarm Metrics */}
            <div className="grid grid-cols-2 gap-3">
                <Card className="bg-slate-900 border-slate-800 p-4" title="Nodes" actions={<Users size={16} className="text-blue-400" />}>
                   <div className="text-2xl font-bold">12 Active</div>
                   <p className="text-[10px] text-slate-500 mt-1">8 Local | 4 Remote</p>
                </Card>
                <Card className="bg-slate-900 border-slate-800 p-4" title="Throughput" actions={<Cpu size={16} className="text-purple-400" />}>
                   <div className="text-2xl font-bold">4.2 T/s</div>
                   <p className="text-[10px] text-slate-500 mt-1">Cognitive Load: 12%</p>
                </Card>
            </div>

            {/* Knight Roster */}
            <div className="flex-1 overflow-y-auto space-y-3">
                <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Knight Roster</h2>
                {knights.map((knight) => (
                    <div key={knight.id} className="bg-slate-900/50 border border-slate-800 rounded-lg p-3 flex items-center justify-between group hover:border-blue-500/50 transition-colors">
                        <div className="flex items-center gap-3">
                            <div className={`p-2 rounded-lg ${
                                knight.status === 'ACTIVE' ? 'bg-blue-500/10 text-blue-400' : 'bg-slate-800 text-slate-500'
                            }`}>
                                <Shield size={20} />
                            </div>
                            <div>
                                <h3 className="text-sm font-medium">{knight.id}</h3>
                                <p className="text-[10px] text-slate-500 font-mono">ROLE: {knight.role}</p>
                            </div>
                        </div>
                        
                        <div className="text-right">
                            {knight.status === 'ACTIVE' ? (
                                <div className="flex flex-col items-end">
                                    <span className="text-[10px] text-blue-400 flex items-center gap-1">
                                        <Zap size={10} className="animate-pulse" /> PROCESSING
                                    </span>
                                    <span className="text-[10px] text-slate-400 truncate max-w-[100px]">{knight.mission}</span>
                                </div>
                            ) : (
                                <span className="text-[10px] text-slate-600">STANDBY</span>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            {/* Broadcast Terminal */}
            <div className="mt-auto">
                <div className="h-24 bg-black rounded-lg border border-slate-800 p-2 font-mono text-[10px] overflow-hidden opacity-70">
                    <div className="text-green-500">[LOG] Swarm pulse verified...</div>
                    <div className="text-slate-500">[SYS] TitanLink Bridge established.</div>
                    <div className="text-blue-400">[HIVE] OMEGA_CONDUCTOR taking control...</div>
                    <div className="text-slate-500">[SYS] Awaiting Q-Focus input.</div>
                </div>
            </div>
        </div>
    );
}
