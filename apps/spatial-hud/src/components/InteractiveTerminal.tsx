import React, { useState, useRef, useEffect } from 'react';
import { TerminalLog } from '../types';
import { Terminal, Play, Trash2, Shield, Sparkles, RefreshCw, Send, CheckCircle2, AlertTriangle, Lock } from 'lucide-react';

interface InteractiveTerminalProps {
  logs: TerminalLog[];
  onExecuteCommand: (command: string) => void;
  onClearLogs: () => void;
}

export const InteractiveTerminal: React.FC<InteractiveTerminalProps> = ({
  logs,
  onExecuteCommand,
  onClearLogs,
}) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [logs]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    onExecuteCommand(input.trim());
    setInput('');
  };

  const handleQuickCmd = (cmd: string) => {
    onExecuteCommand(cmd);
  };

  const getSenderBadge = (sender: TerminalLog['sender']) => {
    switch (sender) {
      case 'ANYA_Ω':
        return 'bg-purple-950/80 text-purple-300 border-purple-800/60';
      case 'MERLIN_Ω':
        return 'bg-amber-950/80 text-amber-300 border-amber-800/60';
      case 'SIR_CODEX':
        return 'bg-sky-950/80 text-sky-300 border-sky-800/60';
      case 'LADY_MNEMOSYNE':
        return 'bg-emerald-950/80 text-emerald-300 border-emerald-800/60';
      case 'GIDEON':
        return 'bg-red-950/80 text-red-300 border-red-800/60';
      case 'SCRIBE':
        return 'bg-yellow-950/80 text-yellow-300 border-yellow-800/60';
      case 'OPERATOR':
        return 'bg-neutral-800 text-neutral-100 border-neutral-700 font-bold';
      default:
        return 'bg-neutral-900 text-neutral-400 border-neutral-800';
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-neutral-950 text-neutral-100 font-mono overflow-hidden">
      {/* Terminal Top Control Bar */}
      <div className="px-6 py-3 bg-neutral-900 border-b border-neutral-800 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-1.5">
            <div className="w-3 h-3 rounded-full bg-red-500/80"></div>
            <div className="w-3 h-3 rounded-full bg-yellow-500/80"></div>
            <div className="w-3 h-3 rounded-full bg-emerald-500/80"></div>
          </div>
          <span className="text-xs font-bold tracking-wider text-neutral-300 uppercase flex items-center gap-1.5">
            <Terminal className="w-4 h-4 text-emerald-400" />
            <span>Living Notebook Virtual Terminal (vMAX)</span>
          </span>
        </div>

        {/* Quick Kinetic Trigger Bar */}
        <div className="flex flex-wrap items-center gap-1.5 text-xs">
          <button
            onClick={() => handleQuickCmd('//boot')}
            className="px-2.5 py-1 bg-amber-500/10 hover:bg-amber-500/20 text-amber-300 border border-amber-500/30 rounded text-[11px] transition-all"
          >
            //boot
          </button>
          <button
            onClick={() => handleQuickCmd('//nano-swarm expand')}
            className="px-2.5 py-1 bg-sky-500/10 hover:bg-sky-500/20 text-sky-300 border border-sky-500/30 rounded text-[11px] transition-all"
          >
            //nano-swarm expand
          </button>
          <button
            onClick={() => handleQuickCmd('//sync')}
            className="px-2.5 py-1 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded text-[11px] transition-all"
          >
            //sync
          </button>
          <button
            onClick={() => handleQuickCmd('//shield')}
            className="px-2.5 py-1 bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/30 rounded text-[11px] transition-all"
          >
            //shield
          </button>
          <button
            onClick={() => handleQuickCmd('//gate')}
            className="px-2.5 py-1 bg-red-500/10 hover:bg-red-500/20 text-red-300 border border-red-500/30 rounded text-[11px] transition-all"
          >
            //gate
          </button>
          <button
            onClick={() => handleQuickCmd('//deploy')}
            className="px-2.5 py-1 bg-neutral-800 hover:bg-neutral-700 text-neutral-200 border border-neutral-700 rounded text-[11px] transition-all"
          >
            //deploy
          </button>
          <button
            onClick={() => handleQuickCmd('//GO_LIVE')}
            className="px-2.5 py-1 bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/50 rounded text-[11px] font-bold transition-all"
          >
            //GO_LIVE
          </button>
          <button
            onClick={() => handleQuickCmd('//DISPATCH')}
            className="px-2.5 py-1 bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 border border-purple-500/50 rounded text-[11px] font-bold transition-all"
          >
            //DISPATCH
          </button>
          <button
            onClick={onClearLogs}
            className="p-1 text-neutral-500 hover:text-neutral-300 transition-colors ml-2"
            title="Clear Console"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Terminal Log Stream Body */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 text-xs leading-relaxed select-text">
        {logs.map((log) => (
          <div
            key={log.id}
            className={`p-3.5 rounded-xl border transition-all ${
              log.sender === 'OPERATOR'
                ? 'bg-neutral-900/90 border-neutral-700 ml-8'
                : 'bg-neutral-900/50 border-neutral-800/80 mr-4'
            }`}
          >
            {/* Header: Timestamp, Sender, Level */}
            <div className="flex items-center justify-between mb-2 text-[11px]">
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-0.5 rounded border text-[10px] font-bold tracking-wider ${getSenderBadge(log.sender)}`}>
                  {log.sender}
                </span>
                <span className="text-neutral-500 text-[10px]">{log.timestamp}</span>
              </div>

              {log.level === 'SUCCESS' && (
                <span className="text-emerald-400 flex items-center gap-1 text-[10px] font-bold">
                  <CheckCircle2 className="w-3 h-3" /> VERIFIED
                </span>
              )}
              {log.level === 'WARN' && (
                <span className="text-amber-400 flex items-center gap-1 text-[10px] font-bold">
                  <AlertTriangle className="w-3 h-3" /> ADVISORY
                </span>
              )}
              {log.level === 'DANGER' && (
                <span className="text-red-400 flex items-center gap-1 text-[10px] font-bold">
                  <Lock className="w-3 h-3" /> BLOCKED
                </span>
              )}
            </div>

            {/* Message Body */}
            <div className="text-neutral-200 whitespace-pre-wrap font-mono">
              {log.message}
            </div>

            {/* Optional Codeblock Output */}
            {log.codeBlock && (
              <div className="mt-3 p-3 bg-neutral-950 rounded-lg border border-neutral-800 text-amber-300 font-mono overflow-x-auto text-[11px]">
                <pre>{log.codeBlock}</pre>
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Interactive Command Input Form */}
      <div className="p-4 bg-neutral-900 border-t border-neutral-800">
        <form onSubmit={handleSubmit} className="flex items-center space-x-3">
          <span className="text-emerald-400 font-bold text-sm select-none">❯</span>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Enter sovereign kinetic command (e.g. //boot, //nano-swarm expand, //sync, //gate)..."
            className="flex-1 bg-neutral-950 border border-neutral-800 focus:border-amber-500/70 rounded-lg px-4 py-2.5 text-xs font-mono text-neutral-100 placeholder:text-neutral-600 focus:outline-none focus:ring-1 focus:ring-amber-500/30 transition-all"
          />
          <button
            type="submit"
            className="px-4 py-2.5 bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/50 rounded-lg text-xs font-bold flex items-center space-x-1.5 transition-all active:scale-95 shadow-sm"
          >
            <span>Execute</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
        <div className="mt-2 flex items-center justify-between text-[10px] text-neutral-500 px-1">
          <span>Supported: //boot | //nano-swarm expand | //sync | //shield | //gate | //deploy | //rezero | //audit | //knights</span>
          <span>Anya First/Last Law Active</span>
        </div>
      </div>
    </div>
  );
};
