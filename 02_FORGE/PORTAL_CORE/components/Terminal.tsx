'use client';

import { FitAddon } from '@xterm/addon-fit';
import { WebglAddon } from '@xterm/addon-webgl'; // Optional, but usually good. I'll stick to Fit for now to minimize deps.
import { Terminal as XTerminal } from '@xterm/xterm';
import React, { useEffect, useRef, useState } from 'react';
import '@xterm/xterm/css/xterm.css';
import { TerminalSquare } from 'lucide-react';

export default function Terminal() {
  const terminalRef = useRef<HTMLDivElement>(null);
  const xtermRef = useRef<XTerminal | null>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);
  const commandBufferRef = useRef<string>('');

  // Keep connection status state for UI feedback if needed outside xterm
  const [status, setStatus] = useState<'connected' | 'disconnected' | 'processing'>('connected');

  useEffect(() => {
    if (!terminalRef.current) return;

    // Initialize XTerm
    const term = new XTerminal({
      cursorBlink: true,
      theme: {
        background: '#0a0a0a', // Matches the bg-black/gray-900 aesthetic
        foreground: '#22c55e', // text-green-500
        cursor: '#22c55e',
        selectionBackground: 'rgba(34, 197, 94, 0.3)',
      },
      fontFamily: '"Fira Code", monospace', // Ideally utilize a font that exists, falling back to monospace
      fontSize: 14,
      allowProposedApi: true,
    });

    const fitAddon = new FitAddon();
    term.loadAddon(fitAddon);
    fitAddonRef.current = fitAddon;

    term.open(terminalRef.current);
    fitAddon.fit();

    // Initial Greeting
    term.writeln('\x1b[1;32m⚔️ CAMELOT OS v100.0 [SARDA ENGINE INTERFACE]\x1b[0m');
    term.writeln('Initializing Sovereign Command Unit...');
    term.writeln('Connected to Local Kernel.');
    term.writeln('');
    prompt(term);

    xtermRef.current = term;

    // Handle Resize
    const handleResize = () => fitAddon.fit();
    window.addEventListener('resize', handleResize);

    // Input Handling
    term.onData(async (data) => {
      const charCode = data.charCodeAt(0);

      // Enter key
      if (charCode === 13) {
        term.write('\r\n');
        const command = commandBufferRef.current.trim();
        commandBufferRef.current = '';

        if (command) {
          await processCommand(term, command);
        }

        prompt(term);
      }
      // Backspace
      else if (charCode === 127) {
        if (commandBufferRef.current.length > 0) {
          commandBufferRef.current = commandBufferRef.current.slice(0, -1);
          term.write('\b \b');
        }
      }
      // Ctrl+C (Interrupt)
      else if (charCode === 3) {
        term.write('^C\r\n');
        commandBufferRef.current = '';
        prompt(term);
      }
      // Normal character
      else if (charCode >= 32) {
        commandBufferRef.current += data;
        term.write(data);
      }
    });

    return () => {
      term.dispose();
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  const prompt = (term: XTerminal) => {
    term.write('\r\x1b[1;34m👑 SOVEREIGN>\x1b[0m ');
  };

  const processCommand = async (term: XTerminal, input: string) => {
    setStatus('processing');

    // Command Logic (Mirroring previous fetch logic)
    try {
      let response;
      if (input.startsWith('/query ')) {
        const query = input.replace('/query ', '');
        term.writeln('\x1b[2mSearching Vault...\x1b[0m');
        response = await fetch(
          `http://localhost:8001/memory/query?q=${encodeURIComponent(query)}`,
          {
            method: 'GET',
            headers: { 'x-camelot-token': 'merlin-v100-dev' },
          },
        );
      } else {
        response = await fetch('http://localhost:8001/agent/dispatch', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'x-camelot-token': 'merlin-v100-dev',
          },
          body: JSON.stringify({ intent: input, agent_id: 'MERLIN' }),
        });
      }

      // Handle Response
      if (response.ok) {
        const data = await response.json();

        if (input.startsWith('/query ')) {
          if (data.results && data.results.length > 0) {
            data.results.forEach((r: any) => {
              term.writeln(`\x1b[33m[${r.score.toFixed(2)}] \x1b[0m${r.content}`);
            });
          } else {
            term.writeln('\x1b[3mNo records found in Vault.\x1b[0m');
          }
        } else {
          // Standard Agent Response
          const reply = data.response || 'No response.';
          term.writeln(`\r\n\x1b[1;32m🧠 MERLIN_Omega>\x1b[0m ${reply}`);
        }
      } else {
        const data = await response.json().catch(() => ({ detail: 'Unknown Error' }));
        term.writeln(`\x1b[1;31m❌ ERROR: ${data.detail || response.statusText}\x1b[0m`);
      }
    } catch (err) {
      term.writeln('\x1b[1;31m❌ CONNECTION ERROR: Kernel Offline or Unreachable.\x1b[0m');
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

      {/* XTerm Container */}
      <div ref={terminalRef} className="flex-1 w-full bg-black pl-1 pb-1" />

      {/* Status Overlay (Optional) */}
      {status === 'processing' && (
        <div className="absolute bottom-4 right-4 text-xs text-green-500 opacity-50 animate-pulse pointer-events-none">
          PROCESSING...
        </div>
      )}
    </div>
  );
}
