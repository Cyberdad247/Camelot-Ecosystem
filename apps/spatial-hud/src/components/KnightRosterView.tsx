import React, { useState } from 'react';
import { KNIGHTS_ROSTER } from '../data/knightsData';
import { Knight } from '../types';
import { Shield, Sparkles, Activity, CheckCircle2, Search, Filter, Play, Check, Layers, Cpu } from 'lucide-react';

interface KnightRosterViewProps {
  onDispatchTask?: (knight: Knight, taskName: string) => void;
}

export const KnightRosterView: React.FC<KnightRosterViewProps> = ({ onDispatchTask }) => {
  const [selectedDivision, setSelectedDivision] = useState<string>('All');
  const [searchTerm, setSearchTerm] = useState('');
  const [dispatchedId, setDispatchedId] = useState<string | null>(null);

  const divisions = ['All', 'Executive', 'Streaming & Customer Ops', 'Property & Asset', 'Core Engineering & Vanguard'];

  const filteredKnights = KNIGHTS_ROSTER.filter((knight) => {
    const matchesDiv = selectedDivision === 'All' || knight.division === selectedDivision;
    const matchesSearch =
      knight.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      knight.role.toLowerCase().includes(searchTerm.toLowerCase()) ||
      knight.domain.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesDiv && matchesSearch;
  });

  const handleDispatch = (knight: Knight) => {
    setDispatchedId(knight.id);
    if (onDispatchTask) {
      onDispatchTask(knight, `DAG_TASK_${Math.floor(Math.random() * 9000 + 1000)}`);
    }
    setTimeout(() => setDispatchedId(null), 2500);
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-neutral-950 text-neutral-100 font-mono overflow-y-auto p-6 md:p-8">
      <div className="max-w-7xl mx-auto w-full space-y-6">
        
        {/* Header & Description */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-neutral-800 pb-6">
          <div>
            <div className="flex items-center space-x-3">
              <h2 className="text-2xl font-bold tracking-tight text-white font-sans">
                The 25-Knight Sovereign Execution Swarm
              </h2>
              <span className="px-2.5 py-0.5 bg-amber-500/20 text-amber-300 text-xs font-semibold rounded-full border border-amber-500/40">
                25 Active Agents
              </span>
            </div>
            <p className="text-xs text-neutral-400 font-sans mt-1">
              Autonomous sub-agent orchestration matrix powered by Merlin's Software Agency & Bio-Kinetic microVM workers.
            </p>
          </div>

          {/* Search Input */}
          <div className="relative w-full md:w-72">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-neutral-500" />
            <input
              type="text"
              placeholder="Search knight by name, role, domain..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-3 py-2 bg-neutral-900 border border-neutral-800 rounded-lg text-xs font-mono text-neutral-200 placeholder:text-neutral-600 focus:outline-none focus:border-amber-500"
            />
          </div>
        </div>

        {/* Division Filter Pills */}
        <div className="flex flex-wrap gap-2 text-xs">
          {divisions.map((div) => (
            <button
              key={div}
              onClick={() => setSelectedDivision(div)}
              className={`px-3.5 py-1.5 rounded-lg border transition-all ${
                selectedDivision === div
                  ? 'bg-amber-500/20 text-amber-300 border-amber-500/50 font-bold shadow-sm'
                  : 'bg-neutral-900 text-neutral-400 border-neutral-800 hover:text-neutral-200'
              }`}
            >
              {div}
            </button>
          ))}
        </div>

        {/* Knights Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredKnights.map((knight) => {
            const isDispatched = dispatchedId === knight.id;

            return (
              <div
                key={knight.id}
                className="bg-neutral-900/90 rounded-xl border border-neutral-800 p-5 flex flex-col justify-between hover:border-neutral-700 transition-all shadow-md group"
              >
                <div className="space-y-3">
                  {/* Top Bar: Division, Status */}
                  <div className="flex items-center justify-between text-[10px]">
                    <span className="text-neutral-400 uppercase tracking-wider bg-neutral-950 px-2 py-0.5 rounded border border-neutral-800">
                      {knight.division}
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold flex items-center gap-1 ${
                        knight.status === 'ARMED'
                          ? 'bg-purple-950/80 text-purple-300 border border-purple-800/60'
                          : knight.status === 'ENGAGED'
                          ? 'bg-amber-950/80 text-amber-300 border border-amber-800/60'
                          : 'bg-emerald-950/80 text-emerald-300 border border-emerald-800/60'
                      }`}
                    >
                      <Activity className="w-3 h-3" />
                      {knight.status}
                    </span>
                  </div>

                  {/* Title & Role */}
                  <div>
                    <h3 className="text-lg font-bold text-white font-sans group-hover:text-amber-300 transition-colors">
                      {knight.name}
                    </h3>
                    <p className="text-xs text-amber-400/90 font-medium">{knight.role}</p>
                    <p className="text-[11px] text-neutral-500 italic mt-0.5">{knight.avatarTitle}</p>
                  </div>

                  {/* Bio */}
                  <p className="text-xs text-neutral-300 font-sans leading-relaxed line-clamp-2">
                    {knight.bio}
                  </p>

                  {/* Skills Badges */}
                  <div className="flex flex-wrap gap-1 pt-1">
                    {knight.skills.map((skill) => (
                      <span
                        key={skill}
                        className="text-[10px] bg-neutral-950 text-neutral-400 border border-neutral-800/80 px-2 py-0.5 rounded"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Bottom Bar: Load & Dispatch Action */}
                <div className="pt-4 mt-4 border-t border-neutral-800/80 space-y-3">
                  <div className="space-y-1 text-[10px]">
                    <div className="flex justify-between text-neutral-400">
                      <span>Compute Load:</span>
                      <span className="font-bold text-neutral-200">{knight.load}%</span>
                    </div>
                    <div className="w-full h-1.5 bg-neutral-950 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-amber-500 rounded-full transition-all"
                        style={{ width: `${knight.load}%` }}
                      />
                    </div>
                  </div>

                  <button
                    onClick={() => handleDispatch(knight)}
                    className={`w-full py-2 px-3 rounded-lg text-xs font-bold transition-all flex items-center justify-center space-x-1.5 shadow-sm active:scale-95 ${
                      isDispatched
                        ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                        : 'bg-neutral-950 hover:bg-neutral-800 text-neutral-200 border border-neutral-800 hover:border-neutral-700'
                    }`}
                  >
                    {isDispatched ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                        <span>DAG Task Dispatched!</span>
                      </>
                    ) : (
                      <>
                        <Play className="w-3.5 h-3.5 text-amber-400" />
                        <span>Dispatch Test DAG Workload</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            );
          })}
        </div>

      </div>
    </div>
  );
};
