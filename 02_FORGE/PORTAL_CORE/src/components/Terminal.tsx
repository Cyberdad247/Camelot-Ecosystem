import React, { useEffect, useRef, useState } from 'react';
import { Terminal as XTerminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import '@xterm/xterm/css/xterm.css';
import { TerminalSquare } from 'lucide-react';
import { useCamelotNetwork } from '../hooks/useCamelotNetwork';
import { BrainMonitor } from './BrainMonitor';

export default function Terminal() {
  const terminalRef = useRef<HTMLDivElement>(null);
  const xtermRef = useRef<XTerminal | null>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);
  const commandBufferRef = useRef<string>('');

  const [status, setStatus] = useState<'connected' | 'disconnected' | 'processing'>('connected');
  const networkStatus = useCamelotNetwork();
  const [currentOp, setCurrentOp] = useState<{ source: 'LOCAL' | 'CLOUD' | 'IDLE'; cost: string }>({
    source: 'IDLE',
    cost: '0.00',
  });

  useEffect(() => {
    if (!terminalRef.current) return;

    // Initialize XTerm
    const term = new XTerminal({
      cursorBlink: true,
      theme: {
        background: '#0a0a0a',
        foreground: '#22c55e',
        cursor: '#22c55e',
        selectionBackground: 'rgba(34, 197, 94, 0.3)',
      },
      fontFamily: '"Fira Code", monospace',
      fontSize: 14,
      allowProposedApi: true,
    });

    const fitAddon = new FitAddon();
    term.loadAddon(fitAddon);
    fitAddonRef.current = fitAddon;

    term.open(terminalRef.current);
    fitAddon.fit();

    term.writeln('\x1b[1;32m⚔️ CAMELOT OS v101.0 [SOVEREIGN VORTEX]\x1b[0m');
    term.writeln('Initializing Sovereign Command Unit...');
    term.writeln('Hexagonal Adapter Linked: [INTELLIGENCE_LAYER_READY]');
    term.writeln(`Network Status: [${networkStatus}]`);
    term.writeln('');
    prompt(term);

    xtermRef.current = term;

    const handleResize = () => fitAddon.fit();
    window.addEventListener('resize', handleResize);

    term.onData(async (data) => {
      const charCode = data.charCodeAt(0);

      if (charCode === 13) {
        // Enter
        term.write('\r\n');
        const command = commandBufferRef.current.trim();
        commandBufferRef.current = '';

        if (command) {
          await processCommand(term, command);
        }

        prompt(term);
      } else if (charCode === 127) {
        // Backspace
        if (commandBufferRef.current.length > 0) {
          commandBufferRef.current = commandBufferRef.current.slice(0, -1);
          term.write('\b \b');
        }
      } else if (charCode === 3) {
        // Ctrl+C
        term.write('^C\r\n');
        commandBufferRef.current = '';
        prompt(term);
      } else if (charCode >= 32) {
        commandBufferRef.current += data;
        term.write(data);
      }
    });

    return () => {
      term.dispose();
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  // Update Status line if network changes
  useEffect(() => {
    if (xtermRef.current) {
      // Need a way to update status line non-destructively or just rely on BrainMonitor
    }
  }, [networkStatus]);

  const prompt = (term: XTerminal) => {
    term.write('\r\x1b[1;34m👑 SOVEREIGN>\x1b[0m ');
  };

  const processCommand = async (term: XTerminal, input: string) => {
    setStatus('processing');
    setCurrentOp((prev) => ({ ...prev, source: 'IDLE' })); // Reset momentarily

    try {
      // DIRECT CALL TO MORGANA LOCAL NODE (Solution 3/4)
      // Even if "useLocalAI" is false, we route through Morgana (The Router)
      const res = await fetch('http://localhost:8001/agent/dispatch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ intent: input }),
      });

      if (res.ok) {
        const data = await res.json();

        // Update BrainMonitor based on response headers or body
        setCurrentOp({
          source: data.source as 'LOCAL' | 'CLOUD',
          cost: data.cost || '0.00',
        });

        term.writeln(`\r\n\x1b[1;32m🧠 REPLY>\x1b[0m ${data.response}`);
      } else {
        term.writeln(`\r\n\x1b[1;31m❌ ERROR>\x1b[0m Morgana rejected request.`);
      }
    } catch (err) {
      term.writeln('\x1b[1;31m❌ CONNECTION ERROR: Morgana Offline.\x1b[0m');
    } finally {
      setStatus('connected');
    }
  };

  return (
    <div className="bg-black border border-green-800 rounded-lg flex flex-col h-[500px] shadow-2xl overflow-hidden relative group">
      {/* Header */}
      <div className="bg-gray-900 border-b border-green-900 p-2 flex items-center justify-between px-4 z-10 select-none">
        <div className="flex items-center space-x-2">
          <TerminalSquare size={14} className="text-green-500" />
          <span className="text-xs font-bold text-green-500 tracking-wider">
            SOVEREIGN_COMMAND_UNIT_v2.0 [XTERM]
          </span>
        </div>
        <div className="flex space-x-1">
          <div className="w-2 h-2 rounded-full bg-red-900"></div>
          <div className="w-2 h-2 rounded-full bg-yellow-900"></div>
          <div
            className={`w-2 h-2 rounded-full transition-colors duration-500 ${status === 'processing' ? 'bg-blue-500 animate-pulse' : 'bg-green-500'}`}
          ></div>
        </div>
      </div>

      {/* Brain Monitor Panel (Solution 4) */}
      <BrainMonitor currentOp={currentOp} networkStatus={networkStatus} />

      <div ref={terminalRef} className="flex-1 w-full bg-black pl-1 pb-1" />

      {status === 'processing' && (
        <div className="absolute bottom-4 right-4 text-xs text-green-500 opacity-50 animate-pulse pointer-events-none">
          PROCESSING...
        </div>
      )}
    </div>
  );
}
