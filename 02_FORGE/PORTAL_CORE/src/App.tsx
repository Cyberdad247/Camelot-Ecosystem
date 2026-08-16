import RotelMonitor from './components/RotelMonitor';
import SaltareController from './components/SaltareController';
import Terminal from './components/Terminal';
import AgnoDebateBridge from './components/AgnoDebateBridge';
import PersonaStudio from './components/PersonaStudio';
import { useState } from 'react';

function App() {
  const [view, setView] = useState<'DASHBOARD' | 'STUDIO'>('DASHBOARD');

  return (
    <main className="min-h-screen bg-black flex flex-col items-center justify-center p-6 font-mono text-green-500 relative overflow-x-hidden">
      {/* Background Decor */}
      <div className="absolute top-0 left-0 w-full h-full opacity-10 pointer-events-none overflow-hidden">
        <div className="animate-pulse text-[10px] whitespace-pre select-none">
          {`0101010101 CAMELOT_APEX 1101010101\n`.repeat(100)}
        </div>
      </div>

      <div className="w-full max-w-7xl z-10">
        <nav className="flex gap-4 mb-4 border-b border-green-900 pb-2">
          <button
            onClick={() => setView('DASHBOARD')}
            className={`px-4 py-1 text-xs font-bold uppercase tracking-widest transition-all ${view === 'DASHBOARD' ? 'bg-green-900 text-black' : 'text-green-900 hover:text-green-400'}`}
          >
            [01_DASHBOARD]
          </button>
          <button
            onClick={() => setView('STUDIO')}
            className={`px-4 py-1 text-xs font-bold uppercase tracking-widest transition-all ${view === 'STUDIO' ? 'bg-purple-900 text-black' : 'text-green-900 hover:text-purple-400'}`}
          >
            [02_PERSONA_STUDIO]
          </button>
        </nav>

        <header className="mb-6 text-center">
          <h1 className="text-5xl font-black tracking-tighter mb-2 animate-bounce">⚔️ CAMELOT OS</h1>
          <p className="text-green-800 text-sm tracking-widest uppercase">
            The Singularity Throne // v207.0.0 (FEEDBACK SINGULARITY)
          </p>
        </header>

        <div className="grid grid-cols-1 xl:grid-cols-4 gap-6 h-[700px]">
          {/* Dashboard Left: Terminal */}
          <div className="xl:col-span-2 h-full">
            <Terminal />
          </div>

          {/* Dashboard Middle: Dynamic View */}
          <div className="h-full">
            {view === 'DASHBOARD' ? <AgnoDebateBridge /> : <PersonaStudio />}
          </div>

          {/* Dashboard Right: Monitors */}
          <div className="space-y-4 h-full flex flex-col">
            <RotelMonitor />
            <div className="flex-1">
              <SaltareController />
            </div>
          </div>
        </div>

        <footer className="mt-8 text-center text-[8px] opacity-30">
          MADE BY INVISIONED MARKETING INC. | ALL RIGHTS RESERVED
        </footer>
      </div>
    </main>
  );
}

export default App;
